# Schema

### ActiveShieldAuditLog
- id: String (pk, default)
- shield_id: String (unique, index)
- session_id: String (index)
- phase: String
- action: String
- passed: Boolean
- processed_content: String (nullable)
- violations: JSON (default)
- warnings: JSON (default)
- metadata_: JSON (default)
- audit_trail: JSON (default)
- processing_time_ms: Integer (default)
- created_at: DateTime

### ActiveShieldAdverseEvent
- id: String (pk, default)
- session_id: String (index)
- audit_log_id: String (index, nullable)
- event_type: String
- description: String
- severity: String
- context_snapshot: JSON (default)
- remediated: Boolean (default)
- remediation_notes: String (nullable)
- created_at: DateTime

### User
- id: int (pk, index)
- email: String (unique, index)
- hashed_password: String
- is_active: Boolean (default)
- created_at: DateTime
- _relations_: workspace_links: 

### Workspace
- id: int (pk, index)
- name: String
- created_at: DateTime
- _relations_: members: , agents: 

### WorkspaceMember
- workspace_id: int (fk, pk)
- user_id: int (fk, pk)
- role: Enum (default)
- _relations_: workspace: , user: 

### AIAgent
- id: int (pk, index)
- workspace_id: int (fk)
- name: String
- system_prompt: Text (nullable)
- is_active: Boolean (default)
- created_at: DateTime
- _relations_: workspace: 

### Conversation
- id: Integer (pk, index)
- user_id: Integer (fk)
- project_id: Integer (fk, nullable)
- title: String (nullable)
- is_incognito: Boolean (default)
- summary: Text (nullable)
- last_summarized_at: DateTime (nullable)
- is_active: Boolean (default)
- created_at: DateTime (default, index)
- updated_at: DateTime (default)
- last_message_at: DateTime (default)
- _relations_: user: User, project: Project, messages: Message

### Message
- id: Integer (pk, index)
- conversation_id: Integer (fk)
- role: String
- content: Text
- tokens: Integer (nullable)
- model: String (nullable)
- created_at: DateTime (default, index)
- _relations_: conversation: Conversation, embeddings: VectorEmbedding

### VectorEmbedding
- id: Integer (pk, index)
- message_id: Integer (fk, nullable)
- memory_id: Integer (fk, nullable)
- embedding: LargeBinary
- model_name: String
- dimension: Integer
- created_at: DateTime (default)
- _relations_: message: Message, memory: Memory

### Memory
- id: Integer (pk, index)
- user_id: Integer (fk)
- project_id: Integer (fk, nullable)
- title: String (nullable)
- content: Text
- memory_type: String (default)
- source_conversation_ids: Text (nullable)
- confidence_score: Float (default)
- is_active: Boolean (default)
- is_user_edited: Boolean (default)
- created_at: DateTime (default, index)
- updated_at: DateTime (default)
- last_accessed_at: DateTime (default)
- _relations_: user: User, project: Project, embeddings: VectorEmbedding

### PerformanceMetric
- id: Integer (pk, index)
- endpoint: String (index)
- method: String
- duration: Float
- timestamp: DateTime (default, index)
- status_code: Integer
- memory_usage: Float (nullable)
- cpu_usage: Float (nullable)
- query_params: JSON (nullable)
- request_body_size: Integer (nullable)
- response_body_size: Integer (nullable)
- error: Text (nullable)

### Bottleneck
- id: Integer (pk, index)
- endpoint: String (index)
- line_number: Integer (nullable)
- file_path: String (nullable)
- function_name: String
- duration: Float
- call_count: Integer
- percentage: Float
- detected_at: DateTime (default)
- severity: String

### OptimizationSuggestion
- id: Integer (pk, index)
- endpoint: String (index)
- suggestion_type: String
- description: Text
- impact: String
- implementation: Text (nullable)
- created_at: DateTime (default)
- applied: Integer (default)

### Project
- id: Integer (pk, index)
- user_id: Integer (fk)
- name: String
- description: Text (nullable)
- memory_enabled: Boolean (default)
- summary: Text (nullable)
- last_synthesis_at: DateTime (nullable)
- created_at: DateTime (default)
- updated_at: DateTime (default)
- _relations_: user: User, conversations: Conversation, memories: Memory

