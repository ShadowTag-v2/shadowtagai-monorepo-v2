#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# AGNT_OS v15.0 — COMPLETE EXTERNAL REFERENCE CLONE SCRIPT
# Includes all 22+ groups (May 2026)
# ============================================================

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "${ROOT}"

DEST="${DEST:-${ROOT}/external_repos/upstream}"
LOG_DIR="${ROOT}/.reports/external_repos"
LOG_FILE="${LOG_DIR}/clone-log.tsv"

mkdir -p "${DEST}" "${LOG_DIR}"
touch "${LOG_FILE}"

# === ALL GROUPS ===
BUILD_REPOS=(bazelbuild/bazel bazelbuild/buildtools bazelbuild/rules_python aspect-build/rules_js aspect-build/rules_ts)
EXECUTION_REPOS=(dagger/dagger temporalio/temporal temporalio/sdk-python)
AUTHZ_REPOS=(openfga/openfga openfga/cli authzed/spicedb)
SEARCH_REPOS=(BurntSushi/ripgrep ast-grep/ast-grep ast-grep/ast-grep-mcp ast-grep/ast-grep-vscode)
SECURITY_REPOS=(trufflesecurity/trufflehog gitleaks/gitleaks betterleaks/betterleaks Vanta/vanta)
MEMORY_REPOS=(steveyegge/beads intellectronica/ruler VectifyAI/PageIndex mainion-ai/memory-kernel)
AGENT_MEMORY_REPOS=(compass-ai/compass Beever-AI/beever-atlas holaOS/holaOS omegamemory/omega)
MONOREPO_REPOS=(abhigyanpatwari/GitNexus repowise-dev/repowise nrwl/nx GoogleCloudPlatform/agent-starter-pack)
DEV_WORKFLOW_REPOS=(Nutlope/aicommits microsoft/vscode-pull-request-github coderabbitai/git-worktree-runner)
EDITOR_REPOS=(microsoft/vscode-pull-request-github Yggdroot/LeaderF)
COLLAB_REPOS=(hbons/SparkleShare go-gitea/gitea)
QUALITY_REPOS=(astral-sh/ruff biomejs/biome pre-commit/pre-commit renovatebot/renovate GoogleChrome/lighthouse bazelbuild/buildtools)
COMMAND_DECK_REPOS=(ag-ui-protocol/ag-ui xyflow/xyflow TanStack/table shadcn-ui/ui)
MCP_REPOS=(modelcontextprotocol/specification modelcontextprotocol/servers langchain-ai/langgraph)
DOCS_REPOS=(anuraghazra/github-readme-stats)
GITHUB_AUTH_REPOS=(actions/create-github-app-token)
CONTAINERIZATION_REPOS=(moby/moby kubernetes/kubernetes containerd/containerd docker/buildx google/kaniko aquasecurity/trivy anchore/syft sigstore/cosign buildpacks/pack)
CICD_REPOS=(argoproj/argo-cd argoproj/argo-workflows tektoncd/pipeline earthly/earthly fluxcd/flux2 dflook/terraform-github-actions)
MONITORING_REPOS=(prometheus/prometheus grafana/grafana jaegertracing/jaeger opentelemetry/opentelemetry-collector grafana/loki grafana/tempo)
TERRAFORM_IAC_REPOS=(GoogleCloudPlatform/terraformer hashicorp/terraform bregman-arie/devops-exercises MichaelCade/90DaysOfDevOps iam-veeramalla/terraform-zero-to-hero GoogleCloudPlatform/microservices-demo GoogleCloudPlatform/gcp-hardening-toolkit GoogleCloudPlatform/cloud-foundation-fabric GoogleCloudPlatform/terraform-google-vertex-ai GoogleCloudPlatform/genai-factory GoogleCloudPlatform/magic-modules GoogleCloudPlatform/click-to-deploy-solutions gruntwork-io/terragrunt-infrastructure-catalog-example gruntwork-io/terragrunt-infrastructure-live-example gruntwork-io/terragrunt-infrastructure-live-stacks-example gruntwork-io/runbooks-infrastructure-live-example gruntwork-io/terragrunt gruntwork-io/pipelines-workflows opentofu/opentofu bpg/terraform-provider-proxmox)
PULUMI_REPOS=(pulumi/pulumi pulumi/examples)
SEMAPHORE_REPOS=(semaphoreui/semaphore)

clone_repo() {
    local group="$1"
    local repo="$2"
    local target_dir="${DEST}/${group}/$(basename "$repo")"

    if [ -d "$target_dir" ]; then
        echo "✓ Already exists: $repo"
        return 0
    fi

    echo "→ Cloning $repo into $group..."
    git clone --depth 1 --filter=blob:none "https://github.com/$repo.git" "$target_dir" 2>/dev/null || {
        echo "✗ Failed to clone: $repo (skipping)"
        return 0
    }

    echo -e "$(date '+%Y-%m-%d %H:%M:%S')\t$group\t$repo\t$(du -sh "$target_dir" | cut -f1)" >> "$LOG_FILE"
}

clone_list() {
    local group="$1"
    shift
    for repo in "$@"; do
        clone_repo "$group" "$repo"
    done
}

echo "📥 AGNT_OS v15.0 — Cloning all external reference repositories..."
echo "Destination: $DEST"
echo ""

clone_list build            "${BUILD_REPOS[@]}"
clone_list execution        "${EXECUTION_REPOS[@]}"
clone_list authz            "${AUTHZ_REPOS[@]}"
clone_list search           "${SEARCH_REPOS[@]}"
clone_list security         "${SECURITY_REPOS[@]}"
clone_list memory           "${MEMORY_REPOS[@]}"
clone_list agent_memory     "${AGENT_MEMORY_REPOS[@]}"
clone_list monorepo         "${MONOREPO_REPOS[@]}"
clone_list dev_workflow     "${DEV_WORKFLOW_REPOS[@]}"
clone_list editor           "${EDITOR_REPOS[@]}"
clone_list collab           "${COLLAB_REPOS[@]}"
clone_list quality          "${QUALITY_REPOS[@]}"
clone_list command_deck     "${COMMAND_DECK_REPOS[@]}"
clone_list mcp              "${MCP_REPOS[@]}"
clone_list docs             "${DOCS_REPOS[@]}"
clone_list github_auth      "${GITHUB_AUTH_REPOS[@]}"
clone_list containerization "${CONTAINERIZATION_REPOS[@]}"
clone_list cicd             "${CICD_REPOS[@]}"
clone_list monitoring       "${MONITORING_REPOS[@]}"
clone_list terraform_iac    "${TERRAFORM_IAC_REPOS[@]}"
clone_list pulumi           "${PULUMI_REPOS[@]}"
clone_list semaphore        "${SEMAPHORE_REPOS[@]}"

echo ""
echo "✅ All repositories cloned successfully."
echo "📊 Log saved to: $LOG_FILE"
echo "📦 Total groups: 22"
