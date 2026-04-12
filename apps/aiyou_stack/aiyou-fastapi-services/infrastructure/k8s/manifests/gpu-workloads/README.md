# GPU Workload Manifests

Example Kubernetes manifests for deploying GPU workloads on GKE.

## Files


- **gpu-test-pod.yaml**: Simple test pod to verify GPU access

- **example-inference-deployment.yaml**: Production inference service with auto-scaling

- **example-training-job.yaml**: Distributed training job using Kubeflow PyTorchJob

## Prerequisites


1. GKE cluster with GPU nodes deployed (see `k8s/terraform/`)

2. NVIDIA GPU Operator installed

3. kubectl configured to access cluster

## Quick Test

### 1. Verify GPU Nodes

```bash

# Check GPU nodes are ready

kubectl get nodes -l cloud.google.com/gke-accelerator -o wide

# Should see nodes with labels:

# - workload=inference,fine-tuning,training,batch

# - gpu=l4,a100,h100

```

### 2. Run GPU Test Pod

```bash

# Deploy test pod

kubectl apply -f gpu-test-pod.yaml

# Wait for completion

kubectl wait --for=condition=Ready pod/gpu-test -n ml-training --timeout=5m

# View output

kubectl logs gpu-test -n ml-training

# Expected output includes:

# - nvidia-smi showing GPU details

# - CUDA samples deviceQuery passing

# Clean up

kubectl delete -f gpu-test-pod.yaml

```

## Deploy Inference Service

### 1. Customize Configuration

Edit `example-inference-deployment.yaml`:

```yaml
env:

  - name: MODEL_NAME
    value: "your-model-name"  # Change this

  - name: MODEL_PATH
    value: "gs://your-bucket/model"  # Change this

```

### 2. Deploy

```bash

# Create namespace if not exists

kubectl create namespace production

# Deploy inference service

kubectl apply -f example-inference-deployment.yaml

# Check deployment

kubectl get deployments -n production
kubectl get pods -n production
kubectl get svc -n production

# View logs

kubectl logs -n production -l app=llm-inference -f

```

### 3. Test Inference

```bash

# Port-forward to test locally

kubectl port-forward -n production svc/llm-inference-service 8080:80

# Test endpoint

curl -X POST http://localhost:8080/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain machine learning in simple terms",
    "max_tokens": 100
  }'

```

### 4. Check Auto-Scaling

```bash

# View HPA status

kubectl get hpa -n production

# Generate load to trigger scaling

# (use load testing tool like k6, locust, etc.)

# Watch pods scale up

kubectl get pods -n production -w

```

## Run Training Job

### 1. Prepare Dataset

```bash

# Upload training data to GCS

gsutil -m cp -r ./training-data gs://omega-data/fine-tune-dataset/

```

### 2. Customize Job

Edit `example-training-job.yaml`:

```yaml
args:

  - --model=your-base-model

  - --dataset=gs://your-bucket/dataset

  - --output=gs://your-bucket/output

  - --epochs=3

  - --batch-size=32

```

### 3. Deploy Training Job

```bash

# Create namespace if not exists

kubectl create namespace ml-training

# Create checkpoint PVC

kubectl apply -f example-training-job.yaml

# Check job status

kubectl get pytorchjob -n ml-training
kubectl get pods -n ml-training

# View training logs (master)

kubectl logs -n ml-training llama-finetune-job-master-0 -f

# View training logs (all workers)

kubectl logs -n ml-training -l role=worker -f

```

### 4. Monitor Training

```bash

# Check GPU utilization

kubectl exec -n ml-training llama-finetune-job-master-0 -- nvidia-smi

# Check training progress

kubectl logs -n ml-training llama-finetune-job-master-0 | grep -i "epoch\|loss\|accuracy"

# View tensorboard (if configured)

kubectl port-forward -n ml-training svc/tensorboard 6006:6006

# Open http://localhost:6006

```

### 5. Retrieve Trained Model

```bash

# Model is automatically saved to GCS

gsutil ls gs://omega-models/llama-7b-finetuned/

# Download locally if needed

gsutil -m cp -r gs://omega-models/llama-7b-finetuned/ ./models/

```

## Resource Limits

### GPU Allocation

All manifests request specific GPU counts:

