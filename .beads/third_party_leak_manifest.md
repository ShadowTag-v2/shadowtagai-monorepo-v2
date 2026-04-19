# Third-Party Leak Manifest

**Generated**: 2026-04-19
**Total Findings**: 686 occurrences → **227 unique secrets**
**Sources**: reference_architectures/ (670), libs/cyberpunk_stack/ (7), labs/ (9)

> [!NOTE]
> These are ALL third-party code — cloned repos, SDK bundles, R&D experiments.
> None are our production secrets. Use `[ ]` checkboxes to select items for action.

---

## Summary by Rule Type

| Rule | Unique Secrets | Occurrences | Risk Level | Source Repos |
|------|---------------|-------------|------------|--------------|
| `algolia-api-key` | 1 | 2 | 🟢 LOW | lighthouse |
| `curl-auth-header` | 1 | 4 | 🟢 LOW | opentofu |
| `curl-auth-user` | 4 | 4 | 🟢 LOW | terraform |
| `discord-client-secret` | 2 | 4 | 🟡 MEDIUM | libs/cyberpunk_stack |
| `gcp-api-key` | 6 | 32 | 🟡 MEDIUM | libs/cyberpunk_stack, lighthouse, lighthouse-ci, terraform |
| `generic-api-key` | 162 | 539 | 🟢 LOW | FFmpeg, claude-code-src, flagger, labs, libs/cyberpunk_stack, lighthouse, lighthouse-ci, notebooklm-py, obsidian-excalidraw-plugin, opentofu, semaphore, terraform |
| `hashicorp-tf-password` | 3 | 12 | 🟢 LOW | terraform |
| `jwt` | 10 | 18 | 🟡 MEDIUM | lighthouse, lighthouse-ci, terraform |
| `kubernetes-secret-yaml` | 4 | 4 | 🟢 LOW | terraform |
| `octopus-deploy-api-key` | 1 | 2 | 🟢 LOW | terraform |
| `pkcs12-file` | 1 | 9 | 🟢 LOW | terraform |
| `private-key` | 30 | 54 | 🟡 MEDIUM | opentofu, terraform |
| `stripe-access-token` | 1 | 1 | 🔴 HIGH | terraform |
| `vault-service-token` | 1 | 1 | 🔴 HIGH | opentofu |

---

## algolia-api-key (1 unique / 2 occurrences) — 🟢 LOW

- [ ] **#1** `01e025...3358` — lighthouse (2 files)
  - `reference_architectures/lighthouse/core/test/fixtures/user-flows/artifacts/step1/devtoolslog.json:15`
  - `reference_architectures/lighthouse/core/test/fixtures/user-flows/artifacts/step1/devtoolslog.json:29`

---

## curl-auth-header (1 unique / 4 occurrences) — 🟢 LOW

- [ ] **#1** `djE......` — opentofu (4 files)
  - `reference_architectures/opentofu/rfc/20241206-oci-registries/1-oci-primer.md:56`
  - `reference_architectures/opentofu/rfc/20241206-oci-registries/1-oci-primer.md:113`
  - `reference_architectures/opentofu/rfc/20241206-oci-registries/1-oci-primer.md:170`
  - _...and 1 more_

---

## curl-auth-user (4 unique / 4 occurrences) — 🟢 LOW

- [ ] **#1** `"admin...lid"` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/k8s/jenkins/apptest/tester/tests/basic-suite.yaml:12`

- [ ] **#2** `dum...mmy` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/k8s/solr/apptest/tester/tests/solrCloud-test.yaml:24`

- [ ] **#3** `adm...min` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/chef/cookbooks/alfresco/files/alfresco:47`

- [ ] **#4** `admin:...ocks` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/chef/cookbooks/solr/templates/solr.erb:29`

---

## discord-client-secret (2 unique / 4 occurrences) — 🟡 MEDIUM

- [ ] **#1** `resolv...licy` — libs/cyberpunk_stack (3 files)
  - `libs/cyberpunk_stack/openclaw/dist/discord-surface-cCb7mXTR.js:30`
  - `libs/cyberpunk_stack/openclaw/dist/plugin-sdk/discord-surface.js:2`
  - `libs/cyberpunk_stack/openclaw/dist/provider-D2WiXTmZ.js:18886`

- [ ] **#2** `resolv...sage` — libs/cyberpunk_stack (1 file)
  - `libs/cyberpunk_stack/openclaw/dist/accounts-ISdL18DD.js:58`

---

## gcp-api-key (6 unique / 32 occurrences) — 🟡 MEDIUM

- [ ] **#1** `AIzaSy...2l_g` — lighthouse (25 files)
  - `reference_architectures/lighthouse/core/test/fixtures/traces/lcp-m78.json:356`
  - `reference_architectures/lighthouse/core/test/fixtures/traces/lcp-m78.devtools.log.json:1`
  - `reference_architectures/lighthouse/core/test/fixtures/traces/lcp-m78.devtools.log.json:1`
  - _...and 22 more_

- [ ] **#2** `AIzaSy..._oYE` — lighthouse (2 files)
  - `reference_architectures/lighthouse/viewer/app/src/psi-api.js:10`
  - `reference_architectures/lighthouse/viewer/test/viewer-test-pptr.js:410`

- [ ] **#3** `AIzaSy...nsaM` — lighthouse-ci (2 files)
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-5-6-0-verge-b.json:2456`
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-5-6-0-verge-a.json:2486`

- [ ] **#4** `AIzaSy...yCmQ` — lighthouse (1 file)
  - `reference_architectures/lighthouse/viewer/app/src/firebase-auth.js:19`

- [ ] **#5** `AIzaSy...OpMQ` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy-solutions/genai-for-marketing/infra/templates/environments.ts:6`

- [ ] **#6** `AIzaSy...M6Lk` — libs/cyberpunk_stack (1 file)
  - `libs/cyberpunk_stack/openclaw/dist/session-DgeCEcIP.js:77880`

---

## generic-api-key (162 unique / 539 occurrences) — 🟢 LOW

- [ ] **#1** `123456...1098` — terraform (57 files)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/containeraws/resource_container_aws_node_pool_generated_test.go.tmpl:242`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/containeraws/resource_container_aws_node_pool_generated_test.go.tmpl:316`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/containeraws/resource_container_aws_node_pool_generated_test.go.tmpl:409`
  - _...and 54 more_

- [ ] **#2** `79CBEB...D2FC` — opentofu, terraform (36 files)
  - `reference_architectures/opentofu/testing/equivalence-tests/outputs/nested_map_update/plan:15`
  - `reference_architectures/opentofu/testing/equivalence-tests/outputs/nested_map_update/plan:20`
  - `reference_architectures/opentofu/testing/equivalence-tests/outputs/nested_map_update/state:8`
  - _...and 33 more_

