from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from apps.counselconduit.api.fastapi_kovel_enclave import app
import json
import hmac
import hashlib
import time

client = TestClient(app)

dummy_payload = {
    "id": "evt_test_123",
    "object": "event",
    "type": "checkout.session.completed",
    "data": {
        "object": {
            "id": "cs_test_123",
            "object": "checkout.session",
            "customer": "cus_test_123",
            "customer_email": "test_attorney@example.com",
            "subscription": "sub_test_123"
        }
    }
}

payload_bytes = json.dumps(dummy_payload).encode("utf-8")
timestamp = int(time.time())
secret = "test_secret"

signed_payload = f"{timestamp}.".encode() + payload_bytes
expected_sig = hmac.new(
    secret.encode("utf-8"),
    signed_payload,
    hashlib.sha256,
).hexdigest()

headers = {
    "Content-Type": "application/json",
    "Stripe-Signature": f"t={timestamp},v1={expected_sig}"
}

with patch("apps.counselconduit.api.stripe_handler._get_webhook_secret", return_value=secret):
    with patch("apps.counselconduit.api.firestore_client._get_client") as mock_get_client:
        mock_db = MagicMock()
        mock_get_client.return_value = mock_db
        # Mock the async doc_ref.set
        mock_doc_ref = MagicMock()
        mock_doc_ref.set = AsyncMock()
        mock_db.collection().document.return_value = mock_doc_ref
        
        response = client.post("/webhooks/stripe", content=payload_bytes, headers=headers)

print("Status Code:", response.status_code)
print("Response JSON:", response.json() if response.status_code == 200 else response.text)

# Verify mock was called
mock_doc_ref.set.assert_called_once()
print("Firestore mock called successfully!")
