from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.accounting.models.journal_entry import JournalEntry


class JournalEntryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[JournalEntry]:
        result = await self.session.execute(select(JournalEntry).order_by(JournalEntry.created_at.desc()))
        return list(result.scalars().all())

    async def get_by_id(self, journal_entry_id: UUID) -> JournalEntry | None:
        return await self.session.get(JournalEntry, journal_entry_id)

    async def count_by_tenant(self, tenant_id: UUID) -> int:
        result = await self.session.execute(select(func.count(JournalEntry.id)).where(JournalEntry.tenant_id == tenant_id))
        return int(result.scalar_one())

    async def add(self, journal_entry: JournalEntry) -> JournalEntry:
        self.session.add(journal_entry)
        await self.session.flush()
        await self.session.refresh(journal_entry)
        return journal_entry
