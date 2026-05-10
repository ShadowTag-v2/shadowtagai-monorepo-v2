# Source: https://www.copilotkit.ai/blog/master-the-17-ag-ui-event-types-for-building-agents-the-right-way

Master the 17 AG-UI Event Types for Building Agents the Right Way | Blog | CopilotKit

![Eyebrow Background Glow](/images/home/eyebrow-background-glow.svg)

MCP Apps: Bring MCP Apps interaction to your users with CopilotKit!Bring MCP Apps to your users!

[Learn More](/mcp-apps)

[Back](/blog)

# Master the 17 AG-UI Event Types for Building Agents the Right Way

By Anmol Baranwal and Nathan TarbertNovember 3, 2025

![Master the 17 AG-UI Event Types for Building Agents the Right Way](/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2Fy3fjfzcd%2Fproduction%2F7916d594a7afafc5ca429e3f33b2fe59ea69e9cb-3200x1800.png&w=1920&q=75)

Agent-User Interaction Protocol (AG-UI) is quickly becoming the standard for connecting agents with user interfaces.

It gives you a clean event stream to keep the UI in sync with what the agent is doing. All the communication is broken into typed events.

I have been digging into the Protocol, especially around those core event types, to understand how everything fits together. Here’s what I picked up and why it matters.

## 1. The Agentic Protocol (AG-UI)

