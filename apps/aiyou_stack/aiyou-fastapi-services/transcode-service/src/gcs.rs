//! Google Cloud Storage client for transcode service
//!
//! Handles downloading source files and uploading transcoded HLS output.

use bytes::Bytes;
use google_cloud_storage::client::{Client, ClientConfig};
use google_cloud_storage::http::objects::download::Range;
use google_cloud_storage::http::objects::get::GetObjectRequest;
use google_cloud_storage::http::objects::upload::{Media, UploadObjectRequest, UploadType};
use std::path::Path;
use std::sync::Arc;
use tokio::fs;
use tracing::{debug, error, info};

use crate::{Result, TranscodeError};

/// GCS client for transcode operations
pub struct GcsClient {
    client: Client,
    bucket: String,
}

impl GcsClient {
    /// Create a new GCS client using ADC
    pub async fn new(bucket: String) -> Result<Self> {
        info!(bucket = %bucket, "Initializing GCS client");

        let config = ClientConfig::default()
            .with_auth()
            .await
            .map_err(|e| TranscodeError::Gcs(format!("Auth failed: {}", e)))?;

        let client = Client::new(config);

        Ok(Self { client, bucket })
    }

    /// Download a file from GCS to local path
    pub async fn download(&self, gcs_path: &str, local_path: &Path) -> Result<()> {
        let object_path = gcs_path
            .strip_prefix(&format!("gs://{}/", self.bucket))
            .unwrap_or(gcs_path)
            .trim_start_matches('/');

        info!(
            bucket = %self.bucket,
            object = %object_path,
            local = %local_path.display(),
            "Downloading from GCS"
        );

        let request = GetObjectRequest {
            bucket: self.bucket.clone(),
            object: object_path.to_string(),
            ..Default::default()
        };

        let data = self
            .client
            .download_object(&request, &Range::default())
            .await
            .map_err(|e| {
                error!(error = %e, path = %object_path, "GCS download failed");
                TranscodeError::Gcs(format!("Download failed: {}", e))
            })?;

        // Ensure parent directory exists
        if let Some(parent) = local_path.parent() {
            fs::create_dir_all(parent).await?;
        }

        fs::write(local_path, &data).await?;

        info!(
            path = %local_path.display(),
            size = data.len(),
            "Download complete"
        );

        Ok(())
    }

    /// Upload a file to GCS
    pub async fn upload(&self, local_path: &Path, gcs_path: &str) -> Result<()> {
        let object_path = gcs_path
            .strip_prefix(&format!("gs://{}/", self.bucket))
            .unwrap_or(gcs_path)
            .trim_start_matches('/');

        let data = fs::read(local_path).await?;
        let content_type = Self::content_type_for_path(local_path);

        debug!(
            bucket = %self.bucket,
            object = %object_path,
            size = data.len(),
            content_type = %content_type,
            "Uploading to GCS"
        );

        let upload_type = UploadType::Simple(Media::new(object_path.to_string()));

        self.client
            .upload_object(
                &UploadObjectRequest {
                    bucket: self.bucket.clone(),
                    ..Default::default()
                },
                data,
                &upload_type,
            )
            .await
            .map_err(|e| {
                error!(error = %e, path = %object_path, "GCS upload failed");
                TranscodeError::Gcs(format!("Upload failed: {}", e))
            })?;

        Ok(())
    }

    /// Upload an entire directory to GCS
    pub async fn upload_directory(&self, local_dir: &Path, gcs_prefix: &str) -> Result<usize> {
        let mut count = 0;

        let mut entries = fs::read_dir(local_dir).await?;

        while let Some(entry) = entries.next_entry().await? {
            let path = entry.path();

            if path.is_file() {
                let file_name = path.file_name().unwrap().to_string_lossy();
                let gcs_path = format!("{}/{}", gcs_prefix.trim_end_matches('/'), file_name);

                self.upload(&path, &gcs_path).await?;
                count += 1;
            } else if path.is_dir() {
                // Recursively upload subdirectories
                let dir_name = path.file_name().unwrap().to_string_lossy();
                let sub_prefix = format!("{}/{}", gcs_prefix.trim_end_matches('/'), dir_name);

                count += Box::pin(self.upload_directory(&path, &sub_prefix)).await?;
            }
        }

        info!(
            dir = %local_dir.display(),
            prefix = %gcs_prefix,
            files = count,
            "Directory upload complete"
        );

        Ok(count)
    }

    /// Determine content type from file extension
    fn content_type_for_path(path: &Path) -> String {
        let ext = path
            .extension()
            .map(|e| e.to_string_lossy().to_lowercase())
            .unwrap_or_default();

        match ext.as_str() {
            "m3u8" => "application/vnd.apple.mpegurl",
            "ts" => "video/mp2t",
            "m4s" => "video/iso.segment",
            "mp4" => "video/mp4",
            "vtt" => "text/vtt",
            "json" => "application/json",
            _ => "application/octet-stream",
        }
        .to_string()
    }

    /// Check if an object exists
    pub async fn exists(&self, gcs_path: &str) -> bool {
        let object_path = gcs_path
            .strip_prefix(&format!("gs://{}/", self.bucket))
            .unwrap_or(gcs_path)
            .trim_start_matches('/');

        self.client
            .get_object(&self.bucket, object_path)
            .await
            .is_ok()
    }
}

/// Thread-safe GCS handle
pub type GcsHandle = Arc<GcsClient>;

/// Create a new GCS handle
pub async fn create_gcs_client(bucket: String) -> Result<GcsHandle> {
    let client = GcsClient::new(bucket).await?;
    Ok(Arc::new(client))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn test_content_type() {
        assert_eq!(
            GcsClient::content_type_for_path(&PathBuf::from("test.m3u8")),
            "application/vnd.apple.mpegurl"
        );
        assert_eq!(
            GcsClient::content_type_for_path(&PathBuf::from("segment.ts")),
            "video/mp2t"
        );
    }
}
