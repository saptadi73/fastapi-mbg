from uuid import UUID

from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.core.tenancy.write_scope import enforce_sppg_write_scope, enforce_tenant_write_scope
from app.modules.delivery.repositories.delivery_order_repository import DeliveryOrderRepository
from app.modules.feedback.models.complaint import Complaint
from app.modules.feedback.models.feedback_item import FeedbackItem
from app.modules.feedback.models.feedback_submission import FeedbackSubmission
from app.modules.feedback.models.service_quality_score import ServiceQualityScore
from app.modules.feedback.repositories.feedback_repository import FeedbackRepository
from app.modules.geography.repositories.school_repository import SchoolRepository
from app.modules.meal_plan.repositories.meal_plan_repository import MealPlanRepository
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, ConflictException, NotFoundException


class FeedbackService:
    def __init__(
        self,
        repository: FeedbackRepository,
        tenant_repository: TenantRepository,
        sppg_repository: SppgRepository,
        school_repository: SchoolRepository,
        meal_plan_repository: MealPlanRepository,
        delivery_order_repository: DeliveryOrderRepository,
    ) -> None:
        self.repository = repository
        self.tenant_repository = tenant_repository
        self.sppg_repository = sppg_repository
        self.school_repository = school_repository
        self.meal_plan_repository = meal_plan_repository
        self.delivery_order_repository = delivery_order_repository

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

    @staticmethod
    def _validate_rating_range(value: float | None, code: str, message: str) -> None:
        if value is None:
            return
        if value < 0 or value > 100:
            raise BadRequestException(code=code, message=message)

    async def list_submissions(self) -> list[FeedbackSubmission]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_submissions(tenant_id=tenant_id, sppg_id=sppg_id)

    async def get_submission_bundle(self, submission_id: UUID) -> dict:
        tenant_id, sppg_id = self._get_scope()
        submission = await self.repository.get_submission_by_id_and_scope(submission_id, tenant_id=tenant_id, sppg_id=sppg_id)
        if submission is None:
            raise NotFoundException(code="FEEDBACK_SUBMISSION_NOT_FOUND", message="Feedback submission tidak ditemukan.")
        items = await self.repository.list_items(submission.id)
        complaints = [item for item in await self.repository.list_complaints(submission.tenant_id, submission.sppg_id) if item.feedback_submission_id == submission.id]
        return {"submission": submission, "items": items, "complaints": complaints}

    async def create_submission(self, payload) -> dict:
        tenant_id = UUID(payload.tenant_id)
        sppg_id = UUID(payload.sppg_id)
        school_id = UUID(payload.school_id) if payload.school_id else None
        meal_plan_id = UUID(payload.meal_plan_id) if payload.meal_plan_id else None
        delivery_order_id = UUID(payload.delivery_order_id) if payload.delivery_order_id else None
        enforce_tenant_write_scope(tenant_id)
        enforce_sppg_write_scope(sppg_id)
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant feedback tidak ditemukan.")
        sppg = await self.sppg_repository.get_by_id(sppg_id)
        if sppg is None or sppg.tenant_id != tenant_id:
            raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG feedback tidak ditemukan.")
        if school_id is not None:
            school = await self.school_repository.get_by_id(school_id)
            if school is None or school.tenant_id != tenant_id:
                raise NotFoundException(code="SCHOOL_NOT_FOUND", message="Sekolah feedback tidak ditemukan.")
        if meal_plan_id is not None:
            meal_plan = await self.meal_plan_repository.get_by_id(meal_plan_id)
            if meal_plan is None or meal_plan.tenant_id != tenant_id or meal_plan.sppg_id != sppg_id:
                raise NotFoundException(code="MEAL_PLAN_NOT_FOUND", message="Meal plan feedback tidak ditemukan.")
        if delivery_order_id is not None:
            delivery_order = await self.delivery_order_repository.get_by_id(delivery_order_id)
            if delivery_order is None or delivery_order.tenant_id != tenant_id or delivery_order.sppg_id != sppg_id:
                raise NotFoundException(code="DELIVERY_ORDER_NOT_FOUND", message="Delivery order feedback tidak ditemukan.")
        self._validate_rating_range(payload.overall_rating, "INVALID_FEEDBACK_RATING", "Nilai overall rating feedback tidak valid.")
        self._validate_rating_range(payload.acceptance_rate, "INVALID_FEEDBACK_ACCEPTANCE_RATE", "Nilai acceptance rate tidak valid.")
        self._validate_rating_range(payload.delivery_timeliness_rating, "INVALID_FEEDBACK_RATING", "Nilai delivery timeliness feedback tidak valid.")
        self._validate_rating_range(payload.temperature_rating, "INVALID_FEEDBACK_RATING", "Nilai temperature feedback tidak valid.")
        if payload.food_waste_portions is not None and payload.food_waste_portions < 0:
            raise BadRequestException(code="INVALID_FOOD_WASTE_VALUE", message="Nilai food waste tidak valid.")
        submission = await self.repository.add_submission(
            FeedbackSubmission(
                tenant_id=tenant_id,
                sppg_id=sppg_id,
                school_id=school_id,
                meal_plan_id=meal_plan_id,
                delivery_order_id=delivery_order_id,
                feedback_date=payload.feedback_date,
                source_type=payload.source_type,
                respondent_name=payload.respondent_name,
                respondent_role=payload.respondent_role,
                overall_rating=payload.overall_rating,
                acceptance_rate=payload.acceptance_rate,
                food_waste_portions=payload.food_waste_portions,
                delivery_timeliness_rating=payload.delivery_timeliness_rating,
                temperature_rating=payload.temperature_rating,
                comment_text=payload.comment_text,
                status=payload.status,
            )
        )
        items: list[FeedbackItem] = []
        for item in payload.items:
            if item.score is not None and (item.score < 0 or item.score > 100):
                raise BadRequestException(code="INVALID_FEEDBACK_ITEM_SCORE", message="Nilai item feedback tidak valid.")
            items.append(
                await self.repository.add_item(
                    FeedbackItem(
                        tenant_id=tenant_id,
                        feedback_submission_id=submission.id,
                        item_type=item.item_type,
                        metric_name=item.metric_name,
                        score=item.score,
                        sentiment=item.sentiment,
                        comment_text=item.comment_text,
                    )
                )
            )
        return {"submission": submission, "items": items, "complaints": []}

    async def list_complaints(self) -> list[Complaint]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_complaints(tenant_id=tenant_id, sppg_id=sppg_id)

    async def create_complaint(self, payload) -> Complaint:
        tenant_id, sppg_id = self._get_scope()
        if tenant_id is None or sppg_id is None:
            raise BadRequestException(code="TENANT_AND_SPPG_CONTEXT_REQUIRED", message="Header X-Tenant-ID dan X-SPPG-ID wajib dikirim.")
        feedback_submission_id = UUID(payload.feedback_submission_id) if payload.feedback_submission_id else None
        if feedback_submission_id is not None:
            submission = await self.repository.get_submission_by_id_and_scope(feedback_submission_id, tenant_id=tenant_id, sppg_id=sppg_id)
            if submission is None:
                raise NotFoundException(code="FEEDBACK_SUBMISSION_NOT_FOUND", message="Feedback submission complaint tidak ditemukan.")
        if payload.resolved_at is not None and payload.resolved_at < payload.complaint_date:
            raise BadRequestException(code="INVALID_COMPLAINT_RESOLUTION_TIME", message="Waktu penyelesaian complaint tidak valid.")
        return await self.repository.add_complaint(
            Complaint(
                tenant_id=tenant_id,
                sppg_id=sppg_id,
                feedback_submission_id=feedback_submission_id,
                complaint_date=payload.complaint_date,
                category=payload.category,
                severity=payload.severity,
                complaint_text=payload.complaint_text,
                resolution_status=payload.resolution_status,
                resolved_at=payload.resolved_at,
                notes=payload.notes,
            )
        )

    async def list_scores(self) -> list[ServiceQualityScore]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_scores(tenant_id=tenant_id, sppg_id=sppg_id)

    async def create_score(self, payload) -> ServiceQualityScore:
        tenant_id = UUID(payload.tenant_id)
        sppg_id = UUID(payload.sppg_id)
        enforce_tenant_write_scope(tenant_id)
        enforce_sppg_write_scope(sppg_id)
        sppg = await self.sppg_repository.get_by_id(sppg_id)
        if sppg is None or sppg.tenant_id != tenant_id:
            raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG score feedback tidak ditemukan.")
        if await self.repository.get_score_by_scope_date(tenant_id, sppg_id, payload.score_date) is not None:
            raise ConflictException(code="SERVICE_QUALITY_SCORE_ALREADY_EXISTS", message="Score quality untuk tanggal ini sudah ada.")
        parts = [
            payload.acceptance_score,
            payload.waste_score,
            payload.delivery_score,
            payload.temperature_score,
            payload.taste_score,
            payload.nutrition_score,
            payload.complaint_score,
        ]
        for value in parts:
            self._validate_rating_range(value, "INVALID_SERVICE_QUALITY_SCORE", "Nilai service quality score tidak valid.")
        total_score = payload.total_score
        if total_score is None:
            values = [value for value in parts if value is not None]
            total_score = round(sum(values) / len(values), 6) if values else 0.0
        self._validate_rating_range(total_score, "INVALID_SERVICE_QUALITY_SCORE", "Nilai service quality score tidak valid.")
        return await self.repository.add_score(
            ServiceQualityScore(
                tenant_id=tenant_id,
                sppg_id=sppg_id,
                score_date=payload.score_date,
                acceptance_score=payload.acceptance_score,
                waste_score=payload.waste_score,
                delivery_score=payload.delivery_score,
                temperature_score=payload.temperature_score,
                taste_score=payload.taste_score,
                nutrition_score=payload.nutrition_score,
                complaint_score=payload.complaint_score,
                total_score=total_score,
                score_status=payload.score_status,
                notes=payload.notes,
            )
        )

    async def summary(self) -> dict:
        tenant_id, sppg_id = self._get_scope()
        submissions = await self.repository.list_submissions(tenant_id=tenant_id, sppg_id=sppg_id)
        complaints = await self.repository.list_complaints(tenant_id=tenant_id, sppg_id=sppg_id)
        scores = await self.repository.list_scores(tenant_id=tenant_id, sppg_id=sppg_id)
        rated_submissions = [item for item in submissions if item.overall_rating is not None]
        accepted_submissions = [item for item in submissions if item.acceptance_rate is not None]
        waste_submissions = [item for item in submissions if item.food_waste_portions is not None]
        avg = lambda items, attr: round(sum(getattr(item, attr) for item in items) / len(items), 6) if items else 0.0
        return {
            "totals": {
                "submissions": len(submissions),
                "complaints": len(complaints),
                "service_quality_scores": len(scores),
            },
            "averages": {
                "overall_rating": avg(rated_submissions, "overall_rating"),
                "acceptance_rate": avg(accepted_submissions, "acceptance_rate"),
                "food_waste_portions": avg(waste_submissions, "food_waste_portions"),
                "service_quality_score": round(sum(item.total_score for item in scores) / len(scores), 6) if scores else 0.0,
            },
            "complaints": {
                "open": len([item for item in complaints if item.resolution_status == "OPEN"]),
                "resolved": len([item for item in complaints if item.resolution_status == "RESOLVED"]),
                "high_severity": len([item for item in complaints if item.severity == "HIGH"]),
            },
        }
