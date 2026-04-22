---
name: Terraform Change
about: Modify infrastructure-as-code (Terraform/Terragrunt modules)
title: "[TF] "
labels: infrastructure, terraform
assignees: ""
---

## Change Type
- [ ] New module
- [ ] Module update
- [ ] Environment config change
- [ ] State migration
- [ ] Provider upgrade
- [ ] Security policy update

## Description
<!-- What infrastructure change are you making and why? -->

## Affected Resources
<!-- List the GCP resources that will be created/modified/destroyed -->
| Action | Resource Type | Resource Name |
|--------|--------------|---------------|
| create/modify/destroy | | |

## Plan Output
<!-- Paste the relevant `terragrunt plan` output -->
```
<paste plan here>
```

## Checklist
- [ ] `terragrunt plan` shows expected changes only
- [ ] No secrets in HCL files (using Secret Manager references)
- [ ] Module has README with usage example
- [ ] Variables have descriptions and validation blocks
- [ ] Outputs are documented
- [ ] `prevent_destroy` lifecycle on stateful resources
- [ ] Checkov scan passes (`checkov -d .`)
- [ ] Drift detection reviewed (if modifying live resources)
- [ ] Cost impact assessed (free tier / paid)
- [ ] Rollback plan documented below

## Rollback Plan
<!-- How to revert if this change causes issues -->

## Cost Impact
- [ ] Within free tier
- [ ] Paid — estimated: $__/month
- [ ] Unknown — needs review
