from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field


class GISCoordinateRead(BaseModel):
    latitude: float
    longitude: float


class GeoJSONGeometry(BaseModel):
    type: str
    coordinates: Any


class GeoJSONFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    id: str | None = None
    geometry: GeoJSONGeometry | None = None
    properties: dict[str, Any] = Field(default_factory=dict)


class GeoJSONFeatureCollection(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[GeoJSONFeature] = Field(default_factory=list)


class GISSppgMapItemRead(BaseModel):
    sppg_id: str
    tenant_id: str
    code: str
    name: str
    city: str
    is_active: bool
    service_radius_meter: float
    coordinate: GISCoordinateRead
    covered_school_count: int


class GISSppgMapRead(BaseModel):
    items: list[GISSppgMapItemRead]


class GISCoverageItemRead(BaseModel):
    sppg_id: str
    tenant_id: str
    code: str
    name: str
    service_radius_meter: float
    covered_school_count: int
    out_of_radius_school_count: int
    nearest_school_distance_km: float | None = None
    farthest_covered_school_distance_km: float | None = None
    average_covered_distance_km: float | None = None


class GISServiceCoverageRead(BaseModel):
    items: list[GISCoverageItemRead]
    totals: dict[str, Any]


class GISUnservedSchoolItemRead(BaseModel):
    school_id: str
    tenant_id: str
    code: str
    name: str
    school_level: str
    coordinate: GISCoordinateRead
    nearest_sppg_id: str | None = None
    nearest_sppg_name: str | None = None
    nearest_distance_km: float | None = None


class GISUnservedSchoolRead(BaseModel):
    items: list[GISUnservedSchoolItemRead]
    totals: dict[str, Any]


class GISRiskHeatmapItemRead(BaseModel):
    sppg_id: str
    tenant_id: str
    code: str
    name: str
    coordinate: GISCoordinateRead
    risk_score: float
    risk_level: str
    metrics: dict[str, Any]


class GISRiskHeatmapRead(BaseModel):
    items: list[GISRiskHeatmapItemRead]


class GISDeliveryRouteItemRead(BaseModel):
    delivery_order_id: str
    delivery_number: str
    status: str
    sppg_id: str
    school_id: str
    from_coordinate: GISCoordinateRead
    to_coordinate: GISCoordinateRead
    distance_km: float
    line: list[GISCoordinateRead]


class GISDeliveryRouteRead(BaseModel):
    items: list[GISDeliveryRouteItemRead]


class GISServiceAreaUpsert(BaseModel):
    name: str | None = None
    boundary_geojson: GeoJSONGeometry | dict[str, Any] | None = None
    boundary_wkt: str | None = None
    valid_from: date | None = None
    valid_to: date | None = None
    tenant_id: str | None = None
    sppg_id: str | None = None


class GISServiceAreaCreate(GISServiceAreaUpsert):
    name: str


class GISServiceAreaItemRead(BaseModel):
    id: str
    tenant_id: str
    sppg_id: str
    name: str
    valid_from: date | None = None
    valid_to: date | None = None
    boundary_wkt: str
    boundary_geojson: dict[str, Any]


class GISServiceAreaListRead(BaseModel):
    items: list[GISServiceAreaItemRead]


class GISNearestKitchenItemRead(BaseModel):
    kitchen_id: str
    tenant_id: str
    code: str
    name: str
    distance_m: float
    inside_service_area: bool
    service_radius_meter: float


class GISNearestKitchenRead(BaseModel):
    school_id: str
    items: list[GISNearestKitchenItemRead]


class GISAssignmentValidationRequest(BaseModel):
    kitchen_id: str
    school_id: str
    planned_portions: int | None = Field(default=None, ge=0)


class GISAssignmentValidationRead(BaseModel):
    is_valid: bool
    distance_m: float | None = None
    inside_service_area: bool
    capacity_available: bool
    warnings: list[str] = Field(default_factory=list)