### User
- id: Integer (pk, index)
- email: String (unique, index)
- username: String (unique, index)
- hashed_password: String
- is_active: Boolean (default)
- is_superuser: Boolean (default)
- memory_enabled: Boolean (default)
- auto_summarization_enabled: Boolean (default)
- created_at: DateTime (default)
- updated_at: DateTime (default)
- last_login: DateTime (nullable)
- _relations_: projects: Project, conversations: Conversation, memories: Memory

### APIKey
- id: String
- key_prefix: String
- email: String
- organization: String
- tier: unknown
- monthly_limit: Integer (default)
- current_month_usage: Integer (default)
- usage_reset_date: DateTime
- is_active: Boolean (default)
- last_used_at: DateTime (nullable)
- expires_at: DateTime (nullable)
- stripe_customer_id: String
- stripe_subscription_id: String

### UsageRecord
- id: Integer (pk)
- api_key_id: String
- timestamp: DateTime (default)
- endpoint: String
- decision_id: String
- risk_level: String
- disposition: String
- latency_ms: Integer (nullable)
- billable: Boolean (default)

### DualCoMetricHistory
- id: String (pk, default)
- period_start: DateTime
- period_end: DateTime
- recorded_at: DateTime (default)
- metrics_data: JSON
- gate_status_snapshot: JSON (nullable)

### DualCoDecision
- id: String (pk, default)
- decision_date: DateTime (default)
- context: Text
- options_considered: JSON
- chosen_option: Text
- why_first_principles: Text
- metrics_to_watch: JSON
- kill_criteria: Text
- owner: String
- review_cadence: String (default)

### DualCoGateState
- gate_name: String (pk)
- status: String (default)
- consecutive_failures: Integer (default)
- last_evaluated_at: DateTime (nullable)
- last_metric_snapshot_id: String (fk)

### Experiment
- id: String (pk)
- hypothesis_id: String (fk)
- experiment_type: String
- description: Text
- protocol: JSON
- status: unknown (default)
- domain: String
- code_generated: Text (nullable)
- execution_time_seconds: Float (nullable)
- error_message: Text (nullable)
- created_at: DateTime (default)
- started_at: DateTime (nullable)
- completed_at: DateTime (nullable)
- _relations_: hypothesis: Hypothesis, results: Result

### Hypothesis
- id: String (pk)
- research_question: Text
- statement: Text
- rationale: Text
- domain: String
- status: unknown (default)
- novelty_score: Float (nullable)
- testability_score: Float (nullable)
- confidence_score: Float (nullable)
- related_papers: JSON (nullable)
- created_at: DateTime (default)
- updated_at: DateTime (default)
- _relations_: experiments: Experiment

### Result
- id: String (pk)
- experiment_id: String (fk)
- data: JSON
- statistical_tests: JSON (nullable)
- interpretation: Text (nullable)
- key_findings: JSON (nullable)
- supports_hypothesis: Boolean (nullable)
- p_value: Float (nullable)
- effect_size: Float (nullable)
- confidence_interval: JSON (nullable)
- figures: JSON (nullable)
- created_at: DateTime (default)
- _relations_: experiment: Experiment

### Paper
- id: String (pk)
- title: String
- authors: JSON
- abstract: Text
- source: String
- url: String (nullable)
- doi: String (nullable)
- arxiv_id: String (nullable)
- publication_date: DateTime (nullable)
- domain: String (nullable)
- keywords: JSON (nullable)
- summary: Text (nullable)
- key_methods: JSON (nullable)
- key_findings: JSON (nullable)
- relevance_score: Float (nullable)
- embedding: JSON (nullable)
- created_at: DateTime (default)
- analyzed_at: DateTime (nullable)

### AgentRecord
- id: String (pk)
- agent_type: String
- status: String
- config: JSON (nullable)
- state_data: JSON (nullable)
- messages_sent: Integer (default)
- messages_received: Integer (default)
- tasks_completed: Integer (default)
- errors_encountered: Integer (default)
- created_at: DateTime (default)
- updated_at: DateTime (default)
- stopped_at: DateTime (nullable)

### ResearchSession
- id: String (pk)
- research_question: Text
- domain: String
- status: String (default)
- iteration: Integer (default)
- hypotheses_generated: Integer (default)
- experiments_completed: Integer (default)
- discoveries_made: JSON (nullable)
- max_iterations: Integer (default)
- autonomous_mode: Boolean (default)
- created_at: DateTime (default)
- updated_at: DateTime (default)
- completed_at: DateTime (nullable)
