# Dokumentasi Teknis Backend ERP Pengelolaan Dapur MBG Berbasis FastAPI

## 1. Ringkasan Sistem

ERP Pengelolaan Dapur MBG adalah platform SaaS multi-tenant untuk mengelola operasional SPPG/Dapur MBG secara terintegrasi, mulai dari perencanaan menu, pengadaan dan persediaan bahan, produksi makanan, distribusi paket bantuan, evaluasi biaya per porsi, pengelolaan anggaran, dana talangan investor, accounting, GIS, hingga pelaporan manajemen.

Platform dirancang sebagai **vertical ERP** dengan fokus utama pada:

1. Pengendalian operasional dapur.
2. Pengendalian biaya dan anggaran.
3. Pengelolaan modal dan pembiayaan.
4. Akuntabilitas transaksi keuangan.
5. Monitoring persediaan dan distribusi.
6. Analisis kinerja SPPG berbasis dashboard dan GIS.
7. Penyediaan data terstruktur untuk AI dan sistem rekomendasi.

Sistem tidak menggunakan paradigma ERP dagang penuh. Modul penjualan, CRM, quotation, dan customer invoicing tidak menjadi pusat desain. Fokus sistem adalah **operational execution, budget control, fund management, inventory, distribution, dan financial ledger**.

---

## 2. Tujuan Implementasi

Backend harus memenuhi kebutuhan berikut:

- Mengelola banyak organisasi/operator dalam satu platform SaaS.
- Menggunakan UUID sebagai primary key seluruh entitas utama agar aman untuk multi-tenant, integrasi, sinkronisasi offline, dan migrasi data.
- Mengelola banyak dapur/SPPG dalam setiap tenant.
- Menyimpan lokasi GPS dapur, sekolah, penerima, supplier, dan jalur distribusi.
- Mengelola meal plan, resep, kebutuhan bahan, produksi, hasil aktual, dan food waste.
- Menghitung budget cost dan actual cost per porsi.
- Mengelola dana pemerintah, modal investor, dana talangan, pengembalian, dan margin.
- Mengelola persediaan bahan baku, bahan kemasan, barang operasional, dan paket bantuan.
- Mengelola pengadaan, penerimaan, pemakaian, transfer, penyesuaian, dan stock opname.
- Mengelola distribusi ke sekolah atau titik penerima.
- Menghasilkan jurnal akuntansi otomatis dari transaksi operasional.
- Menyediakan API dashboard operasional, keuangan, inventory, distribusi, dan investor.
- Menjadi sumber data bagi AI recommendation, anomaly detection, forecasting, dan GIS intelligence.

---

## 3. Arsitektur Sistem

### 3.1 Arsitektur Tingkat Tinggi

```text
Vue 3 / Nuxt / Mobile PWA
            |
            v
       API Gateway
            |
            v
         FastAPI
            |
    +-------+--------+-------------------+
    |       |        |                   |
 Identity  ERP     Analytics          Integration
 Tenant    Core    & Reporting        Services
    |       |        |                   |
    +-------+--------+-------------------+
            |
            v
 PostgreSQL + PostGIS
            |
     Redis / Queue / Object Storage
```

### 3.2 Pola Implementasi

Gunakan **modular monolith** pada fase awal. Setiap domain bisnis dipisahkan sebagai modul internal, tetapi masih berada dalam satu aplikasi dan satu deployment.

Keuntungan:

- Pengembangan lebih cepat.
- Transaksi antar modul lebih mudah.
- Konsistensi data lebih baik.
- Lebih mudah diuji dan dipelihara.
- Dapat dipisahkan menjadi microservice ketika beban dan organisasi tim meningkat.

### 3.3 Prinsip Modularitas Domain

Backend menggunakan pola **modular monolith dengan domain module yang independen**. Setiap modul memiliki router, service, model, schema, repository, policy, exception, event, dan test sendiri. Modul tidak boleh mengakses tabel modul lain secara langsung melalui query ad-hoc.

Aturan dependensi:

```text
routes -> services -> repositories -> models/database
                 -> domain events -> service modul lain
```

Ketentuan utama:

- `routes` hanya menangani HTTP, dependency injection, validasi request, dan pemetaan response.
- `services` menangani aturan bisnis dan orchestration transaksi.
- `repositories` menangani akses database.
- `models` hanya mendefinisikan persistence model SQLAlchemy.
- `schemas` mendefinisikan kontrak input/output Pydantic.
- `policies` menangani authorization berbasis role, scope, tenant, dan kepemilikan data.
- `events` mendefinisikan event domain dan handler.
- Modul berkomunikasi melalui service interface atau domain event, bukan dengan mengimpor router modul lain.
- Seluruh tabel tenant-scoped tetap wajib memiliki `tenant_id` UUID.

### 3.4 Struktur Proyek Utama

```text
erp_mbg_backend/
├── app/
│   ├── main.py
│   ├── bootstrap.py
│   ├── core/
│   │   ├── config/
│   │   │   ├── settings.py
│   │   │   ├── environment.py
│   │   │   └── constants.py
│   │   ├── database/
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   ├── transaction.py
│   │   │   └── naming.py
│   │   ├── security/
│   │   │   ├── jwt.py
│   │   │   ├── password.py
│   │   │   ├── permissions.py
│   │   │   └── dependencies.py
│   │   ├── tenancy/
│   │   │   ├── context.py
│   │   │   ├── middleware.py
│   │   │   └── rls.py
│   │   └── observability/
│   │       ├── logging.py
│   │       ├── tracing.py
│   │       └── metrics.py
│   ├── support/
│   │   ├── responses/
│   │   │   ├── envelope.py
│   │   │   ├── pagination.py
│   │   │   └── codes.py
│   │   ├── exceptions/
│   │   │   ├── base.py
│   │   │   ├── handlers.py
│   │   │   └── error_codes.py
│   │   ├── middleware/
│   │   │   ├── cors.py
│   │   │   ├── request_id.py
│   │   │   ├── audit_context.py
│   │   │   └── timing.py
│   │   ├── pagination/
│   │   ├── filters/
│   │   ├── files/
│   │   └── utilities/
│   ├── modules/
│   │   ├── identity/
│   │   ├── tenant/
│   │   ├── sppg/
│   │   ├── geography/
│   │   ├── beneficiary/
│   │   ├── meal_plan/
│   │   ├── recipe/
│   │   ├── procurement/
│   │   ├── inventory/
│   │   ├── production/
│   │   ├── distribution/
│   │   ├── feedback/
│   │   ├── budget/
│   │   ├── funding/
│   │   ├── accounting/
│   │   ├── asset/
│   │   ├── reporting/
│   │   ├── gis/
│   │   ├── notification/
│   │   └── audit/
│   └── integrations/
│       ├── object_storage/
│       ├── messaging/
│       ├── government/
│       ├── maps/
│       └── ai/
├── alembic/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   └── e2e/
├── scripts/
├── docker/
├── .env.example
├── .env.development
├── .env.testing
├── .env.production
├── alembic.ini
├── pyproject.toml
└── README.md
```

### 3.5 Struktur Standar Setiap Modul

Setiap modul wajib mengikuti struktur yang seragam:

```text
modules/inventory/
├── __init__.py
├── manifest.py
├── routes/
│   ├── __init__.py
│   ├── stock_routes.py
│   ├── warehouse_routes.py
│   └── transaction_routes.py
├── services/
│   ├── __init__.py
│   ├── stock_service.py
│   ├── reservation_service.py
│   └── valuation_service.py
├── repositories/
│   ├── __init__.py
│   ├── stock_repository.py
│   └── transaction_repository.py
├── models/
│   ├── __init__.py
│   ├── warehouse.py
│   ├── stock_balance.py
│   └── inventory_transaction.py
├── schemas/
│   ├── __init__.py
│   ├── warehouse_schema.py
│   ├── stock_schema.py
│   └── transaction_schema.py
├── policies/
│   ├── __init__.py
│   └── inventory_policy.py
├── events/
│   ├── __init__.py
│   ├── definitions.py
│   └── handlers.py
├── exceptions/
│   ├── __init__.py
│   └── inventory_exceptions.py
├── dependencies.py
├── constants.py
└── tests/
    ├── test_routes.py
    ├── test_services.py
    └── test_repositories.py
```

`manifest.py` mendeskripsikan router, prefix, tag OpenAPI, dan event handler modul:

```python
from dataclasses import dataclass
from fastapi import APIRouter

from .routes import router

@dataclass(frozen=True)
class ModuleManifest:
    name: str
    prefix: str
    tags: list[str]
    router: APIRouter

manifest = ModuleManifest(
    name="inventory",
    prefix="/api/v1/inventory",
    tags=["Inventory"],
    router=router,
)
```

Bootstrap aplikasi melakukan registrasi modul secara eksplisit agar dependensi terlihat jelas dan mudah diuji.

### 3.6 Support Layer Bersama

Folder `app/support` hanya berisi kebutuhan lintas modul yang tidak memiliki aturan bisnis MBG. Contohnya:

- standar JSON response;
- exception handler global;
- CORS;
- request ID dan correlation ID;
- pagination;
- filter query;
- upload file;
- formatter tanggal, uang, dan satuan;
- reusable dependency.

Support layer tidak boleh menyimpan aturan meal plan, stock, budget, accounting, atau distribusi.

#### Standar JSON Response

```json
{
  "success": true,
  "code": "INVENTORY_STOCK_FOUND",
  "message": "Data stock berhasil diambil",
  "data": {},
  "meta": {
    "request_id": "0a580d1d-9bb4-4e59-8fc3-d83b6426ed39",
    "timestamp": "2026-07-19T13:00:00+07:00"
  }
}
```

Response error:

```json
{
  "success": false,
  "code": "INSUFFICIENT_STOCK",
  "message": "Stock bahan tidak mencukupi",
  "errors": [
    {
      "field": "product_id",
      "detail": "Kekurangan 25 kg beras"
    }
  ],
  "meta": {
    "request_id": "0a580d1d-9bb4-4e59-8fc3-d83b6426ed39"
  }
}
```

### 3.7 Pemisahan Domain dan Integrasi Antar Modul

Contoh alur penyelesaian produksi:

```text
production.service.complete_order()
    ├── validasi meal plan dan hasil aktual
    ├── publish ProductionCompleted
    ├── inventory handler membuat konsumsi stock
    ├── budget handler membuat realisasi anggaran
    ├── accounting handler membuat jurnal otomatis
    └── reporting handler memperbarui projection/materialized view
```

Gunakan transaksi database sinkron untuk konsekuensi yang wajib konsisten, misalnya konsumsi stock dan jurnal. Gunakan queue untuk proses yang dapat ditunda, misalnya notifikasi, refresh analytics berat, ekspor laporan, dan integrasi eksternal.

### 3.8 Konfigurasi Berbasis Environment

Semua konfigurasi deployment harus berasal dari environment variable. File `.env` dipakai untuk pengembangan lokal dan deployment yang mendukung env file. Secret produksi tidak boleh di-commit ke repository.

Prioritas sumber konfigurasi:

```text
OS environment / secret manager
        > file .env sesuai environment
        > nilai default aman pada Settings
```

Gunakan `pydantic-settings`:

```python
from functools import lru_cache
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "ERP MBG API"
    app_env: str = "development"
    app_debug: bool = False
    api_v1_prefix: str = "/api/v1"

    database_url: PostgresDsn
    redis_url: str | None = None

    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14

    cors_origins: list[str] = []
    cors_allow_credentials: bool = True

    storage_endpoint: str | None = None
    storage_access_key: str | None = None
    storage_secret_key: str | None = None
    storage_bucket: str = "erp-mbg"

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

Contoh `.env.example`:

```dotenv
APP_NAME=ERP MBG API
APP_ENV=development
APP_DEBUG=true
API_V1_PREFIX=/api/v1

DATABASE_URL=postgresql+asyncpg://erp_mbg:change-me@localhost:5432/erp_mbg
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_RECYCLE=1800

REDIS_URL=redis://localhost:6379/0

JWT_SECRET_KEY=replace-with-minimum-32-character-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=14

CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET","POST","PUT","PATCH","DELETE","OPTIONS"]
CORS_ALLOW_HEADERS=["Authorization","Content-Type","X-Request-ID","X-Tenant-ID"]

DEFAULT_TIMEZONE=Asia/Jakarta
DEFAULT_CURRENCY=IDR

STORAGE_DRIVER=s3
STORAGE_ENDPOINT=http://localhost:9000
STORAGE_ACCESS_KEY=minioadmin
STORAGE_SECRET_KEY=minioadmin
STORAGE_BUCKET=erp-mbg

SENTRY_DSN=
OTEL_EXPORTER_OTLP_ENDPOINT=
LOG_LEVEL=INFO
LOG_FORMAT=json
```

File yang boleh masuk repository hanya `.env.example`. Untuk server:

- Development: `.env.development` lokal.
- Testing: `.env.testing` dengan database terpisah.
- Staging: secret pada CI/CD atau orchestrator.
- Production: Docker/Kubernetes secret, Vault, atau secret manager lain.

### 3.9 Konfigurasi CORS

CORS diambil dari `Settings`, tidak ditulis statis pada `main.py`.

```python
from fastapi.middleware.cors import CORSMiddleware


def register_cors(app, settings):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
```

Pada production, jangan menggunakan `allow_origins=["*"]` bersama cookie atau credential. Daftarkan domain frontend SaaS, admin, dan mobile web secara eksplisit.

### 3.10 Application Factory dan Bootstrap

```python
from fastapi import FastAPI

from app.core.config.settings import get_settings
from app.support.exceptions.handlers import register_exception_handlers
from app.support.middleware.cors import register_cors
from app.support.middleware.request_id import register_request_id
from app.bootstrap import register_modules


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    )

    register_request_id(app)
    register_cors(app, settings)
    register_exception_handlers(app)
    register_modules(app, settings.api_v1_prefix)

    return app


app = create_app()
```

`main.py` tetap tipis. Inisialisasi database, middleware, router, event handler, observability, dan lifecycle ditempatkan pada bootstrap atau factory masing-masing.

---

## 4. Teknologi yang Direkomendasikan

| Komponen | Teknologi |
|---|---|
| Backend API | FastAPI |
| ORM | SQLAlchemy 2.x dengan native PostgreSQL UUID |
| Migration | Alembic |
| Database | PostgreSQL 14+ |
| GIS | PostGIS |
| Validation | Pydantic 2.x |
| Authentication | OAuth2 Password Flow + JWT |
| Authorization | RBAC + policy-based access |
| Background job | Celery atau Dramatiq |
| Message broker | Redis atau RabbitMQ |
| Cache | Redis |
| Object storage | MinIO atau S3-compatible storage |
| Reporting | SQLAlchemy/SQL + materialized views |
| Observability | OpenTelemetry + Prometheus + Grafana |
| Error tracking | Sentry |
| Testing | Pytest |
| API documentation | OpenAPI/Swagger bawaan FastAPI |
| Containerization | Docker |
| Reverse proxy | Nginx |

---


## 5. Standar Identitas Data Berbasis UUID

### 5.1 Kebijakan UUID

Seluruh entitas utama dan tabel transaksi menggunakan UUID sebagai primary key. Sistem tidak menggunakan `SERIAL`, `BIGSERIAL`, atau integer auto-increment sebagai identitas bisnis utama.

Standar kolom identitas:

```sql
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
```

Aktifkan ekstensi PostgreSQL:

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

UUID harus digunakan pada:

- tenant dan organisasi;
- user, role, permission, dan scope;
- SPPG, gudang, sekolah, supplier, dan beneficiary;
- meal plan, resep, produksi, procurement, inventory, dan distribusi;
- budget, funding, accounting, asset, feedback, audit, dan notification;
- seluruh foreign key yang mengacu pada entitas tersebut.

### 5.2 Pilihan Versi UUID

Untuk implementasi awal, gunakan UUID v4 karena dukungannya matang di Python, SQLAlchemy, Pydantic, PostgreSQL, dan berbagai integration client.

```python
from uuid import UUID, uuid4

from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

class UUIDPrimaryKeyMixin:
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default="gen_random_uuid()",
    )