- [ ] **#3** `9E8580...0422` — opentofu, terraform (34 files)
  - `reference_architectures/opentofu/testing/equivalence-tests/outputs/nested_map_update/plan:14`
  - `reference_architectures/opentofu/testing/equivalence-tests/outputs/nested_map_update/state:11`
  - `reference_architectures/opentofu/testing/equivalence-tests/outputs/nested_map_update/state.json:28`
  - _...and 31 more_

- [ ] **#4** `6E80C7...9052` — opentofu, terraform (34 files)
  - `reference_architectures/opentofu/testing/equivalence-tests/outputs/nested_map_update/plan:19`
  - `reference_architectures/opentofu/testing/equivalence-tests/outputs/nested_map_update/state:6`
  - `reference_architectures/opentofu/testing/equivalence-tests/outputs/nested_map_update/state.json:23`
  - _...and 31 more_

- [ ] **#5** `D55D0E...D3C0` — opentofu, terraform (32 files)
  - `reference_architectures/opentofu/testing/equivalence-tests/outputs/nested_map_update/state:7`
  - `reference_architectures/opentofu/testing/equivalence-tests/outputs/nested_map_update/state.json:24`
  - `reference_architectures/opentofu/testing/equivalence-tests/outputs/nested_map_update/plan.json:22`
  - _...and 29 more_

- [ ] **#6** `X25519...M768` — lighthouse (22 files)
  - `reference_architectures/lighthouse/core/test/fixtures/user-flows/artifacts/step0/devtoolslog.json:120`
  - `reference_architectures/lighthouse/core/test/fixtures/user-flows/artifacts/step0/devtoolslog.json:125`
  - `reference_architectures/lighthouse/core/test/fixtures/user-flows/artifacts/step0/devtoolslog.json:153`
  - _...and 19 more_

- [ ] **#7** `boq-la....X.O` — notebooklm-py (21 files)
  - `reference_architectures/notebooklm-py/tests/cassettes/artifacts_export_report.yaml:63`
  - `reference_architectures/notebooklm-py/tests/cassettes/artifacts_delete.yaml:63`
  - `reference_architectures/notebooklm-py/tests/cassettes/artifacts_rename.yaml:63`
  - _...and 18 more_

- [ ] **#8** `SGVsbG...cm0=` — terraform (20 files)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_region_disk_test.go.tmpl:709`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_instance_migrate_test.go.tmpl:481`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_instance_migrate_test.go.tmpl:506`
  - _...and 17 more_

- [ ] **#9** `ieCx/N...MA==` — terraform (11 files)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_region_disk_test.go.tmpl:372`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_disk_test.go.tmpl:1164`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_region_instance_group_manager_test.go.tmpl:524`
  - _...and 8 more_

- [ ] **#10** `efd28c...9c36` — lighthouse-ci (10 files)
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-5-6-0-verge-b.json:549`
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-5-6-0-verge-b.json:984`
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-5-6-0-verge-b.json:2066`
  - _...and 7 more_

- [ ] **#11** `tagKey...7890` — terraform (8 files)
  - `reference_architectures/terraform/cloud-foundation-fabric/tests/modules/project/examples/tags-factory.yaml:28`
  - `reference_architectures/terraform/cloud-foundation-fabric/tests/modules/project/context.yaml:285`
  - `reference_architectures/terraform/cloud-foundation-fabric/tests/modules/project/context.yaml:291`
  - _...and 5 more_

- [ ] **#12** `fB6BS8...Eg==` — terraform (7 files)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_disk_test.go.tmpl:1697`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_image_test.go.tmpl:328`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_image_test.go.tmpl:350`
  - _...and 4 more_

- [ ] **#13** `AQIDBA...EA==` — opentofu (6 files)
  - `reference_architectures/opentofu/internal/encryption/keyprovider/external/testprovider/data/testprovider.sh:20`
  - `reference_architectures/opentofu/internal/encryption/keyprovider/external/testprovider/data/testprovider.sh:33`
  - `reference_architectures/opentofu/internal/encryption/keyprovider/external/testprovider/data/testprovider.sh:34`
  - _...and 3 more_

- [ ] **#14** `H+LmnX...ps0=` — terraform (6 files)
  - `reference_architectures/terraform/cloud-builders/gcs-fetcher/vendor/cloud.google.com/go/storage/storage.replay:8208`
  - `reference_architectures/terraform/cloud-builders/gcs-fetcher/vendor/cloud.google.com/go/storage/storage.replay:8279`
  - `reference_architectures/terraform/cloud-builders/gcs-fetcher/vendor/cloud.google.com/go/storage/storage.replay:8359`
  - _...and 3 more_

- [ ] **#15** `esTuF7...X9E=` — terraform (6 files)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_instance_migrate_test.go.tmpl:507`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_instance_migrate_test.go.tmpl:516`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_instance_migrate_test.go.tmpl:576`
  - _...and 3 more_

- [ ] **#16** `UPdcec...b317` — lighthouse-ci (5 files)
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-5-6-0-verge-b.json:4236`
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-5-6-0-verge-b.json:6420`
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-5-6-0-verge-b.json:6429`
  - _...and 2 more_

- [ ] **#17** `UPb8e1...2947` — lighthouse-ci (5 files)
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-5-6-0-verge-a.json:3930`
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-5-6-0-verge-a.json:6419`
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-5-6-0-verge-a.json:6428`
  - _...and 2 more_

- [ ] **#18** `4Dm1n4...XNk=` — opentofu, terraform (5 files)
  - `reference_architectures/opentofu/internal/backend/remote-state/s3/backend_test.go:1141`
  - `reference_architectures/opentofu/internal/backend/remote-state/s3/backend_test.go:1203`
  - `reference_architectures/terraform/terraform/internal/backend/remote-state/s3/backend_test.go:2529`
  - _...and 2 more_

- [ ] **#19** `AAAAB3...Sw==` — terraform (5 files)
  - `reference_architectures/terraform/90DaysOfDevOps/2022/Days/Configmgmt/ansible-scenario5/facts.json:952`
  - `reference_architectures/terraform/90DaysOfDevOps/2022/es/Days/Configmgmt/ansible-scenario5/facts.json:952`
  - `reference_architectures/terraform/90DaysOfDevOps/2022/ja/Days/Configmgmt/ansible-scenario5/facts.json:952`
  - _...and 2 more_

