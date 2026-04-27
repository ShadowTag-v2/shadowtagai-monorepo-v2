# Crime Prevention Module Implementation

## Goal
Integrate "Cor.Judge.Grok" Crime Prevention Module (fully GCP native) into Judge6 v5.

## Proposed Changes
#### [NEW] `apps/src/api/domain/judge6/layers/crime_prevention_agent.py`
- Implements `CrimeDetector`, `CrimeMitigator`, `CrimeNotifier` classes as defined in prototype.
- Uses `google-cloud-bigquery`, `aiplatform`, `logging`, `securitycenter`.

#### [MODIFY] `apps/src/api/domain/judge6/api/routes.py`
- Add `CRIME` domain to `/evaluate` endpoint.
- Route `CRIME` requests to `CrimePreventionAgent`.

#### [MODIFY] `apps/requirements.txt`
- Add `google-cloud-bigquery`, `google-cloud-securitycenter`.

## Verification
- Deploy to Cloud Run.
- `curl` test with "embezzlement" payload.
