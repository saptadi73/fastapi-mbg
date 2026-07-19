# Dokumentasi Teknis PostGIS
## ERP Pengelolaan Dapur MBG — Backend FastAPI

**Versi:** 1.0  
**Target:** FastAPI, SQLAlchemy 2.x Async, PostgreSQL 18, PostGIS 3.x, GeoAlchemy2, Alembic  
**Primary key:** UUID  
**Arsitektur:** SaaS multi-tenant dan multi-dapur

---

## 1. Tujuan

Modul PostGIS menjadi fondasi spasial untuk:

1. memetakan tenant, SPPG/dapur, sekolah, gudang, pemasok, dan titik distribusi;
2. mengelola satu tenant dengan banyak dapur;
3. menentukan cakupan layanan setiap dapur;
4. menghubungkan dapur dengan sekolah berdasarkan periode;
5. menampilkan jumlah distribusi dan feedback sekolah;
6. menampilkan kapasitas, utilisasi, kualitas, biaya, stok, dan risiko dapur;
7. menghitung jarak, radius, kedekatan, dan cakupan wilayah;
8. menyediakan GeoJSON bagi frontend Vue/mobile;
9. mendukung dashboard GIS operasional dan analitik.

PostGIS diposisikan sebagai **spatial operational intelligence layer**, bukan hanya penyimpan koordinat.

---

## 2. Prinsip Arsitektur

### 2.1 Multi-tenant

```text
Tenant
 └── Kitchen/SPPG
      ├── Location
      ├── Service Area
      ├── School Assignment
      ├── Delivery Route
      ├── Performance Snapshot
      └── Risk Snapshot
```

Aturan:

- satu tenant dapat memiliki banyak dapur;
- satu dapur hanya dimiliki satu tenant;
- sekolah dapat berpindah dapur berdasarkan periode;
- semua query wajib difilter dengan `tenant_id`;
- histori assignment tidak boleh ditimpa;
- `tenant_id` harus berasal dari token/session, bukan body request.

### 2.2 Pemisahan data

- **Master spatial:** dapur, sekolah, gudang, pemasok, batas administratif.
- **Relationship spatial:** service area dan penugasan sekolah.
- **Transactional spatial:** pengiriman, rute, stop, posisi kendaraan, lokasi penerimaan.
- **Analytical spatial:** agregasi distribusi, feedback, performa, biaya, dan risiko.

### 2.3 UUID

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;

id UUID PRIMARY KEY DEFAULT gen_random_uuid()
```

---

## 3. Keputusan Tipe Spasial

### 3.1 SRID utama

Gunakan `EPSG:4326` agar kompatibel dengan GeoJSON, Leaflet, MapLibre, dan OpenLayers.

Urutan koordinat:

```text
POINT(longitude latitude)
```

Bukan `POINT(latitude longitude)`.

### 3.2 Geometry vs Geography

Gunakan `geometry` untuk penyimpanan dan operasi topologi:

```sql
geometry(Point, 4326)
geometry(LineString, 4326)
geometry(MultiPolygon, 4326)
```

Gunakan cast ke `geography` saat menghitung jarak dalam meter:

```sql
ST_DWithin(
    kitchen.location::geography,
    school.location::geography,
    10000
)
```

Rekomendasi:

- kolom utama disimpan sebagai `geometry(...,4326)`;
- cast ke `geography` untuk radius/jarak;
- kolom geography terpisah hanya ditambahkan jika hasil profiling membuktikan kebutuhan.

### 3.3 Tipe per entitas

| Entitas | Kolom | Tipe |
|---|---|---|
| Tenant | `head_office_location` | `geometry(Point,4326)` |
| Kitchen | `location` | `geometry(Point,4326)` |
| Service area | `area` | `geometry(MultiPolygon,4326)` |
| School | `location` | `geometry(Point,4326)` |
| Warehouse | `location` | `geometry(Point,4326)` |
| Supplier | `location` | `geometry(Point,4326)` |
| Delivery route | `route_geometry` | `geometry(LineString,4326)` |
| Delivery stop | `location` | `geometry(Point,4326)` |
| Vehicle tracking | `location` | `geometry(Point,4326)` |
| Administrative boundary | `boundary` | `geometry(MultiPolygon,4326)` |

---

## 4. Struktur Modul FastAPI

```text
app/
├── core/
│   ├── config.py
│   ├── database.py
│   ├── security.py
│   └── tenant_context.py
├── support/
│   ├── api_response.py
│   ├── geojson.py
│   ├── pagination.py
│   └── exceptions.py
├── modules/
│   ├── tenant/
│   ├── kitchen/
│   ├── school/
│   ├── distribution/
│   └── gis/
│       ├── models.py
│       ├── schemas.py
│       ├── repository.py
│       ├── service.py
│       ├── routes.py
│       ├── queries.py
│       └── constants.py
├── migrations/
└── main.py
```

Modul `gis` menyediakan query lintas modul, serialisasi GeoJSON, spatial filtering, layer peta, dan spatial analytics. Kepemilikan tabel master tetap berada pada modul domain masing-masing.

---

## 5. Dependency

```bash
pip install \
  fastapi \
  "uvicorn[standard]" \
  "sqlalchemy[asyncio]" \
  asyncpg \
  psycopg2-binary \
  alembic \
  geoalchemy2 \
  shapely \
  pydantic \
  pydantic-settings \
  python-dotenv
```

Fungsi dependency:

- `asyncpg`: koneksi async aplikasi;
- `psycopg2-binary`: koneksi sinkron Alembic/utilitas;
- `GeoAlchemy2`: tipe dan fungsi spasial SQLAlchemy;
- `Shapely`: validasi atau transformasi geometri di Python.

---

## 6. Konfigurasi `.env`

```env
APP_NAME=ERP Dapur MBG
APP_ENV=development
DEBUG=true

