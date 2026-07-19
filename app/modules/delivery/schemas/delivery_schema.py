from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DeliveryRouteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    route_code: str
    route_name: str
    route_status: str
    planned_departure: datetime | None
    actual_departure: datetime | None
    planned_arrival: datetime | None
    actual_arrival: datetime | None
    origin_gps: str | None
    destination_gps: str | None
    total_distance_km: float | None
    notes: str | None


class DeliveryRouteStopRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    route_id: UUID
    delivery_order_id: UUID | None
    school_id: UUID
    stop_sequence: int
    planned_arrival: datetime | None
    actual_arrival: datetime | None
    planned_departure: datetime | None
    actual_departure: datetime | None
    status: str
    recipient_name: str | None
    stop_gps: str | None
    notes: str | None


class DeliveryIncidentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    delivery_order_id: UUID | None
    route_id: UUID | None
    route_stop_id: UUID | None
    incident_time: datetime
    category: str
    severity: str
    title: str
    description: str | None
    incident_gps: str | None
    temperature_celsius: float | None
    media_urls: list[str]
    status: str
    resolution_notes: str | None


class DeliveryOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    production_order_id: UUID
    route_id: UUID | None
    school_id: UUID
    delivery_number: str
    planned_departure: datetime
    actual_departure: datetime | None
    planned_arrival: datetime
    actual_arrival: datetime | None
    planned_portions: int
    shipped_portions: int | None
    received_portions: int | None
    rejected_portions: int | None
    status: str
    receiver_name: str | None
    receiver_gps: str | None


class DeliveryProofRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    delivery_order_id: UUID
    received_at: datetime
    receiver_name: str
    receiver_gps: str | None
    route_id: UUID | None
    route_stop_id: UUID | None
    received_portions: int
    rejected_portions: int
    temperature_celsius: float | None
    condition_status: str | None
    condition_notes: str | None
    photo_urls: list[str]
    signature_name: str | None
    signature_url: str | None
    signature_signed_at: datetime | None
    incident_notes: str | None
    linked_incident_ids: list[str]


class DeliveryCreateFromProduction(BaseModel):
    school_id: str
    planned_departure: datetime
    planned_arrival: datetime
    receiver_name: str | None = None


class DeliveryRouteStopPlan(BaseModel):
    delivery_order_id: str
    planned_arrival: datetime | None = None
    planned_departure: datetime | None = None
    recipient_name: str | None = None
    stop_gps: str | None = None
    notes: str | None = None


class DeliveryRouteCreate(BaseModel):
    route_name: str
    planned_departure: datetime | None = None
    planned_arrival: datetime | None = None
    notes: str | None = None
    stops: list[DeliveryRouteStopPlan] = Field(default_factory=list)


class DeliveryIncidentCreate(BaseModel):
    incident_time: datetime
    category: str
    severity: str = "MEDIUM"
    title: str
    description: str | None = None
    route_stop_id: str | None = None
    incident_gps: str | None = None
    temperature_celsius: float | None = None
    media_urls: list[str] = Field(default_factory=list)
    status: str = "OPEN"
    resolution_notes: str | None = None


class DeliveryProofCreate(BaseModel):
    received_at: datetime
    receiver_name: str
    receiver_gps: str | None = None
    route_stop_id: str | None = None
    received_portions: int
    rejected_portions: int = 0
    temperature_celsius: float | None = None
    condition_status: str | None = None
    condition_notes: str | None = None
    photo_urls: list[str] = Field(default_factory=list)
    signature_name: str | None = None
    signature_url: str | None = None
    signature_signed_at: datetime | None = None
    incident_notes: str | None = None
    linked_incident_ids: list[str] = Field(default_factory=list)


class DeliveryOrderBundleRead(BaseModel):
    delivery_order: DeliveryOrderRead
    route: DeliveryRouteRead | None = None
    route_stops: list[DeliveryRouteStopRead] = Field(default_factory=list)
    incidents: list[DeliveryIncidentRead] = Field(default_factory=list)
    proofs: list[DeliveryProofRead]


class DeliveryRouteBundleRead(BaseModel):
    route: DeliveryRouteRead
    stops: list[DeliveryRouteStopRead] = Field(default_factory=list)
    incidents: list[DeliveryIncidentRead] = Field(default_factory=list)