- [ ] **#20** `AAAAE2...j14=` — terraform (5 files)
  - `reference_architectures/terraform/90DaysOfDevOps/2022/Days/Configmgmt/ansible-scenario5/facts.json:954`
  - `reference_architectures/terraform/90DaysOfDevOps/2022/es/Days/Configmgmt/ansible-scenario5/facts.json:954`
  - `reference_architectures/terraform/90DaysOfDevOps/2022/ja/Days/Configmgmt/ansible-scenario5/facts.json:954`
  - _...and 2 more_

- [ ] **#21** `AAAAC3...wPar` — terraform (5 files)
  - `reference_architectures/terraform/90DaysOfDevOps/2022/Days/Configmgmt/ansible-scenario5/facts.json:956`
  - `reference_architectures/terraform/90DaysOfDevOps/2022/es/Days/Configmgmt/ansible-scenario5/facts.json:956`
  - `reference_architectures/terraform/90DaysOfDevOps/2022/ja/Days/Configmgmt/ansible-scenario5/facts.json:956`
  - _...and 2 more_

- [ ] **#22** `AAAAB3...jBk=` — terraform (5 files)
  - `reference_architectures/terraform/90DaysOfDevOps/2022/Days/Configmgmt/ansible-scenario5/facts.json:958`
  - `reference_architectures/terraform/90DaysOfDevOps/2022/es/Days/Configmgmt/ansible-scenario5/facts.json:958`
  - `reference_architectures/terraform/90DaysOfDevOps/2022/ja/Days/Configmgmt/ansible-scenario5/facts.json:958`
  - _...and 2 more_

- [ ] **#23** `5a7d70...23f8` — terraform (5 files)
  - `reference_architectures/terraform/90DaysOfDevOps/2022/Days/Kubernetes/configs/join.sh:1`
  - `reference_architectures/terraform/90DaysOfDevOps/2022/es/Days/Kubernetes/configs/join.sh:1`
  - `reference_architectures/terraform/90DaysOfDevOps/2022/ja/Days/Kubernetes/configs/join.sh:1`
  - _...and 2 more_

- [ ] **#24** `ZS2uEV...KQ==` — terraform (5 files)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/microsoft_calendar/tests/test_microsoft_event.py:354`
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/microsoft_calendar/tests/test_sync_microsoft2odoo.py:73`
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/microsoft_calendar/tests/test_sync_microsoft2odoo.py:89`
  - _...and 2 more_

- [ ] **#25** `0836c6...b08e` — terraform (5 files)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/datalossprevention/resource_data_loss_prevention_deidentify_template_test.go:1989`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/datalossprevention/resource_data_loss_prevention_deidentify_template_test.go:3487`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/datalossprevention/resource_data_loss_prevention_deidentify_template_test.go:4236`
  - _...and 2 more_

- [ ] **#26** `=CT70a...mdka` — opentofu, terraform (4 files)
  - `reference_architectures/opentofu/internal/backend/remote-state/s3/backend_test.go:1137`
  - `reference_architectures/opentofu/internal/backend/remote-state/s3/backend_test.go:1199`
  - `reference_architectures/terraform/terraform/internal/backend/remote-state/s3/backend_test.go:2547`
  - _...and 1 more_

- [ ] **#27** `DJFdtA...Uqow` — terraform (4 files)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/test_mail_full/tests/test_web_push.py:66`
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/test_mail_full/tests/test_web_push.py:76`
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/test_mail_full/tests/test_web_push.py:265`
  - _...and 1 more_

- [ ] **#28** `UP692c...bdab` — lighthouse-ci (3 files)
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-7-0-0-coursehero-a.json:2814`
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-7-0-0-coursehero-perf-a.json:2613`
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-7-0-0-coursehero-a.json:9720`

- [ ] **#29** `QUNDRV...WQ0K` — opentofu, terraform (3 files)
  - `reference_architectures/opentofu/internal/backend/remote-state/azure/backend_test.go:43`
  - `reference_architectures/opentofu/internal/backend/remote-state/azure/backend_test.go:66`
  - `reference_architectures/terraform/terraform/internal/backend/remote-state/azure/backend_test.go:29`

- [ ] **#30** `double..._col` — terraform (3 files)
  - `reference_architectures/terraform/DataflowTemplates/v2/datastream-to-spanner/src/test/resources/MySQLDataTypesIT/mysql-data-types.sql:286`
  - `reference_architectures/terraform/DataflowTemplates/v2/sourcedb-to-spanner/src/test/resources/DataTypesIT/mysql-data-types.sql:298`
  - `reference_architectures/terraform/DataflowTemplates/v2/spanner-to-sourcedb/src/test/resources/SpannerToMySqlDataTypesIT/mysql-schema.sql:286`

- [ ] **#31** `6Lf9Yn...4YzX` — terraform (3 files)
  - `reference_architectures/terraform/magic-modules/mmv1/products/firebaseappcheck/RecaptchaV3Config.yaml:50`
  - `reference_architectures/terraform/magic-modules/mmv1/products/firebaseappcheck/RecaptchaV3Config.yaml:55`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/firebaseappcheck/resource_firebase_app_check_recaptcha_v3_config_test.go.tmpl:20`

- [ ] **#32** `ZW5jcn...Cg==` — terraform (3 files)
  - `reference_architectures/terraform/magic-modules/mmv1/templates/terraform/examples/cloudbuild_trigger_allow_exit_codes.tf.tmpl:33`
  - `reference_architectures/terraform/magic-modules/mmv1/templates/terraform/examples/cloudbuild_trigger_allow_failure.tf.tmpl:33`
  - `reference_architectures/terraform/magic-modules/mmv1/templates/terraform/examples/cloudbuild_trigger_build.tf.tmpl:39`

- [ ] **#33** `second...9012` — terraform (3 files)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_instance_test.go.tmpl:821`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_instance_test.go.tmpl:8075`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_instance_test.go.tmpl:8092`

- [ ] **#34** `VVdWVW...dz09` — terraform (3 files)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/datalossprevention/resource_data_loss_prevention_deidentify_template_test.go:148`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/datalossprevention/resource_data_loss_prevention_deidentify_template_test.go:240`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/datalossprevention/resource_data_loss_prevention_deidentify_template_test.go:1308`

- [ ] **#35** `UWVUaF...Qw==` — terraform (3 files)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/datalossprevention/resource_data_loss_prevention_deidentify_template_test.go:148`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/datalossprevention/resource_data_loss_prevention_deidentify_template_test.go:240`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/datalossprevention/resource_data_loss_prevention_deidentify_template_test.go:1308`

- [ ] **#36** `UPbe0d...38fb` — lighthouse-ci (2 files)
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-7-0-0-coursehero-b.json:2935`
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-7-0-0-coursehero-b.json:9684`

