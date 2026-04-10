//! Google Cloud Storage backend for media content
//!
//! Uses Application Default Credentials (ADC) for authentication.

use bytes::Bytes;
use google_cloud_storage::client::{Client, ClientConfig};
use google_cloud_storage::http::objects::get::GetObjectRequest;
use std::sync::Arc;
use tracing::{debug, error, info};

use crate::{MediaEdgeError, Result};

/// GCS backend client
pub struct GcsBackend {
    client: Client,
    bucket: String,
    prefix: String,
}

impl GcsBackend {
    /// Create a new GCS backend
    ///
    /// Uses ADC for authentication (works automatically in GKE with Workload Identity)
    pub async fn new(bucket: String, prefix: String) -> Result<Self> {
        info!(bucket = %bucket, prefix = %prefix, "Initializing GCS backend");

        let config = ClientConfig::default()
            .with_auth()
            .await
            .map_err(|e| MediaEdgeError::Gcs(format!("Auth failed: {}", e)))?;

        let client = Client::new(config);

        Ok(Self {
            client,
            bucket,
            prefix,
        })
    }

    /// Fetch an object from GCS
    ///
    /// # Arguments
    /// * `path` - Relative path within the bucket (e.g., "content/abc123/playlist.m3u8")
    ///
    /// # Returns
    /// Tuple of (data, content_type)
    pub async fn get_object(&self, path: &str) -> Result<(Bytes, String)> {
        let full_path = format!("{}{}", self.prefix, path.trim_start_matches('/'));

        debug!(
            bucket = %self.bucket,
            path = %full_path,
            "Fetching from GCS"
        );

        let request = GetObjectRequest {
            bucket: self.bucket.clone(),
            object: full_path.clone(),
            ..Default::default()
        };

        let data = self
            .client
            .download_object(&request, &Default::default())
            .await
            .map_err(|e| {
                error!(error = %e, path = %full_path, "GCS download failed");
                MediaEdgeError::Gcs(format!("Download failed: {}", e))
            })?;

        // Determine content type from extension
        let content_type = Self::content_type_for_path(&full_path);

        debug!(
            path = %full_path,
            size = data.len(),
            content_type = %content_type,
            "GCS fetch successful"
        );

        Ok((Bytes::from(data), content_type))
    }

    /// Determine content type from file extension
    fn content_type_for_path(path: &str) -> String {
        if path.ends_with(".m3u8") {
            "application/vnd.apple.mpegurl".to_string()
        } else if path.ends_with(".ts") {
            "video/mp2t".to_string()
        } else if path.ends_with(".m4s") {
            "video/iso.segment".to_string()
        } else if path.ends_with(".mp4") {
            "video/mp4".to_string()
        } else if path.ends_with(".vtt") {
            "text/vtt".to_string()
        } else {
            "application/octet-stream".to_string()
        }
    }

    /// Check if an object exists
    pub async fn exists(&self, path: &str) -> bool {
        let full_path = format!("{}{}", self.prefix, path.trim_start_matches('/'));

        match self.client.get_object(&self.bucket, &full_path).await {
            Ok(_) => true,
            Err(_) => false,
        }
    }
}

/// Thread-safe GCS handle
pub type GcsHandle = Arc<GcsBackend>;

/// Create a new GCS handle
pub async fn create_gcs(bucket: String, prefix: String) -> Result<GcsHandle> {
    let backend = GcsBackend::new(bucket, prefix).await?;
    Ok(Arc::new(backend))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_content_type() {
        assert_eq!(
            GcsBackend::content_type_for_path("test.m3u8"),
            "application/vnd.apple.mpegurl"
        );
        assert_eq!(
            GcsBackend::content_type_for_path("segment.ts"),
            "video/mp2t"
        );
        assert_eq!(
            GcsBackend::content_type_for_path("chunk.m4s"),
            "video/iso.segment"
        );
    }
}
