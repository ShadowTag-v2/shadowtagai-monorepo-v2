# GKE Inference Deployment Scripts

Production-grade deployment scripts for AI/ML inference workloads on Google Kubernetes Engine (GKE), based on the [GoogleCloudPlatform/accelerated-platforms](https://github.com/GoogleCloudPlatform/accelerated-platforms) inference reference architecture.

## Overview

This repository contains automated deployment scripts for running large language models (LLMs) and diffusion models on GKE with GPU/TPU acceleration. The scripts follow Google Cloud best practices for:

- **Scalability**: Horizontal and vertical autoscaling
- **Cost Optimization**: Efficient resource utilization
- **High Availability**: Multi-zone deployments
- **Observability**: Comprehensive monitoring and logging
- **Security**: Workload Identity, IAM, and secret management

## Architecture

The deployment implements the GKE Inference Reference Architecture with:

- **Model Storage**: Cloud Storage with GCS FUSE CSI driver
- **Inference Runtime**: vLLM for LLMs, Diffusers for image generation
- **Load Balancing**: GKE Inference Gateway for AI-aware routing
- **Autoscaling**: Horizontal Pod Autoscaler with custom metrics
- **GPU Support**: NVIDIA L4, H100, H200
- **TPU Support**: Cloud TPU v5e, v6e

## Prerequisites

- Google Cloud Project with billing enabled
- `gcloud` CLI installed and authenticated
- `kubectl` installed (v1.28+)
- `terraform` installed (v1.0+)
- Hugging Face account with model access
- Sufficient GPU/TPU quota in target region

## Quick Start

### 1. Setup Environment

```bash
# Interactive setup
./00-setup-environment.sh

# Load configuration
source .env.gcp-inference
```

### 2. Enable GCP Services

```bash
./01-enable-gcp-services.sh
```

### 3. Create Infrastructure

```bash
./02-setup-infrastructure.sh
```

### 4. Configure Hugging Face

```bash
./03-setup-huggingface.sh
```

### 5. Download Model

```bash
# Interactive model selection
./04-download-model.sh

# Or specify model directly
export HF_MODEL_ID="google/gemma-3-27b-it"
./04-download-model.sh

# Load model configuration
source .env.model-info
```

### 6. Deploy Inference

```bash
# Deploy vLLM inference
./05-deploy-vllm-inference.sh

# Select accelerator when prompted:
# 1) NVIDIA L4
# 2) NVIDIA H100
# 3) NVIDIA H200
```

### 7. Test Deployment

```bash
./06-test-inference.sh
```

### 8. Monitor

```bash
# Continuous monitoring
./07-monitor-deployment.sh

# Single snapshot
./07-monitor-deployment.sh once
```

## Script Reference

| Script | Purpose | Runtime |
|--------|---------|---------|
| `00-setup-environment.sh` | Configure project settings | 2-5 min |
| `01-enable-gcp-services.sh` | Enable required GCP APIs | 5-10 min |
| `02-setup-infrastructure.sh` | Create GKE cluster and storage | 10-15 min |
| `03-setup-huggingface.sh` | Configure model access | 1-2 min |
| `04-download-model.sh` | Download model to GCS | 5-30 min* |
| `05-deploy-vllm-inference.sh` | Deploy inference workload | 10-20 min |
| `06-test-inference.sh` | Run inference tests | 2-5 min |
| `07-monitor-deployment.sh` | Monitor deployment health | Continuous |
| `99-cleanup.sh` | Delete resources | 5-15 min |

*Model download time varies by size: 1B models ~5min, 70B models ~30min

## Supported Models

### LLM Models (vLLM)

| Model | Size | Compatible GPUs | Machine Type |
|-------|------|----------------|--------------|
| Gemma 3 1B IT | 1B | L4 | g2-standard-24 |
| Gemma 3 4B IT | 4B | L4 | g2-standard-48 |
| Gemma 3 27B IT | 27B | L4, H100, H200 | g2-standard-96 |
| Llama 3.3 70B | 70B | H100, H200 | a3-highgpu-4g |
| Llama 4 Scout 17B | 17B | H100, H200 | a3-highgpu-8g |
| Qwen 3 32B | 32B | L4, H100, H200 | g2-standard-96 |

### Diffusion Models

| Model | Compatible GPUs | Use Case |
|-------|----------------|----------|
| FLUX.1-schnell | L4, H100 | Fast image generation |

## GPU Selection Guide

### NVIDIA L4 (g2-standard-96)
- **Cost**: $$ (most cost-effective)
- **Performance**: Good for models up to 32B
- **Best for**: Development, smaller models
- **Memory**: 24GB per GPU

### NVIDIA H100 (a3-highgpu)
- **Cost**: $$$ (high-end)
- **Performance**: Excellent for all models
- **Best for**: Production workloads, 70B+ models
- **Memory**: 80GB per GPU

### NVIDIA H200 (a3-ultragpu)
- **Cost**: $$$$ (premium)
- **Performance**: Maximum for largest models
- **Best for**: Frontier models, memory-intensive workloads
- **Memory**: 141GB per GPU

## Advanced Usage

### Custom Model Deployment

```bash
# Set custom model
export HF_MODEL_ID="organization/custom-model"
export ACCELERATOR_TYPE="h100"

# Download and deploy
./04-download-model.sh
source .env.model-info
./05-deploy-vllm-inference.sh
```

### Scaling Deployment

```bash
# Scale replicas
kubectl scale deployment/vllm-${ACCELERATOR_TYPE}-${HF_MODEL_NAME} \
  -n inference-online-gpu --replicas=3

# Update HPA limits
kubectl patch hpa vllm-${ACCELERATOR_TYPE}-${HF_MODEL_NAME} \
  -n inference-online-gpu \
  -p '{"spec":{"maxReplicas":10}}'
```

### Multi-Region Deployment

```bash
# Deploy in multiple regions
REGIONS=("us-central1" "europe-west4" "asia-northeast1")

for region in "${REGIONS[@]}"; do
  export REGION="$region"
  ./00-setup-environment.sh
  ./02-setup-infrastructure.sh
  # Continue with deployment...
done
```

### Access Inference API

```bash
# Port forward
kubectl port-forward -n inference-online-gpu \
  svc/vllm-${ACCELERATOR_TYPE}-${HF_MODEL_NAME} 8000:8000

# Test API
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "/gcs/google/gemma-3-27b-it",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Monitoring & Observability

### Cloud Console

- **GKE Workloads**: [console.cloud.google.com/kubernetes/workload](https://console.cloud.google.com/kubernetes/workload)
- **Cloud Monitoring**: [console.cloud.google.com/monitoring](https://console.cloud.google.com/monitoring)
- **Cloud Logging**: [console.cloud.google.com/logs](https://console.cloud.google.com/logs)

### kubectl Commands

```bash
# View deployment status
kubectl get deployment,pod,svc,hpa -n inference-online-gpu

# View logs
kubectl logs -n inference-online-gpu \
  -l model=${HF_MODEL_NAME} --tail=100 -f

# Check GPU utilization
kubectl exec -n inference-online-gpu <pod-name> -- nvidia-smi

# View events
kubectl get events -n inference-online-gpu --sort-by='.lastTimestamp'
```

### Metrics

Key metrics to monitor:

- **Latency**: p50, p90, p99 response times
- **Throughput**: Requests per second (QPS)
- **GPU Utilization**: % GPU compute usage
- **GPU Memory**: Used vs. available memory
- **Error Rate**: 4xx/5xx errors per second
- **Pod Count**: Current vs. desired replicas

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod -n inference-online-gpu <pod-name>

# Common issues:
# - Insufficient GPU quota: Request quota increase
# - Image pull errors: Check artifact registry permissions
# - OOM errors: Reduce batch size or use larger GPU
```

### Model Download Fails

```bash
# Check job logs
kubectl logs -n model-download job/<job-name>

# Common issues:
# - Invalid HF token: Update token in Secret Manager
# - Model access denied: Accept model license on Hugging Face
# - Network timeout: Retry download
```

### High Latency

```bash
# Check GPU utilization
./07-monitor-deployment.sh

# Solutions:
# - Scale up replicas: kubectl scale deployment/...
# - Use larger GPU: Redeploy with H100/H200
# - Enable tensor parallelism: Update deployment args
```

### Out of Memory

```bash
# Check memory usage
kubectl top pod -n inference-online-gpu

# Solutions:
# - Reduce max-model-len in deployment
# - Use GPU with more memory (H200)
# - Enable KV cache quantization
```

## Cost Optimization

### Recommendations

1. **Start Small**: Begin with L4 GPUs for development
2. **Right-Size**: Match GPU to model size (see compatibility matrix)
3. **Use Spot/Preemptible**: Save 60-91% with spot VMs
4. **Enable Autoscaling**: Scale to zero during idle periods
5. **Batch Requests**: Higher throughput reduces cost per request
6. **Model Optimization**: Use quantization (INT8/INT4)

### Cost Estimation

Approximate monthly costs (us-central1):

| GPU | Machine Type | Hourly | Monthly (730h) |
|-----|-------------|--------|----------------|
| L4 x8 | g2-standard-96 | $12 | $8,760 |
| H100 x1 | a3-highgpu-1g | $15 | $10,950 |
| H100 x8 | a3-highgpu-8g | $120 | $87,600 |

*Add ~10% for storage, networking, and logging costs

## Security Best Practices

1. **Workload Identity**: Enabled by default for pod-to-GCP auth
2. **IAM**: Least privilege service accounts
3. **Secret Manager**: HF tokens stored securely
4. **Network Policies**: Restrict pod-to-pod communication
5. **Binary Authorization**: Verify container images (optional)
6. **VPC Service Controls**: Perimeter security (optional)

## Cleanup

```bash
# Delete workload only
./99-cleanup.sh workload

# Delete everything (cluster, buckets, etc.)
./99-cleanup.sh all
```

## Support & Resources

- **Reference Architecture**: [accelerated-platforms/docs/inference-ref-arch](https://github.com/GoogleCloudPlatform/accelerated-platforms/tree/main/docs/platforms/gke/base/use-cases/inference-ref-arch)
- **GKE AI Docs**: [cloud.google.com/kubernetes-engine/docs/integrations/ai-infra](https://cloud.google.com/kubernetes-engine/docs/integrations/ai-infra)
- **vLLM Docs**: [docs.vllm.ai](https://docs.vllm.ai)
- **Hugging Face**: [huggingface.co/docs](https://huggingface.co/docs)

## License

Based on GoogleCloudPlatform/accelerated-platforms (Apache 2.0)

## Generated

These scripts were generated from the GKE Inference Reference Architecture on 2025-11-08.
