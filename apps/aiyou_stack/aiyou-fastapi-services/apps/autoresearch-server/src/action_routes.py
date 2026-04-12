from fastapi import APIRouter
from pydantic import BaseModel

# from google.cloud import firestore # Commented out until auth configured

router = APIRouter()
# db = firestore.Client()


class Approval(BaseModel):
    agent_id: str
    decision: str


@router.post("/adjudicate")
def adjudicate_agent(a: Approval):
    # Mock impl
    print(f"⚖️ JUDGE: Agent {a.agent_id} was {a.decision}")
    return {"status": "success"}
