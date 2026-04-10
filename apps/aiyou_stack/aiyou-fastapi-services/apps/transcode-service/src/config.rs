//! Configuration for transcode service
//!
//! Environment variables with TRANSCODE_ prefix

use serde::Deserialize;
use tracing::info;

use crate::{Result, TranscodeError};

#[derive(Debug, Deserialize, Clone)]
pub struct Config {
    /// HTTP server address for health checks
    #[serde(default = "default_listen_addr")]
    pub listen_addr: String,

    /// Metrics server address
    #[serde(default = "default_metrics_addr")]
    pub metrics_addr: String,

    /// GCS bucket for source and output files
    pub gcs_bucket: String,

    /// Prefix for HLS output (e.g., "hls/")
    #[serde(default = "default_output_prefix")]
    pub output_prefix: String,

    /// Pub/Sub subscription for job queue
    pub pubsub_subscription: String,

    /// GCP project ID
    pub gcp_project_id: String,

    /// Temporary directory for transcoding
    #[serde(default = "default_temp_dir")]
    pub temp_dir: String,

    /// HLS segment duration in seconds
    #[serde(default = "default_segment_duration")]
    pub segment_duration: u32,

    /// Maximum concurrent transcode jobs
    #[serde(default = "default_max_concurrent")]
    pub max_concurrent_jobs: usize,

    /// FFmpeg thread count (0 = auto)
    #[serde(default)]
    pub ffmpeg_threads: usize,

    /// Enable hardware acceleration (NVENC)
    #[serde(default)]
    pub enable_nvenc: bool,

    /// Job timeout in seconds
    #[serde(default = "default_job_timeout")]
    pub job_timeout_seconds: u64,
}

fn default_listen_addr() -> String {
    "0.0.0.0:8080".to_string()
}

fn default_metrics_addr() -> String {
    "0.0.0.0:9090".to_string()
}

fn default_output_prefix() -> String {
    "hls/".to_string()
}

fn default_temp_dir() -> String {
    "/tmp/transcode".to_string()
}

fn default_segment_duration() -> u32 {
    6 // 6 seconds is standard for HLS
}

fn default_max_concurrent() -> usize {
    2 // Conservative for GPU memory
}

fn default_job_timeout() -> u64 {
    3600 // 1 hour
}

impl Config {
    /// Load configuration from environment variables
    pub fn from_env() -> Result<Self> {
        let config = config::Config::builder()
            .add_source(
                config::Environment::with_prefix("TRANSCODE")
                    .separator("_")
                    .try_parsing(true),
            )
            .build()
            .map_err(|e| TranscodeError::Config(format!("Failed to load config: {}", e)))?;

        let cfg: Self = config
            .try_deserialize()
            .map_err(|e| TranscodeError::Config(format!("Failed to parse config: {}", e)))?;

        info!(
            bucket = %cfg.gcs_bucket,
            subscription = %cfg.pubsub_subscription,
            segment_duration = cfg.segment_duration,
            nvenc = cfg.enable_nvenc,
            "Configuration loaded"
        );

        Ok(cfg)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_defaults() {
        assert_eq!(default_segment_duration(), 6);
        assert_eq!(default_max_concurrent(), 2);
    }
}
