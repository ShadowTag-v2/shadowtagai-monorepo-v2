//! Configuration management for Media Edge proxy
//!
//! Loads configuration from environment variables with EDGE_ prefix.

use serde::Deserialize;
use crate::{MediaEdgeError, Result};

/// Main configuration struct
#[derive(Debug, Deserialize, Clone)]
pub struct Config {
    /// Server listen address
    #[serde(default = "default_listen_addr")]
    pub listen_addr: String,

    /// Metrics server address
    #[serde(default = "default_metrics_addr")]
    pub metrics_addr: String,

    /// GCS bucket name for media storage
    pub gcs_bucket: String,

    /// GCS prefix for HLS content
    #[serde(default = "default_gcs_prefix")]
    pub gcs_prefix: String,

    /// Cache size in megabytes
    #[serde(default = "default_cache_size_mb")]
    pub cache_size_mb: usize,

    /// Cache TTL in seconds
    #[serde(default = "default_cache_ttl_seconds")]
    pub cache_ttl_seconds: u64,

    /// JWT secret (must match Python backend)
    pub jwt_secret: String,

    /// JWT algorithm (default: HS256)
    #[serde(default = "default_jwt_algorithm")]
    pub jwt_algorithm: String,

    /// Upstream timeout in milliseconds
    #[serde(default = "default_upstream_timeout_ms")]
    pub upstream_timeout_ms: u64,

    /// POP identifier for metrics
    #[serde(default = "default_pop_id")]
    pub pop_id: String,
}

fn default_listen_addr() -> String {
    "0.0.0.0:8080".to_string()
}

fn default_metrics_addr() -> String {
    "0.0.0.0:9090".to_string()
}

fn default_gcs_prefix() -> String {
    "hls/".to_string()
}

fn default_cache_size_mb() -> usize {
    512 // 512MB for MVP
}

fn default_cache_ttl_seconds() -> u64 {
    3600 // 1 hour default
}

fn default_jwt_algorithm() -> String {
    "HS256".to_string()
}

fn default_upstream_timeout_ms() -> u64 {
    30000 // 30 seconds
}

fn default_pop_id() -> String {
    "unknown".to_string()
}

impl Config {
    /// Load configuration from environment variables
    ///
    /// Environment variables should be prefixed with EDGE_
    /// Example: EDGE_GCS_BUCKET, EDGE_JWT_SECRET
    pub fn from_env() -> Result<Self> {
        config::Config::builder()
            .add_source(config::Environment::with_prefix("EDGE"))
            .build()
            .map_err(|e| MediaEdgeError::Config(e.to_string()))?
            .try_deserialize()
            .map_err(|e| MediaEdgeError::Config(e.to_string()))
    }

    /// Validate configuration
    pub fn validate(&self) -> Result<()> {
        if self.gcs_bucket.is_empty() {
            return Err(MediaEdgeError::Config("GCS bucket cannot be empty".into()));
        }
        if self.jwt_secret.is_empty() {
            return Err(MediaEdgeError::Config("JWT secret cannot be empty".into()));
        }
        if self.cache_size_mb == 0 {
            return Err(MediaEdgeError::Config("Cache size must be > 0".into()));
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_defaults() {
        assert_eq!(default_cache_size_mb(), 512);
        assert_eq!(default_jwt_algorithm(), "HS256");
    }
}
