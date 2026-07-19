from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FundingSourceCreate(BaseModel):
    tenant_id: str
    code: str
    source_type: str
    name: str
    party_name: str | None = None
    contract_number: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str = "DRAFT"
    is_active: bool = True
    notes: str | None = None


class FundingAgreementCreate(BaseModel):
    funding_source_id: str
    agreement_type: str
    principal_amount: float
    margin_method: str | None = None
    margin_rate: float | None = None
    fixed_margin_amount: float | None = None
    disbursement_schedule: dict = Field(default_factory=dict)
    repayment_terms: dict = Field(default_factory=dict)
    status: str = "DRAFT"
    notes: str | None = None


class FundingDisbursementCreate(BaseModel):
    sppg_id: str | None = None
    disbursement_date: date
    amount: float
    bank_account_id: str | None = None
    reference_number: str | None = None
    status: str = "POSTED"
    notes: str | None = None
    debit_account_code: str = "110000"
    credit_account_code: str = "230500"


class FundingRepaymentCreate(BaseModel):
    repayment_date: date
    principal_amount: float = 0
    margin_amount: float = 0
    penalty_amount: float = 0
    payment_reference: str | None = None
    status: str = "POSTED"
    notes: str | None = None
    debit_account_code: str = "230500"
    credit_account_code: str = "110000"


class FundingSourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    code: str
    source_type: str
    name: str
    party_name: str | None
    contract_number: str | None
    start_date: date | None
    end_date: date | None
    status: str
    is_active: bool
    notes: str | None


class FundingAgreementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    funding_source_id: UUID
    agreement_type: str
    principal_amount: float
    margin_method: str | None
    margin_rate: float | None
    fixed_margin_amount: float | None
    disbursement_schedule: dict
    repayment_terms: dict
    status: str
    notes: str | None


class FundingDisbursementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    agreement_id: UUID
    sppg_id: UUID | None
    journal_entry_id: UUID | None
    disbursement_date: date
    amount: float
    bank_account_id: UUID | None
    reference_number: str | None
    status: str
    notes: str | None


class FundingRepaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    agreement_id: UUID
    journal_entry_id: UUID | None
    repayment_date: date
    principal_amount: float
    margin_amount: float
    penalty_amount: float
    payment_reference: str | None
    status: str
    notes: str | None


class FundingAgreementBundleRead(BaseModel):
    agreement: FundingAgreementRead
    source: FundingSourceRead
    disbursements: list[FundingDisbursementRead]
    repayments: list[FundingRepaymentRead]
    principal_disbursed: float
    principal_repaid: float
    outstanding_principal: float
    realized_margin: float


class FundingSummaryRead(BaseModel):
    totals: dict
    breakdown: dict
