//! Transcode Service - FFmpeg-based video transcoding with HLS packaging
//!
//! This service consumes jobs from Pub/Sub, transcodes video to multiple
//! bitrate variants using FFmpeg, packages as HLS, and uploads to GCS.

pub mod config;
pub mod encoder;
pub mod gcs;
pub mod health;
pub mod hls;
pub mod queue;

use thiserror::Error;

/// Central error type for transcode service
#[derive(Error, Debug)]
pub enum TranscodeError {
    #[error("Configuration error: {0}")]
    Config(String),

    #[error("FFmpeg error: {0}")]
    Ffmpeg(String),

    #[error("GCS error: {0}")]
    Gcs(String),

    #[error("Pub/Sub error: {0}")]
    PubSub(String),

    #[error("HLS packaging error: {0}")]
    Hls(String),

    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("Job failed: {0}")]
    JobFailed(String),
}

pub type Result<T> = std::result::Result<T, TranscodeError>;

/// Bitrate ladder variant
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct Variant {
    pub name: String,
    pub width: u32,
    pub height: u32,
    pub video_bitrate: u64, // in bps
    pub audio_bitrate: u64, // in bps
    pub framerate: f64,
}

impl Variant {
    /// Standard bitrate ladder for streaming
    pub fn standard_ladder() -> Vec<Self> {
        vec![
            Self {
                name: "4k".to_string(),
                width: 3840,
                height: 2160,
                video_bitrate: 15_000_000, // 15 Mbps
                audio_bitrate: 192_000,
                framerate: 30.0,
            },
            Self {
                name: "1080p".to_string(),
                width: 1920,
                height: 1080,
                video_bitrate: 6_000_000, // 6 Mbps
                audio_bitrate: 128_000,
                framerate: 30.0,
            },
            Self {
                name: "720p".to_string(),
                width: 1280,
                height: 720,
                video_bitrate: 3_000_000, // 3 Mbps
                audio_bitrate: 128_000,
                framerate: 30.0,
            },
            Self {
                name: "480p".to_string(),
                width: 854,
                height: 480,
                video_bitrate: 1_500_000, // 1.5 Mbps
                audio_bitrate: 96_000,
                framerate: 30.0,
            },
            Self {
                name: "360p".to_string(),
                width: 640,
                height: 360,
                video_bitrate: 800_000, // 800 kbps
                audio_bitrate: 64_000,
                framerate: 30.0,
            },
        ]
    }

    /// Get variants at or below source resolution
    pub fn for_source(source_width: u32, source_height: u32) -> Vec<Self> {
        Self::standard_ladder()
            .into_iter()
            .filter(|v| v.width <= source_width && v.height <= source_height)
            .collect()
    }
}

/// Transcode job specification
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct TranscodeJob {
    pub job_id: uuid::Uuid,
    pub content_id: String,
    pub source_uri: String, // gs://bucket/path/source.mp4
    pub output_prefix: String, // gs://bucket/hls/content_id/
    pub variants: Vec<Variant>,
    pub segment_duration: u32, // seconds, typically 6
    pub created_at: chrono::DateTime<chrono::Utc>,
}

/// Job status
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub enum JobStatus {
    Pending,
    Downloading,
    Transcoding { progress: f32, variant: String },
    Uploading,
    Completed,
    Failed { error: String },
}

/// Job result
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct TranscodeResult {
    pub job_id: uuid::Uuid,
    pub content_id: String,
    pub master_playlist_uri: String,
    pub variants: Vec<VariantResult>,
    pub duration_seconds: f64,
    pub transcode_time_seconds: f64,
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct VariantResult {
    pub name: String,
    pub playlist_uri: String,
    pub bandwidth: u64,
    pub resolution: String,
    pub segment_count: u32,
}
