//! Pub/Sub queue consumer for transcode jobs
//!
//! Pulls jobs from a Pub/Sub subscription and processes them.

use google_cloud_pubsub::client::{Client, ClientConfig};
use google_cloud_pubsub::subscriber::ReceivedMessage;
use google_cloud_pubsub::subscription::Subscription;
use std::sync::Arc;
use std::time::Duration;
use tokio::sync::mpsc;
use tracing::{debug, error, info, warn};

use crate::{Result, TranscodeError, TranscodeJob};

/// Queue consumer configuration
pub struct QueueConsumer {
    subscription: Subscription,
    max_messages: i32,
    ack_deadline: Duration,
}

impl QueueConsumer {
    /// Create a new queue consumer
    pub async fn new(
        project_id: &str,
        subscription_id: &str,
    ) -> Result<Self> {
        info!(
            project = %project_id,
            subscription = %subscription_id,
            "Initializing Pub/Sub consumer"
        );

        let config = ClientConfig::default()
            .with_auth()
            .await
            .map_err(|e| TranscodeError::PubSub(format!("Auth failed: {}", e)))?;

        let client = Client::new(config)
            .await
            .map_err(|e| TranscodeError::PubSub(format!("Client creation failed: {}", e)))?;

        let subscription = client.subscription(&format!(
            "projects/{}/subscriptions/{}",
            project_id, subscription_id
        ));

        Ok(Self {
            subscription,
            max_messages: 1, // Process one at a time for GPU jobs
            ack_deadline: Duration::from_secs(600), // 10 minute ack deadline
        })
    }

    /// Pull and process jobs
    pub async fn pull(&self) -> Result<Option<(TranscodeJob, AckHandle)>> {
        let messages = self
            .subscription
            .pull(self.max_messages, None)
            .await
            .map_err(|e| TranscodeError::PubSub(format!("Pull failed: {}", e)))?;

        if messages.is_empty() {
            return Ok(None);
        }

        let message = messages.into_iter().next().unwrap();
        let data = message.message.data.clone();

        debug!(
            message_id = %message.message.message_id,
            "Received message"
        );

        // Parse job from message data
        let job: TranscodeJob = serde_json::from_slice(&data).map_err(|e| {
            TranscodeError::PubSub(format!("Failed to parse job: {}", e))
        })?;

        info!(
            job_id = %job.job_id,
            content_id = %job.content_id,
            variants = job.variants.len(),
            "Job received"
        );

        let ack_handle = AckHandle {
            subscription: self.subscription.clone(),
            ack_id: message.ack_id.clone(),
        };

        Ok(Some((job, ack_handle)))
    }

    /// Start a continuous consumer loop
    pub async fn run<F, Fut>(
        &self,
        processor: F,
    ) -> Result<()>
    where
        F: Fn(TranscodeJob) -> Fut + Send + Sync + 'static,
        Fut: std::future::Future<Output = Result<()>> + Send,
    {
        info!("Starting queue consumer loop");

        loop {
            match self.pull().await {
                Ok(Some((job, ack_handle))) => {
                    let job_id = job.job_id;

                    match processor(job).await {
                        Ok(()) => {
                            if let Err(e) = ack_handle.ack().await {
                                error!(job_id = %job_id, error = %e, "Failed to ack message");
                            } else {
                                info!(job_id = %job_id, "Job completed and acked");
                            }
                        }
                        Err(e) => {
                            error!(job_id = %job_id, error = %e, "Job processing failed");
                            // Nack to allow retry
                            if let Err(e) = ack_handle.nack().await {
                                error!(job_id = %job_id, error = %e, "Failed to nack message");
                            }
                        }
                    }
                }
                Ok(None) => {
                    // No messages, wait before polling again
                    tokio::time::sleep(Duration::from_secs(5)).await;
                }
                Err(e) => {
                    error!(error = %e, "Failed to pull from queue");
                    tokio::time::sleep(Duration::from_secs(10)).await;
                }
            }
        }
    }
}

/// Handle for acknowledging/nacking a message
pub struct AckHandle {
    subscription: Subscription,
    ack_id: String,
}

impl AckHandle {
    /// Acknowledge the message (mark as processed)
    pub async fn ack(&self) -> Result<()> {
        self.subscription
            .ack(vec![self.ack_id.clone()])
            .await
            .map_err(|e| TranscodeError::PubSub(format!("Ack failed: {}", e)))?;
        Ok(())
    }

    /// Negative acknowledge (return to queue for retry)
    pub async fn nack(&self) -> Result<()> {
        self.subscription
            .modify_ack_deadline(vec![self.ack_id.clone()], 0)
            .await
            .map_err(|e| TranscodeError::PubSub(format!("Nack failed: {}", e)))?;
        Ok(())
    }
}

/// Publish a job to the queue (for testing/manual submission)
pub async fn publish_job(
    project_id: &str,
    topic_id: &str,
    job: &TranscodeJob,
) -> Result<String> {
    let config = ClientConfig::default()
        .with_auth()
        .await
        .map_err(|e| TranscodeError::PubSub(format!("Auth failed: {}", e)))?;

    let client = Client::new(config)
        .await
        .map_err(|e| TranscodeError::PubSub(format!("Client creation failed: {}", e)))?;

    let topic = client.topic(&format!("projects/{}/topics/{}", project_id, topic_id));

    let data = serde_json::to_vec(job)
        .map_err(|e| TranscodeError::PubSub(format!("Serialization failed: {}", e)))?;

    let publisher = topic.new_publisher(None);
    let awaiter = publisher
        .publish(google_cloud_pubsub::publisher::Message {
            data,
            ..Default::default()
        })
        .await;

    let message_id = awaiter
        .get()
        .await
        .map_err(|e| TranscodeError::PubSub(format!("Publish failed: {}", e)))?;

    info!(
        message_id = %message_id,
        job_id = %job.job_id,
        "Job published"
    );

    Ok(message_id)
}