```

Jika volume transaksi sudah sangat besar dan locality index menjadi masalah, sistem dapat mempertimbangkan UUID v7. Perubahan tersebut harus dilakukan melalui abstraksi generator UUID agar model bisnis tidak berubah.

### 5.3 Aturan Foreign Key

Semua foreign key harus menggunakan tipe UUID yang sama dengan primary key tujuan.

```sql
CREATE TABLE production_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    sppg_id UUID NOT NULL REFERENCES sppg(id),
    meal_plan_id UUID NOT NULL REFERENCES meal_plans(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Jangan menyimpan relasi UUID sebagai `VARCHAR`. Penggunaan tipe native UUID diperlukan agar validasi, indexing, storage, dan query planner PostgreSQL tetap optimal.

### 5.4 UUID dan Multi-Tenant

UUID tidak menggantikan tenant isolation. Setiap query tetap wajib memfilter `tenant_id`. Untuk tabel tenant-scoped, gunakan composite uniqueness agar nomor dokumen dapat sama pada tenant berbeda.

```sql
CREATE UNIQUE INDEX uq_production_order_number_per_tenant
ON production_orders (tenant_id, document_number);
```

Foreign key lintas tenant harus dicegah. Untuk relasi kritis, gunakan composite foreign key:

```sql
ALTER TABLE warehouses
ADD CONSTRAINT uq_warehouses_tenant_id_id UNIQUE (tenant_id, id);

ALTER TABLE inventory_transactions
ADD CONSTRAINT fk_inventory_warehouse_same_tenant
FOREIGN KEY (tenant_id, warehouse_id)
REFERENCES warehouses (tenant_id, id);
```

### 5.5 Indexing UUID

Primary key UUID otomatis memperoleh B-tree index. Tambahkan index berdasarkan pola akses, bukan hanya setiap foreign key secara terpisah.

```sql
CREATE INDEX ix_inventory_transactions_tenant_sppg_date
ON inventory_transactions (tenant_id, sppg_id, transaction_date DESC);

CREATE INDEX ix_distribution_orders_tenant_status_date
ON distribution_orders (tenant_id, status, delivery_date);
```

Untuk tabel yang sangat besar, pertimbangkan:

- partitioning berdasarkan periode dan/atau tenant group;
- UUID v7 untuk locality yang lebih baik;
- BRIN index untuk kolom waktu;
- materialized view untuk dashboard agregat.

### 5.6 UUID pada API

Semua path parameter dan schema API memakai tipe `UUID`, bukan `str` bebas.

```python
from uuid import UUID
from fastapi import APIRouter

router = APIRouter()

@router.get("/meal-plans/{meal_plan_id}")
async def get_meal_plan(meal_plan_id: UUID):
    ...
```

Contoh payload:

```json
{
  "id": "0190f3e2-86fb-7b18-a9f2-a17f4d81d961",
  "tenant_id": "1b2f4267-20ad-46dc-87b1-24b981f518a4",
  "sppg_id": "bb3654d1-59ed-4f76-9b9b-0a308946ac15"
}
```

API tidak boleh mengekspos sequence internal. Nomor dokumen seperti `PO-2026-000123` atau `PROD-2026-000456` adalah business identifier, bukan primary key.

### 5.7 UUID dan Migrasi Data

UUID memudahkan penggabungan data dari banyak instalasi atau tenant karena risiko collision sangat kecil. Strategi migrasi yang direkomendasikan:

1. Pertahankan legacy ID pada kolom khusus, misalnya `legacy_id` atau `source_record_id`.
2. Tambahkan `source_system` dan `source_tenant_code`.
3. Buat mapping table antara ID lama dan UUID baru.
4. Migrasikan master lebih dahulu, lalu transaksi berdasarkan dependency graph.
5. Validasi referential integrity dan jumlah record setelah setiap batch.
6. Jangan menggunakan nomor dokumen sebagai foreign key.

Contoh mapping:

```sql
CREATE TABLE migration_id_maps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_system VARCHAR(100) NOT NULL,
    source_table VARCHAR(100) NOT NULL,
    source_record_id VARCHAR(255) NOT NULL,
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    target_record_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source_system, source_table, source_record_id, tenant_id)
);
```

Untuk proses import idempotent, gunakan kombinasi `source_system`, `source_table`, `source_record_id`, dan `tenant_id` sebagai kunci pencarian.

### 5.8 UUID dan Audit Trail

Audit log harus menyimpan UUID record secara native atau konsisten sebagai UUID-compatible value.

```text
audit_logs
- id UUID
- tenant_id UUID
- actor_user_id UUID
- entity_type VARCHAR
- entity_id UUID
- action VARCHAR
- before_data JSONB
- after_data JSONB
- created_at TIMESTAMPTZ
```

Untuk relasi polymorphic, `entity_id` dapat tetap bertipe UUID karena seluruh entitas utama menggunakan standar UUID yang sama.

---

## 6. Multi-Tenant SaaS

### 6.1 Model Tenant

Tahap awal menggunakan:

```text
Shared application
Shared database
Shared schema
Tenant isolation melalui tenant_id
```

Semua tabel transaksi wajib memiliki:

```text
tenant_id UUID NOT NULL
```

Tabel yang terkait dapur juga memiliki:

```text
sppg_id UUID NULL/NOT NULL
```

### 6.2 Isi JWT

```json
{
  "sub": "user_uuid",
  "tenant_id": "tenant_uuid",
  "roles": ["tenant_admin", "finance_manager"],
  "permissions": ["budget.read", "journal.post"],
  "sppg_scope": ["sppg_uuid_1", "sppg_uuid_2"],
  "exp": 1780000000
}
```

### 6.3 Isolasi Data

Setiap query harus mengandung tenant context:

```sql
WHERE tenant_id = :current_tenant_id
```

Untuk penguatan keamanan gunakan PostgreSQL Row-Level Security:

```sql
ALTER TABLE inventory_transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_inventory
ON inventory_transactions
USING (tenant_id = current_setting('app.current_tenant')::uuid);
```

Aplikasi harus mengatur session variable pada setiap koneksi/transaksi database.

### 6.4 Hierarki Organisasi

```text
Tenant / Operator
  └── Region / Area
       └── SPPG / Dapur
            ├── Warehouse
            ├── Production Unit
            └── Delivery Unit
```

---

## 7. Modul Identity dan Hak Akses

### 7.1 Entitas Utama

- users
- roles
- permissions
- user_roles
- role_permissions
- user_sppg_scopes
- sessions
- api_keys

### 7.2 Role Awal

- super_admin
- tenant_admin
- regional_manager
- sppg_manager
- kitchen_operator
- warehouse_operator
- procurement_officer
- production_supervisor
- delivery_officer
- finance_manager
- accountant
- investor_viewer
- auditor
- government_viewer

### 7.3 Prinsip Otorisasi

Gunakan kombinasi:

- Role-Based Access Control.
- Permission-Based Access Control.
- SPPG scope.
- Transaction status policy.
- Approval limit policy.

Contoh permission:

```text
meal_plan.create
meal_plan.approve
inventory.issue
inventory.adjust
budget.commit
budget.override
journal.post
funding.disburse
report.investor.read
```

---

## 8. Modul Master SPPG dan GIS

### 8.1 Tujuan

Menyimpan identitas, lokasi, kapasitas, status operasional, area layanan, fasilitas, dan hubungan SPPG dengan sekolah atau titik penerima.

### 8.2 Entitas Utama

#### tenants

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
code
name
subscription_plan
status
created_at
```

#### sppg

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
tenant_id
code
name
legal_name
operational_status
activation_date
daily_capacity
manager_user_id
province_id
regency_id
district_id
village_id
address
latitude
longitude
location geometry(Point, 4326)
service_radius_km
kitchen_area_m2
warehouse_area_m2
status
created_at
updated_at
```

#### sppg_facilities

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
tenant_id
sppg_id
facility_type
name
capacity
condition
acquisition_date
```

#### schools

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
tenant_id
code
name
school_level
address
location geometry(Point, 4326)
student_count
active_beneficiary_count
```

#### sppg_school_assignments

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
tenant_id
sppg_id
school_id
valid_from
valid_to
planned_portions
service_status
```

#### service_areas

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
tenant_id
sppg_id
name
boundary geometry(Polygon, 4326)
valid_from
valid_to
```

### 8.3 Fitur GIS

- Menampilkan marker SPPG.
- Menampilkan status operasional dengan warna marker.
- Menghitung jarak SPPG ke sekolah.
- Menghitung radius cakupan.
- Mendeteksi tumpang tindih area layanan.
- Mendeteksi sekolah yang belum terlayani.
- Menentukan dapur terdekat.
- Menghasilkan heatmap kapasitas, penerima, biaya, dan risiko.
- Menyimpan rute distribusi sebagai LineString.

Contoh query PostGIS:

```sql
SELECT
    s.id,
    s.name,
    ST_DistanceSphere(s.location, sch.location) / 1000 AS distance_km
FROM sppg s
JOIN schools sch ON sch.tenant_id = s.tenant_id
WHERE s.id = :sppg_id
  AND sch.id = :school_id;
```

---

## 9. Modul Penerima Manfaat

### 9.1 Entitas

- beneficiary_groups
- beneficiaries
- school_beneficiary_summaries
- dietary_restrictions
- allergy_profiles

### 9.2 Data Utama

```text
beneficiary
- id UUID PRIMARY KEY DEFAULT gen_random_uuid()
- tenant_id
- school_id
- external_reference
- category
- age_group
- gender (opsional)
- dietary_restriction
- allergy_notes
- active_from
- active_to
```

Untuk efisiensi, data penerima dapat disimpan dalam bentuk individual atau agregat per sekolah/kelas sesuai kebutuhan regulasi dan privasi.

---

## 10. Modul Meal Plan dan Recipe

### 10.1 Tujuan

Mengelola perencanaan menu, standar gizi, resep, kebutuhan bahan, budget cost, realisasi produksi, dan evaluasi menu.

### 10.2 Entitas Utama

#### meal_plans

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
tenant_id
sppg_id
plan_date
meal_type
status
planned_portions
budget_cost_per_portion
nutrition_standard_id
approved_by
approved_at
notes
```

#### meal_plan_items

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
meal_plan_id
recipe_id
menu_component_type
planned_portions
planned_quantity
planned_cost
sequence
```

#### recipes

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
tenant_id
code
name
category
standard_portions
version
valid_from
valid_to
nutrition_profile_id
active
```

#### recipe_ingredients

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
recipe_id
product_id
quantity
uom_id
waste_factor_percent
yield_factor_percent
standard_unit_cost
```

#### nutrition_profiles

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
calories
protein_g
carbohydrate_g
fat_g
fiber_g
sodium_mg
other_nutrients_json
```

### 10.3 Kalkulasi Kebutuhan Bahan

```text
Gross Requirement =
(planned_portions / recipe_standard_portions)
× ingredient_quantity
× (1 + waste_factor)
```

### 10.4 Kalkulasi Planned Cost per Portion

```text
Planned Material Cost
+ Planned Labor Cost
+ Planned Utility Cost
+ Planned Packaging Cost
+ Planned Distribution Cost
+ Allocated Overhead
--------------------------------
Planned Portions
```

### 10.5 Status Meal Plan

```text
DRAFT
SUBMITTED
APPROVED
MATERIAL_RESERVED
IN_PRODUCTION
COMPLETED
CANCELLED
```

### 10.6 API Utama

```text
POST   /api/v1/meal-plans
GET    /api/v1/meal-plans
GET    /api/v1/meal-plans/{meal_plan_id}
POST   /api/v1/meal-plans/{meal_plan_id}/submit
POST   /api/v1/meal-plans/{meal_plan_id}/approve
POST   /api/v1/meal-plans/{meal_plan_id}/calculate-requirements
POST   /api/v1/meal-plans/{meal_plan_id}/reserve-materials
GET    /api/v1/meal-plans/{meal_plan_id}/cost-preview
```

---

## 11. Modul Procurement

### 11.1 Tujuan

Mengelola kebutuhan pembelian bahan berdasarkan meal plan, reorder stock, kontrak supplier, dan kebutuhan operasional.

### 11.2 Entitas

- suppliers
- supplier_products
- purchase_requests
- purchase_request_lines
- purchase_orders
- purchase_order_lines
- goods_receipts
- goods_receipt_lines
- supplier_price_histories

### 11.3 Workflow

```text
Meal Plan / Reorder Point
        ↓
Purchase Requirement
        ↓
Purchase Request
        ↓
Approval
        ↓
Purchase Order
        ↓
Goods Receipt
        ↓
Inventory Increase
        ↓
Budget Realization
        ↓
Accounting Journal
```

### 11.4 Kontrol Procurement

- Supplier aktif dan terverifikasi.
- Harga dibandingkan dengan histori.
- Harga melebihi toleransi memerlukan approval.
- Pembelian harus terkait budget line.
- Penerimaan harus mencatat kuantitas diterima dan ditolak.
- Batch, tanggal kedaluwarsa, dan kualitas dapat dicatat.

---

## 12. Modul Inventory

### 12.1 Tujuan

Mengelola persediaan bahan baku, bahan kemasan, barang konsumsi, perlengkapan, barang bantuan, dan barang operasional.

### 12.2 Entitas Utama

#### products

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
tenant_id
code
name
product_type
category_id
base_uom_id
stockable
track_batch
track_expiry
minimum_stock
maximum_stock
reorder_point
valuation_method
active
```

#### warehouses

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
tenant_id
sppg_id
code
name
warehouse_type
location
```

#### stock_locations

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
tenant_id
warehouse_id
code
name
location_type
parent_id
```

#### inventory_balances

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
tenant_id
sppg_id
location_id
product_id
batch_id
quantity_on_hand
quantity_reserved
quantity_available
average_cost
```

#### inventory_transactions

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
tenant_id
sppg_id
transaction_type
reference_type
reference_id
product_id
batch_id
source_location_id
destination_location_id
quantity
uom_id
unit_cost
total_cost
transaction_at
posted_by
```

#### inventory_batches

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
tenant_id
product_id
batch_number
production_date
expiry_date
supplier_id
```

### 12.3 Tipe Transaksi

```text
RECEIPT
ISSUE_TO_PRODUCTION
PRODUCTION_RETURN
INTERNAL_TRANSFER
DELIVERY_ISSUE
ADJUSTMENT_IN
ADJUSTMENT_OUT
DONATION_RECEIPT
DONATION_DISTRIBUTION
WASTE
EXPIRED
```

### 12.4 Metode Valuasi

Tahap awal direkomendasikan:

- Moving Average untuk bahan umum.
- FIFO untuk bahan dengan batch/expiry jika diperlukan.

### 12.5 Prinsip Data Stock

Jangan menjadikan `inventory_balances` sebagai satu-satunya sumber kebenaran. Sumber kebenaran adalah transaction ledger. Balance digunakan untuk optimasi baca dan harus selalu dapat direkonsiliasi.

### 12.6 Stock Reservation

Saat meal plan disetujui:

```text
available_stock >= requirement
    -> reserve
available_stock < requirement
    -> shortage report + purchase request suggestion
```

---

## 13. Modul Penerimaan Paket Bantuan

### 13.1 Tujuan

Mencatat bantuan non-pembelian yang diterima dari pemerintah, donor, investor, mitra, atau pihak lain.

### 13.2 Entitas

- aid_programs
- aid_receipts
- aid_receipt_lines
- aid_distributions
- aid_distribution_lines
- donors

### 13.3 Data Penerimaan

```text
aid_receipt
- id UUID PRIMARY KEY DEFAULT gen_random_uuid()
- tenant_id
- sppg_id
- donor_id
- aid_program_id
- receipt_number
- receipt_date
- source_document
- valuation_basis
- total_estimated_value
- status
```

### 13.4 Konsekuensi Accounting

Jika bantuan berupa barang dan perlu diakui nilainya:

```text
Dr Persediaan Bantuan
    Cr Pendapatan Hibah / Dana Terikat
```

Jika hanya memorandum/non-financial, transaksi disimpan di inventory tanpa jurnal finansial berdasarkan kebijakan organisasi.

---

## 14. Modul Produksi

### 14.1 Tujuan

Mencatat realisasi proses memasak dari bahan yang dikeluarkan hingga makanan siap didistribusikan.

### 14.2 Entitas

#### production_orders

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
tenant_id
sppg_id
meal_plan_id
production_date
status
planned_portions
actual_portions
started_at
completed_at
supervisor_id
```

#### production_materials

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
production_order_id
product_id
planned_quantity
reserved_quantity
issued_quantity
returned_quantity
waste_quantity
actual_unit_cost
actual_total_cost
```

#### production_outputs

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
production_order_id
recipe_id
planned_portions
actual_portions
rejected_portions
sample_portions
```

#### production_costs

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
production_order_id
cost_type
source_reference
quantity
unit_cost
amount
allocation_method
```

### 14.3 Komponen Actual Cost

- Material actual.
- Tenaga kerja langsung.
- Gas/bahan bakar.
- Listrik.
- Air.
- Packaging.
- Distribusi.
- Penyusutan alat yang dialokasikan.
- Overhead operasional.
- Waste dan reject.

### 14.4 Formula Actual Cost per Portion

```text
Actual Cost per Portion =
Total Actual Production Cost
----------------------------
Accepted / Distributed Portions
```

Disarankan menyimpan beberapa perspektif biaya:

```text
actual_cost_per_produced_portion
actual_cost_per_distributed_portion
actual_cost_per_accepted_portion
```

### 14.5 Variance Analysis

```text
Material Price Variance
Material Usage Variance
Labor Variance
Utility Variance
Packaging Variance
Distribution Variance
Total Cost Variance
```

### 14.6 Workflow

```text
Meal Plan Approved
        ↓
Material Reserved
        ↓
Production Order Created
        ↓
Material Issued
        ↓
Production Started
        ↓
Actual Consumption Recorded
        ↓
Output and Waste Recorded
        ↓
Production Completed
        ↓
Actual Cost Calculated
        ↓
Journal Posted
```

---

## 15. Modul Distribusi

### 15.1 Tujuan

Mengelola pengiriman makanan atau paket bantuan dari dapur ke sekolah/titik penerima.

### 15.2 Entitas

- delivery_plans
- delivery_routes
- delivery_route_stops
- delivery_orders
- delivery_order_lines
- delivery_proofs
- delivery_incidents
- vehicles
- drivers

### 15.3 Delivery Order

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
tenant_id
sppg_id
production_order_id
school_id
route_id
planned_departure
actual_departure
planned_arrival
actual_arrival
planned_portions
shipped_portions
received_portions
rejected_portions
status
receiver_name
receiver_gps
```

### 15.4 Proof of Delivery

- GPS lokasi penerimaan.
- Tanggal dan waktu.
- Nama penerima.
- Foto penerimaan.
- Tanda tangan digital.
- Jumlah diterima.
- Kondisi makanan/paket.
- Suhu saat diterima.
- Catatan insiden.

### 15.5 Status Distribusi

```text
PLANNED
LOADING
IN_TRANSIT
ARRIVED
RECEIVED
PARTIALLY_RECEIVED
REJECTED
CANCELLED
```

### 15.6 KPI Distribusi

- On-time departure rate.
- On-time arrival rate.
- Delivery completion rate.
- Average delivery time.
- Rejection rate.
- Temperature compliance.
- Cost per delivery.
- Cost per portion delivered.

---

## 16. Modul Feedback dan Evaluasi Layanan

### 16.1 Tujuan

Mengumpulkan data penerimaan layanan untuk mengevaluasi menu, kualitas makanan, distribusi, dan performa SPPG serta menjadi data pembelajaran AI.

### 16.2 Entitas

- feedback_submissions
- feedback_items
- menu_acceptance_records
- food_waste_records
- complaints
- service_quality_scores

### 16.3 Dimensi Feedback

- Acceptance rate.
- Taste rating.
- Portion suitability.
- Temperature.
- Packaging condition.
- Delivery timeliness.
- Appearance.
- Food waste.
- Complaint category.
- Free-text comment.

### 16.4 Sumber Feedback

- Kepala sekolah.
- Guru.
- Petugas penerima.
- Operator distribusi.
- Operator dapur.
- Orang tua.
- Penerima manfaat dengan UI sederhana.

### 16.5 Service Quality Index

Contoh formula:

```text
SQI =
25% Acceptance Rate
20% Food Waste Score
15% On-Time Delivery
10% Temperature Compliance
10% Taste Rating
10% Nutrition Compliance
10% Complaint Score
```

Bobot harus configurable per tenant atau kebijakan program.

---

## 17. Modul Budget Management

### 17.1 Tujuan

Mengelola pagu, alokasi, komitmen, realisasi, sisa anggaran, forecast, dan variance.

### 17.2 Entitas

#### budgets

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
tenant_id
name
fiscal_year
period_start
period_end
currency
status
approved_by
approved_at
```

#### budget_lines

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
budget_id
sppg_id
cost_center_id
account_id
budget_category_id
amount_allocated
amount_revised
amount_committed
amount_realized
amount_available
```

#### budget_transactions

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
tenant_id
budget_line_id
transaction_type
reference_type
reference_id
amount
transaction_date
status
```

### 17.3 Tipe Transaksi Budget

```text
ALLOCATION
REVISION_IN
REVISION_OUT
COMMITMENT
COMMITMENT_RELEASE
REALIZATION
REALIZATION_REVERSAL
TRANSFER_IN
TRANSFER_OUT
```

### 17.4 Formula Budget

```text
Available Budget =
Allocated + Revision In - Revision Out
- Commitment - Realization
```

### 17.5 Kontrol

- Soft warning saat penggunaan mendekati batas.
- Hard stop jika melebihi anggaran.
- Override hanya untuk role tertentu.
- Semua override harus masuk audit trail.
- Purchase Request dan transaksi expense harus memiliki budget line.

---

## 18. Modul Funding dan Pembiayaan

### 18.1 Tujuan

Mengelola dana pemerintah, dana talangan investor, modal pembangunan, modal kerja, jadwal pencairan, pengembalian, margin, dan outstanding.

### 18.2 Entitas

#### funding_sources

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
tenant_id
source_type
name
party_id
contract_number
start_date
end_date
status
```

#### funding_agreements

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
tenant_id
funding_source_id
agreement_type
principal_amount
margin_method
margin_rate
fixed_margin_amount
disbursement_schedule
repayment_terms
status
```

#### funding_disbursements

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
tenant_id
agreement_id
sppg_id
disbursement_date
amount
bank_account_id
reference_number
status
```

#### funding_repayments

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
tenant_id
agreement_id
repayment_date
principal_amount
margin_amount
penalty_amount
payment_reference
status
```

#### government_fund_claims

```text
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
tenant_id
sppg_id
claim_period
claim_number
portion_count
claim_amount
submitted_at
approved_amount
paid_amount
outstanding_amount
status
```

### 18.3 Funding Type

```text
GOVERNMENT_BUDGET
INVESTOR_BRIDGE_FUND
OWNER_CAPITAL
BANK_FINANCING
GRANT
DONATION
OTHER
```

### 18.4 KPI Funding

- Total dana ditempatkan.
- Outstanding dana talangan.
- Repayment ratio.
- Margin realized.
- Margin forecast.
- Government receivable aging.
- Cash runway.
- Funding utilization by SPPG.
- ROI per SPPG.

### 18.5 Catatan Kebijakan

Margin investor harus dimodelkan secara transparan berdasarkan kontrak, regulasi, dan struktur hukum yang berlaku. Sistem harus mendukung pemisahan:

- Pengembalian pokok.
- Biaya pendanaan.
- Margin pengelolaan.
- Reimbursement biaya infra.
- Operating fee.

---

## 19. Modul Accounting

### 19.1 Prinsip

Meskipun kebutuhan accounting relatif sederhana, engine harus menggunakan double-entry bookkeeping.

Setiap transaksi harus menghasilkan jurnal seimbang:

```text
Total Debit = Total Credit
```

### 19.2 Entitas Utama

- chart_of_accounts
- account_types
- journals
- journal_entries
- journal_entry_lines
- fiscal_periods
- cost_centers
- analytic_dimensions
- bank_accounts
- payment_transactions
- account_balances

### 19.3 Journal Entry

```text
journal_entries
- id UUID PRIMARY KEY DEFAULT gen_random_uuid()
- tenant_id
- entry_number
- journal_id
- entry_date
- reference_type
- reference_id
- description
- status
- posted_by
- posted_at
```

```text
journal_entry_lines
- id UUID PRIMARY KEY DEFAULT gen_random_uuid()
- journal_entry_id
- account_id
- sppg_id
- cost_center_id
- debit
- credit
- partner_id
- budget_line_id
- analytic_tags
```

### 19.4 Status Jurnal

```text
DRAFT
POSTED
REVERSED
CANCELLED
```

Jurnal posted tidak boleh diedit. Koreksi dilakukan dengan reversal entry.

### 19.5 Contoh Jurnal Otomatis

#### Dana investor masuk

```text
Dr Kas/Bank
    Cr Utang Dana Talangan Investor
```

#### Modal pemilik

```text
Dr Kas/Bank
    Cr Modal Pemilik
```

#### Pembelian bahan tunai

```text
Dr Persediaan Bahan
    Cr Kas/Bank
```

#### Pembelian kredit

```text
Dr Persediaan Bahan
    Cr Utang Supplier
```

#### Pemakaian bahan produksi

```text
Dr Biaya Produksi / WIP
    Cr Persediaan Bahan
```

#### Penyelesaian produksi

Jika makanan tidak disimpan sebagai finished goods dan langsung didistribusikan:

```text
Dr Beban Program Makanan
    Cr Biaya Produksi / WIP
```

#### Pencairan dana pemerintah

```text
Dr Kas/Bank
    Cr Piutang Pemerintah
```

Jika pengakuan pendapatan dilakukan saat klaim disetujui:

```text
Dr Piutang Pemerintah
    Cr Pendapatan Program
```

#### Pengembalian pokok investor

```text
Dr Utang Dana Talangan Investor
    Cr Kas/Bank
```

#### Pembayaran margin investor

```text
Dr Biaya Pendanaan / Bagi Hasil
    Cr Kas/Bank
```

### 19.6 Laporan Accounting

- General Ledger.
- Trial Balance.
- Balance Sheet.
- Income Statement / Statement of Activities.
- Cash Flow.
- Budget vs Actual.
- Government Receivable Aging.
- Supplier Payable Aging.
- Investor Funding Position.
- Cost by SPPG.
- Cost by program.
- Cost per portion.

---

## 20. Integrasi Transaksi Operasional dan Keuangan

Gunakan domain event agar satu transaksi operasional dapat memicu pencatatan modul lain.

Contoh event:

```text
GoodsReceiptPosted
InventoryIssuedToProduction
ProductionCompleted
DeliveryReceived
GovernmentClaimApproved
GovernmentFundReceived
InvestorFundDisbursed
InvestorRepaymentPosted
```

Contoh alur:

```text
Goods Receipt Posted
    ├── Update inventory ledger
    ├── Create budget realization
    ├── Create supplier payable
    ├── Create accounting journal
    └── Write audit log
```

Gunakan pola **transactional outbox** jika event akan dikirim ke worker atau service lain.

---

## 21. Reporting dan Dashboard

### 21.1 Prinsip

Dashboard tidak boleh menghitung semua data mentah secara langsung setiap request. Gunakan:

- Aggregate tables.
- Materialized views.
- Scheduled refresh.
- Incremental summary.
- Redis cache untuk metric populer.

### 21.2 Dashboard Operasional Dapur

Metric utama:

- SPPG aktif.
- Kapasitas harian.
- Planned portions.
- Produced portions.
- Distributed portions.
- Received portions.
- Production completion rate.
- Material shortage.
- Waste quantity dan waste percentage.
- Meal plan status.
- QC incident.
- Cost per portion.

Endpoint:

```text
GET /api/v1/dashboard/operations/summary
GET /api/v1/dashboard/operations/sppg-performance
GET /api/v1/dashboard/operations/production-trend
GET /api/v1/dashboard/operations/cost-per-portion
```

### 21.3 Dashboard Anggaran dan Keuangan

Metric utama:

- Total pagu.
- Total committed.
- Total realized.
- Available budget.
- Absorption rate.
- Actual vs budget variance.
- Cash balance.
- Government receivable.
- Investor funding outstanding.
- Repayment position.
- Margin realized.
- Cash runway.

Endpoint:

```text
GET /api/v1/dashboard/finance/budget-summary
GET /api/v1/dashboard/finance/funding-summary
GET /api/v1/dashboard/finance/cash-flow-forecast
GET /api/v1/dashboard/finance/investor-position
```

### 21.4 Dashboard Inventory

Metric:

- Stock value.
- Critical stock.
- Out-of-stock item.
- Overstock item.
- Near-expiry item.
- Waste stock.
- Stock accuracy.
- Consumption trend.
- Days of inventory.

### 21.5 Dashboard Distribusi

Metric:

- Delivery planned vs completed.
- On-time departure.
- On-time arrival.
- Delay by route.
- Rejected portions.
- Temperature compliance.
- Cost per route.
- Cost per delivered portion.

### 21.6 Dashboard Harga per Porsi

Metric:

- Target cost per portion.
- Actual cost per portion.
- Variance amount.
- Variance percentage.
- Cost component composition.
- Cost trend.
- SPPG ranking.
- Menu ranking.
- Supplier contribution to variance.

### 21.7 Dashboard GIS

Data per marker SPPG:

```text
status
capacity
planned portions
actual production
cost per portion
budget absorption
stock risk
delivery performance
service quality index
funding outstanding
```

Endpoint:

```text
GET /api/v1/gis/sppg-map
GET /api/v1/gis/service-coverage
GET /api/v1/gis/delivery-routes
GET /api/v1/gis/unserved-schools
GET /api/v1/gis/sppg-risk-heatmap
```

---

## 22. API Design Standard

### 22.1 Base URL

```text
/api/v1
```

### 22.2 Response Format

```json
{
  "data": {},
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-07-19T13:00:00+07:00"
  },
  "errors": []
}
```

### 22.3 Error Format

```json
{
  "data": null,
  "meta": {
    "request_id": "uuid"
  },
  "errors": [
    {
      "code": "BUDGET_EXCEEDED",
      "message": "Realisasi melebihi sisa anggaran.",
      "field": "amount",
      "details": {
        "available_budget": 10000000,
        "requested_amount": 12500000
      }
    }
  ]
}
```

### 22.4 Pagination

```text
?page=1&page_size=50
```

atau cursor pagination untuk data besar:

```text
?cursor=...&limit=100
```

### 22.5 Idempotency

Endpoint transaksi harus mendukung:

```text
Idempotency-Key: <uuid>
```

Wajib untuk:

- pembayaran;
- penerimaan barang;
- posting jurnal;
- pencairan dana;
- pengembalian investor;
- integrasi eksternal.

---

## 23. Audit Trail

Semua transaksi penting harus dicatat pada audit_logs.

```text
audit_logs
- id UUID PRIMARY KEY DEFAULT gen_random_uuid()
- tenant_id
- user_id
- action
- entity_type
- entity_id
- before_data
- after_data
- ip_address
- user_agent
- request_id
- created_at
```

Audit wajib untuk:

- perubahan budget;
- override limit;
- stock adjustment;
- pembatalan transaksi;
- perubahan rekening;
- posting dan reversal jurnal;
- perubahan kontrak funding;
- perubahan approval;
- perubahan data lokasi.

---

## 24. Penyimpanan Dokumen

Dokumen disimpan di object storage, bukan di kolom binary database besar.

Jenis dokumen:

- kontrak pemerintah;
- kontrak investor;
- purchase order;
- invoice supplier;
- bukti transfer;
- foto penerimaan;
- proof of delivery;
- sertifikat kualitas;
- laporan audit;
- foto food waste;

Tabel metadata:

```text
documents
- id UUID PRIMARY KEY DEFAULT gen_random_uuid()
- tenant_id
- entity_type
- entity_id
- category
- object_key
- original_filename
- mime_type
- size_bytes
- checksum
- uploaded_by
- uploaded_at
```

---

## 25. Background Jobs

Job yang dijalankan asynchronous:

- Refresh materialized view.
- Generate dashboard summary.
- Generate monthly financial report.
- Calculate cost allocation.
- Send notification.
- Recalculate stock balance.
- Sync external government data.
- Process uploaded file.
- Generate PDF report.
- AI feature extraction.
- GIS route recalculation.

---

## 26. Notification dan Early Warning

Jenis alert:

- Stock di bawah minimum.
- Barang mendekati kedaluwarsa.
- Actual cost melebihi target.
- Budget hampir habis.
- Purchase price abnormal.
- Produksi terlambat.
- Distribusi terlambat.
- Dana pemerintah belum cair.
- Cash runway di bawah batas.
- Investor repayment jatuh tempo.
- Food waste tinggi.
- SQI turun.

Channel:

- In-app notification.
- Email.
- WhatsApp gateway.
- Push notification.

---

## 27. Data untuk AI dan Recommendation Engine

Backend harus menyimpan data historis yang cukup granular.

### 27.1 Feature Set Menu Recommendation

- Menu dan komponen.
- Cost per portion.
- Nutrition values.
- Acceptance rate.
- Waste rate.
- Age group.
- School level.
- Region.
- Weather/season jika diintegrasikan.
- Supplier price.
- Stock availability.
- Menu frequency.
- Complaint category.

### 27.2 Feature Set Forecasting

- Historical portions.
- School calendar.
- Holiday.
- Attendance trend.
- Ingredient consumption.
- Purchase lead time.
- Supplier performance.
- Government payment delay.
- Cash balance.

### 27.3 Feature Set Anomaly Detection

- Quantity variance.
- Price variance.
- Consumption variance.
- Purchase timing.
- Supplier concentration.
- Repeated adjustment.
- Delivery rejection.
- Unusual journal pattern.

AI tidak boleh langsung melakukan posting transaksi. Rekomendasi AI harus melalui human approval kecuali untuk tindakan berisiko rendah yang telah dikonfigurasi.

---

## 28. Keamanan

### 28.1 Wajib

- HTTPS.
- Password hashing menggunakan Argon2 atau bcrypt.
- JWT access token berumur pendek.
- Refresh token rotation.
- MFA untuk role sensitif.
- Tenant isolation.
- Rate limiting.
- Audit log.
- Encryption at rest untuk secret dan data sensitif.
- Secure secret management.
- Input validation.
- SQL injection prevention melalui ORM/parameterized query.
- File type validation.
- Malware scanning untuk upload.

### 28.2 Hak Akses Finansial

Gunakan segregation of duties:

- Pembuat transaksi tidak boleh otomatis menyetujui.
- Pengguna yang mengubah rekening tidak boleh mengeksekusi pembayaran tanpa approval.
- Stock adjustment dan journal reversal memerlukan permission khusus.

---

## 29. Integritas dan Konsistensi Data

### 29.1 Prinsip Posting

Transaksi memiliki dua kondisi:

```text
DRAFT: dapat diedit
POSTED: immutable
```

### 29.2 Reversal

Transaksi posted tidak dihapus. Koreksi dilakukan dengan:

- reversal transaction;
- correction transaction;
- audit reference ke transaksi asal.

### 29.3 Database Transaction

Proses berikut harus atomic:

```text
Goods receipt
+ inventory posting
+ budget realization
+ accounting journal
```

Jika salah satu gagal, seluruh transaksi harus rollback.

---

## 30. Performance dan Skalabilitas

### 30.1 Index Wajib

```text
(tenant_id, id)
(tenant_id, sppg_id)
(tenant_id, transaction_date)
(tenant_id, status)
(tenant_id, product_id, location_id)
(tenant_id, meal_plan_id)
```

Gunakan GIST index untuk geometry:

```sql
CREATE INDEX idx_sppg_location_gist
ON sppg USING GIST (location);
```

### 30.2 Partitioning

Tabel besar dapat dipartisi berdasarkan bulan atau tahun:

- inventory_transactions.
- journal_entry_lines.
- delivery_tracking_events.
- audit_logs.
- feedback_submissions.

### 30.3 Read Model

Gunakan summary table terpisah untuk dashboard agar query transaksi tidak terganggu.

---

## 31. Dependency dan Prasyarat Instalasi

### 31.1 Versi Platform yang Direkomendasikan

Baseline lingkungan backend:

```text
Python          3.12 atau 3.13
PostgreSQL      18.x
PostGIS         3.6.x
SQLAlchemy      2.x
Alembic         versi stabil terbaru yang kompatibel dengan SQLAlchemy 2.x
FastAPI         versi stabil terbaru
Uvicorn         versi stabil terbaru
```

PostgreSQL 18 digunakan sebagai database utama. PostgreSQL 18 menyediakan dukungan native `uuidv7()`, sehingga sistem dapat memakai UUID yang terurut berdasarkan waktu untuk tabel transaksi berukuran besar. PostGIS 3.6 mendukung PostgreSQL 18 dan digunakan untuk tipe `geometry`, spatial index GiST, analisis radius, rute, titik lokasi, dan area layanan.

Untuk produksi, versi paket Python harus dikunci melalui lock file. Jangan menggunakan rentang versi terbuka tanpa proses pengujian regresi.

### 31.2 Dependency Sistem Operasi

Contoh instalasi pada Ubuntu/Debian:

```bash
sudo apt update
sudo apt install -y \
  build-essential \
  python3-dev \
  python3-venv \
  libpq-dev \
  libssl-dev \
  libffi-dev \
  pkg-config \
  curl \
  git \
  postgresql-18 \
  postgresql-client-18 \
  postgresql-18-postgis-3 \
  postgresql-18-postgis-3-scripts
