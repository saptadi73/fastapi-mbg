from datetime import datetime
from uuid import UUID

from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.core.tenancy.write_scope import enforce_sppg_write_scope, enforce_tenant_write_scope
from app.modules.accounting.services.accounting_service import AccountingService
from app.modules.delivery.repositories.delivery_order_repository import DeliveryOrderRepository
from app.modules.document.repositories.document_repository import DocumentRepository
from app.modules.government_claim.models.claim_adjustment import ClaimAdjustment
from app.modules.government_claim.models.claim_evidence import ClaimEvidence
from app.modules.government_claim.models.claim_payment import ClaimPayment
from app.modules.government_claim.models.claim_verification import ClaimVerification
from app.modules.government_claim.models.government_claim import GovernmentClaim
from app.modules.government_claim.models.government_claim_line import GovernmentClaimLine
from app.modules.government_claim.repositories.government_claim_repository import GovernmentClaimRepository
from app.modules.government_claim.schemas.government_claim_schema import (
    ClaimAdjustmentCreate,
    ClaimPaymentCreate,
    ClaimSubmitPayload,
    ClaimVerificationCreate,
    GovernmentClaimCreate,
)
from app.modules.identity.models.user import User
from app.modules.production.repositories.production_order_repository import ProductionOrderRepository
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, NotFoundException


