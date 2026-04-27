# Task Checklist
- [x] Navigate to Gemini 3.1 Flash Lite Preview in Vertex Model Garden.
- [x] Check if model exists and if it is enabled. (Model exists and is functional in Vertex AI Studio)
- [x] Enable model if necessary. (Already enabled for project shadowtag-omega-v4)
- [x] Verify model status. (Tested successfully in Vertex AI Studio)
- [x] Identify correct API endpoint. (Discovered that the recommended curl command uses `locations/global` instead of `locations/us-central1`)
- [ ] Return summary of findings.

## Findings
- Model is fully enabled and functional in Vertex AI Studio for project `shadowtag-omega-v4`.
- The `404 NOT_FOUND` error in the user's `curl` test was likely due to using `locations/us-central1` and a regional endpoint prefix.
- The official Vertex AI "View Code" documentation for this model specifies the endpoint as `https://aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/global/publishers/google/models/gemini-3.1-flash-lite-preview:streamGenerateContent`.
