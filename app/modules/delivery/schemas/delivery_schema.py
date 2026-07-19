from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DeliveryOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID
    production_order_id: UUID
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
    received_portions: int
    rejected_portions: int
    temperature_celsius: float | None
    condition_notes: str | None


class DeliveryCreateFromProduction(BaseModel):
    school_id: str
    planned_departure: datetime
    planned_arrival: datetime
    receiver_name: str | None = None


class DeliveryProofCreate(BaseModel):
    received_at: datetime
    receiver_name: str
    receiver_gps: str | None = None
    received_portions: int
    rejected_portions: int = 0
    temperature_celsius: float | None = None
    condition_notes: str | None = None


class DeliveryOrderBundleRead(BaseModel):
    delivery_order: DeliveryOrderRead
    proofs: list[DeliveryProofRead]
