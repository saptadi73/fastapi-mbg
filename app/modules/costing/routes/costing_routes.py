from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.audit.repositories.audit_repository import AuditRepository
from app.modules.audit.services.audit_service import AuditService
from app.modules.costing.repositories.cost_policy_repository import CostPolicyRepository
from app.modules.costing.schemas.costing_schema import CostPolicyCreate, CostPolicyRead, ProductionCostSummaryRead
from app.modules.costing.services.costing_service import CostingService
from app.modules.identity.models.user import User
from app.modules.meal_plan.repositories.meal_plan_repository import MealPlanRepository
from app.modules.production.repositories.production_material_consumption_repository import (
    ProductionMaterialConsumptionRepository,
)
from app.modules.production.repositories.production_order_repository import ProductionOrderRepository
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.responses.envelope import success_response

router = APIRouter()


def get_costing_service(session: AsyncSession = Depends(get_db_session)) -> CostingService:
    return CostingService(
        CostPolicyRepository(session),
        ProductionOrderRepository(session),
        ProductionMaterialConsumptionRepository(session),
        MealPlanRepository(session),
        TenantRepository(session),
        SppgRepository(session),
    )


def get_audit_service(session: AsyncSession) -> AuditService:
    return AuditService(AuditRepository(session))


@router.get("/policies")
async def list_cost_policies(request: Request, service: CostingService = Depends(get_costing_service)) -> dict:
    items = [CostPolicyRead.model_validate(item) for item in await service.list_cost_policies()]
    return success_response(
        code="COST_POLICY_LIST_FOUND",
        message="Daftar cost policy berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/policies", status_code=status.HTTP_201_CREATED)
async def create_cost_policy(
    payload: CostPolicyCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    actor: User = Depends(require_roles("super_admin", "tenant_admin", "finance_manager")),
) -> dict:
    service = get_costing_service(session)
    policy = await service.create_cost_policy(payload)
    await get_audit_service(session).record_event(
        event_type="COSTING",
        module_name="costing",
        action_name="CREATE_COST_POLICY",
        summary="Cost policy dibuat.",
        actor=actor,
        tenant_id=policy.tenant_id,
        sppg_id=policy.sppg_id,
        entity_type="cost_policy",
        entity_id=policy.id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"code": payload.code, "effective_from": str(payload.effective_from)},
    )
    await session.commit()
    return success_response(
        code="COST_POLICY_CREATED",
        message="Cost policy berhasil dibuat.",
        data=CostPolicyRead.model_validate(policy),
        meta={"request_id": request.state.request_id},
    )


@router.get("/production-costs/{production_order_id}")
async def get_production_cost_summary(
    production_order_id: UUID,
    request: Request,
    service: CostingService = Depends(get_costing_service),
) -> dict:
    payload = await service.get_production_cost_summary(production_order_id)
    return success_response(
        code="PRODUCTION_COST_SUMMARY_FOUND",
        message="Ringkasan costing production berhasil diambil.",
        data=ProductionCostSummaryRead.model_validate(payload),
        meta={"request_id": request.state.request_id, "total": len(payload["materials"])},
    )
