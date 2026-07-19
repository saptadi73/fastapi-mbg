import math
from datetime import datetime, timezone
from uuid import UUID

from app.modules.delivery.models.delivery_incident import DeliveryIncident
from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.modules.delivery.models.delivery_order import DeliveryOrder
from app.modules.delivery.models.delivery_proof import DeliveryProof
from app.modules.delivery.models.delivery_route import DeliveryRoute
from app.modules.delivery.models.delivery_route_stop import DeliveryRouteStop
from app.modules.delivery.repositories.delivery_incident_repository import DeliveryIncidentRepository
from app.modules.delivery.repositories.delivery_order_repository import DeliveryOrderRepository
from app.modules.delivery.repositories.delivery_proof_repository import DeliveryProofRepository
from app.modules.delivery.repositories.delivery_route_repository import DeliveryRouteRepository
from app.modules.delivery.repositories.delivery_route_stop_repository import DeliveryRouteStopRepository
from app.modules.delivery.schemas.delivery_schema import (
    DeliveryCreateFromProduction,
    DeliveryIncidentCreate,
    DeliveryProofCreate,
    DeliveryRouteCreate,
)
from app.modules.geography.repositories.school_repository import SchoolRepository
from app.modules.production.services.production_service import PRODUCTION_COMPLETED, ProductionService
from app.modules.quality.services.quality_service import QualityService
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, NotFoundException

DELIVERY_PLANNED = "PLANNED"
DELIVERY_LOADING = "LOADING"
DELIVERY_IN_TRANSIT = "IN_TRANSIT"
DELIVERY_ARRIVED = "ARRIVED"
DELIVERY_RECEIVED = "RECEIVED"
DELIVERY_PARTIALLY_RECEIVED = "PARTIALLY_RECEIVED"
DELIVERY_REJECTED = "REJECTED"
DELIVERY_CANCELLED = "CANCELLED"