- [ ] **#37** `UPe6d0...0545` — lighthouse-ci (2 files)
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-6-0-0-coursehero-a.json:3013`
  - `reference_architectures/lighthouse-ci/packages/utils/src/seed-data/sample-report.json:3013`

- [ ] **#38** `yRyCOi...oVk=` — opentofu, terraform (2 files)
  - `reference_architectures/opentofu/internal/backend/remote-state/gcs/backend_test.go:37`
  - `reference_architectures/terraform/terraform/internal/backend/remote-state/gcs/backend_test.go:33`

- [ ] **#39** `e2bfb7...c4c0` — opentofu, terraform (2 files)
  - `reference_architectures/opentofu/internal/legacy/helper/schema/resource_timeout.go:18`
  - `reference_architectures/terraform/terraform/internal/legacy/helper/schema/resource_timeout.go:16`

- [ ] **#40** `ur6xT-...d44J` — terraform (2 files)
  - `reference_architectures/terraform/90DaysOfDevOps/2023/day58.md:216`
  - `reference_architectures/terraform/90DaysOfDevOps/2023/day58.md:286`

- [ ] **#41** `ZHJhZ2...Cg==` — terraform (2 files)
  - `reference_architectures/terraform/click-to-deploy/docker/dragonfly/2/debian11/2.1/dragonfly-manager2/config/manager.yaml:28`
  - `reference_architectures/terraform/click-to-deploy/docker/dragonfly/templates/dragonfly-manager2/config/manager.yaml:28`

- [ ] **#42** `3AD1LU...aoog` — terraform (2 files)
  - `reference_architectures/terraform/click-to-deploy/docker/hydra/README.md:76`
  - `reference_architectures/terraform/click-to-deploy/docker/hydra/tests/functional_tests/functional_test.yaml:58`

- [ ] **#43** `177F40...D1D8` — terraform (2 files)
  - `reference_architectures/terraform/click-to-deploy/docker/mariadb/10/debian12/10.11/Dockerfile:57`
  - `reference_architectures/terraform/click-to-deploy/docker/mariadb/11/debian12/11.5/Dockerfile:57`

- [ ] **#44** `50E3EE...F6EC` — terraform (2 files)
  - `reference_architectures/terraform/click-to-deploy/docker/solr/9/debian12/9.6/Dockerfile:23`
  - `reference_architectures/terraform/click-to-deploy/docker/solr/9/debian12/9.8/Dockerfile:23`

- [ ] **#45** `51379D...9B6E` — terraform (2 files)
  - `reference_architectures/terraform/click-to-deploy/docker/storm/2/debian11/2.4/Dockerfile:46`
  - `reference_architectures/terraform/click-to-deploy/docker/storm/templates/Dockerfile.template:49`

- [ ] **#46** `ZS2uEV...PA==` — terraform (2 files)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/microsoft_calendar/tests/test_sync_microsoft2odoo.py:123`
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/microsoft_calendar/tests/test_sync_microsoft2odoo.py:125`

- [ ] **#47** `ZS2uEV...kw==` — terraform (2 files)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/microsoft_calendar/tests/test_sync_microsoft2odoo.py:203`
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/microsoft_calendar/tests/test_sync_microsoft2odoo.py:206`

- [ ] **#48** `pynKRn...Uw==` — terraform (2 files)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/microsoft_calendar/tests/test_sync_microsoft2odoo.py:278`
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/microsoft_calendar/tests/test_sync_microsoft2odoo.py:280`

- [ ] **#49** `f9d2ff...dc20` — terraform (2 files)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/website_crm/tests/test_crm_lead_merge.py:26`
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/website_event_crm/tests/test_visitor_propagation.py:26`

- [ ] **#50** `ChBvYm...aGVz` — terraform (2 files)
  - `reference_architectures/terraform/cloud-builders/gcs-fetcher/vendor/cloud.google.com/go/storage/storage.replay:2340`
  - `reference_architectures/terraform/cloud-builders/gcs-fetcher/vendor/cloud.google.com/go/storage/storage.replay:2535`

- [ ] **#51** `6LdpMX...ytuw` — terraform (2 files)
  - `reference_architectures/terraform/magic-modules/mmv1/products/firebaseappcheck/RecaptchaEnterpriseConfig.yaml:47`
  - `reference_architectures/terraform/magic-modules/mmv1/products/firebaseappcheck/RecaptchaEnterpriseConfig.yaml:52`

- [ ] **#52** `4A67F2...23DF` — terraform (2 files)
  - `reference_architectures/terraform/magic-modules/mmv1/templates/terraform/examples/transcoder_job_template_encryptions.tf.tmpl:10`
  - `reference_architectures/terraform/magic-modules/mmv1/templates/terraform/examples/transcoder_job_encryptions.tf.tmpl:28`

- [ ] **#53** `Ym9vdD...MTI=` — terraform (2 files)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_instance_test.go.tmpl:817`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_instance_test.go.tmpl:856`

- [ ] **#54** `c2Vjb2...wMTI` — terraform (2 files)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_instance_test.go.tmpl:8075`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_instance_test.go.tmpl:8092`

- [ ] **#55** `dmPoli...bled` — libs/cyberpunk_stack (2 files)
  - `libs/cyberpunk_stack/openclaw/dist/access-control-DqrdUO7B.js:92`
  - `libs/cyberpunk_stack/openclaw/dist/src-Ba-Tb42Y.js:1536`

- [ ] **#56** `do_hsv...lice` — FFmpeg (1 file)
  - `reference_architectures/FFmpeg/libavfilter/vf_hsvkey.c:237`

- [ ] **#57** `gnutls...rt_t` — FFmpeg (1 file)
  - `reference_architectures/FFmpeg/libavformat/tls_gnutls.c:215`

- [ ] **#58** `defaul..._20x` — claude-code-src (1 file)
  - `reference_architectures/claude-code-src/src/commands/upgrade/upgrade.tsx:16`

- [ ] **#59** `pubbbf...99bf` — claude-code-src (1 file)
  - `reference_architectures/claude-code-src/src/services/analytics/datadog.ts:14`

- [ ] **#60** `5ee8bf...85de` — flagger (1 file)
  - `reference_architectures/flagger/.github/workflows/scan.yml:25`

- [ ] **#61** `e.defa...void` — lighthouse (1 file)
  - `reference_architectures/lighthouse/core/test/fixtures/source-maps/coursehero-bundle-2.js:1`

- [ ] **#62** `A3dHTS...dWV9` — lighthouse (1 file)
  - `reference_architectures/lighthouse/cli/test/fixtures/unused-javascript.js:9`

- [ ] **#63** `UP9d9e...58ef` — lighthouse-ci (1 file)
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-6-2-0-coursehero-b.json:2908`

