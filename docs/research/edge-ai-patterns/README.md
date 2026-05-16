# Edge AI Patterns - Reference Archive

## Purpose
Archive promising edge AI architectures and deployment patterns for future reference when Pnkln reaches scale justification.

## Decision Criteria for Edge AI Adoption

Evaluate edge AI models when:
1. **Cost Threshold**: Cloud inference costs >$50K/year
2. **Latency Requirements**: Real-time (<100ms) inference needed
3. **Privacy Requirements**: Data cannot leave device/premises
4. **Offline Requirements**: Functionality needed without network
5. **Regulatory Requirements**: Data sovereignty, compliance constraints

## Reference Architectures

### DeepSeek OCR (3B) - November 2025
- **Model Type**: Vision-Language Model (VLM) for OCR
- **Parameters**: 3B (edge-deployable)
- **Key Insights**:
  - Small models can achieve specialized task performance
  - Edge deployment viable for vision tasks
  - Chinese AI labs iterating rapidly on efficient models
- **Reference Notebook**: [DeepSeek OCR (3B) Colab](https://colab.research.google.com/...)
- **Decision**: Deferred - see [ADR 001](../../decisions/001-deepseek-ocr-evaluation.md)
- **Potential Use Cases**:
  - AiURCM: Legacy compliance document ingestion (non-regulated)
  - ShadowTag: Visible watermark/overlay text detection
  - Internal: Cost optimization for high-volume doc processing
- **Learned Patterns**:
  ```python
  # Model serving optimization
  - Quantization strategies (INT8, FP16)
  - Batch inference for throughput
  - GPU memory management
  - Request queuing and batching

  # Edge deployment
  - Model size vs. accuracy tradeoffs
  - Hardware acceleration (CUDA, TensorRT)
  - Fallback strategies (edge → cloud)
  ```

## Comparable Technologies

### Google Gemini Nano
- **Size**: 1.8B - 3.25B parameters
- **Deployment**: Android on-device, Chrome browser
- **Use Case**: Privacy-preserving inference, offline capability
- **Advantage**: First-party Google support, proven at scale

### PaliGemma (Google)
- **Type**: Vision-Language Model
- **Deployment**: Vertex AI, self-hosted
- **Use Case**: Image understanding, OCR, VQA
- **Advantage**: Fine-tuning support, GCP native

### Microsoft Phi-3 Vision
- **Size**: 4.2B parameters
- **Deployment**: ONNX Runtime, cloud/edge
- **Use Case**: Multimodal understanding at small scale
- **Advantage**: Microsoft ecosystem integration

## Evaluation Framework

When evaluating edge AI models:

```python
class EdgeAIEvaluation:
    def __init__(self, model_name, use_case):
        self.model = model_name
        self.use_case = use_case

    def evaluate(self):
        return {
            'accuracy': self._measure_accuracy(),
            'latency': self._measure_latency(),
            'cost_savings': self._calculate_savings(),
            'deployment_complexity': self._assess_complexity(),
            'compliance_fit': self._check_compliance(),
            'roi_timeline': self._project_roi()
        }

    def decision(self, evaluation):
        if evaluation['roi_timeline'] > '2 years':
            return 'DEFER'
        elif evaluation['compliance_fit'] == False:
            return 'REJECT'
        elif evaluation['cost_savings'] > 50000:  # $50K threshold
            return 'EVALUATE_POC'
        else:
            return 'DEFER'
```

## Learning Resources

### Model Optimization
- [TensorRT Optimization Guide](https://docs.nvidia.com/deeplearning/tensorrt/)
- [ONNX Runtime Performance Tuning](https://onnxruntime.ai/docs/performance/)
- [Vertex AI Model Deployment](https://cloud.google.com/vertex-ai/docs/predictions/deploy-model)

### Edge Deployment
- [Google Edge TPU](https://coral.ai/docs/)
- [NVIDIA Jetson](https://developer.nvidia.com/embedded/jetson)
- [AWS Panorama](https://aws.amazon.com/panorama/)

### Quantization & Compression
- [Post-Training Quantization](https://www.tensorflow.org/lite/performance/post_training_quantization)
- [Knowledge Distillation](https://arxiv.org/abs/1503.02531)
- [Pruning Techniques](https://pytorch.org/tutorials/intermediate/pruning_tutorial.html)

---

**Philosophy**: Archive promising patterns, defer implementation until scale justifies investment.

**Last Updated**: 2025-11-07
