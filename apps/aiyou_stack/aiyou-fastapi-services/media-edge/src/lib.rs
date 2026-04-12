//! Media Edge Proxy - Pingora-based HLS edge with TinyUfo caching
//!
//! Architecture: Rust Pingora → TinyUfo Cache → GCS Backend
//! Fronted by GCP Cloud CDN for global distribution.

pub mod auth;
pub mod cache;
pub mod config;
pub mod gcs;
pub mod health;
pub mod proxy;

pub use config::Config;
pub use proxy::MediaEdgeProxy;

use thiserror::Error;

/// Central error type for the media-edge proxy
#[derive(Error, Debug)]
pub enum MediaEdgeError {
    #[error("Configuration error: {0}")]
    Config(String),

    #[error("Cache error: {0}")]
    Cache(String),

    #[error("GCS error: {0}")]
    Gcs(String),

    #[error("Authentication error: {0}")]
    Auth(String),

    #[error("Proxy error: {0}")]
    Proxy(String),

    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
}

pub type Result<T> = std::result::Result<T, MediaEdgeError>;