```

Nama paket PostgreSQL/PostGIS dapat berbeda sesuai repository dan distribusi Linux. Pastikan repository PostgreSQL Global Development Group dan repository PostGIS yang sesuai sudah aktif jika paket belum tersedia pada repository bawaan OS.

Aktifkan extension database:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS btree_gist;
```

Verifikasi:

```sql
SELECT version();
SELECT postgis_full_version();
SELECT gen_random_uuid();
SELECT uuidv7();
```

`postgis_topology` bersifat opsional. Extension tersebut hanya diperlukan jika aplikasi benar-benar memakai topology model. Untuk kebutuhan titik dapur, sekolah, supplier, area layanan, dan rute, extension `postgis` sudah mencukupi.

### 31.3 Dependency Python Utama

Dependency yang diperlukan dikelompokkan sebagai berikut.

#### A. Web API dan konfigurasi

| Paket | Fungsi |
|---|---|
| `fastapi` | Framework REST API dan dependency injection. |
| `uvicorn[standard]` | ASGI server untuk development dan production worker. |
| `pydantic` | Validasi request/response dan domain schema. |
| `pydantic-settings` | Loading konfigurasi berbasis environment variables. |
| `python-dotenv` | Membaca `.env` pada development dan tooling lokal. |
| `python-multipart` | Upload file dan form-data. |
| `email-validator` | Validasi `EmailStr` pada Pydantic. |
| `httpx` | HTTP client async untuk integrasi eksternal dan API test. |
| `jinja2` | Template email, laporan HTML, atau dokumen server-side. |

