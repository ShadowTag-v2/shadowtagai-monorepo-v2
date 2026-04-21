# Database

> **Navigation aid.** Schema shapes and field types extracted via AST. Read the actual schema source files before writing migrations or query logic.

**sqlalchemy** — 26 models

### ActiveShieldAuditLog

pk: `id` (String)

- `id`: String _(pk, default)_
- `shield_id`: String _(unique, index)_
- `session_id`: String _(index)_
- `phase`: String
- `action`: String
- `passed`: Boolean
- `processed_content`: String _(nullable)_
- `violations`: JSON _(default)_
- `warnings`: JSON _(default)_
- `metadata_`: JSON _(default)_
- `audit_trail`: JSON _(default)_
- `processing_time_ms`: Integer _(default)_
- `created_at`: DateTime

### ActiveShieldAdverseEvent

pk: `id` (String)

- `id`: String _(pk, default)_
- `session_id`: String _(index)_
- `audit_log_id`: String _(index, nullable)_
- `event_type`: String
- `description`: String
- `severity`: String
- `context_snapshot`: JSON _(default)_
- `remediated`: Boolean _(default)_
- `remediation_notes`: String _(nullable)_
- `created_at`: DateTime

### User

pk: `id` (int)

- `id`: int _(pk, index)_
- `email`: String _(unique, index)_
- `hashed_password`: String
- `is_active`: Boolean _(default)_
- `created_at`: DateTime
- _relations_: workspace_links: 

### Workspace

pk: `id` (int)

- `id`: int _(pk, index)_
- `name`: String
- `created_at`: DateTime
- _relations_: members: , agents: 

### WorkspaceMember

pk: `workspace_id` (int) · fk: workspace_id, user_id

- `workspace_id`: int _(fk, pk)_
- `user_id`: int _(fk, pk)_
- `role`: Enum _(default)_
- _relations_: workspace: , user: 

### AIAgent

pk: `id` (int) · fk: workspace_id

- `id`: int _(pk, index)_
- `workspace_id`: int _(fk)_
- `name`: String
- `system_prompt`: Text _(nullable)_
- `is_active`: Boolean _(default)_
- `created_at`: DateTime
- _relations_: workspace: 

### Conversation

pk: `id` (Integer) · fk: user_id, project_id

- `id`: Integer _(pk, index)_
- `user_id`: Integer _(fk)_
- `project_id`: Integer _(fk, nullable)_
- `title`: String _(nullable)_
- `is_incognito`: Boolean _(default)_
- `summary`: Text _(nullable)_
- `last_summarized_at`: DateTime _(nullable)_
- `is_active`: Boolean _(default)_
- `created_at`: DateTime _(default, index)_
- `updated_at`: DateTime _(default)_
- `last_message_at`: DateTime _(default)_
- _relations_: user: User, project: Project, messages: Message

### Message

pk: `id` (Integer) · fk: conversation_id

- `id`: Integer _(pk, index)_
- `conversation_id`: Integer _(fk)_
- `role`: String
- `content`: Text
- `tokens`: Integer _(nullable)_
- `model`: String _(nullable)_
- `created_at`: DateTime _(default, index)_
- _relations_: conversation: Conversation, embeddings: VectorEmbedding

### VectorEmbedding

pk: `id` (Integer) · fk: message_id, memory_id

- `id`: Integer _(pk, index)_
- `message_id`: Integer _(fk, nullable)_
- `memory_id`: Integer _(fk, nullable)_
- `embedding`: LargeBinary
- `model_name`: String
- `dimension`: Integer
- `created_at`: DateTime _(default)_
- _relations_: message: Message, memory: Memory

### Memory

pk: `id` (Integer) · fk: user_id, project_id

- `id`: Integer _(pk, index)_
- `user_id`: Integer _(fk)_
- `project_id`: Integer _(fk, nullable)_
- `title`: String _(nullable)_
- `content`: Text
- `memory_type`: String _(default)_
- `source_conversation_ids`: Text _(nullable)_
- `confidence_score`: Float _(default)_
- `is_active`: Boolean _(default)_
- `is_user_edited`: Boolean _(default)_
- `created_at`: DateTime _(default, index)_
- `updated_at`: DateTime _(default)_
- `last_accessed_at`: DateTime _(default)_
- _relations_: user: User, project: Project, embeddings: VectorEmbedding

