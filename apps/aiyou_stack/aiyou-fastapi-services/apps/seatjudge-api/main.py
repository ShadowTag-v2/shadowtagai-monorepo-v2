import os
import random
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="SeatJudge API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- In-Memory DB (Pilot Only) ---
SEAT_DB = {}  # venue_id -> {seat_id -> SeatStatus}


# --- Models ---
class SeatRequest(BaseModel):
    venue_id: str
    section_id: str
    seat_id: str
    user_id: str | None = None


class RiskAssessment(BaseModel):
    score: int  # 0-100
    decision: str  # "APPROVE", "FLAG", "BLOCK"
    reason: str


class SeatStatus(BaseModel):
    id: str
    status: str
    price: float
    risk_score: int | None = None


# --- Mock Database / Logic (until AlloyDB connected) ---
# In production, this connects to the 'risk_scores' table
def calculate_risk(seat: SeatRequest) -> RiskAssessment:
    # SIMPLE HEURISTIC MOCK
    # 1. Random baseline
    base_score = random.randint(0, 20)

    # 2. "VIP" Section Check (Mock)
    if "VIP" in seat.section_id:
        base_score += 10

    # 3. Decision
    if base_score > 80:
        return RiskAssessment(score=base_score, decision="BLOCK", reason="High Risk Profile")
    if base_score > 50:
        return RiskAssessment(score=base_score, decision="FLAG", reason="Manual Review Needed")
    return RiskAssessment(score=base_score, decision="APPROVE", reason="Low Risk")


# --- Endpoints ---


@app.get("/")
def health_check():
    return {"status": "active", "service": "seatjudge-api"}


@app.post("/assess", response_model=RiskAssessment)
def assess_risk(seat: SeatRequest):
    """Judge 6 Endpoint: Scores a specific seat transaction in real-time."""
    risk = calculate_risk(seat)

    # Store in Memory (Ingestion)
    if seat.venue_id not in SEAT_DB:
        SEAT_DB[seat.venue_id] = {}

    SEAT_DB[seat.venue_id][seat.seat_id] = SeatStatus(
        id=seat.seat_id,
        status="BOOKED" if risk.decision == "APPROVE" else "LOCKED",
        price=random.uniform(50.0, 250.0),  # Mock price
        risk_score=risk.score,
    )

    return risk


@app.get("/map/{venue_id}", response_model=list[SeatStatus])
def get_liquid_seat_map(venue_id: str):
    """Returns the real-time 'Liquid' status of the venue."""
    # Return Ingested Data + Some Mock Data if empty
    ingested_seats = []
    if venue_id in SEAT_DB:
        ingested_seats = list(SEAT_DB[venue_id].values())

    # Add random filler if less than 5
    if len(ingested_seats) < 5:
        for _i in range(50):
            ingested_seats.append(
                SeatStatus(
                    id=str(uuid.uuid4()),
                    status=random.choice(["AVAILABLE", "BOOKED", "LOCKED"]),
                    price=random.uniform(50.0, 250.0),
                    risk_score=random.randint(0, 30),
                ),
            )

    return ingested_seats


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
