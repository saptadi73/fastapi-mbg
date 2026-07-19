from datetime import date, datetime, timezone
from uuid import UUID

from app.core.tenancy.context import get_current_tenant
from app.core.tenancy.write_scope import enforce_tenant_write_scope
from app.modules.accounting.repositories.account_repository import AccountRepository
from app.modules.budget.models.budget import Budget
from app.modules.budget.models.budget_line import BudgetLine
from app.modules.budget.repositories.budget_line_repository import BudgetLineRepository
from app.modules.budget.repositories.budget_repository import BudgetRepository
from app.modules.budget.schemas.budget_schema import BudgetCreate
from app.modules.identity.models.user import User
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, NotFoundException


class BudgetService:
    def __init__(
        self,
        budget_repository: BudgetRepository,
        budget_line_repository: BudgetLineRepository,
        tenant_repository: TenantRepository,
        account_repository: AccountRepository,
    ) -> None:
        self.budget_repository = budget_repository
        self.budget_line_repository = budget_line_repository
        self.tenant_repository = tenant_repository
        self.account_repository = account_repository

    def _get_tenant_scope(self) -> UUID | None:
        current_tenant = get_current_tenant()
        if current_tenant is None:
            return None
        try:
            return UUID(current_tenant)
        except ValueError as exc:
            raise BadRequestException(
                code="INVALID_TENANT_CONTEXT",
                message="Header X-Tenant-ID tidak valid.",
            ) from exc

    async def list_budgets(self) -> list[Budget]:
        tenant_id = self._get_tenant_scope()
        return await self.budget_repository.list_all(tenant_id=tenant_id)

    async def get_budget_bundle(self, budget_id: UUID) -> dict:
        tenant_id = self._get_tenant_scope()
        if tenant_id is None:
            budget = await self.budget_repository.get_by_id(budget_id)
        else:
            budget = await self.budget_repository.get_by_id_and_tenant(budget_id, tenant_id)
        if budget is None:
            raise NotFoundException(code="BUDGET_NOT_FOUND", message="Budget tidak ditemukan.")
        lines = await self.budget_line_repository.list_by_budget(budget_id)
        return {"budget": budget, "lines": lines}

    async def create_budget(self, payload: BudgetCreate) -> dict:
        tenant_id = UUID(payload.tenant_id)
        enforce_tenant_write_scope(tenant_id)
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant untuk budget tidak ditemukan.")
        if payload.date_end < payload.date_start:
            raise BadRequestException(code="INVALID_BUDGET_DATE_RANGE", message="Tanggal akhir budget tidak valid.")
        next_number = await self.budget_repository.count_by_tenant(tenant_id) + 1
        budget = await self.budget_repository.add(
            Budget(
                tenant_id=tenant_id,
                budget_number=f"BG-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}",
                name=payload.name,
                date_start=payload.date_start,
                date_end=payload.date_end,
                version_number=payload.version_number,
                status="DRAFT",
                approved_by=None,
                approved_at=None,
                notes=payload.notes,
            )
        )
        lines: list[BudgetLine] = []
        for line in payload.lines:
            account_id = UUID(line.account_id) if line.account_id else None
            if account_id is not None:
                account = await self.account_repository.get_by_id(account_id)
                if account is None or account.tenant_id != tenant_id:
                    raise NotFoundException(code="ACCOUNT_NOT_FOUND", message="Account budget line tidak ditemukan.")
            lines.append(
                await self.budget_line_repository.add(
                    BudgetLine(
                        tenant_id=tenant_id,
                        budget_id=budget.id,
                        category_name=line.category_name,
                        account_id=account_id,
                        planned_amount=line.planned_amount,
                        revised_amount=line.revised_amount,
                        control_mode=line.control_mode,
                        tolerance_percentage=line.tolerance_percentage,
                        cached_reserved_amount=0,
                        cached_committed_amount=0,
                        cached_actual_amount=0,
                        notes=line.notes,
                    )
                )
            )
        return {"budget": budget, "lines": lines}

    async def submit_budget(self, budget_id: UUID) -> dict:
        bundle = await self.get_budget_bundle(budget_id)
        budget = bundle["budget"]
        if budget.status != "DRAFT":
            raise BadRequestException(code="BUDGET_SUBMIT_INVALID_STATUS", message="Budget hanya bisa disubmit dari DRAFT.")
        budget.status = "SUBMITTED"
        return bundle

    async def approve_budget(self, budget_id: UUID, actor: User) -> dict:
        bundle = await self.get_budget_bundle(budget_id)
        budget = bundle["budget"]
        if budget.status != "SUBMITTED":
            raise BadRequestException(code="BUDGET_APPROVE_INVALID_STATUS", message="Budget hanya bisa diapprove dari SUBMITTED.")
        budget.status = "APPROVED"
        budget.approved_by = actor.id
        budget.approved_at = datetime.now(timezone.utc)
        return bundle

    async def get_budget_availability(self, budget_id: UUID) -> dict:
        bundle = await self.get_budget_bundle(budget_id)
        lines = bundle["lines"]
        line_payloads = []
        total_effective = 0.0
        total_available = 0.0
        for line in lines:
            effective_budget = line.revised_amount if line.revised_amount is not None else line.planned_amount
            available_budget = effective_budget - line.cached_reserved_amount - line.cached_committed_amount - line.cached_actual_amount
            total_effective += effective_budget
            total_available += available_budget
            line_payloads.append(
                {
                    "budget_line_id": str(line.id),
                    "category_name": line.category_name,
                    "effective_budget": round(effective_budget, 6),
                    "reserved_amount": round(line.cached_reserved_amount, 6),
                    "committed_amount": round(line.cached_committed_amount, 6),
                    "actual_amount": round(line.cached_actual_amount, 6),
                    "available_budget": round(available_budget, 6),
                }
            )
        return {
            "budget_id": str(bundle["budget"].id),
            "totals": {
                "effective_budget": round(total_effective, 6),
                "available_budget": round(total_available, 6),
            },
            "lines": line_payloads,
        }

    async def actualize_budget_by_account(self, tenant_id: UUID, account_id: UUID, amount: float, actual_date: date) -> list[dict]:
        if amount <= 0:
            return []
        budgets = await self.budget_repository.list_approved_by_tenant_and_date(tenant_id, actual_date)
        applied: list[dict] = []
        for budget in budgets:
            lines = await self.budget_line_repository.list_by_budget_and_account(budget.id, account_id)
            for line in lines:
                released_commitment = min(line.cached_committed_amount, amount)
                line.cached_committed_amount = round(line.cached_committed_amount - released_commitment, 6)
                line.cached_actual_amount = round(line.cached_actual_amount + amount, 6)
                applied.append(
                    {
                        "budget_id": str(budget.id),
                        "budget_line_id": str(line.id),
                        "applied_amount": round(amount, 6),
                        "released_committed_amount": round(released_commitment, 6),
                    }
                )
        return applied

    async def reserve_budget_by_account(self, tenant_id: UUID, account_id: UUID, amount: float, reserve_date: date) -> list[dict]:
        if amount <= 0:
            return []
        budgets = await self.budget_repository.list_approved_by_tenant_and_date(tenant_id, reserve_date)
        applied: list[dict] = []
        for budget in budgets:
            lines = await self.budget_line_repository.list_by_budget_and_account(budget.id, account_id)
            for line in lines:
                line.cached_reserved_amount = round(line.cached_reserved_amount + amount, 6)
                applied.append(
                    {
                        "budget_id": str(budget.id),
                        "budget_line_id": str(line.id),
                        "applied_amount": round(amount, 6),
                    }
                )
        return applied

    async def commit_budget_by_account(self, tenant_id: UUID, account_id: UUID, amount: float, commit_date: date) -> list[dict]:
        if amount <= 0:
            return []
        budgets = await self.budget_repository.list_approved_by_tenant_and_date(tenant_id, commit_date)
        applied: list[dict] = []
        for budget in budgets:
            lines = await self.budget_line_repository.list_by_budget_and_account(budget.id, account_id)
            for line in lines:
                released_reserved = min(line.cached_reserved_amount, amount)
                line.cached_reserved_amount = round(line.cached_reserved_amount - released_reserved, 6)
                line.cached_committed_amount = round(line.cached_committed_amount + amount, 6)
                applied.append(
                    {
                        "budget_id": str(budget.id),
                        "budget_line_id": str(line.id),
                        "applied_amount": round(amount, 6),
                        "released_reserved_amount": round(released_reserved, 6),
                    }
                )
        return applied
