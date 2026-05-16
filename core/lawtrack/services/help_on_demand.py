# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HelpRequest(BaseModel):
  matter_id: str
  user_id: str
  context_task: str
  escalation_tier: str  # e.g., 'ai_tutor', 'peer', 'expert_live'


@router.post("/ping")
def request_help(request: HelpRequest):
  """
  The 'Help-on-Demand' Plugin.
  This allows students or entry-level professionals to click a single button during a 'nag'
  and immediately get un-stuck via AI routing or human escalation.
  """

  if request.escalation_tier == "ai_tutor":
    # Dispatch to Gemini 3.1 Pro tutor persona, feeding in the exact syllabus/rules context
    response_action = "Initiated interactive AI tutoring session with matter context."
  elif request.escalation_tier == "expert_live":
    # Ping the Partner Dashboard (Legal) or Teacher Dashboard (Academic)
    response_action = "Escalated to human supervisor queue."
  else:
    response_action = "Routed to default peer network."

  # Audit log this request so managers/parents can see where the user is getting stuck
  print(
    f"Audit: User {request.user_id} requested {request.escalation_tier} for {request.context_task}"
  )

  return {"status": "help_dispatched", "action_taken": response_action}
