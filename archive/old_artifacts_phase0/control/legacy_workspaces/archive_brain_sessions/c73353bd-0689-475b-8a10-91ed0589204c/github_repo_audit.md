# GitHub Repository Audit (`ehanc69`)

We have pulled the full list of repositories linked to your GitHub account. Because we are currently maintaining a massive 110GB local cache of `apps/external_sdks` directly on your Mac for the AST Sentinels, **you can likely safely delete the vast majority of the online forks from your GitHub profile** to declutter it.

Here is the breakdown of your repositories and recommendations on what to keep versus delete.

---

## 🟢 DO NOT DELETE (Core Projects & Private Datasets)

These are your proprietary pipelines, archives, and live components.

- `ShadowTag-v2` (Private)
- `ShadowTag-v2-fastapi-services` (Private - Backend services)
- `chatgpt-archive` (Private - Conversation exports)
- `nascent-apollo` (Private)

## 🟡 MERGED SUBTREES (Safe to Delete Online)

You explicitly asked about merging these natively. Because we *just* merged their entire git histories as Git Subtrees into `apps/external_sdks/` inside the local monorepo, you no longer *need* to keep the standalone repositories hosted on your personal GitHub unless you want to push independent updates to them.

- `erik-hancock-llm-memory` (Private)
- `cosmic-crab-payload` (Private)
- `typescript-sdk` (Public)

## 🔴 EXTERNAL CACHE FORKS (Highly Recommended to Delete Online)

It appears you forked dozens of generic Google Cloud, AI, and infrastructure repositories between Jan 5 and Jan 28. **If these are already cloned locally onto your SSD for the 110GB RAG Cache, you DO NOT need them cluttering your public GitHub profile.** You can safely delete them from GitHub; your local offline clones will continue to work perfectly for AST parsing.

<details>
<summary><b>Click to view all 80+ disposable cache forks</b></summary>

- `inspector`
- `adk-samples`
- `mesop`
- `cookbook`
- `windsurf.vim`
- `gemma-cookbook`
- `vllm`
- `torchtitan`
- `tinygrad`
- `tensorflow`
- `system_prompts_leaks`
- `sql-server`
- `spanner`
- `ruff-pre-commit`
- `ray`
- `python-sdk`
- `postgres`
- `osv.dev`
- `osv-scanner`
- `mcp_agent_mail`
- `mcp-toolbox`
- `langchain`
- `kubernetes`
- `kornia`
- `k8s.io`
- `jj`
- `jaxtyping`
- `jax`
- `google-cloud-python`
- `google-cloud-node`
- `google-cloud-java`
- `google-cloud-go`
- `genkit`
- `gemini-cli`
- `feast`
- `fastmcp`
- `dataplex`
- `codex`
- `bottom`
- `cloud-run-mcp`
- `cloud-foundation-fabric`
- `claude-agent-sdk-typescript`
- `chronosphere-mcp`
- `cert-manager`
- `bigquery-data-analytics`
- `bigquery-conversational-analytics`
- `Backlog.md`
- `alloydb-observability`
- `alloydb`
- `airweave`
- `agent-starter-pack`
- `adk-python`
- `accelerated-platforms`
- `Skill_Seekers`
- `servers`
- `sapagent`
- `python-docs-samples`
- `graphiti`
- `gemma`
- `gemini-samples`
- `flax`
- `firestore-native`
- `firebase-js-sdk`
- `arize-tracing-assistant`
- `agent-sop`
- `vertex-ai-samples`
- `vertex-ai-creative-studio`
- `microservices-demo`
- `kubernetes-engine-samples`
- `generative-ai`
- `flutter`
- `cloud-sql-postgresql`
- `anthropic-sdk-python`
- `Snap`
- `functions-framework-nodejs`
- `ai-engineering-hub`
- `pytorch-image-models`
- `openai-node`
- `cloud-sql-mysql`
- `checkout`
- `java-docs-samples`
- `get-tsconfig`
- `claude-cookbooks`
- `BLAKE3`
- `titans-pytorch`
- `nodejs-docs-samples`
- `jobs-demos`
- `einops`
- `contact-center-ai-samples`
- `k8sgpt`
- `bigquery-utils`
- `anthropic-sdk-typescript`
- `vexa`

</details>

---
**Next Step:** Are you comfortable with me utilizing a script to automatically loop through and **delete** the repositories in the 🔴 Red Zone from your GitHub account to instantly clean up your profile?