- [ ] **#64** `UP9da4...54c9` — lighthouse-ci (1 file)
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-6-2-0-coursehero-b.json:2918`

- [ ] **#65** `UP8cd7...3cad` — lighthouse-ci (1 file)
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-6-2-0-coursehero-a.json:2903`

- [ ] **#66** `905663...Fha0` — lighthouse (1 file)
  - `reference_architectures/lighthouse/core/test/fixtures/artifacts/redirect/devtoolslog.json:546`

- [ ] **#67** `boq-la....X.O` — notebooklm-py (1 file)
  - `reference_architectures/notebooklm-py/tests/cassettes/sources_add_drive.yaml:63`

- [ ] **#68** `6d2993...8c49` — obsidian-excalidraw-plugin (1 file)
  - `reference_architectures/obsidian-excalidraw-plugin/src/utils/fileUtils.ts:187`

- [ ] **#69** `1hwbcN...75o=` — opentofu (1 file)
  - `reference_architectures/opentofu/internal/backend/remote-state/s3/backend_test.go:872`

- [ ] **#70** `YW1iaW...b3Jk` — opentofu (1 file)
  - `reference_architectures/opentofu/internal/command/cliconfig/testdata/oci-credentials-policy/mixed-darwin/home/.config/containers/auth.json:5`

- [ ] **#71** `YW1iaW...cmQ=` — opentofu (1 file)
  - `reference_architectures/opentofu/internal/command/cliconfig/testdata/oci-credentials-policy/mixed-darwin/home/.config/containers/auth.json:8`

- [ ] **#72** `8f6fb3...8257` — opentofu (1 file)
  - `reference_architectures/opentofu/internal/command/jsonformat/plan_test.go:1843`

- [ ] **#73** `f8b902...b274` — opentofu (1 file)
  - `reference_architectures/opentofu/internal/command/jsonformat/plan_test.go:1847`

- [ ] **#74** `1234ab...90ab` — opentofu (1 file)
  - `reference_architectures/opentofu/internal/encryption/keyprovider/aws_kms/README.md:25`

- [ ] **#75** `h4a_i4...vfs=` — semaphore (1 file)
  - `reference_architectures/semaphore/.dredd/hooks/main.go:12`

- [ ] **#76** `kwofd6...yhu=` — semaphore (1 file)
  - `reference_architectures/semaphore/.dredd/hooks/main.go:13`

- [ ] **#77** `RAX6yK...RPls` — semaphore (1 file)
  - `reference_architectures/semaphore/api/projects/projects.go:92`

- [ ] **#78** `hHYgPr...DmM=` — semaphore (1 file)
  - `reference_architectures/semaphore/services/server/AccessKey_test.go:83`

- [ ] **#79** `1/wRYX...Vos=` — semaphore (1 file)
  - `reference_architectures/semaphore/util/config_test.go:303`

- [ ] **#80** `hvs.p1...SjDu` — terraform (1 file)
  - `reference_architectures/terraform/90DaysOfDevOps/2023/day39/cluster-keys.json:14`

- [ ] **#81** `col_qc...ttvY` — terraform (1 file)
  - `reference_architectures/terraform/DataflowTemplates/v2/sourcedb-to-spanner/src/test/resources/WideRow/RowMaxSizeLimit/mysql-schema.sql:2`

- [ ] **#82** `col_qc...16ed` — terraform (1 file)
  - `reference_architectures/terraform/DataflowTemplates/v2/spanner-to-sourcedb/src/test/resources/SpannerToCassandraSourceIT/cassandra-schema.sql:221`

- [ ] **#83** `test-a...2345` — terraform (1 file)
  - `reference_architectures/terraform/agent-starter-pack/tests/cli/commands/test_create_local.py:274`

- [ ] **#84** `ZaJdUU...kcQ=` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/docker/conjur/tests/functional_tests/running_test.yaml:43`

- [ ] **#85** `E05FDF...2455` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/docker/solr/9/debian11/9.5/Dockerfile:23`

- [ ] **#86** `Lb3qA1...POYP` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/docker/superset/tests/functional_tests/running_test.yaml:43`

- [ ] **#87** `209c61...e634` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/chef/cookbooks/alfresco/templates/default/alfresco-global.properties.template.erb:52`

- [ ] **#88** `rHdWcU...aXjH` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/base/tests/test_mail_examples.py:245`

- [ ] **#89** `1ashiq...n197` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/l10n_eg_edi_eta/tests/common.py:29`

- [ ] **#90** `self.l...ency` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/l10n_es_edi_tbai/models/res_company.py:92`

- [ ] **#91** `Xlj15L...fSs=` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/l10n_sa_edi/models/account_journal.py:40`

- [ ] **#92** `dBwSQ1...GcQ=` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/l10n_sa_edi/models/account_journal.py:615`

- [ ] **#93** `f9YRho...4qw=` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/l10n_sa_edi/models/account_journal.py:616`

- [ ] **#94** `MIID1D...SpG1` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/l10n_sa_edi/models/account_journal.py:39`

- [ ] **#95** `MIID2z...JA==` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/l10n_sa_edi/models/account_journal.py:616`

- [ ] **#96** `ZS2uEV...xQ==` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/microsoft_calendar/tests/test_sync_microsoft2odoo.py:22`

- [ ] **#97** `ZS2uEV...nw==` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/microsoft_calendar/tests/test_sync_microsoft2odoo.py:150`

- [ ] **#98** `ZS2uEV...pg==` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/microsoft_calendar/tests/test_sync_microsoft2odoo.py:169`

- [ ] **#99** `ZS2uEV...qg==` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/microsoft_calendar/tests/test_sync_microsoft2odoo.py:181`

- [ ] **#100** `ZS2uEV...ig==` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/microsoft_calendar/tests/test_sync_microsoft2odoo.py:202`

- [ ] **#101** `pynKRn...NQ==` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/microsoft_calendar/tests/test_sync_microsoft2odoo.py:272`

- [ ] **#102** `123abc...f789` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/payment_aps/tests/common.py:42`

- [ ] **#103** `FLWSEC...56-X` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/payment_flutterwave/tests/common.py:14`

- [ ] **#104** `flw-t1...m03k` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/payment_flutterwave/tests/common.py:37`

- [ ] **#105** `pk_tes...4S6J` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/payment_stripe/tests/common.py:14`

- [ ] **#106** `whsec_...BLxB` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/payment_stripe/tests/common.py:15`

- [ ] **#107** `pi_123...6789` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/payment_stripe/tests/test_stripe.py:20`

- [ ] **#108** `4ead4b...aaac` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/survey/tests/test_survey_ui_certification.py:16`

- [ ] **#109** `b13764...aafe` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/survey/tests/test_survey_ui_session.py:39`