[AG-UI (Agent–User Interaction Protocol)](https://github.com/ag-ui-protocol/ag-ui) is an open, lightweight, event-based protocol that standardizes real-time communication between AI agents and user-facing applications.

In an agentic app, the frontend (let's suppose a React UI) and the agent backend exchange a stream of JSON events (such as messages, tool calls, state updates, lifecycle signals) over WebSockets, SSE or HTTP.

This lets the UI stay in perfect sync with the agent’s progress, streaming tokens as they are generated, showing tool execution progress and reflecting live state changes.

Instead of custom WebSockets or ad-hoc JSON per agent, AG-UI provides a `common vocabulary of events`, so any AG-UI compatible agent (such as LangGraph, CrewAI, Mastra, LlamaIndex, Pydantic AI, Agno) can plug into any AG-UI aware frontend without rewriting the integration. Check the list of all [supported frameworks](https://docs.ag-ui.com/introduction#supported-frameworks).

For example, the diagram below shows how a user action in the UI is sent via AG-UI to any agent backend and responses flow back as standardized events:

![protocol](https://cdn.sanity.io/images/y3fjfzcd/production/f5f9aacafd5503eb9aa10e93a5a744c7dacfd4d9-760x960.webp)

*Credit:* [dailydoseofds.com](https://blog.dailydoseofds.com/p/updates-to-the-ag-ui-protocol)

You can create a new app using the CLI with the following command.

```
npx create-ag-ui-app@latest
```

## 2. What are AG-UI Event Types and why should you care about them?

AG-UI defines 17 core event types (special cases included), covering everything an agent might do during its lifecycle. Think of events as the basic communication units between agents and frontends.

Each event is a JSON object with a `type` (such as `"TextMessageContent"`, `"ToolCallStart"`) with a payload.

![ag-ui event diagram](https://cdn.sanity.io/images/y3fjfzcd/production/c0b02ed4b504075d4353555b89beaf61820d8153-800x394.webp)

*Credit:* [dailydoseofds.com](https://blog.dailydoseofds.com/p/updates-to-the-ag-ui-protocol)

Because these events are standard and self-describing, the front-end knows exactly how to interpret them. For example:

* `TEXT_MESSAGE_CONTENT` : event streams LLM tokens
* `TOOL_CALL_START/END` : convey function call progress
* `STATE_DELTA` : carries JSON Patch deltas to sync state

Standardizing these -- decouples the UI from the agent logic and vice versa. The UI doesn’t need custom glue code to understand the agent’s behavior.

Any agent backend can **emit AG-UI events**.
And any AG-UI compliant UI can **consume them**.

The protocol groups all the events into five high-level categories:

✅ `Lifecycle Events` : Track the progress of an agent run (start, finish, errors, sub-steps).

✅ `Text Message Events` : Stream chat or other text content (token by token).

✅ `Tool Call Events` : Report calls to external tools or APIs and their results.

✅ `State Management Events` : Synchronize shared application state between agent and UI.

✅ `Special Events` : Generic passthrough or custom events for advanced use cases.

In the next section, let's learn all about them along with practical examples.

## 3. Breaking ALL Events with Practical Examples

If you are interested in exploring yourself, read the [official docs](https://docs.ag-ui.com/concepts/events) which includes an overview, lifecycle events, flow patterns and more.

All events inherit from the `BaseEvent` type, which provides common properties shared across all event types:

* `type` : what kind of event it is
* `timestamp` (optional) : when the event was created
* `rawEvent` (optional) : the original event data if the event was transformed

```
type BaseEvent = {
  type: EventType // Discriminator field
  timestamp?: number
  rawEvent?: any
}
```

There are other properties (like `runId`, `threadId`) that are specific to the event type.

### Event Encoding

The Agent User Interaction Protocol uses a streaming approach to send events from agents to clients. The `EventEncoder` class provides the functionality to encode events into a format that can be sent over HTTP.

We will be using it in the examples in all the event categories so here's a simple example:

```
from ag_ui.core import BaseEvent
from ag_ui.encoder import EventEncoder

# Initialize the encoder
encoder = EventEncoder()

# Encode an event
encoded_event = encoder.encode(event)
```

Once the encoder is set up, agents can emit events in real time, and frontends can listen and react to them immediately. Read more on the [docs](https://docs.ag-ui.com/sdk/python/encoder/overview).

Let's cover each category in-depth with examples.

### ✅ Lifecycle Events

Lifecycle events help to monitor the overall run and its sub-steps. They tell the UI when a run starts, progresses, succeeds or fails.

The five lifecycle events are:

1) `RunStarted` : signals the start of an agent run
2) `RunFinished` : signals successful completion of a run.
3) `RunError` : signals a failure during the run.
4) `StepStarted` (optional) : start of a sub-task within a run.
5) `StepFinished` : marks the completion of a sub-task.

There could be multiple `StepStarted` / `StepFinished` pairs within a single run, representing progress through intermediate sub-tasks.

Example flow:

* `RunStarted → (StepStarted → StepFinished …) → RunFinished`
* If something fails, RunError replaces RunFinished.

Here's a simple example of how events are emitted on the agent's side:

```
# When the agent starts running
yield encoder.encode(RunStartedEvent(
    type=EventType.RUN_STARTED,
    thread_id=thread_id,
    run_id=run_id
))
# ... agent does work (e.g. sends messages, calls tools, etc.) ...
# When the run completes
yield encoder.encode(RunFinishedEvent(
    type=EventType.RUN_FINISHED,
    thread_id=thread_id,
    run_id=run_id
))
```

Here is a simple example code of a stock analysis Agent (frontend side).

```
async function handleLifecycleEvents(event) {
switch(event.type) {
case 'RUN_STARTED':
// event.thread_id, event.run_id are available in real AG-UI events
setAgentStatus('processing');
showProgressBar();
break;
case 'STEP_STARTED':
  updateStepIndicator(event.step_name);
  // e.g. "Gathering stock data", "Analyzing trends", "Generating insights"
  break;

case 'STEP_FINISHED':
  clearStepIndicator(event.step_name);
  break;

case 'RUN_FINISHED':
// event.thread_id, event.run_id context here too
  setAgentStatus('completed');
  hideProgressBar();
  break;

case 'RUN_ERROR':
  showErrorUI(event.error);
  offerRetryOption();
  logErrorForDebugging(event);
  break;

}
}
```

Here the UI would listen for these events to know when to show loading indicators and when to display the final result. If something goes wrong, the agent would emit `RunError` instead, which the UI can catch to display an error message.

### ✅ Text Message Events

Text events carry human or assistant messages, typically streaming content token by token. There are three events defined in this category:

1) `TEXT_MESSAGE_START` : signals the start of a new message. Contains `messageId` and `role` (such as “developer”, “system”, “assistant”, “user”, “tool”) as properties.

2) `TEXT_MESSAGE_CONTENT` : carries a chunk of text (`delta`) as it’s generated, allowing the UI to display text in real time.

3) `TEXT_MESSAGE_END` : signals the end of the message.

In non-streaming scenarios, when the entire content is available at once, the agent might use the `TextMessageChunk` event, which sends complete text messages in a single event instead of the three-event sequence. Read more on [docs](https://docs.ag-ui.com/concepts/events#textmessagechunk).

Example flow:

* `TEXT_MESSAGE_START → (TEXT_MESSAGE_CONTENT → TEXT_MESSAGE_CONTENT ...) → TEXT_MESSAGE_END`

Each message is framed by `TEXT_MESSAGE_START` and `TEXT_MESSAGE_END`, with one or more `TEXT_MESSAGE_CONTENT` events in between.

For example, an assistant reply “Hello” might be sent as (agent’s side):

```
yield encoder.encode(TextMessageStartEvent(
    type=EventType.TEXT_MESSAGE_START,
    message_id=msg_id,
    role="assistant"
))
yield encoder.encode(TextMessageContentEvent(
    type=EventType.TEXT_MESSAGE_CONTENT,
    message_id=msg_id,
    delta="Hello"
))
yield encoder.encode(TextMessageEndEvent(
    type=EventType.TEXT_MESSAGE_END,
    message_id=msg_id
))
```

Here's how the UI might handle it:

```
async function handleTextEvents(event) {
  switch(event.type) {
    case 'TEXT_MESSAGE_START':
      createMessageContainer(event.message_id, event.role);
      break;

    case 'TEXT_MESSAGE_CONTENT':
      // Real-time text streaming for natural conversation
      appendToMessage(event.message_id, event.delta);
      break;

    case 'TEXT_MESSAGE_END':
      finalizeMessage(event.message_id);
      enableUserInput();
      break;
  }
}
```

In summary, **Text Message events** handle all streaming of textual content between the agent and UI, decoupling chat logic from the transport.

### ✅ Tool Call Events

These events represent the lifecycle of tool calls made by agents. Tool calls follow a streaming pattern similar to text messages.

1) `TOOL_CALL_START` : emitted when the agent begins calling a tool. Includes a unique `tool_call_id` and `tool_name`.

2) `TOOL_CALL_ARGS` : optionally emitted if the tool’s arguments are streamed in parts. Each event carries a `delta` field containing a partial chunk of the argument data (useful for large or dynamically generated inputs).

