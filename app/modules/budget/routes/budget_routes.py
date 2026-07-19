from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.dependencies import get_current_user
from app.core.security.permissions import require_roles
from app.modules.accounting.repositories.account_repository import AccountRepository
from app.modules.audit.repositories.audit_repository import AuditRepository
from app.modules.audit.services.audit_service import AuditService
from app.modules.budget.repositories.budget_line_repository import BudgetLineRepository
from app.modules.budget.repositories.budget_repository import BudgetRepository
from app.modules.budget.schemas.budget_schema import BudgetAvailabilityRead, BudgetBundleRead, BudgetCreate, BudgetRead
from app.modules.budget.services.budget_service import BudgetService
from app.modules.identity.models.user import User
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.modules.workflow.repositories.workflow_repository import WorkflowRepository
from app.modules.workflow.services.workflow_service import WorkflowService
from app.support.responses.envelope import success_response

router = APIRouter()


def get_budget_service(session: AsyncSession = Depends(get_db_session)) -> BudgetService:
    return BudgetService(
        BudgetRepository(session),
        BudgetLineRepository(session),
        TenantRepository(session),
        AccountRepository(session),
        WorkflowService(WorkflowRepository(session)),
    )


def get_audit_service(session: AsyncSession) -> AuditService:
    return AuditService(AuditRepository(session))


@router.get("/budgets")
async def list_budgets(request: Request, service: BudgetService = Depends(get_budget_service)) -> dict:
    items = [BudgetRead.model_validate(item) for item in await service.list_budgets()]
    return success_response(
        code="BUDGET_LIST_FOUND",
        message="Daftar budget berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/budgets/{budget_id}")
async def get_budget(budget_id: UUID, request: Request, service: BudgetService = Depends(get_budget_service)) -> dict:
    bundle = await service.get_budget_bundle(budget_id)
    return success_response(
        code="BUDGET_FOUND",
        message="Detail budget berhasil diambil.",
        data=BudgetBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id},
    )


@router.post("/budgets", status_code=status.HTTP_201_CREATED)
async def create_budget(
    payload: BudgetCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "finance_manager")),
) -> dict:
    service = get_budget_service(session)
    bundle = await service.create_budget(payload, current_user)
    await get_audit_service(session).record_event(
        event_type="BUDGET",
        module_name="budget",
        action_name="CREATE",
        summary="Budget dibuat.",
        actor=current_user,
        tenant_id=UUID(payload.tenant_id),
        entity_type="budget",
        entity_id=bundle["budget"].id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
        metadata_json={"name": payload.name, "line_count": len(payload.lines)},
    )
    await session.commit()
    return success_response(
        code="BUDGET_CREATED",
        message="Budget berhasil dibuat.",
        data=BudgetBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id, "total": len(bundle["lines"])},
    )


@router.post("/budgets/{budget_id}/submit")
async def submit_budget(
    budget_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "finance_manager")),
) -> dict:
    service = get_budget_service(session)
    bundle = await service.submit_budget(budget_id, current_user)
    await get_audit_service(session).record_event(
        event_type="APPROVAL",
        module_name="budget",
        action_name="SUBMIT",
        summary="Budget disubmit.",
        actor=current_user,
        tenant_id=bundle["budget"].tenant_id,
        entity_type="budget",
        entity_id=bundle["budget"].id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
    )
    await session.commit()
    return success_response(
        code="BUDGET_SUBMITTED",
        message="Budget berhasil disubmit.",
        data=BudgetBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id, "total": len(bundle["lines"])},
    )


@router.post("/budgets/{budget_id}/approve")
async def approve_budget(
    budget_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "finance_manager")),
) -> dict:
    service = get_budget_service(session)
    bundle = await service.approve_budget(budget_id, current_user)
    await get_audit_service(session).record_event(
        event_type="APPROVAL",
        module_name="budget",
        action_name="APPROVE",
        summary="Budget diapprove.",
        actor=current_user,
        tenant_id=bundle["budget"].tenant_id,
        entity_type="budget",
        entity_id=bundle["budget"].id,
        request_id=request.state.request_id,
        ip_address=request.client.host if request.client else None,
    )
    await session.commit()
    return success_response(
        code="BUDGET_APPROVED",
        message="Budget berhasil diapprove.",
        data=BudgetBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id, "total": len(bundle["lines"])},
    )


@router.get("/budgets/{budget_id}/availability")
async def get_budget_availability(
    budget_id: UUID,
    request: Request,
    service: BudgetService = Depends(get_budget_service),
) -> dict:
    availability = await service.get_budget_availability(budget_id)
    return success_response(
        code="BUDGET_AVAILABILITY_FOUND",
        message="Availability budget berhasil diambil.",
        data=BudgetAvailabilityRead.model_validate(availability),
        meta={"request_id": request.state.request_id, "total": len(availability["lines"])},
    )
