# Source: https://cloud.google.com/blog/products/management-tools/datadog-integrates-agent-development-kit-or-adk

Datadog integrates Agent Development Kit, or ADK | Google Cloud Blog

Management Tools

# Monitoring Google ADK agentic applications with Datadog LLM Observability

January 23, 2026

##### Abhi Das

Senior Strategic Partnerships Manager, Google

##### Trammell Saltzgaber

Product Marketing Manager, Datadog

##### Try Nano Banana 2

State-of-the-art image generation and editing

[Try now](https://console.cloud.google.com/vertex-ai/studio/multimodal?model=gemini-3.1-flash-image-preview)

Google’s [Agent Development Kit (ADK)](https://google.github.io/adk-docs/) gives you the building blocks to create powerful agentic systems. These multi-step agents can plan, loop, collaborate, and call tools dynamically to solve problems on their own. However, this flexibility also makes them unpredictable, leading to potential issues like incomplete outputs, unexpected costs, and security risks. To help you manage this complexity, [Datadog LLM Observability](https://www.datadoghq.com/product/llm-observability/) now provides automatic instrumentation for systems built with ADK. This integration gives you the visibility to monitor agent behavior, track costs and errors, and optimize agents for response quality and safety through offline experimentation and online evaluation without extensive manual setup.

This is significant as agentic systems are complex, and interagent interactions and the non-deterministic nature of LLMs makes it difficult to predict responses. 

Common risks when running these agents include:

* **Pace of change:** New foundation models drop weekly and “best-practice” prompting patterns change just as fast. Teams must constantly evaluate new combinations.
* **Multi-agent handoffs:** If one agent produces low-quality output, it can cascade downstream and cause other agents to make poor decisions.
* **Loops and retries:** Planners can get stuck calling the same tool repeatedly, such as retrying a search query indefinitely, which causes latency spikes.
* **Hidden costs:** A single misrouted planner step can multiply token usage or API calls, pushing costs over budget.
* **Safety and accuracy:** LLM responses may contain hallucinations, sensitive data, or prompt injection attempts, risking security incidents and reduced customer trust.

Finally, ADK is just one of many agentic frameworks available on the market. Having to manually instrument it  only adds another learning curve to an already tedious and error-prone process.

### **Trace agent decisions and unexpected behaviors**

Datadog LLM Observability addresses these pains by automatically instrumenting and tracing your ADK agents, so you can start evaluating your agents offline and monitoring them in production in minutes — without code changes. This allows you to visualize every step and planner choice — from agent orchestration to tool calls — on a single trace timeline.

For example, if an agent selects an incorrect tool to respond to a user query, it can yield unexpected errors or inaccurate responses. You can use Datadog’s visualizations to pinpoint the exact step where the incorrect tool was selected, making troubleshooting easier and helping you reproduce the issue.

### **Monitor token usage and latency**

Sudden increases in latency or cost are often a sign of trouble in agentic applications. Datadog lets you view token usage and latency per tool, branch, and workflow to identify where errors happened and how they affected downstream steps.

For example, if a planner agent retries a summarization tool five times, it can significantly increase latency. Datadog highlights these loops, showing you exactly how long they took and the associated cost impact.

### **Evaluate agent response quality and security**

Operational performance metrics like latency are critical monitoring signals, but for a holistic view of how agentic applications are performing, teams also need to evaluate the semantic quality of the LLM and agentic responses. Datadog provides built-in evaluations to detect hallucinations, PII leaks, prompt injections, and unsafe responses.

You can also add custom evaluators, including [LLM-as-a-judge evaluators](https://docs.datadoghq.com/llm_observability/evaluations/custom_llm_as_a_judge_evaluations/?tab=boolean), for domain-specific checks. For instance, if a retrieval agent fetches irrelevant documents that lead to off-topic answers, a custom evaluator can flag that trace as having low retrieval relevance.

### **Iterate quickly and confidently with experiments**

When you roll out a new system prompt, you might notice spikes in latency or drifts in output consistency. Datadog allows you to replay production LLM calls in its Playground to test different models, prompts, or parameters to find the configurations that move you closer to your ideal behavior.

From there, you can run [structured experiments](https://www.datadoghq.com/blog/llm-experiments/) to compare versions side-by-side using datasets built from real traffic to optimize operational and functional performance. Because every agent step is logged through ADK instrumentation, you have the full context you need to reproduce regressions and validate fixes before you deploy.

### **Get started with Datadog LLM Observability**

Datadog LLM Observability simplifies monitoring and debugging for Google ADK systems, helping users debug agent operations, evaluate responses, iterate quickly, and validate changes before deploying them to production. 

You can get started today with the latest version of the LLM Observability SDK, or start a [free trial](https://console.cloud.google.com/marketplace/product/datadog-public/datadog) if you are new to Datadog.

For more information on how to debug agent operations and evaluate responses, view Datadog’s [LLM Observability documentation](https://docs.datadoghq.com/llm_observability/)**.**

Posted in

* [Management Tools](https://cloud.google.com/blog/products/management-tools)
* [AI & Machine Learning](https://cloud.google.com/blog/products/ai-machine-learning)
* [Application Development](https://cloud.google.com/blog/products/application-development)
* [Partners](https://cloud.google.com/blog/topics/partners)

##### Related articles

[![https://storage.googleapis.com/gweb-cloudblog-publish/images/21_-_Management_Tools_EI9iqlb.max-700x700.jpg](https://storage.googleapis.com/gweb-cloudblog-publish/images/21_-_Management_Tools_EI9iqlb.max-700x700.jpg)

Management Tools

### Unified Maintenance: A new, unified way to manage maintenance across Google Cloud

By Erol-Valeriu Chioasca • 2-minute read](https://cloud.google.com/blog/products/management-tools/unified-maintenance-centralizes-planned-maintenance)

[![https://storage.googleapis.com/gweb-cloudblog-publish/images/1_-_hero_image_-_png_uncompressed.max-700x700.png](https://storage.googleapis.com/gweb-cloudblog-publish/images/1_-_hero_image_-_png_uncompressed.max-700x700.png)

Management Tools

### OTLP everywhere: Cloud Monitoring now supports OpenTelemetry Protocol metrics

By Lee Yanco • 4-minute read](https://cloud.google.com/blog/products/management-tools/otlp-opentelemetry-protocol-for-google-cloud-monitoring-metrics)

[![https://storage.googleapis.com/gweb-cloudblog-publish/images/05_-_Compute.max-700x700.jpg](https://storage.googleapis.com/gweb-cloudblog-publish/images/05_-_Compute.max-700x700.jpg)

Compute

### Simplify VM OS agent management at scale: Introducing VM Extensions Manager

By Omkar Suram • 4-minute read](https://cloud.google.com/blog/products/compute/introducing-vm-extensions-manager)

[![https://storage.googleapis.com/gweb-cloudblog-publish/images/08_-__Cost_Management.max-700x700.jpg](https://storage.googleapis.com/gweb-cloudblog-publish/images/08_-__Cost_Management.max-700x700.jpg)

Cost Management

### Automating FinOps cost management policies using Workload Manager

By Pathik Sharma • 6-minute read](https://cloud.google.com/blog/topics/cost-management/automate-financial-governance-policies-using-workload-manager)
