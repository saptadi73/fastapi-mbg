from uuid import UUID

from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.core.tenancy.write_scope import enforce_sppg_write_scope, enforce_tenant_write_scope
from app.modules.ai.models.ai_daily_summary import AIDailySummary
from app.modules.ai.models.ai_forecast import AIForecast
from app.modules.ai.models.ai_recommendation import AIRecommendation
from app.modules.ai.repositories.ai_repository import AIRepository
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, ConflictException, NotFoundException


class AIService:
    def __init__(
        self,
        repository: AIRepository,
        tenant_repository: TenantRepository,
        sppg_repository: SppgRepository,
    ) -> None:
        self.repository = repository
        self.tenant_repository = tenant_repository
        self.sppg_repository = sppg_repository

    def _parse_scope_uuid(self, value: str | None, code: str, message: str) -> UUID | None:
        if value is None:
            return None
        try:
            return UUID(value)
        except ValueError as exc:
            raise BadRequestException(code=code, message=message) from exc

    def _get_scope(self) -> tuple[UUID | None, UUID | None]:
        return (
            self._parse_scope_uuid(get_current_tenant(), "INVALID_TENANT_CONTEXT", "Header X-Tenant-ID tidak valid."),
            self._parse_scope_uuid(get_current_sppg(), "INVALID_SPPG_CONTEXT", "Header X-SPPG-ID tidak valid."),
        )

    async def _validate_scope_entities(self, tenant_id: UUID, sppg_id: UUID | None) -> None:
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant AI tidak ditemukan.")
        if sppg_id is not None:
            sppg = await self.sppg_repository.get_by_id(sppg_id)
            if sppg is None or sppg.tenant_id != tenant_id:
                raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG AI tidak ditemukan.")

    async def list_forecasts(self) -> list[AIForecast]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_forecasts(tenant_id=tenant_id, sppg_id=sppg_id)

    async def get_forecast(self, forecast_id: UUID) -> AIForecast:
        tenant_id, sppg_id = self._get_scope()
        forecast = await self.repository.get_forecast_by_id_and_scope(forecast_id, tenant_id=tenant_id, sppg_id=sppg_id)
        if forecast is None:
            raise NotFoundException(code="AI_FORECAST_NOT_FOUND", message="AI forecast tidak ditemukan.")
        return forecast

    async def create_forecast(self, payload) -> AIForecast:
        tenant_id = UUID(payload.tenant_id)
        sppg_id = UUID(payload.sppg_id) if payload.sppg_id else None
        enforce_tenant_write_scope(tenant_id)
        if sppg_id is not None:
            enforce_sppg_write_scope(sppg_id)
        await self._validate_scope_entities(tenant_id, sppg_id)
        if payload.target_date < payload.forecast_date:
            raise BadRequestException(code="INVALID_AI_FORECAST_DATE_RANGE", message="Tanggal target forecast tidak valid.")
        if payload.confidence_score is not None and (payload.confidence_score < 0 or payload.confidence_score > 1):
            raise BadRequestException(code="INVALID_AI_CONFIDENCE_SCORE", message="Confidence score AI harus antara 0 dan 1.")
        return await self.repository.add_forecast(
            AIForecast(
                tenant_id=tenant_id,
                sppg_id=sppg_id,
                forecast_type=payload.forecast_type,
                forecast_date=payload.forecast_date,
                target_date=payload.target_date,
                model_name=payload.model_name,
                input_snapshot=payload.input_snapshot,
                forecast_payload=payload.forecast_payload,
                confidence_score=payload.confidence_score,
                status=payload.status,
                notes=payload.notes,
            )
        )

    async def list_recommendations(self) -> list[AIRecommendation]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_recommendations(tenant_id=tenant_id, sppg_id=sppg_id)

    async def get_recommendation(self, recommendation_id: UUID) -> AIRecommendation:
        tenant_id, sppg_id = self._get_scope()
        recommendation = await self.repository.get_recommendation_by_id_and_scope(
            recommendation_id,
            tenant_id=tenant_id,
            sppg_id=sppg_id,
        )
        if recommendation is None:
            raise NotFoundException(code="AI_RECOMMENDATION_NOT_FOUND", message="AI recommendation tidak ditemukan.")
        return recommendation

    async def create_recommendation(self, payload) -> AIRecommendation:
        tenant_id = UUID(payload.tenant_id)
        sppg_id = UUID(payload.sppg_id) if payload.sppg_id else None
        reference_id = UUID(payload.reference_id) if payload.reference_id else None
        enforce_tenant_write_scope(tenant_id)
        if sppg_id is not None:
            enforce_sppg_write_scope(sppg_id)
        await self._validate_scope_entities(tenant_id, sppg_id)
        return await self.repository.add_recommendation(
            AIRecommendation(
                tenant_id=tenant_id,
                sppg_id=sppg_id,
                recommendation_date=payload.recommendation_date,
                recommendation_type=payload.recommendation_type,
                reference_type=payload.reference_type,
                reference_id=reference_id,
                title=payload.title,
                summary_text=payload.summary_text,
                recommendation_payload=payload.recommendation_payload,
                priority=payload.priority,
                status=payload.status,
                notes=payload.notes,
            )
        )

    async def list_summaries(self) -> list[AIDailySummary]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_summaries(tenant_id=tenant_id, sppg_id=sppg_id)

    async def get_summary(self, summary_id: UUID) -> AIDailySummary:
        tenant_id, sppg_id = self._get_scope()
        summary = await self.repository.get_summary_by_id_and_scope(summary_id, tenant_id=tenant_id, sppg_id=sppg_id)
        if summary is None:
            raise NotFoundException(code="AI_DAILY_SUMMARY_NOT_FOUND", message="AI daily summary tidak ditemukan.")
        return summary

    async def create_summary(self, payload) -> AIDailySummary:
        tenant_id = UUID(payload.tenant_id)
        sppg_id = UUID(payload.sppg_id) if payload.sppg_id else None
        enforce_tenant_write_scope(tenant_id)
        if sppg_id is not None:
            enforce_sppg_write_scope(sppg_id)
        await self._validate_scope_entities(tenant_id, sppg_id)
        if await self.repository.get_summary_by_scope_date(tenant_id, sppg_id, payload.summary_date) is not None:
            raise ConflictException(code="AI_DAILY_SUMMARY_ALREADY_EXISTS", message="AI daily summary pada tanggal ini sudah ada.")
        if payload.anomaly_count < 0 or payload.recommendation_count < 0:
            raise BadRequestException(code="INVALID_AI_SUMMARY_COUNT", message="Jumlah anomaly atau recommendation tidak valid.")
        return await self.repository.add_summary(
            AIDailySummary(
                tenant_id=tenant_id,
                sppg_id=sppg_id,
                summary_date=payload.summary_date,
                summary_type=payload.summary_type,
                headline=payload.headline,
                summary_text=payload.summary_text,
                metrics_payload=payload.metrics_payload,
                anomaly_count=payload.anomaly_count,
                recommendation_count=payload.recommendation_count,
                status=payload.status,
                notes=payload.notes,
            )
        )

    async def overview(self) -> dict:
        tenant_id, sppg_id = self._get_scope()
        forecasts = await self.repository.list_forecasts(tenant_id=tenant_id, sppg_id=sppg_id)
        recommendations = await self.repository.list_recommendations(tenant_id=tenant_id, sppg_id=sppg_id)
        summaries = await self.repository.list_summaries(tenant_id=tenant_id, sppg_id=sppg_id)
        return {
            "totals": {
                "forecasts": len(forecasts),
                "recommendations": len(recommendations),
                "daily_summaries": len(summaries),
            },
            "breakdown": {
                "open_recommendations": len([item for item in recommendations if item.status == "OPEN"]),
                "high_priority_recommendations": len([item for item in recommendations if item.priority == "HIGH"]),
                "generated_forecasts": len([item for item in forecasts if item.status == "GENERATED"]),
                "anomaly_flags": sum(item.anomaly_count for item in summaries),
            },
        }
