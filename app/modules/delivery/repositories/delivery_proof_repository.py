from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.delivery.models.delivery_proof import DeliveryProof


class DeliveryProofRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_delivery_order(self, delivery_order_id: UUID) -> list[DeliveryProof]:
        result = await self.session.execute(
            select(DeliveryProof).where(DeliveryProof.delivery_order_id == delivery_order_id).order_by(DeliveryProof.received_at)
        )
        return list(result.scalars().all())

    async def add(self, delivery_proof: DeliveryProof) -> DeliveryProof:
        self.session.add(delivery_proof)
        await self.session.flush()
        await self.session.refresh(delivery_proof)
        return delivery_proof
