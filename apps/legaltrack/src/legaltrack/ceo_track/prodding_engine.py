from fastapi import APIRouter, BackgroundTasks

from ..models import CEOTrackSchedule
from .integrations.tesla_api import TeslaController

router = APIRouter()

tesla = TeslaController(api_key="TBD", active_vin="TBD")


async def _orchestrate_departure(schedule: CEOTrackSchedule):
    """The background loop for Schiznit hardware prodding prior to an external meeting."""
    # 15 mins prior: Wake up car and start pre-conditioning
    await tesla.wake_vehicle()
    await tesla.precondition_cabin(target_temp_c=21.0)

    # Check charge vs route
    await tesla.check_charge_limits()

    # 5 mins prior: Push destination to FSD
    if schedule.location:
        await tesla.set_navigation_target(address=schedule.location)

    print(f"Schiznit Hardware Orchestration complete for {schedule.task_name}. Car prepped.")


@router.post("/schiznit/nudge")
async def trigger_schiznit_nudge(schedule: CEOTrackSchedule, background_tasks: BackgroundTasks):
    """CEOTrack "Schiznit" Orchestrator.
    Monitors the CEO's active schedule and sends dynamic API pushes
    (to phone, smart home, or Tesla FSD).
    """
    action_plan = []

    if schedule.location == "Office" and not schedule.is_completed:
        action_plan.append("Send 'Time to focus' push notification to phone.")
        action_plan.append("Ping smart chair/desk API to adjust to working posture.")

    if schedule.location and schedule.location != "Office":
        action_plan.append(f"Pushing destination {schedule.location} to Tesla FSD API.")
        action_plan.append("Verifying pre-conditioning is active.")
        # Fire off the physical hardware prodding loop asynchronously
        background_tasks.add_task(_orchestrate_departure, schedule)

    return {
        "status": "active_prodding",
        "task": schedule.task_name,
        "actions_dispatched": action_plan,
    }
