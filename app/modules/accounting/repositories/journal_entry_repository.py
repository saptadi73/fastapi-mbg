from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.accounting.models.journal_entry import JournalEntry


class JournalEntryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self, tenant_id: UUID | None = None) -> list[JournalEntry]:
        query = select(JournalEntry).order_by(JournalEntry.created_at.desc())
        if tenant_id is not None:
            query = query.where(JournalEntry.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, journal_entry_id: UUID) -> JournalEntry | None:
        return await self.session.get(JournalEntry, journal_entry_id)

    async def get_by_id_and_tenant(self, journal_entry_id: UUID, tenant_id: UUID) -> JournalEntry | None:
        result = await self.session.execute(
            select(JournalEntry).where(JournalEntry.id == journal_entry_id, JournalEntry.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def count_by_tenant(self, tenant_id: UUID) -> int:
        result = await self.session.execute(select(func.count(JournalEntry.id)).where(JournalEntry.tenant_id == tenant_id))
        return int(result.scalar_one())

    async def add(self, journal_entry: JournalEntry) -> JournalEntry:
        self.session.add(journal_entry)
        await self.session.flush()
        await self.session.refresh(journal_entry)
        return journal_entry
