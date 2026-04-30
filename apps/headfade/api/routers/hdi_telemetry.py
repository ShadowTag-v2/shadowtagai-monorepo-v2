from fastapi import APIRouter
from google.cloud import firestore

router = APIRouter()

# The B2B Datastore: Locked to the exact Omega Project per user mandate
db = firestore.Client(project="shadowtag-omega-v4")


@router.post("/vote")
async def record_human_deception_index(
    video_id: str,
    user_vote: str,
    actual_truth: str,
    latency_ms: int,
):
    """[ THE CORE B2B ENGINE ]
    This is the exact mechanism that generates the proprietary Human Deception Index (HDI).
    Every swipe is logged. We are mapping human susceptibility to synthetic physics.
    """
    doc_ref = db.collection("human_deception_index").document()

    juked = user_vote.upper() != actual_truth.upper()

    doc_ref.set(
        {
            "video_id": video_id,
            "user_vote": user_vote.upper(),
            "actual_truth": actual_truth.upper(),
            "juked": juked,  # Did the AI fool them?
            "hesitation_latency_ms": latency_ms,
            "environment": "edge_node_chrome146",
            "timestamp": firestore.SERVER_TIMESTAMP,
        },
    )

    return {"status": "HDI Matrix Updated", "user_fooled": juked}
