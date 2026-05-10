# Task: Investigate Billing and Global Resources in Asset Inventory

## Plan
1. [ ] Open Cloud Asset Inventory dashboard.
2. [ ] Analyze "Global" resource count and breakdown.
3. [ ] Identify types of global resources (IAM, Networking, etc.).
4. [ ] Check resources in `us-central1`.
5. [ ] Capture screenshots of the resource breakdown.
6. [ ] Return detailed explanation to the user.

## Findings
- **Global Resources (~400):**
    - `serviceusage.Service`: 160 (Enabled APIs - Non-billable)
    - `compute.Route`: 103 (Default VPC routes - Non-billable)
    - `iam.ServiceAccount`: 23 (Non-billable)
    - `iam.ServiceAccountKey`: 22 (Non-billable)
    - `pubsub.Topic`: 14
    - `secretmanager.Secret`: 13
    - `secretmanager.SecretVersion`: 9
    - These are mostly "infrastructure metadata" and do not incur significant costs (except secrets which are nominal).
- **us-central1 Resources (444):**
    - `artifactregistry.DockerImage`: 287 (Stored images)
    - `alloydb.Backup`: 19 (Billable!)
    - `storage.Bucket`: 14
    - `compute.Address`: 3 (Static IPs - Billable if unattached!)
    - `vpcaccess.Connector`: 1 (Billable!)
    - `config.Deployment`: 1 (`generative-ai-knowledge-base` - in process of deletion)
    - `run.Service`: (Need to check count)
- **Scrubbing Opportunities:**
    - AlloyDB Backups (19) should be removed if the database is gone.
    - Unattached Static IPs should be released.
    - VPC Connector should be deleted if no longer needed by Cloud Run.
    - Empty or old storage buckets.
