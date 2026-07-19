from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.settings import Settings
from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.core.tenancy.write_scope import enforce_sppg_write_scope, enforce_tenant_write_scope
from app.integrations.ai import GoogleAIMultimodalClient, OpenAINL2SQLClient
from app.modules.ai.models.ai_daily_summary import AIDailySummary
from app.modules.ai.models.ai_forecast import AIForecast
from app.modules.ai.models.ai_recommendation import AIRecommendation
from app.modules.ai.repositories.ai_repository import AIRepository
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, ConflictException, NotFoundException, ServiceUnavailableException


class AIService:
    def __init__(
        self,
        session: AsyncSession,
        repository: AIRepository,
        tenant_repository: TenantRepository,
        sppg_repository: SppgRepository,
        settings: Settings,
        openai_nl2sql_client: OpenAINL2SQLClient,
        google_ai_client: GoogleAIMultimodalClient,
    ) -> None:
        self.session = session
        self.repository = repository
        self.tenant_repository = tenant_repository
        self.sppg_repository = sppg_repository
        self.settings = settings
        self.openai_nl2sql_client = openai_nl2sql_client
        self.google_ai_client = google_ai_client

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

    def provider_status(self) -> dict:
        return {
            "providers": {
                "openai_nl2sql": {
                    "enabled": self.settings.openai_enabled,
                    "configured": self.openai_nl2sql_client.is_configured(),
                    "base_url": self.settings.openai_base_url,
                    "model": self.settings.openai_nl2sql_model,
                    "allow_execution": self.settings.openai_nl2sql_allow_execution,
                },
                "google_ai_media": {
                    "enabled": self.settings.google_ai_enabled,
                    "configured": self.google_ai_client.is_configured(),
                    "base_url": self.settings.google_ai_base_url,
                    "model": self.settings.google_ai_media_model,
                    "max_download_mb": self.settings.google_ai_media_max_download_mb,
                },
            }
        }

    async def generate_nl2sql(self, payload) -> dict:
        tenant_id, _ = self._get_scope()
        if tenant_id is not None:
            await self._validate_scope_entities(tenant_id, None)
        schema_context = payload.schema_context
        if payload.auto_schema_context or not schema_context:
            schema_context = await self._build_schema_context()
        max_rows = payload.max_rows or self.settings.openai_nl2sql_max_rows
        translated = await self.openai_nl2sql_client.translate_to_sql(
            question=payload.question,
            schema_context=schema_context,
            dialect=payload.dialect,
            max_rows=max_rows,
        )
        sql = translated["sql"].strip()
        executed = False
        rows: list[dict] = []
        if payload.execute_sql:
            if not self.settings.openai_nl2sql_allow_execution:
                raise ServiceUnavailableException(
                    code="OPENAI_NL2SQL_EXECUTION_DISABLED",
                    message="Eksekusi NL2SQL dinonaktifkan pada konfigurasi .env.",
                )
            self._validate_read_only_sql(sql)
            rows = await self._execute_read_only_sql(sql, max_rows)
            executed = True
        return {
            "provider": "openai",
            "model": self.settings.openai_nl2sql_model,
            "sql": sql,
            "explanation": translated.get("explanation"),
            "assumptions": translated.get("assumptions"),
            "safety_notes": translated.get("safety_notes"),
            "executed": executed,
            "rows": rows,
            "row_count": len(rows),
        }

    async def analyze_image(self, payload) -> dict:
        self._validate_media_mime(payload.mime_type, allowed_prefix="image/")
        return await self.google_ai_client.analyze_media(
            prompt=payload.prompt,
            mime_type=payload.mime_type,
            source_url=payload.source_url,
            base64_data=payload.base64_data,
        )

    async def analyze_video(self, payload) -> dict:
        self._validate_media_mime(payload.mime_type, allowed_prefix="video/")
        return await self.google_ai_client.analyze_media(
            prompt=payload.prompt,
            mime_type=payload.mime_type,
            source_url=payload.source_url,
            base64_data=payload.base64_data,
        )

    async def _build_schema_context(self) -> str:
        query = text(
            """
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
            """
        )
        result = await self.session.execute(query)
        grouped: dict[str, list[str]] = {}
        for row in result:
            grouped.setdefault(row.table_name, []).append(f"{row.column_name}:{row.data_type}")
        return "\n".join(f"{table}({', '.join(columns)})" for table, columns in grouped.items())

    def _validate_read_only_sql(self, sql: str) -> None:
        normalized = " ".join(sql.strip().lower().split())
        if not normalized.startswith(("select", "with")):
            raise BadRequestException(code="NL2SQL_ONLY_SELECT_ALLOWED", message="Hanya query SELECT/CTE yang diizinkan.")
        forbidden = [" insert ", " update ", " delete ", " drop ", " alter ", " truncate ", " create ", " grant ", " revoke ", " copy "]
        wrapped = f" {normalized} "
        if any(keyword in wrapped for keyword in forbidden):
            raise BadRequestException(code="NL2SQL_UNSAFE_QUERY", message="Query NL2SQL mengandung perintah yang tidak aman.")
        if ";" in normalized.rstrip(";"):
            raise BadRequestException(code="NL2SQL_MULTISTATEMENT_FORBIDDEN", message="Multi-statement SQL tidak diizinkan.")

    async def _execute_read_only_sql(self, sql: str, max_rows: int) -> list[dict]:
        statement = sql.rstrip().rstrip(";")
        lowered = statement.lower()
        if " limit " not in lowered:
            statement = f"{statement} LIMIT {int(max_rows)}"
        result = await self.session.execute(text(statement))
        return [dict(row._mapping) for row in result.fetchall()]

    @staticmethod
    def _validate_media_mime(mime_type: str, *, allowed_prefix: str) -> None:
        if not mime_type.startswith(allowed_prefix):
            raise BadRequestException(code="INVALID_AI_MEDIA_MIME_TYPE", message="Mime type media tidak sesuai endpoint.")
