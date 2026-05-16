# Pub/Sub SMT & Data Lake Integration

## Architecture

We have implemented a dual-path architecture for the `streaming-ingest-topic`:



1. **Raw Data Lake Path (New Feature: Cloud Storage Subscription)**


    * **Subscription:** `streaming-datalake-sub`


    * **Destination:** `gs://acquired-jet-478701-b3-datalake/raw_events/`


    * **Behavior:** Writes raw, untransformed JSON events directly to GCS.


    * **Benefit:** Simplifies ingestion, no intermediate Dataflow/Cloud Function needed.



2. **Secure/Transformed Path (New Feature: Single Message Transforms)**


    * **Subscription:** `streaming-secure-sub`


    * **Transform Resource:** `gs://acquired-jet-478701-b3-datalake/scripts/pubsub_transform.js`


    * **Function:** `transform`


    * **Behavior:** Applies JS-based redaction (SSN), masking (Email), and casting (Timestamp) *in-flight*.


    * **Benefit:** PII protection and schema normalization at the edge.

## Configuration Instructions (Console)

Since SMT configuration via CLI is currently in Preview/Beta and varies, use the Console link provided to attach the UDF:



1. Go to: [Pub/Sub Subscriptions](https://console.cloud.google.com/cloudpubsub/subscription/list?project=acquired-jet-478701-b3)


2. Click `streaming-secure-sub` -> **Edit**.


3. Enable **"Message transformation"**.


4. Select **"JavaScript UDF"**.


5. **Cloud Storage path:** `gs://acquired-jet-478701-b3-datalake/scripts/pubsub_transform.js`


6. **Function name:** `transform`


7. Click **Update**.

## Verification



- **Raw:** Publish `{"ssn": "123", "email": "me@test.com"}` -> Check GCS bucket `raw_events/`.


- **Secure:** Pull from `streaming-secure-sub` -> Verify `ssn` is removed and `email` is masked.