DATABASE_HOST=127.0.0.1
DATABASE_PORT=5432
DATABASE_NAME=mbg_erp
DATABASE_USER=mbg_app
DATABASE_PASSWORD=change_me

DATABASE_ASYNC_URL=postgresql+asyncpg://mbg_app:change_me@127.0.0.1:5432/mbg_erp
DATABASE_SYNC_URL=postgresql+psycopg2://mbg_app:change_me@127.0.0.1:5432/mbg_erp

POSTGIS_SRID=4326
DEFAULT_SERVICE_RADIUS_METERS=10000
MAX_GIS_BBOX_AREA_KM2=250000
MAX_GEOJSON_FEATURES=5000
```

---

## 7. Inisialisasi Database

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE SCHEMA IF NOT EXISTS app;
CREATE SCHEMA IF NOT EXISTS gis;

SELECT PostGIS_Full_Version();
```

Pembagian schema:

- `app`: tabel bisnis;
- `gis`: service area, boundary, snapshot, materialized view, dan analytical view.

Jangan memindahkan object internal extension PostGIS tanpa kebutuhan dan pengujian khusus.

---

## 8. Model Data

### 8.1 Tenant

```sql
CREATE TABLE app.tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    head_office_location geometry(Point, 4326),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ix_tenants_head_office_location_gist
ON app.tenants USING GIST (head_office_location);
```

### 8.2 Kitchen/SPPG

```sql
CREATE TABLE app.kitchens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES app.tenants(id),
    code VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    operational_status VARCHAR(30) NOT NULL DEFAULT 'planned',
    address TEXT,
    province_code VARCHAR(20),
    regency_code VARCHAR(20),
    district_code VARCHAR(20),
    village_code VARCHAR(20),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    location geometry(Point, 4326) NOT NULL,
    daily_capacity_portions INTEGER NOT NULL DEFAULT 0,
    default_service_radius_m INTEGER NOT NULL DEFAULT 10000,
    opened_at DATE,
    closed_at DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_kitchens_tenant_code UNIQUE (tenant_id, code),
    CONSTRAINT ck_kitchens_latitude CHECK (
        latitude IS NULL OR latitude BETWEEN -90 AND 90
    ),
    CONSTRAINT ck_kitchens_longitude CHECK (
        longitude IS NULL OR longitude BETWEEN -180 AND 180
    ),
    CONSTRAINT ck_kitchens_capacity CHECK (daily_capacity_portions >= 0)
);

CREATE INDEX ix_kitchens_tenant_id
ON app.kitchens (tenant_id);

CREATE INDEX ix_kitchens_location_gist
ON app.kitchens USING GIST (location);

CREATE INDEX ix_kitchens_tenant_status
ON app.kitchens (tenant_id, operational_status);
```

`location` menjadi sumber data spasial utama. Latitude/longitude dapat dipertahankan untuk ekspor dan integrasi, tetapi sinkronisasinya harus dikendalikan service layer.

### 8.3 Kitchen service area

```sql
CREATE TABLE gis.kitchen_service_areas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES app.tenants(id),
    kitchen_id UUID NOT NULL REFERENCES app.kitchens(id),
    name VARCHAR(200) NOT NULL,
    area_type VARCHAR(30) NOT NULL DEFAULT 'operational',
    area geometry(MultiPolygon, 4326) NOT NULL,
    valid_from DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_until DATE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    source VARCHAR(50) NOT NULL DEFAULT 'manual',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_service_area_period CHECK (
        valid_until IS NULL OR valid_until >= valid_from
    )
);

CREATE INDEX ix_kitchen_service_areas_tenant_kitchen
ON gis.kitchen_service_areas (tenant_id, kitchen_id);

CREATE INDEX ix_kitchen_service_areas_area_gist
ON gis.kitchen_service_areas USING GIST (area);
```

Nilai `area_type`:

```text
administrative
radius
operational
planned
emergency
```

### 8.4 School

```sql
CREATE TABLE app.schools (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES app.tenants(id),
    national_school_id VARCHAR(50),
    code VARCHAR(50),
    name VARCHAR(250) NOT NULL,
    education_level VARCHAR(50),
    address TEXT,
    province_code VARCHAR(20),
    regency_code VARCHAR(20),
    district_code VARCHAR(20),
    village_code VARCHAR(20),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    location geometry(Point, 4326) NOT NULL,
    beneficiary_count INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_schools_tenant_national_id
        UNIQUE NULLS NOT DISTINCT (tenant_id, national_school_id),
    CONSTRAINT ck_schools_beneficiary_count CHECK (beneficiary_count >= 0)
);

CREATE INDEX ix_schools_tenant_id
ON app.schools (tenant_id);

CREATE INDEX ix_schools_location_gist
ON app.schools USING GIST (location);
```

### 8.5 Penugasan dapur-sekolah

```sql
CREATE TABLE app.kitchen_school_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES app.tenants(id),
    kitchen_id UUID NOT NULL REFERENCES app.kitchens(id),
    school_id UUID NOT NULL REFERENCES app.schools(id),
    valid_from DATE NOT NULL,
    valid_until DATE,
    planned_daily_portions INTEGER NOT NULL DEFAULT 0,
    priority INTEGER NOT NULL DEFAULT 100,
    service_status VARCHAR(30) NOT NULL DEFAULT 'active',
    planned_distance_m DOUBLE PRECISION,
    planned_travel_time_min INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_assignment_period CHECK (
        valid_until IS NULL OR valid_until >= valid_from
    ),
    CONSTRAINT ck_assignment_portions CHECK (planned_daily_portions >= 0)
);

CREATE INDEX ix_assignment_tenant_kitchen
ON app.kitchen_school_assignments (tenant_id, kitchen_id);

CREATE INDEX ix_assignment_tenant_school
ON app.kitchen_school_assignments (tenant_id, school_id);

CREATE UNIQUE INDEX uq_assignment_active_school
ON app.kitchen_school_assignments (tenant_id, school_id)
WHERE valid_until IS NULL AND service_status = 'active';
```

