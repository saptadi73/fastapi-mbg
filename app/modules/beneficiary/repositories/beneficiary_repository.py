from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.beneficiary.models.beneficiary import Beneficiary


class BeneficiaryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[Beneficiary]:
        result = await self.session.execute(select(Beneficiary).order_by(Beneficiary.external_reference))
        return list(result.scalars().all())

    async def get_by_id(self, beneficiary_id: UUID) -> Beneficiary | None:
        return await self.session.get(Beneficiary, beneficiary_id)

    async def get_by_tenant_and_external_reference(
        self,
        tenant_id: UUID,
        external_reference: str,
    ) -> Beneficiary | None:
        result = await self.session.execute(
            select(Beneficiary).where(
                Beneficiary.tenant_id == tenant_id,
                Beneficiary.external_reference == external_reference,
            )
        )
        return result.scalar_one_or_none()

    async def add(self, beneficiary: Beneficiary) -> Beneficiary:
        self.session.add(beneficiary)
        await self.session.flush()
        await self.session.refresh(beneficiary)
        return beneficiary
