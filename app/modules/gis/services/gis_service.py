import json
from datetime import date
from uuid import UUID

from geoalchemy2.elements import WKTElement
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.settings import get_settings
from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.modules.delivery.repositories.delivery_order_repository import DeliveryOrderRepository
from app.modules.geography.repositories.school_repository import SchoolRepository
from app.modules.gis.models.service_area import ServiceArea
from app.modules.gis.repositories.service_area_repository import ServiceAreaRepository
from app.modules.sppg.models.sppg import Sppg
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, NotFoundException


class GISService:
    def __init__(
        self,
        session: AsyncSession,
        sppg_repository: SppgRepository,
        school_repository: SchoolRepository,
        delivery_order_repository: DeliveryOrderRepository,
        service_area_repository: ServiceAreaRepository,
        tenant_repository: TenantRepository,
    ) -> None:
        self.session = session
        self.sppg_repository = sppg_repository
        self.school_repository = school_repository
        self.delivery_order_repository = delivery_order_repository
        self.service_area_repository = service_area_repository
        self.tenant_repository = tenant_repository
        self.settings = get_settings()

    def _get_scope(self) -> tuple[UUID | None, UUID | None]:
        return (
            self._parse_scope_uuid(get_current_tenant(), "INVALID_TENANT_CONTEXT", "Header X-Tenant-ID tidak valid."),
            self._parse_scope_uuid(get_current_sppg(), "INVALID_SPPG_CONTEXT", "Header X-SPPG-ID tidak valid."),
        )

    @staticmethod
    def _parse_scope_uuid(value: str | None, code: str, message: str) -> UUID | None:
        if value is None:
            return None
        try:
            return UUID(value)
        except ValueError as exc:
            raise BadRequestException(code=code, message=message) from exc

    def _require_tenant_scope(self) -> UUID:
        tenant_id, _ = self._get_scope()
        if tenant_id is None:
            raise BadRequestException(
                code="TENANT_CONTEXT_REQUIRED",
                message="Header X-Tenant-ID wajib dikirim untuk endpoint GIS ini.",
            )
        return tenant_id

    async def sppg_map(self) -> dict:
        sppg_items, _ = await self._load_scope_data()
        items = []
        for item in sppg_items:
            covered_school_count = await self._count_covered_schools(item.id)
            items.append(
                {
                    "sppg_id": str(item.id),
                    "tenant_id": str(item.tenant_id),
                    "code": item.code,
                    "name": item.name,
                    "city": item.city,
                    "is_active": item.is_active,
                    "service_radius_meter": round(float(item.service_radius_meter), 6),
                    "coordinate": {"latitude": float(item.latitude), "longitude": float(item.longitude)},
                    "covered_school_count": covered_school_count,
                }
            )
        return {"items": items}

    async def kitchens_layer(
        self,
        bbox: tuple[float, float, float, float],
        snapshot_date: date | None = None,
        status: str | None = None,
        metric: str | None = None,
        limit: int = 2000,
    ) -> dict:
        tenant_id = self._require_tenant_scope()
        params: dict[str, object] = {
            "tenant_id": tenant_id,
            "min_lon": bbox[0],
            "min_lat": bbox[1],
            "max_lon": bbox[2],
            "max_lat": bbox[3],
            "limit": limit,
        }
        conditions = [
            "s.tenant_id = :tenant_id",
            "s.location && ST_MakeEnvelope(:min_lon, :min_lat, :max_lon, :max_lat, 4326)",
        ]
        if status is not None:
            params["is_active"] = status.lower() == "active"
            conditions.append("s.is_active = :is_active")
        rows = (
            await self.session.execute(
                text(
                    f"""
                    SELECT
                        s.id,
                        s.tenant_id,
                        s.code,
                        s.name,
                        s.city,
                        s.is_active,
                        s.service_radius_meter,
                        COALESCE(covered.covered_school_count, 0) AS covered_school_count,
                        ST_AsGeoJSON(s.location) AS geometry
                    FROM sppg s
                    LEFT JOIN LATERAL (
                        SELECT COUNT(*) AS covered_school_count
                        FROM schools sch
                        WHERE sch.tenant_id = s.tenant_id
                          AND ST_DWithin(s.location::geography, sch.location::geography, s.service_radius_meter)
                    ) covered ON TRUE
                    WHERE {" AND ".join(conditions)}
                    ORDER BY s.name
                    LIMIT :limit
                    """
                ),
                params,
            )
        ).mappings().all()

        features = []
        for row in rows:
            features.append(
                {
                    "type": "Feature",
                    "id": str(row["id"]),
                    "geometry": json.loads(row["geometry"]),
                    "properties": {
                        "kitchen_id": str(row["id"]),
                        "tenant_id": str(row["tenant_id"]),
                        "code": row["code"],
                        "name": row["name"],
                        "city": row["city"],
                        "is_active": row["is_active"],
                        "service_radius_meter": self._round_or_none(row["service_radius_meter"]) or 0.0,
                        "covered_school_count": int(row["covered_school_count"] or 0),
                        "snapshot_date": snapshot_date.isoformat() if snapshot_date else None,
                        "metric": metric,
                    },
                }
            )
        return {"type": "FeatureCollection", "features": features}

    async def schools_layer(
        self,
        bbox: tuple[float, float, float, float] | None = None,
        kitchen_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        feedback_min: float | None = None,
        complaint_only: bool = False,
        distribution_min: int | None = None,
        limit: int = 2000,
    ) -> dict:
        tenant_id = self._require_tenant_scope()
        params: dict[str, object] = {"tenant_id": tenant_id, "limit": limit, "date_from": date_from, "date_to": date_to}
        conditions = ["sch.tenant_id = :tenant_id"]
        delivery_date_conditions: list[str] = []
        feedback_date_conditions: list[str] = []
        complaint_date_conditions: list[str] = []

        if bbox is not None:
            params.update({"min_lon": bbox[0], "min_lat": bbox[1], "max_lon": bbox[2], "max_lat": bbox[3]})
            conditions.append("sch.location && ST_MakeEnvelope(:min_lon, :min_lat, :max_lon, :max_lat, 4326)")
        if kitchen_id is not None:
            params["kitchen_id"] = kitchen_id
            conditions.append(
                """
                EXISTS (
                    SELECT 1
                    FROM sppg s
                    WHERE s.id = :kitchen_id
                      AND s.tenant_id = sch.tenant_id
                      AND (
                          ST_DWithin(s.location::geography, sch.location::geography, s.service_radius_meter)
                          OR EXISTS (
                              SELECT 1
                              FROM service_areas sa
                              WHERE sa.sppg_id = s.id
                                AND sa.tenant_id = s.tenant_id
                                AND ST_Covers(sa.boundary, sch.location)
                          )
                      )
                )
                """
            )
        if feedback_min is not None:
            params["feedback_min"] = feedback_min
            conditions.append("COALESCE(feedback.avg_feedback, 0) >= :feedback_min")
        if complaint_only:
            conditions.append("COALESCE(complaints.complaint_count, 0) > 0")
        if distribution_min is not None:
            params["distribution_min"] = distribution_min
            conditions.append("COALESCE(delivery.delivery_count, 0) >= :distribution_min")
        if date_from is not None:
            delivery_date_conditions.append("d.created_at::date >= :date_from")
            feedback_date_conditions.append("fs.feedback_date >= :date_from")
            complaint_date_conditions.append("c.complaint_date::date >= :date_from")
        if date_to is not None:
            delivery_date_conditions.append("d.created_at::date <= :date_to")
            feedback_date_conditions.append("fs.feedback_date <= :date_to")
            complaint_date_conditions.append("c.complaint_date::date <= :date_to")

        delivery_date_sql = f" AND {' AND '.join(delivery_date_conditions)}" if delivery_date_conditions else ""
        feedback_date_sql = f" AND {' AND '.join(feedback_date_conditions)}" if feedback_date_conditions else ""
        complaint_date_sql = f" AND {' AND '.join(complaint_date_conditions)}" if complaint_date_conditions else ""
        rows = (
            await self.session.execute(
                text(
                    f"""
                    SELECT
                        sch.id,
                        sch.tenant_id,
                        sch.code,
                        sch.name,
                        sch.school_level,
                        sch.student_count,
                        sch.active_beneficiary_count,
                        COALESCE(delivery.delivery_count, 0) AS delivery_count,
                        COALESCE(feedback.avg_feedback, 0) AS avg_feedback,
                        COALESCE(complaints.complaint_count, 0) AS complaint_count,
                        ST_AsGeoJSON(sch.location) AS geometry
                    FROM schools sch
                    LEFT JOIN LATERAL (
                        SELECT COUNT(*) AS delivery_count
                        FROM delivery_orders d
                        WHERE d.school_id = sch.id
                          AND d.tenant_id = sch.tenant_id
                          {delivery_date_sql}
                    ) delivery ON TRUE
                    LEFT JOIN LATERAL (
                        SELECT AVG(fs.overall_rating) AS avg_feedback
                        FROM feedback_submissions fs
                        WHERE fs.school_id = sch.id
                          AND fs.tenant_id = sch.tenant_id
                          {feedback_date_sql}
                    ) feedback ON TRUE
                    LEFT JOIN LATERAL (
                        SELECT COUNT(*) AS complaint_count
                        FROM complaints c
                        LEFT JOIN feedback_submissions fs ON fs.id = c.feedback_submission_id
                        WHERE c.tenant_id = sch.tenant_id
                          AND fs.school_id = sch.id
                          {complaint_date_sql}
                    ) complaints ON TRUE
                    WHERE {" AND ".join(conditions)}
                    ORDER BY sch.name
                    LIMIT :limit
                    """
                ),
                params,
            )
        ).mappings().all()

        features = []
        for row in rows:
            features.append(
                {
                    "type": "Feature",
                    "id": str(row["id"]),
                    "geometry": json.loads(row["geometry"]),
                    "properties": {
                        "school_id": str(row["id"]),
                        "tenant_id": str(row["tenant_id"]),
                        "code": row["code"],
                        "name": row["name"],
                        "school_level": row["school_level"],
                        "student_count": int(row["student_count"] or 0),
                        "active_beneficiary_count": int(row["active_beneficiary_count"] or 0),
                        "delivery_count": int(row["delivery_count"] or 0),
                        "avg_feedback": self._round_or_none(row["avg_feedback"]) or 0.0,
                        "complaint_count": int(row["complaint_count"] or 0),
                    },
                }
            )
        return {"type": "FeatureCollection", "features": features}

    async def service_coverage(self, sppg_id: UUID | None = None) -> dict:
        sppg_items, schools = await self._load_scope_data()
        if sppg_id is not None:
            sppg_items = [item for item in sppg_items if item.id == sppg_id]
            if not sppg_items:
                raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG GIS tidak ditemukan.")

        items: list[dict] = []
        covered_school_ids: set[str] = set()
        for item in sppg_items:
            metrics = await self._coverage_metrics(item.id)
            covered_ids = await self._covered_school_ids(item.id)
            covered_school_ids.update(covered_ids)
            items.append(
                {
                    "sppg_id": str(item.id),
                    "tenant_id": str(item.tenant_id),
                    "code": item.code,
                    "name": item.name,
                    "service_radius_meter": round(float(item.service_radius_meter), 6),
                    "covered_school_count": metrics["covered_school_count"],
                    "out_of_radius_school_count": max(len(schools) - metrics["covered_school_count"], 0),
                    "nearest_school_distance_km": metrics["nearest_school_distance_km"],
                    "farthest_covered_school_distance_km": metrics["farthest_covered_school_distance_km"],
                    "average_covered_distance_km": metrics["average_covered_distance_km"],
                }
            )
        return {
            "items": items,
            "totals": {
                "sppg_count": len(sppg_items),
                "school_count": len(schools),
                "covered_school_count": len(covered_school_ids),
                "unserved_school_count": max(len(schools) - len(covered_school_ids), 0),
            },
        }

    async def unserved_schools(self) -> dict:
        tenant_id, sppg_scope = self._get_scope()
        schools = await self.school_repository.list_all(tenant_id)
        items: list[dict] = []
        for school in schools:
            conditions = ["sch.id = :school_id"]
            params: dict[str, object] = {"school_id": school.id}
            if tenant_id is not None:
                conditions.append("s.tenant_id = :tenant_id")
                params["tenant_id"] = tenant_id
            if sppg_scope is not None:
                conditions.append("s.id = :sppg_id")
                params["sppg_id"] = sppg_scope
            row = (
                await self.session.execute(
                    text(
                        f"""
                        SELECT
                            s.id,
                            s.name,
                            ST_Distance(s.location::geography, sch.location::geography) / 1000.0 AS distance_km,
                            ST_DWithin(s.location::geography, sch.location::geography, s.service_radius_meter) AS is_covered
                        FROM schools sch
                        JOIN sppg s ON s.tenant_id = sch.tenant_id
                        WHERE {" AND ".join(conditions)}
                        ORDER BY ST_Distance(s.location::geography, sch.location::geography)
                        LIMIT 1
                        """
                    ),
                    params,
                )
            ).mappings().first()
            if row is not None and row["is_covered"]:
                continue
            items.append(
                {
                    "school_id": str(school.id),
                    "tenant_id": str(school.tenant_id),
                    "code": school.code,
                    "name": school.name,
                    "school_level": school.school_level,
                    "coordinate": {"latitude": float(school.latitude), "longitude": float(school.longitude)},
                    "nearest_sppg_id": str(row["id"]) if row is not None else None,
                    "nearest_sppg_name": row["name"] if row is not None else None,
                    "nearest_distance_km": self._round_or_none(row["distance_km"] if row is not None else None),
                }
            )
        return {
            "items": items,
            "totals": {"school_count": len(schools), "unserved_school_count": len(items)},
        }

    async def risk_heatmap(self) -> dict:
        sppg_items, _ = await self._load_scope_data()
        items: list[dict] = []
        for item in sppg_items:
            metrics = await self._coverage_metrics(item.id)
            covered_count = metrics["covered_school_count"]
            avg_distance = metrics["average_covered_distance_km"] or 0.0
            max_distance = metrics["farthest_covered_school_distance_km"] or 0.0
            radius_km = float(item.service_radius_meter) / 1000 if item.service_radius_meter else 0.0
            radius_utilization = (max_distance / radius_km) if radius_km > 0 else 1.0
            risk_score = min(100.0, round((covered_count * 8.0) + (avg_distance * 10.0) + (radius_utilization * 35.0), 2))
            risk_level = "LOW"
            if risk_score >= 75:
                risk_level = "HIGH"
            elif risk_score >= 45:
                risk_level = "MEDIUM"
            items.append(
                {
                    "sppg_id": str(item.id),
                    "tenant_id": str(item.tenant_id),
                    "code": item.code,
                    "name": item.name,
                    "coordinate": {"latitude": float(item.latitude), "longitude": float(item.longitude)},
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "metrics": {
                        "covered_school_count": covered_count,
                        "average_covered_distance_km": metrics["average_covered_distance_km"],
                        "farthest_covered_distance_km": metrics["farthest_covered_school_distance_km"],
                        "radius_utilization_ratio": round(radius_utilization, 6),
                    },
                }
            )
        return {"items": items}

    async def distribution_heatmap(self) -> dict:
        tenant_id = self._require_tenant_scope()
        rows = (
            await self.session.execute(
                text(
                    """
                    SELECT
                        sch.id,
                        sch.tenant_id,
                        sch.code,
                        sch.name,
                        COUNT(d.id) AS distribution_count,
                        ST_AsGeoJSON(sch.location) AS geometry
                    FROM schools sch
                    LEFT JOIN delivery_orders d
                      ON d.school_id = sch.id
                     AND d.tenant_id = sch.tenant_id
                    WHERE sch.tenant_id = :tenant_id
                    GROUP BY sch.id, sch.tenant_id, sch.code, sch.name, sch.location
                    ORDER BY distribution_count DESC, sch.name
                    """
                ),
                {"tenant_id": tenant_id},
            )
        ).mappings().all()
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": str(row["id"]),
                    "geometry": json.loads(row["geometry"]),
                    "properties": {
                        "school_id": str(row["id"]),
                        "tenant_id": str(row["tenant_id"]),
                        "code": row["code"],
                        "name": row["name"],
                        "distribution_count": int(row["distribution_count"] or 0),
                    },
                }
                for row in rows
            ],
        }

    async def delivery_routes(self) -> dict:
        tenant_id, sppg_scope = self._get_scope()
        conditions = []
        params: dict[str, object] = {}
        if tenant_id is not None:
            conditions.append("d.tenant_id = :tenant_id")
            params["tenant_id"] = tenant_id
        if sppg_scope is not None:
            conditions.append("d.sppg_id = :sppg_id")
            params["sppg_id"] = sppg_scope
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        rows = (
            await self.session.execute(
                text(
                    f"""
                    SELECT
                        d.id AS delivery_order_id,
                        d.delivery_number,
                        d.status,
                        d.sppg_id,
                        d.school_id,
                        s.latitude AS from_latitude,
                        s.longitude AS from_longitude,
                        sch.latitude AS to_latitude,
                        sch.longitude AS to_longitude,
                        ST_Distance(s.location::geography, sch.location::geography) / 1000.0 AS distance_km,
                        ST_AsGeoJSON(ST_MakeLine(s.location, sch.location)) AS line_geojson
                    FROM delivery_orders d
                    JOIN sppg s ON s.id = d.sppg_id
                    JOIN schools sch ON sch.id = d.school_id
                    {where_clause}
                    ORDER BY d.created_at DESC
                    """
                ),
                params,
            )
        ).mappings().all()
        return {"items": [self._serialize_route_row(row) for row in rows]}

    async def get_delivery_route(self, delivery_id: UUID) -> dict:
        tenant_id, sppg_scope = self._get_scope()
        conditions = ["d.id = :delivery_id"]
        params: dict[str, object] = {"delivery_id": delivery_id}
        if tenant_id is not None:
            conditions.append("d.tenant_id = :tenant_id")
            params["tenant_id"] = tenant_id
        if sppg_scope is not None:
            conditions.append("d.sppg_id = :sppg_id")
            params["sppg_id"] = sppg_scope
        row = (
            await self.session.execute(
                text(
                    f"""
                    SELECT
                        d.id AS delivery_order_id,
                        d.delivery_number,
                        d.status,
                        d.sppg_id,
                        d.school_id,
                        s.latitude AS from_latitude,
                        s.longitude AS from_longitude,
                        sch.latitude AS to_latitude,
                        sch.longitude AS to_longitude,
                        ST_Distance(s.location::geography, sch.location::geography) / 1000.0 AS distance_km,
                        ST_AsGeoJSON(ST_MakeLine(s.location, sch.location)) AS line_geojson
                    FROM delivery_orders d
                    JOIN sppg s ON s.id = d.sppg_id AND s.tenant_id = d.tenant_id
                    JOIN schools sch ON sch.id = d.school_id AND sch.tenant_id = d.tenant_id
                    WHERE {" AND ".join(conditions)}
                    """
                ),
                params,
            )
        ).mappings().first()
        if row is None:
            raise NotFoundException(code="DELIVERY_ROUTE_NOT_FOUND", message="Rute delivery tidak ditemukan.")
        return self._serialize_route_row(row)

    async def list_service_areas(self) -> dict:
        tenant_id, sppg_scope = self._get_scope()
        conditions = []
        params: dict[str, object] = {}
        if tenant_id is not None:
            conditions.append("tenant_id = :tenant_id")
            params["tenant_id"] = tenant_id
        if sppg_scope is not None:
            conditions.append("sppg_id = :sppg_id")
            params["sppg_id"] = sppg_scope
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        rows = (
            await self.session.execute(
                text(
                    f"""
                    SELECT
                        id,
                        tenant_id,
                        sppg_id,
                        name,
                        valid_from,
                        valid_to,
                        ST_AsText(boundary) AS boundary_wkt,
                        ST_AsGeoJSON(boundary) AS boundary_geojson
                    FROM service_areas
                    {where_clause}
                    ORDER BY name
                    """
                ),
                params,
            )
        ).mappings().all()
        return {"items": [self._serialize_service_area_row(row) for row in rows]}

    async def get_service_area(self, service_area_id: UUID) -> dict:
        tenant_id, sppg_scope = self._get_scope()
        conditions = ["id = :service_area_id"]
        params: dict[str, object] = {"service_area_id": service_area_id}
        if tenant_id is not None:
            conditions.append("tenant_id = :tenant_id")
            params["tenant_id"] = tenant_id
        if sppg_scope is not None:
            conditions.append("sppg_id = :sppg_id")
            params["sppg_id"] = sppg_scope
        row = (
            await self.session.execute(
                text(
                    f"""
                    SELECT
                        id,
                        tenant_id,
                        sppg_id,
                        name,
                        valid_from,
                        valid_to,
                        ST_AsText(boundary) AS boundary_wkt,
                        ST_AsGeoJSON(boundary) AS boundary_geojson
                    FROM service_areas
                    WHERE {" AND ".join(conditions)}
                    """
                ),
                params,
            )
        ).mappings().first()
        if row is None:
            raise NotFoundException(code="SERVICE_AREA_NOT_FOUND", message="Service area tidak ditemukan.")
        return self._serialize_service_area_row(row)

    async def get_service_area_by_kitchen(self, kitchen_id: UUID) -> dict:
        tenant_id = self._require_tenant_scope()
        row = (
            await self.session.execute(
                text(
                    """
                    SELECT
                        id,
                        tenant_id,
                        sppg_id,
                        name,
                        valid_from,
                        valid_to,
                        ST_AsText(boundary) AS boundary_wkt,
                        ST_AsGeoJSON(boundary) AS boundary_geojson
                    FROM service_areas
                    WHERE tenant_id = :tenant_id
                      AND sppg_id = :kitchen_id
                    ORDER BY COALESCE(valid_from, DATE '1900-01-01') DESC, created_at DESC
                    LIMIT 1
                    """
                ),
                {"tenant_id": tenant_id, "kitchen_id": kitchen_id},
            )
        ).mappings().first()
        if row is None:
            raise NotFoundException(code="SERVICE_AREA_NOT_FOUND", message="Service area dapur tidak ditemukan.")
        return self._serialize_service_area_row(row)

    async def create_service_area(self, payload) -> dict:
        tenant_id = self._require_tenant_scope()
        sppg_scope = self._get_scope()[1]
        sppg_id = self._resolve_sppg_id(payload.sppg_id, sppg_scope)
        return await self._create_service_area_record(tenant_id, sppg_id, payload)

    async def upsert_service_area(self, kitchen_id: UUID, payload) -> dict:
        tenant_id = self._require_tenant_scope()
        service_area = await self._create_service_area_record(tenant_id, kitchen_id, payload)
        return service_area

    async def nearest_kitchens(self, school_id: UUID, limit: int = 5) -> dict:
        tenant_id = self._require_tenant_scope()
        school = await self.school_repository.get_by_id_and_tenant(school_id, tenant_id)
        if school is None:
            raise NotFoundException(code="SCHOOL_NOT_FOUND", message="Sekolah GIS tidak ditemukan.")
        rows = (
            await self.session.execute(
                text(
                    """
                    SELECT
                        s.id,
                        s.tenant_id,
                        s.code,
                        s.name,
                        s.service_radius_meter,
                        ST_Distance(s.location::geography, sch.location::geography) AS distance_m,
                        EXISTS (
                            SELECT 1
                            FROM service_areas sa
                            WHERE sa.tenant_id = s.tenant_id
                              AND sa.sppg_id = s.id
                              AND ST_Covers(sa.boundary, sch.location)
                        ) AS inside_service_area
                    FROM schools sch
                    JOIN sppg s ON s.tenant_id = sch.tenant_id
                    WHERE sch.id = :school_id
                      AND sch.tenant_id = :tenant_id
                    ORDER BY s.location <-> sch.location
                    LIMIT :limit
                    """
                ),
                {"school_id": school_id, "tenant_id": tenant_id, "limit": limit},
            )
        ).mappings().all()
        return {
            "school_id": str(school_id),
            "items": [
                {
                    "kitchen_id": str(row["id"]),
                    "tenant_id": str(row["tenant_id"]),
                    "code": row["code"],
                    "name": row["name"],
                    "distance_m": self._round_or_none(row["distance_m"]) or 0.0,
                    "inside_service_area": bool(row["inside_service_area"]),
                    "service_radius_meter": self._round_or_none(row["service_radius_meter"]) or 0.0,
                }
                for row in rows
            ],
        }

    async def validate_assignment(self, payload) -> dict:
        tenant_id = self._require_tenant_scope()
        kitchen_id = UUID(payload.kitchen_id)
        school_id = UUID(payload.school_id)
        row = (
            await self.session.execute(
                text(
                    """
                    SELECT
                        ST_Distance(s.location::geography, sch.location::geography) AS distance_m,
                        ST_DWithin(s.location::geography, sch.location::geography, s.service_radius_meter) AS inside_radius,
                        EXISTS (
                            SELECT 1
                            FROM service_areas sa
                            WHERE sa.tenant_id = s.tenant_id
                              AND sa.sppg_id = s.id
                              AND ST_Covers(sa.boundary, sch.location)
                        ) AS inside_service_area,
                        sch.active_beneficiary_count
                    FROM sppg s
                    JOIN schools sch
                      ON sch.tenant_id = s.tenant_id
                    WHERE s.id = :kitchen_id
                      AND sch.id = :school_id
                      AND s.tenant_id = :tenant_id
                    """
                ),
                {"kitchen_id": kitchen_id, "school_id": school_id, "tenant_id": tenant_id},
            )
        ).mappings().first()
        if row is None:
            raise NotFoundException(code="GIS_ASSIGNMENT_SCOPE_NOT_FOUND", message="Kombinasi dapur dan sekolah tidak ditemukan.")

        warnings: list[str] = []
        inside_service_area = bool(row["inside_service_area"])
        inside_radius = bool(row["inside_radius"])
        if not inside_service_area:
            warnings.append("Sekolah berada di luar service area dapur.")
        if not inside_radius:
            warnings.append("Sekolah berada di luar radius layanan dapur.")

        beneficiary_count = int(row["active_beneficiary_count"] or 0)
        planned_portions = payload.planned_portions or beneficiary_count
        capacity_available = beneficiary_count <= 0 or planned_portions <= beneficiary_count
        if not capacity_available:
            warnings.append("Penambahan porsi melebihi beneficiary aktif sekolah untuk assignment ini.")

        return {
            "is_valid": inside_radius and inside_service_area and capacity_available,
            "distance_m": self._round_or_none(row["distance_m"]),
            "inside_service_area": inside_service_area,
            "capacity_available": capacity_available,
            "warnings": warnings,
        }

    async def _create_service_area_record(self, tenant_id: UUID, sppg_id: UUID, payload) -> dict:
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant GIS tidak ditemukan.")
        sppg = await self.sppg_repository.get_by_id_and_tenant(sppg_id, tenant_id)
        if sppg is None:
            raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG GIS tidak ditemukan.")
        normalized = await self._normalize_geometry(payload.boundary_geojson, payload.boundary_wkt)
        service_area = await self.service_area_repository.add(
            ServiceArea(
                tenant_id=tenant_id,
                sppg_id=sppg_id,
                name=payload.name or f"Service Area {sppg.name}",
                boundary=WKTElement(normalized["boundary_wkt"], srid=4326),
                valid_from=payload.valid_from,
                valid_to=payload.valid_to,
            )
        )
        row = (
            await self.session.execute(
                text(
                    """
                    SELECT
                        id,
                        tenant_id,
                        sppg_id,
                        name,
                        valid_from,
                        valid_to,
                        ST_AsText(boundary) AS boundary_wkt,
                        ST_AsGeoJSON(boundary) AS boundary_geojson
                    FROM service_areas
                    WHERE id = :service_area_id
                    """
                ),
                {"service_area_id": service_area.id},
            )
        ).mappings().first()
        return self._serialize_service_area_row(row)

    async def _normalize_geometry(self, boundary_geojson, boundary_wkt: str | None) -> dict:
        if boundary_geojson is None and not boundary_wkt:
            raise BadRequestException(
                code="SERVICE_AREA_GEOMETRY_REQUIRED",
                message="Boundary service area wajib diisi dalam format GeoJSON atau WKT.",
            )

        if boundary_geojson is not None:
            geometry_payload = (
                boundary_geojson.model_dump(mode="json")
                if hasattr(boundary_geojson, "model_dump")
                else boundary_geojson
            )
            row = (
                await self.session.execute(
                    text(
                        """
                        WITH normalized AS (
                            SELECT ST_Multi(
                                ST_Force2D(
                                    ST_SetSRID(ST_GeomFromGeoJSON(:geojson), 4326)
                                )
                            ) AS geom
                        )
                        SELECT
                            ST_IsValid(geom) AS is_valid,
                            ST_IsEmpty(geom) AS is_empty,
                            ST_IsValidReason(geom) AS invalid_reason,
                            ST_NPoints(geom) AS vertex_count,
                            ST_AsText(geom) AS boundary_wkt,
                            ST_AsGeoJSON(geom) AS boundary_geojson
                        FROM normalized
                        """
                    ),
                    {"geojson": json.dumps(geometry_payload)},
                )
            ).mappings().first()
        else:
            row = (
                await self.session.execute(
                    text(
                        """
                        WITH normalized AS (
                            SELECT ST_Multi(
                                ST_Force2D(
                                    ST_SetSRID(ST_GeomFromText(:boundary_wkt), 4326)
                                )
                            ) AS geom
                        )
                        SELECT
                            ST_IsValid(geom) AS is_valid,
                            ST_IsEmpty(geom) AS is_empty,
                            ST_IsValidReason(geom) AS invalid_reason,
                            ST_NPoints(geom) AS vertex_count,
                            ST_AsText(geom) AS boundary_wkt,
                            ST_AsGeoJSON(geom) AS boundary_geojson
                        FROM normalized
                        """
                    ),
                    {"boundary_wkt": boundary_wkt},
                )
            ).mappings().first()

        if row is None or row["is_empty"]:
            raise BadRequestException(code="INVALID_SERVICE_AREA_GEOMETRY", message="Geometry service area kosong atau tidak dapat diproses.")
        if not row["is_valid"]:
            raise BadRequestException(
                code="INVALID_SERVICE_AREA_GEOMETRY",
                message=f"Geometry service area tidak valid: {row['invalid_reason']}.",
            )
        max_vertices = getattr(self.settings, "max_geojson_vertices", 5000)
        if int(row["vertex_count"] or 0) > max_vertices:
            raise BadRequestException(
                code="SERVICE_AREA_GEOMETRY_TOO_COMPLEX",
                message="Jumlah vertex geometry service area melebihi batas yang diizinkan.",
            )
        return {
            "boundary_wkt": row["boundary_wkt"],
            "boundary_geojson": json.loads(row["boundary_geojson"]),
        }

    def _resolve_sppg_id(self, payload_sppg_id: str | None, sppg_scope: UUID | None) -> UUID:
        if sppg_scope is not None:
            return sppg_scope
        if payload_sppg_id is None:
            raise BadRequestException(
                code="SPPG_CONTEXT_REQUIRED",
                message="Header X-SPPG-ID atau sppg_id pada payload wajib dikirim.",
            )
        return UUID(payload_sppg_id)

    async def _load_scope_data(self) -> tuple[list[Sppg], list]:
        tenant_id, sppg_scope = self._get_scope()
        sppg_items = await self.sppg_repository.list_all(tenant_id)
        schools = await self.school_repository.list_all(tenant_id)
        if sppg_scope is not None:
            sppg_items = [item for item in sppg_items if item.id == sppg_scope]
        return sppg_items, schools

    async def _count_covered_schools(self, sppg_id: UUID) -> int:
        row = (
            await self.session.execute(
                text(
                    """
                    SELECT COUNT(*) AS covered_school_count
                    FROM schools sch
                    JOIN sppg s ON s.tenant_id = sch.tenant_id
                    WHERE s.id = :sppg_id
                      AND ST_DWithin(s.location::geography, sch.location::geography, s.service_radius_meter)
                    """
                ),
                {"sppg_id": sppg_id},
            )
        ).mappings().first()
        return int(row["covered_school_count"] or 0)

    async def _covered_school_ids(self, sppg_id: UUID) -> set[str]:
        rows = (
            await self.session.execute(
                text(
                    """
                    SELECT sch.id
                    FROM schools sch
                    JOIN sppg s ON s.tenant_id = sch.tenant_id
                    WHERE s.id = :sppg_id
                      AND ST_DWithin(s.location::geography, sch.location::geography, s.service_radius_meter)
                    """
                ),
                {"sppg_id": sppg_id},
            )
        ).mappings().all()
        return {str(row["id"]) for row in rows}

    async def _coverage_metrics(self, sppg_id: UUID) -> dict:
        row = (
            await self.session.execute(
                text(
                    """
                    WITH distances AS (
                        SELECT
                            sch.id,
                            ST_Distance(s.location::geography, sch.location::geography) / 1000.0 AS distance_km,
                            ST_DWithin(s.location::geography, sch.location::geography, s.service_radius_meter) AS is_covered
                        FROM schools sch
                        JOIN sppg s ON s.tenant_id = sch.tenant_id
                        WHERE s.id = :sppg_id
                    )
                    SELECT
                        COUNT(*) FILTER (WHERE is_covered) AS covered_school_count,
                        MIN(distance_km) AS nearest_school_distance_km,
                        MAX(distance_km) FILTER (WHERE is_covered) AS farthest_covered_school_distance_km,
                        AVG(distance_km) FILTER (WHERE is_covered) AS average_covered_distance_km
                    FROM distances
                    """
                ),
                {"sppg_id": sppg_id},
            )
        ).mappings().first()
        return {
            "covered_school_count": int(row["covered_school_count"] or 0),
            "nearest_school_distance_km": self._round_or_none(row["nearest_school_distance_km"]),
            "farthest_covered_school_distance_km": self._round_or_none(row["farthest_covered_school_distance_km"]),
            "average_covered_distance_km": self._round_or_none(row["average_covered_distance_km"]),
        }

    @staticmethod
    def _serialize_service_area_row(row) -> dict:
        return {
            "id": str(row["id"]),
            "tenant_id": str(row["tenant_id"]),
            "sppg_id": str(row["sppg_id"]),
            "name": row["name"],
            "valid_from": row["valid_from"],
            "valid_to": row["valid_to"],
            "boundary_wkt": row["boundary_wkt"],
            "boundary_geojson": json.loads(row["boundary_geojson"]),
        }

    def _serialize_route_row(self, row) -> dict:
        line = json.loads(row["line_geojson"])["coordinates"]
        return {
            "delivery_order_id": str(row["delivery_order_id"]),
            "delivery_number": row["delivery_number"],
            "status": row["status"],
            "sppg_id": str(row["sppg_id"]),
            "school_id": str(row["school_id"]),
            "from_coordinate": {"latitude": float(row["from_latitude"]), "longitude": float(row["from_longitude"])},
            "to_coordinate": {"latitude": float(row["to_latitude"]), "longitude": float(row["to_longitude"])},
            "distance_km": self._round_or_none(row["distance_km"]) or 0.0,
            "line": [{"latitude": float(point[1]), "longitude": float(point[0])} for point in line],
        }

    @staticmethod
    def _round_or_none(value: float | None) -> float | None:
        if value is None:
            return None
        return round(float(value), 6)
