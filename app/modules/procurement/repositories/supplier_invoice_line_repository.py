from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.procurement.models.supplier_invoice_line import SupplierInvoiceLine


class SupplierInvoiceLineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_supplier_invoice(self, supplier_invoice_id: UUID) -> list[SupplierInvoiceLine]:
        result = await self.session.execute(
            select(SupplierInvoiceLine)
            .where(SupplierInvoiceLine.supplier_invoice_id == supplier_invoice_id)
            .order_by(SupplierInvoiceLine.created_at)
        )
        return list(result.scalars().all())

    async def add(self, supplier_invoice_line: SupplierInvoiceLine) -> SupplierInvoiceLine:
        self.session.add(supplier_invoice_line)
        await self.session.flush()
        await self.session.refresh(supplier_invoice_line)
        return supplier_invoice_line