Walaupun `python-dotenv` digunakan, seluruh aplikasi sebaiknya mengakses konfigurasi melalui satu class `Settings` berbasis `pydantic-settings`. Modul bisnis tidak boleh memanggil `os.getenv()` secara langsung.

#### B. ORM, migration, database, dan GIS

| Paket | Fungsi |
|---|---|
| `sqlalchemy[asyncio]` | ORM dan SQL toolkit dengan async support. |
| `alembic` | Versioning dan migrasi schema database. |
| `asyncpg` | Driver PostgreSQL asynchronous untuk runtime FastAPI. |
| `psycopg2-binary` | Driver synchronous untuk utility, script lama, atau tooling tertentu. |
| `greenlet` | Dependency SQLAlchemy untuk bridging context tertentu. |
| `aiosqlite` | Database SQLite async khusus unit test atau development ringan. |
| `geoalchemy2` | Mapping tipe PostGIS `Geometry`/`Geography` pada SQLAlchemy. |

Driver utama aplikasi adalah `asyncpg`:

```env
DATABASE_URL=postgresql+asyncpg://erp_mbg:password@localhost:5432/erp_mbg
```

URL synchronous untuk Alembic atau utility tertentu:

```env
DATABASE_SYNC_URL=postgresql+psycopg2://erp_mbg:password@localhost:5432/erp_mbg
```

