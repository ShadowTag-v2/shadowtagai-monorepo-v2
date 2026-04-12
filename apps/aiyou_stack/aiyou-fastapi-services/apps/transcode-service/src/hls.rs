//! HLS packaging and master playlist generation
//!
//! Creates HLS master playlist from transcoded variants.

use std::path::Path;
use tokio::fs;
use tracing::{debug, info};

use crate::{Result, TranscodeError, Variant, VariantResult};

/// HLS packager
pub struct HlsPackager {
    segment_duration: u32,
}

impl HlsPackager {
    pub fn new(segment_duration: u32) -> Self {
        Self { segment_duration }
    }

    /// Generate master playlist from variant playlists
    pub async fn generate_master_playlist(
        &self,
        output_dir: &Path,
        variants: &[VariantResult],
    ) -> Result<String> {
        let mut master = String::new();

        // HLS header
        master.push_str("#EXTM3U\n");
        master.push_str("#EXT-X-VERSION:4\n");
        master.push_str("#EXT-X-INDEPENDENT-SEGMENTS\n");
        master.push_str("\n");

        // Add each variant
        for variant in variants {
            // Stream info
            master.push_str(&format!(
                "#EXT-X-STREAM-INF:BANDWIDTH={},RESOLUTION={},CODECS=\"avc1.640029,mp4a.40.2\",NAME=\"{}\"\n",
                variant.bandwidth,
                variant.resolution,
                variant.name
            ));

            // Relative path to variant playlist
            master.push_str(&format!("{}/playlist.m3u8\n", variant.name));
            master.push_str("\n");
        }

        let master_path = output_dir.join("master.m3u8");
        fs::write(&master_path, &master)
            .await
            .map_err(|e| TranscodeError::Hls(format!("Failed to write master playlist: {}", e)))?;

        info!(
            path = %master_path.display(),
            variants = variants.len(),
            "Master playlist generated"
        );

        Ok(master)
    }

    /// Parse variant playlist to count segments
    pub async fn count_segments(&self, variant_dir: &Path) -> Result<u32> {
        let playlist_path = variant_dir.join("playlist.m3u8");

        let content = fs::read_to_string(&playlist_path)
            .await
            .map_err(|e| TranscodeError::Hls(format!("Failed to read playlist: {}", e)))?;

        // Count #EXTINF lines
        let count = content.lines().filter(|l| l.starts_with("#EXTINF")).count() as u32;

        debug!(
            path = %playlist_path.display(),
            segments = count,
            "Segment count"
        );

        Ok(count)
    }

    /// Build variant result from transcoded output
    pub async fn build_variant_result(
        &self,
        variant: &Variant,
        variant_dir: &Path,
        gcs_prefix: &str,
    ) -> Result<VariantResult> {
        let segment_count = self.count_segments(variant_dir).await?;

        Ok(VariantResult {
            name: variant.name.clone(),
            playlist_uri: format!("{}{}/playlist.m3u8", gcs_prefix, variant.name),
            bandwidth: variant.video_bitrate + variant.audio_bitrate,
            resolution: format!("{}x{}", variant.width, variant.height),
            segment_count,
        })
    }

    /// List all segment files in a variant directory
    pub async fn list_segments(&self, variant_dir: &Path) -> Result<Vec<String>> {
        let mut segments = Vec::new();

        let mut entries = fs::read_dir(variant_dir)
            .await
            .map_err(|e| TranscodeError::Hls(format!("Failed to read variant dir: {}", e)))?;

        while let Some(entry) = entries
            .next_entry()
            .await
            .map_err(|e| TranscodeError::Hls(format!("Failed to read entry: {}", e)))?
        {
            let name = entry.file_name().to_string_lossy().to_string();
            if name.ends_with(".ts") || name.ends_with(".m3u8") {
                segments.push(name);
            }
        }

        segments.sort();
        Ok(segments)
    }
}

/// Validate HLS playlist structure
pub async fn validate_playlist(path: &Path) -> Result<bool> {
    let content = fs::read_to_string(path)
        .await
        .map_err(|e| TranscodeError::Hls(format!("Failed to read playlist: {}", e)))?;

    // Basic validation
    let has_header = content.starts_with("#EXTM3U");
    let has_end = content.contains("#EXT-X-ENDLIST") || content.contains("#EXT-X-STREAM-INF");
    let has_segments = content.contains("#EXTINF") || content.contains("#EXT-X-STREAM-INF");

    if !has_header {
        return Err(TranscodeError::Hls("Missing #EXTM3U header".to_string()));
    }

    if !has_segments {
        return Err(TranscodeError::Hls("No segments or streams found".to_string()));
    }

    Ok(true)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_variant_result() {
        let variant = Variant {
            name: "1080p".to_string(),
            width: 1920,
            height: 1080,
            video_bitrate: 6_000_000,
            audio_bitrate: 128_000,
            framerate: 30.0,
        };

        let result = VariantResult {
            name: variant.name.clone(),
            playlist_uri: "gs://bucket/hls/content/1080p/playlist.m3u8".to_string(),
            bandwidth: variant.video_bitrate + variant.audio_bitrate,
            resolution: format!("{}x{}", variant.width, variant.height),
            segment_count: 120,
        };

        assert_eq!(result.bandwidth, 6_128_000);
        assert_eq!(result.resolution, "1920x1080");
    }
}
