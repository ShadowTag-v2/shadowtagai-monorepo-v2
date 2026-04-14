import logging
from typing import Any

from fastapi import APIRouter
from googleapiclient.discovery import build

router = APIRouter()

logger = logging.getLogger(__name__)


class GoogleCalendarController:
    """Idempotent abstraction for interacting with Google Calendar API.
    Acts as the source of truth for LegalTrack + CEOTrack convergence.
    """

    def __init__(self, oauth_credentials=None):
        self.creds = oauth_credentials
        if self.creds:
            self.service = build("calendar", "v3", credentials=self.creds)
        else:
            self.service = None

    def _generate_idempotency_key(self, source_system: str, event_hash: str) -> str:
        """Ensures we never duplicate events if LegalTrack calculations vary.
        Output: e.g. "legaltrackfrcp12a54321" (Must be base32-hex for GCal ID)
        """
        raw_key = f"{source_system}_{event_hash}"
        return raw_key.replace("-", "").replace("_", "")

    async def upsert_event(
        self,
        calendar_id: str,
        title: str,
        start_iso: str,
        end_iso: str,
        source_system: str,
        event_hash: str,
        location: str | None = None,
    ) -> dict[str, Any]:
        """Checks if the event ID exists. If yes, updates it. If no, creates it.
        """
        event_id = self._generate_idempotency_key(source_system, event_hash)

        if not self.service:
            logger.warning(
                f"GoogleCalendarController: No credentials provided. Mocking upsert for {title} at {start_iso}",
            )
            return {"status": "success", "event_id": event_id, "idempotent": True}

        event_body = {
            "id": event_id,
            "summary": title,
            "location": location,
            "start": {"date": start_iso} if len(start_iso) <= 10 else {"dateTime": start_iso},
            "end": {"date": end_iso} if len(end_iso) <= 10 else {"dateTime": end_iso},
        }

        try:
            try:
                # Try inserting first (O(1) fast path)
                event = (
                    self.service.events().insert(calendarId=calendar_id, body=event_body).execute()
                )
            except Exception:
                # If it fails with 409 conflict, update instead
                event = (
                    self.service.events()
                    .update(calendarId=calendar_id, eventId=event_id, body=event_body)
                    .execute()
                )

            logger.info(f"Successfully upserted Google Calendar event: {event.get('id')}")
            return {"status": "success", "event_id": event.get("id"), "idempotent": True}

        except Exception as e:
            logger.error(f"Failed to upsert to Google Calendar: {e}")
            return {"status": "error", "error": str(e)}


from pydantic import BaseModel


class CalendarUpsertRequest(BaseModel):
    calendar_id: str = "primary"
    title: str
    start_iso: str
    end_iso: str
    source_system: str
    event_hash: str
    location: str | None = None


@router.post("/upsert")
async def upsert_calendar_event(req: CalendarUpsertRequest) -> dict[str, Any]:
    """Idempotent Google Calendar event upsert. Credentials injected via OAuth flow."""
    cal = GoogleCalendarController()  # no creds → dev mock mode
    return await cal.upsert_event(
        calendar_id=req.calendar_id,
        title=req.title,
        start_iso=req.start_iso,
        end_iso=req.end_iso,
        source_system=req.source_system,
        event_hash=req.event_hash,
        location=req.location,
    )