Walaupun `psycopg2-binary` praktis untuk instalasi, deployment produksi yang sangat ketat dapat menggunakan build `psycopg2` dari source atau beralih ke `psycopg` generasi baru setelah seluruh migration tooling diuji. Jangan memakai `asyncpg` dan `psycopg2` secara bergantian dalam satu transaction boundary.

`aiosqlite` tidak digunakan sebagai database produksi karena perilaku locking, tipe data, UUID, JSONB, constraint, dan fitur GIS berbeda dari PostgreSQL. Gunakan PostgreSQL/PostGIS untuk integration test yang memverifikasi query nyata.

#### C. Authentication dan cryptography

| Paket | Fungsi |
|---|---|
| `passlib[bcrypt]` | Abstraksi hashing password. |
| `bcrypt` | Algoritma hashing password. |
| `python-jose[cryptography]` | Encoding dan decoding JWT/JWS. |
| `cryptography` | Primitive cryptography, key handling, dan backend JOSE. |

Aturan keamanan:

- Password tidak pernah disimpan dalam bentuk plaintext.
- JWT access token berumur pendek.
- Refresh token disimpan sebagai hash dan dapat dicabut.
- Secret dan private key hanya berasal dari environment/secret manager.
- Untuk deployment baru, pertimbangkan algoritma password modern seperti Argon2. Jika tetap menggunakan bcrypt, lakukan compatibility test antara versi `passlib` dan `bcrypt` sebelum mengunci lock file.

