from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GovernmentClaimCreate(BaseModel):
    tenant_id: str
    sppg_id: str | None = None
    program_id: str | None = None
    period_start: date
    period_end: date
    claim_type: str = "ACTUAL_COST"
    delivery_order_ids: list[str]
    evidence_document_ids: list[str] = []
    notes: str | None = None


class ClaimSubmitPayload(BaseModel):
    submitted_at: date


class ClaimVerificationCreate(BaseModel):
    verification_date: date
    verification_status: str
    verified_amount: float
    verifier_name: str
    notes: str | None = None


class ClaimAdjustmentCreate(BaseModel):
    adjustment_date: date
    adjustment_amount: float
    reason: str


class ClaimPaymentCreate(BaseModel):
    payment_date: date
    amount: float
    payment_reference: str | None = None
    notes: str | None = None
    debit_account_code: str = "110000"
    credit_account_code: str = "120500"


class GovernmentClaimRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID | None
    program_id: UUID | None
    claim_number: str
    period_start: date
    period_end: date
    claim_type: str
    status: str
    total_portions: int
    claimed_amount: float
    approved_amount: float | None
    paid_amount: float
    notes: str | None
    submitted_at: date | None
    verified_at: date | None
    paid_at: date | None
    is_active: bool


class GovernmentClaimLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    claim_id: UUID
    delivery_order_id: UUID | None
    production_order_id: UUID | None
    line_type: str
    description: str
    portions: int
    unit_cost: float
    line_amount: float


class ClaimEvidenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    claim_id: UUID
    document_id: UUID
    evidence_type: str
    notes: str | None


class ClaimVerificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    claim_id: UUID
    verification_date: date
    verification_status: str
    verified_amount: float
    verifier_name: str
    notes: str | None


class ClaimAdjustmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    claim_id: UUID
    adjustment_date: date
    adjustment_amount: float
    reason: str


class ClaimPaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    claim_id: UUID
    journal_entry_id: UUID | None
    payment_date: date
    payment_reference: str | None
    amount: float
    notes: str | None


class GovernmentClaimBundleRead(BaseModel):
    claim: GovernmentClaimRead
    lines: list[GovernmentClaimLineRead]
    evidences: list[ClaimEvidenceRead]
    verifications: list[ClaimVerificationRead]
    adjustments: list[ClaimAdjustmentRead]
    payments: list[ClaimPaymentRead]
