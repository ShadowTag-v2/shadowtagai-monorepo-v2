//! Core Pingora proxy implementation
//!
//! Implements the ProxyHttp trait for HLS edge serving.

use async_trait::async_trait;
use bytes::Bytes;
use http::{Response, StatusCode};
use pingora::prelude::*;
use pingora_proxy::{ProxyHttp, Session};
use std::sync::Arc;
use tracing::{debug, error, info, warn};

use crate::auth::JwtHandle;
use crate::cache::CacheHandle;
use crate::config::Config;
use crate::gcs::GcsHandle;
use crate::health::HealthHandle;
use crate::{MediaEdgeError, Result};

/// Request context for tracking per-request state
pub struct RequestContext {
    /// Whether this was a cache hit
    pub cache_hit: bool,

    /// Request start time
    pub start_time: std::time::Instant,

    /// Content path
    pub path: String,
}

impl Default for RequestContext {
    fn default() -> Self {
        Self {
            cache_hit: false,
            start_time: std::time::Instant::now(),
            path: String::new(),
        }
    }
}

/// Media Edge proxy service
pub struct MediaEdgeProxy {
    config: Arc<Config>,
    cache: CacheHandle,
    gcs: GcsHandle,
    jwt: JwtHandle,
    health: HealthHandle,
}

impl MediaEdgeProxy {
    /// Create a new proxy instance
    pub fn new(
        config: Arc<Config>,
        cache: CacheHandle,
        gcs: GcsHandle,
        jwt: JwtHandle,
        health: HealthHandle,
    ) -> Self {
        Self {
            config,
            cache,
            gcs,
            jwt,
            health,
        }
    }

    /// Send an error response
    async fn send_error(
        session: &mut Session,
        status: StatusCode,
        message: &str,
    ) -> pingora::Result<bool> {
        let body = format!(r#"{{"error": "{}"}}"#, message);
        let resp = Response::builder()
            .status(status)
            .header("Content-Type", "application/json")
            .header("X-Cache", "ERROR")
            .body(Bytes::from(body))
            .map_err(|e| pingora::Error::because(
                pingora::ErrorType::HTTPStatus(500),
                "Failed to build response",
                e,
            ))?;

        session.write_response_header(Box::new(resp.into_parts().0), false).await?;
        session.write_response_body(Some(Bytes::from(body)), true).await?;
        Ok(true)
    }

    /// Send a successful response with body
    async fn send_response(
        session: &mut Session,
        data: Bytes,
        content_type: &str,
        cache_status: &str,
        pop_id: &str,
    ) -> pingora::Result<bool> {
        let resp = Response::builder()
            .status(StatusCode::OK)
            .header("Content-Type", content_type)
            .header("Content-Length", data.len().to_string())
            .header("X-Cache", cache_status)
            .header("X-Edge-Pop", pop_id)
            .header("Access-Control-Allow-Origin", "*")
            .body(())
            .map_err(|e| pingora::Error::because(
                pingora::ErrorType::HTTPStatus(500),
                "Failed to build response",
                e,
            ))?;

        session.write_response_header(Box::new(resp.into_parts().0), false).await?;
        session.write_response_body(Some(data), true).await?;
        Ok(true)
    }

    /// Handle health check requests
    async fn handle_health(&self, session: &mut Session, path: &str) -> pingora::Result<bool> {
        let (status, body) = match path {
            "/health" => {
                let resp = self.health.liveness_response();
                (StatusCode::OK, serde_json::to_string(&resp).unwrap())
            }
            "/ready" => {
                let resp = self.health.readiness_response();
                let status = if self.health.is_ready() {
                    StatusCode::OK
                } else {
                    StatusCode::SERVICE_UNAVAILABLE
                };
                (status, serde_json::to_string(&resp).unwrap())
            }
            _ => return Ok(false),
        };

        let resp = Response::builder()
            .status(status)
            .header("Content-Type", "application/json")
            .body(())
            .map_err(|e| pingora::Error::because(
                pingora::ErrorType::HTTPStatus(500),
                "Failed to build response",
                e,
            ))?;

        session.write_response_header(Box::new(resp.into_parts().0), false).await?;
        session.write_response_body(Some(Bytes::from(body)), true).await?;
        Ok(true)
    }
}

#[async_trait]
impl ProxyHttp for MediaEdgeProxy {
    type CTX = RequestContext;