### PerformanceMetric

pk: `id` (Integer)

- `id`: Integer _(pk, index)_
- `endpoint`: String _(index)_
- `method`: String
- `duration`: Float
- `timestamp`: DateTime _(default, index)_
- `status_code`: Integer
- `memory_usage`: Float _(nullable)_
- `cpu_usage`: Float _(nullable)_
- `query_params`: JSON _(nullable)_
- `request_body_size`: Integer _(nullable)_
- `response_body_size`: Integer _(nullable)_
- `error`: Text _(nullable)_

### Bottleneck

pk: `id` (Integer)

- `id`: Integer _(pk, index)_
- `endpoint`: String _(index)_
- `line_number`: Integer _(nullable)_
- `file_path`: String _(nullable)_
- `function_name`: String
- `duration`: Float
- `call_count`: Integer
- `percentage`: Float
- `detected_at`: DateTime _(default)_
- `severity`: String

### OptimizationSuggestion

pk: `id` (Integer)

- `id`: Integer _(pk, index)_
- `endpoint`: String _(index)_
- `suggestion_type`: String
- `description`: Text
- `impact`: String
- `implementation`: Text _(nullable)_
- `created_at`: DateTime _(default)_
- `applied`: Integer _(default)_

### Project

pk: `id` (Integer) · fk: user_id

- `id`: Integer _(pk, index)_
- `user_id`: Integer _(fk)_
- `name`: String
- `description`: Text _(nullable)_
- `memory_enabled`: Boolean _(default)_
- `summary`: Text _(nullable)_
- `last_synthesis_at`: DateTime _(nullable)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_
- _relations_: user: User, conversations: Conversation, memories: Memory

### User

pk: `id` (Integer)

- `id`: Integer _(pk, index)_
- `email`: String _(unique, index)_
- `username`: String _(unique, index)_
- `hashed_password`: String
- `is_active`: Boolean _(default)_
- `is_superuser`: Boolean _(default)_
- `memory_enabled`: Boolean _(default)_
- `auto_summarization_enabled`: Boolean _(default)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_
- `last_login`: DateTime _(nullable)_
- _relations_: projects: Project, conversations: Conversation, memories: Memory

### APIKey

- `id`: String
- `key_prefix`: String
- `email`: String
- `organization`: String
- `tier`: unknown
- `monthly_limit`: Integer _(default)_
- `current_month_usage`: Integer _(default)_
- `usage_reset_date`: DateTime
- `is_active`: Boolean _(default)_
- `last_used_at`: DateTime _(nullable)_
- `expires_at`: DateTime _(nullable)_
- `stripe_customer_id`: String
- `stripe_subscription_id`: String

### UsageRecord

pk: `id` (Integer)

- `id`: Integer _(pk)_
- `api_key_id`: String
- `timestamp`: DateTime _(default)_
- `endpoint`: String
- `decision_id`: String
- `risk_level`: String
- `disposition`: String
- `latency_ms`: Integer _(nullable)_
- `billable`: Boolean _(default)_

### DualCoMetricHistory

pk: `id` (String)

- `id`: String _(pk, default)_
- `period_start`: DateTime
- `period_end`: DateTime
- `recorded_at`: DateTime _(default)_
- `metrics_data`: JSON
- `gate_status_snapshot`: JSON _(nullable)_

### DualCoDecision

pk: `id` (String)

- `id`: String _(pk, default)_
- `decision_date`: DateTime _(default)_
- `context`: Text
- `options_considered`: JSON
- `chosen_option`: Text
- `why_first_principles`: Text
- `metrics_to_watch`: JSON
- `kill_criteria`: Text
- `owner`: String
- `review_cadence`: String _(default)_

### DualCoGateState

pk: `gate_name` (String) · fk: last_metric_snapshot_id