#### D. Testing dan quality assurance

| Paket | Fungsi |
|---|---|
| `pytest` | Test runner. |
| `pytest-asyncio` | Menjalankan async unit dan integration test. |
| `pytest-cov` | Coverage report. |
| `httpx` | Test client asynchronous untuk FastAPI. |

Dependency tambahan yang disarankan:

| Paket | Fungsi |
|---|---|
| `ruff` | Linting dan formatting. |
| `mypy` | Static type checking. |
| `pre-commit` | Menjalankan pemeriksaan otomatis sebelum commit. |
| `factory-boy` | Pembuatan fixture data kompleks. |
| `testcontainers[postgres]` | PostgreSQL/PostGIS disposable untuk integration test. |

#### E. AI, image processing, dan inference

| Paket | Fungsi |
|---|---|
| `google-genai` | Integrasi Gemini/Google Gen AI untuk insight, summarization, dan recommendation. |
| `pillow` | Pembacaan dan transformasi gambar. |
| `numpy` | Komputasi array dan preprocessing model. |
| `onnxruntime` | Menjalankan model ONNX untuk inference. |

Dependency ini ditempatkan pada integration layer atau worker AI, bukan di domain service inti. Modul operasional harus tetap dapat berjalan ketika provider AI tidak tersedia.

Struktur yang disarankan:

```text
app/integrations/ai/
├── client.py
├── schemas.py
├── prompts/
├── providers/
│   ├── google_genai.py
│   └── onnx_runtime.py
└── services/
    ├── meal_recommendation.py
    ├── anomaly_explanation.py
    └── feedback_classification.py
```

### 31.4 Dependency File untuk `pyproject.toml`

Contoh deklarasi dependency berbasis Poetry/PEP 621:

```toml
[project]
name = "erp-mbg-backend"
version = "0.1.0"
requires-python = ">=3.12,<3.14"
dependencies = [
  "fastapi",
  "uvicorn[standard]",
  "pydantic",
  "pydantic-settings",
  "python-dotenv",
  "python-multipart",
  "email-validator",
  "httpx",
  "jinja2",

  "sqlalchemy[asyncio]",
  "alembic",
  "asyncpg",
  "psycopg2-binary",
  "greenlet",
  "geoalchemy2",

  "passlib[bcrypt]",
  "bcrypt",
  "python-jose[cryptography]",
  "cryptography",

  "google-genai",
  "pillow",
  "numpy",
  "onnxruntime",
]

[project.optional-dependencies]
test = [
  "aiosqlite",
  "pytest",
  "pytest-asyncio",
  "pytest-cov",
  "httpx",
]
dev = [
  "ruff",
  "mypy",
  "pre-commit",
  "factory-boy",
  "testcontainers[postgres]",
]
```

Setelah versi-versi tervalidasi pada CI, hasil resolusi wajib dikunci dengan tool yang dipilih, misalnya `uv.lock`, `poetry.lock`, atau `requirements.lock`.

### 31.5 Alternatif `requirements` Terpisah

Untuk proyek yang menggunakan `pip`, pisahkan dependency berdasarkan lingkungan:

```text
requirements/
├── base.txt
├── production.txt
├── development.txt
├── testing.txt
└── ai.txt
```

Contoh `requirements/base.txt`:

```text
fastapi
uvicorn[standard]
pydantic
pydantic-settings
python-dotenv
python-multipart
email-validator
httpx
jinja2
sqlalchemy[asyncio]
alembic
asyncpg
psycopg2-binary
greenlet
geoalchemy2
passlib[bcrypt]
bcrypt
python-jose[cryptography]
cryptography
```

Contoh `requirements/ai.txt`:

```text
google-genai
pillow
numpy
onnxruntime
```

Contoh `requirements/testing.txt`:

```text
-r base.txt
aiosqlite
pytest
pytest-asyncio
pytest-cov
```

### 31.6 Instalasi Virtual Environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements/base.txt
pip install -r requirements/ai.txt
pip install -r requirements/testing.txt
```

Atau dengan `uv`:

```bash
uv venv --python 3.12
source .venv/bin/activate
uv sync --all-extras
```

### 31.7 Konfigurasi `.env`

Tambahkan konfigurasi minimal berikut pada `.env.example`:

```env
APP_NAME=ERP MBG Backend
APP_ENV=development
APP_DEBUG=true
APP_HOST=0.0.0.0
APP_PORT=8000
API_V1_PREFIX=/api/v1