| Workload | GPUs | Memory | CPU |
|----------|------|--------|-----|
| Test Pod | 1 | 8Gi | 4 |
| Inference | 1 | 32Gi | 8 |
| Training (per replica) | 2 | 128Gi | 32 |

### Cost Estimates

Based on GCP pricing (us-central1):

| Workload | Node Type | Cost/hour | Daily (8h) |
|----------|-----------|-----------|------------|
| Inference (2 pods) | 2× L4 | $1.40 | $11.20 |
| Training (4 replicas) | 4× A100 2-GPU | $24.00 | $192.00 |

## Best Practices

### 1. Resource Management

```yaml

# Always set both requests and limits

resources:
  requests:  # What you need
    nvidia.com/gpu: "1"
    memory: "16Gi"
  limits:    # Maximum allowed
    nvidia.com/gpu: "1"
    memory: "32Gi"

```

### 2. Shared Memory

```yaml

# Increase /dev/shm for PyTorch DataLoader

volumes:

  - name: dshm
    emptyDir:
      medium: Memory
      sizeLimit: "32Gi"  # Match memory request

```

### 3. Checkpointing

```yaml

# Save checkpoints frequently for spot instances


- --checkpoint-interval=15  # Every 15 minutes

- --resume-from-checkpoint=/workspace/checkpoints/latest

```

### 4. Node Selection

```yaml

# Target specific GPU types

nodeSelector:
  gpu: l4  # or a100, h100
  workload: inference  # or fine-tuning, training

# Tolerate GPU taint

tolerations:

  - key: nvidia.com/gpu
    operator: Exists
    effect: NoSchedule

```

## Troubleshooting

### Pod Stuck in Pending

```bash

# Check events

kubectl describe pod <pod-name> -n <namespace>

# Common causes:

# - Insufficient GPU nodes (scale up node pool)

# - Resource requests too high (reduce memory/CPU)

# - Node selector mismatch (check labels)

```

### GPU Not Detected

```bash

# Check if GPU Operator is running

kubectl get pods -n gpu-operator

# Check node GPU allocation

kubectl describe node <node-name> | grep nvidia.com/gpu

# Check device plugin logs

kubectl logs -n gpu-operator -l app=nvidia-device-plugin-daemonset

```

### OOM (Out of Memory)

```bash

# Check pod memory usage

kubectl top pod <pod-name> -n <namespace>

# Solutions:

# - Increase memory request/limit

# - Reduce batch size

# - Enable gradient checkpointing

# - Use mixed precision (fp16)

```

### Training Job Fails

```bash

# Check master logs

kubectl logs -n ml-training llama-finetune-job-master-0

# Check worker logs

kubectl logs -n ml-training llama-finetune-job-worker-0

# Common issues:

# - NCCL communication failure (check network)

# - OOM (reduce batch size)

# - Data loading errors (check GCS permissions)

```

## Advanced Topics

### Multi-Node Training

For 8-GPU training across multiple nodes:

```yaml

# Use placement policy in node pool

placement_policy {
  type = "COMPACT"
}

# Enable InfiniBand (for a3-highgpu)

# Use NCCL with IB:

env:

  - name: NCCL_IB_DISABLE
    value: "0"

  - name: NCCL_NET_GDR_LEVEL
    value: "5"

```

### Model Caching

```yaml

# Cache models locally to avoid repeated downloads

volumes:

  - name: model-cache
    persistentVolumeClaim:
      claimName: model-cache-pvc

volumeMounts:

  - name: model-cache
    mountPath: /root/.cache/huggingface

```

### GPU Sharing

For multiple small workloads on one GPU:

```yaml

# Time-sharing (configured in node pool)

gpu_sharing_strategy = "TIME_SHARING"
max_shared_clients_per_gpu = 4

# Request fraction of GPU

resources:
  requests:
    nvidia.com/gpu: "0.5"  # Half a GPU

```

## Related Documentation


- [GKE GPU Integration Guide](../../../docs/architecture/gke-gpu-integration.md)

- [GPU Infrastructure Strategy](../../../docs/architecture/gpu-infrastructure-strategy.md)

- [Terraform Configuration](../../terraform/README.md)

## Support

For questions or issues:

- **Internal**: #gpu-infrastructure Slack

- **GKE Docs**: https://cloud.google.com/kubernetes-engine/docs/how-to/gpus

- **NVIDIA GPU Operator**: https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/