- [ ] **#110** `3cfadc...9527` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/survey/tests/test_survey_ui_feedback.py:178`

- [ ] **#111** `1cb935...b4dc` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/survey/tests/test_survey_ui_feedback.py:236`

- [ ] **#112** `853ebb...a365` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/survey/tests/test_survey_ui_feedback.py:300`

- [ ] **#113** `5632a4...f50b` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/test_website_slides_full/tests/test_ui_wslides.py:68`

- [ ] **#114** `ZnJlZG...cg==` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/test_mail/data/test_mail_data.py:1212`

- [ ] **#115** `m2oPro...tion` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/web/static/src/views/fields/reference/reference_field.xml:19`

- [ ] **#116** `f9d2b1...62ed` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/website/tests/test_website_visitor.py:294`

- [ ] **#117** `f9d2d2...2f47` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/website/tests/test_website_visitor.py:300`

- [ ] **#118** `f9d2c3...e678` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/website_crm/tests/test_crm_lead_merge.py:30`

- [ ] **#119** `f9d2c6...fcb6` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/website_crm/tests/test_website_visitor.py:27`

- [ ] **#120** `f9d28a...aa00` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/website_crm/tests/test_website_visitor.py:81`

- [ ] **#121** `f9d2b9...5a6c` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/website_event_track/tests/test_website_visitor.py:28`

- [ ] **#122** `f9d2e7...9a19` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/website_livechat/tests/test_ui.py:14`

- [ ] **#123** `Tm9ib2...IQ==` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/website_sale_autocomplete/tests/test_ui.py:8`

- [ ] **#124** `MWYyZD...N2Rm` — terraform (1 file)
  - `reference_architectures/terraform/cloud-builders/gke-deploy/test/configs-all/secret.yaml:8`

- [ ] **#125** `api-cf...c223` — terraform (1 file)
  - `reference_architectures/terraform/cloud-foundation-fabric/tests/modules/api_gateway/examples/existing-sa.yaml:32`

- [ ] **#126** `ZmssLN...ejr2` — terraform (1 file)
  - `reference_architectures/terraform/cloud-run-mcp/.env.gcloud-sdk-oauth:6`

- [ ] **#127** `6da6e0...af5b` — terraform (1 file)
  - `reference_architectures/terraform/firebase-extensions/_emulator/.firebaserc:40`

- [ ] **#128** `5f5976...098c` — terraform (1 file)
  - `reference_architectures/terraform/firebase-extensions/_emulator/.firebaserc:70`

- [ ] **#129** `db069a...e530` — terraform (1 file)
  - `reference_architectures/terraform/firebase-extensions/_emulator/.firebaserc:75`

- [ ] **#130** `2e4117...2fd5` — terraform (1 file)
  - `reference_architectures/terraform/firebase-extensions/_emulator/.firebaserc:87`

- [ ] **#131** `af2bfd...f328` — terraform (1 file)
  - `reference_architectures/terraform/firebase-extensions/_emulator/.firebaserc:88`

- [ ] **#132** `serial...pb=b` — terraform (1 file)
  - `reference_architectures/terraform/gcsfuse/perfmetrics/scripts/ls_metrics/directory_pb2.py:21`

- [ ] **#133** `FnBvfQ...GrQ=` — terraform (1 file)
  - `reference_architectures/terraform/cloud-builders/gcs-fetcher/vendor/cloud.google.com/go/storage/storage.replay:9087`

- [ ] **#134** `5f3ae8...9d2a` — terraform (1 file)
  - `reference_architectures/terraform/genai-factory/gecx-dialogflow/1-apps/data/agents/default/flows/Set Current Date/Set Current Date.json:45`

- [ ] **#135** `292885...b938` — terraform (1 file)
  - `reference_architectures/terraform/genai-factory/gecx-dialogflow/1-apps/data/agents/default/flows/Default Start Flow/Default Start Flow.json:89`

- [ ] **#136** `5E7283...BB98` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/products/firebaseappcheck/DebugToken.yaml:52`

- [ ] **#137** `eyJhbG...VCJ9` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/templates/terraform/examples/integrations_auth_config_auth_token.tf.tmpl:9`

- [ ] **#138** `D-XXFD...wliJ` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/templates/terraform/examples/integrations_auth_config_oauth2_authorization_code.tf.tmpl:9`

- [ ] **#139** `MJlO3b...9jk1` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/templates/terraform/examples/integrations_auth_config_oauth2_client_credentials.tf.tmpl:9`

- [ ] **#140** `bgpPee...Ipv4` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_router_peer_meta.yaml.tmpl:35`

- [ ] **#141** `bgpPee...Ipv6` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_router_peer_meta.yaml.tmpl:37`

- [ ] **#142** `c4afb1...a4b9` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_backend_service_test.go.tmpl:2592`

- [ ] **#143** `c2Vjb2...MTI=` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_instance_test.go.tmpl:821`

- [ ] **#144** `dGhpcm...MTI=` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_instance_test.go.tmpl:825`

- [ ] **#145** `third6...9012` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/resource_compute_instance_test.go.tmpl:825`

- [ ] **#146** `7Lf9Yn...4YzX` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/firebaseappcheck/resource_firebase_app_check_recaptcha_v3_config_test.go.tmpl:27`

- [ ] **#147** `KEY_AL...1024` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/resourcemanager/resource_google_service_account_key.go:36`

- [ ] **#148** `KEY_AL...2048` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/resourcemanager/resource_google_service_account_key.go:37`

- [ ] **#149** `qI6+xv...Do4=` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/storage/resource_storage_bucket_object_test.go:357`

- [ ] **#150** `variab...key1` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/website/docs/d/compute_instance_guest_attributes.html.markdown:34`

- [ ] **#151** `Io4lnO...fDc=` — terraform (1 file)
  - `reference_architectures/terraform/cloud-builders/gcs-fetcher/vendor/cloud.google.com/go/storage/storage.replay:25213`

- [ ] **#152** `cRKXxV...Qls=` — terraform (1 file)
  - `reference_architectures/terraform/terraform/internal/backend/remote-state/gcs/backend_test.go:34`

- [ ] **#153** `API-CK...TXUO` — terraform (1 file)
  - `reference_architectures/terraform/terraformer/docs/octopus.md:7`

- [ ] **#154** `sk-pro...l012` — labs (1 file)
  - `labs/claude_code_ingest/hermes-agent/tests/agent/__pycache__/test_redact.cpython-314.pyc:11`

- [ ] **#155** `sk-pro...o345` — labs (1 file)
  - `labs/claude_code_ingest/hermes-agent/tests/agent/__pycache__/test_redact.cpython-314.pyc:22`

