//! FFmpeg encoder implementation
//!
//! Handles video transcoding to H.264/H.265 with optional NVENC hardware acceleration.

use std::path::{Path, PathBuf};
use std::process::Stdio;
use tokio::process::Command;
use tracing::{debug, error, info, warn};

use crate::{Result, TranscodeError, Variant};

/// Encoder configuration
pub struct Encoder {
    ffmpeg_path: PathBuf,
    threads: usize,
    enable_nvenc: bool,
}

/// Encoding preset
#[derive(Debug, Clone, Copy)]
pub enum Preset {
    Ultrafast,
    Veryfast,
    Fast,
    Medium,
    Slow,
}

impl Preset {
    fn as_str(&self) -> &'static str {
        match self {
            Self::Ultrafast => "ultrafast",
            Self::Veryfast => "veryfast",
            Self::Fast => "fast",
            Self::Medium => "medium",
            Self::Slow => "slow",
        }
    }
}

impl Encoder {
    /// Create a new encoder
    pub fn new(threads: usize, enable_nvenc: bool) -> Result<Self> {
        // Find ffmpeg binary
        let ffmpeg_path = Self::find_ffmpeg()?;

        info!(
            ffmpeg = %ffmpeg_path.display(),
            threads = threads,
            nvenc = enable_nvenc,
            "Encoder initialized"
        );

        Ok(Self {
            ffmpeg_path,
            threads,
            enable_nvenc,
        })
    }

    fn find_ffmpeg() -> Result<PathBuf> {
        // Check common locations
        let paths = vec![
            PathBuf::from("/usr/bin/ffmpeg"),
            PathBuf::from("/usr/local/bin/ffmpeg"),
            PathBuf::from("/opt/ffmpeg/bin/ffmpeg"),
        ];

        for path in paths {
            if path.exists() {
                return Ok(path);
            }
        }

        // Try PATH
        if let Ok(output) = std::process::Command::new("which").arg("ffmpeg").output() {
            if output.status.success() {
                let path = String::from_utf8_lossy(&output.stdout).trim().to_string();
                return Ok(PathBuf::from(path));
            }
        }

        Err(TranscodeError::Ffmpeg("FFmpeg not found".to_string()))
    }

    /// Transcode a single variant
    ///
    /// Returns the output directory containing HLS segments and playlist
    pub async fn transcode_variant(
        &self,
        input: &Path,
        output_dir: &Path,
        variant: &Variant,
        segment_duration: u32,
    ) -> Result<PathBuf> {
        let variant_dir = output_dir.join(&variant.name);
        tokio::fs::create_dir_all(&variant_dir)
            .await
            .map_err(|e| TranscodeError::Io(e))?;

        let playlist_path = variant_dir.join("playlist.m3u8");
        let segment_pattern = variant_dir.join("segment_%04d.ts");

        info!(
            variant = %variant.name,
            resolution = %format!("{}x{}", variant.width, variant.height),
            bitrate = variant.video_bitrate,
            "Starting transcode"
        );

        let mut args = self.build_args(
            input,
            &playlist_path,
            &segment_pattern,
            variant,
            segment_duration,
        );

        debug!(cmd = %self.ffmpeg_path.display(), args = ?args, "FFmpeg command");

        let output = Command::new(&self.ffmpeg_path)
            .args(&args)
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .map_err(|e| TranscodeError::Ffmpeg(format!("Failed to spawn FFmpeg: {}", e)))?
            .wait_with_output()
            .await
            .map_err(|e| TranscodeError::Ffmpeg(format!("FFmpeg execution failed: {}", e)))?;

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            error!(variant = %variant.name, stderr = %stderr, "FFmpeg failed");
            return Err(TranscodeError::Ffmpeg(format!(
                "FFmpeg failed for {}: {}",
                variant.name, stderr
            )));
        }

        info!(
            variant = %variant.name,
            output = %variant_dir.display(),
            "Transcode complete"
        );

