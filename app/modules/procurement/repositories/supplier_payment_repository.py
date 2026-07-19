from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.procurement.models.supplier_payment import SupplierPayment


class SupplierPaymentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[SupplierPayment]:
        result = await self.session.execute(select(SupplierPayment).order_by(SupplierPayment.created_at.desc()))
        return list(result.scalars().all())

    async def get_by_id(self, supplier_payment_id: UUID) -> SupplierPayment | None:
        return await self.session.get(SupplierPayment, supplier_payment_id)

    async def get_by_supplier_invoice_id(self, supplier_invoice_id: UUID) -> SupplierPayment | None:
        result = await self.session.execute(
            select(SupplierPayment).where(SupplierPayment.supplier_invoice_id == supplier_invoice_id)
        )
        return result.scalar_one_or_none()

    async def count_by_tenant(self, tenant_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count(SupplierPayment.id)).where(SupplierPayment.tenant_id == tenant_id)
        )
        return int(result.scalar_one())

    async def add(self, supplier_payment: SupplierPayment) -> SupplierPayment:
        self.session.add(supplier_payment)
        await self.session.flush()
        await self.session.refresh(supplier_payment)
        return supplier_payment