- [ ] **#156** `fc-sho...9012` — labs (1 file)
  - `labs/claude_code_ingest/hermes-agent/tests/agent/__pycache__/test_redact.cpython-314.pyc:24`

- [ ] **#157** `sk-tes...7890` — labs (1 file)
  - `labs/claude_code_ingest/hermes-agent/tests/agent/__pycache__/test_redact.cpython-314.pyc:27`

- [ ] **#158** `ghp_ab...9jkl` — labs (1 file)
  - `labs/claude_code_ingest/hermes-agent/tests/agent/__pycache__/test_redact.cpython-314.pyc:27`

- [ ] **#159** `sk_abc...rstu` — labs (1 file)
  - `labs/claude_code_ingest/hermes-agent/tests/agent/__pycache__/test_redact.cpython-314.pyc:31`

- [ ] **#160** `tvly-A...0000` — labs (1 file)
  - `labs/claude_code_ingest/hermes-agent/tests/agent/__pycache__/test_redact.cpython-314.pyc:32`

- [ ] **#161** `valFIR...val2` — labs (1 file)
  - `labs/claude_code_ingest/hermes-agent/tests/hermes_cli/__pycache__/test_config.cpython-314.pyc:95`

- [ ] **#162** `YmVuY2...NA==` — labs (1 file)
  - `labs/uphillsnowball/external_payloads/repos/uvicorn/tests/benchmarks/__pycache__/ws.cpython-314.pyc:9`

---

## hashicorp-tf-password (3 unique / 12 occurrences) — 🟢 LOW

- [ ] **#1** `"pa...rd"` — terraform (10 files)
  - `reference_architectures/terraform/DataflowTemplates/v2/spanner-to-sourcedb/terraform/samples/spanner-to-cassandra/variables.tf:85`
  - `reference_architectures/terraform/runbooks-infrastructure-live-example/prod/us-east-1/stateful-ec2-asg-service/terragrunt.stack.hcl:7`
  - `reference_architectures/terraform/runbooks-infrastructure-live-example/non-prod/us-east-1/stateful-ec2-asg-service/terragrunt.stack.hcl:7`
  - _...and 7 more_

- [ ] **#2** `"alloy...ter"` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/tgc/tests/data/example_alloydb_instance.tf:23`

- [ ] **#3** `"test-...ord"` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/tgc/tests/data/full_sql_database_instance.tf:48`

---

## jwt (10 unique / 18 occurrences) — 🟡 MEDIUM

- [ ] **#1** `eyJhbG...WCBA` — terraform (5 files)
  - `reference_architectures/terraform/90DaysOfDevOps/2022/Days/Kubernetes/configs/token:1`
  - `reference_architectures/terraform/90DaysOfDevOps/2022/es/Days/Kubernetes/configs/token:1`
  - `reference_architectures/terraform/90DaysOfDevOps/2022/ja/Days/Kubernetes/configs/token:1`
  - _...and 2 more_

- [ ] **#2** `eyJhbG...G9ij` — lighthouse (3 files)
  - `reference_architectures/lighthouse/core/test/fixtures/artifacts/paul/devtoolslog.json:188`
  - `reference_architectures/lighthouse/core/test/fixtures/artifacts/paul/devtoolslog.json:194`
  - `reference_architectures/lighthouse/core/test/fixtures/artifacts/paul/devtoolslog.json:188`

- [ ] **#3** `eyJhbG...WYLw` — lighthouse-ci (2 files)
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-5-6-0-verge-b.json:6210`
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-5-6-0-verge-b.json:14751`

- [ ] **#4** `eyJhbG...BmcQ` — lighthouse-ci (2 files)
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-5-6-0-verge-a.json:6247`
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-5-6-0-verge-a.json:15020`

- [ ] **#5** `eyJhbG...zH5\` — lighthouse (1 file)
  - `reference_architectures/lighthouse/core/test/fixtures/traces/lcp-m78.devtools.log.json:1`

- [ ] **#6** `eyJhbG...9ij\` — lighthouse (1 file)
  - `reference_architectures/lighthouse/core/test/fixtures/artifacts/paul/devtoolslog.json:188`

- [ ] **#7** `eyJhbG...Fl2g` — lighthouse-ci (1 file)
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-5-6-0-verge-b.json:5317`

- [ ] **#8** `eyJhbG...HjZg` — lighthouse-ci (1 file)
  - `reference_architectures/lighthouse-ci/packages/server/test/fixtures/lh-5-6-0-verge-a.json:4771`

- [ ] **#9** `eyJhbG...sw5c` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/provider/provider_internal_test.go:96`

- [ ] **#10** `eyJhbG...ture` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/provider/provider_internal_test.go:105`

---

## kubernetes-secret-yaml (4 unique / 4 occurrences) — 🟢 LOW

- [ ] **#1** `redisU...MzA=` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/k8s/harbor/chart/harbor/templates/trivy/trivy-secret.yaml:2`

- [ ] **#2** `kind: ...ount` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/k8s/sonarqube/chart/sonarqube/templates/sonarqube-secret.yaml:2`

- [ ] **#3** `passwo...N2Rm` — terraform (1 file)
  - `reference_architectures/terraform/cloud-builders/gke-deploy/test/configs-all/secret.yaml:2`

- [ ] **#4** `passwo...67df` — terraform (1 file)
  - `reference_architectures/terraform/cloud-builders/gke-deploy/test/configs-all/secret.yaml:2`

---

## octopus-deploy-api-key (1 unique / 2 occurrences) — 🟢 LOW

- [ ] **#1** `API-YV...KPWQ` — terraform (2 files)
  - `reference_architectures/terraform/terraformer/tests/octopusdeploy/provider.tf:3`
  - `reference_architectures/terraform/terraformer/tests/octopusdeploy/README.md:39`

---

## pkcs12-file (1 unique / 9 occurrences) — 🟢 LOW

- [ ] **#1** `***` — terraform (9 files)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/l10n_es_edi_facturae/demo/certificate_demo.pfx:0`
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/l10n_es_edi_facturae/tests/data/certificate_test.pfx:0`
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/l10n_es_edi_sii/demo/certificates/sello_entidad_act.p12:0`
  - _...and 6 more_

---

## private-key (30 unique / 54 occurrences) — 🟡 MEDIUM

- [ ] **#1** `-----B...----` — terraform (5 files)
  - `reference_architectures/terraform/90DaysOfDevOps/2022/Days/Kubernetes/configs/config:19`
  - `reference_architectures/terraform/90DaysOfDevOps/2022/es/Days/Kubernetes/configs/config:19`
  - `reference_architectures/terraform/90DaysOfDevOps/2022/ja/Days/Kubernetes/configs/config:19`
  - _...and 2 more_

