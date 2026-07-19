from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    code: str
    name: str
    category: str
    normal_balance: str
    allow_posting: bool
    is_active: bool


class AccountCreate(BaseModel):
    tenant_id: str
    code: str
    name: str
    category: str
    normal_balance: str
    allow_posting: bool = True
    is_active: bool = True


class JournalLineCreate(BaseModel):
    account_id: str
    line_type: str
    amount: float = Field(gt=0)
    description: str | None = None


class JournalEntryCreate(BaseModel):
    tenant_id: str
    entry_date: date
    reference: str | None = None
    description: str
    source_module: str
    source_document_type: str
    source_document_id: str | None = None
    lines: list[JournalLineCreate]


class JournalLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    journal_entry_id: UUID
    account_id: UUID
    line_type: str
    amount: float
    description: str | None


class JournalEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    entry_number: str
    entry_date: date
    reference: str | None
    description: str
    source_module: str
    source_document_type: str
    source_document_id: UUID | None
    status: str
    posted_at: datetime | None
    posted_by: UUID | None


class JournalEntryBundleRead(BaseModel):
    journal_entry: JournalEntryRead
    lines: list[JournalLineRead]
