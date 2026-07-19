from uuid import UUID

from app.core.tenancy.context import get_current_tenant
from app.core.tenancy.write_scope import enforce_sppg_write_scope, enforce_tenant_write_scope
from app.modules.accounting.services.accounting_service import AccountingService
from app.modules.funding.models.funding_agreement import FundingAgreement
from app.modules.funding.models.funding_disbursement import FundingDisbursement
from app.modules.funding.models.funding_repayment import FundingRepayment
from app.modules.funding.models.funding_source import FundingSource
from app.modules.funding.repositories.funding_repository import FundingRepository
from app.modules.funding.schemas.funding_schema import (
    FundingAgreementCreate,
    FundingDisbursementCreate,
    FundingRepaymentCreate,
    FundingSourceCreate,
)
from app.modules.identity.models.user import User
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, ConflictException, NotFoundException


class FundingService:
    def __init__(
        self,
        repository: FundingRepository,
        tenant_repository: TenantRepository,
        sppg_repository: SppgRepository,
        accounting_service: AccountingService,
    ) -> None:
        self.repository = repository
        self.tenant_repository = tenant_repository
        self.sppg_repository = sppg_repository
        self.accounting_service = accounting_service

    def _get_tenant_scope(self) -> UUID | None:
        current_tenant = get_current_tenant()
        if current_tenant is None:
            return None
        try:
            return UUID(current_tenant)
        except ValueError as exc:
            raise BadRequestException(code="INVALID_TENANT_CONTEXT", message="Header X-Tenant-ID tidak valid.") from exc

    async def list_sources(self) -> list[FundingSource]:
        return await self.repository.list_sources(self._get_tenant_scope())

    async def create_source(self, payload: FundingSourceCreate) -> FundingSource:
        tenant_id = UUID(payload.tenant_id)
        enforce_tenant_write_scope(tenant_id)
        if payload.end_date and payload.start_date and payload.end_date < payload.start_date:
            raise BadRequestException(code="INVALID_FUNDING_SOURCE_DATE_RANGE", message="Tanggal funding source tidak valid.")
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant funding source tidak ditemukan.")
        if await self.repository.get_source_by_tenant_code(tenant_id, payload.code) is not None:
            raise ConflictException(code="FUNDING_SOURCE_CODE_ALREADY_EXISTS", message="Kode funding source sudah digunakan.")
        return await self.repository.add_source(
            FundingSource(
                tenant_id=tenant_id,
                code=payload.code,
                source_type=payload.source_type,
                name=payload.name,
                party_name=payload.party_name,
                contract_number=payload.contract_number,
                start_date=payload.start_date,
                end_date=payload.end_date,
                status=payload.status,
                is_active=payload.is_active,
                notes=payload.notes,
            )
        )

    async def list_agreements(self) -> list[FundingAgreement]:
        return await self.repository.list_agreements(self._get_tenant_scope())

    async def create_agreement(self, payload: FundingAgreementCreate) -> FundingAgreement:
        source_id = UUID(payload.funding_source_id)
        source = await self.repository.get_source_by_id(source_id)
        if source is None:
            raise NotFoundException(code="FUNDING_SOURCE_NOT_FOUND", message="Funding source tidak ditemukan.")
        enforce_tenant_write_scope(source.tenant_id)
        if payload.principal_amount <= 0:
            raise BadRequestException(code="INVALID_FUNDING_PRINCIPAL_AMOUNT", message="Principal funding harus lebih besar dari nol.")
        return await self.repository.add_agreement(
            FundingAgreement(
                tenant_id=source.tenant_id,
                funding_source_id=source.id,
                agreement_type=payload.agreement_type,
                principal_amount=round(payload.principal_amount, 6),
                margin_method=payload.margin_method,
                margin_rate=payload.margin_rate,
                fixed_margin_amount=payload.fixed_margin_amount,
                disbursement_schedule=payload.disbursement_schedule,
                repayment_terms=payload.repayment_terms,
                status=payload.status,
                notes=payload.notes,
            )
        )

    async def get_agreement_bundle(self, agreement_id: UUID) -> dict:
        agreement = await self.repository.get_agreement_by_id(agreement_id)
        if agreement is None:
            raise NotFoundException(code="FUNDING_AGREEMENT_NOT_FOUND", message="Funding agreement tidak ditemukan.")
        tenant_scope = self._get_tenant_scope()
        if tenant_scope is not None and agreement.tenant_id != tenant_scope:
            raise NotFoundException(code="FUNDING_AGREEMENT_NOT_FOUND", message="Funding agreement tidak ditemukan.")
        source = await self.repository.get_source_by_id(agreement.funding_source_id)
        if source is None:
            raise NotFoundException(code="FUNDING_SOURCE_NOT_FOUND", message="Funding source tidak ditemukan.")
        disbursements = await self.repository.list_disbursements_by_agreement(agreement.id)
        repayments = await self.repository.list_repayments_by_agreement(agreement.id)
        principal_disbursed = round(sum(item.amount for item in disbursements), 6)
        principal_repaid = round(sum(item.principal_amount for item in repayments), 6)
        realized_margin = round(sum(item.margin_amount for item in repayments), 6)
        return {
            "agreement": agreement,
            "source": source,
            "disbursements": disbursements,
            "repayments": repayments,
            "principal_disbursed": principal_disbursed,
            "principal_repaid": principal_repaid,
            "outstanding_principal": round(principal_disbursed - principal_repaid, 6),
            "realized_margin": realized_margin,
        }

    async def list_disbursements(self) -> list[FundingDisbursement]:
        return await self.repository.list_disbursements(self._get_tenant_scope())

    async def create_disbursement(self, agreement_id: UUID, payload: FundingDisbursementCreate, actor: User) -> dict:
        agreement = await self.repository.get_agreement_by_id(agreement_id)
        if agreement is None:
            raise NotFoundException(code="FUNDING_AGREEMENT_NOT_FOUND", message="Funding agreement tidak ditemukan.")
        enforce_tenant_write_scope(agreement.tenant_id)
        sppg_id = UUID(payload.sppg_id) if payload.sppg_id else None
        if sppg_id is not None:
            enforce_sppg_write_scope(sppg_id)
            sppg = await self.sppg_repository.get_by_id(sppg_id)
            if sppg is None or sppg.tenant_id != agreement.tenant_id:
                raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG funding disbursement tidak ditemukan.")
        if payload.amount <= 0:
            raise BadRequestException(code="INVALID_FUNDING_DISBURSEMENT_AMOUNT", message="Nilai funding disbursement harus lebih besar dari nol.")
        bundle = await self.get_agreement_bundle(agreement_id)
        if bundle["principal_disbursed"] + payload.amount > agreement.principal_amount:
            raise BadRequestException(code="FUNDING_DISBURSEMENT_EXCEEDS_PRINCIPAL", message="Disbursement melebihi principal agreement.")
        journal = await self.accounting_service.create_and_post_operational_journal(
            tenant_id=agreement.tenant_id,
            entry_date=payload.disbursement_date,
            reference=payload.reference_number,
            description=f"Funding disbursement agreement {agreement.id}",
            source_module="funding",
            source_document_type="funding_disbursement",
            source_document_id=None,
            debit_account_code=payload.debit_account_code,
            credit_account_code=payload.credit_account_code,
            amount=round(payload.amount, 6),
            actor=actor,
        )
        disbursement = await self.repository.add_disbursement(
            FundingDisbursement(
                tenant_id=agreement.tenant_id,
                agreement_id=agreement.id,
                sppg_id=sppg_id,
                journal_entry_id=journal["journal_entry"].id,
                disbursement_date=payload.disbursement_date,
                amount=round(payload.amount, 6),
                bank_account_id=UUID(payload.bank_account_id) if payload.bank_account_id else None,
                reference_number=payload.reference_number,
                status=payload.status,
                notes=payload.notes,
            )
        )
        agreement.status = "ACTIVE"
        return {"disbursement": disbursement, "journal_entry": journal["journal_entry"]}

    async def list_repayments(self) -> list[FundingRepayment]:
        return await self.repository.list_repayments(self._get_tenant_scope())

    async def create_repayment(self, agreement_id: UUID, payload: FundingRepaymentCreate, actor: User) -> dict:
        agreement = await self.repository.get_agreement_by_id(agreement_id)
        if agreement is None:
            raise NotFoundException(code="FUNDING_AGREEMENT_NOT_FOUND", message="Funding agreement tidak ditemukan.")
        enforce_tenant_write_scope(agreement.tenant_id)
        total_amount = round(payload.principal_amount + payload.margin_amount + payload.penalty_amount, 6)
        if total_amount <= 0:
            raise BadRequestException(code="INVALID_FUNDING_REPAYMENT_AMOUNT", message="Nilai funding repayment harus lebih besar dari nol.")
        bundle = await self.get_agreement_bundle(agreement_id)
        if payload.principal_amount > bundle["outstanding_principal"]:
            raise BadRequestException(code="FUNDING_REPAYMENT_EXCEEDS_OUTSTANDING", message="Principal repayment melebihi outstanding.")
        journal = await self.accounting_service.create_and_post_operational_journal(
            tenant_id=agreement.tenant_id,
            entry_date=payload.repayment_date,
            reference=payload.payment_reference,
            description=f"Funding repayment agreement {agreement.id}",
            source_module="funding",
            source_document_type="funding_repayment",
            source_document_id=None,
            debit_account_code=payload.debit_account_code,
            credit_account_code=payload.credit_account_code,
            amount=total_amount,
            actor=actor,
        )
        repayment = await self.repository.add_repayment(
            FundingRepayment(
                tenant_id=agreement.tenant_id,
                agreement_id=agreement.id,
                journal_entry_id=journal["journal_entry"].id,
                repayment_date=payload.repayment_date,
                principal_amount=round(payload.principal_amount, 6),
                margin_amount=round(payload.margin_amount, 6),
                penalty_amount=round(payload.penalty_amount, 6),
                payment_reference=payload.payment_reference,
                status=payload.status,
                notes=payload.notes,
            )
        )
        refreshed = await self.get_agreement_bundle(agreement_id)
        if refreshed["outstanding_principal"] <= 0:
            agreement.status = "CLOSED"
        else:
            agreement.status = "ACTIVE"
        return {"repayment": repayment, "journal_entry": journal["journal_entry"]}

    async def summary(self) -> dict:
        tenant_id = self._get_tenant_scope()
        sources = await self.repository.list_sources(tenant_id)
        agreements = await self.repository.list_agreements(tenant_id)
        disbursements = await self.repository.list_disbursements(tenant_id)
        repayments = await self.repository.list_repayments(tenant_id)
        principal_committed = round(sum(item.principal_amount for item in agreements), 6)
        principal_disbursed = round(sum(item.amount for item in disbursements), 6)
        principal_repaid = round(sum(item.principal_amount for item in repayments), 6)
        margin_realized = round(sum(item.margin_amount for item in repayments), 6)
        return {
            "totals": {
                "funding_sources": len(sources),
                "funding_agreements": len(agreements),
                "principal_committed": principal_committed,
                "principal_disbursed": principal_disbursed,
                "principal_repaid": principal_repaid,
                "outstanding_principal": round(principal_disbursed - principal_repaid, 6),
                "margin_realized": margin_realized,
            },
            "breakdown": {
                "active_agreements": len([item for item in agreements if item.status == "ACTIVE"]),
                "closed_agreements": len([item for item in agreements if item.status == "CLOSED"]),
                "government_sources": len([item for item in sources if item.source_type == "GOVERNMENT_BUDGET"]),
                "investor_sources": len([item for item in sources if item.source_type == "INVESTOR_BRIDGE_FUND"]),
            },
        }
