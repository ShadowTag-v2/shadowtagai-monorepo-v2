//! Transcode Service - Main entry point
//!
//! FFmpeg-based video transcoding with HLS packaging for CineVerse.

use std::path::PathBuf;
use std::sync::Arc;
use std::time::Instant;
use tokio::signal;
use tracing::{error, info, warn};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

use transcode_service::{
    config::Config,
    encoder::Encoder,
    gcs::{create_gcs_client, GcsHandle},
    health::{start_health_server, HealthHandle, HealthState},
    hls::HlsPackager,
    queue::QueueConsumer,
    Result, TranscodeError, TranscodeJob, TranscodeResult, Variant, VariantResult,
};

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize logging
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "transcode_service=info,warn".into()),
        )
        .with(tracing_subscriber::fmt::layer().json())
        .init();

    info!("Starting Transcode Service");

    // Load configuration
    let config = Config::from_env()?;

    // Initialize components
    let gcs = create_gcs_client(config.gcs_bucket.clone()).await?;
    let encoder = Arc::new(Encoder::new(config.ffmpeg_threads, config.enable_nvenc)?);
    let packager = Arc::new(HlsPackager::new(config.segment_duration));
    let health = Arc::new(HealthState::new());

    // Create temp directory
    tokio::fs::create_dir_all(&config.temp_dir).await?;

    // Start health server in background
    let health_clone = health.clone();
    let health_addr = config.listen_addr.clone();
    tokio::spawn(async move {
        if let Err(e) = start_health_server(&health_addr, health_clone).await {
            error!(error = %e, "Health server failed");
        }
    });

    // Initialize queue consumer
    let consumer = QueueConsumer::new(&config.gcp_project_id, &config.pubsub_subscription).await?;

    // Mark as ready
    health.set_ready(true);
    info!("Service ready");

    // Create processor closure
    let processor = {
        let gcs = gcs.clone();
        let encoder = encoder.clone();
        let packager = packager.clone();
        let health = health.clone();
        let config = config.clone();

        move |job: TranscodeJob| {
            let gcs = gcs.clone();
            let encoder = encoder.clone();
            let packager = packager.clone();
            let health = health.clone();
            let config = config.clone();

            async move {
                health.set_current_job(Some(job.job_id.to_string()));
                let result = process_job(&job, &gcs, &encoder, &packager, &config).await;

                match &result {
                    Ok(_) => health.increment_processed(),
                    Err(_) => health.increment_failed(),
                }

                health.set_current_job(None);
                result
            }
        }
    };

    // Run consumer loop with graceful shutdown
    tokio::select! {
        result = consumer.run(processor) => {
            if let Err(e) = result {
                error!(error = %e, "Consumer loop failed");
            }
        }
        _ = shutdown_signal() => {
            info!("Shutdown signal received");
        }
    }

    info!("Shutting down");
    Ok(())
}

/// Process a single transcode job
async fn process_job(
    job: &TranscodeJob,
    gcs: &GcsHandle,
    encoder: &Encoder,
    packager: &HlsPackager,
    config: &Config,
) -> Result<TranscodeResult> {
    let start = Instant::now();

    info!(
        job_id = %job.job_id,
        content_id = %job.content_id,
        variants = job.variants.len(),
        "Processing job"
    );

    // Create job-specific temp directory
    let job_dir = PathBuf::from(&config.temp_dir).join(job.job_id.to_string());
    tokio::fs::create_dir_all(&job_dir).await?;

    // Download source file
    let source_path = job_dir.join("source.mp4");
    info!(job_id = %job.job_id, "Downloading source");
    gcs.download(&job.source_uri, &source_path).await?;

    // Probe source for metadata
    let video_info = encoder.probe(&source_path).await?;
    info!(
        job_id = %job.job_id,
        width = video_info.width,
        height = video_info.height,
        duration = video_info.duration,
        "Source probed"
    );

    // Determine variants (filter by source resolution if not specified)
    let variants = if job.variants.is_empty() {
        Variant::for_source(video_info.width, video_info.height)
    } else {
        job.variants.clone()
    };

    // Create output directory
    let output_dir = job_dir.join("output");
    tokio::fs::create_dir_all(&output_dir).await?;

    // Transcode each variant
    let mut variant_results = Vec::new();

    for variant in &variants {
        info!(
            job_id = %job.job_id,
            variant = %variant.name,
            "Transcoding variant"
        );

        let variant_dir = encoder
            .transcode_variant(&source_path, &output_dir, variant, job.segment_duration)
            .await?;

        // Build variant result
        let gcs_prefix = format!("{}{}/", job.output_prefix, job.content_id);
        let result = packager
            .build_variant_result(variant, &variant_dir, &gcs_prefix)
            .await?;

        variant_results.push(result);
    }

    // Generate master playlist
    info!(job_id = %job.job_id, "Generating master playlist");
    packager
        .generate_master_playlist(&output_dir, &variant_results)
        .await?;

    // Upload all output to GCS
    info!(job_id = %job.job_id, "Uploading to GCS");
    let gcs_prefix = format!("{}{}", job.output_prefix, job.content_id);
    let uploaded = gcs.upload_directory(&output_dir, &gcs_prefix).await?;

    // Cleanup temp files
    if let Err(e) = tokio::fs::remove_dir_all(&job_dir).await {
        warn!(job_id = %job.job_id, error = %e, "Failed to cleanup temp files");
    }

    let transcode_time = start.elapsed().as_secs_f64();

    let result = TranscodeResult {
        job_id: job.job_id,
        content_id: job.content_id.clone(),
        master_playlist_uri: format!("{}{}/master.m3u8", job.output_prefix, job.content_id),
        variants: variant_results,
        duration_seconds: video_info.duration,
        transcode_time_seconds: transcode_time,
    };

    info!(
        job_id = %job.job_id,
        duration = video_info.duration,
        transcode_time = transcode_time,
        files_uploaded = uploaded,
        "Job complete"
    );

    Ok(result)
}

/// Wait for shutdown signal
async fn shutdown_signal() {
    let ctrl_c = async {
        signal::ctrl_c()
            .await
            .expect("Failed to install Ctrl+C handler");
    };

    #[cfg(unix)]
    let terminate = async {
        signal::unix::signal(signal::unix::SignalKind::terminate())
            .expect("Failed to install signal handler")
            .recv()
            .await;
    };

    #[cfg(not(unix))]
    let terminate = std::future::pending::<()>();

    tokio::select! {
        _ = ctrl_c => {},
        _ = terminate => {},
    }
}
