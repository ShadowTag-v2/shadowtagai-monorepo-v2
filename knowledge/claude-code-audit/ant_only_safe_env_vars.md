# ANT_ONLY_SAFE_ENV_VARS Allowlist

Extracted from \`src/tools/BashTool/bashPermissions.ts\`. These environment variables are uniquely permitted for internal Anthropic (Ant) users and are bypassed during prefix permission matching to prevent strict deny-rules from blocking workflow operations.

### Kubernetes and Container Config
- \`KUBECONFIG\`
- \`DOCKER_HOST\`

### Cloud Provider / Project Selection
- \`AWS_PROFILE\`
- \`CLOUDSDK_CORE_PROJECT\`
- \`CLUSTER\`
- \`COO_CLUSTER\`
- \`COO_CLUSTER_NAME\`
- \`COO_NAMESPACE\`
- \`COO_LAUNCH_YAML_DRY_RUN\`

### Feature Flags
- \`SKIP_NODE_VERSION_CHECK\`
- \`EXPECTTEST_ACCEPT\`
- \`CI\`
- \`GIT_LFS_SKIP_SMUDGE\`

### GPU / Hardware Selection
- \`CUDA_VISIBLE_DEVICES\`
- \`JAX_PLATFORMS\`

### Display / Terminal
- \`COLUMNS\`
- \`TMUX\`

### Test / Debug Configuration
- \`POSTGRESQL_VERSION\`
- \`FIRESTORE_EMULATOR_HOST\`
- \`HARNESS_QUIET\`
- \`TEST_CROSSCHECK_LISTS_MATCH_UPDATE\`
- \`DBT_PER_DEVELOPER_ENVIRONMENTS\`
- \`STATSIG_FORD_DB_CHECKS\`

### Build Configuration
- \`ANT_ENVIRONMENT\`
- \`ANT_SERVICE\`
- \`MONOREPO_ROOT_DIR\`

### Version Selectors
- \`PYENV_VERSION\`

### Credentials (Approved Subset)
- \`PGPASSWORD\`
- \`GH_TOKEN\`
- \`GROWTHBOOK_API_KEY\`
