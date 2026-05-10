//! Claurst — Rust-based Agent Execution Loop
//!
//! High-performance agent loop for ShadowTagAI with sub-millisecond
//! latency for real-time inference routing decisions.

use anyhow::Result;
use serde::{Deserialize, Serialize};
use tracing::{info, warn};

/// Represents a single agent action in the execution loop.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentAction {
    pub id: String,
    pub action_type: ActionType,
    pub payload: serde_json::Value,
}

/// Types of actions the agent can perform.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ActionType {
    Inference,
    ToolCall,
    Observation,
    Decision,
    Terminate,
}

/// Agent execution loop state.
#[derive(Debug)]
pub struct AgentLoop {
    max_iterations: usize,
    current_iteration: usize,
    actions: Vec<AgentAction>,
}

impl AgentLoop {
    /// Create a new agent loop with the given max iterations.
    pub fn new(max_iterations: usize) -> Self {
        Self {
            max_iterations,
            current_iteration: 0,
            actions: Vec::new(),
        }
    }

    /// Execute one iteration of the agent loop.
    pub fn step(&mut self, action: AgentAction) -> Result<bool> {
        if self.current_iteration >= self.max_iterations {
            warn!(
                iteration = self.current_iteration,
                max = self.max_iterations,
                "Agent loop reached max iterations"
            );
            return Ok(false);
        }

        info!(
            iteration = self.current_iteration,
            action_type = ?action.action_type,
            "Executing agent action"
        );

        let should_continue = !matches!(action.action_type, ActionType::Terminate);
        self.actions.push(action);
        self.current_iteration += 1;

        Ok(should_continue)
    }

    /// Get the action history.
    pub fn history(&self) -> &[AgentAction] {
        &self.actions
    }

    /// Get the current iteration count.
    pub fn iteration(&self) -> usize {
        self.current_iteration
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter("claurst=info")
        .init();

    info!("Claurst agent loop starting");

    let mut loop_state = AgentLoop::new(100);

    // Example: Execute a single step
    let action = AgentAction {
        id: "init-001".to_string(),
        action_type: ActionType::Observation,
        payload: serde_json::json!({"message": "Agent initialized"}),
    };

    let should_continue = loop_state.step(action)?;
    info!(should_continue, "Agent loop step completed");

    info!(
        total_actions = loop_state.history().len(),
        "Claurst agent loop finished"
    );

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_agent_loop_basic() {
        let mut agent = AgentLoop::new(10);
        let action = AgentAction {
            id: "test-001".to_string(),
            action_type: ActionType::Observation,
            payload: serde_json::json!({"test": true}),
        };
        let result = agent.step(action).unwrap();
        assert!(result);
        assert_eq!(agent.iteration(), 1);
    }

    #[test]
    fn test_agent_loop_terminate() {
        let mut agent = AgentLoop::new(10);
        let action = AgentAction {
            id: "term-001".to_string(),
            action_type: ActionType::Terminate,
            payload: serde_json::json!({}),
        };
        let result = agent.step(action).unwrap();
        assert!(!result);
    }

    #[test]
    fn test_agent_loop_max_iterations() {
        let mut agent = AgentLoop::new(2);
        for i in 0..2 {
            let action = AgentAction {
                id: format!("step-{i}"),
                action_type: ActionType::Observation,
                payload: serde_json::json!({}),
            };
            agent.step(action).unwrap();
        }
        let action = AgentAction {
            id: "overflow".to_string(),
            action_type: ActionType::Observation,
            payload: serde_json::json!({}),
        };
        let result = agent.step(action).unwrap();
        assert!(!result);
    }
}