DATABASE_URL=postgresql+asyncpg://erp_mbg:change-me@127.0.0.1:5432/erp_mbg
DATABASE_SYNC_URL=postgresql+psycopg2://erp_mbg:change-me@127.0.0.1:5432/erp_mbg
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=1800
DATABASE_ECHO=false

JWT_SECRET_KEY=replace-with-long-random-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30
PASSWORD_HASH_SCHEME=bcrypt

CORS_ALLOWED_ORIGINS=["http://localhost:5173"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOWED_METHODS=["GET","POST","PUT","PATCH","DELETE","OPTIONS"]
CORS_ALLOWED_HEADERS=["Authorization","Content-Type","X-Request-ID","X-Tenant-ID"]

GOOGLE_GENAI_API_KEY=
GOOGLE_GENAI_MODEL=
ONNXRUNTIME_PROVIDERS=["CPUExecutionProvider"]

UPLOAD_MAX_SIZE_MB=20
MEDIA_ROOT=./storage/media
TEMPLATE_ROOT=./app/templates
```

Jangan menyimpan `.env.production` di Git. Repository hanya menyimpan `.env.example` tanpa credential nyata.

### 31.8 SQLAlchemy Async Engine

```python
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config.settings import settings

engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_timeout=settings.database_pool_timeout,
    pool_recycle=settings.database_pool_recycle,
    echo=settings.database_echo,
)

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)
```

Gunakan satu `AsyncSession` per request atau per background job. Service tidak boleh membuat engine baru.

### 31.9 Alembic dan PostGIS

`alembic/env.py` harus mengimpor seluruh metadata model dari semua modul sebelum menjalankan autogenerate. Karena model tersebar per domain, buat central model registry:

```python
# app/core/database/model_registry.py
from app.modules.identity.models import *
from app.modules.tenant.models import *
from app.modules.sppg.models import *
from app.modules.geography.models import *
from app.modules.inventory.models import *
from app.modules.production.models import *
from app.modules.accounting.models import *
```

Migration awal harus mengaktifkan extension:

```python
from alembic import op


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
```

Untuk kolom GIS:

```python
from geoalchemy2 import Geometry
from sqlalchemy.orm import Mapped, mapped_column

location: Mapped[object] = mapped_column(
    Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
    nullable=False,
)
```

Setelah autogenerate, migration GIS harus direview manual. Pastikan index GiST, SRID, geometry type, dan constraint dibuat sesuai desain.

### 31.10 Strategi UUID pada PostgreSQL 18

Untuk tabel master atau data yang dibuat dari banyak sumber, UUID v4 tetap aman:

```sql
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
```

Untuk tabel transaksi dengan volume tinggi, PostgreSQL 18 dapat memakai UUID v7:

```sql
id UUID PRIMARY KEY DEFAULT uuidv7()
```

UUID v7 memberi locality index yang lebih baik dibanding UUID v4 acak. Namun aplikasi harus menetapkan satu strategi yang konsisten per kategori tabel dan tidak mengganti default UUID tanpa migration plan.

### 31.11 Pemeriksaan Instalasi

Jalankan pemeriksaan berikut setelah instalasi:

```bash
python -c "import fastapi, sqlalchemy, asyncpg, alembic, pydantic"
python -c "import geoalchemy2, google.genai, PIL, numpy, onnxruntime"
pytest --cov=app --cov-report=term-missing
alembic current
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Health check minimal:

```text
GET /health/live
GET /health/ready
GET /health/database
GET /health/gis
```

`/health/ready` harus gagal jika koneksi database atau migration state belum siap. Pemeriksaan provider AI tidak boleh membuat API utama dianggap tidak sehat, kecuali deployment tersebut memang dikhususkan sebagai AI worker.

### 31.12 Dependency Governance

- Semua dependency wajib melalui lock file.
- CI menjalankan security audit dan dependency vulnerability scan.
- Upgrade dependency dilakukan pada branch terpisah dengan regression test.
- Runtime dependency dan development dependency dipisahkan.
- Paket AI yang berat dapat ditempatkan dalam worker/deployment image terpisah.
- Jangan memasukkan API key, password, atau secret ke source code maupun image Docker.
- Catat lisensi dependency yang dipakai untuk kebutuhan SaaS komersial.
- Lakukan benchmark sebelum mengaktifkan ONNX Runtime provider GPU.

---

## 32. Testing Strategy

### 31.1 Unit Test

- Formula kebutuhan bahan.
- Cost per portion.
- Budget availability.
- Journal balance.
- Stock valuation.
- Funding repayment.

### 31.2 Integration Test

- Purchase receipt sampai jurnal.
- Meal plan sampai produksi.
- Produksi sampai distribusi.
- Funding disbursement sampai accounting.
- Government claim sampai receipt.

### 31.3 Security Test

- Cross-tenant access.
- Privilege escalation.
- Unauthorized posting.
- File upload validation.
- JWT manipulation.

### 31.4 Reconciliation Test

- Inventory ledger vs stock balance.
- Journal debit vs credit.
- Budget realization vs journal expense.
- Funding outstanding vs general ledger.

---

## 33. Tahapan Implementasi

### Fase 1 — Foundation

- Project structure.
- Authentication.
- Tenant management.
- User, role, permission.
- SPPG master.
- GIS basic.
- Product and warehouse master.
- Audit log.

### Fase 2 — Core Operations

- Meal plan.
- Recipe.
- Material requirement.
- Procurement.
- Inventory.
- Production.
- Actual cost per portion.

### Fase 3 — Distribution and Feedback

- School assignment.
- Delivery planning.
- Route and proof of delivery.
- Feedback.
- Food waste.
- Service Quality Index.

### Fase 4 — Financial Control

- Budget.
- Funding.
- Government claim.
- Investor bridge fund.
- Accounting ledger.
- Auto journal.
- Reconciliation.

### Fase 5 — Dashboard and Reporting

- Operational dashboard.
- Budget dashboard.
- Investor dashboard.
- Inventory dashboard.
- Distribution dashboard.
- GIS dashboard.
- Cost per portion analytics.

### Fase 6 — Intelligence

- Daily AI summary.
- Anomaly detection.
- Menu recommendation.
- Demand forecast.
- Cash flow forecast.
- Route optimization.
- Site selection support.

---

## 34. Prioritas MVP

MVP sebaiknya tidak langsung mencakup seluruh fitur advanced.

### MVP Wajib

1. Multi-tenant dan user management.
2. Master SPPG dan lokasi GPS.
3. Master sekolah/titik penerima.
4. Meal plan dan recipe.
5. Material requirement.
6. Purchase request dan goods receipt.
7. Inventory ledger.
8. Production order.
9. Actual material consumption.
10. Actual cost per portion.
11. Delivery order dan proof of delivery.
12. Budget allocation dan realization.
13. Funding disbursement dan repayment.
14. Double-entry accounting dasar.
15. Dashboard operasional dan keuangan dasar.
16. Audit trail.

### Setelah MVP

- AI recommendation.
- Advanced routing.
- Automated forecast.
- Full investor portal.
- Government portal.
- Vision AI food waste.
- Complex asset management.

---

## 35. Indikator Keberhasilan Sistem

Sistem dianggap berhasil apabila dapat menjawab secara cepat dan konsisten:

- Berapa porsi direncanakan, diproduksi, dikirim, dan diterima?
- Berapa actual cost per porsi setiap menu dan SPPG?
- Komponen biaya mana yang menyebabkan variance?
- Berapa stock tersedia, reserved, dan kritis?
- Berapa anggaran yang dialokasikan, committed, realized, dan tersisa?
- Berapa dana investor yang telah ditempatkan dan belum kembali?
- Berapa dana pemerintah yang masih outstanding?
- SPPG mana yang paling efisien dan paling berisiko?
- Sekolah mana yang belum terlayani atau mengalami keterlambatan?
- Menu mana yang paling diterima dan menghasilkan waste paling rendah?
- Apakah seluruh transaksi operasional telah tercermin dalam accounting?

---

## 36. Kesimpulan Desain

Backend ERP Pengelolaan Dapur MBG sebaiknya dibangun sebagai platform FastAPI modular, multi-tenant, API-first, dan terintegrasi dengan PostgreSQL/PostGIS.

Empat domain inti sistem adalah:

1. **Kitchen Operations** — meal plan, recipe, procurement, inventory, production, distribusi, feedback.
2. **Financial Control** — budget, funding, modal, dana talangan, realisasi, accounting.
3. **GIS & Network Management** — lokasi dapur, sekolah, coverage, rute, heatmap, ekspansi.
4. **Analytics & Intelligence** — dashboard, cost per portion, variance, KPI, AI recommendation.

Accounting harus menjadi financial ledger yang menerima konsekuensi otomatis dari transaksi operasional. Inventory harus menggunakan transaction ledger. Budget harus terhubung dengan commitment dan realization. Funding investor harus dipisahkan antara pokok, margin, biaya pendanaan, dan pengembalian. Seluruh data harus memiliki tenant isolation dan audit trail.

Dengan desain ini, platform dapat berkembang dari ERP operasional menjadi **AI-powered Operational, Financial, and Geospatial Intelligence Platform untuk jaringan SPPG/MBG**.