### 8.6 Distribution delivery

```sql
CREATE TABLE app.distribution_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES app.tenants(id),
    kitchen_id UUID NOT NULL REFERENCES app.kitchens(id),
    school_id UUID NOT NULL REFERENCES app.schools(id),
    delivery_date DATE NOT NULL,
    delivery_number VARCHAR(80) NOT NULL,
    planned_portions INTEGER NOT NULL DEFAULT 0,
    dispatched_portions INTEGER NOT NULL DEFAULT 0,
    received_portions INTEGER NOT NULL DEFAULT 0,
    planned_departure_at TIMESTAMPTZ,
    actual_departure_at TIMESTAMPTZ,
    planned_arrival_at TIMESTAMPTZ,
    actual_arrival_at TIMESTAMPTZ,
    departure_location geometry(Point, 4326),
    receipt_location geometry(Point, 4326),
    status VARCHAR(30) NOT NULL DEFAULT 'planned',
    is_on_time BOOLEAN,
    distance_m DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_delivery_tenant_number UNIQUE (tenant_id, delivery_number),
    CONSTRAINT ck_delivery_portions CHECK (
        planned_portions >= 0
        AND dispatched_portions >= 0
        AND received_portions >= 0
    )
);
```

### 8.7 School feedback

```sql
CREATE TABLE app.school_feedbacks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES app.tenants(id),
    kitchen_id UUID NOT NULL REFERENCES app.kitchens(id),
    school_id UUID NOT NULL REFERENCES app.schools(id),
    delivery_id UUID REFERENCES app.distribution_deliveries(id),
    feedback_date DATE NOT NULL,
    overall_score NUMERIC(3,2),
    taste_score NUMERIC(3,2),
    portion_score NUMERIC(3,2),
    packaging_score NUMERIC(3,2),
    delivery_score NUMERIC(3,2),
    complaint_count INTEGER NOT NULL DEFAULT 0,
    leftover_portions INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_feedback_overall CHECK (
        overall_score IS NULL OR overall_score BETWEEN 1 AND 5
    ),
    CONSTRAINT ck_feedback_counts CHECK (
        complaint_count >= 0 AND leftover_portions >= 0
    )
);

CREATE INDEX ix_school_feedback_tenant_kitchen_date
ON app.school_feedbacks (tenant_id, kitchen_id, feedback_date);
```

### 8.8 Kitchen performance snapshot

```sql
CREATE TABLE gis.kitchen_performance_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES app.tenants(id),
    kitchen_id UUID NOT NULL REFERENCES app.kitchens(id),
    snapshot_date DATE NOT NULL,
    daily_capacity_portions INTEGER NOT NULL DEFAULT 0,
    produced_portions INTEGER NOT NULL DEFAULT 0,
    distributed_portions INTEGER NOT NULL DEFAULT 0,
    received_portions INTEGER NOT NULL DEFAULT 0,
    beneficiary_count INTEGER NOT NULL DEFAULT 0,
    served_school_count INTEGER NOT NULL DEFAULT 0,
    capacity_utilization_pct NUMERIC(7,2),
    on_time_delivery_pct NUMERIC(7,2),
    average_feedback_score NUMERIC(5,2),
    complaint_rate_pct NUMERIC(7,2),
    food_waste_rate_pct NUMERIC(7,2),
    cost_per_portion NUMERIC(18,2),
    stock_fulfillment_pct NUMERIC(7,2),
    risk_score NUMERIC(7,2),
    performance_score NUMERIC(7,2),
    formula_version VARCHAR(50),
    calculation_metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_kitchen_performance_snapshot
        UNIQUE (tenant_id, kitchen_id, snapshot_date)
);
```

Snapshot menyimpan histori dan mencegah agregasi transaksi berat setiap kali peta dibuka.

---

## 9. SQLAlchemy Async dan GeoAlchemy2

### 9.1 Database session

```python
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


engine = create_async_engine(
    settings.database_async_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
```

### 9.2 Kitchen model

```python
import uuid
from datetime import date, datetime

from geoalchemy2 import Geometry
from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Kitchen(Base):
    __tablename__ = "kitchens"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_kitchens_tenant_code"),
        CheckConstraint(
            "daily_capacity_portions >= 0",
            name="ck_kitchens_capacity",
        ),
        Index("ix_kitchens_tenant_id", "tenant_id"),
        Index(
            "ix_kitchens_location_gist",
            "location",
            postgresql_using="gist",
        ),
        {"schema": "app"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("app.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    operational_status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="planned"
    )
    address: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    location = mapped_column(
        Geometry(
            geometry_type="POINT",
            srid=4326,
            spatial_index=False,
        ),
        nullable=False,
    )
    daily_capacity_portions: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    default_service_radius_m: Mapped[int] = mapped_column(
        Integer, nullable=False, default=10000
    )
    opened_at: Mapped[date | None] = mapped_column(Date)
    closed_at: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
```

Gunakan `spatial_index=False` bila index dibuat eksplisit agar nama index konsisten dan migration tidak menduplikasi index.

---

## 10. Pydantic Schema