        Ok(variant_dir)
    }

    fn build_args(
        &self,
        input: &Path,
        playlist_path: &Path,
        segment_pattern: &Path,
        variant: &Variant,
        segment_duration: u32,
    ) -> Vec<String> {
        let mut args = vec![
            "-y".to_string(),                // Overwrite output
            "-hide_banner".to_string(),      // Reduce noise
            "-loglevel".to_string(),
            "warning".to_string(),
            "-i".to_string(),
            input.to_string_lossy().to_string(),
        ];

        // Video codec selection
        if self.enable_nvenc {
            args.extend([
                "-c:v".to_string(),
                "h264_nvenc".to_string(),
                "-preset".to_string(),
                "p4".to_string(), // NVENC preset (p1-p7, lower is faster)
                "-tune".to_string(),
                "hq".to_string(),
            ]);
        } else {
            args.extend([
                "-c:v".to_string(),
                "libx264".to_string(),
                "-preset".to_string(),
                Preset::Fast.as_str().to_string(),
                "-tune".to_string(),
                "film".to_string(),
            ]);
        }

        // Video parameters
        args.extend([
            "-vf".to_string(),
            format!("scale={}:{}", variant.width, variant.height),
            "-b:v".to_string(),
            format!("{}", variant.video_bitrate),
            "-maxrate".to_string(),
            format!("{}", (variant.video_bitrate as f64 * 1.5) as u64),
            "-bufsize".to_string(),
            format!("{}", variant.video_bitrate * 2),
            "-r".to_string(),
            format!("{}", variant.framerate),
            "-g".to_string(),
            format!("{}", (variant.framerate * segment_duration as f64) as u32), // Keyframe every segment
            "-sc_threshold".to_string(),
            "0".to_string(), // Disable scene change detection for consistent GOPs
            "-profile:v".to_string(),
            "high".to_string(),
            "-level".to_string(),
            "4.1".to_string(),
        ]);

        // Audio parameters
        args.extend([
            "-c:a".to_string(),
            "aac".to_string(),
            "-b:a".to_string(),
            format!("{}", variant.audio_bitrate),
            "-ar".to_string(),
            "48000".to_string(),
            "-ac".to_string(),
            "2".to_string(),
        ]);

        // Thread control
        if self.threads > 0 {
            args.extend(["-threads".to_string(), format!("{}", self.threads)]);
        }

        // HLS output
        args.extend([
            "-f".to_string(),
            "hls".to_string(),
            "-hls_time".to_string(),
            format!("{}", segment_duration),
            "-hls_list_size".to_string(),
            "0".to_string(), // Keep all segments in playlist
            "-hls_segment_filename".to_string(),
            segment_pattern.to_string_lossy().to_string(),
            "-hls_flags".to_string(),
            "independent_segments".to_string(),
            playlist_path.to_string_lossy().to_string(),
        ]);

        args
    }

    /// Probe source video for metadata
    pub async fn probe(&self, input: &Path) -> Result<VideoInfo> {
        let ffprobe_path = self.ffmpeg_path.with_file_name("ffprobe");

        let output = Command::new(&ffprobe_path)
            .args([
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_streams",
                "-show_format",
                input.to_string_lossy().as_ref(),
            ])
            .output()
            .await
            .map_err(|e| TranscodeError::Ffmpeg(format!("ffprobe failed: {}", e)))?;

        if !output.status.success() {
            return Err(TranscodeError::Ffmpeg("ffprobe failed".to_string()));
        }

        let json: serde_json::Value = serde_json::from_slice(&output.stdout)
            .map_err(|e| TranscodeError::Ffmpeg(format!("Failed to parse ffprobe output: {}", e)))?;

        // Find video stream
        let video_stream = json["streams"]
            .as_array()
            .and_then(|streams| {
                streams
                    .iter()
                    .find(|s| s["codec_type"].as_str() == Some("video"))
            })
            .ok_or_else(|| TranscodeError::Ffmpeg("No video stream found".to_string()))?;

        let width = video_stream["width"].as_u64().unwrap_or(0) as u32;
        let height = video_stream["height"].as_u64().unwrap_or(0) as u32;

        // Parse duration
        let duration = json["format"]["duration"]
            .as_str()
            .and_then(|s| s.parse::<f64>().ok())
            .unwrap_or(0.0);

        // Parse framerate (avg_frame_rate is usually "30000/1001" format)
        let framerate = video_stream["avg_frame_rate"]
            .as_str()
            .and_then(|s| {
                let parts: Vec<&str> = s.split('/').collect();
                if parts.len() == 2 {
                    let num: f64 = parts[0].parse().ok()?;
                    let den: f64 = parts[1].parse().ok()?;
                    Some(num / den)
                } else {
                    s.parse().ok()
                }
            })
            .unwrap_or(30.0);

        Ok(VideoInfo {
            width,
            height,
            duration,
            framerate,
            codec: video_stream["codec_name"]
                .as_str()
                .unwrap_or("unknown")
                .to_string(),
        })
    }
}

/// Source video information
#[derive(Debug, Clone)]
pub struct VideoInfo {
    pub width: u32,
    pub height: u32,
    pub duration: f64,
    pub framerate: f64,
    pub codec: String,
}