3) `TOOL_CALL_END` : marks the completion of the tool call execution.

4) `TOOL_CALL_RESULT` : carries the final output returned by the tool.

Example flow:

`TOOL_CALL_START → (TOOL_CALL_ARGS ...) → TOOL_CALL_END → TOOL_CALL_RESULT`

Here's how it looks on the agent side (emitting events):

```
# Agent initiates tool call
yield encoder.encode(ToolCallStartEvent(
    type=EventType.TOOL_CALL_START,
    tool_call_id="tool123",
    tool_call_name="fetch_weather"
))

# streams tool arguments as they are generated
yield encoder.encode(ToolCallArgsEvent(
    type=EventType.TOOL_CALL_ARGS,
    tool_call_id="tool123",
    delta=json.dumps({"city": "San Francisco"})
))

# Agent signals end of call
yield encoder.encode(ToolCallEndEvent(
    type=EventType.TOOL_CALL_END,
    tool_call_id="tool123"
))

# Agent provides the tool result back to the UI
yield encoder.encode(ToolCallResultEvent(
    type=EventType.TOOL_CALL_RESULT,
    tool_call_id="tool123",
    content="72°F, Sunny"
))
```

Here’s the example code on the frontend side:

```
async function handleToolEvents(event) {
  switch(event.type) {
    case 'TOOL_CALL_START':
      showLoadingSpinner(`Calling ${event.tool_call_name}...`);
      break;
case 'TOOL_CALL_ARGS':
  displayToolParams(event.tool_call_id, event.delta);
  // Show: "Getting weather for San Francisco, CA"
  break;

case 'TOOL_CALL_RESULT':
  displayToolResult(event.content);
  hideLoadingSpinner();
  break;

}
}
```

