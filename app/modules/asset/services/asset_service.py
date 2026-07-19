from uuid import UUID

from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.core.tenancy.write_scope import enforce_sppg_write_scope, enforce_tenant_write_scope
from app.modules.accounting.services.accounting_service import AccountingService
from app.modules.asset.models.asset import Asset
from app.modules.asset.models.asset_assignment import AssetAssignment
from app.modules.asset.models.asset_category import AssetCategory
from app.modules.asset.models.asset_depreciation import AssetDepreciation
from app.modules.asset.repositories.asset_repository import AssetRepository
from app.modules.identity.models.user import User
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, ConflictException, NotFoundException


class AssetService:
    def __init__(
        self,
        repository: AssetRepository,
        tenant_repository: TenantRepository,
        sppg_repository: SppgRepository,
        accounting_service: AccountingService,
    ) -> None:
        self.repository = repository
        self.tenant_repository = tenant_repository
        self.sppg_repository = sppg_repository
        self.accounting_service = accounting_service

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

    async def list_categories(self) -> list[AssetCategory]:
        tenant_id, _ = self._get_scope()
        return await self.repository.list_categories(tenant_id=tenant_id)

    async def create_category(self, payload) -> AssetCategory:
        tenant_id = UUID(payload.tenant_id)
        enforce_tenant_write_scope(tenant_id)
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant asset tidak ditemukan.")
        if await self.repository.get_category_by_tenant_code(tenant_id, payload.code) is not None:
            raise ConflictException(code="ASSET_CATEGORY_CODE_ALREADY_EXISTS", message="Kode kategori asset sudah digunakan.")
        for account_id in [payload.asset_account_id, payload.depreciation_expense_account_id, payload.accumulated_depreciation_account_id]:
            if account_id:
                account = await self.accounting_service.account_repository.get_by_id(UUID(account_id))
                if account is None or account.tenant_id != tenant_id:
                    raise NotFoundException(code="ACCOUNT_NOT_FOUND", message="Account kategori asset tidak ditemukan.")
        if payload.useful_life_months is not None and payload.useful_life_months <= 0:
            raise BadRequestException(code="INVALID_ASSET_USEFUL_LIFE", message="Useful life asset harus lebih besar dari nol.")
        return await self.repository.add_category(
            AssetCategory(
                tenant_id=tenant_id,
                code=payload.code,
                name=payload.name,
                asset_account_id=UUID(payload.asset_account_id) if payload.asset_account_id else None,
                depreciation_expense_account_id=UUID(payload.depreciation_expense_account_id) if payload.depreciation_expense_account_id else None,
                accumulated_depreciation_account_id=UUID(payload.accumulated_depreciation_account_id) if payload.accumulated_depreciation_account_id else None,
                useful_life_months=payload.useful_life_months,
                depreciation_method=payload.depreciation_method,
                is_active=payload.is_active,
            )
        )

    async def list_assets(self) -> list[Asset]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_assets(tenant_id=tenant_id, sppg_id=sppg_id)

    async def get_asset_bundle(self, asset_id: UUID) -> dict:
        tenant_id, sppg_id = self._get_scope()
        asset = await self.repository.get_asset_by_id_and_scope(asset_id, tenant_id=tenant_id, sppg_id=sppg_id)
        if asset is None:
            raise NotFoundException(code="ASSET_NOT_FOUND", message="Asset tidak ditemukan.")
        return {
            "asset": asset,
            "assignments": await self.repository.list_assignments_by_asset(asset.id),
            "depreciations": await self.repository.list_depreciations_by_asset(asset.id),
        }

    async def create_asset(self, payload) -> Asset:
        tenant_id = UUID(payload.tenant_id)
        sppg_id = UUID(payload.sppg_id) if payload.sppg_id else None
        category_id = UUID(payload.asset_category_id) if payload.asset_category_id else None
        enforce_tenant_write_scope(tenant_id)
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant asset tidak ditemukan.")
        if await self.repository.get_asset_by_tenant_code(tenant_id, payload.asset_code) is not None:
            raise ConflictException(code="ASSET_CODE_ALREADY_EXISTS", message="Kode asset sudah digunakan.")
        if sppg_id is not None:
            enforce_sppg_write_scope(sppg_id)
            sppg = await self.sppg_repository.get_by_id(sppg_id)
            if sppg is None or sppg.tenant_id != tenant_id:
                raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG asset tidak ditemukan.")
        if category_id is not None:
            category = await self.repository.get_category_by_id(category_id)
            if category is None or category.tenant_id != tenant_id:
                raise NotFoundException(code="ASSET_CATEGORY_NOT_FOUND", message="Kategori asset tidak ditemukan.")
        if payload.acquisition_cost <= 0:
            raise BadRequestException(code="INVALID_ASSET_ACQUISITION_COST", message="Nilai perolehan asset harus lebih besar dari nol.")
        if payload.residual_value < 0 or payload.residual_value > payload.acquisition_cost:
            raise BadRequestException(code="INVALID_ASSET_RESIDUAL_VALUE", message="Nilai residu asset tidak valid.")
        useful_life_months = payload.useful_life_months
        if useful_life_months is None and category_id is not None:
            category = await self.repository.get_category_by_id(category_id)
            useful_life_months = category.useful_life_months if category else None
        if useful_life_months is not None and useful_life_months <= 0:
            raise BadRequestException(code="INVALID_ASSET_USEFUL_LIFE", message="Useful life asset harus lebih besar dari nol.")
        return await self.repository.add_asset(
            Asset(
                tenant_id=tenant_id,
                sppg_id=sppg_id,
                asset_category_id=category_id,
                asset_code=payload.asset_code,
                asset_name=payload.asset_name,
                acquisition_date=payload.acquisition_date,
                acquisition_cost=round(payload.acquisition_cost, 6),
                residual_value=round(payload.residual_value, 6),
                useful_life_months=useful_life_months,
                depreciation_method=payload.depreciation_method,
                status=payload.status,
                serial_number=payload.serial_number,
                condition_status=payload.condition_status,
                location_name=payload.location_name,
                is_active=payload.is_active,
                notes=payload.notes,
            )
        )

    async def list_assignments(self) -> list[AssetAssignment]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_assignments(tenant_id=tenant_id, sppg_id=sppg_id)

    async def assign_asset(self, asset_id: UUID, payload) -> AssetAssignment:
        asset = await self.repository.get_asset_by_id(asset_id)
        if asset is None:
            raise NotFoundException(code="ASSET_NOT_FOUND", message="Asset tidak ditemukan.")
        sppg_id = UUID(payload.sppg_id)
        enforce_tenant_write_scope(asset.tenant_id)
        enforce_sppg_write_scope(sppg_id)
        sppg = await self.sppg_repository.get_by_id(sppg_id)
        if sppg is None or sppg.tenant_id != asset.tenant_id:
            raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG assignment asset tidak ditemukan.")
        if payload.end_date and payload.end_date < payload.assignment_date:
            raise BadRequestException(code="INVALID_ASSET_ASSIGNMENT_DATE_RANGE", message="Tanggal assignment asset tidak valid.")
        asset.sppg_id = sppg_id
        return await self.repository.add_assignment(
            AssetAssignment(
                tenant_id=asset.tenant_id,
                sppg_id=sppg_id,
                asset_id=asset.id,
                assigned_to_name=payload.assigned_to_name,
                assignment_date=payload.assignment_date,
                end_date=payload.end_date,
                assignment_role=payload.assignment_role,
                status=payload.status,
                is_active=payload.is_active,
                notes=payload.notes,
            )
        )

    async def list_depreciations(self) -> list[AssetDepreciation]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_depreciations(tenant_id=tenant_id, sppg_id=sppg_id)

    async def create_depreciation(self, asset_id: UUID, payload, actor: User) -> dict:
        asset = await self.repository.get_asset_by_id(asset_id)
        if asset is None:
            raise NotFoundException(code="ASSET_NOT_FOUND", message="Asset tidak ditemukan.")
        enforce_tenant_write_scope(asset.tenant_id)
        if await self.repository.get_depreciation_by_asset_date(asset.id, payload.depreciation_date) is not None:
            raise ConflictException(code="ASSET_DEPRECIATION_ALREADY_EXISTS", message="Depresiasi asset pada tanggal ini sudah ada.")
        if asset.useful_life_months is None or asset.useful_life_months <= 0:
            raise BadRequestException(code="ASSET_USEFUL_LIFE_REQUIRED", message="Useful life asset diperlukan untuk depresiasi.")
        if asset.acquisition_cost <= asset.residual_value:
            raise BadRequestException(code="INVALID_ASSET_DEPRECIABLE_VALUE", message="Nilai depresiasi asset tidak valid.")
        prior = await self.repository.list_depreciations_by_asset(asset.id)
        prior_amount = sum(item.depreciation_amount for item in prior)
        remaining_depreciable = round((asset.acquisition_cost - asset.residual_value) - prior_amount, 6)
        if remaining_depreciable <= 0:
            raise BadRequestException(code="ASSET_FULLY_DEPRECIATED", message="Asset sudah terdepresiasi penuh.")
        depreciation_amount = payload.depreciation_amount
        if depreciation_amount is None:
            depreciation_amount = round((asset.acquisition_cost - asset.residual_value) / asset.useful_life_months, 6)
        if depreciation_amount <= 0 or depreciation_amount > remaining_depreciable:
            raise BadRequestException(code="INVALID_ASSET_DEPRECIATION_AMOUNT", message="Nilai depresiasi asset tidak valid.")
        category = await self.repository.get_category_by_id(asset.asset_category_id) if asset.asset_category_id else None
        debit_code = payload.debit_account_code
        credit_code = payload.credit_account_code
        if category is not None and debit_code is None and category.depreciation_expense_account_id is not None:
            debit_account = await self.accounting_service.account_repository.get_by_id(category.depreciation_expense_account_id)
            debit_code = debit_account.code if debit_account else None
        if category is not None and credit_code is None and category.accumulated_depreciation_account_id is not None:
            credit_account = await self.accounting_service.account_repository.get_by_id(category.accumulated_depreciation_account_id)
            credit_code = credit_account.code if credit_account else None
        if debit_code is None or credit_code is None:
            raise BadRequestException(code="ASSET_DEPRECIATION_ACCOUNT_REQUIRED", message="Account depresiasi asset belum lengkap.")
        journal = await self.accounting_service.create_and_post_operational_journal(
            tenant_id=asset.tenant_id,
            entry_date=payload.depreciation_date,
            reference=asset.asset_code,
            description=f"Depresiasi asset {asset.asset_code}",
            source_module="asset",
            source_document_type="asset_depreciation",
            source_document_id=None,
            debit_account_code=debit_code,
            credit_account_code=credit_code,
            amount=round(depreciation_amount, 6),
            actor=actor,
        )
        accumulated = round(prior_amount + depreciation_amount, 6)
        depreciation = await self.repository.add_depreciation(
            AssetDepreciation(
                tenant_id=asset.tenant_id,
                sppg_id=asset.sppg_id,
                asset_id=asset.id,
                journal_entry_id=journal["journal_entry"].id,
                depreciation_date=payload.depreciation_date,
                depreciation_amount=round(depreciation_amount, 6),
                accumulated_depreciation_amount=accumulated,
                book_value_after=round(asset.acquisition_cost - accumulated, 6),
                status=payload.status,
                notes=payload.notes,
            )
        )
        return {"depreciation": depreciation, "journal_entry": journal["journal_entry"]}
