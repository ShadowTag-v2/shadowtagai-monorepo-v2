# Kosmos Agent (GCP Native)

An autonomous AI scientist implementation based on the **Kosmos architecture** (FutureHouse), designed for **Google Cloud Platform**.

## Architecture

- **Core Loop**: ReAct (Reason -> Act -> Observe)

- **Runtime**: Python 3.11 + `uv`

- **Compute**: Google Kubernetes Engine (Autopilot recommended)

- **Cognitive**: Vertex AI (Gemini 1.5 Pro/Flash)

- **Observability**: OpenTelemetry -> Google Cloud Trace

## Quick Start (Local)

1. **Install uv** (if not installed):

   ```bash
   pip install uv
   ```

2. **Install Dependencies**:

   ```bash
   cd kosmos_agent
   uv sync
   ```

3. **Set Credentials**:

   ```bash
   export GEMINI_API_KEY="your-api-key"
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   ```

4. **Run Agent**:

   ```bash
   uv run python -m src.loop
   ```

## Deployment (GKE)

1. **Build Container**:

   ```bash
   gcloud builds submit -t gcr.io/$GOOGLE_CLOUD_PROJECT/kosmos-agent .
   ```

2. **Deploy to Cluster**:
   - Updates `k8s/deployment.yaml` with your project ID.

   ```bash
   sed -i "s/PROJECT_ID_PLACEHOLDER/$GOOGLE_CLOUD_PROJECT/g" k8s/deployment.yaml
   kubectl apply -f k8s/deployment.yaml
   ```

3. **Verify**:

   ```bash
   kubectl logs -f -l app=kosmos-agent -n kosmos-research
   ```

## Observability

- Open **Google Cloud Trace** to view the "Waterfall" of the agent's reasoning steps (`agent_step` -> `llm_call`).

- Logs are structured JSON in **Cloud Logging**.
