from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.models.ai_daily_summary import AIDailySummary
from app.modules.ai.models.ai_forecast import AIForecast
from app.modules.ai.models.ai_recommendation import AIRecommendation


class AIRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_forecasts(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[AIForecast]:
        query = select(AIForecast).order_by(AIForecast.target_date.desc(), AIForecast.created_at.desc())
        if tenant_id is not None:
            query = query.where(AIForecast.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(AIForecast.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_forecast_by_id(self, forecast_id: UUID) -> AIForecast | None:
        return await self.session.get(AIForecast, forecast_id)

    async def get_forecast_by_id_and_scope(
        self,
        forecast_id: UUID,
        tenant_id: UUID | None = None,
        sppg_id: UUID | None = None,
    ) -> AIForecast | None:
        query = select(AIForecast).where(AIForecast.id == forecast_id)
        if tenant_id is not None:
            query = query.where(AIForecast.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(AIForecast.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def add_forecast(self, forecast: AIForecast) -> AIForecast:
        self.session.add(forecast)
        await self.session.flush()
        await self.session.refresh(forecast)
        return forecast

    async def list_recommendations(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[AIRecommendation]:
        query = select(AIRecommendation).order_by(AIRecommendation.recommendation_date.desc(), AIRecommendation.created_at.desc())
        if tenant_id is not None:
            query = query.where(AIRecommendation.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(AIRecommendation.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_recommendation_by_id(self, recommendation_id: UUID) -> AIRecommendation | None:
        return await self.session.get(AIRecommendation, recommendation_id)

    async def get_recommendation_by_id_and_scope(
        self,
        recommendation_id: UUID,
        tenant_id: UUID | None = None,
        sppg_id: UUID | None = None,
    ) -> AIRecommendation | None:
        query = select(AIRecommendation).where(AIRecommendation.id == recommendation_id)
        if tenant_id is not None:
            query = query.where(AIRecommendation.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(AIRecommendation.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def add_recommendation(self, recommendation: AIRecommendation) -> AIRecommendation:
        self.session.add(recommendation)
        await self.session.flush()
        await self.session.refresh(recommendation)
        return recommendation

    async def list_summaries(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[AIDailySummary]:
        query = select(AIDailySummary).order_by(AIDailySummary.summary_date.desc(), AIDailySummary.created_at.desc())
        if tenant_id is not None:
            query = query.where(AIDailySummary.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(AIDailySummary.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_summary_by_id(self, summary_id: UUID) -> AIDailySummary | None:
        return await self.session.get(AIDailySummary, summary_id)

    async def get_summary_by_id_and_scope(
        self,
        summary_id: UUID,
        tenant_id: UUID | None = None,
        sppg_id: UUID | None = None,
    ) -> AIDailySummary | None:
        query = select(AIDailySummary).where(AIDailySummary.id == summary_id)
        if tenant_id is not None:
            query = query.where(AIDailySummary.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(AIDailySummary.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_summary_by_scope_date(self, tenant_id: UUID, sppg_id: UUID | None, summary_date) -> AIDailySummary | None:
        query = select(AIDailySummary).where(AIDailySummary.tenant_id == tenant_id, AIDailySummary.summary_date == summary_date)
        if sppg_id is None:
            query = query.where(AIDailySummary.sppg_id.is_(None))
        else:
            query = query.where(AIDailySummary.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def add_summary(self, summary: AIDailySummary) -> AIDailySummary:
        self.session.add(summary)
        await self.session.flush()
        await self.session.refresh(summary)
        return summary
