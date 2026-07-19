from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.accounting.models.journal_line import JournalLine


class JournalLineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_journal_entry(self, journal_entry_id: UUID) -> list[JournalLine]:
        result = await self.session.execute(
            select(JournalLine).where(JournalLine.journal_entry_id == journal_entry_id).order_by(JournalLine.created_at)
        )
        return list(result.scalars().all())

    async def add(self, journal_line: JournalLine) -> JournalLine:
        self.session.add(journal_line)
        await self.session.flush()
        await self.session.refresh(journal_line)
        return journal_line
