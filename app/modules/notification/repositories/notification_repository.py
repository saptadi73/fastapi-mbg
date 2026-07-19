from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notification.models.notification import Notification
from app.modules.notification.models.notification_delivery import NotificationDelivery
from app.modules.notification.models.notification_preference import NotificationPreference
from app.modules.notification.models.notification_recipient import NotificationRecipient
from app.modules.notification.models.notification_template import NotificationTemplate


class NotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_templates(self, tenant_id: UUID | None = None) -> list[NotificationTemplate]:
        query = select(NotificationTemplate).order_by(NotificationTemplate.name)
        if tenant_id is not None:
            query = query.where(NotificationTemplate.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_template_by_id(self, template_id: UUID) -> NotificationTemplate | None:
        return await self.session.get(NotificationTemplate, template_id)

    async def get_template_by_tenant_code(self, tenant_id: UUID, code: str) -> NotificationTemplate | None:
        result = await self.session.execute(
            select(NotificationTemplate).where(
                NotificationTemplate.tenant_id == tenant_id,
                NotificationTemplate.code == code,
            )
        )
        return result.scalar_one_or_none()

    async def add_template(self, template: NotificationTemplate) -> NotificationTemplate:
        self.session.add(template)
        await self.session.flush()
        await self.session.refresh(template)
        return template

    async def get_preference(self, tenant_id: UUID, user_id: UUID, channel: str) -> NotificationPreference | None:
        result = await self.session.execute(
            select(NotificationPreference).where(
                NotificationPreference.tenant_id == tenant_id,
                NotificationPreference.user_id == user_id,
                NotificationPreference.channel == channel,
            )
        )
        return result.scalar_one_or_none()

    async def list_preferences_by_user(self, tenant_id: UUID, user_id: UUID) -> list[NotificationPreference]:
        result = await self.session.execute(
            select(NotificationPreference)
            .where(
                NotificationPreference.tenant_id == tenant_id,
                NotificationPreference.user_id == user_id,
            )
            .order_by(NotificationPreference.channel)
        )
        return list(result.scalars().all())

    async def add_preference(self, preference: NotificationPreference) -> NotificationPreference:
        self.session.add(preference)
        await self.session.flush()
        await self.session.refresh(preference)
        return preference

    async def add_notification(self, notification: Notification) -> Notification:
        self.session.add(notification)
        await self.session.flush()
        await self.session.refresh(notification)
        return notification

    async def add_recipient(self, recipient: NotificationRecipient) -> NotificationRecipient:
        self.session.add(recipient)
        await self.session.flush()
        await self.session.refresh(recipient)
        return recipient

    async def add_delivery(self, delivery: NotificationDelivery) -> NotificationDelivery:
        self.session.add(delivery)
        await self.session.flush()
        await self.session.refresh(delivery)
        return delivery

    async def list_inbox(self, tenant_id: UUID, user_id: UUID, sppg_id: UUID | None = None) -> list[NotificationRecipient]:
        query = (
            select(NotificationRecipient)
            .join(Notification, Notification.id == NotificationRecipient.notification_id)
            .where(
                NotificationRecipient.tenant_id == tenant_id,
                NotificationRecipient.user_id == user_id,
            )
            .order_by(Notification.created_at.desc(), NotificationRecipient.created_at.desc())
        )
        if sppg_id is not None:
            query = query.where(Notification.sppg_id.in_([sppg_id, None]))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_recipient_by_id(self, recipient_id: UUID) -> NotificationRecipient | None:
        return await self.session.get(NotificationRecipient, recipient_id)

    async def get_notification_by_id(self, notification_id: UUID) -> Notification | None:
        return await self.session.get(Notification, notification_id)

    async def list_recipients(self, notification_id: UUID) -> list[NotificationRecipient]:
        result = await self.session.execute(
            select(NotificationRecipient)
            .where(NotificationRecipient.notification_id == notification_id)
            .order_by(NotificationRecipient.created_at)
        )
        return list(result.scalars().all())

    async def list_deliveries(self, notification_id: UUID) -> list[NotificationDelivery]:
        result = await self.session.execute(
            select(NotificationDelivery)
            .where(NotificationDelivery.notification_id == notification_id)
            .order_by(NotificationDelivery.attempt_no, NotificationDelivery.created_at)
        )
        return list(result.scalars().all())
