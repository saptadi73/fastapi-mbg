from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.procurement.models.supplier_invoice import SupplierInvoice


class SupplierInvoiceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[SupplierInvoice]:
        result = await self.session.execute(select(SupplierInvoice).order_by(SupplierInvoice.created_at.desc()))
        return list(result.scalars().all())

    async def get_by_id(self, supplier_invoice_id: UUID) -> SupplierInvoice | None:
        return await self.session.get(SupplierInvoice, supplier_invoice_id)

    async def get_by_goods_receipt_id(self, goods_receipt_id: UUID) -> SupplierInvoice | None:
        result = await self.session.execute(
            select(SupplierInvoice).where(SupplierInvoice.goods_receipt_id == goods_receipt_id)
        )
        return result.scalar_one_or_none()

    async def count_by_tenant(self, tenant_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count(SupplierInvoice.id)).where(SupplierInvoice.tenant_id == tenant_id)
        )
        return int(result.scalar_one())

    async def add(self, supplier_invoice: SupplierInvoice) -> SupplierInvoice:
        self.session.add(supplier_invoice)
        await self.session.flush()
        await self.session.refresh(supplier_invoice)
        return supplier_invoice
