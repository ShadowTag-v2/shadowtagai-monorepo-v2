# Glass House Ascension (Genesis V6) Implementation Plan

## Proposed Changes

### LangExtract Workers Initialization

- Create a deployment script, `scripts/deploy_langextract_workers.sh` to build and deploy the `langextract-rs` and `langextract-typescript` Dockerfiles to Google Cloud Run.
- Ensure the script registers the deployed URLs so that the `ServerlessQueueMatrix` (defined in `src/infra/cloud_tasks_publisher.py`) can route Deep Mode tasks to them correctly.

### GlassBox Dashboard Expansion

#### [MODIFY] GlassBoxDashboard.tsx(file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/frontend/app/GlassBoxDashboard.tsx)

- The KINETIC OUTPUT pane currently renders `StitchRenderer` components for `UI_RENDER_COMPONENT` events.
- I will expand this to support rendering raw HTML/DOM artifacts (e.g., using a sanitized `dangerouslySetInnerHTML`) or iframe isolation for when the Swarm generates pure DOM artifacts rather than specific Stitch components.
- Add visual indicators for the LangExtract parsing status.

### 'Caduceus/Midas' Vertical Test

#### [NEW] test_caduceus_vertical.py(file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/scripts/test_caduceus_vertical.py)

- Create a test script to validate the ingestion layer.
- The script will submit a mock 10-K SEC filing extraction task to the `gideon-deep-mode` Cloud Task queue, targeting the deployed `langextract-rs` endpoint.
- It will simulate an illegal/hallucinated data extraction to explicitly test the `dow_crsmc_sentinel.py` (17-Layer Sentinel) rejection capability.

## Verification Plan

### Automated Tests

- Run `deploy_langextract_workers.sh` with a dry-run flag or verify its Docker builds locally.
- Execute `python scripts/test_caduceus_vertical.py` to ensure the simulated task routes through Cloud Tasks to the dummy endpoint and interacts with the Sentinel properly.

### Manual Verification

- Launch the UI (`npm run dev` in the frontend director) and verify the KINETIC OUTPUT pane properly renders the raw HTML thought artifacts.
- Confirm the GlassBox UI websocket continues to connect and display stream logs correctly.