class DeliveryService:
    def __init__(
        self,
        delivery_order_repository: DeliveryOrderRepository,
        delivery_proof_repository: DeliveryProofRepository,
        delivery_route_repository: DeliveryRouteRepository,
        delivery_route_stop_repository: DeliveryRouteStopRepository,
        delivery_incident_repository: DeliveryIncidentRepository,
        tenant_repository: TenantRepository,
        sppg_repository: SppgRepository,
        school_repository: SchoolRepository,
        production_service: ProductionService,
        quality_service: QualityService | None = None,
    ) -> None:
        self.delivery_order_repository = delivery_order_repository
        self.delivery_proof_repository = delivery_proof_repository
        self.delivery_route_repository = delivery_route_repository
        self.delivery_route_stop_repository = delivery_route_stop_repository
        self.delivery_incident_repository = delivery_incident_repository
        self.tenant_repository = tenant_repository
        self.sppg_repository = sppg_repository
        self.school_repository = school_repository
        self.production_service = production_service
        self.quality_service = quality_service

    def _get_scope(self) -> tuple[UUID | None, UUID | None]:
        tenant_id = None
        sppg_id = None
        current_tenant = get_current_tenant()
        current_sppg = get_current_sppg()
        if current_tenant is not None:
            try:
                tenant_id = UUID(current_tenant)
            except ValueError as exc:
                raise BadRequestException(
                    code="INVALID_TENANT_CONTEXT",
                    message="Header X-Tenant-ID tidak valid.",
                ) from exc
        if current_sppg is not None:
            try:
                sppg_id = UUID(current_sppg)
            except ValueError as exc:
                raise BadRequestException(
                    code="INVALID_SPPG_CONTEXT",
                    message="Header X-SPPG-ID tidak valid.",
                ) from exc
        return tenant_id, sppg_id

    @staticmethod
    def _format_gps(latitude: float, longitude: float) -> str:
        return f"{latitude:.6f},{longitude:.6f}"

    @staticmethod
    def _distance_km(start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> float:
        radius = 6371.0
        lat1 = math.radians(start_lat)
        lat2 = math.radians(end_lat)
        delta_lat = math.radians(end_lat - start_lat)
        delta_lon = math.radians(end_lon - start_lon)
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
        return radius * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

    async def _build_delivery_bundle(self, delivery_order: DeliveryOrder) -> dict:
        route = None
        route_stops: list[DeliveryRouteStop] = []
        incidents = await self.delivery_incident_repository.list_by_delivery_order(delivery_order.id)
        if delivery_order.route_id is not None:
            route = await self.delivery_route_repository.get_by_id(delivery_order.route_id)
            route_stops = await self.delivery_route_stop_repository.list_by_route(delivery_order.route_id)
            if route is not None:
                incidents = await self.delivery_incident_repository.list_by_route(route.id)
        proofs = await self.delivery_proof_repository.list_by_delivery_order(delivery_order.id)
        return {
            "delivery_order": delivery_order,
            "route": route,
            "route_stops": route_stops,
            "incidents": incidents,
            "proofs": proofs,
        }

    async def list_delivery_orders(self) -> list[DeliveryOrder]:
        tenant_id, sppg_id = self._get_scope()
        return await self.delivery_order_repository.list_all(tenant_id=tenant_id, sppg_id=sppg_id)

    async def get_delivery_order(self, delivery_order_id: UUID) -> dict:
        tenant_id, sppg_id = self._get_scope()
        if tenant_id is None and sppg_id is None:
            delivery_order = await self.delivery_order_repository.get_by_id(delivery_order_id)
        else:
            delivery_order = await self.delivery_order_repository.get_by_id_and_scope(
                delivery_order_id,
                tenant_id=tenant_id,
                sppg_id=sppg_id,
            )
        if delivery_order is None:
            raise NotFoundException(code="DELIVERY_ORDER_NOT_FOUND", message="Delivery order tidak ditemukan.")
        return await self._build_delivery_bundle(delivery_order)

    async def list_routes(self) -> list[DeliveryRoute]:
        tenant_id, sppg_id = self._get_scope()
        return await self.delivery_route_repository.list_all(tenant_id=tenant_id, sppg_id=sppg_id)

    async def get_route(self, route_id: UUID) -> dict:
        tenant_id, sppg_id = self._get_scope()
        route = await self.delivery_route_repository.get_by_id_and_scope(route_id, tenant_id=tenant_id, sppg_id=sppg_id)
        if route is None:
            raise NotFoundException(code="DELIVERY_ROUTE_NOT_FOUND", message="Route delivery tidak ditemukan.")
        stops = await self.delivery_route_stop_repository.list_by_route(route.id)
        incidents = await self.delivery_incident_repository.list_by_route(route.id)
        return {"route": route, "stops": stops, "incidents": incidents}

    async def create_from_production_order(self, production_order_id: UUID, payload: DeliveryCreateFromProduction) -> dict:
        production_order = await self.production_service.get_production_order(production_order_id)
        if production_order.status != PRODUCTION_COMPLETED:
            raise BadRequestException(
                code="PRODUCTION_ORDER_NOT_READY_FOR_DELIVERY",
                message="Production order harus selesai sebelum dibuat delivery order.",
            )
        if self.quality_service is not None:
            await self.quality_service.validate_release_for_reference("PRODUCTION_ORDER", production_order.id)
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
        return await self._build_delivery_bundle(delivery_order)

    async def create_route(self, payload: DeliveryRouteCreate) -> dict:
        if not payload.stops:
            raise BadRequestException(code="DELIVERY_ROUTE_STOPS_REQUIRED", message="Route harus memiliki minimal satu stop.")

        delivery_order_ids = [UUID(stop.delivery_order_id) for stop in payload.stops]
        delivery_orders = await self.delivery_order_repository.list_by_ids(delivery_order_ids)
        if len(delivery_orders) != len(delivery_order_ids):
            raise NotFoundException(code="DELIVERY_ORDER_NOT_FOUND", message="Salah satu delivery order tidak ditemukan.")

        orders_by_id = {order.id: order for order in delivery_orders}
        first_order = delivery_orders[0]
        for delivery_order_id in delivery_order_ids:
            order = orders_by_id[delivery_order_id]
            if order.tenant_id != first_order.tenant_id or order.sppg_id != first_order.sppg_id:
                raise BadRequestException(
                    code="DELIVERY_ROUTE_SCOPE_MISMATCH",
                    message="Semua delivery order dalam satu route harus berasal dari tenant dan SPPG yang sama.",
                )

        sppg = await self.sppg_repository.get_by_id(first_order.sppg_id)
        if sppg is None:
            raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG route tidak ditemukan.")

        next_number = await self.delivery_route_repository.count_by_tenant(first_order.tenant_id) + 1
        total_distance_km = 0.0
        current_lat = sppg.latitude
        current_lon = sppg.longitude
        destination_gps = None
        route = await self.delivery_route_repository.add(
            DeliveryRoute(
                tenant_id=first_order.tenant_id,
                sppg_id=first_order.sppg_id,
                route_code=f"RT-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}",
                route_name=payload.route_name,
                route_status=DELIVERY_PLANNED,
                planned_departure=payload.planned_departure,
                actual_departure=None,
                planned_arrival=payload.planned_arrival,
                actual_arrival=None,
                origin_gps=self._format_gps(sppg.latitude, sppg.longitude),
                destination_gps=None,
                total_distance_km=None,
                notes=payload.notes,
            )
        )

        for sequence, stop_payload in enumerate(payload.stops, start=1):
            delivery_order = orders_by_id[UUID(stop_payload.delivery_order_id)]
            school = await self.school_repository.get_by_id(delivery_order.school_id)
            if school is None:
                raise NotFoundException(code="SCHOOL_NOT_FOUND", message="Sekolah stop delivery tidak ditemukan.")
            stop_gps = stop_payload.stop_gps or self._format_gps(school.latitude, school.longitude)
            total_distance_km += self._distance_km(current_lat, current_lon, school.latitude, school.longitude)
            current_lat = school.latitude
            current_lon = school.longitude
            destination_gps = stop_gps

            await self.delivery_route_stop_repository.add(
                DeliveryRouteStop(
                    tenant_id=delivery_order.tenant_id,
                    route_id=route.id,
                    delivery_order_id=delivery_order.id,
                    school_id=delivery_order.school_id,
                    stop_sequence=sequence,
                    planned_arrival=stop_payload.planned_arrival or delivery_order.planned_arrival,
                    actual_arrival=None,
                    planned_departure=stop_payload.planned_departure,
                    actual_departure=None,
                    status=DELIVERY_PLANNED,
                    recipient_name=stop_payload.recipient_name or delivery_order.receiver_name,
                    stop_gps=stop_gps,
                    notes=stop_payload.notes,
                )
            )
            delivery_order.route_id = route.id
            if delivery_order.status == DELIVERY_IN_TRANSIT:
                delivery_order.status = DELIVERY_LOADING

        route.destination_gps = destination_gps
        route.total_distance_km = round(total_distance_km, 3)
        return await self.get_route(route.id)

    async def record_incident(self, delivery_order_id: UUID, payload: DeliveryIncidentCreate) -> dict:
        delivery_order = await self.delivery_order_repository.get_by_id(delivery_order_id)
        if delivery_order is None:
            raise NotFoundException(code="DELIVERY_ORDER_NOT_FOUND", message="Delivery order tidak ditemukan.")

        route_stop_id = UUID(payload.route_stop_id) if payload.route_stop_id else None
        if route_stop_id is not None:
            route_stop = await self.delivery_route_stop_repository.get_by_id(route_stop_id)
            if route_stop is None or route_stop.delivery_order_id != delivery_order.id:
                raise BadRequestException(
                    code="DELIVERY_ROUTE_STOP_INVALID",
                    message="Route stop tidak sesuai dengan delivery order.",
                )
        incident = await self.delivery_incident_repository.add(
            DeliveryIncident(
                tenant_id=delivery_order.tenant_id,
                delivery_order_id=delivery_order.id,
                route_id=delivery_order.route_id,
                route_stop_id=route_stop_id,
                incident_time=payload.incident_time,
                category=payload.category,
                severity=payload.severity,
                title=payload.title,
                description=payload.description,
                incident_gps=payload.incident_gps,
                temperature_celsius=payload.temperature_celsius,
                media_urls=payload.media_urls,
                status=payload.status,
                resolution_notes=payload.resolution_notes,
            )
        )
        return {"incident": incident, "delivery": await self._build_delivery_bundle(delivery_order)}

    async def record_proof(self, delivery_order_id: UUID, payload: DeliveryProofCreate) -> dict:
        delivery_order = await self.delivery_order_repository.get_by_id(delivery_order_id)
        if delivery_order is None:
            raise NotFoundException(code="DELIVERY_ORDER_NOT_FOUND", message="Delivery order tidak ditemukan.")
        if delivery_order.status not in {DELIVERY_PLANNED, DELIVERY_LOADING, DELIVERY_IN_TRANSIT, DELIVERY_ARRIVED}:
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
        route_stop_id = UUID(payload.route_stop_id) if payload.route_stop_id else None
        if route_stop_id is not None:
            route_stop = await self.delivery_route_stop_repository.get_by_id(route_stop_id)
            if route_stop is None or route_stop.delivery_order_id != delivery_order.id:
                raise BadRequestException(
                    code="DELIVERY_ROUTE_STOP_INVALID",
                    message="Route stop tidak sesuai dengan delivery order.",
                )

        proof = await self.delivery_proof_repository.add(
            DeliveryProof(
                tenant_id=delivery_order.tenant_id,
                delivery_order_id=delivery_order.id,
                route_id=delivery_order.route_id,
                route_stop_id=route_stop_id,
                received_at=payload.received_at,
                receiver_name=payload.receiver_name,
                receiver_gps=payload.receiver_gps,
                received_portions=payload.received_portions,
                rejected_portions=payload.rejected_portions,
                temperature_celsius=payload.temperature_celsius,
                condition_status=payload.condition_status,
                condition_notes=payload.condition_notes,
                photo_urls=payload.photo_urls,
                signature_name=payload.signature_name,
                signature_url=payload.signature_url,
                signature_signed_at=payload.signature_signed_at,
                incident_notes=payload.incident_notes,
                linked_incident_ids=payload.linked_incident_ids,
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

        if delivery_order.route_id is not None:
            route = await self.delivery_route_repository.get_by_id(delivery_order.route_id)
            if route is not None:
                route.actual_arrival = payload.received_at
                route.route_status = DELIVERY_ARRIVED if delivery_order.status in {DELIVERY_PARTIALLY_RECEIVED, DELIVERY_RECEIVED} else route.route_status
            if route_stop_id is not None:
                route_stop = await self.delivery_route_stop_repository.get_by_id(route_stop_id)
                if route_stop is not None:
                    route_stop.actual_arrival = payload.received_at
                    route_stop.status = delivery_order.status

        return await self._build_delivery_bundle(delivery_order)
