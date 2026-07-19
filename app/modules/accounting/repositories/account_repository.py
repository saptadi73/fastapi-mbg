from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.accounting.models.account import Account


class AccountRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[Account]:
        result = await self.session.execute(select(Account).order_by(Account.code))
        return list(result.scalars().all())

    async def get_by_id(self, account_id: UUID) -> Account | None:
        return await self.session.get(Account, account_id)

    async def get_by_tenant_and_code(self, tenant_id: UUID, code: str) -> Account | None:
        result = await self.session.execute(select(Account).where(Account.tenant_id == tenant_id, Account.code == code))
        return result.scalar_one_or_none()

    async def add(self, account: Account) -> Account:
        self.session.add(account)
        await self.session.flush()
        await self.session.refresh(account)
        return account
