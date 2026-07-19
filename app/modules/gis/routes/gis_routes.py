from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session
from app.core.security.permissions import require_roles
from app.modules.delivery.repositories.delivery_order_repository import DeliveryOrderRepository
from app.modules.geography.repositories.school_repository import SchoolRepository
from app.modules.gis.repositories.service_area_repository import ServiceAreaRepository
from app.modules.gis.schemas.gis_schema import (
    GISAssignmentValidationRead,
    GISAssignmentValidationRequest,
    GISDeliveryRouteItemRead,
    GISDeliveryRouteRead,
    GISNearestKitchenRead,
    GISRiskHeatmapRead,
    GISServiceAreaCreate,
    GISServiceAreaItemRead,
    GISServiceAreaListRead,
    GISServiceAreaUpsert,
    GISServiceCoverageRead,
    GISSppgMapRead,
    GISUnservedSchoolRead,
    GeoJSONFeatureCollection,
)
from app.modules.gis.services.gis_service import GISService
from app.modules.identity.models.user import User
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.responses.envelope import success_response

router = APIRouter()


def parse_bbox(value: str) -> tuple[float, float, float, float]:
    parts = [float(item.strip()) for item in value.split(",")]
    if len(parts) != 4:
        raise ValueError("bbox harus berisi empat angka.")
    min_lon, min_lat, max_lon, max_lat = parts
    if not (-180 <= min_lon < max_lon <= 180):
        raise ValueError("Rentang longitude bbox tidak valid.")
    if not (-90 <= min_lat < max_lat <= 90):
        raise ValueError("Rentang latitude bbox tidak valid.")
    return min_lon, min_lat, max_lon, max_lat


def get_gis_service(session: AsyncSession = Depends(get_db_session)) -> GISService:
    return GISService(
        session,
        SppgRepository(session),
        SchoolRepository(session),
        DeliveryOrderRepository(session),
        ServiceAreaRepository(session),
        TenantRepository(session),
    )


@router.get("/sppg-map")
async def get_sppg_map(request: Request, service: GISService = Depends(get_gis_service)) -> dict:
    payload = await service.sppg_map()
    return success_response(
        code="GIS_SPPG_MAP_FOUND",
        message="Data peta SPPG berhasil diambil.",
        data=GISSppgMapRead.model_validate(payload),
        meta={"request_id": request.state.request_id, "total": len(payload["items"])},
    )


@router.get("/kitchens")
async def get_kitchens_layer(
    request: Request,
    bbox: str,
    snapshot_date: date | None = None,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    metric: str | None = None,
    limit: Annotated[int, Query(ge=1, le=5000)] = 2000,
    service: GISService = Depends(get_gis_service),
) -> dict:
    payload = await service.kitchens_layer(
        bbox=parse_bbox(bbox),
        snapshot_date=snapshot_date,
        status=status_filter,
        metric=metric,
        limit=limit,
    )
    return success_response(
        code="GIS_KITCHEN_LAYER_FOUND",
        message="Layer dapur berhasil diambil.",
        data=GeoJSONFeatureCollection.model_validate(payload),
        meta={"request_id": request.state.request_id, "total": len(payload["features"])},
    )


@router.get("/schools")
async def get_schools_layer(
    request: Request,
    bbox: str | None = None,
    kitchen_id: UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    feedback_min: float | None = None,
    complaint_only: bool = False,
    distribution_min: int | None = None,
    limit: Annotated[int, Query(ge=1, le=5000)] = 2000,
    service: GISService = Depends(get_gis_service),
) -> dict:
    payload = await service.schools_layer(
        bbox=parse_bbox(bbox) if bbox else None,
        kitchen_id=kitchen_id,
        date_from=date_from,
        date_to=date_to,
        feedback_min=feedback_min,
        complaint_only=complaint_only,
        distribution_min=distribution_min,
        limit=limit,
    )
    return success_response(
        code="GIS_SCHOOL_LAYER_FOUND",
        message="Layer sekolah berhasil diambil.",
        data=GeoJSONFeatureCollection.model_validate(payload),
        meta={"request_id": request.state.request_id, "total": len(payload["features"])},
    )


@router.get("/service-coverage")
async def get_service_coverage(
    request: Request,
    sppg_id: UUID | None = Query(default=None),
    service: GISService = Depends(get_gis_service),
) -> dict:
    payload = await service.service_coverage(sppg_id)
    return success_response(
        code="GIS_SERVICE_COVERAGE_FOUND",
        message="Analisa coverage layanan berhasil diambil.",
        data=GISServiceCoverageRead.model_validate(payload),
        meta={"request_id": request.state.request_id, "total": len(payload["items"])},
    )


@router.get("/unserved-schools")
async def get_unserved_schools(request: Request, service: GISService = Depends(get_gis_service)) -> dict:
    payload = await service.unserved_schools()
    return success_response(
        code="GIS_UNSERVED_SCHOOLS_FOUND",
        message="Daftar sekolah yang belum terlayani berhasil diambil.",
        data=GISUnservedSchoolRead.model_validate(payload),
        meta={"request_id": request.state.request_id, "total": len(payload["items"])},
    )


