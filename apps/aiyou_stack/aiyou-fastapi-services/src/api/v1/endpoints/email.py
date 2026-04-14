"""Email automation API endpoints"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api.v1.dependencies import get_db, get_email_service
from src.core.exceptions import (
    EmailProviderError,
    InvalidEmailFlow,
    TemplateNotFound,
)
from src.services.email import repository, schemas
from src.services.email.service import EmailService

router = APIRouter(prefix="/email", tags=["email"])


# Recipients
@router.post("/recipients", response_model=schemas.RecipientResponse, status_code=201)
def create_recipient(recipient: schemas.RecipientCreate, db: Session = Depends(get_db)):
    """Create a new email recipient"""
    # Check if recipient already exists
    existing = repository.EmailRepository.get_recipient_by_email(db, recipient.email)
    if existing:
        raise HTTPException(status_code=400, detail="Recipient already exists")

    return repository.EmailRepository.create_recipient(db, recipient)


@router.get("/recipients/{recipient_id}", response_model=schemas.RecipientResponse)
def get_recipient(recipient_id: int, db: Session = Depends(get_db)):
    """Get recipient by ID"""
    recipient = repository.EmailRepository.get_recipient(db, recipient_id)
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    return recipient


@router.get("/recipients", response_model=list[schemas.RecipientResponse])
def list_recipients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """List all recipients"""
    return repository.EmailRepository.get_recipients(db, skip, limit)


@router.patch("/recipients/{recipient_id}", response_model=schemas.RecipientResponse)
def update_recipient(
    recipient_id: int, recipient_update: schemas.RecipientUpdate, db: Session = Depends(get_db),
):
    """Update recipient"""
    recipient = repository.EmailRepository.update_recipient(db, recipient_id, recipient_update)
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    return recipient


# Templates
@router.post("/templates", response_model=schemas.EmailTemplateResponse, status_code=201)
def create_template(template: schemas.EmailTemplateCreate, db: Session = Depends(get_db)):
    """Create a new email template"""
    # Check if template already exists
    existing = repository.EmailRepository.get_template_by_name(db, template.name)
    if existing:
        raise HTTPException(status_code=400, detail="Template with this name already exists")

    return repository.EmailRepository.create_template(db, template)


@router.get("/templates/{template_id}", response_model=schemas.EmailTemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    """Get template by ID"""
    template = repository.EmailRepository.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.get("/templates", response_model=list[schemas.EmailTemplateResponse])
def list_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """List all templates"""
    return repository.EmailRepository.get_templates(db, skip, limit)


# Email Flows
@router.post("/flows", response_model=schemas.EmailFlowResponse, status_code=201)
def create_flow(
    flow: schemas.EmailFlowCreate,
    db: Session = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
):
    """Create a new email flow"""
    try:
        return email_service.create_flow(db, flow)
    except InvalidEmailFlow as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/flows/{flow_id}", response_model=schemas.EmailFlowResponse)
def get_flow(flow_id: int, db: Session = Depends(get_db)):
    """Get flow by ID"""
    flow = repository.EmailRepository.get_flow(db, flow_id)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    return flow


@router.get("/flows", response_model=list[schemas.EmailFlowResponse])
def list_flows(active_only: bool = Query(False), db: Session = Depends(get_db)):
    """List all email flows"""
    return repository.EmailRepository.get_flows(db, active_only)


# Flow Enrollments
@router.post("/flows/{flow_id}/enroll", response_model=schemas.FlowEnrollmentResponse)
def enroll_in_flow(
    flow_id: int,
    recipient_email: str,
    db: Session = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
):
    """Enroll a recipient in an email flow"""
    try:
        return email_service.enroll_recipient(db, flow_id, recipient_email)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/flows/bulk-enroll", response_model=schemas.BulkEnrollResponse)
async def bulk_enroll(
    request: schemas.BulkEnrollRequest,
    db: Session = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
):
    """Bulk enroll recipients in a flow"""
    return await email_service.bulk_enroll(db, request)


# Send Emails
@router.post("/send", response_model=schemas.EmailResponse, status_code=201)
async def send_email(
    request: schemas.EmailSendRequest,
    db: Session = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
):
    """Send an email"""
    try:
        return await email_service.send_email(db, request)
    except TemplateNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except EmailProviderError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {e!s}")


@router.get("/emails/{email_id}", response_model=schemas.EmailResponse)
def get_email(email_id: int, db: Session = Depends(get_db)):
    """Get email by ID"""
    email = repository.EmailRepository.get_email(db, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@router.get("/emails", response_model=list[schemas.EmailResponse])
def list_emails(
    recipient_id: int | None = Query(None),
    status: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """List emails"""
    from src.db.models import EmailStatus as EmailStatusEnum

    email_status = None
    if status:
        try:
            email_status = EmailStatusEnum(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    return repository.EmailRepository.get_emails(db, recipient_id, email_status, skip, limit)


# Analytics
@router.get("/emails/{email_id}/analytics", response_model=schemas.EmailAnalyticsResponse)
def get_email_analytics(email_id: int, db: Session = Depends(get_db)):
    """Get email analytics"""
    from src.db.models import EmailAnalytics

    analytics = db.query(EmailAnalytics).filter(EmailAnalytics.email_id == email_id).first()
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics not found")
    return analytics


@router.get("/metrics/campaign")
def get_campaign_metrics(
    flow_id: int | None = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
):
    """Get campaign metrics"""
    return email_service.get_campaign_metrics(db, flow_id, days)


# Tracking Endpoints
@router.get("/track/open/{tracking_id}")
def track_open(
    tracking_id: str,
    db: Session = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
):
    """Track email open (typically called via tracking pixel)"""
    email_service.track_open(db, tracking_id)
    # Return 1x1 transparent GIF
    import base64

    from fastapi.responses import Response

    gif = base64.b64decode("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")
    return Response(content=gif, media_type="image/gif")


@router.get("/track/click/{tracking_id}")
def track_click(
    tracking_id: str,
    url: str = Query(...),
    db: Session = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
):
    """Track email click and redirect"""
    from fastapi.responses import RedirectResponse

    email_service.track_click(db, tracking_id, {"url": url})
    return RedirectResponse(url=url)


# Background Tasks
@router.post("/process/queue")
async def process_email_queue(
    background_tasks: BackgroundTasks,
    batch_size: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
):
    """Process email queue (typically called by scheduler)"""
    count = await email_service.process_email_queue(db, batch_size)
    return {"processed": count}


@router.post("/process/flows")
async def process_flow_enrollments(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
):
    """Process flow enrollments (typically called by scheduler)"""
    count = await email_service.process_flow_enrollments(db)
    return {"processed": count}
