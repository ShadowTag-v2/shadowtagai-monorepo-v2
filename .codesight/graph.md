# Dependency Graph

## Most Imported Files (change these carefully)

- `external_repos/node/test/common/index.js` — imported by **4885** files
- `external_repos/node/test/common/fixtures.js` — imported by **1104** files
- `external_repos/node/test/common/tmpdir.js` — imported by **735** files
- `external_repos/node/benchmark/common.js` — imported by **436** files
- `external_repos/firebase-tools/src/error.ts` — imported by **333** files
- `path/filepath` — imported by **326** files
- `encoding/json` — imported by **303** files
- `net/http` — imported by **300** files
- `external_repos/firebase-tools/src/utils.ts` — imported by **232** files
- `external_repos/firebase-tools/src/logger.ts` — imported by **222** files
- `external_repos/node/test/common/child_process.js` — imported by **195** files
- `external_repos/firebase-tools/src/command.ts` — imported by **181** files
- `archive/claude-code-src-leak/src/utils/debug.ts` — imported by **158** files
- `archive/claude-code-src-leak/src/ink.ts` — imported by **153** files
- `external_repos/firebase-tools/src/api.ts` — imported by **133** files
- `external_repos/node/test/common/crypto.js` — imported by **123** files
- `net/url` — imported by **115** files
- `external_repos/firebase-tools/src/projectUtils.ts` — imported by **110** files
- `archive/claude-code-src-leak/src/utils/envUtils.ts` — imported by **106** files
- `external_repos/firebase-tools/src/apiv2.ts` — imported by **103** files

## Import Map (who imports what)

- `external_repos/node/test/common/index.js` ← `external_repos/node/benchmark/http/http_server_for_chunky_client.js`, `external_repos/node/test/abort/test-abort-backtrace.js`, `external_repos/node/test/abort/test-abort-fatal-error.js`, `external_repos/node/test/abort/test-abort-uncaught-exception.js`, `external_repos/node/test/abort/test-addon-register-signal-handler.js` +4880 more
- `external_repos/node/test/common/fixtures.js` ← `external_repos/node/benchmark/esm/import-cjs.js`, `external_repos/node/benchmark/fixtures/simple-https-server.js`, `external_repos/node/benchmark/source_map/source-map-cache.js`, `external_repos/node/benchmark/source_map/source-map.js`, `external_repos/node/benchmark/tls/secure-pair.js` +1099 more
- `external_repos/node/test/common/tmpdir.js` ← `external_repos/node/benchmark/esm/detect-esm-syntax.js`, `external_repos/node/benchmark/esm/esm-legacyMainResolve.js`, `external_repos/node/benchmark/esm/esm-loader-defaultResolve.js`, `external_repos/node/benchmark/esm/esm-loader-import.js`, `external_repos/node/benchmark/esm/import-cjs.js` +730 more
- `external_repos/node/benchmark/common.js` ← `external_repos/node/benchmark/abort_controller/abort-signal-static-abort.js`, `external_repos/node/benchmark/assert/assertion-error.js`, `external_repos/node/benchmark/assert/deepequal-buffer.js`, `external_repos/node/benchmark/assert/deepequal-map.js`, `external_repos/node/benchmark/assert/deepequal-object.js` +431 more
- `external_repos/firebase-tools/src/error.ts` ← `external_repos/firebase-tools/src/accountExporter.ts`, `external_repos/firebase-tools/src/accountImporter.ts`, `external_repos/firebase-tools/src/agentSkills.ts`, `external_repos/firebase-tools/src/apiv2.spec.ts`, `external_repos/firebase-tools/src/apiv2.ts` +328 more
- `path/filepath` ← `external_repos/Mole/cmd/analyze/analyze_test.go`, `external_repos/Mole/cmd/analyze/cache.go`, `external_repos/Mole/cmd/analyze/cleanable.go`, `external_repos/Mole/cmd/analyze/delete.go`, `external_repos/Mole/cmd/analyze/delete_test.go` +321 more
- `encoding/json` ← `apps/bennett/edge/main.go`, `external_repos/Mole/cmd/analyze/cache.go`, `external_repos/Mole/cmd/analyze/json.go`, `external_repos/Mole/cmd/status/main.go`, `external_repos/Mole/cmd/status/metrics_gpu.go` +298 more
- `net/http` ← `apps/aiyou_stack/aiyou-fastapi-services/cloud-run-go/main.go`, `apps/aiyou_stack/shield/shield.go`, `apps/bennett/edge/main.go`, `external_repos/apps/open-location-code/tile_server/main.go`, `external_repos/apps/terragrunt/test/integration_aws_oidc_test.go` +295 more
- `external_repos/firebase-tools/src/utils.ts` ← `external_repos/firebase-tools/scripts/emulator-tests/functionsEmulatorRuntime.spec.ts`, `external_repos/firebase-tools/scripts/webframeworks-deploy-tests/tests.ts`, `external_repos/firebase-tools/src/accountExporter.ts`, `external_repos/firebase-tools/src/accountImporter.ts`, `external_repos/firebase-tools/src/agentSkills.spec.ts` +227 more
- `external_repos/firebase-tools/src/logger.ts` ← `external_repos/firebase-tools/firebase-vscode/src/logger-wrapper.ts`, `external_repos/firebase-tools/scripts/emulator-tests/functionsEmulator.spec.ts`, `external_repos/firebase-tools/src/accountImporter.ts`, `external_repos/firebase-tools/src/api.ts`, `external_repos/firebase-tools/src/apiv2.ts` +217 more