By listening to these events, the UI can show real-time tool progress (such as “Loading data…”) and then display the results (under a “tool” role) when ready.

### ✅ State Management Events

These events are used to manage and synchronize the agent’s state with the frontend. Instead of re-sending a large data blob each time, the agent follows an efficient snapshot-delta pattern where:

1) `StateSnapshot` : sends a full JSON snapshot of the current state. Useful for initial sync or occasional full refreshes.

2) `StateDelta` : sends incremental changes as a JSON Patch diff ([RFC6902](https://datatracker.ietf.org/doc/html/rfc6902)). Reduces data transfer for frequent updates.

3) `MessagesSnapshot` (optional) : sends a full conversation history if needed to resync the UI.

Example flow:

* `StateSnapshot → (StateDelta → StateDelta …) → StateSnapshot → (StateDelta ...)`

The agent starts with a `StateSnapshot` to initialize the frontend, then streams incremental `StateDelta` events as changes occur. Occasional `StateSnapshot` events to resync if needed.

Here's how it looks on the agent side (emitting events):

```
# Send full state snapshot (initial or large update)
yield encoder.encode(StateSnapshotEvent(
    type=EventType.STATE_SNAPSHOT,
    snapshot={
        "score": 0,
        "tasks_completed": 0,
        "current_step": "fetching_data"
    }
))

# Later, send just the change (JSON Patch format)
yield encoder.encode(StateDeltaEvent(
    type=EventType.STATE_DELTA,
    delta=[
        {"op": "replace", "path": "/score", "value": 42},
        {"op": "replace", "path": "/current_step", "value": "analyzing_data"}
    ]
))

# optional: sync entire conversation history
yield encoder.encode(MessagesSnapshotEvent(
    type=EventType.MESSAGES_SNAPSHOT,
    messages=[...]
))
```

Here’s how to handle those events on the frontend side:

```
async function handleStateEvents(event) {
  switch(event.type) {
    case 'STATE_SNAPSHOT':
      setAppState(event.snapshot);
      restoreUIFromState(event.snapshot); // restore UI from snapshot
      break;

    case 'STATE_DELTA':
      applyStateDelta(event.delta);  // Apply incremental real-time updates
      // Example: event.delta = [{"op": "replace", "path": "/portfolio/AAPL", "value": 1250}]
      break;

    case 'MESSAGES_SNAPSHOT':
      setMessageHistory(event.messages);  // Replace conversation history if needed
      break;
  }
}
```

Let's suppose an agent is updating a UI table or a shopping cart: it can add or modify entries via a state delta instead of re-sending the whole table.

By using state events, the UI can merge small updates without restarting from scratch.

### ✅ Special Events

Special events are `“catch-all”` events in AG-UI. They are used when an interaction doesn’t fit into the usual categories. These don’t follow the standard lifecycle or streaming patterns of other event types.

In simple terms: If you need the agent and frontend to do something unique or custom that the standard events don’t cover, you use special events.

1) `RawEvent` :

* Used to pass through events from external systems.
* Acts as a container for events originating outside AG-UI, preserving the original data.
* The optional `source` property can identify the external system.
* Frontends can handle these events directly or delegate them to system-specific handlers.
* Properties: `event` contains the original event data & `source` (optional) identifies the external system.

