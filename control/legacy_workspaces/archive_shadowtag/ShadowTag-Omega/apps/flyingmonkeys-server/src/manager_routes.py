import os, json; from fastapi import APIRouter; from pydantic import BaseModel; from google.cloud import firestore
router = APIRouter();
try: db = firestore.Client()
except: db = None
class AgentUpdate(BaseModel): agent_id: str; status: str; summary: str = None
@router.get("/inbox")
def get_inbox(): return [d.to_dict() for d in db.collection("agents").stream()] if db else []
@router.post("/update")
def post_update(u: AgentUpdate):
    if db: db.collection("agents").document(u.agent_id).set(u.dict())
    return {"status":"synced"}
