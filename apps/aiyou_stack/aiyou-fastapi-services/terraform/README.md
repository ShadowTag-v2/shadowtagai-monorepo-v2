# Omega Infrastructure as Code (Terraform)

Terraform configuration for provisioning Omega's GCP infrastructure.

## Overview

This Terraform configuration provisions:

- **GKE Cluster** - Kubernetes cluster for FastAPI + PNKLN services
- **VPC Network** - Private network with Cloud NAT for secure outbound access
- **Cloud Memorystore (Redis)** - Rate limiting and caching
- **Secret Manager** - Secure storage for API keys and secrets
- **IAM Service Accounts** - Workload Identity for secure GCP API access
- **Cloud SQL (Optional)** - PostgreSQL database for production

## Prerequisites

1. **GCP Project** with billing enabled
2. **Terraform** >= 1.5.0 ([Install](https://developer.hashicorp.com/terraform/downloads))
3. **gcloud CLI** ([Install](https://cloud.google.com/sdk/docs/install))
4. **GCS Bucket** for Terraform state storage

### Initial Setup

```bash
# Authenticate with GCP
gcloud auth application-default login

# Set your GCP project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable compute.googleapis.com
gcloud services enable container.googleapis.com
gcloud services enable redis.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable iam.googleapis.com

# Create GCS bucket for Terraform state
gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://omega-terraform-state
gsutil versioning set on gs://omega-terraform-state
```

## Configuration

1. Copy the example variables file:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. Edit `terraform.tfvars` with your values:
   ```hcl
   project_id  = "your-gcp-project-id"
   environment = "development"  # or "staging", "production"
   ```

3. Update the backend bucket name in `main.tf` if you used a different name:
   ```hcl
   backend "gcs" {
     bucket = "omega-terraform-state"  # Your bucket name
     prefix = "terraform/state"
   }
   ```

## Usage

### Initialize Terraform

```bash
cd terraform
terraform init
```

### Plan Infrastructure Changes

```bash
terraform plan
```

### Apply Infrastructure

```bash
terraform apply
```

**Review the plan carefully before typing "yes"!**

### Destroy Infrastructure

```bash
terraform destroy
```

**⚠️ WARNING: This will delete all resources! Use with caution.**

## Environments

### Development

```hcl
environment     = "development"
machine_type    = "n1-standard-2"
node_count      = 1
min_node_count  = 1
max_node_count  = 3
redis_tier      = "BASIC"
redis_memory_gb = 1
enable_cloud_sql = false
```

**Cost:** ~$75-100/month (1-3 nodes, basic Redis, no Cloud SQL)

### Staging

```hcl
environment     = "staging"
machine_type    = "n1-standard-2"
node_count      = 2
min_node_count  = 1
max_node_count  = 5
redis_tier      = "BASIC"
redis_memory_gb = 2
enable_cloud_sql = true
cloud_sql_tier   = "db-f1-micro"
```

**Cost:** ~$150-200/month (2-5 nodes, basic Redis, small Cloud SQL)

### Production

```hcl
environment     = "production"
machine_type    = "n1-standard-4"
node_count      = 3
min_node_count  = 3
max_node_count  = 10
redis_tier      = "STANDARD_HA"
redis_memory_gb = 4
enable_cloud_sql = true
cloud_sql_tier   = "db-n1-standard-2"
cloud_sql_disk_size = 50
```

**Cost:** ~$500-800/month (3-10 nodes, HA Redis, standard Cloud SQL)

## Post-Deployment

### 1. Configure kubectl

```bash
gcloud container clusters get-credentials $(terraform output -raw cluster_name) \
  --zone=$(terraform output -raw zone)
```

### 2. Create Kubernetes Namespace

```bash
kubectl create namespace production
kubectl create namespace staging
```

### 3. Configure Workload Identity

```bash
# Create Kubernetes service account
kubectl create serviceaccount omega-fastapi --namespace=default

# Annotate service account with GCP service account
kubectl annotate serviceaccount omega-fastapi \
  --namespace=default \
  iam.gke.io/gcp-service-account=$(terraform output -raw gke_service_account_email)
```

### 4. Store Secrets in Secret Manager

```bash
# YouTube API Key
echo -n "YOUR_YOUTUBE_API_KEY" | gcloud secrets versions add youtube-api-key --data-file=-

# Twitter Bearer Token
echo -n "YOUR_TWITTER_TOKEN" | gcloud secrets versions add twitter-bearer-token --data-file=-

# NewsAPI Key
echo -n "YOUR_NEWSAPI_KEY" | gcloud secrets versions add newsapi-key --data-file=-

# Reddit Credentials (JSON)
echo -n '{"client_id":"YOUR_CLIENT_ID","client_secret":"YOUR_CLIENT_SECRET"}' | \
  gcloud secrets versions add reddit-api-credentials --data-file=-

# FastAPI Auth Keys (JSON)
echo -n '{"customer-key-123":"tier_2","enterprise-key-456":"enterprise"}' | \
  gcloud secrets versions add fastapi-auth-keys --data-file=-

# Redis URL (from Terraform output)
echo -n "$(terraform output -raw redis_connection_string)" | \
  gcloud secrets versions add redis-url --data-file=-

# Database URL (if using Cloud SQL)
echo -n "postgresql://REDACTED_USER:REDACTED_PASS@/ShadowTag_governance?host=/cloudsql/$(terraform output -raw cloud_sql_connection_name)" | \
  gcloud secrets versions add database-url --data-file=-
```

### 5. Deploy Application

```bash
# Apply Kubernetes manifests
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml

# Check deployment status
kubectl get pods
kubectl get services
```

## Outputs

After `terraform apply`, you can view outputs:

```bash
# All outputs
terraform output

# Specific output
terraform output cluster_name
terraform output redis_host
terraform output gke_service_account_email
```

## Important Outputs

- `cluster_name` - GKE cluster name for kubectl access
- `cluster_endpoint` - GKE API endpoint (sensitive)
- `redis_host` - Redis instance hostname
- `redis_port` - Redis port (default: 6379)
- `redis_connection_string` - Full Redis connection string with auth (sensitive)
- `gke_service_account_email` - Service account for Workload Identity
- `vpc_network_name` - VPC network name
- `cloud_sql_connection_name` - Cloud SQL connection name (if enabled)

## State Management

Terraform state is stored in GCS bucket: `gs://omega-terraform-state/terraform/state`

**Security:**
- State files contain sensitive data (Redis passwords, endpoint URLs)
- Access to GCS bucket should be restricted
- Enable versioning for state rollback capability

## Troubleshooting

### Error: Quota Exceeded

```
Error: Error creating instance: googleapi: Error 403: Quota 'CPUS' exceeded.
```

**Solution:** Request quota increase in GCP Console → IAM & Admin → Quotas

### Error: API Not Enabled

```
Error: Error 403: [...] API has not been used in project
```

**Solution:** Enable the required API:
```bash
gcloud services enable <API_NAME>
```

### Error: Terraform State Locked

```
Error: Error acquiring the state lock
```

**Solution:** Release the lock (if safe):
```bash
terraform force-unlock LOCK_ID
```

### GKE Cluster Not Reachable

```
Unable to connect to the server: dial tcp [...]: i/o timeout
```

**Solution:** Configure kubectl with correct credentials:
```bash
gcloud container clusters get-credentials <CLUSTER_NAME> --zone=<ZONE>
```

## Cost Optimization

### Development

- Use preemptible nodes (enabled by default for non-production)
- Set `min_node_count = 1` for aggressive downscaling
- Use `BASIC` Redis tier
- Disable Cloud SQL (use SQLite or external DB)

### Production

- Use regular nodes (non-preemptible)
- Set appropriate `min_node_count` for availability
- Use `STANDARD_HA` Redis for high availability
- Enable Cloud SQL with REGIONAL availability

## Security Best Practices

1. **Private GKE Nodes** - Nodes are private (no external IPs)
2. **Workload Identity** - Secure IAM integration (no service account keys)
3. **Secret Manager** - All secrets stored encrypted
4. **TLS Encryption** - Redis transit encryption enabled
5. **Auth Enabled** - Redis requires authentication
6. **Network Policies** - Implement Kubernetes network policies for pod-to-pod communication
7. **Least Privilege IAM** - Service account has minimal required permissions

## Maintenance

### Update GKE Cluster

GKE auto-upgrades are enabled. Manual upgrade:

```bash
gcloud container clusters upgrade <CLUSTER_NAME> \
  --zone=<ZONE> \
  --cluster-version=<VERSION>
```

### Resize Node Pool

```bash
gcloud container clusters resize <CLUSTER_NAME> \
  --zone=<ZONE> \
  --num-nodes=<NEW_SIZE>
```

### Rotate Secrets

```bash
# Add new secret version
echo -n "NEW_SECRET_VALUE" | gcloud secrets versions add <SECRET_ID> --data-file=-

# Disable old version
gcloud secrets versions disable <VERSION> --secret=<SECRET_ID>
```

## Terraform Modules Structure

```
terraform/
├── main.tf                 # Main infrastructure definitions
├── variables.tf            # Variable declarations
├── terraform.tfvars        # Variable values (gitignored)
├── terraform.tfvars.example # Example values (committed)
├── README.md               # This file
└── .gitignore             # Ignore sensitive files
```

## Next Steps

1. **Deploy Application** - Create Kubernetes manifests for FastAPI + PNKLN
2. **Configure Monitoring** - Set up Cloud Monitoring dashboards
3. **Set Up Alerting** - Create alerts for high CPU, memory, rate limit exceeded
4. **Implement Backups** - Configure automated backups for Cloud SQL
5. **Document Runbooks** - Create incident response procedures

## Support

For issues or questions:
- Check Terraform docs: https://registry.terraform.io/providers/hashicorp/google/latest/docs
- GCP documentation: https://cloud.google.com/docs
- File an issue in the repository
