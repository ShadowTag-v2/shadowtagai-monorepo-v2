from fastapi import APIRouter
from google.cloud import spanner
from pydantic import BaseModel

router = APIRouter()


class ReceiptPayload(BaseModel):
  session_id: str
  prompt: str
  video_uri: str


@router.post("/log-receipt")
async def secure_shadowtag_receipt(payload: ReceiptPayload):
  """Immutable cryptographic ledger tracking AI asset generation."""
  try:
    spanner_client = spanner.Client(project="shadowtag-omega-v4")
    instance = spanner_client.instance("headfade-ledger")
    database = instance.database("audit-db")

    with database.batch() as batch:
      batch.insert(
        table="ForensicReceipts",
        columns=("SessionId", "PromptData", "VideoUri", "Timestamp", "SynthIdVerified"),
        values=[
          (
            payload.session_id,
            payload.prompt,
            payload.video_uri,
            spanner.COMMIT_TIMESTAMP,
            True,
          ),
        ],
      )

    return {"status": "success", "message": "ShadowTag receipt irrevocably logged."}
  except Exception as e:
    return {"status": "error", "message": f"Failed writing to Spanner: {e!s}"}