class GovernmentClaimService:
    def __init__(
        self,
        repository: GovernmentClaimRepository,
        delivery_repository: DeliveryOrderRepository,
        production_repository: ProductionOrderRepository,
        document_repository: DocumentRepository,
        tenant_repository: TenantRepository,
        sppg_repository: SppgRepository,
        accounting_service: AccountingService,
    ) -> None:
        self.repository = repository
        self.delivery_repository = delivery_repository
        self.production_repository = production_repository
        self.document_repository = document_repository
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

    async def list_claims(self) -> list[GovernmentClaim]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_claims(tenant_id=tenant_id, sppg_id=sppg_id)

    async def get_claim_bundle(self, claim_id: UUID) -> dict:
        tenant_id, sppg_id = self._get_scope()
        claim = await self.repository.get_claim_by_id_and_scope(claim_id, tenant_id=tenant_id, sppg_id=sppg_id)
        if claim is None:
            raise NotFoundException(code="GOVERNMENT_CLAIM_NOT_FOUND", message="Government claim tidak ditemukan.")
        return {
            "claim": claim,
            "lines": await self.repository.list_lines(claim.id),
            "evidences": await self.repository.list_evidences(claim.id),
            "verifications": await self.repository.list_verifications(claim.id),
            "adjustments": await self.repository.list_adjustments(claim.id),
            "payments": await self.repository.list_payments(claim.id),
        }

    async def create_claim(self, payload: GovernmentClaimCreate) -> dict:
        tenant_id = UUID(payload.tenant_id)
        sppg_id = UUID(payload.sppg_id) if payload.sppg_id else None
        program_id = UUID(payload.program_id) if payload.program_id else None
        enforce_tenant_write_scope(tenant_id)
        if sppg_id is not None:
            enforce_sppg_write_scope(sppg_id)
        if payload.period_end < payload.period_start:
            raise BadRequestException(code="INVALID_CLAIM_PERIOD", message="Periode government claim tidak valid.")
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant government claim tidak ditemukan.")
        if sppg_id is not None:
            sppg = await self.sppg_repository.get_by_id(sppg_id)
            if sppg is None or sppg.tenant_id != tenant_id:
                raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG government claim tidak ditemukan.")
        if not payload.delivery_order_ids:
            raise BadRequestException(code="CLAIM_DELIVERY_REQUIRED", message="Minimal satu delivery order wajib dipilih.")

        next_number = await self.repository.count_by_tenant(tenant_id) + 1
        claim = await self.repository.add_claim(
            GovernmentClaim(
                tenant_id=tenant_id,
                sppg_id=sppg_id,
                program_id=program_id,
                claim_number=f"CLM-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}",
                period_start=payload.period_start,
                period_end=payload.period_end,
                claim_type=payload.claim_type,
                status="DRAFT",
                total_portions=0,
                claimed_amount=0,
                approved_amount=None,
                paid_amount=0,
                notes=payload.notes,
                submitted_at=None,
                verified_at=None,
                paid_at=None,
                is_active=True,
            )
        )

        total_portions = 0
        claimed_amount = 0.0
        for delivery_order_id_str in payload.delivery_order_ids:
            delivery_order_id = UUID(delivery_order_id_str)
            delivery = await self.delivery_repository.get_by_id_and_scope(delivery_order_id, tenant_id=tenant_id, sppg_id=sppg_id)
            if delivery is None:
                raise NotFoundException(code="DELIVERY_ORDER_NOT_FOUND", message="Delivery order untuk claim tidak ditemukan.")
            if delivery.received_portions is None:
                raise BadRequestException(code="DELIVERY_ORDER_NOT_RECEIVED", message="Delivery order belum memiliki proof penerimaan.")
            production_order = await self.production_repository.get_by_id(delivery.production_order_id)
            if production_order is None:
                raise NotFoundException(code="PRODUCTION_ORDER_NOT_FOUND", message="Production order untuk claim tidak ditemukan.")
            unit_cost = round(production_order.actual_cost_per_portion, 6)
            portions = int(delivery.received_portions or 0)
            line_amount = round(unit_cost * portions, 6)
            total_portions += portions
            claimed_amount = round(claimed_amount + line_amount, 6)
            await self.repository.add_line(
                GovernmentClaimLine(
                    tenant_id=tenant_id,
                    claim_id=claim.id,
                    delivery_order_id=delivery.id,
                    production_order_id=production_order.id,
                    line_type="DELIVERY_ACTUAL_COST",
                    description=f"Klaim biaya actual delivery {delivery.delivery_number}",
                    portions=portions,
                    unit_cost=unit_cost,
                    line_amount=line_amount,
                )
            )

        for document_id_str in payload.evidence_document_ids:
            document_id = UUID(document_id_str)
            document = await self.document_repository.get_document_by_id(document_id)
            if document is None or document.tenant_id != tenant_id:
                raise NotFoundException(code="DOCUMENT_NOT_FOUND", message="Dokumen evidence claim tidak ditemukan.")
            await self.repository.add_evidence(
                ClaimEvidence(
                    tenant_id=tenant_id,
                    claim_id=claim.id,
                    document_id=document.id,
                    evidence_type="SUPPORTING_DOCUMENT",
                    notes=None,
                )
            )

        claim.total_portions = total_portions
        claim.claimed_amount = round(claimed_amount, 6)
        return await self.get_claim_bundle(claim.id)

    async def submit_claim(self, claim_id: UUID, payload: ClaimSubmitPayload) -> GovernmentClaim:
        claim = await self.repository.get_claim_by_id(claim_id)
        if claim is None:
            raise NotFoundException(code="GOVERNMENT_CLAIM_NOT_FOUND", message="Government claim tidak ditemukan.")
        if claim.status != "DRAFT":
            raise BadRequestException(code="CLAIM_SUBMIT_INVALID_STATUS", message="Hanya claim DRAFT yang bisa disubmit.")
        if claim.claimed_amount <= 0 or claim.total_portions <= 0:
            raise BadRequestException(code="CLAIM_EMPTY_AMOUNT", message="Government claim belum memiliki nilai yang bisa diajukan.")
        evidences = await self.repository.list_evidences(claim.id)
        if not evidences:
            raise BadRequestException(code="CLAIM_EVIDENCE_REQUIRED", message="Government claim membutuhkan minimal satu evidence.")
        claim.status = "SUBMITTED"
        claim.submitted_at = payload.submitted_at
        return claim

    async def verify_claim(self, claim_id: UUID, payload: ClaimVerificationCreate) -> dict:
        claim = await self.repository.get_claim_by_id(claim_id)
        if claim is None:
            raise NotFoundException(code="GOVERNMENT_CLAIM_NOT_FOUND", message="Government claim tidak ditemukan.")
        if claim.status not in {"SUBMITTED", "UNDER_VERIFICATION"}:
            raise BadRequestException(code="CLAIM_VERIFY_INVALID_STATUS", message="Status government claim belum siap diverifikasi.")
        verification = await self.repository.add_verification(
            ClaimVerification(
                tenant_id=claim.tenant_id,
                claim_id=claim.id,
                verification_date=payload.verification_date,
                verification_status=payload.verification_status,
                verified_amount=round(payload.verified_amount, 6),
                verifier_name=payload.verifier_name,
                notes=payload.notes,
            )
        )
        claim.verified_at = payload.verification_date
        if payload.verification_status == "APPROVED":
            claim.status = "APPROVED"
            claim.approved_amount = round(payload.verified_amount, 6)
        elif payload.verification_status == "ADJUSTED":
            claim.status = "ADJUSTED"
            claim.approved_amount = round(payload.verified_amount, 6)
        elif payload.verification_status == "REJECTED":
            claim.status = "REJECTED"
            claim.approved_amount = 0
        else:
            claim.status = "UNDER_VERIFICATION"
        return {"claim": claim, "verification": verification}

    async def add_adjustment(self, claim_id: UUID, payload: ClaimAdjustmentCreate) -> ClaimAdjustment:
        claim = await self.repository.get_claim_by_id(claim_id)
        if claim is None:
            raise NotFoundException(code="GOVERNMENT_CLAIM_NOT_FOUND", message="Government claim tidak ditemukan.")
        adjustment = await self.repository.add_adjustment(
            ClaimAdjustment(
                tenant_id=claim.tenant_id,
                claim_id=claim.id,
                adjustment_date=payload.adjustment_date,
                adjustment_amount=round(payload.adjustment_amount, 6),
                reason=payload.reason,
            )
        )
        current = claim.approved_amount if claim.approved_amount is not None else claim.claimed_amount
        claim.approved_amount = round(current + payload.adjustment_amount, 6)
        claim.status = "ADJUSTED"
        return adjustment

    async def record_payment(self, claim_id: UUID, payload: ClaimPaymentCreate, actor: User) -> dict:
        claim = await self.repository.get_claim_by_id(claim_id)
        if claim is None:
            raise NotFoundException(code="GOVERNMENT_CLAIM_NOT_FOUND", message="Government claim tidak ditemukan.")
        if claim.status not in {"APPROVED", "ADJUSTED", "PARTIALLY_PAID", "PAID"}:
            raise BadRequestException(code="CLAIM_PAYMENT_INVALID_STATUS", message="Government claim belum bisa dibayar.")
        approved_amount = claim.approved_amount if claim.approved_amount is not None else claim.claimed_amount
        remaining = round(approved_amount - claim.paid_amount, 6)
        if payload.amount <= 0 or payload.amount > remaining:
            raise BadRequestException(code="INVALID_CLAIM_PAYMENT_AMOUNT", message="Jumlah pembayaran government claim tidak valid.")
        journal = await self.accounting_service.create_and_post_operational_journal(
            tenant_id=claim.tenant_id,
            entry_date=payload.payment_date,
            reference=payload.payment_reference,
            description=f"Pembayaran government claim {claim.claim_number}",
            source_module="government_claim",
            source_document_type="government_claim",
            source_document_id=claim.id,
            debit_account_code=payload.debit_account_code,
            credit_account_code=payload.credit_account_code,
            amount=round(payload.amount, 6),
            actor=actor,
        )
        payment = await self.repository.add_payment(
            ClaimPayment(
                tenant_id=claim.tenant_id,
                claim_id=claim.id,
                journal_entry_id=journal["journal_entry"].id,
                payment_date=payload.payment_date,
                payment_reference=payload.payment_reference,
                amount=round(payload.amount, 6),
                notes=payload.notes,
            )
        )
        claim.paid_amount = round(claim.paid_amount + payload.amount, 6)
        claim.paid_at = payload.payment_date
        claim.status = "PAID" if round(approved_amount - claim.paid_amount, 6) <= 0 else "PARTIALLY_PAID"
        return {"claim": claim, "payment": payment, "journal_entry": journal["journal_entry"]}
