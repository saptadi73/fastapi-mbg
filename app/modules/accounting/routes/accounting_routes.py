from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.dependencies import get_current_user
from app.core.security.permissions import require_roles
from app.modules.accounting.repositories.account_repository import AccountRepository
from app.modules.accounting.repositories.journal_entry_repository import JournalEntryRepository
from app.modules.accounting.repositories.journal_line_repository import JournalLineRepository
from app.modules.accounting.schemas.accounting_schema import (
    AccountCreate,
    AccountRead,
    JournalEntryBundleRead,
    JournalEntryCreate,
    JournalEntryRead,
)
from app.modules.accounting.services.accounting_service import AccountingService
from app.modules.identity.models.user import User
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.responses.envelope import success_response

router = APIRouter()


def get_accounting_service(session: AsyncSession = Depends(get_db_session)) -> AccountingService:
    return AccountingService(
        AccountRepository(session),
        JournalEntryRepository(session),
        JournalLineRepository(session),
        TenantRepository(session),
    )


@router.get("/accounts")
async def list_accounts(request: Request, service: AccountingService = Depends(get_accounting_service)) -> dict:
    items = [AccountRead.model_validate(item) for item in await service.list_accounts()]
    return success_response(
        code="ACCOUNT_LIST_FOUND",
        message="Daftar account berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.post("/accounts", status_code=status.HTTP_201_CREATED)
async def create_account(
    payload: AccountCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "finance_manager")),
) -> dict:
    service = get_accounting_service(session)
    account = await service.create_account(payload)
    await session.commit()
    return success_response(
        code="ACCOUNT_CREATED",
        message="Account berhasil dibuat.",
        data=AccountRead.model_validate(account),
        meta={"request_id": request.state.request_id},
    )


@router.get("/journal-entries")
async def list_journal_entries(request: Request, service: AccountingService = Depends(get_accounting_service)) -> dict:
    items = [JournalEntryRead.model_validate(item) for item in await service.list_journal_entries()]
    return success_response(
        code="JOURNAL_ENTRY_LIST_FOUND",
        message="Daftar journal entry berhasil diambil.",
        data=items,
        meta={"request_id": request.state.request_id, "total": len(items)},
    )


@router.get("/journal-entries/{journal_entry_id}")
async def get_journal_entry(
    journal_entry_id: UUID,
    request: Request,
    service: AccountingService = Depends(get_accounting_service),
) -> dict:
    bundle = await service.get_journal_entry_bundle(journal_entry_id)
    return success_response(
        code="JOURNAL_ENTRY_FOUND",
        message="Detail journal entry berhasil diambil.",
        data=JournalEntryBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id},
    )


@router.post("/journal-entries", status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    payload: JournalEntryCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "finance_manager")),
) -> dict:
    service = get_accounting_service(session)
    bundle = await service.create_journal_entry(payload)
    await session.commit()
    return success_response(
        code="JOURNAL_ENTRY_CREATED",
        message="Journal entry berhasil dibuat.",
        data=JournalEntryBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id, "total": len(bundle["lines"])},
    )


@router.post("/journal-entries/{journal_entry_id}/post")
async def post_journal_entry(
    journal_entry_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "finance_manager")),
) -> dict:
    service = get_accounting_service(session)
    bundle = await service.post_journal_entry(journal_entry_id, current_user)
    await session.commit()
    return success_response(
        code="JOURNAL_ENTRY_POSTED",
        message="Journal entry berhasil diposting.",
        data=JournalEntryBundleRead.model_validate(bundle),
        meta={"request_id": request.state.request_id, "total": len(bundle["lines"])},
    )
