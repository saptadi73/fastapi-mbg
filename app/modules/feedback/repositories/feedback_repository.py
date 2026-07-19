from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.feedback.models.complaint import Complaint
from app.modules.feedback.models.feedback_item import FeedbackItem
from app.modules.feedback.models.feedback_submission import FeedbackSubmission
from app.modules.feedback.models.service_quality_score import ServiceQualityScore


class FeedbackRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_submissions(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[FeedbackSubmission]:
        query = select(FeedbackSubmission).order_by(FeedbackSubmission.feedback_date.desc(), FeedbackSubmission.created_at.desc())
        if tenant_id is not None:
            query = query.where(FeedbackSubmission.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(FeedbackSubmission.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_submission_by_id(self, submission_id: UUID) -> FeedbackSubmission | None:
        return await self.session.get(FeedbackSubmission, submission_id)

    async def get_submission_by_id_and_scope(
        self,
        submission_id: UUID,
        tenant_id: UUID | None = None,
        sppg_id: UUID | None = None,
    ) -> FeedbackSubmission | None:
        query = select(FeedbackSubmission).where(FeedbackSubmission.id == submission_id)
        if tenant_id is not None:
            query = query.where(FeedbackSubmission.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(FeedbackSubmission.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def add_submission(self, submission: FeedbackSubmission) -> FeedbackSubmission:
        self.session.add(submission)
        await self.session.flush()
        await self.session.refresh(submission)
        return submission

    async def list_items(self, submission_id: UUID) -> list[FeedbackItem]:
        result = await self.session.execute(
            select(FeedbackItem)
            .where(FeedbackItem.feedback_submission_id == submission_id)
            .order_by(FeedbackItem.created_at.asc())
        )
        return list(result.scalars().all())

    async def add_item(self, item: FeedbackItem) -> FeedbackItem:
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def list_complaints(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[Complaint]:
        query = select(Complaint).order_by(Complaint.complaint_date.desc(), Complaint.created_at.desc())
        if tenant_id is not None:
            query = query.where(Complaint.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(Complaint.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def add_complaint(self, complaint: Complaint) -> Complaint:
        self.session.add(complaint)
        await self.session.flush()
        await self.session.refresh(complaint)
        return complaint

    async def list_scores(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[ServiceQualityScore]:
        query = select(ServiceQualityScore).order_by(ServiceQualityScore.score_date.desc(), ServiceQualityScore.created_at.desc())
        if tenant_id is not None:
            query = query.where(ServiceQualityScore.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(ServiceQualityScore.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_score_by_scope_date(self, tenant_id: UUID, sppg_id: UUID, score_date) -> ServiceQualityScore | None:
        result = await self.session.execute(
            select(ServiceQualityScore).where(
                ServiceQualityScore.tenant_id == tenant_id,
                ServiceQualityScore.sppg_id == sppg_id,
                ServiceQualityScore.score_date == score_date,
            )
        )
        return result.scalar_one_or_none()

    async def add_score(self, score: ServiceQualityScore) -> ServiceQualityScore:
        self.session.add(score)
        await self.session.flush()
        await self.session.refresh(score)
        return score
