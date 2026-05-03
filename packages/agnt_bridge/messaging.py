"""Safe Harbor bridge message routing.

Ported from src/bridge/bridgeMessaging.ts. Local IPC only.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any
from collections.abc import Callable

from ._types import (
    BridgeMessage,
    ControlRequest,
    ControlRequestSubtype,
    ControlResponse,
    ControlResponseSubtype,
)
from .bounded_set import BoundedUUIDSet

logger = logging.getLogger(__name__)


def is_user_message(msg: BridgeMessage) -> bool:
    return msg.msg_type == "user"


def handle_ingress_message(
    msg: BridgeMessage,
    recent_posted: BoundedUUIDSet,
    recent_inbound: BoundedUUIDSet,
    on_inbound: Callable[[BridgeMessage], None] | None = None,
    on_control_response: Callable[[dict[str, Any]], None] | None = None,
    on_control_request: Callable[[ControlRequest], None] | None = None,
) -> None:
    """Route ingress message with echo/replay dedup."""
    msg_uuid = msg.msg_uuid

    if msg.msg_type == "control_response":
        if on_control_response:
            on_control_response(msg.payload)
        return

    if msg.msg_type == "control_request":
        sub = msg.payload.get("subtype", "unknown")
        if on_control_request:
            try:
                req = ControlRequest(
                    subtype=ControlRequestSubtype(sub),
                    request_id=msg.payload.get("request_id", ""),
                    model=msg.payload.get("model"),
                    max_thinking_tokens=msg.payload.get("max_thinking_tokens"),
                    mode=msg.payload.get("mode"),
                )
                on_control_request(req)
            except ValueError:
                logger.warning("Unknown control subtype: %s", sub)
        return

    if msg_uuid and recent_posted.has(msg_uuid):
        return
    if msg_uuid and recent_inbound.has(msg_uuid):
        return

    if is_user_message(msg):
        if msg_uuid:
            recent_inbound.add(msg_uuid)
        if on_inbound:
            on_inbound(msg)


def handle_control_request(
    request: ControlRequest,
    on_interrupt: Callable[[], None] | None = None,
    on_set_model: Callable[[str | None], None] | None = None,
) -> ControlResponse:
    """Handle control_request, return response."""
    match request.subtype:
        case ControlRequestSubtype.INITIALIZE:
            return ControlResponse(
                subtype=ControlResponseSubtype.SUCCESS,
                request_id=request.request_id,
                response={"commands": [], "output_style": "normal"},
            )
        case ControlRequestSubtype.SET_MODEL:
            if on_set_model:
                on_set_model(request.model)
            return ControlResponse(
                subtype=ControlResponseSubtype.SUCCESS,
                request_id=request.request_id,
            )
        case ControlRequestSubtype.INTERRUPT:
            if on_interrupt:
                on_interrupt()
            return ControlResponse(
                subtype=ControlResponseSubtype.SUCCESS,
                request_id=request.request_id,
            )
        case _:
            return ControlResponse(
                subtype=ControlResponseSubtype.ERROR,
                request_id=request.request_id,
                error=f"Unknown subtype: {request.subtype}",
            )


def make_result_message(session_id: str) -> BridgeMessage:
    """Build minimal result message for session archival."""
    return BridgeMessage(
        msg_type="result",
        session_id=session_id,
        payload={"subtype": "success", "is_error": False},
        msg_uuid=str(uuid.uuid4()),
    )