```python
from typing import Any, Literal

from pydantic import BaseModel, Field


class CoordinateInput(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class KitchenCreate(BaseModel):
    code: str
    name: str
    address: str | None = None
    coordinate: CoordinateInput
    daily_capacity_portions: int = Field(default=0, ge=0)
    default_service_radius_m: int = Field(default=10000, ge=100)


class GeoJSONGeometry(BaseModel):
    type: str
    coordinates: Any


class GeoJSONFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    id: str | None = None
    geometry: GeoJSONGeometry | None
    properties: dict[str, Any]


class GeoJSONFeatureCollection(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[GeoJSONFeature]
    bbox: list[float] | None = None
```

---

## 11. Membentuk Point dengan Aman

Jangan membuat WKT melalui string interpolation dari input mentah.

```python
from sqlalchemy import func

location_expression = func.ST_SetSRID(
    func.ST_MakePoint(
        payload.coordinate.longitude,
        payload.coordinate.latitude,
    ),
    4326,
)
```

Contoh:

```python
kitchen = Kitchen(
    tenant_id=tenant_id,
    code=payload.code,
    name=payload.name,
    address=payload.address,
    latitude=payload.coordinate.latitude,
    longitude=payload.coordinate.longitude,
    location=location_expression,
    daily_capacity_portions=payload.daily_capacity_portions,
)
```

---

## 12. Alembic Migration

### 12.1 Extension dan schema

```python
from alembic import op


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE SCHEMA IF NOT EXISTS app")
    op.execute("CREATE SCHEMA IF NOT EXISTS gis")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS gis CASCADE")
    op.execute("DROP SCHEMA IF EXISTS app CASCADE")
```

Jangan menjalankan `DROP EXTENSION postgis CASCADE` pada downgrade reguler karena berisiko menghapus seluruh object spasial.

### 12.2 Geometry dan GiST index

```python
import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

op.create_table(
    "kitchens",
    sa.Column(
        "id",
        postgresql.UUID(as_uuid=True),
        server_default=sa.text("gen_random_uuid()"),
        nullable=False,
    ),
    sa.Column(
        "tenant_id",
        postgresql.UUID(as_uuid=True),
        nullable=False,
    ),
    sa.Column("code", sa.String(length=50), nullable=False),
    sa.Column(
        "location",
        geoalchemy2.types.Geometry(
            geometry_type="POINT",
            srid=4326,
            spatial_index=False,
        ),
        nullable=False,
    ),
    sa.PrimaryKeyConstraint("id"),
    schema="app",
)

op.create_index(
    "ix_kitchens_location_gist",
    "kitchens",
    ["location"],
    schema="app",
    postgresql_using="gist",
)
```

`target_metadata` harus memuat semua model domain.

---

## 13. Query Spasial Utama

### 13.1 Dapur dalam bounding box

```sql
SELECT
    id,
    name,
    operational_status,
    ST_AsGeoJSON(location)::jsonb AS geometry
FROM app.kitchens
WHERE tenant_id = :tenant_id
  AND location && ST_MakeEnvelope(
      :min_lon,
      :min_lat,
      :max_lon,
      :max_lat,
      4326
  );
```

### 13.2 Sekolah dalam radius dapur

```sql
SELECT
    s.id,
    s.name,
    ST_Distance(
        k.location::geography,
        s.location::geography
    ) AS distance_m
FROM app.kitchens k
JOIN app.schools s
  ON s.tenant_id = k.tenant_id
WHERE k.id = :kitchen_id
  AND k.tenant_id = :tenant_id
  AND ST_DWithin(
      k.location::geography,
      s.location::geography,
      :radius_m
  )
ORDER BY distance_m;
```

Gunakan `ST_DWithin` untuk filter radius agar spatial index dapat dimanfaatkan.

### 13.3 Sekolah di dalam service area

```sql
SELECT s.id, s.name
FROM app.schools s
JOIN gis.kitchen_service_areas a
  ON a.tenant_id = s.tenant_id
WHERE a.kitchen_id = :kitchen_id
  AND a.tenant_id = :tenant_id
  AND a.is_active = TRUE
  AND ST_Covers(a.area, s.location);
```

`ST_Covers` dipilih agar titik tepat pada boundary tetap dianggap terlayani.

### 13.4 Dapur terdekat

```sql
SELECT
    k.id,
    k.name,
    ST_Distance(
        k.location::geography,
        s.location::geography
    ) AS distance_m
FROM app.schools s
JOIN app.kitchens k
  ON k.tenant_id = s.tenant_id
WHERE s.id = :school_id
  AND s.tenant_id = :tenant_id
  AND k.operational_status = 'active'
ORDER BY k.location <-> s.location
LIMIT :limit;
```

KNN `<->` dipakai untuk shortlist. Jarak final tetap dihitung menggunakan geography.

### 13.5 Validasi lokasi penerimaan

```sql
SELECT ST_DWithin(
    :receipt_location::geography,
    s.location::geography,
    :tolerance_m
) AS is_valid
FROM app.schools s
WHERE s.id = :school_id
  AND s.tenant_id = :tenant_id;
```

Tolerance misalnya 50–200 meter dan harus configurable.

### 13.6 Distribusi dan feedback sekolah

```sql
SELECT
    s.id,
    s.name,
    s.beneficiary_count,
    COALESCE(SUM(d.received_portions), 0) AS distributed_portions,
    AVG(f.overall_score) AS average_feedback_score,
    COALESCE(SUM(f.complaint_count), 0) AS complaint_count,
    ST_AsGeoJSON(s.location)::jsonb AS geometry
FROM app.schools s
LEFT JOIN app.distribution_deliveries d
  ON d.school_id = s.id
 AND d.tenant_id = s.tenant_id
 AND d.delivery_date BETWEEN :date_from AND :date_to
 AND d.status IN ('received', 'completed')
LEFT JOIN app.school_feedbacks f
  ON f.school_id = s.id
 AND f.tenant_id = s.tenant_id
 AND f.feedback_date BETWEEN :date_from AND :date_to
WHERE s.tenant_id = :tenant_id
  AND s.status = 'active'
GROUP BY s.id, s.name, s.beneficiary_count, s.location;
```

