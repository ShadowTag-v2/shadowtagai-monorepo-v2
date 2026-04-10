//! Health check endpoints for K8s probes
//!
//! Provides /health (liveness) and /ready (readiness) endpoints
//! compatible with GCP Load Balancer health checks.

use serde::Serialize;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;

/// Health check response
#[derive(Debug, Serialize)]
pub struct HealthResponse {
    pub status: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cache_ready: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub gcs_ready: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub pop_id: Option<String>,
}

/// Health state tracking
pub struct HealthState {
    /// Whether the service is ready to accept traffic
    ready: AtomicBool,

    /// Whether the cache is initialized
    cache_ready: AtomicBool,

    /// Whether GCS connection is healthy
    gcs_ready: AtomicBool,

    /// POP identifier
    pop_id: String,
}

impl HealthState {
    /// Create a new health state
    pub fn new(pop_id: String) -> Self {
        Self {
            ready: AtomicBool::new(false),
            cache_ready: AtomicBool::new(false),
            gcs_ready: AtomicBool::new(false),
            pop_id,
        }
    }

    /// Set ready state
    pub fn set_ready(&self, ready: bool) {
        self.ready.store(ready, Ordering::SeqCst);
    }

    /// Set cache ready state
    pub fn set_cache_ready(&self, ready: bool) {
        self.cache_ready.store(ready, Ordering::SeqCst);
    }

    /// Set GCS ready state
    pub fn set_gcs_ready(&self, ready: bool) {
        self.gcs_ready.store(ready, Ordering::SeqCst);
    }

    /// Check if service is live (always true unless crashed)
    pub fn is_live(&self) -> bool {
        true
    }

    /// Check if service is ready to accept traffic
    pub fn is_ready(&self) -> bool {
        self.ready.load(Ordering::SeqCst)
    }

    /// Get liveness response
    pub fn liveness_response(&self) -> HealthResponse {
        HealthResponse {
            status: "alive".to_string(),
            cache_ready: None,
            gcs_ready: None,
            pop_id: Some(self.pop_id.clone()),
        }
    }

    /// Get readiness response
    pub fn readiness_response(&self) -> HealthResponse {
        let cache_ready = self.cache_ready.load(Ordering::SeqCst);
        let gcs_ready = self.gcs_ready.load(Ordering::SeqCst);
        let ready = self.ready.load(Ordering::SeqCst);

        HealthResponse {
            status: if ready { "ready" } else { "not_ready" }.to_string(),
            cache_ready: Some(cache_ready),
            gcs_ready: Some(gcs_ready),
            pop_id: Some(self.pop_id.clone()),
        }
    }
}

/// Thread-safe health state handle
pub type HealthHandle = Arc<HealthState>;

/// Create a new health handle
pub fn create_health_state(pop_id: String) -> HealthHandle {
    Arc::new(HealthState::new(pop_id))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_health_state() {
        let health = HealthState::new("test-pop".to_string());

        // Initially not ready
        assert!(!health.is_ready());
        assert!(health.is_live());

        // Set ready
        health.set_ready(true);
        assert!(health.is_ready());

        // Check response
        let response = health.readiness_response();
        assert_eq!(response.status, "ready");
        assert_eq!(response.pop_id, Some("test-pop".to_string()));
    }
}
