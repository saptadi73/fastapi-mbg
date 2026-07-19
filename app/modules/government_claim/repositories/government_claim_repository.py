from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.government_claim.models.claim_adjustment import ClaimAdjustment
from app.modules.government_claim.models.claim_evidence import ClaimEvidence
from app.modules.government_claim.models.claim_payment import ClaimPayment
from app.modules.government_claim.models.claim_verification import ClaimVerification
from app.modules.government_claim.models.government_claim import GovernmentClaim
from app.modules.government_claim.models.government_claim_line import GovernmentClaimLine


class GovernmentClaimRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_claims(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[GovernmentClaim]:
        query = select(GovernmentClaim).order_by(GovernmentClaim.created_at.desc())
        if tenant_id is not None:
            query = query.where(GovernmentClaim.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(GovernmentClaim.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_claim_by_id(self, claim_id: UUID) -> GovernmentClaim | None:
        return await self.session.get(GovernmentClaim, claim_id)

    async def get_claim_by_id_and_scope(self, claim_id: UUID, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> GovernmentClaim | None:
        query = select(GovernmentClaim).where(GovernmentClaim.id == claim_id)
        if tenant_id is not None:
            query = query.where(GovernmentClaim.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(GovernmentClaim.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def count_by_tenant(self, tenant_id: UUID) -> int:
        result = await self.session.execute(select(func.count(GovernmentClaim.id)).where(GovernmentClaim.tenant_id == tenant_id))
        return int(result.scalar_one())

    async def add_claim(self, claim: GovernmentClaim) -> GovernmentClaim:
        self.session.add(claim)
        await self.session.flush()
        await self.session.refresh(claim)
        return claim

    async def add_line(self, line: GovernmentClaimLine) -> GovernmentClaimLine:
        self.session.add(line)
        await self.session.flush()
        await self.session.refresh(line)
        return line

    async def add_evidence(self, evidence: ClaimEvidence) -> ClaimEvidence:
        self.session.add(evidence)
        await self.session.flush()
        await self.session.refresh(evidence)
        return evidence

    async def add_verification(self, verification: ClaimVerification) -> ClaimVerification:
        self.session.add(verification)
        await self.session.flush()
        await self.session.refresh(verification)
        return verification

    async def add_adjustment(self, adjustment: ClaimAdjustment) -> ClaimAdjustment:
        self.session.add(adjustment)
        await self.session.flush()
        await self.session.refresh(adjustment)
        return adjustment

    async def add_payment(self, payment: ClaimPayment) -> ClaimPayment:
        self.session.add(payment)
        await self.session.flush()
        await self.session.refresh(payment)
        return payment

    async def list_lines(self, claim_id: UUID) -> list[GovernmentClaimLine]:
        result = await self.session.execute(
            select(GovernmentClaimLine).where(GovernmentClaimLine.claim_id == claim_id).order_by(GovernmentClaimLine.created_at)
        )
        return list(result.scalars().all())

    async def list_evidences(self, claim_id: UUID) -> list[ClaimEvidence]:
        result = await self.session.execute(
            select(ClaimEvidence).where(ClaimEvidence.claim_id == claim_id).order_by(ClaimEvidence.created_at)
        )
        return list(result.scalars().all())

    async def list_verifications(self, claim_id: UUID) -> list[ClaimVerification]:
        result = await self.session.execute(
            select(ClaimVerification).where(ClaimVerification.claim_id == claim_id).order_by(ClaimVerification.created_at)
        )
        return list(result.scalars().all())

    async def list_adjustments(self, claim_id: UUID) -> list[ClaimAdjustment]:
        result = await self.session.execute(
            select(ClaimAdjustment).where(ClaimAdjustment.claim_id == claim_id).order_by(ClaimAdjustment.created_at)
        )
        return list(result.scalars().all())

    async def list_payments(self, claim_id: UUID) -> list[ClaimPayment]:
        result = await self.session.execute(
            select(ClaimPayment).where(ClaimPayment.claim_id == claim_id).order_by(ClaimPayment.created_at)
        )
        return list(result.scalars().all())