@router.get("/sppg-risk-heatmap")
async def get_sppg_risk_heatmap(request: Request, service: GISService = Depends(get_gis_service)) -> dict:
    payload = await service.risk_heatmap()
    return success_response(
        code="GIS_SPPG_RISK_HEATMAP_FOUND",
        message="Data heatmap risiko SPPG berhasil diambil.",
        data=GISRiskHeatmapRead.model_validate(payload),
        meta={"request_id": request.state.request_id, "total": len(payload["items"])},
    )


@router.get("/heatmaps/distribution")
async def get_distribution_heatmap(request: Request, service: GISService = Depends(get_gis_service)) -> dict:
    payload = await service.distribution_heatmap()
    return success_response(
        code="GIS_DISTRIBUTION_HEATMAP_FOUND",
        message="Heatmap distribusi berhasil diambil.",
        data=GeoJSONFeatureCollection.model_validate(payload),
        meta={"request_id": request.state.request_id, "total": len(payload["features"])},
    )


@router.get("/delivery-routes")
async def get_delivery_routes(request: Request, service: GISService = Depends(get_gis_service)) -> dict:
    payload = await service.delivery_routes()
    return success_response(
        code="GIS_DELIVERY_ROUTES_FOUND",
        message="Data rute delivery berhasil diambil.",
        data=GISDeliveryRouteRead.model_validate(payload),
        meta={"request_id": request.state.request_id, "total": len(payload["items"])},
    )


@router.get("/deliveries/{delivery_id}/route")
async def get_delivery_route(delivery_id: UUID, request: Request, service: GISService = Depends(get_gis_service)) -> dict:
    payload = await service.get_delivery_route(delivery_id)
    return success_response(
        code="GIS_DELIVERY_ROUTE_FOUND",
        message="Detail rute delivery berhasil diambil.",
        data=GISDeliveryRouteItemRead.model_validate(payload),
        meta={"request_id": request.state.request_id},
    )


@router.get("/service-areas")
async def list_service_areas(request: Request, service: GISService = Depends(get_gis_service)) -> dict:
    payload = await service.list_service_areas()
    return success_response(
        code="GIS_SERVICE_AREA_LIST_FOUND",
        message="Daftar service area berhasil diambil.",
        data=GISServiceAreaListRead.model_validate(payload),
        meta={"request_id": request.state.request_id, "total": len(payload["items"])},
    )


@router.get("/service-areas/{service_area_id}")
async def get_service_area(service_area_id: UUID, request: Request, service: GISService = Depends(get_gis_service)) -> dict:
    payload = await service.get_service_area(service_area_id)
    return success_response(
        code="GIS_SERVICE_AREA_FOUND",
        message="Detail service area berhasil diambil.",
        data=GISServiceAreaItemRead.model_validate(payload),
        meta={"request_id": request.state.request_id},
    )


@router.get("/kitchens/{kitchen_id}/service-area")
async def get_kitchen_service_area(kitchen_id: UUID, request: Request, service: GISService = Depends(get_gis_service)) -> dict:
    payload = await service.get_service_area_by_kitchen(kitchen_id)
    return success_response(
        code="GIS_KITCHEN_SERVICE_AREA_FOUND",
        message="Service area dapur berhasil diambil.",
        data=GISServiceAreaItemRead.model_validate(payload),
        meta={"request_id": request.state.request_id},
    )


@router.post("/service-areas", status_code=status.HTTP_201_CREATED)
async def create_service_area(
    payload: GISServiceAreaCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = get_gis_service(session)
    created = await service.create_service_area(payload)
    await session.commit()
    return success_response(
        code="GIS_SERVICE_AREA_CREATED",
        message="Service area berhasil dibuat.",
        data=GISServiceAreaItemRead.model_validate(created),
        meta={"request_id": request.state.request_id},
    )


@router.put("/kitchens/{kitchen_id}/service-area")
async def upsert_kitchen_service_area(
    kitchen_id: UUID,
    payload: GISServiceAreaUpsert,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles("super_admin", "tenant_admin", "operations_manager")),
) -> dict:
    service = get_gis_service(session)
    updated = await service.upsert_service_area(kitchen_id, payload)
    await session.commit()
    return success_response(
        code="GIS_KITCHEN_SERVICE_AREA_SAVED",
        message="Service area dapur berhasil disimpan.",
        data=GISServiceAreaItemRead.model_validate(updated),
        meta={"request_id": request.state.request_id},
    )


@router.get("/schools/{school_id}/nearest-kitchens")
async def get_nearest_kitchens(
    school_id: UUID,
    request: Request,
    limit: Annotated[int, Query(ge=1, le=20)] = 5,
    service: GISService = Depends(get_gis_service),
) -> dict:
    payload = await service.nearest_kitchens(school_id, limit=limit)
    return success_response(
        code="GIS_NEAREST_KITCHENS_FOUND",
        message="Daftar dapur terdekat berhasil diambil.",
        data=GISNearestKitchenRead.model_validate(payload),
        meta={"request_id": request.state.request_id, "total": len(payload["items"])},
    )


@router.post("/assignments/validate")
async def validate_assignment(
    payload: GISAssignmentValidationRequest,
    request: Request,
    service: GISService = Depends(get_gis_service),
) -> dict:
    result = await service.validate_assignment(payload)
    return success_response(
        code="GIS_ASSIGNMENT_VALIDATED",
        message="Validasi assignment GIS berhasil diproses.",
        data=GISAssignmentValidationRead.model_validate(result),
        meta={"request_id": request.state.request_id},
    )
