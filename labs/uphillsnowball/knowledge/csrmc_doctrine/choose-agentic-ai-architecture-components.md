# Source: https://docs.cloud.google.com/architecture/choose-agentic-ai-architecture-components

Choose your agentic AI architecture components  |  Cloud Architecture Center  |  Google Cloud Documentation



[Skip to main content](#main-content)

[![Google Cloud Documentation](https://www.gstatic.com/devrel-devsite/prod/vd3309c0d80f416d7367081c5c5ffd3cd171f6ea37becda6136423538d770ce20/clouddocs/images/lockup.svg)](/)

`/`

[Console](//console.cloud.google.com/)


* English
* Deutsch
* Español
* Español – América Latina
* Français
* Indonesia
* Italiano
* Português
* Português – Brasil
* עברית
* 中文 – 简体
* 中文 – 繁體
* 日本語
* 한국어

Sign in

[![](https://docs.cloud.google.com/_static/clouddocs/images/icons/cloud.svg)](https://docs.cloud.google.com/architecture)

* [Documentation](https://docs.cloud.google.com/docs)
* [Cloud Architecture Center](https://docs.cloud.google.com/architecture)

[Start free](//console.cloud.google.com/freetrial)



* [Home](https://docs.cloud.google.com/)
* [Documentation](https://docs.cloud.google.com/docs)
* [Cloud Architecture Center](https://docs.cloud.google.com/architecture)

Send feedback

# Choose your agentic AI architecture components Stay organized with collections Save and categorize content based on your preferences.



Last reviewed 2025-11-24 UTC

This document provides guidance to help you choose architectural components for
your agentic AI applications in Google Cloud. It describes how to evaluate the
characteristics of your application and workload in order to choose an
appropriate product or service that best suits your needs. The process to design
an agentic AI architecture is iterative. You should periodically reassess your
architecture as your workload characteristics change, as your requirements
evolve, or as new Google Cloud products and features become available.

AI agents are effective for applications that solve open-ended problems, which
might require autonomous decision-making and complex multi-step workflow
management. Agents excel at solving problems in real-time by using external data
and they excel at automating knowledge-intensive tasks. These capabilities
enable agents to provide more business value than the assistive and generative
capabilities of an AI model.

You can use AI agents for deterministic problems with predefined steps.
However, other approaches can be more efficient and cost-effective. For example,
you don't need an agentic workflow for tasks like summarizing a document,
translating text, or classifying customer feedback.

For information about alternative non-agentic AI solutions, see the following
resources:

* [What is the difference between AI agents, AI assistants, and bots?](https://cloud.google.com/discover/what-are-ai-agents#what-is-the-difference-between-ai-agents-ai-assistants-and-bots)
* [Choose models and infrastructure for your generative AI application](/docs/generative-ai/choose-models-infra-for-ai)

## Agent architecture overview

An
[agent](/docs/generative-ai/glossary#ai-agents)
is an application that achieves a goal by processing input, performing reasoning
with available tools, and taking actions based on its decisions. An agent uses
an AI model as its core reasoning engine to automate complex tasks. The agent
uses a set of tools that let the AI model interact with external systems and
data sources. An agent can use a memory system to maintain context and learn
from interactions. The goal of an agentic architecture is to create an autonomous
system that can understand a user's intent, create a multi-step plan, and
execute that plan by using the available tools.

The following diagram shows a high-level overview of an agentic system's
architecture components:

![The architecture components of an agentic system.](/static/architecture/images/choose-agentic-ai-architecture-components.svg)

![](/static/architecture/images/choose-agentic-ai-architecture-components.svg)

The agentic system architecture includes the following components:

* **Frontend framework**: A collection of prebuilt components,
  libraries, and tools that you use to build the user interface (UI) for your
  application.
* **Agent development framework**: The frameworks and libraries that you
  use to build and structure your agent's logic.
* **Agent tools**: The collection of tools, such as APIs, services, and
  functions, that fetch data and perform actions or transactions.
* **Agent memory**: The system that your agent uses to store and recall
  information.
* **Agent design patterns**: Common architectural approaches for
  structuring your agentic application.
* **Agent runtime**: The compute environment where your agent's
  application logic runs.
* **AI models**: The core reasoning engine that powers your agent's
  decision-making capabilities.
* **Model runtime**: The infrastructure that hosts and serves your AI model.

The following sections provide a detailed analysis of the components to help
you make decisions about how to build your architecture. The components that you
choose will influence your agent's performance, scalability, cost, and security.
This document focuses on the essential architectural components that you use to
build and deploy an agent's core reasoning and execution logic. Topics such as
responsible AI safety frameworks and agent identity management are considered
out of scope for this document.

## Frontend framework

The *frontend framework* is a collection of prebuilt components, libraries,
and tools that you use to build the UI for your agentic application. The
frontend framework that you choose defines the requirements for your backend. A
simple interface for an internal demo might only require a synchronous HTTP API,
while a production-grade application requires a backend that supports streaming
protocols and robust state management.

Consider the following categories of frameworks:

* **Prototyping and internal tool frameworks**: For rapid development,
  internal demos, and proof-of-concept applications, choose frameworks that
  prioritize developer experience and velocity. These frameworks typically
  favor a simple and synchronous model that's called a *request-response
  model*. A request-response model lets you build a functional UI with
  minimal code and a simpler backend compared to a production framework. This
  approach is ideal for quickly testing agent logic and tool integrations,
  but it might not be suitable for highly scalable, public-facing
  applications that require real-time interactions. Common frameworks in this
  category include
  [Mesop](https://mesop-dev.github.io/mesop/)
  and
  [Gradio](https://www.gradio.app/).
* **Production frameworks**: For scalable, responsive, and feature-rich
  applications for external users, choose a framework that allows for custom
  components. These frameworks require a backend architecture that can
  support a modern user experience. A production framework should include
  support for streaming protocols, a stateless API design, and a robust,
  externalized memory system to manage conversation state across multiple
  user sessions. Common frameworks for production applications include
  [Streamlit](https://streamlit.io/),
  [React](https://react.dev/),
  and the
  [Flutter AI Toolkit](https://pub.dev/packages/flutter_ai_toolkit).

To manage the communication between these frameworks and your AI agent, you can
use
[Agent–User Interaction (AG-UI) protocol](https://docs.ag-ui.com/introduction).
AG-UI is an open protocol that enables backend AI agents to interact with your
frontend framework. AG-UI tells the frontend framework when to render the
agent's response, update application state, or trigger a client-side action. To
build interactive AI applications, combine
[AG-UI with Agent Development Kit (ADK)](https://developers.googleblog.com/en/delight-users-by-combining-adk-agents-with-fancy-frontends-using-ag-ui/). For information about ADK, continue to the next section "Agent development frameworks."

## Agent development frameworks

*Agent development frameworks* are libraries that simplify the process of
building, testing, and deploying agentic AI applications. These development
tools provide prebuilt components and abstractions for core agent capabilities,
including reasoning loops, memory, and tool integration.

To accelerate agent development in Google Cloud, we recommend that you
use
[ADK](https://google.github.io/adk-docs/).
ADK is an open-source, opinionated, and modular framework that provides a
high-level of abstraction for building and orchestrating workflows from simple
tasks to complex, multi-agent systems.

ADK is optimized for Gemini models and Google Cloud, but it's
built for compatibility with other frameworks. ADK supports other AI models and
runtimes, so you can use it with any model or deployment method. For multi-agent
systems, ADK supports interaction through shared session states, model-driven
delegation to route tasks between agents, and explicit invocation that lets one
agent call another agent as a function or tool.

To help you get started quickly, ADK provides
[code samples](https://github.com/google/adk-samples)
in Python, Java, and Go that demonstrate a variety of use cases across multiple
industries. Although many of these samples highlight conversational flows, ADK
is also well-suited for building autonomous agents that perform backend tasks.
For these non-interactive use cases, choose an
[agent design pattern](#agent-design-patterns)
that excels in processing a single, self-contained request and that implements
robust error handling.

To build a custom agent architecture, you can also use a general-purpose AI
framework like
[Genkit](https://genkit.dev/).
Genkit provides primitives that let you have fine-grain control over your
[agent logic](https://genkit.dev/docs/agentic-patterns/)
without the high-level abstraction that ADK offers. However, a dedicated agent
framework like ADK provides specialized tools for developing agentic
applications.

## Agent tools

An agent's ability to interact with external systems through tools defines its
effectiveness. *Agent tools* are functions or APIs that are available to the AI
model and that the agent uses to enhance output and allow for task automation.
When you connect an AI agent to external systems, tools transform the agent from
a simple text generator into a system that can automate complex, multi-step
tasks.

To enable tool interactions, choose from the following tool use patterns:

| Use case | Tool use pattern |
| --- | --- |
| You need to perform a common task like completing a web search, running a calculation, or executing code, and you want to accelerate initial development. | Built-in tools |
| You want to build a modular or multi-agent system that requires interoperable and reusable tools. | Model Context Protocol (MCP) |
| You need to manage, secure, and monitor a large number of API-based tools at an enterprise scale. | API management platform |
| You need to integrate with a specific internal or third-party API that doesn't have an MCP server. | Custom function tools |

When you select tools for your agent, evaluate them on their functional
capabilities and their operational reliability. Prioritize tools that are
observable, easy to debug, and that include robust error handling. These
capabilities help to ensure that you can trace actions and resolve failures
quickly. In addition, evaluate the agent's ability to select the right tool to
successfully complete its assigned tasks.

### Built-in tools

ADK provides several
[built-in tools](https://google.github.io/adk-docs/tools/built-in-tools/) that are integrated directly into the agent's runtime. You can call these tools
as [functions](https://google.github.io/adk-docs/tools/function-tools/)
without configuring external communication protocols. These tools provide common
functionalities, including accessing real-time information from the web,
executing code programmatically in a secure environment, retrieving information
from private enterprise data to implement RAG, and interacting with structured
data in cloud databases. The built-in tools work alongside any custom tools that
you create.

### MCP

To enable the components of your agentic system to interact, you need to
establish clear communication protocols. [MCP](https://modelcontextprotocol.io/overview)
is an open protocol that provides a standardized interface for agents to access
and use the necessary tools, data, and other services.

MCP decouples the agent's
core reasoning logic from the specific implementation of its tools, similar to
how a standard hardware port allows different peripherals to connect to a
device. MCP simplifies tool integration because it provides a growing list of
prebuilt connectors and a consistent way to build custom integrations. The
flexibility to integrate tools promotes interoperability across different models
and tools.

You can connect to a remote MCP server if one is available, or you can host
your own MCP server. When you host your own MCP server, you have full control
over how you expose proprietary or third-party API to your agents. To host your
own custom MCP server, deploy it as a containerized application on
Cloud Run or GKE.

### API management platform

An *API management platform* is a centralized system that lets you secure,
monitor, and control internal or external services through APIs. An API
management platform provides a centralized location to catalog all of your
organization's APIs, simplifies how you expose data, and provides observability
through usage monitoring.

To manage your agent's API-based tools at an enterprise scale on
Google Cloud, we recommend that you use
[Apigee API hub](/apigee/docs/apihub/what-is-api-hub).
API hub lets agents connect to data instantly through direct
HTTP calls, prebuilt connectors, custom APIs registered in the hub, or direct
access to Google Cloud data sources. This approach gives your agents
immediate access to the information that they need without the complexity of
building custom data loading and integration pipelines.

An API management platform and a communication protocol like MCP solve
different architectural problems. A communication protocol standardizes the
interaction format between the agent and the tool, which ensures that components
are reusable and can be swapped. By contrast, an API management platform
governs the lifecycle and security of the API endpoint, handling tasks like
authentication, rate limiting, and monitoring. These patterns are
complementary. For example, an agent can use MCP to communicate with a tool, and
that tool can in turn be a secure API endpoint that API hub
manages and protects.

### Custom function tool

A [function tool](https://google.github.io/adk-docs/tools/function-tools/#function-tool)
gives an agent new capabilities. You can write a custom function tool to give
your agent specialized capabilities, such as to integrate with an external API
or a proprietary business system. Writing a custom function tool is the most
common pattern for extending an agent's abilities beyond what built-in tools can
offer.

To create a custom function tool, you write a function in your preferred
programming language and then provide a clear, natural-language description of
its purpose, parameters, and return values. The agent's model uses this
description to reason about when the tool is needed, what inputs to provide, and
how to interpret the output to complete a user's request.

You can also create a custom function tool that implements an
[agent-as-a-tool function](https://google.github.io/adk-docs/tools/function-tools/#agent-tool).
An agent-as-a-tool function exposes one agent as a callable function that
another agent can invoke. This technique lets you build complex, multi-agent
systems where an agent can coordinate and delegate specialized tasks to other,
specialized agents. For more information about agent design patterns and coordinating
multi-agent orchestration, see the section on
[agent design patterns](#agent-design-patterns)
later in this document.

## Agent memory

An agent's ability to remember past interactions is fundamental to provide a
coherent and useful conversational experience. To create stateful, context-aware
agents, you must implement mechanisms for short-term memory and long-term
memory. The following sections explore the design choices and Google Cloud
services that you can use to implement both short-term and long-term memory for
your agent.

### Short-term memory

Short-term memory enables an agent to maintain context within a single, ongoing
conversation. To implement short-term memory, you must manage both the session
and its associated state.

* [**Session**](https://google.github.io/adk-docs/sessions/session/):
  A session is the conversational thread between a user and the agent, from
  the initial interaction to the end of the dialogue.
* [**State**](https://google.github.io/adk-docs/sessions/state/):
  State is the data that the agent uses and collects within a specific
  session. The state data that's collected includes the history of messages
  that the user and agent exchanged, the results of any tool calls, and other
  variables that the agent needs in order to understand the context of the
  conversation.

The following are options for
[implementing short-term memory with ADK](https://google.github.io/adk-docs/sessions/session/#sessionservice-implementations):

* **In-memory storage**: For development, testing, or simple applications
  that run on a single instance, you can store the session state directly in
  your application's memory. The agent uses a data structure, such as a
  dictionary or an object, to store a
  [list of key-value pairs](https://google.github.io/adk-docs/sessions/state/#key-characteristics-of-state)
  and it updates these values throughout the session. However, when you use
  in-memory storage, session state isn't persistent. If the application
  restarts, it loses all conversation history.
* **External state management**: For production applications that require
  scalability and reliability, we recommend that you build a stateless agent
  application and manage the session state in an external storage service. In
  this architecture, each time the agent application receives a request, it
  retrieves the current conversation state from the external store, processes
  the new turn, and then saves the updated state back to the store. This
  design lets you scale your application horizontally because any instance
  can serve any user's request. Common choices for external state management
  include
  [Memorystore for Redis](/memorystore/docs/redis/memorystore-for-redis-overview),
  [Firestore](https://cloud.google.com/products/firestore/),
  or
  [Vertex AI Agent Engine sessions](/vertex-ai/generative-ai/docs/agent-engine/sessions/overview).

  If you use ADK, the
  [`DatabaseSessionService`](https://google.github.io/adk-docs/sessions/session/#sessionservice-implementations) requires a
  relational database, such as
  [Cloud SQL](https://cloud.google.com/sql).

### Long-term memory

[Long-term memory](https://google.github.io/adk-docs/sessions/memory/)
provides the agent with a persistent knowledge base that exists across all
conversations for individual users. Long-term memory lets the agent retrieve and use external
information, learn from past interactions, and provide more accurate and
relevant responses.

The following are options for implementing long-term memory with ADK:

* **In-memory storage**: For development and testing, you can store the
  session state directly in your application's memory. This approach is
  simple to implement, but it isn't persistent. If the application restarts,
  it loses the conversation history. You typically implement this pattern by
  using an in-memory provider within a development framework, such as the
  [`InMemoryMemoryService`](https://google.github.io/adk-docs/sessions/memory/#in-memory-memory)
  that's included in ADK for testing.
* **External storage**: For production applications, manage your agent's
  knowledge base in an external, persistent storage service. An external
  storage service ensures that your agent's knowledge is durable, scalable,
  and accessible across multiple application instances. Use
  [Memory Bank](/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview)
  for long-term storage with any agent runtime on Google Cloud.

## Agent design patterns

Agent design patterns are common architectural approaches to build agentic
applications. These patterns offer a distinct framework for organizing a
system's components, integrating the AI model, and orchestrating a single agent
or multiple agents to accomplish a workflow. To determine which approach is best
for your workflow, you must consider the complexity and workflow of your tasks,
latency, performance, and cost requirements.

A
[single-agent system](/architecture/choose-design-pattern-agentic-ai-system#single-agent-system)
relies on one model's reasoning capabilities to interpret a user's request, plan
a sequence of steps, and decide which tools to use. This approach is an
effective starting point that lets you focus on refining the core logic,
prompts, and tool definitions before you add architectural complexity. However,
a single agent's performance can degrade as tasks and the number of tools grow
in complexity.

For complex problems, a
[multi-agent system](/architecture/choose-design-pattern-agentic-ai-system#multi-agent-systems)
orchestrates multiple specialized agents to achieve a goal that a single agent
can't easily manage. This modular design can improve the scalability,
reliability, and maintainability of the system. However, it also introduces
additional evaluation, security, and cost considerations compared to a
single-agent system.

When you develop a multi-agent system, you must implement precise access
controls for each specialized agent, design a robust orchestration system to
ensure reliable inter-agent communication, and manage the increased operational
costs from the computational overhead of running multiple agents. To facilitate
communication between agents, use
[Agent2Agent (A2A) protocol with ADK](https://google.github.io/adk-docs/a2a/).
A2A is an open standard protocol that enables AI agents to communicate and
collaborate across different platforms and frameworks, regardless of their
underlying technologies.

For more information about common agent design patterns and how to select a
pattern based on your workload requirements, see
[Choose a design pattern for your agentic AI system](/architecture/choose-design-pattern-agentic-ai-system).

## AI models

Agentic applications depend on the reasoning and understanding capabilities of
a model to act as the primary task orchestrator. For this core agent role, we
recommend that you use
[Gemini Pro](https://deepmind.google/models/gemini/pro/).

Google models, like Gemini, provide access to the latest and
most capable proprietary models through a managed API. This approach is ideal
for minimizing operational overhead. In contrast, an open, self-hosted model
provides the deep control that's required when you fine-tune on proprietary
data. Workloads with strict security and data residency requirements also
require a self-hosted model, because it lets you run the model within your own
network.

To improve agent performance, you can adjust the model's reasoning
capabilities. Models such as the latest
[Gemini Pro and Flash models](https://deepmind.google/models/gemini/)
feature a built-in thinking process that improves reasoning and multi-step
planning. For debugging and refinement, you can review the model's
[thought summaries](https://ai.google.dev/gemini-api/docs/thinking#summaries),
or synthesized versions of its internal thoughts, to understand its reasoning
path. You can control the model's reasoning capabilities by adjusting the
[thinking budget](https://ai.google.dev/gemini-api/docs/thinking#set-budget),
or the number of thinking tokens, based on task complexity. A higher thinking
budget lets the model perform more detailed reasoning and planning before it
provides an answer. A higher thinking budget can improve response quality, but
it might also increase latency and cost.

To optimize for performance and cost, implement
[model routing](https://medium.com/google-cloud/a-developers-guide-to-model-routing-1f21ecc34d60)
to dynamically select the most appropriate model for each task based on the
task's complexity, cost, or latency requirements. For example, you can route
simple requests to a small language model (SLM) for structured tasks like code
generation or text classification, and reserve a more powerful and expensive
model for complex reasoning. If you implement model routing in your agentic
application, you can create a cost-effective system that maintains high
performance.

Google Cloud provides access to a wide selection of Google models,
partner models, and open models that you can use in your agentic architecture.
For more information on the models that are available and how to choose a model
to fit your needs, see
[Model Garden on Vertex AI](https://cloud.google.com/model-garden#choose-a-model-that-fits-your-needs).

## Model runtime

A model runtime is the environment that hosts and serves your AI model and that
makes its reasoning capabilities available to your agent.

### Choose a model runtime

To select the best runtime when you host your AI
models, use the following guidance:

| Use case | Model runtime |
| --- | --- |
| You need a fully managed API to serve Gemini models, partner models, open models, or custom models with enterprise-grade security, scaling, and generative AI tools. | Vertex AI |
| You need to deploy an open or custom containerized model and prioritize serverless simplicity and cost-efficiency for variable traffic. | Cloud Run |
| You need maximum control over the infrastructure to run an open or custom containerized model on specialized hardware or to meet complex security and networking requirements. | GKE |

The following sections provide an overview of the preceding model runtimes,
including key features and design considerations. This document focuses on
Vertex AI, Cloud Run, and
GKE. However, Google Cloud offers other services that
you might consider for a model runtime:

* [Gemini API](https://ai.google.dev/gemini-api/docs):
  The Gemini API is designed for developers who need quick,
  direct access to Gemini models without the enterprise
  governance features that complex agentic systems often require.
* [Compute Engine](/compute/docs/gpus/about-gpus):
  Compute Engine is an infrastructure as a service (IaaS) product that is
  suitable for legacy applications. It introduces significant operational
  overhead compared to modern, container-based runtimes.

For more information about the features that distinguish all of the service options for model runtimes, see
[Model hosting infrastructure](/docs/generative-ai/choose-models-infra-for-ai#model-hosting-infrastructure).

#### Vertex AI

[Vertex AI](/vertex-ai/generative-ai/docs)
provides a fully managed, serverless environment that hosts your AI models. You
can serve and fine-tune Google models, partner models, and open models through
a secure and scalable API. This approach abstracts away all infrastructure
management, and it lets you focus on integrating model intelligence into your
applications.

When you use Vertex AI
as a model runtime, the key features and considerations include the following:

* **Infrastructure control**: A fully managed API for your
  models. Google manages the underlying infrastructure.
* **Security**: Managed security defaults and standard compliance
  certifications are sufficient for your needs. To provide prompt and response protection and to
  ensure responsible AI practices, you can integrate [Model Armor](/security-command-center/docs/model-armor-vertex-integration)
  into Vertex AI.
* **Model availability**: Access to a wide selection of models,
  including the latest Gemini models, through a managed API.
* **Cost**: Pay-per-use pricing model that scales with your
  application's traffic. For more information, see [Cost of building
  and deploying AI models in Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/pricing).

#### Cloud Run

Cloud Run provides a serverless runtime that hosts your
models inside custom containers. Cloud Run offers a balance
between the fully managed simplicity of Vertex AI and the deep
infrastructure control of GKE. This approach is ideal when
you need the flexibility to run your model in a containerized environment
without managing servers or clusters.

When you use Cloud Run
as a model runtime, the key features and considerations include the following:

* **Infrastructure control**: Run any model in a custom
  container, which provides full control over the software environment, while the
  platform manages the underlying serverless infrastructure.
* **Security**: Provides security through ephemeral, isolated
  compute instances and allows for secure connections to private resources by using
  [Direct
  VPC egress](/run/docs/configuring/vpc-direct-vpc) or a [Serverless VPC Access
  connector](/run/docs/configuring/vpc-connectors). For more information, see [Private
  networking and Cloud Run](/run/docs/securing/private-networking#from-vpc).
* **Model availability**: Serve open models such as
  Gemma or serve your own custom models. You can't host or serve
  Gemini models on Cloud Run.
* **Cost**: Features a pay-per-use, request-based pricing model
  that scales to zero, which makes it highly cost-effective for models with
  sporadic or variable traffic. For more information, see [Cloud Run
  pricing](https://cloud.google.com/run/pricing).

#### GKE

GKE provides the most control and flexibility for
hosting your AI models. To use this approach, you run your models in containers
on a GKE cluster that you configure and manage. GKE is
the ideal choice when you need to run models on specialized hardware, colocate
them with your applications for minimal latency, or require granular control
over every aspect of the serving environment.

When you use GKE as a model runtime, the key features and considerations include the following:

* **Infrastructure control**: Provides maximum, granular
  control over the entire serving environment, including node configurations,
  specialized machine accelerators, and the specific model serving software.
* **Security**: Enables the highest level of security and data
  isolation because it lets you run models entirely within your network and apply
  fine-grained Kubernetes security policies. To screen traffic to and from a GKE cluster
  and to protect all interactions with the AI models, you can integrate [Model Armor](/security-command-center/docs/model-armor-gke-integration)
  with GKE .
* **Model availability**: Serve open models such as
  Gemma, or serve your own custom models. You can't host or serve
  Gemini models on GKE.
* **Cost**: Features a cost model that's based on the underlying compute
  and cluster resources that you consume, which makes it highly optimized for
  predictable, high-volume workloads when you use [committed use
  discounts (CUDs)](https://cloud.google.com/kubernetes-engine/cud). For more information, see [Google Kubernetes Engine
  pricing](https://cloud.google.com/kubernetes-engine/pricing).

## Agent runtime

To host and deploy your agentic application, you must choose an agent runtime.
This service runs your application code—the business logic and orchestration
that you write when you use an
[agent development framework](#agent-development-frameworks).
From this runtime, your application makes API calls to the models that your
chosen
[model runtime](#model-runtime) hosts and manages.

### Choose an agent runtime

To select the runtime when you host your AI agents, use the following guidance:

| Use case | Agent runtime |
| --- | --- |
| Your application is a Python agent and it requires a fully managed experience with minimal operational overhead. | Vertex AI Agent Engine |
| Your application is containerized and it requires serverless, event-driven scaling with language flexibility. | Cloud Run |
| Your application is containerized, has complex stateful requirements, and it needs fine-grained infrastructure configuration. | GKE |

If you already manage applications on Cloud Run or on
GKE, you can accelerate development and simplify long-term operations
by using the same platform for your agentic workload.

The following sections provide an overview of each agent runtime, including key
features and design considerations.

### Vertex AI Agent Engine

[Vertex AI Agent Engine](/vertex-ai/generative-ai/docs/agent-engine/overview) is a fully-managed, opinionated runtime that you can use to deploy,
operate, and scale agentic applications. Vertex AI Agent Engine abstracts away the
underlying infrastructure, which lets you focus on agent logic instead of
operations.

The following are features and considerations for Vertex AI Agent Engine:

* **Programming language and framework
  flexibility**:Develop agents in Python with any [supported
  frameworks](/vertex-ai/generative-ai/docs/agent-engine/overview#supported-frameworks).
* **Communication protocols**: Orchestrate agents and tools that
  use MCP and A2A. Vertex AI Agent Engine efficiently manages the runtime for these
  components, but it doesn't support the hosting of custom MCP servers.
* **Memory**: Provides built-in, managed memory capabilities,
  which removes the need to configure external databases for core agent memory.

  | Requirement | Available options |
  | --- | --- |
  | Short-term memory | [Vertex AI Agent Engine sessions](/vertex-ai/generative-ai/docs/agent-engine/sessions/overview) |
  | Long-term memory | [Memory Bank](/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview) |
  | Database search and retrieval | + [Cloud SQL](/sql/docs/postgres/introduction) + [AlloyDB for PostgreSQL](/alloydb/docs/overview) |
* **Scalability**: Automatically scales to meet the demands
  of your agentic workload, which removes the need for manual configuration.
* **Observability**: Provides integrated logging, monitoring, and
  tracing through [Google Cloud Observability](/stackdriver/docs)
  services.
* **Security**: Provides the following
  enterprise-level reliability, scalability, and compliance:
  + Built-in
    service identity for secure, authenticated calls to Google
    Cloud APIs.
  + Run code in a secure, isolated, and managed sandbox with [Vertex AI Agent Engine Code
    Execution](/vertex-ai/generative-ai/docs/agent-engine/code-execution/overview).
  + Protect your data with your own [customer-managed
    encryption key (CMEK)](/agent-builder/agent-engine/manage/access#cmek) in [Secret Manager](/secret-manager/docs).
  + Restrict [IAM
    permissions](/run/docs/securing/managing-access) and [use VPC firewall rules](/firewall/docs/using-firewalls) to prevent unwanted
    network calls.

  For information about
  Vertex AI Agent Engine security features, see [Enterprise security](/vertex-ai/generative-ai/docs/agent-engine/overview#enterprise_security).

Vertex AI Agent Engine accelerates the path to production
because it provides a purpose-built, managed environment that handles many
complex aspects when you operate agents, such as lifecycle and context
management. Vertex AI Agent Engine is less suitable for use cases
that require extensive customization of the compute environment or that require
programming languages other than Python. For workloads that have strict security
requirements for private dependency management, Cloud Run and
GKE offer a more direct, IAM-based
configuration path.

### Cloud Run

[Cloud Run](https://cloud.google.com/run) is a fully managed,
serverless platform that lets you run your agent application code in a stateless
container. Cloud Run is ideal when you want to deploy the entire
agent application, individual components, or custom tools as scalable HTTP
endpoints without needing to manage the underlying infrastructure.

The
following are features and considerations for
Cloud Run:

* **Programming language and framework flexibility**: When
  you package your application in a container, you can develop agents in any
  programming language and with any framework.
* **Communication
  protocols**: Orchestrate agents and tools that use MCP and A2A. [Host MCP clients and
  servers](/run/docs/host-mcp-servers) with streamable HTTP transport on Cloud Run.
* **Memory**: Cloud Run instances are stateless,
  which means that an instance loses any in-memory data after it terminates. To
  implement persistent memory, connect your service to a managed
  Google Cloud storage service:

  | Requirement | Available options |
  | --- | --- |
  | Short-term memory | + [Memorystore for Redis](/memorystore/docs/redis/connect-redis-instance-cloud-run) + [Vertex AI Agent Engine   sessions with Cloud Run](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/agents/cloud_run/agents_with_memory/get_started_with_memory_for_adk_in_cloud_run.ipynb) + [Firestore](/firestore/docs) + [ADK's   `DatabaseSessionService`](https://google.github.io/adk-docs/sessions/session/#sessionservice-implementations) with [Cloud SQL](/sql/docs/postgres/introduction) |
  | Long-term memory | + Firestore + [Memory Bank with   Cloud Run](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/agents/cloud_run/agents_with_memory/get_started_with_memory_for_adk_in_cloud_run.ipynb) |
  | Database search and retrieval | + Cloud SQL + [AlloyDB for PostgreSQL](/alloydb/docs/overview) |
* **Scalability**: [Automatically scales the number of instances](/run/docs/about-instance-autoscaling)
  based on incoming traffic, and also scales instances down to zero. This feature
  helps make Cloud Run cost-effective for applications that have
  variable workloads.
* **Observability**: Provides integrated
  logging, monitoring, and tracing through [Google Cloud Observability](/stackdriver/docs) services. For more
  information, see [Monitoring and logging
  overview](/run/docs/monitoring-overview).
* **Security**: Provides the following
  security controls for your agents:
  + Built-in identity service for secure,
    authenticated calls to Google
    Cloud APIs.
  + Run untested code in a secure environment with the [Cloud Run sandbox environment](/run/docs/code-execution)
    or with [Vertex AI Agent Engine code
    execution](/vertex-ai/generative-ai/docs/agent-engine/code-execution/overview).
  + Store sensitive data that Cloud Run uses
    by [configuring secrets](/run/docs/configuring/services/secrets)
    in [Secret Manager](/secret-manager/docs).
  + Prevent unwanted network calls by restricting [IAM
    permissions](/run/docs/securing/managing-access) and using [VPC firewall rules](/firewall/docs/using-firewalls).

Cloud Run offers significant operational simplicity and
cost-effectiveness because it eliminates infrastructure management. However, the
stateless nature of Cloud Run requires you to use a storage
service in order to manage context across a multi-step workflow. Additionally,
the maximum request timeout for Cloud Run services is up to one
hour, which might constrain long-running agentic tasks.

### GKE

[Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine) is a managed
container orchestration service that provides granular control over your agentic
application's architecture and infrastructure.
GKE is suitable for complex agentic systems that require
robust, production-grade capabilities or if you are already a
GKE customer and you want to implement an agentic workflow
on top of your existing application.

The following are features and considerations that are available on
GKE:

* **Programming language and framework flexibility**: When
  you package your application in a container, you can develop agents in any
  programming language and with any framework.
* **Communication protocols**: Orchestrate agents and tools that
  use MCP and A2A. Host MCP clients and servers on GKE when
  you package them as containers.
* **Memory**: GKE pods are ephemeral.
  However, you can build stateful agents with persistent memory by using
  in-cluster resources or by connecting to external services:

  | Requirement | Available options |
  | --- | --- |
  | Short-term memory | + [Memorystore for Redis](/memorystore/docs/redis/connect-redis-instance-cloud-run) + [Vertex AI Agent Engine   sessions with GKE](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/agents/gke/agents_with_memory/get_started_with_memory_for_adk_in_gke.ipynb) + [Firestore](https://cloud.google.com/products/firestore/) + [ADK's   `DatabaseSessionService`](https://google.github.io/adk-docs/sessions/session/#sessionservice-implementations) with [Cloud SQL](/sql/docs/postgres/introduction) |
  | Long-term memory | + Firestore + [Memory Bank with   GKE](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/agents/gke/agents_with_memory/get_started_with_memory_for_adk_in_gke.ipynb) |
  | Database search and retrieval | + [StatefulSets](/kubernetes-engine/docs/concepts/statefulset) and [Persistent Volumes](/kubernetes-engine/docs/concepts/persistent-volumes) for durable   storage within your cluster. + Cloud SQL + [AlloyDB for PostgreSQL](/alloydb/docs/overview) |
* **Scalability**: GKE clusters [automatically provision](/kubernetes-engine/docs/how-to/node-auto-provisioning) and [scale](/kubernetes-engine/docs/concepts/cluster-autoscaler) your node
  pools to meet the requirements of your workload.
* **Observability**: Provides integrated logging, monitoring, and
  tracing at the cluster, node, and pod levels with Google Cloud Observability. To collect
  configured third-party and user-defined metrics and then send them to
  Cloud Monitoring, you can also use [Google Cloud Managed Service for Prometheus](/stackdriver/docs/managed-prometheus). For more
  information, see [Overview of
  GKE observability](/stackdriver/docs/solutions/gke).
* **Security**: Provides fine-grained security controls for your
  agents.
  + Use [Workload Identity Federation for GKE](/kubernetes-engine/docs/concepts/workload-identity) for
    secure authentication to Google Cloud APIs.
  + Isolate
    untrusted code with [GKE Sandbox](/kubernetes-engine/docs/concepts/sandbox-pods).
  + [Store sensitive data that your
    GKE clusters use](/secret-manager/docs/secret-manager-managed-csi-component) in
    Secret Manager.
  + Restrict [IAM permissions](/run/docs/securing/managing-access) and use [VPC firewall
    rules](/firewall/docs/firewalls) and [Network Policies](/kubernetes-engine/docs/how-to/network-policy) to prevent unwanted
    network calls.

GKE provides maximum control and flexibility, which lets
you run complex, stateful agents. However, this control introduces significant
operational overhead and complexity. You must configure and manage the
Kubernetes cluster, including node pools, networking, and scaling policies,
which requires more expertise and development effort than a serverless platform
requires.

## What's next

* Agent tools:
  + [Building custom tools for agents](https://www.youtube.com/embed/NiLb5DK4_rU).
  + [Tools Make an Agent: From Zero to Assistant with ADK](https://cloud.google.com/blog/topics/developers-practitioners/tools-make-an-agent-from-zero-to-assistant-with-adk).
  + [Agent Factory Recap: A Deep Dive into Agent Evaluation, Practical Tooling, and Multi-Agent Systems](https://cloud.google.com/blog/topics/developers-practitioners/agent-factory-recap-a-deep-dive-into-agent-evaluation-practical-tooling-and-multi-agent-systems).
  + [How to deploy a secure MCP server on Cloud Run](https://codelabs.developers.google.com/codelabs/cloud-run/how-to-deploy-a-secure-mcp-server-on-cloud-run).
* Agent memory:
  + [Remember me, memory in agents](https://www.youtube.com/embed/2yW7aTfjo88).
  + [Remember this: Agent state and memory with ADK](https://cloud.google.com/blog/topics/developers-practitioners/remember-this-agent-state-and-memory-with-adk).
* Agent design patterns:
  + [Choose a design pattern for your agentic AI system](/architecture/choose-design-pattern-agentic-ai-system).
  + [Multi-agent systems, concepts & patterns](https://www.youtube.com/embed/TGNScswE0kU).
  + [Multi-Agent Systems in ADK](https://google.github.io/adk-docs/agents/multi-agents/).
  + [Agent Patterns with ADK](https://medium.com/google-cloud/agent-patterns-with-adk-1-agent-5-ways-58bff801c2d6).
* Agent runtime:
  + [Develop and deploy agents on Vertex AI Agent Engine](/vertex-ai/generative-ai/docs/agent-engine/quickstart).
  + [Host AI apps and agents on Cloud Run](/run/docs/ai-agents).
  + [Deploy an agentic AI application on GKE with ADK and Vertex AI](/kubernetes-engine/docs/tutorials/agentic-adk-vertex).
* Other agentic AI resources on Google Cloud:
  + [Google's Approach for Secure AI Agents](https://research.google/pubs/an-introduction-to-googles-approach-for-secure-ai-agents/).
  + [Agent Factory Recap: Securing AI Agents in Production](https://cloud.google.com/blog/topics/developers-practitioners/agent-factory-recap-securing-ai-agents-in-production).
  + [Responsible Agents: A Phased Approach on Google Cloud](https://medium.com/google-cloud/responsible-agents-a-phased-approach-on-google-cloud-bef6badf2e7a).
  + [The Agent Factory playlist](https://www.youtube.com/embed/playlist?list=PLIivdWyY5sqLXR1eSkiM5bE6pFlXC-OSs).
* For more reference architectures, diagrams, and best practices, explore the
  [Cloud Architecture Center](/architecture).

## Contributors

Author: [Samantha He](https://www.linkedin.com/in/samantha-he-05a98173) | Technical Writer

Other contributors:

* [Amina Mansour](https://www.linkedin.com/in/aminamansour/) | Head of Cloud Platform Evaluations Team
* [Amit Maraj](https://www.linkedin.com/in/amit-maraj) | Developer Relations Engineer
* [Casey West](https://www.linkedin.com/in/caseywest) | Architecture Advocate, Google Cloud
* [Jack Wotherspoon](https://www.linkedin.com/in/jack-wotherspoon) | Developer Advocate
* [Joe Fernandez](https://www.linkedin.com/in/joefernandez007/) | Staff Technical Writer
* [Joe Shirey](https://www.linkedin.com/in/jshirey) | Cloud Developer Relations Manager
* [Karl Weinmeister](https://www.linkedin.com/in/karlweinmeister/) | Director of Cloud Product Developer Relations
* [Kumar Dhanagopal](https://www.linkedin.com/in/kumardhanagopal) | Cross-Product Solution Developer
* [Lisa Shen](https://www.linkedin.com/in/lisa-shen-6167241/) | Senior Outbound Product Manager, Google Cloud
* [Mandy Grover](https://www.linkedin.com/in/mandygrovermatc/) | Head of Architecture Center
* [Megan O'Keefe](https://www.linkedin.com/in/askmeegs) | Developer Advocate
* [Olivier Bourgeois](https://www.linkedin.com/in/olivi-eh/) | Developer Relations Engineer
* [Polong Lin](https://www.linkedin.com/in/polonglin) | Developer Relations Engineering Manager
* [Ryan Pei](https://www.linkedin.com/in/ryanpei/) | Product Manager, Google Cloud
* [Shir Meir Lador](https://www.linkedin.com/in/shirmeirlador) | Developer Relations Engineering Manager
* [Vlad Kolesnikov](https://www.linkedin.com/in/vkolesnikov) | Developer Relations Engineer




Send feedback

Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-11-24 UTC.




Need to tell us more?

[[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Hard to understand","hardToUnderstand","thumb-down"],["Incorrect information or sample code","incorrectInformationOrSampleCode","thumb-down"],["Missing the information/samples I need","missingTheInformationSamplesINeed","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2025-11-24 UTC."],[],[]]