2) `CustomEvent` :

* Used for application-specific events not covered by standard types.
* Explicitly part of the protocol (unlike Raw) but fully defined by the app.
* Enables protocol extensions without changing the specification.
* Properties: `name` identifies the custom event & `value` contains the associated data.

Let's say if you want to implement a multi-agent workflow where control passes from one agent to another, you could define a custom event like:

```
{
  "type": "Custom",
  "name": "AGENT_HANDOFF",
  "value": {
    "from_agent": "Planner",
    "to_agent": "Executor"
  }
}
```

AG-UI doesn’t inherently know what `“handoff”` means, it’s up to your application code to enforce it. So `Custom` enables this pattern, but it’s entirely app-defined.

Example flow:

* `RawEvent → CustomEvent → RawEvent → CustomEvent …`

These events don’t have a fixed order: they appear as needed in the event stream, depending on external triggers and app-specific logic.

Here's a simple example on the agent side:

```
# Raw event from an external monitoring system
yield encoder.encode(RawEvent(
    type=EventType.RAW,
    event={"alert": "high_cpu", "value": 92},
    source="monitoring_system"
))

# Custom event to handoff control between agents (we discussed earlier)
yield encoder.encode(CustomEvent(
    type=EventType.CUSTOM,
    name="AGENT_HANDOFF",
    value={"from_agent": "Planner", "to_agent": "Executor"}
))
```

Here's how it is handled on the frontend side:

```
async function handleSpecialEvents(event) {
  switch(event.type) {
    case 'RAW':
      forwardToExternalSystem(event.event, event.source);
      console.log("External system event:", event.source, event.event);
      break;

    case 'CUSTOM':
      if(event.name === "AGENT_HANDOFF") {
        switchActiveAgent(event.value.from_agent, event.value.to_agent);
      }
      break;
  }
}
```

In short, special events provide an extension point when you need “something extra” beyond the core AG-UI schema.

### ✅ Draft Events

There are more events that are currently in draft status and may change before finalization. Here are some of those types:

* `Activity Events` : will represent agent progress between messages, letting the UI show fine-grained updates in order.
* `Reasoning Events` : will support LLM reasoning visibility and continuity, enabling chain-of-thought reasoning.
* `Meta Events` : will provide annotations or signals independent of agent runs, like user feedback or external events.
* `Modified Lifecycle Events` : will extend existing lifecycle events to handle interrupts or branching.