---

## 14. Repository Pattern

```python
from datetime import date
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class GISRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_kitchen_layer(
        self,
        *,
        tenant_id: UUID,
        snapshot_date: date,
        min_lon: float,
        min_lat: float,
        max_lon: float,
        max_lat: float,
        limit: int,
    ) -> list[dict]:
        statement = text(
            """
            SELECT
                k.id,
                k.code,
                k.name,
                k.operational_status,
                k.daily_capacity_portions,
                COALESCE(p.distributed_portions, 0) AS distributed_portions,
                COALESCE(p.served_school_count, 0) AS served_school_count,
                p.capacity_utilization_pct,
                p.on_time_delivery_pct,
                p.average_feedback_score,
                p.cost_per_portion,
                p.risk_score,
                p.performance_score,
                ST_AsGeoJSON(k.location)::jsonb AS geometry
            FROM app.kitchens k
            LEFT JOIN gis.kitchen_performance_snapshots p
              ON p.kitchen_id = k.id
             AND p.tenant_id = k.tenant_id
             AND p.snapshot_date = :snapshot_date
            WHERE k.tenant_id = :tenant_id
              AND k.location && ST_MakeEnvelope(
                    :min_lon, :min_lat, :max_lon, :max_lat, 4326
              )
            ORDER BY k.name
            LIMIT :limit
            """
        )

        result = await self.session.execute(
            statement,
            {
                "tenant_id": tenant_id,
                "snapshot_date": snapshot_date,
                "min_lon": min_lon,
                "min_lat": min_lat,
                "max_lon": max_lon,
                "max_lat": max_lat,
                "limit": limit,
            },
        )
        return [dict(row) for row in result.mappings().all()]
```

Semua query lintas tabel harus mengikat `tenant_id` pada setiap join yang relevan.

---

## 15. Service Layer

```python
from datetime import date
from uuid import UUID

from app.modules.gis.repository import GISRepository


class GISService:
    def __init__(self, repository: GISRepository):
        self.repository = repository

    async def get_kitchen_feature_collection(
        self,
        *,
        tenant_id: UUID,
        snapshot_date: date,
        bbox: tuple[float, float, float, float],
        limit: int,
    ) -> dict:
        min_lon, min_lat, max_lon, max_lat = bbox

        rows = await self.repository.get_kitchen_layer(
            tenant_id=tenant_id,
            snapshot_date=snapshot_date,
            min_lon=min_lon,
            min_lat=min_lat,
            max_lon=max_lon,
            max_lat=max_lat,
            limit=limit,
        )

        features = [
            {
                "type": "Feature",
                "id": str(row["id"]),
                "geometry": row["geometry"],
                "properties": {
                    key: value
                    for key, value in row.items()
                    if key not in {"id", "geometry"}
                },
            }
            for row in rows
        ]

        return {
            "type": "FeatureCollection",
            "features": features,
            "bbox": [min_lon, min_lat, max_lon, max_lat],
        }
```

Service layer menangani validasi bbox, limit feature, mapping kategori, tenant enforcement, dan audit.

---

## 16. API Endpoint

### 16.1 Layer dapur

```http
GET /api/v1/gis/kitchens
```

Parameter:

```text
bbox=112.0,-8.5,114.0,-6.5
snapshot_date=2026-07-20
status=active
metric=performance_score
limit=2000
```

### 16.2 Layer sekolah

```http
GET /api/v1/gis/schools
```

Filter:

```text
bbox
kitchen_id
date_from
date_to
feedback_min
complaint_only
distribution_min
```

### 16.3 Service area

```http
GET /api/v1/gis/kitchens/{kitchen_id}/service-area
PUT /api/v1/gis/kitchens/{kitchen_id}/service-area
```

Input menggunakan GeoJSON `MultiPolygon`.

### 16.4 Dapur terdekat

```http
GET /api/v1/gis/schools/{school_id}/nearest-kitchens
```

### 16.5 Validasi assignment

```http
POST /api/v1/gis/assignments/validate
```

Contoh response:

```json
{
  "is_valid": false,
  "distance_m": 17840.32,
  "inside_service_area": false,
  "capacity_available": false,
  "warnings": [
    "Sekolah berada di luar service area dapur.",
    "Penambahan porsi menyebabkan utilisasi rencana melebihi 100%."
  ]
}
```

### 16.6 Heatmap distribusi

```http
GET /api/v1/gis/heatmaps/distribution
```

### 16.7 Rute pengiriman

```http
GET /api/v1/gis/deliveries/{delivery_id}/route
```

---

## 17. Contoh Route FastAPI

```python
from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.tenant_context import get_current_tenant_id
from app.modules.gis.repository import GISRepository
from app.modules.gis.service import GISService

router = APIRouter(prefix="/api/v1/gis", tags=["GIS"])


def parse_bbox(value: str) -> tuple[float, float, float, float]:
    parts = [float(item.strip()) for item in value.split(",")]
    if len(parts) != 4:
        raise ValueError("bbox must contain four numbers")

    min_lon, min_lat, max_lon, max_lat = parts
    if not (-180 <= min_lon < max_lon <= 180):
        raise ValueError("invalid longitude range")
    if not (-90 <= min_lat < max_lat <= 90):
        raise ValueError("invalid latitude range")

    return min_lon, min_lat, max_lon, max_lat


@router.get("/kitchens")
async def get_kitchens_layer(
    bbox: Annotated[str, Query(...)],
    snapshot_date: date,
    limit: Annotated[int, Query(ge=1, le=5000)] = 2000,
    tenant_id: UUID = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_db_session),
):
    service = GISService(GISRepository(session))
    return await service.get_kitchen_feature_collection(
        tenant_id=tenant_id,
        snapshot_date=snapshot_date,
        bbox=parse_bbox(bbox),
        limit=limit,
    )
```

