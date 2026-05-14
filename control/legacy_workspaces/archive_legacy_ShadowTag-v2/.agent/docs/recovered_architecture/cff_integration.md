# CFF Integration Pattern

## Goal
Demonstrate "Best Practice" usage of the locally cloned Cloud Foundation Fabric (`libs/infra/cff`) within the monorepo.

## Structure
We will use the **Local Module Source** pattern. This ensures that:
1.  We rely on the "vendored" code in `libs/infra/cff`.
2.  We satisfy the "ExToto" requirement for self-contained logic (no external git deps during apply).

## Implementation
Creating `infra/blueprints/00-bootstrap/main.tf`:

```hcl
module "project" {
  source          = "../../../libs/infra/cff/modules/project"
  billing_account = var.billing_account
  name            = "antigravity-bootstrap"
  parent          = var.folder_id
  services        = [
    "aiplatform.googleapis.com",
    "compute.googleapis.com"
  ]
}
```

## Governance (Judge 6)
We will add a mechanism to `Judge 6` to run CFF's built-in linters (`tflint`, `terraform validate`) on these blueprints.