Check the complete list on the [official docs](https://docs.ag-ui.com/concepts/events#draft-events).

In the next section, you will find a live interaction flow to understand how all the events come together to work in practice.

## Live Interaction Flow (showing even stream)

Here’s a live example combining multiple event types to illustrate the full lifecycle of an agent interaction. You can try it out at .

<https://www.copilotkit.ai/blog/introducing-the-ag-ui-dojo>

Here's the complete event sequence from the [LangGraph AG-UI demo](https://github.com/copilotkit-support/open-ag-ui-demo-langgraph) showing a stock analysis agent:

```
RUN_STARTED → Agent begins processing user investment query
STATE_SNAPSHOT → Initialize portfolio state with available cash
TEXT_MESSAGE_START → Begin greeting message
TEXT_MESSAGE_CONTENT → Stream "Analyzing your investment request..."
TEXT_MESSAGE_END → Complete greeting message
TOOL_CALL_START → Begin stock data extraction
TOOL_CALL_ARGS → Show parameters: {"tickers": ["AAPL"], "amount": [10000]}
TOOL_CALL_END → Stock data fetch complete
STATE_DELTA → Update tool logs: "Gathering stock data" → "completed"
TOOL_CALL_START → Begin cash allocation calculations
STATE_DELTA → Update portfolio holdings in real-time
TEXT_MESSAGE_START → Begin analysis response
TEXT_MESSAGE_CONTENT → Stream investment analysis results
TEXT_MESSAGE_END → Complete analysis message
TOOL_CALL_START → Generate bull/bear insights
TOOL_CALL_RESULT → Display investment insights
RUN_FINISHED → Agent task complete
```

Once you get the hang of AG-UI events, you realize how much simpler and more predictable interactive agents become.

It’s one of those specs that quietly solves a big problem for anyone building serious agent apps.

I hope you learned something valuable. Have a great day!

‍

## Top posts

[See All](/blog)

[![AWS Announces Dedicated AG-UI Endpoint in AgentCore and FAST Template for Building Fullstack Agents](/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2Fy3fjfzcd%2Fproduction%2F1e4f8d388ffce8b95b1b2dbf477f141ac039d97b-1920x1080.png&w=3840&q=75)

Anmol Baranwal and Nathan TarbertMarch 24, 2026

AWS Announces Dedicated AG-UI Endpoint in AgentCore and FAST Template for Building Fullstack AgentsAWS and CopilotKit release a dedicated AG-UI endpoint in AgentCore and a new FAST template pattern with Generative UI, shared state, and human-in-the-loop flows out of the box.](/blog/aws-announces-dedicated-ag-ui-endpoint-in-agentcore-and-fast-template-for-building-fullstack-agents)[![Reusable Agents Meet Generative UIs](/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2Fy3fjfzcd%2Fproduction%2F30ffc80380890b29471a8fcbc7f7f7939ca0c3eb-1000x400.png&w=3840&q=75)

Anmol Baranwal and Nathan TarbertMarch 12, 2026

Reusable Agents Meet Generative UIsOracle, Google, and CopilotKit have jointly released an integration that standardizes how AI agents are defined, how they communicate with frontends in real time, and how they describe the UI they require.
The integration connects three distinct layers. Oracle's Open Agent Specification (Agent Spec) provides a framework-agnostic way to define agent logic, workflows, and tool usage once and run it across compatible runtimes. AG-UI handles the live interaction stream between the agent and the frontend, keeping tool progress, state updates, and user interactions synchronized while the agent is executing.
A2UI, developed by Google, allows agents to describe the UI they need - forms, tables, multi-step flows - as structured JSONL, which CopilotKit then renders automatically inside the host application.
Previously, each of these layers required custom implementation per project. This release establishes a shared contract across all three, meaning agent developers can define the agent once, expose a standardized interaction stream, and have the frontend render structured UI surfaces without writing custom wiring for each tool or workflow.
The practical impact is reduced integration friction across the ecosystem - agent runtimes and frontend clients that implement these standards can interoperate without lock-in to a specific framework or vendor.](/blog/reusable-agents-meet-generative-uis)[![The Developer's Guide to Generative UI in 2026](/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2Fy3fjfzcd%2Fproduction%2Fff99f879000b0a01c7cb24e74cc43825036eff9a-3200x1800.png&w=3840&q=75)

Anmol Baranwal and Nathan TarbertJanuary 29, 2026

The Developer's Guide to Generative UI in 2026AI agents have become much better at reasoning and planning. The UI layer has mostly stayed the same, and it is holding back the experience.
Most agent experiences still rely on chat, even when the task clearly needs forms, previews, controls, or step-by-step feedback.
Generative UI is the idea that allows agents to influence the interface at runtime, so the UI can change as context changes. This is usually done through UI specs like A2UI, Open-JSON-UI, or MCP Apps.
We'll break down Generative UI, the three practical patterns, and how CopilotKit supports them (using AG-UI protocol under the hood).](/blog/the-developer-s-guide-to-generative-ui-in-2026)

Are you ready?

## Stay in the know

Subscribe to our blog and get updates on CopilotKit in your inbox.

Subscribe

![](https://static.scarf.sh/a.png?x-pxid=1c040678-b704-471e-a3f5-69c6bf52b703)