Error parser sebaiknya dikonversi menjadi HTTP 422 melalui exception handler aplikasi.

---

## 18. Standar GeoJSON

Gunakan convention RFC 7946:

- koordinat `[longitude, latitude]`;
- WGS84/EPSG:4326;
- UUID sebagai string;
- timestamp ISO 8601;
- `FeatureCollection` sebagai response layer.

```json
{
  "type": "FeatureCollection",
  "bbox": [112.0, -8.5, 114.0, -6.5],
  "features": [],
  "meta": {
    "count": 0,
    "snapshot_date": "2026-07-20",
    "metric": "performance_score"
  }
}
```

---

## 19. Layer GIS

### Kitchen

```text
kitchen_location
kitchen_capacity
kitchen_utilization
kitchen_distribution
kitchen_performance
kitchen_feedback
kitchen_cost
kitchen_stock_risk
kitchen_operational_risk
kitchen_facility_status
```

### School

```text
school_location
school_beneficiary
school_distribution
school_feedback
school_complaint
school_leftover
school_unserved
school_outside_service_area
```

### Distribution

```text
active_routes
delivery_delay
delivery_density
route_overlap
distance_anomaly
receipt_location_anomaly
```

### Administrative

```text
province
regency
district
village
```

Boundary administratif harus menyimpan `source`, `source_version`, dan tanggal impor.

---

## 20. Visualisasi Dapur

Ukuran marker dapat didasarkan pada:

```text
distributed_portions
served_school_count
daily_capacity_portions
beneficiary_count
```

Warna marker dapat didasarkan pada:

```text
operational_status
capacity_utilization_pct
performance_score
risk_score
average_feedback_score
```

Kategori performa:

```text
85–100 : very_good
70–84  : good
55–69  : attention
0–54   : critical
```

Backend mengirim nilai dan kategori; frontend menentukan warna aktual.

---

## 21. Kitchen Performance Index

Contoh bobot awal:

```text
20% capacity utilization
20% on-time delivery
20% feedback quality
15% cost efficiency
15% stock fulfillment
10% compliance and facility
```

Ketentuan:

- bobot disimpan sebagai konfigurasi;
- tidak hard-code permanen dalam service;
- snapshot menyimpan `formula_version`;
- `calculation_metadata` menyimpan komponen audit;
- perubahan formula tidak mengubah snapshot historis.

---

## 22. Risk Score

Contoh:

```text
30% operational risk
25% delivery risk
20% inventory risk
15% quality risk
10% geographic risk
```

Indikator:

```text
capacity overload
stockout
late delivery
food safety incident
complaint spike
high leftover
equipment failure
staff shortage
flood exposure
poor road access
```

Simpan raw indicator, normalized value, weight, result, timestamp, dan formula version.

---

## 23. Materialized View dan Snapshot

Gunakan materialized view untuk ringkasan terbaru dan tabel snapshot untuk histori.

```sql
CREATE MATERIALIZED VIEW gis.mv_kitchen_daily_map AS
SELECT
    k.tenant_id,
    k.id AS kitchen_id,
    CURRENT_DATE AS snapshot_date,
    k.name,
    k.operational_status,
    k.daily_capacity_portions,
    k.location,
    COUNT(DISTINCT a.school_id) AS served_school_count,
    COALESCE(SUM(d.received_portions), 0) AS distributed_portions,
    AVG(f.overall_score) AS average_feedback_score
FROM app.kitchens k
LEFT JOIN app.kitchen_school_assignments a
  ON a.kitchen_id = k.id
 AND a.tenant_id = k.tenant_id
 AND a.service_status = 'active'
LEFT JOIN app.distribution_deliveries d
  ON d.kitchen_id = k.id
 AND d.tenant_id = k.tenant_id
 AND d.delivery_date = CURRENT_DATE
LEFT JOIN app.school_feedbacks f
  ON f.kitchen_id = k.id
 AND f.tenant_id = k.tenant_id
 AND f.feedback_date = CURRENT_DATE
GROUP BY
    k.tenant_id,
    k.id,
    k.name,
    k.operational_status,
    k.daily_capacity_portions,
    k.location;

CREATE UNIQUE INDEX uq_mv_kitchen_daily_map
ON gis.mv_kitchen_daily_map (tenant_id, kitchen_id, snapshot_date);

CREATE INDEX ix_mv_kitchen_daily_map_location_gist
ON gis.mv_kitchen_daily_map USING GIST (location);
```

Refresh:

```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY gis.mv_kitchen_daily_map;
```

---

## 24. Optimasi Performa

1. Semua geometry utama memiliki GiST index.
2. Endpoint peta wajib menerima bbox.
3. Default feature maksimal 2.000; hard limit 5.000.
4. Radius menggunakan `ST_DWithin`.
5. Gunakan `EXPLAIN (ANALYZE, BUFFERS)`.
6. Pastikan query plan menggunakan GiST/Index Scan/Bitmap Index Scan.
7. Hindari transformasi fungsi pada kolom index bila tidak perlu.
8. Aktifkan autovacuum dan jalankan `ANALYZE` setelah impor besar.
9. Sesuaikan connection pool dengan jumlah worker.
10. Gunakan clustering atau vector tile untuk skala nasional.