- `gate_name`: String _(pk)_
- `status`: String _(default)_
- `consecutive_failures`: Integer _(default)_
- `last_evaluated_at`: DateTime _(nullable)_
- `last_metric_snapshot_id`: String _(fk)_

### Experiment

pk: `id` (String) · fk: hypothesis_id

- `id`: String _(pk)_
- `hypothesis_id`: String _(fk)_
- `experiment_type`: String
- `description`: Text
- `protocol`: JSON
- `status`: unknown _(default)_
- `domain`: String
- `code_generated`: Text _(nullable)_
- `execution_time_seconds`: Float _(nullable)_
- `error_message`: Text _(nullable)_
- `created_at`: DateTime _(default)_
- `started_at`: DateTime _(nullable)_
- `completed_at`: DateTime _(nullable)_
- _relations_: hypothesis: Hypothesis, results: Result

### Hypothesis

pk: `id` (String)

- `id`: String _(pk)_
- `research_question`: Text
- `statement`: Text
- `rationale`: Text
- `domain`: String
- `status`: unknown _(default)_
- `novelty_score`: Float _(nullable)_
- `testability_score`: Float _(nullable)_
- `confidence_score`: Float _(nullable)_
- `related_papers`: JSON _(nullable)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_
- _relations_: experiments: Experiment

### Result

pk: `id` (String) · fk: experiment_id

- `id`: String _(pk)_
- `experiment_id`: String _(fk)_
- `data`: JSON
- `statistical_tests`: JSON _(nullable)_
- `interpretation`: Text _(nullable)_
- `key_findings`: JSON _(nullable)_
- `supports_hypothesis`: Boolean _(nullable)_
- `p_value`: Float _(nullable)_
- `effect_size`: Float _(nullable)_
- `confidence_interval`: JSON _(nullable)_
- `figures`: JSON _(nullable)_
- `created_at`: DateTime _(default)_
- _relations_: experiment: Experiment

### Paper

pk: `id` (String)

- `id`: String _(pk)_
- `title`: String
- `authors`: JSON
- `abstract`: Text
- `source`: String
- `url`: String _(nullable)_
- `doi`: String _(nullable)_
- `arxiv_id`: String _(nullable)_
- `publication_date`: DateTime _(nullable)_
- `domain`: String _(nullable)_
- `keywords`: JSON _(nullable)_
- `summary`: Text _(nullable)_
- `key_methods`: JSON _(nullable)_
- `key_findings`: JSON _(nullable)_
- `relevance_score`: Float _(nullable)_
- `embedding`: JSON _(nullable)_
- `created_at`: DateTime _(default)_
- `analyzed_at`: DateTime _(nullable)_

### AgentRecord

pk: `id` (String)

- `id`: String _(pk)_
- `agent_type`: String
- `status`: String
- `config`: JSON _(nullable)_
- `state_data`: JSON _(nullable)_
- `messages_sent`: Integer _(default)_
- `messages_received`: Integer _(default)_
- `tasks_completed`: Integer _(default)_
- `errors_encountered`: Integer _(default)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_
- `stopped_at`: DateTime _(nullable)_

### ResearchSession

pk: `id` (String)

- `id`: String _(pk)_
- `research_question`: Text
- `domain`: String
- `status`: String _(default)_
- `iteration`: Integer _(default)_
- `hypotheses_generated`: Integer _(default)_
- `experiments_completed`: Integer _(default)_
- `discoveries_made`: JSON _(nullable)_
- `max_iterations`: Integer _(default)_
- `autonomous_mode`: Boolean _(default)_
- `created_at`: DateTime _(default)_
- `updated_at`: DateTime _(default)_
- `completed_at`: DateTime _(nullable)_

## Schema Source Files

Search for ORM schema declarations:
- Drizzle: `pgTable` / `mysqlTable` / `sqliteTable`
- Prisma: `prisma/schema.prisma`
- TypeORM: `@Entity()` decorator
- SQLAlchemy: class inheriting `Base`

---
_Back to [overview.md](./overview.md)_