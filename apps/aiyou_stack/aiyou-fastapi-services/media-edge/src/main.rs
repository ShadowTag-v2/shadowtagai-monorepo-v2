//! Media Edge Proxy - Entry Point
//!
//! Pingora-based HLS edge proxy with TinyUfo caching.

use media_edge::{
    auth::create_jwt_verifier,
    cache::create_cache,
    config::Config,
    gcs::create_gcs,
    health::create_health_state,
    proxy::MediaEdgeProxy,
    Result,
};
use pingora::prelude::*;
use prometheus::{Encoder, TextEncoder, Counter, Gauge, register_counter, register_gauge};
use std::sync::Arc;
use tracing::{error, info};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

lazy_static::lazy_static! {
    static ref REQUESTS_TOTAL: Counter = register_counter!(
        "media_edge_requests_total",
        "Total number of requests processed"
    ).unwrap();

    static ref CACHE_HITS: Counter = register_counter!(
        "media_edge_cache_hits_total",
        "Total number of cache hits"
    ).unwrap();

    static ref CACHE_MISSES: Counter = register_counter!(
        "media_edge_cache_misses_total",
        "Total number of cache misses"
    ).unwrap();

    static ref ACTIVE_CONNECTIONS: Gauge = register_gauge!(
        "media_edge_active_connections",
        "Current number of active connections"
    ).unwrap();
}

/// Start the metrics HTTP server
async fn start_metrics_server(addr: &str) {
    use hyper::service::{make_service_fn, service_fn};
    use hyper::{Body, Request, Response, Server};

    let make_svc = make_service_fn(|_| async {
        Ok::<_, hyper::Error>(service_fn(|_req: Request<Body>| async {
            let encoder = TextEncoder::new();
            let metric_families = prometheus::gather();
            let mut buffer = vec![];
            encoder.encode(&metric_families, &mut buffer).unwrap();
            Ok::<_, hyper::Error>(Response::new(Body::from(buffer)))
        }))
    });

    let addr: std::net::SocketAddr = addr.parse().expect("Invalid metrics address");
    info!(addr = %addr, "Starting metrics server");

    if let Err(e) = Server::bind(&addr).serve(make_svc).await {
        error!(error = %e, "Metrics server error");
    }
}

fn main() -> Result<()> {
    // Initialize tracing with JSON format for GKE
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::fmt::layer()
                .json()
                .with_target(true)
                .with_thread_ids(true),
        )
        .with(tracing_subscriber::EnvFilter::from_default_env())
        .init();

    info!("Media Edge Proxy starting...");

    // Load configuration
    let config = Config::from_env()?;
    config.validate()?;
    info!(
        listen_addr = %config.listen_addr,
        cache_size_mb = config.cache_size_mb,
        pop_id = %config.pop_id,
        "Configuration loaded"
    );

    // Create runtime for async operations
    let rt = tokio::runtime::Runtime::new()?;

    // Initialize components
    let cache = create_cache(config.cache_size_mb, config.cache_ttl_seconds);
    let gcs = rt.block_on(create_gcs(
        config.gcs_bucket.clone(),
        config.gcs_prefix.clone(),
    ))?;
    let jwt = create_jwt_verifier(&config.jwt_secret, &config.jwt_algorithm);
    let health = create_health_state(config.pop_id.clone());

    // Mark service as ready
    health.set_cache_ready(true);
    health.set_gcs_ready(true);
    health.set_ready(true);

    info!("All components initialized, service is ready");

    // Start metrics server in background
    let metrics_addr = config.metrics_addr.clone();
    std::thread::spawn(move || {
        let rt = tokio::runtime::Runtime::new().unwrap();
        rt.block_on(start_metrics_server(&metrics_addr));
    });

    // Create Pingora server
    let mut server = Server::new(None).map_err(|e| {
        media_edge::MediaEdgeError::Proxy(format!("Failed to create server: {}", e))
    })?;
    server.bootstrap();

    // Create proxy service
    let proxy = MediaEdgeProxy::new(
        Arc::new(config.clone()),
        cache,
        gcs,
        jwt,
        health,
    );

    // Create HTTP service
    let mut http_service = http_proxy_service(&server.configuration, proxy);
    http_service.add_tcp(&config.listen_addr);

    info!(addr = %config.listen_addr, "Starting HTTP server");

    server.add_service(http_service);
    server.run_forever();
}
