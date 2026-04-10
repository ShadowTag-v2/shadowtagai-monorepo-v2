# SHADOWTAGAI Intelligence Pipeline - Setup Guide

This guide walks you through setting up the SHADOWTAGAI Intelligence Pipeline from scratch.

## Prerequisites

### Required Software

- Python 3.9 or higher
- Node.js 18 or higher (for Repomix)
- Git
- gcloud CLI (Google Cloud SDK)

### Required Accounts & API Keys

1. **Google Cloud Platform**
   - Active GCP project with billing enabled
   - Enabled APIs:
     - Cloud Storage API
     - BigQuery API
     - Vertex AI API
     - Cloud Logging API
     - Cloud Monitoring API

2. **OpenAI** (for embeddings)
   - API key from <https://platform.openai.com/api-keys>

3. **Voyage AI** (alternative for embeddings)
   - API key from <https://www.voyageai.com/>

4. **Reddit** (for tech news)
   - Create app at <https://www.reddit.com/prefs/apps>
   - Note down client_id and client_secret

5. **GitHub** (optional, for private repos)
   - Personal access token from <https://github.com/settings/tokens>

## Step 1: Clone and Install

```bash
# Clone repository
git clone https://github.com/ehanc69/ShadowTag-v2-fastapi-services.git
cd ShadowTag-v2-fastapi-services

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install Repomix globally
npm install -g repomix

# Verify installations
python --version  # Should be 3.9+
repomix --version
gcloud --version
```

## Step 2: GCP Setup

### 2.1 Authenticate with GCP

```bash
# Login to GCP
gcloud auth login

# Set default project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable storage.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable monitoring.googleapis.com

# Create service account for local development
gcloud iam service-accounts create shadowtagai-pipeline \
    --display-name="SHADOWTAGAI Intelligence Pipeline"

# Grant necessary permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:shadowtagai-pipeline@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:shadowtagai-pipeline@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:shadowtagai-pipeline@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.admin"

# Download service account key
gcloud iam service-accounts keys create ~/shadowtagai-sa-key.json \
    --iam-account=shadowtagai-pipeline@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=~/shadowtagai-sa-key.json
```

### 2.2 Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your values
nano .env  # or use your preferred editor
```

Fill in the following in `.env`:

```bash
# GCP Settings
GCP_PROJECT_ID=your-actual-project-id
GCP_LOCATION=us-central1

# Embedding Settings
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL_NAME=text-embedding-3-large
EMBEDDING_OPENAI_API_KEY=YOUR_API_KEY_HERE

# Reddit Settings
REDDIT_CLIENT_ID=your-reddit-client-id
REDDIT_CLIENT_SECRET=your-reddit-client-secret

# (Optional) Other settings can use defaults
```

## Step 3: Initialize Infrastructure

Run the initialization script to set up BigQuery, GCS, and Vertex AI:

```bash
python -m shadowtagai_intelligence.scripts.init_infrastructure
```

This will:

- ✓ Create BigQuery dataset and tables
- ✓ Create GCS buckets with lifecycle policies
- ✓ Initialize Vertex AI
- ✓ Set up directory structure

Expected output:

```
INFO: Creating BigQuery dataset: your-project-id.code_search
INFO: Created dataset successfully
INFO: Executing SQL statements...
INFO: BigQuery initialization completed
INFO: Creating GCS bucket: shadowtagai-code-storage-prod
INFO: Created bucket successfully
INFO: Created directory: raw/repositories/
...
INFO: Infrastructure initialization completed successfully!
```

## Step 4: Verify Setup

### 4.1 Verify BigQuery

```bash
# List tables
bq ls --project_id=YOUR_PROJECT_ID code_search

# Should show:
# - repositories
# - files
# - functions
# - code_chunks
# - research_papers
# - tech_news
# - embeddings_metadata
# - ingestion_logs
```

### 4.2 Verify GCS

```bash
# List buckets
gsutil ls gs://shadowtagai-code-storage-prod/

# Should show directory structure:
# gs://shadowtagai-code-storage-prod/raw/
# gs://shadowtagai-code-storage-prod/processed/
# gs://shadowtagai-code-storage-prod/models/
# gs://shadowtagai-code-storage-prod/indexes/
# gs://shadowtagai-code-storage-prod/logs/
```

### 4.3 Test Python Imports

```python
# Run Python shell
python

>>> from shadowtagai_intelligence.config import get_settings
>>> from shadowtagai_intelligence.ingestion import RepositoryFlattener
>>> from shadowtagai_intelligence.aggregators import ArxivAggregator
>>> from shadowtagai_intelligence.embedding import EmbeddingGenerator
>>> print("All imports successful!")
```

## Step 5: Test Components

### 5.1 Test Repository Flattening

```bash
python -c "
import asyncio
from shadowtagai_intelligence.ingestion import RepositoryFlattener

async def test():
    flattener = RepositoryFlattener()
    repo = await flattener.flatten_repository(
        'https://github.com/anthropics/anthropic-sdk-python',
        tool='gitingest'  # Faster than repomix for testing
    )
    print(f'✓ Flattened {repo.repo_name}: {repo.file_count} files, {repo.total_lines} lines')
    await flattener.close()