    fn new_ctx(&self) -> Self::CTX {
        RequestContext::default()
    }

    async fn request_filter(
        &self,
        session: &mut Session,
        ctx: &mut Self::CTX,
    ) -> pingora::Result<bool> {
        let path = session.req_header().uri.path().to_string();
        ctx.path = path.clone();
        ctx.start_time = std::time::Instant::now();

        debug!(path = %path, "Request received");

        // Handle health checks
        if path == "/health" || path == "/ready" {
            return self.handle_health(session, &path).await;
        }

        // Handle metrics (separate port, but just in case)
        if path == "/metrics" {
            // Metrics should be on a separate port
            return Self::send_error(session, StatusCode::NOT_FOUND, "Use metrics port").await;
        }

        // JWT verification for private paths
        if path.starts_with("/private/") {
            match session.req_header().headers.get("Authorization") {
                Some(auth_header) => {
                    let auth_str = auth_header.to_str().unwrap_or("");
                    match self.jwt.verify(auth_str) {
                        Ok(claims) => {
                            info!(user_id = %claims.sub, path = %path, "JWT verified");
                        }
                        Err(e) => {
                            warn!(error = %e, path = %path, "JWT verification failed");
                            return Self::send_error(
                                session,
                                StatusCode::UNAUTHORIZED,
                                "Invalid or expired token",
                            )
                            .await;
                        }
                    }
                }
                None => {
                    return Self::send_error(
                        session,
                        StatusCode::UNAUTHORIZED,
                        "Authorization required",
                    )
                    .await;
                }
            }
        }

        // Try cache first
        let cache_key = path.clone();
        if let Some((data, content_type)) = self.cache.get(&cache_key) {
            ctx.cache_hit = true;
            info!(path = %path, size = data.len(), "Cache HIT");
            return Self::send_response(
                session,
                data,
                &content_type,
                "HIT",
                &self.config.pop_id,
            )
            .await;
        }

        // Cache miss - fetch from GCS
        ctx.cache_hit = false;
        info!(path = %path, "Cache MISS - fetching from GCS");

        match self.gcs.get_object(&path).await {
            Ok((data, content_type)) => {
                // Insert into cache
                self.cache.insert(cache_key, data.clone(), content_type.clone());

                info!(path = %path, size = data.len(), "GCS fetch successful");
                Self::send_response(
                    session,
                    data,
                    &content_type,
                    "MISS",
                    &self.config.pop_id,
                )
                .await
            }
            Err(e) => {
                error!(error = %e, path = %path, "GCS fetch failed");
                Self::send_error(session, StatusCode::NOT_FOUND, "Content not found").await
            }
        }
    }

    async fn upstream_peer(
        &self,
        _session: &mut Session,
        _ctx: &mut Self::CTX,
    ) -> pingora::Result<Box<HttpPeer>> {
        // We handle everything in request_filter, this shouldn't be called
        // But required by trait - return a dummy peer
        Ok(Box::new(HttpPeer::new(
            ("127.0.0.1", 80),
            false,
            "".to_string(),
        )))
    }

    async fn logging(
        &self,
        session: &mut Session,
        _e: Option<&pingora::Error>,
        ctx: &mut Self::CTX,
    ) {
        let latency = ctx.start_time.elapsed();
        let status = session
            .response_written()
            .map(|r| r.status.as_u16())
            .unwrap_or(0);

        info!(
            path = %ctx.path,
            status = status,
            cache_hit = ctx.cache_hit,
            latency_ms = latency.as_millis(),
            "Request completed"
        );
    }
}