Contoh:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT ...;
```

---

## 25. Clustering

Untuk banyak sekolah:

1. frontend mengirim bbox dan zoom;
2. backend memilih grid size;
3. titik diagregasi;
4. backend mengembalikan centroid dan jumlah.

```sql
SELECT
    COUNT(*) AS point_count,
    ST_AsGeoJSON(
        ST_Centroid(ST_Collect(location))
    )::jsonb AS geometry
FROM app.schools
WHERE tenant_id = :tenant_id
  AND location && ST_MakeEnvelope(
      :min_lon, :min_lat, :max_lon, :max_lat, 4326
  )
GROUP BY ST_SnapToGrid(location, :grid_size);
```

Untuk analisis metrik presisi, gunakan proyeksi yang sesuai atau strategi tile.

---

## 26. Vector Tile

Tahap lanjutan:

```http
GET /api/v1/gis/tiles/{z}/{x}/{y}.mvt
```

Fungsi PostGIS:

```text
ST_TileEnvelope
ST_AsMVTGeom
ST_AsMVT
```

GeoJSON tetap dipakai untuk detail feature dan CRUD.

---

## 27. Validasi Geometry

```sql
SELECT
    ST_IsValid(:geometry),
    ST_IsValidReason(:geometry);
```

Normalisasi:

```sql
ST_Force2D(
    ST_SetSRID(
        ST_GeomFromGeoJSON(:geojson),
        4326
    )
)
```

Polygon menjadi MultiPolygon:

```sql
ST_Multi(...)
```

Perbaikan geometry:

```sql
ST_MakeValid(...)
```

Aturan:

- geometry kosong ditolak;
- SRID selain 4326 ditolak atau ditransformasi eksplisit;
- polygon invalid ditolak atau diperbaiki dengan audit;
- ukuran payload dan jumlah vertex dibatasi;
- perubahan geometry menyimpan old/new value.

---

## 28. Keamanan Multi-tenant

### Tenant context

```text
JWT/current user
  → tenant context
  → repository filter
```

### Join aman

```sql
JOIN app.schools s
  ON s.id = a.school_id
 AND s.tenant_id = a.tenant_id
```

### Row-Level Security opsional

```sql
ALTER TABLE app.kitchens ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_kitchens
ON app.kitchens
USING (
    tenant_id = current_setting('app.current_tenant_id')::uuid
);
```

Set per transaction:

```sql
SET LOCAL app.current_tenant_id = '...';
```

RLS merupakan defense in depth, bukan pengganti filter repository.

---

## 29. Audit Trail

Audit perubahan:

```text
kitchen location
school location
service area
school assignment
receipt location override
invalid geometry repair
risk score override
```

```sql
CREATE TABLE app.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    actor_user_id UUID,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Untuk geometry simpan GeoJSON ringkas, hash, bbox, SRID, dan alasan perubahan.

---

## 30. Testing

### Unit test

- validasi latitude/longitude;
- parser bbox;
- GeoJSON serialization;
- kategori performa;
- tenant context;
- feature limit.

### Integration test PostGIS

- membuat point dapur dan sekolah;
- sekolah dalam/luar radius;
- titik di dalam service area;
- titik tepat pada boundary;
- cross-tenant tidak bocor;
- polygon invalid ditolak;
- GeoJSON valid;
- index digunakan.

```python
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_get_kitchen_layer(auth_headers):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/api/v1/gis/kitchens",
            params={
                "bbox": "112.0,-8.5,114.0,-6.5",
                "snapshot_date": "2026-07-20",
            },
            headers=auth_headers,
        )

    assert response.status_code == 200
    assert response.json()["type"] == "FeatureCollection"
```

---

## 31. Import Data

Alur:

```text
upload
→ staging table
→ validation
→ coordinate normalization
→ duplicate detection
→ spatial validation
→ commit to master
→ import report
```

Validasi:

```text
tenant exists
code unique
latitude numeric
longitude numeric
coordinate range valid
location not null
school identifier valid
duplicate point warning
administrative code exists
```

Koordinat Indonesia dapat dipakai sebagai warning konteks:

```text
latitude sekitar -11 sampai 6
longitude sekitar 95 sampai 141
```

Jangan gunakan rentang tersebut sebagai validasi global tunggal.

---

## 32. Integrasi Frontend

Rekomendasi:

```text
MapLibre GL JS
```

Kontrak frontend:

- bbox selalu dikirim;
- zoom dikirim untuk clustering;
- filter tanggal eksplisit;
- layer dimuat terpisah;
- detail dimuat on-demand;
- jangan memuat seluruh transaksi pada marker awal.

---

## 33. Observability

Metrik:

```text
gis_query_duration_ms
gis_features_returned
gis_bbox_area
gis_query_type
gis_cache_hit
gis_timeout_count
invalid_geometry_count
cross_tenant_denied_count
```

Aktifkan `pg_stat_statements` untuk menganalisis query berulang dan lambat.

---

## 34. Caching

Cocok untuk cache:

```text
administrative boundary
daily performance snapshot
static service area
cluster result by bbox/zoom
legend configuration
```

Cache key minimal:

```text
tenant_id
layer
bbox/tile
zoom
date range
filter
data version
```

Data real-time seperti posisi kendaraan, delivery status, insiden, dan stok kritis memerlukan TTL pendek atau tidak dicache.

---

## 35. Error Handling

Kode error:

