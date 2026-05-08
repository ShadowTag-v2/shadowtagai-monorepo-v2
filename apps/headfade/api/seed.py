import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, UTC
import uuid


def seed():
    print("Initializing Firebase...")
    cred = credentials.ApplicationDefault()
    import contextlib

    with contextlib.suppress(ValueError):
        firebase_admin.initialize_app(cred, {"projectId": "shadowtag-omega-v4"})
    db = firestore.client()

    print("Seeding users...")
    user_id_1 = str(uuid.uuid4())
    db.collection("users").document(user_id_1).set(
        {
            "uid": user_id_1,
            "role": "CREATOR",
            "displayName": "Alice Creator",
            "email": "alice@example.com",
            "createdAt": datetime.now(UTC),
            "updatedAt": datetime.now(UTC),
        }
    )

    print("Seeding videos...")
    video_id_1 = str(uuid.uuid4())
    db.collection("videos").document(video_id_1).set(
        {
            "id": video_id_1,
            "creatorId": user_id_1,
            "gcsUri": "gs://shadowtag-omega-v4/video1.mp4",
            "title": "A Real Person Walking",
            "description": "Just a normal walk.",
            "groundTruth": "REAL",
            "status": "PUBLISHED",
            "createdAt": datetime.now(UTC),
        }
    )

    video_id_2 = str(uuid.uuid4())
    db.collection("videos").document(video_id_2).set(
        {
            "id": video_id_2,
            "creatorId": user_id_1,
            "gcsUri": "gs://shadowtag-omega-v4/video2.mp4",
            "title": "AI generated speech",
            "description": "Sora test.",
            "groundTruth": "AI",
            "status": "PUBLISHED",
            "createdAt": datetime.now(UTC),
        }
    )

    print("Seeding forensic_verdicts...")
    verdict_id = str(uuid.uuid4())
    db.collection("forensic_verdicts").document(verdict_id).set(
        {
            "id": verdict_id,
            "videoId": video_id_1,
            "model": "gemini-3.1-flash-lite-preview",
            "geminiVerdict": "The video shows natural lighting and consistent physics.",
            "geminiThoughts": "The shadows align perfectly with the light source.",
            "confidenceScore": 0.99,
            "latencyMs": 1200,
            "analyzedAt": datetime.now(UTC),
        }
    )

    print("Seeding human telemetry...")
    db.collection("human_telemetry").document(str(uuid.uuid4())).set(
        {"videoId": video_id_1, "userVote": "AI", "actualTruth": "REAL", "isCorrect": False, "latencyMs": 1500, "votedAt": datetime.now(UTC)}
    )

    print("Seeding licenses...")
    license_id = str(uuid.uuid4())
    db.collection("licenses").document(license_id).set(
        {
            "id": license_id,
            "videoId": video_id_1,
            "buyerId": str(uuid.uuid4()),
            "sellerId": user_id_1,
            "licenseType": "STANDARD",
            "priceAmount": 500,
            "priceCurrency": "usd",
            "stripePaymentIntentId": "pi_mock123",
            "purchasedAt": datetime.now(UTC),
        }
    )

    print("Seeding complete.")


if __name__ == "__main__":
    seed()
