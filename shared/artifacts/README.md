# Shared Artifacts Bridge

This directory (`shared/artifacts/`) serves as the strict operational boundary and data exchange plane between the production environment and the local laboratory.

## The Architecture
1. **CounselConduit (Product)** runs on Google Cloud architecture (Cloud Run, Firebase). 
2. **UphillSnowball (Lab)** runs locally on Apple Silicon (M-series ANE, LanceDB).
3. **The Bridge** is this folder.

## Exchange Protocol
- **Extraction**: CounselConduit must export scrubbed, anonymized fixtures, query traces, and production logs into this directory.
- **Replay**: UphillSnowball reads these artifacts to replay production scenarios locally against Apple Silicon memory engines (LanceDB/MLX) for debugging and R&D.
- **Promotion**: Local evaluation reports and benchmarks are emitted by UphillSnowball back into this directory. These reports form the explicit criteria required to promote experimental lab features back up into CounselConduit.

**Rule**: Code dependencies cannot cross the Product/Lab boundary directly. They can only exchange state via the serialized artifacts placed realistically in this directory.