- [ ] **#2** `-----B...----` — terraform (5 files)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/certificatemanager/test-fixtures/private-key.pem:1`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/test-fixtures/private-key.pem:1`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/datastream/text-fixtures/private-key.pem:1`
  - _...and 2 more_

- [ ] **#3** `-----B...----` — opentofu, terraform (4 files)
  - `reference_architectures/opentofu/internal/lang/funcs/crypto_test.go:689`
  - `reference_architectures/opentofu/internal/lang/functions_test.go:1368`
  - `reference_architectures/terraform/terraform/internal/lang/functions_test.go:1416`
  - _...and 1 more_

- [ ] **#4** `-----B...----` — opentofu, terraform (2 files)
  - `reference_architectures/opentofu/internal/backend/remote-state/http/testdata/certs/client.key:1`
  - `reference_architectures/terraform/terraform/internal/backend/remote-state/http/testdata/certs/client.key:1`

- [ ] **#5** `-----B...----` — opentofu, terraform (2 files)
  - `reference_architectures/opentofu/internal/backend/remote-state/http/testdata/certs/ca.key:1`
  - `reference_architectures/terraform/terraform/internal/backend/remote-state/http/testdata/certs/ca.key:1`

- [ ] **#6** `-----B...----` — opentofu, terraform (2 files)
  - `reference_architectures/opentofu/internal/backend/remote-state/http/testdata/certs/server.key:1`
  - `reference_architectures/terraform/terraform/internal/backend/remote-state/http/testdata/certs/server.key:1`

- [ ] **#7** `-----B...----` — opentofu, terraform (2 files)
  - `reference_architectures/opentofu/internal/communicator/ssh/communicator_test.go:34`
  - `reference_architectures/terraform/terraform/internal/communicator/ssh/communicator_test.go:33`

- [ ] **#8** `-----B...----` — opentofu, terraform (2 files)
  - `reference_architectures/opentofu/internal/communicator/ssh/communicator_test.go:554`
  - `reference_architectures/terraform/terraform/internal/communicator/ssh/communicator_test.go:477`

- [ ] **#9** `-----B...----` — opentofu, terraform (2 files)
  - `reference_architectures/opentofu/internal/communicator/ssh/communicator_test.go:583`
  - `reference_architectures/terraform/terraform/internal/communicator/ssh/communicator_test.go:506`

- [ ] **#10** `-----B...----` — opentofu, terraform (2 files)
  - `reference_architectures/opentofu/internal/lang/funcs/crypto_test.go:718`
  - `reference_architectures/terraform/terraform/internal/lang/funcs/crypto_test.go:716`

- [ ] **#11** `-----B...----` — opentofu, terraform (2 files)
  - `reference_architectures/opentofu/internal/lang/funcs/crypto_test.go:747`
  - `reference_architectures/terraform/terraform/internal/lang/funcs/crypto_test.go:745`

- [ ] **#12** `-----B...----` — opentofu, terraform (2 files)
  - `reference_architectures/opentofu/internal/lang/funcs/crypto_test.go:776`
  - `reference_architectures/terraform/terraform/internal/lang/funcs/crypto_test.go:774`

- [ ] **#13** `-----B...----` — terraform (2 files)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/account_peppol/tests/assets/private_key.pem:1`
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/account_peppol/tools/private_key.pem:1`

- [ ] **#14** `-----B...----` — terraform (2 files)
  - `reference_architectures/terraform/magic-modules/mmv1/templates/terraform/examples/integrations_auth_config_client_certificate_only.tf.tmpl:27`
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/integrations/resource_integrations_auth_config_test.go:107`

- [ ] **#15** `-----B...----` — terraform (2 files)
  - `reference_architectures/terraform/terraform/internal/pluginshared/testdata/sample.private.key:1`
  - `reference_architectures/terraform/terraform/internal/releaseauth/testdata/sample.private.key:1`

- [ ] **#16** `-----B...----` — terraform (2 files)
  - `reference_architectures/terraform/terragrunt/test/fixtures/sops/test_pgp_key.asc:1`
  - `reference_architectures/terraform/terragrunt/test/fixtures/units-reading/test_pgp_key.asc:1`

- [ ] **#17** `-----B...----` — terraform (1 file)
  - `reference_architectures/terraform/DataflowTemplates/v1/src/test/resources/PubsubToSplunkTestData/PrivateKey.pem:1`

- [ ] **#18** `-----B...----` — terraform (1 file)
  - `reference_architectures/terraform/DataflowTemplates/v1/src/test/resources/PubsubToSplunkTestData/RootCA_PrivateKey.pem:1`

- [ ] **#19** `-----B...----` — terraform (1 file)
  - `reference_architectures/terraform/cli/crates/google-workspace-cli/src/auth.rs:581`

- [ ] **#20** `-----B...----` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/point_of_sale/tools/posbox/overwrite_after_init/etc/ssl/private/nginx-cert.key:1`

- [ ] **#21** `-----B...----` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/products/chronicle/Feed.yaml:1039`

- [ ] **#22** `-----B...----` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/apigee/test-fixtures/apigee_keystore_alias_test_key.pem:1`

- [ ] **#23** `-----B...----` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/ces/test-fixtures/test.key:1`

- [ ] **#24** `-----B...----` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/compute/test-fixtures/test.key:1`

- [ ] **#25** `-----B...----` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/datastream/resource_datastream_connection_profile_test.go:90`

- [ ] **#26** `-----B...----` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/datastream/resource_datastream_connection_profile_test.go:119`

- [ ] **#27** `-----B...----` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/firebaseappcheck/test-fixtures/private-key.p8:1`

- [ ] **#28** `-----B...----` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/firebaseappcheck/test-fixtures/private-key-2.p8:1`

- [ ] **#29** `-----B...----` — terraform (1 file)
  - `reference_architectures/terraform/magic-modules/mmv1/third_party/terraform/services/storage/data_source_storage_object_signed_url_internal_test.go:17`

- [ ] **#30** `-----B...----` — terraform (1 file)
  - `reference_architectures/terraform/terragrunt/internal/gcphelper/config_test.go:60`

---

## stripe-access-token (1 unique / 1 occurrences) — 🔴 HIGH

- [ ] **#1** `sk_tes...O5E8` — terraform (1 file)
  - `reference_architectures/terraform/click-to-deploy/vm/test/usr/lib/python3/dist-packages/odoo/addons/payment_stripe/tests/common.py:13`

---

## vault-service-token (1 unique / 1 occurrences) — 🔴 HIGH

- [ ] **#1** `s.Fg8w...rTmt` — opentofu (1 file)
  - `reference_architectures/opentofu/website/docs/language/state/examples/encryption/openbao.tf:11`

---
