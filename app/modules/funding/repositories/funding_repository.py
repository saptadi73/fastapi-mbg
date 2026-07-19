from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.funding.models.funding_agreement import FundingAgreement
from app.modules.funding.models.funding_disbursement import FundingDisbursement
from app.modules.funding.models.funding_repayment import FundingRepayment
from app.modules.funding.models.funding_source import FundingSource


class FundingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_sources(self, tenant_id: UUID | None = None) -> list[FundingSource]:
        query = select(FundingSource).order_by(FundingSource.name)
        if tenant_id is not None:
            query = query.where(FundingSource.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_source_by_id(self, source_id: UUID) -> FundingSource | None:
        return await self.session.get(FundingSource, source_id)

    async def get_source_by_tenant_code(self, tenant_id: UUID, code: str) -> FundingSource | None:
        result = await self.session.execute(
            select(FundingSource).where(FundingSource.tenant_id == tenant_id, FundingSource.code == code)
        )
        return result.scalar_one_or_none()

    async def add_source(self, source: FundingSource) -> FundingSource:
        self.session.add(source)
        await self.session.flush()
        await self.session.refresh(source)
        return source

    async def list_agreements(self, tenant_id: UUID | None = None) -> list[FundingAgreement]:
        query = select(FundingAgreement).order_by(FundingAgreement.created_at.desc())
        if tenant_id is not None:
            query = query.where(FundingAgreement.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_agreement_by_id(self, agreement_id: UUID) -> FundingAgreement | None:
        return await self.session.get(FundingAgreement, agreement_id)

    async def add_agreement(self, agreement: FundingAgreement) -> FundingAgreement:
        self.session.add(agreement)
        await self.session.flush()
        await self.session.refresh(agreement)
        return agreement

    async def list_disbursements(self, tenant_id: UUID | None = None) -> list[FundingDisbursement]:
        query = select(FundingDisbursement).order_by(FundingDisbursement.disbursement_date.desc(), FundingDisbursement.created_at.desc())
        if tenant_id is not None:
            query = query.where(FundingDisbursement.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_disbursements_by_agreement(self, agreement_id: UUID) -> list[FundingDisbursement]:
        result = await self.session.execute(
            select(FundingDisbursement)
            .where(FundingDisbursement.agreement_id == agreement_id)
            .order_by(FundingDisbursement.disbursement_date.desc(), FundingDisbursement.created_at.desc())
        )
        return list(result.scalars().all())

    async def add_disbursement(self, disbursement: FundingDisbursement) -> FundingDisbursement:
        self.session.add(disbursement)
        await self.session.flush()
        await self.session.refresh(disbursement)
        return disbursement

    async def list_repayments(self, tenant_id: UUID | None = None) -> list[FundingRepayment]:
        query = select(FundingRepayment).order_by(FundingRepayment.repayment_date.desc(), FundingRepayment.created_at.desc())
        if tenant_id is not None:
            query = query.where(FundingRepayment.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_repayments_by_agreement(self, agreement_id: UUID) -> list[FundingRepayment]:
        result = await self.session.execute(
            select(FundingRepayment)
            .where(FundingRepayment.agreement_id == agreement_id)
            .order_by(FundingRepayment.repayment_date.desc(), FundingRepayment.created_at.desc())
        )
        return list(result.scalars().all())

    async def add_repayment(self, repayment: FundingRepayment) -> FundingRepayment:
        self.session.add(repayment)
        await self.session.flush()
        await self.session.refresh(repayment)
        return repayment

    async def count_agreements_by_tenant(self, tenant_id: UUID) -> int:
        result = await self.session.execute(select(func.count(FundingAgreement.id)).where(FundingAgreement.tenant_id == tenant_id))
        return int(result.scalar_one() or 0)