```text
GIS_INVALID_COORDINATE
GIS_INVALID_BBOX
GIS_BBOX_TOO_LARGE
GIS_INVALID_GEOJSON
GIS_INVALID_GEOMETRY
GIS_UNSUPPORTED_GEOMETRY
GIS_SRID_MISMATCH
GIS_FEATURE_LIMIT_EXCEEDED
GIS_KITCHEN_NOT_FOUND
GIS_SCHOOL_NOT_FOUND
GIS_OUTSIDE_SERVICE_AREA
GIS_CROSS_TENANT_ACCESS_DENIED
```

```json
{
  "success": false,
  "error": {
    "code": "GIS_INVALID_BBOX",
    "message": "Bounding box tidak valid.",
    "details": {
      "expected": "min_lon,min_lat,max_lon,max_lat"
    }
  }
}
```

---

## 36. Tahapan Implementasi

### Tahap 1 — Spatial foundation

- extension PostGIS;
- schema database;
- lokasi dapur dan sekolah;
- GiST index;
- endpoint bbox;
- GeoJSON;
- tenant isolation.

### Tahap 2 — Service area dan assignment

- polygon service area;
- assignment dapur-sekolah;
- nearest kitchen;
- radius;
- validasi cakupan;
- histori assignment.

### Tahap 3 — Distribusi dan feedback

- lokasi delivery;
- received portions;
- feedback sekolah;
- layer distribusi dan kualitas;
- anomaly penerimaan.

### Tahap 4 — Operational intelligence

- performance snapshot;
- risk snapshot;
- cost per portion;
- stock risk;
- utilization;
- heatmap.

### Tahap 5 — Scale optimization

- clustering;
- materialized view;
- vector tile;
- cache;
- RLS;
- observability;
- query tuning.

---

## 37. Keputusan Desain Final

1. Titik utama memakai `geometry(Point,4326)`.
2. Service area memakai `geometry(MultiPolygon,4326)`.
3. Route memakai `geometry(LineString,4326)`.
4. Jarak meter memakai cast ke `geography`.
5. Semua geometry utama memiliki GiST index.
6. Endpoint peta wajib menggunakan bbox.
7. Semua query wajib melakukan tenant isolation.
8. Sekolah dipetakan berdasarkan distribusi, penerima manfaat, feedback, keluhan, dan sisa makanan.
9. Dapur dipetakan berdasarkan kapasitas, utilisasi, distribusi, kualitas, biaya, stok, fasilitas, performa, dan risiko.
10. Tenant-dapur adalah one-to-many.
11. Dapur-sekolah memakai assignment berperiode.
12. Histori spasial penting tidak boleh ditimpa tanpa audit.
13. GeoJSON digunakan untuk API operasional.
14. Vector tile disiapkan untuk scaling.
15. Agregasi harian disimpan sebagai snapshot.

---

## 38. Checklist

### Database

- [ ] PostgreSQL 18 tersedia.
- [ ] PostGIS kompatibel dan terpasang.
- [ ] `pgcrypto` aktif.
- [ ] `postgis` aktif.
- [ ] schema `app` dan `gis` dibuat.
- [ ] semua geometry memakai SRID 4326.
- [ ] GiST index tersedia.
- [ ] constraint tenant dan business key tersedia.

### Backend

- [ ] SQLAlchemy async aktif.
- [ ] GeoAlchemy2 terpasang.
- [ ] Alembic mengenali geometry.
- [ ] tenant context berasal dari authentication.
- [ ] endpoint bbox tersedia.
- [ ] response GeoJSON konsisten.
- [ ] radius memakai `ST_DWithin`.
- [ ] feature limit aktif.
- [ ] error spasial terstandar.
- [ ] audit location/service area tersedia.

### Testing

- [ ] point creation.
- [ ] bbox query.
- [ ] radius query.
- [ ] service area.
- [ ] boundary point.
- [ ] cross-tenant isolation.
- [ ] invalid polygon.
- [ ] large payload.
- [ ] query plan.
- [ ] GeoJSON serialization.

### Operasional

- [ ] monitoring query lambat.
- [ ] backup/restore PostGIS diuji.
- [ ] extension version dicatat.
- [ ] sumber boundary dicatat.
- [ ] snapshot job dijadwalkan.
- [ ] cache invalidation ditentukan.

---

## 39. Referensi Teknis

- PostGIS documentation: `https://postgis.net/docs/`
- PostGIS data management: `https://postgis.net/docs/using_postgis_dbmanagement.html`
- PostGIS `ST_DWithin`: `https://postgis.net/docs/ST_DWithin.html`
- PostGIS spatial indexing: `https://postgis.net/workshops/postgis-intro/indexing.html`
- GeoAlchemy2: `https://geoalchemy-2.readthedocs.io/`
- FastAPI async: `https://fastapi.tiangolo.com/async/`
- FastAPI dependencies: `https://fastapi.tiangolo.com/tutorial/dependencies/`
- Alembic asyncio cookbook: `https://alembic.sqlalchemy.org/en/latest/cookbook.html`
- PostgreSQL 18 `CREATE EXTENSION`: `https://www.postgresql.org/docs/18/sql-createextension.html`

---

## 40. Penutup

Fondasi PostGIS ini memungkinkan backend menjawab secara langsung:

- dapur mana yang melayani sekolah tertentu;
- sekolah mana yang berada di luar cakupan;
- dapur terdekat yang masih memiliki kapasitas;
- wilayah dengan distribusi tinggi tetapi feedback rendah;
- dapur yang overload atau berisiko;
- rute yang terlambat atau tidak efisien;
- validitas lokasi penerimaan;
- perubahan performa berdasarkan waktu dan wilayah.

Dengan desain ini, GIS menjadi pusat kendali spasial untuk operasi, monitoring, evaluasi, dan pengambilan keputusan ERP Dapur MBG.
