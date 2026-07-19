from datetime import datetime, timezone
from uuid import UUID

from app.modules.delivery.models.delivery_order import DeliveryOrder
from app.modules.delivery.models.delivery_proof import DeliveryProof
from app.modules.delivery.repositories.delivery_order_repository import DeliveryOrderRepository
from app.modules.delivery.repositories.delivery_proof_repository import DeliveryProofRepository
from app.modules.delivery.schemas.delivery_schema import DeliveryCreateFromProduction, DeliveryProofCreate
from app.modules.geography.repositories.school_repository import SchoolRepository
from app.modules.production.services.production_service import PRODUCTION_COMPLETED, ProductionService
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, NotFoundException

DELIVERY_PLANNED = "PLANNED"
DELIVERY_IN_TRANSIT = "IN_TRANSIT"
DELIVERY_RECEIVED = "RECEIVED"
DELIVERY_PARTIALLY_RECEIVED = "PARTIALLY_RECEIVED"
DELIVERY_REJECTED = "REJECTED"


class DeliveryService:
    def __init__(
        self,
        delivery_order_repository: DeliveryOrderRepository,
        delivery_proof_repository: DeliveryProofRepository,
        tenant_repository: TenantRepository,
        sppg_repository: SppgRepository,
        school_repository: SchoolRepository,
        production_service: ProductionService,
    ) -> None:
        self.delivery_order_repository = delivery_order_repository
        self.delivery_proof_repository = delivery_proof_repository
        self.tenant_repository = tenant_repository
        self.sppg_repository = sppg_repository
        self.school_repository = school_repository
        self.production_service = production_service

    async def list_delivery_orders(self) -> list[DeliveryOrder]:
        return await self.delivery_order_repository.list_all()

    async def get_delivery_order(self, delivery_order_id: UUID) -> dict:
        delivery_order = await self.delivery_order_repository.get_by_id(delivery_order_id)
        if delivery_order is None:
            raise NotFoundException(code="DELIVERY_ORDER_NOT_FOUND", message="Delivery order tidak ditemukan.")
        proofs = await self.delivery_proof_repository.list_by_delivery_order(delivery_order_id)
        return {"delivery_order": delivery_order, "proofs": proofs}

    async def create_from_production_order(self, production_order_id: UUID, payload: DeliveryCreateFromProduction) -> dict:
        production_order = await self.production_service.get_production_order(production_order_id)
        if production_order.status != PRODUCTION_COMPLETED:
            raise BadRequestException(
                code="PRODUCTION_ORDER_NOT_READY_FOR_DELIVERY",
                message="Production order harus selesai sebelum dibuat delivery order.",
            )
        if await self.tenant_repository.get_by_id(production_order.tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant delivery tidak ditemukan.")
        if await self.sppg_repository.get_by_id(production_order.sppg_id) is None:
            raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG delivery tidak ditemukan.")
        school_id = UUID(payload.school_id)
        school = await self.school_repository.get_by_id(school_id)
        if school is None or school.tenant_id != production_order.tenant_id:
            raise NotFoundException(code="SCHOOL_NOT_FOUND", message="Sekolah tujuan delivery tidak ditemukan.")

        next_number = await self.delivery_order_repository.count_by_tenant(production_order.tenant_id) + 1
        shipped_portions = production_order.accepted_portions or production_order.actual_portions or production_order.planned_portions
        delivery_order = await self.delivery_order_repository.add(
            DeliveryOrder(
                tenant_id=production_order.tenant_id,
                sppg_id=production_order.sppg_id,
                production_order_id=production_order.id,
                school_id=school_id,
                delivery_number=f"DO-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}",
                planned_departure=payload.planned_departure,
                actual_departure=datetime.now(timezone.utc),
                planned_arrival=payload.planned_arrival,
                actual_arrival=None,
                planned_portions=production_order.planned_portions,
                shipped_portions=shipped_portions,
                received_portions=None,
                rejected_portions=None,
                status=DELIVERY_IN_TRANSIT,
                receiver_name=payload.receiver_name,
                receiver_gps=None,
            )
        )
        return {"delivery_order": delivery_order, "proofs": []}

    async def record_proof(self, delivery_order_id: UUID, payload: DeliveryProofCreate) -> dict:
        delivery_order = await self.delivery_order_repository.get_by_id(delivery_order_id)
        if delivery_order is None:
            raise NotFoundException(code="DELIVERY_ORDER_NOT_FOUND", message="Delivery order tidak ditemukan.")
        if delivery_order.status not in {DELIVERY_PLANNED, DELIVERY_IN_TRANSIT}:
            raise BadRequestException(
                code="DELIVERY_PROOF_INVALID_STATUS",
                message="Proof of delivery hanya bisa dicatat untuk delivery yang masih aktif.",
            )
        shipped = delivery_order.shipped_portions or delivery_order.planned_portions
        total_received = payload.received_portions + payload.rejected_portions
        if total_received > shipped:
            raise BadRequestException(
                code="DELIVERY_RECEIPT_EXCEEDS_SHIPPED",
                message="Porsi diterima melebihi jumlah yang dikirim.",
            )

        proof = await self.delivery_proof_repository.add(
            DeliveryProof(
                tenant_id=delivery_order.tenant_id,
                delivery_order_id=delivery_order.id,
                received_at=payload.received_at,
                receiver_name=payload.receiver_name,
                receiver_gps=payload.receiver_gps,
                received_portions=payload.received_portions,
                rejected_portions=payload.rejected_portions,
                temperature_celsius=payload.temperature_celsius,
                condition_notes=payload.condition_notes,
            )
        )

        delivery_order.actual_arrival = payload.received_at
        delivery_order.receiver_name = payload.receiver_name
        delivery_order.receiver_gps = payload.receiver_gps
        delivery_order.received_portions = payload.received_portions
        delivery_order.rejected_portions = payload.rejected_portions

        if payload.received_portions == 0 and payload.rejected_portions > 0:
            delivery_order.status = DELIVERY_REJECTED
        elif payload.received_portions < shipped:
            delivery_order.status = DELIVERY_PARTIALLY_RECEIVED
        else:
            delivery_order.status = DELIVERY_RECEIVED

        proofs = await self.delivery_proof_repository.list_by_delivery_order(delivery_order.id)
        return {"delivery_order": delivery_order, "proofs": proofs}
