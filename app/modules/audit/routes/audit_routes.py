from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.audit.repositories.audit_repository import AuditRepository
from app.modules.audit.schemas.audit_schema import AuditEventRead
from app.modules.audit.services.audit_service import AuditService
from app.modules.identity.models.user import User
from app.support.responses.envelope import success_response

router = APIRouter(prefix="/events")


def get_audit_service(session: AsyncSession = Depends(get_db_session)) -> AuditService:
    return AuditService(AuditRepository(session))


@router.get("/")
async def list_audit_events(
    request: Request,
    module_name: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    service: AuditService = Depends(get_audit_service),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    items = [AuditEventRead.model_validate(item) for item in await service.list_events(module_name, event_type)]
    return success_response(
        code="AUDIT_EVENT_LIST_FOUND",
        message="Daftar audit event berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/{event_id}")
async def get_audit_event(
    event_id: UUID,
    request: Request,
    service: AuditService = Depends(get_audit_service),
    _: User = Depends(require_roles("super_admin", "tenant_admin")),
) -> dict:
    event = await service.get_event(event_id)
    return success_response(
        code="AUDIT_EVENT_FOUND",
        message="Detail audit event berhasil diambil.",
        data=AuditEventRead.model_validate(event),
        meta={"request_id": request.state.request_id},
    )
