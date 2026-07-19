from datetime import datetime, timezone
from uuid import UUID

from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.modules.identity.models.user import User
from app.modules.audit.models.audit_event import AuditEvent
from app.modules.audit.repositories.audit_repository import AuditRepository
from app.support.exceptions.base import BadRequestException, NotFoundException


class AuditService:
    def __init__(self, repository: AuditRepository) -> None:
        self.repository = repository

    def _parse_scope_uuid(self, value: str | None, code: str, message: str) -> UUID | None:
        if value is None:
            return None
        try:
            return UUID(value)
        except ValueError as exc:
            raise BadRequestException(code=code, message=message) from exc

    def _get_scope(self) -> tuple[UUID | None, UUID | None]:
        return (
            self._parse_scope_uuid(get_current_tenant(), "INVALID_TENANT_CONTEXT", "Header X-Tenant-ID tidak valid."),
            self._parse_scope_uuid(get_current_sppg(), "INVALID_SPPG_CONTEXT", "Header X-SPPG-ID tidak valid."),
        )

    async def list_events(self, module_name: str | None = None, event_type: str | None = None) -> list[AuditEvent]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_events(
            tenant_id=tenant_id,
            sppg_id=sppg_id,
            module_name=module_name,
            event_type=event_type,
        )

    async def get_event(self, event_id: UUID) -> AuditEvent:
        event = await self.repository.get_by_id(event_id)
        if event is None:
            raise NotFoundException(code="AUDIT_EVENT_NOT_FOUND", message="Audit event tidak ditemukan.")
        tenant_id, sppg_id = self._get_scope()
        if tenant_id is not None and event.tenant_id not in {None, tenant_id}:
            raise NotFoundException(code="AUDIT_EVENT_NOT_FOUND", message="Audit event tidak ditemukan.")
        if sppg_id is not None and event.sppg_id not in {None, sppg_id}:
            raise NotFoundException(code="AUDIT_EVENT_NOT_FOUND", message="Audit event tidak ditemukan.")
        return event

    async def record_event(
        self,
        *,
        event_type: str,
        module_name: str,
        action_name: str,
        summary: str,
        actor: User | None = None,
        tenant_id: UUID | None = None,
        sppg_id: UUID | None = None,
        entity_type: str | None = None,
        entity_id: UUID | None = None,
        request_id: str | None = None,
        ip_address: str | None = None,
        success: bool = True,
        metadata_json: dict | None = None,
        occurred_at: datetime | None = None,
    ) -> AuditEvent:
        scoped_tenant_id, scoped_sppg_id = self._get_scope()
        return await self.repository.add(
            AuditEvent(
                tenant_id=tenant_id if tenant_id is not None else scoped_tenant_id,
                sppg_id=sppg_id if sppg_id is not None else scoped_sppg_id,
                actor_user_id=actor.id if actor is not None else None,
                actor_name=actor.full_name if actor is not None else None,
                event_type=event_type,
                module_name=module_name,
                action_name=action_name,
                entity_type=entity_type,
                entity_id=entity_id,
                request_id=request_id,
                success=success,
                ip_address=ip_address,
                summary=summary,
                metadata_json=metadata_json or {},
                occurred_at=occurred_at or datetime.now(timezone.utc),
            )
        )