asyncio.run(test())
"
```

### 5.2 Test arXiv Integration

```bash
python -c "
import asyncio
from shadowtagai_intelligence.aggregators import ArxivAggregator

async def test():
    aggregator = ArxivAggregator()
    papers = await aggregator.search_papers(
        categories=['cs.AI'],
        max_results=5
    )
    print(f'✓ Found {len(papers)} papers')
    for paper in papers[:2]:
        print(f'  - {paper.title}')

asyncio.run(test())
"
```

### 5.3 Test Embedding Generation

```bash
python -c "
import asyncio
from shadowtagai_intelligence.embedding import EmbeddingGenerator

async def test():
    generator = EmbeddingGenerator()
    embedding = await generator.generate_embedding(
        'def hello_world(): print(\"Hello, World!\")',
        metadata={'type': 'test'}
    )
    print(f'✓ Generated embedding: {embedding.dimensions} dimensions')
    print(f'  Model: {embedding.model}')

asyncio.run(test())
"
```

## Step 6: Run Initial Ingestion

### 6.1 Ingest Critical Repositories (5-10 repos)

```bash
# Ingest only critical priority repositories
python -m shadowtagai_intelligence.scripts.ingest_repositories --priority critical --limit 5
```

This will take 10-30 minutes depending on repository sizes.

### 6.2 Discover Recent Papers

```bash
python -c "
import asyncio
from shadowtagai_intelligence.aggregators import ArxivAggregator

async def discover():
    aggregator = ArxivAggregator()
    papers = await aggregator.aggregate_recent_papers(days_back=7)
    print(f'Found {len(papers)} recent papers')

asyncio.run(discover())
"
```

### 6.3 Aggregate Tech News

```bash
python -c "
import asyncio
from shadowtagai_intelligence.aggregators import HackerNewsAggregator

async def aggregate():
    hn = HackerNewsAggregator()
    stories = await hn.aggregate_ai_ml_stories(days_back=7)
    print(f'Found {len(stories)} HN stories')
    await hn.close()

asyncio.run(aggregate())
"
```

## Step 7: Create Vector Search Index

After embeddings are generated, create the Vertex AI index:

```bash
python -c "
import asyncio
from shadowtagai_intelligence.search import VectorSearchManager

async def create():
    manager = VectorSearchManager()

    # Create index
    index = await manager.create_index(
        display_name='shadowtagai-code-search-v1',
        dimensions=1536  # OpenAI text-embedding-3-large
    )
    print(f'✓ Created index: {index.display_name}')

    # Create endpoint
    endpoint = await manager.create_index_endpoint(
        display_name='shadowtagai-code-endpoint-v1'
    )
    print(f'✓ Created endpoint: {endpoint.display_name}')

    # Deploy (this takes 15-30 minutes)
    print('Deploying index to endpoint (this will take 15-30 minutes)...')
    await manager.deploy_index(index, endpoint)
    print('✓ Deployment complete!')

asyncio.run(create())
"
```

## Troubleshooting

### Issue: "Permission denied" errors

**Solution**: Ensure service account has correct permissions:

```bash
gcloud projects get-iam-policy YOUR_PROJECT_ID \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:shadowtagai-pipeline@YOUR_PROJECT_ID.iam.gserviceaccount.com"
```

### Issue: "Module not found" errors

**Solution**: Ensure virtual environment is activated:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Repomix fails with "Command not found"

**Solution**: Install Repomix globally or use npx:

```bash
npm install -g repomix
# OR
npx repomix@latest --help
```

### Issue: OpenAI API rate limits

**Solution**:

1. Check your OpenAI usage limits
2. Reduce batch size: Set `EMBEDDING_BATCH_SIZE=10` in `.env`
3. Switch to Voyage AI: Set `EMBEDDING_PROVIDER=voyage`

### Issue: GCS bucket already exists

**Solution**: Use existing bucket or choose different name in `.env`:

```bash
GCP_GCS_BUCKET_RAW=shadowtagai-code-storage-prod-YOUR_UNIQUE_ID
```

## Next Steps

After successful setup:

1. **Scale Ingestion**: Ingest all 70 repositories

   ```bash
   python -m shadowtagai_intelligence.scripts.ingest_repositories
   ```

2. **Set Up Monitoring**: Configure Cloud Monitoring dashboards

3. **Automate Updates**: Set up Cloud Scheduler for daily runs

4. **Build Query API**: Create REST API for semantic search

5. **Optimize Costs**: Review and implement cost optimization strategies

## Support

For issues:

- Check logs: `ls logs/`
- Review BigQuery ingestion_logs table
- GitHub Issues: <https://github.com/ehanc69/ShadowTag-v2-fastapi-services/issues>

## Resources

- [GCP IAM Documentation](https://cloud.google.com/iam/docs)
- [Vertex AI Vector Search](https://cloud.google.com/vertex-ai/docs/vector-search)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
