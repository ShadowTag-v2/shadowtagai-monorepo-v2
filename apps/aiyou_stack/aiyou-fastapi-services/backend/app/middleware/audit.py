# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Audit Middleware - Automatically log all API requests for compliance"""

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.config import settings
from app.db.session import AsyncSessionLocal
from app.models.audit_log import ActionType
from app.services.compliance_service import ComplianceService

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically audit all API requests"""

    async def dispatch(self, request: Request, call_next):
        """Process request and create audit log"""
        start_time = time.time()
        str(uuid.uuid4())

        # Skip audit for health checks and docs
        if request.url.path in ["/health", "/api/docs", "/api/redoc", "/openapi.json"]:
            return await call_next(request)

        # Extract request information
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        request_method = request.method
        request_path = request.url.path

        # Anonymize IP if configured
        if settings.ANONYMIZE_IP and ip_address:
            ip_address = self._anonymize_ip(ip_address)

        # Process request
        response = None
        error_message = None
        success = "success"

        try:
            response = await call_next(request)
            status_code = response.status_code

            if status_code >= 400:
                success = "failure" if status_code >= 500 else "denied"

        except Exception as e:
            logger.error(f"Request failed: {e}")
            status_code = 500
            success = "failure"
            error_message = str(e)
            raise
        finally:
            # Calculate duration
            int((time.time() - start_time) * 1000)

            # Determine action type from method
            action = self._method_to_action(request_method)

            # Create audit log asynchronously
            try:
                async with AsyncSessionLocal() as db:
                    service = ComplianceService(db)
                    await service.create_audit_log(
                        action=action,
                        resource_type=self._extract_resource_type(request_path),
                        resource_id=self._extract_resource_id(request_path),
                        ip_address=ip_address,
                        user_agent=user_agent,
                        request_method=request_method,
                        request_path=request_path,
                        status_code=status_code if response else 500,
                        success=success,
                        error_message=error_message,
                    )
            except Exception as e:
                logger.error(f"Failed to create audit log: {e}")

        return response

    def _method_to_action(self, method: str) -> ActionType:
        """Map HTTP method to audit action type"""
        mapping = {
            "GET": ActionType.READ,
            "POST": ActionType.CREATE,
            "PUT": ActionType.UPDATE,
            "PATCH": ActionType.UPDATE,
            "DELETE": ActionType.DELETE,
        }
        return mapping.get(method, ActionType.READ)

    def _extract_resource_type(self, path: str) -> str:
        """Extract resource type from path"""
        parts = path.strip("/").split("/")
        # Typically /api/v1/resource/{id}
        if len(parts) >= 3:
            return parts[2]  # e.g., "users", "compliance"
        return "unknown"

    def _extract_resource_id(self, path: str) -> str:
        """Extract resource ID from path"""
        parts = path.strip("/").split("/")
        # Look for UUID-like patterns
        for part in parts:
            if len(part) == 36 and "-" in part:  # Simple UUID check
                return part
        return None

    def _anonymize_ip(self, ip: str) -> str:
        """Anonymize IP address for privacy"""
        # For IPv4: mask last octet
        # For IPv6: mask last 80 bits
        try:
            if ":" in ip:  # IPv6
                parts = ip.split(":")
                return ":".join(parts[:4]) + ":0:0:0:0"
            # IPv4
            parts = ip.split(".")
            return ".".join(parts[:3]) + ".0"
        except Exception:
            return "anonymized"
