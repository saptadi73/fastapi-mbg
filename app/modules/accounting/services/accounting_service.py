from datetime import datetime, timezone
from uuid import UUID

from app.modules.accounting.models.account import Account
from app.modules.accounting.models.journal_entry import JournalEntry
from app.modules.accounting.models.journal_line import JournalLine
from app.modules.accounting.repositories.account_repository import AccountRepository
from app.modules.accounting.repositories.journal_entry_repository import JournalEntryRepository
from app.modules.accounting.repositories.journal_line_repository import JournalLineRepository
from app.modules.accounting.schemas.accounting_schema import AccountCreate, JournalEntryCreate
from app.modules.identity.models.user import User
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, ConflictException, NotFoundException


class AccountingService:
    def __init__(
        self,
        account_repository: AccountRepository,
        journal_entry_repository: JournalEntryRepository,
        journal_line_repository: JournalLineRepository,
        tenant_repository: TenantRepository,
    ) -> None:
        self.account_repository = account_repository
        self.journal_entry_repository = journal_entry_repository
        self.journal_line_repository = journal_line_repository
        self.tenant_repository = tenant_repository

    async def list_accounts(self) -> list[Account]:
        return await self.account_repository.list_all()

    async def get_account_by_code(self, tenant_id: UUID, code: str) -> Account | None:
        return await self.account_repository.get_by_tenant_and_code(tenant_id, code)

    async def create_account(self, payload: AccountCreate) -> Account:
        tenant_id = UUID(payload.tenant_id)
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant untuk account tidak ditemukan.")
        existing = await self.account_repository.get_by_tenant_and_code(tenant_id, payload.code)
        if existing is not None:
            raise ConflictException(code="ACCOUNT_CODE_ALREADY_EXISTS", message="Kode account sudah digunakan.")
        if payload.normal_balance not in {"DEBIT", "CREDIT"}:
            raise BadRequestException(code="INVALID_NORMAL_BALANCE", message="Normal balance harus DEBIT atau CREDIT.")
        account = Account(
            tenant_id=tenant_id,
            code=payload.code,
            name=payload.name,
            category=payload.category,
            normal_balance=payload.normal_balance,
            allow_posting=payload.allow_posting,
            is_active=payload.is_active,
        )
        return await self.account_repository.add(account)

    async def list_journal_entries(self) -> list[JournalEntry]:
        return await self.journal_entry_repository.list_all()

    async def get_journal_entry_bundle(self, journal_entry_id: UUID) -> dict:
        journal_entry = await self.journal_entry_repository.get_by_id(journal_entry_id)
        if journal_entry is None:
            raise NotFoundException(code="JOURNAL_ENTRY_NOT_FOUND", message="Journal entry tidak ditemukan.")
        lines = await self.journal_line_repository.list_by_journal_entry(journal_entry_id)
        return {"journal_entry": journal_entry, "lines": lines}

    async def create_journal_entry(self, payload: JournalEntryCreate) -> dict:
        tenant_id = UUID(payload.tenant_id)
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant untuk journal entry tidak ditemukan.")
        debit_total = round(sum(line.amount for line in payload.lines if line.line_type == "DEBIT"), 6)
        credit_total = round(sum(line.amount for line in payload.lines if line.line_type == "CREDIT"), 6)
        if debit_total <= 0 or credit_total <= 0 or debit_total != credit_total:
            raise BadRequestException(
                code="JOURNAL_ENTRY_NOT_BALANCED",
                message="Total debit dan credit harus sama dan lebih besar dari nol.",
            )
        next_number = await self.journal_entry_repository.count_by_tenant(tenant_id) + 1
        journal_entry = await self.journal_entry_repository.add(
            JournalEntry(
                tenant_id=tenant_id,
                entry_number=f"JE-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}",
                entry_date=payload.entry_date,
                reference=payload.reference,
                description=payload.description,
                source_module=payload.source_module,
                source_document_type=payload.source_document_type,
                source_document_id=UUID(payload.source_document_id) if payload.source_document_id else None,
                status="DRAFT",
                posted_at=None,
                posted_by=None,
            )
        )
        created_lines: list[JournalLine] = []
        for line in payload.lines:
            account = await self.account_repository.get_by_id(UUID(line.account_id))
            if account is None or account.tenant_id != tenant_id:
                raise NotFoundException(code="ACCOUNT_NOT_FOUND", message="Account journal line tidak ditemukan.")
            created_lines.append(
                await self.journal_line_repository.add(
                    JournalLine(
                        tenant_id=tenant_id,
                        journal_entry_id=journal_entry.id,
                        account_id=account.id,
                        line_type=line.line_type,
                        amount=line.amount,
                        description=line.description,
                    )
                )
            )
        return {"journal_entry": journal_entry, "lines": created_lines}

    async def post_journal_entry(self, journal_entry_id: UUID, actor: User) -> dict:
        journal_entry = await self.journal_entry_repository.get_by_id(journal_entry_id)
        if journal_entry is None:
            raise NotFoundException(code="JOURNAL_ENTRY_NOT_FOUND", message="Journal entry tidak ditemukan.")
        if journal_entry.status != "DRAFT":
            raise BadRequestException(code="JOURNAL_ENTRY_POST_INVALID_STATUS", message="Hanya jurnal DRAFT yang bisa diposting.")
        lines = await self.journal_line_repository.list_by_journal_entry(journal_entry_id)
        debit_total = round(sum(line.amount for line in lines if line.line_type == "DEBIT"), 6)
        credit_total = round(sum(line.amount for line in lines if line.line_type == "CREDIT"), 6)
        if debit_total <= 0 or debit_total != credit_total:
            raise BadRequestException(code="JOURNAL_ENTRY_NOT_BALANCED", message="Journal entry tidak balance.")
        journal_entry.status = "POSTED"
        journal_entry.posted_at = datetime.now(timezone.utc)
        journal_entry.posted_by = actor.id
        return {"journal_entry": journal_entry, "lines": lines}

    async def create_and_post_operational_journal(
        self,
        *,
        tenant_id: UUID,
        entry_date,
        reference: str | None,
        description: str,
        source_module: str,
        source_document_type: str,
        source_document_id: UUID | None,
        debit_account_code: str,
        credit_account_code: str,
        amount: float,
        actor: User,
    ) -> dict:
        if amount <= 0:
            raise BadRequestException(code="INVALID_JOURNAL_AMOUNT", message="Nilai jurnal harus lebih besar dari nol.")
        debit_account = await self.get_account_by_code(tenant_id, debit_account_code)
        if debit_account is None:
            raise NotFoundException(code="ACCOUNT_NOT_FOUND", message=f"Account debit {debit_account_code} tidak ditemukan.")
        credit_account = await self.get_account_by_code(tenant_id, credit_account_code)
        if credit_account is None:
            raise NotFoundException(code="ACCOUNT_NOT_FOUND", message=f"Account credit {credit_account_code} tidak ditemukan.")

        bundle = await self.create_journal_entry(
            JournalEntryCreate(
                tenant_id=str(tenant_id),
                entry_date=entry_date,
                reference=reference,
                description=description,
                source_module=source_module,
                source_document_type=source_document_type,
                source_document_id=str(source_document_id) if source_document_id else None,
                lines=[
                    {"account_id": str(debit_account.id), "line_type": "DEBIT", "amount": round(amount, 6), "description": description},
                    {"account_id": str(credit_account.id), "line_type": "CREDIT", "amount": round(amount, 6), "description": description},
                ],
            )
        )
        return await self.post_journal_entry(bundle["journal_entry"].id, actor)
