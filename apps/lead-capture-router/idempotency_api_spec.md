# Idempotency API Protocol

## Generation
External clients MUST generate a 256-bit SHA-2 hash composed of:
`timestamp_millis` + `payload_email` + `request_origin`

## Insertion
This explicit string must be dropped inside the headers:
`X-KOVELAI-IDEMPOTENCY: <SHA_256>`

## Lifecycle
If the key maps to `LOCK_ACQUIRED` inside Firestore `system_idempotency_keys` across the 250ms Temporal boundary, a `200 OK` is immediately fired to the client. Subsequent payloads carrying the exact key within 600 seconds trigger a `304 Not Modified` bypass.
