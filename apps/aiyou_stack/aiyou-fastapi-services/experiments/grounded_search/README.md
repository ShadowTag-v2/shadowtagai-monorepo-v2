# Grounded Generation Experiments

This directory contains experiments for setting up Grounded Generation with Google Search using Vertex AI.

## Status

- **Authentication**: Successfully authenticated with ADC.

- **APIs**: Enabled `discoveryengine.googleapis.com`, `aiplatform.googleapis.com`, `generativelanguage.googleapis.com`.

- **Scripts**:
  - `vertex_grounding_demo.py`: Uses Vertex AI SDK (`vertexai`). **Current Status**: Fails with `404 Publisher Model not found` for `gemini-1.0-pro` and `gemini-1.5-flash` in `us-central1`.

  - `grounded_gen_demo.py`: Uses Agent Builder SDK (`discoveryengine`). **Current Status**: Fails with `501 Method not found` in `global` and `us-central1`.

## Troubleshooting

The `404 Publisher Model not found` error suggests that the project `acquired-jet-478701-b3` may not have access to these models in `us-central1`, or there is a billing/quota issue preventing access.

## How to Run

1. **Vertex AI Demo** (Recommended approach):

   ```bash
   python3 vertex_grounding_demo.py
   ```

2. **Agent Builder Demo**:

   ```bash
   python3 grounded_gen_demo.py
   ```

## Helper Scripts

- `enable_api.py`: Script to enable Google Cloud APIs.

- `get_project_number.py`: Script to retrieve the project number.

- `test_models.py`: Script to test model initialization (note: initialization succeeds, but generation fails).
