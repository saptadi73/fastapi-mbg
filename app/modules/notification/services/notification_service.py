from datetime import datetime, timezone
from uuid import UUID

from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.core.tenancy.write_scope import enforce_sppg_write_scope, enforce_tenant_write_scope
from app.modules.identity.repositories.user_repository import UserRepository
from app.modules.notification.models.notification import Notification
from app.modules.notification.models.notification_delivery import NotificationDelivery
from app.modules.notification.models.notification_preference import NotificationPreference
from app.modules.notification.models.notification_recipient import NotificationRecipient
from app.modules.notification.models.notification_template import NotificationTemplate
from app.modules.notification.repositories.notification_repository import NotificationRepository
from app.modules.notification.schemas.notification_schema import (
    NotificationDispatchCreate,
    NotificationPreferenceUpsert,
    NotificationTemplateCreate,
)
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, ConflictException, NotFoundException


class NotificationService:
    def __init__(
        self,
        repository: NotificationRepository,
        tenant_repository: TenantRepository,
        sppg_repository: SppgRepository,
        user_repository: UserRepository,
    ) -> None:
        self.repository = repository
        self.tenant_repository = tenant_repository
        self.sppg_repository = sppg_repository
        self.user_repository = user_repository

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

    async def list_templates(self) -> list[NotificationTemplate]:
        tenant_id, _ = self._get_scope()
        return await self.repository.list_templates(tenant_id=tenant_id)

    async def create_template(self, payload: NotificationTemplateCreate) -> NotificationTemplate:
        tenant_id = UUID(payload.tenant_id)
        enforce_tenant_write_scope(tenant_id)
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant notification template tidak ditemukan.")
        existing = await self.repository.get_template_by_tenant_code(tenant_id, payload.code)
        if existing is not None:
            raise ConflictException(
                code="NOTIFICATION_TEMPLATE_CODE_ALREADY_EXISTS",
                message="Kode notification template sudah digunakan.",
            )
        return await self.repository.add_template(
            NotificationTemplate(
                tenant_id=tenant_id,
                code=payload.code,
                name=payload.name,
                channel=payload.channel,
                subject_template=payload.subject_template,
                body_template=payload.body_template,
                variables_json=payload.variables_json,
                is_active=payload.is_active,
            )
        )

    async def list_my_preferences(self, user_id: UUID) -> list[NotificationPreference]:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException(code="USER_NOT_FOUND", message="User notifikasi tidak ditemukan.")
        return await self.repository.list_preferences_by_user(user.tenant_id, user.id)

    async def upsert_my_preference(self, user_id: UUID, payload: NotificationPreferenceUpsert) -> NotificationPreference:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException(code="USER_NOT_FOUND", message="User notifikasi tidak ditemukan.")
        preference = await self.repository.get_preference(user.tenant_id, user.id, payload.channel)
        if preference is None:
            return await self.repository.add_preference(
                NotificationPreference(
                    tenant_id=user.tenant_id,
                    user_id=user.id,
                    channel=payload.channel,
                    is_enabled=payload.is_enabled,
                    quiet_hours_json=payload.quiet_hours_json,
                    config_json=payload.config_json,
                )
            )
        preference.is_enabled = payload.is_enabled
        preference.quiet_hours_json = payload.quiet_hours_json
        preference.config_json = payload.config_json
        return preference

    async def dispatch_notification(self, payload: NotificationDispatchCreate) -> dict:
        tenant_id = UUID(payload.tenant_id)
        sppg_id = UUID(payload.sppg_id) if payload.sppg_id else None
        enforce_tenant_write_scope(tenant_id)
        if sppg_id is not None:
            enforce_sppg_write_scope(sppg_id)
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant notifikasi tidak ditemukan.")
        if sppg_id is not None:
            sppg = await self.sppg_repository.get_by_id(sppg_id)
            if sppg is None or sppg.tenant_id != tenant_id:
                raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG notifikasi tidak ditemukan.")
        if not payload.recipients:
            raise BadRequestException(code="NOTIFICATION_RECIPIENT_REQUIRED", message="Minimal satu recipient wajib diisi.")

        template_id = UUID(payload.template_id) if payload.template_id else None
        template = None
        if template_id is not None:
            template = await self.repository.get_template_by_id(template_id)
            if template is None or template.tenant_id != tenant_id:
                raise NotFoundException(code="NOTIFICATION_TEMPLATE_NOT_FOUND", message="Notification template tidak ditemukan.")

        source_entity_id = UUID(payload.source_entity_id) if payload.source_entity_id else None
        notification = await self.repository.add_notification(
            Notification(
                tenant_id=tenant_id,
                sppg_id=sppg_id,
                template_id=template.id if template else None,
                source_module=payload.source_module,
                source_entity_type=payload.source_entity_type,
                source_entity_id=source_entity_id,
                title=payload.title,
                message=payload.message,
                priority=payload.priority,
                status="QUEUED",
                scheduled_at=payload.scheduled_at,
                sent_at=None,
            )
        )

        recipients: list[NotificationRecipient] = []
        deliveries: list[NotificationDelivery] = []
        for recipient_payload in payload.recipients:
            recipient_user_id = UUID(recipient_payload.user_id) if recipient_payload.user_id else None
            recipient_address = recipient_payload.recipient_address
            if recipient_user_id is not None:
                user = await self.user_repository.get_by_id_and_tenant(recipient_user_id, tenant_id)
                if user is None:
                    raise NotFoundException(code="USER_NOT_FOUND", message="Recipient user tidak ditemukan.")
                preference = await self.repository.get_preference(tenant_id, user.id, recipient_payload.channel)
                if preference is not None and preference.is_enabled is False:
                    raise BadRequestException(
                        code="NOTIFICATION_CHANNEL_DISABLED",
                        message="Channel notifikasi untuk user ini sedang nonaktif.",
                    )
                if recipient_address is None and recipient_payload.channel == "EMAIL":
                    recipient_address = user.email
            if recipient_user_id is None and not recipient_address:
                raise BadRequestException(
                    code="NOTIFICATION_RECIPIENT_ADDRESS_REQUIRED",
                    message="recipient_address wajib diisi bila user_id tidak ada.",
                )

            recipient = await self.repository.add_recipient(
                NotificationRecipient(
                    tenant_id=tenant_id,
                    notification_id=notification.id,
                    user_id=recipient_user_id,
                    channel=recipient_payload.channel,
                    recipient_address=recipient_address,
                    delivery_status="QUEUED",
                    is_read=False,
                    is_primary=True,
                    read_at=None,
                )
            )
            recipients.append(recipient)
            delivery = await self.repository.add_delivery(
                NotificationDelivery(
                    tenant_id=tenant_id,
                    notification_id=notification.id,
                    recipient_id=recipient.id,
                    channel=recipient.channel,
                    provider_name="INTERNAL_QUEUE",
                    provider_message_id=None,
                    attempt_no=1,
                    status="QUEUED",
                    delivered_at=payload.scheduled_at if payload.scheduled_at is not None else datetime.now(timezone.utc),
                    failure_reason=None,
                    payload_json={"title": payload.title, "message": payload.message},
                    response_json={},
                )
            )
            deliveries.append(delivery)

        notification.status = "SENT" if payload.scheduled_at is None else "QUEUED"
        if payload.scheduled_at is None:
            notification.sent_at = datetime.now(timezone.utc)
            for recipient in recipients:
                recipient.delivery_status = "SENT"
            for delivery in deliveries:
                delivery.status = "SENT"

        return {
            "notification": notification,
            "recipients": recipients,
            "deliveries": deliveries,
        }

    async def list_my_inbox(self, user_id: UUID) -> list[dict]:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException(code="USER_NOT_FOUND", message="User notifikasi tidak ditemukan.")
        _, sppg_scope = self._get_scope()
        recipients = await self.repository.list_inbox(user.tenant_id, user.id, sppg_id=sppg_scope)
        items: list[dict] = []
        for recipient in recipients:
            notification = await self.repository.get_notification_by_id(recipient.notification_id)
            if notification is None:
                continue
            items.append({"recipient": recipient, "notification": notification})
        return items

    async def mark_as_read(self, recipient_id: UUID, user_id: UUID) -> NotificationRecipient:
        recipient = await self.repository.get_recipient_by_id(recipient_id)
        if recipient is None or recipient.user_id != user_id:
            raise NotFoundException(code="NOTIFICATION_RECIPIENT_NOT_FOUND", message="Notification inbox item tidak ditemukan.")
        recipient.is_read = True
        recipient.read_at = datetime.now(timezone.utc)
        return recipient

    async def get_notification_bundle(self, notification_id: UUID) -> dict:
        notification = await self.repository.get_notification_by_id(notification_id)
        if notification is None:
            raise NotFoundException(code="NOTIFICATION_NOT_FOUND", message="Notification tidak ditemukan.")
        tenant_scope, sppg_scope = self._get_scope()
        if tenant_scope is not None and notification.tenant_id != tenant_scope:
            raise NotFoundException(code="NOTIFICATION_NOT_FOUND", message="Notification tidak ditemukan.")
        if sppg_scope is not None and notification.sppg_id not in {None, sppg_scope}:
            raise NotFoundException(code="NOTIFICATION_NOT_FOUND", message="Notification tidak ditemukan.")
        return {
            "notification": notification,
            "recipients": await self.repository.list_recipients(notification.id),
            "deliveries": await self.repository.list_deliveries(notification.id),
        }
