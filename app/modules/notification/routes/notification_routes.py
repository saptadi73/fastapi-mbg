from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import get_current_user, require_roles
from app.modules.audit.repositories.audit_repository import AuditRepository
from app.modules.audit.services.audit_service import AuditService
from app.modules.identity.models.user import User
from app.modules.identity.repositories.user_repository import UserRepository
from app.modules.notification.repositories.notification_repository import NotificationRepository
from app.modules.notification.schemas.notification_schema import (
    InboxItemRead,
    NotificationBundleRead,
    NotificationDispatchCreate,
    NotificationPreferenceRead,
    NotificationPreferenceUpsert,
    NotificationRecipientRead,
    NotificationTemplateCreate,
    NotificationTemplateRead,
)
from app.modules.notification.services.notification_service import NotificationService
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.responses.envelope import success_response

router = APIRouter()


def get_notification_service(session: AsyncSession = Depends(get_db_session)) -> NotificationService:
    return NotificationService(
        NotificationRepository(session),
        TenantRepository(session),
        SppgRepository(session),
        UserRepository(session),
    )


def get_audit_service(session: AsyncSession) -> AuditService:
    return AuditService(AuditRepository(session))


@router.get("/templates")
async def list_notification_templates(
    request: Request,
    service: NotificationService = Depends(get_notification_service),
) -> dict:
    items = [NotificationTemplateRead.model_validate(item) for item in await service.list_templates()]
    return success_response(
        code="NOTIFICATION_TEMPLATE_LIST_FOUND",
        message="Daftar notification template berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/templates", status_code=status.HTTP_201_CREATED)
async def create_notification_template(
    payload: NotificationTemplateCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = get_notification_service(session)
    template = await service.create_template(payload)
    await get_audit_service(session).record_event(
        event_type="NOTIFICATION",
        module_name="notification",
        action_name="CREATE_TEMPLATE",
        summary="Notification template dibuat.",
        actor=actor,
        tenant_id=template.tenant_id,
        entity_type="notification_template",
        entity_id=template.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"code": template.code, "channel": template.channel},
    )
    await session.commit()
    return success_response(
        code="NOTIFICATION_TEMPLATE_CREATED",
        message="Notification template berhasil dibuat.",
        data=NotificationTemplateRead.model_validate(template),
        meta={"request_id": request.state.request_id},
    )


@router.get("/preferences/me")
async def list_my_notification_preferences(
    request: Request,
    actor: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> dict:
    items = [NotificationPreferenceRead.model_validate(item) for item in await service.list_my_preferences(actor.id)]
    return success_response(
        code="NOTIFICATION_PREFERENCE_LIST_FOUND",
        message="Daftar notification preference berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.put("/preferences/me")
async def upsert_my_notification_preference(
    payload: NotificationPreferenceUpsert,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(get_current_user),
) -> dict:
    service = get_notification_service(session)
    preference = await service.upsert_my_preference(actor.id, payload)
    await get_audit_service(session).record_event(
        event_type="NOTIFICATION",
        module_name="notification",
        action_name="UPSERT_PREFERENCE",
        summary="Notification preference diperbarui.",
        actor=actor,
        tenant_id=preference.tenant_id,
        sppg_id=actor.active_sppg_id,
        entity_type="notification_preference",
        entity_id=preference.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"channel": preference.channel, "is_enabled": preference.is_enabled},
    )
    await session.commit()
    return success_response(
        code="NOTIFICATION_PREFERENCE_UPDATED",
        message="Notification preference berhasil diperbarui.",
        data=NotificationPreferenceRead.model_validate(preference),
        meta={"request_id": request.state.request_id},
    )


@router.get("/inbox")
async def list_my_inbox(
    request: Request,
    actor: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> dict:
    items = [InboxItemRead.model_validate(item) for item in await service.list_my_inbox(actor.id)]
    return success_response(
        code="NOTIFICATION_INBOX_FOUND",
        message="Inbox notification berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def dispatch_notification(
    payload: NotificationDispatchCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager", "quality_officer", "finance_manager")),
) -> dict:
    service = get_notification_service(session)
    bundle = await service.dispatch_notification(payload)
    notification = bundle["notification"]
    await get_audit_service(session).record_event(
        event_type="NOTIFICATION",
        module_name="notification",
        action_name="DISPATCH_NOTIFICATION",
        summary="Notification dibuat dan dimasukkan ke queue.",
        actor=actor,
        tenant_id=notification.tenant_id,
        sppg_id=notification.sppg_id,
        entity_type="notification",
        entity_id=notification.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"priority": notification.priority, "recipient_count": len(bundle["recipients"])},
    )
    await session.commit()
    return success_response(
        code="NOTIFICATION_DISPATCHED",
        message="Notification berhasil dibuat.",
        data=NotificationBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id},
    )


@router.get("/{notification_id}")
async def get_notification_detail(
    notification_id: UUID,
    request: Request,
    service: NotificationService = Depends(get_notification_service),
) -> dict:
    bundle = await service.get_notification_bundle(notification_id)
    return success_response(
        code="NOTIFICATION_FOUND",
        message="Detail notification berhasil diambil.",
        data=NotificationBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id},
    )


@router.post("/inbox/{recipient_id}/mark-read")
async def mark_notification_as_read(
    recipient_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(get_current_user),
) -> dict:
    service = get_notification_service(session)
    recipient = await service.mark_as_read(recipient_id, actor.id)
    await get_audit_service(session).record_event(
        event_type="NOTIFICATION",
        module_name="notification",
        action_name="MARK_READ",
        summary="Notification ditandai sudah dibaca.",
        actor=actor,
        tenant_id=recipient.tenant_id,
        sppg_id=actor.active_sppg_id,
        entity_type="notification_recipient",
        entity_id=recipient.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"notification_id": str(recipient.notification_id)},
    )
    await session.commit()
    return success_response(
        code="NOTIFICATION_MARKED_READ",
        message="Notification berhasil ditandai sudah dibaca.",
        data=NotificationRecipientRead.model_validate(recipient),
        meta={"request_id": request.state.request_id},
    )
