//! Health check endpoints for Kubernetes probes

use axum::{
    extract::State,
    http::StatusCode,
    response::IntoResponse,
    routing::get,
    Json, Router,
};
use serde::Serialize;
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::Arc;
use tracing::info;

/// Application health state
pub struct HealthState {
    ready: AtomicBool,
    jobs_processed: AtomicU64,
    jobs_failed: AtomicU64,
    current_job: parking_lot::RwLock<Option<String>>,
}

impl HealthState {
    pub fn new() -> Self {
        Self {
            ready: AtomicBool::new(false),
            jobs_processed: AtomicU64::new(0),
            jobs_failed: AtomicU64::new(0),
            current_job: parking_lot::RwLock::new(None),
        }
    }

    pub fn set_ready(&self, ready: bool) {
        self.ready.store(ready, Ordering::SeqCst);
    }

    pub fn is_ready(&self) -> bool {
        self.ready.load(Ordering::SeqCst)
    }

    pub fn increment_processed(&self) {
        self.jobs_processed.fetch_add(1, Ordering::SeqCst);
    }

    pub fn increment_failed(&self) {
        self.jobs_failed.fetch_add(1, Ordering::SeqCst);
    }

    pub fn set_current_job(&self, job_id: Option<String>) {
        *self.current_job.write() = job_id;
    }

    pub fn get_current_job(&self) -> Option<String> {
        self.current_job.read().clone()
    }

    pub fn get_stats(&self) -> (u64, u64) {
        (
            self.jobs_processed.load(Ordering::SeqCst),
            self.jobs_failed.load(Ordering::SeqCst),
        )
    }
}

pub type HealthHandle = Arc<HealthState>;

/// Health response
#[derive(Serialize)]
struct HealthResponse {
    status: &'static str,
    jobs_processed: u64,
    jobs_failed: u64,
    current_job: Option<String>,
}

/// Liveness probe - always returns OK if process is running
async fn liveness() -> impl IntoResponse {
    (StatusCode::OK, "OK")
}

/// Readiness probe - returns OK if service is ready to process jobs
async fn readiness(State(state): State<HealthHandle>) -> impl IntoResponse {
    if state.is_ready() {
        (StatusCode::OK, "Ready")
    } else {
        (StatusCode::SERVICE_UNAVAILABLE, "Not Ready")
    }
}

/// Detailed health status
async fn health_detail(State(state): State<HealthHandle>) -> impl IntoResponse {
    let (processed, failed) = state.get_stats();
    let current = state.get_current_job();

    let status = if state.is_ready() { "healthy" } else { "degraded" };

    Json(HealthResponse {
        status,
        jobs_processed: processed,
        jobs_failed: failed,
        current_job: current,
    })
}

/// Create health router
pub fn health_router(state: HealthHandle) -> Router {
    Router::new()
        .route("/health", get(liveness))
        .route("/ready", get(readiness))
        .route("/status", get(health_detail))
        .with_state(state)
}

/// Start health server
pub async fn start_health_server(addr: &str, state: HealthHandle) -> Result<(), std::io::Error> {
    let app = health_router(state);

    let listener = tokio::net::TcpListener::bind(addr).await?;
    info!(addr = %addr, "Health server started");

    axum::serve(listener, app).await?;

    Ok(())
}
