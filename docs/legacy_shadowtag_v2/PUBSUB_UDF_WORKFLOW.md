# Pub/Sub UDF Development & Deployment Workflow

## Overview

This document outlines the development lifecycle for Pub/Sub User-Defined Functions (UDFs) within the Antigravity ecosystem. UDFs are critical for "Edge Sanitization" and "Cost Control."

## Directory Structure

Store all UDFs in `shadowtag_v2/ingress_udf/` (or a dedicated `udfs/` directory at the root if shared).

```

shadowtag_v2/
└── ingress_udf/
    ├── sanity_check.js      # The UDF code
    ├── sanity_check.test.js # Local unit tests (Jest)
    └── deploy.sh            # Deployment script

```

## Development Cycle

### 1. Local Development (The "Lab")

- **Write Code:** Create the `.js` file using standard ES6 JavaScript.

- **Constraints:** Remember the limits:
  - No `require()` or `import`.

  - Max 500ms execution.

  - Max 20KB size.

- **Test Locally:** Use `jest` or a simple node script to mock the `message` object and verify the transformation. **Do not deploy without testing.**

### 2. Validation (The "Gatekeeper")

- **Linting:** Ensure syntax is valid.

- **Dry Run:** Use the `gcloud pubsub topics publish --dry-run` (conceptual) or a dedicated test topic to verify behavior before attaching to production.

### 3. Deployment (The "Push")

- **Upload:** The UDF code is uploaded to the Pub/Sub resource (Topic or Subscription).

- **Command:**

  ```bash
  gcloud pubsub topics update shadowtag-ingress \
      --message-transform-function=sanityCheck \
      --message-transform-file=shadowtag_v2/ingress_udf/sanity_check.js
  ```

  _(Note: Exact gcloud syntax for SMTs may vary/evolve; check `gcloud alpha` or console if needed)._

### 4. Monitoring (The "Watchtower")

- **Metrics:** Monitor `pubsub.googleapis.com/topic/transform_message_count` and `transform_execution_error_count`.

- **Dead Letter Queue (DLQ):** **CRITICAL.** Always configure a DLQ for the subscription. If a UDF throws an error (e.g., unexpected data type), the message is rejected. Without a DLQ, it might be lost or retry infinitely.

## Integration into CI/CD

- **Cloud Build:** Add a step in `cloudbuild.yaml` to update the UDF whenever `*.js` files in the UDF directory change.

- **Rollback:** Keep versioned copies (e.g., `sanity_check_v1.js`) in case a bad UDF starts dropping valid traffic.

## Best Practices

1. **Fail Safe:** If you are unsure, return the original message rather than `null` (dropping it) or throwing an error.

2. **Log Logic:** You cannot `console.log` in a UDF. Logic must be deterministic.

3. **Keep it Simple:** Do not try to implement complex business logic here. Stick to: **Validate, Sanitize, Normalize.**
