# ERP Pengelolaan Dapur MBG

## Enterprise Domain Model v3.0

**Arsitektur:** Domain-Driven Design
**Pola implementasi:** Modular Monolith
**Backend:** FastAPI
**Database:** PostgreSQL 18 + PostGIS
**Primary Key:** UUID
**Frontend:** Vue.js
**Versi dokumen:** 3.0

---

# 1. Tujuan Dokumen

Dokumen ini menetapkan pembagian domain bisnis, batas tanggung jawab modul, kepemilikan data, hubungan antardomain, serta event utama dalam ERP Pengelolaan Dapur MBG.

Tujuan utamanya adalah:

* mencegah model database menjadi terlalu terpusat dan saling bergantung;
* memastikan setiap modul memiliki tanggung jawab yang jelas;
* mendukung satu Tenant mengelola banyak SPPG/Dapur;
* mendukung satu Program melibatkan banyak Tenant dan SPPG;
* menyediakan dasar implementasi FastAPI modular;
* memudahkan pemisahan modul menjadi microservice di masa depan;
* memastikan accounting, budget, inventory, produksi, dan distribusi tetap terintegrasi.

---

# 2. Prinsip Arsitektur

## 2.1 Modular Monolith

Sistem dibangun sebagai satu aplikasi FastAPI dan satu database PostgreSQL, tetapi setiap domain dipisahkan secara ketat pada level:

* model;
* schema;
* repository;
* service;
* route;
* permission;
* event;
* command;
* query;
* exception.

Struktur ini memberikan kesederhanaan operasional monolith tanpa menghasilkan ketergantungan kode yang tidak terkendali.

## 2.2 Domain Ownership

Setiap data hanya memiliki satu domain sebagai **source of truth**.

Contoh:

* `sppg` / `kitchen` dimiliki domain Organization;
* `stock_balance` dimiliki domain Inventory;
* `production_batch` dimiliki domain Production;
* `journal_entry` dimiliki domain Accounting;
* `budget_commitment` dimiliki domain Budget Control.

Domain lain tidak diperbolehkan mengubah tabel tersebut secara langsung.

## 2.3 Komunikasi Antardomain

Komunikasi dilakukan melalui:

1. application service;
2. command;
3. query interface;
4. internal domain event.

Domain tidak diperbolehkan mengimpor repository domain lain secara langsung.

Contoh yang tidak diperbolehkan:

```python
# production/service.py
from app.modules.inventory.repository import StockRepository
```

Pola yang disarankan:

```python
await event_bus.publish(
    MaterialsConsumed(
        production_batch_id=batch.id,
        kitchen_id=batch.kitchen_id,
        items=consumption_items,
    )
)
```

Domain Inventory kemudian memproses event tersebut melalui handler miliknya.

---

# 3. Hierarki Organisasi Utama

Struktur organisasi sistem adalah:

```text
Platform
└── Tenant
    ├── Regional (opsional)
    ├── Kitchen / SPPG
    ├── User
    └── Tenant Configuration
```

Struktur program adalah:

```text
Program
├── Program Tenant
├── Program Kitchen
├── Budget
├── Funding Source
└── Reporting Period
```

Program tidak ditempatkan secara permanen di atas Tenant karena hubungan bisnisnya bersifat banyak-ke-banyak.

Satu Tenant dapat mengikuti beberapa Program, sedangkan satu Program dapat melibatkan banyak Tenant.

```text
Tenant >──< Program
```

Relasi tersebut disimpan melalui:

```text
program_tenant
```

Kitchen/SPPG dapat ditugaskan pada Program melalui:

```text
program_kitchen
```

Dengan model ini, Kitchen tidak perlu dipindahkan dari Tenant ketika mengikuti Program yang berbeda.

---

# 4. Daftar Bounded Context

ERP MBG dibagi menjadi bounded context berikut.

| No. | Bounded Context        | Tanggung Jawab Utama                                            |
| --: | ---------------------- | --------------------------------------------------------------- |
|   1 | Identity & Access      | User, autentikasi, role, permission, scope                      |
|   2 | Organization           | Tenant, regional, Kitchen/SPPG, konfigurasi                     |
|   3 | Program Management     | Program, pendanaan, periode, penugasan Tenant dan Kitchen       |
|   4 | Geography & GIS        | wilayah administrasi, koordinat, polygon, radius, spatial query |
|   5 | Master Product         | produk, kategori, UoM, bahan, atribut                           |
|   6 | Supplier & Procurement | supplier, permintaan pembelian, PO, penerimaan                  |
|   7 | Warehouse & Inventory  | gudang, lokasi stok, movement, balance, lot                     |
|   8 | Meal Planning          | siklus menu, rencana menu, target porsi                         |
|   9 | Recipe & Nutrition     | resep, komposisi, konversi UoM, nilai gizi                      |
|  10 | Production             | production order, batch, konsumsi, hasil, waste                 |
|  11 | Quality Control        | pemeriksaan bahan, proses, hasil, tindakan koreksi              |
|  12 | Distribution           | penerima, rute, pengiriman, proof of delivery                   |
|  13 | Fleet                  | kendaraan, pengemudi, jadwal, biaya operasional                 |
|  14 | Budget Control         | pagu, alokasi, reservasi, komitmen, realisasi                   |
|  15 | Accounting             | CoA, jurnal, ledger, periode, laporan keuangan                  |
|  16 | Costing                | biaya bahan, tenaga kerja, overhead, cost per portion           |
|  17 | Government Claim       | klaim biaya, dokumen pendukung, pembayaran pemerintah           |
|  18 | Investor & Funding     | modal investor, pencairan, pengembalian, keuntungan             |
|  19 | Workforce              | pegawai, penempatan, jadwal, tenaga produksi                    |
|  20 | Workflow               | definisi proses, state, transition, approval                    |
|  21 | Notification           | notifikasi internal, email, WhatsApp, push                      |
|  22 | Audit & Compliance     | audit trail, perubahan data, aktivitas kritis                   |
|  23 | Reporting & Dashboard  | read model, agregasi, KPI, ekspor                               |
|  24 | Document Management    | lampiran, bukti transaksi, versi dokumen                        |
|  25 | AI & Forecasting       | prediksi kebutuhan, biaya, produksi, waste                      |
|  26 | Integration            | API eksternal, webhook, import, export, sinkronisasi            |

---

# 5. Organization Context

## 5.1 Tanggung Jawab

Domain Organization mengelola:

* Tenant;
* Regional;
* Kitchen/SPPG;
* profil operasional Kitchen;
* kapasitas Kitchen;
* manager Kitchen;
* status operasional;
* hubungan Kitchen dengan gudang utama;
* konfigurasi tenant dan Kitchen.

## 5.2 Aggregate Utama

```text
Tenant
Regional
Kitchen
TenantSetting
KitchenSetting
```

## 5.3 Relasi

```text
Tenant 1 ─── N Regional
Tenant 1 ─── N Kitchen
Regional 1 ─── N Kitchen
```

`regional_id` pada Kitchen bersifat opsional.

## 5.4 Kitchen sebagai Unit Operasional

Kitchen/SPPG merupakan unit utama untuk:

* perencanaan menu;
* produksi;
* inventory;
* distribusi;
* budget;
* costing;
* accounting dimensional reporting;
* monitoring GIS.

Setiap transaksi operasional wajib memiliki `kitchen_id`, kecuali transaksi yang secara sah hanya terjadi pada level Tenant atau Program.

## 5.5 Data Lokasi Kitchen

Kitchen memiliki:

```text
address
province_id
city_id
district_id
village_id
latitude
longitude
geom
service_radius_meter
timezone
```

`geom` menggunakan:

```sql
GEOGRAPHY(Point, 4326)
```

atau `Geometry(Point, 4326)` apabila sebagian besar operasi menggunakan proyeksi dan fungsi geometri.

---

# 6. Program Management Context

## 6.1 Tujuan

Program Management memisahkan pengelola organisasi dari sumber program dan pendanaan.

Contoh Program:

* MBG APBN 2026;
* MBG APBD Provinsi;
* Program CSR;
* Program Pilot;
* Program Donasi;
* Program Perluasan Wilayah.

## 6.2 Aggregate Utama

```text
Program
ProgramPeriod
ProgramTenant
ProgramKitchen
FundingSource
ProgramTarget
ProgramPolicy
```

## 6.3 Relasi

```text
Program N ─── N Tenant
Program N ─── N Kitchen
Program 1 ─── N ProgramPeriod
Program 1 ─── N FundingSource
```

Tabel penghubung:

```text
program_tenant
program_kitchen
```

## 6.4 Aturan

* Kitchen tetap dimiliki oleh satu Tenant.
* Program tidak memiliki Kitchen secara langsung.
* Kitchen ditugaskan ke Program untuk periode tertentu.
* Penugasan Kitchen dapat memiliki tanggal mulai dan selesai.
* Transaksi program harus menggunakan `program_id`.
* Transaksi nonprogram boleh memiliki `program_id = NULL` bila memang diperbolehkan kebijakan sistem.

---

# 7. Geography & GIS Context

## 7.1 Tanggung Jawab

Domain GIS mengelola:

* master wilayah administrasi;
* titik lokasi Kitchen;
* titik lokasi sekolah/penerima;
* polygon wilayah layanan;
* radius pelayanan;
* spatial query;
* nearest Kitchen;
* heatmap;
* layer peta;
* analisis cakupan distribusi.

## 7.2 Aggregate Utama

```text
Province
CityRegency
District
Village
ServiceArea
MapLayer
GeoFeature
```

## 7.3 Kepemilikan Data

Data profil Kitchen tetap dimiliki domain Organization.

Domain GIS memiliki:

* geometry;
* polygon;
* spatial index;
* hasil analisis spasial;
* layer visualisasi.

Untuk implementasi awal, field `geom` dapat tetap disimpan di tabel `kitchen`. Ketika kebutuhan GIS berkembang, detail spasial dapat dipisahkan ke tabel `kitchen_geo_profile`.

## 7.4 Spatial Index

```sql
CREATE INDEX ix_kitchen_geom_gist
ON kitchen
USING GIST (geom);
```

## 7.5 Contoh Query Radius

```sql
SELECT
    id,
    name,
    ST_Distance(
        geom,
        ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)::geography
    ) AS distance_meter
FROM kitchen
WHERE ST_DWithin(
    geom,
    ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)::geography,
    :radius_meter
);
```

---

# 8. Master Product Context

## 8.1 Tanggung Jawab

Domain ini mengelola master semua barang dan bahan yang digunakan sistem.

## 8.2 Aggregate Utama

```text
Product
ProductCategory
ProductType
UoM
UoMCategory
UoMConversion
ProductUoM
ProductAttribute
ProductBarcode
```

## 8.3 Jenis Produk

```text
INGREDIENT
PACKAGING
SUPPLY
FUEL
CLEANING_MATERIAL
FINISHED_MEAL
SERVICE
ASSET
OTHER
```

## 8.4 UoM Wajib Digunakan

UoM tetap diperlukan karena pembelian, penyimpanan, resep, dan konsumsi dapat menggunakan satuan berbeda.

Contoh:

```text
Pembelian beras  : karung
Penyimpanan      : kilogram
Pemakaian resep  : gram
```

Konversi harus dilakukan melalui tabel UoM, bukan angka konversi yang ditulis langsung pada transaksi.

---

# 9. Recipe & Nutrition Context

## 9.1 Tanggung Jawab

Mengelola:

* resep;
* versi resep;
* komponen bahan;
* yield;
* serving size;
* nilai gizi;
* allergen;
* kehilangan normal;
* substitusi bahan.

## 9.2 Aggregate Utama

```text
Recipe
RecipeVersion
RecipeIngredient
RecipeYield
NutritionProfile
NutritionValue
Allergen
RecipeSubstitution
```

## 9.3 Versioning

Resep wajib menggunakan versi.

```text
Recipe
└── RecipeVersion
    └── RecipeIngredient
```

Meal Plan dan Production Order harus mereferensikan `recipe_version_id`, bukan hanya `recipe_id`, agar histori komposisi tidak berubah ketika resep diperbarui.

---

# 10. Meal Planning Context

## 10.1 Tanggung Jawab

Mengelola:

* siklus menu;
* kalender menu;
* rencana porsi;
* target penerima;
* rencana kebutuhan bahan;
* status persetujuan meal plan.

## 10.2 Aggregate Utama

```text
MealCycle
MealPlan
MealPlanDay
MealPlanItem
MealTarget
MealPlanMaterialRequirement
```

## 10.3 Relasi Utama

```text
Kitchen 1 ─── N MealPlan
Program 1 ─── N MealPlan
MealPlan 1 ─── N MealPlanDay
MealPlanDay 1 ─── N MealPlanItem
MealPlanItem N ─── 1 RecipeVersion
```

## 10.4 Output Domain

Meal Planning menghasilkan:

* kebutuhan bahan terencana;
* kebutuhan porsi;
* kebutuhan produksi;
* baseline cost per portion.

Output tersebut digunakan oleh:

* Procurement;
* Inventory;
* Production;
* Budget Control;
* Costing.

---

# 11. Procurement Context

## 11.1 Tanggung Jawab

Mengelola:

* supplier;
* purchase requisition;
* request for quotation;
* purchase order;
* harga pembelian;
* approval pembelian;
* penerimaan dan invoice reference.

## 11.2 Aggregate Utama

```text
Supplier
SupplierProduct
PurchaseRequisition
PurchaseRequisitionLine
RequestForQuotation
PurchaseOrder
PurchaseOrderLine
PurchaseReceiptReference
```

## 11.3 Hubungan dengan Budget

Sebelum Purchase Order disetujui, Procurement meminta pemeriksaan anggaran kepada Budget Control.

```text
Purchase Requisition
        ↓
Budget Availability Check
        ↓
Budget Reservation
        ↓
Purchase Approval
        ↓
Purchase Order
```

Procurement tidak mengubah saldo budget secara langsung.

---

# 12. Warehouse & Inventory Context

## 12.1 Tanggung Jawab

Mengelola:

* warehouse;
* storage location;
* stock movement;
* stock balance;
* lot/batch;
* expiration date;
* reservation;
* stock adjustment;
* transfer antar lokasi;
* transfer antar Kitchen bila diperbolehkan.

## 12.2 Aggregate Utama

```text
Warehouse
StockLocation
StockItem
StockLot
StockMovement
StockMovementLine
StockBalance
StockReservation
StockAdjustment
```

## 12.3 Warehouse dan Kitchen

Setiap Warehouse dimiliki satu Kitchen:

```text
Kitchen 1 ─── N Warehouse
```

Satu Kitchen dapat memiliki:

* gudang bahan kering;
* cold storage;
* gudang kemasan;
* staging produksi;
* staging distribusi.

## 12.4 Source of Truth

`stock_balance` hanya boleh diubah oleh domain Inventory melalui pencatatan `stock_movement`.

Tidak diperbolehkan mengubah kuantitas saldo secara langsung.

---

# 13. Production Context

## 13.1 Tanggung Jawab

Mengelola:

* production order;
* production batch;
* material issue;
* material consumption;
* hasil produksi;
* porsi aktual;
* waste;
* status proses;
* produksi ulang;
* variance plan vs actual.

## 13.2 Aggregate Utama

```text
ProductionOrder
ProductionOrderLine
ProductionBatch
MaterialIssue
MaterialConsumption
ProductionOutput
ProductionWaste
ProductionVariance
```

## 13.3 Hubungan Utama

```text
MealPlanItem
    ↓
ProductionOrder
    ↓
ProductionBatch
    ├── MaterialConsumption
    ├── ProductionOutput
    └── ProductionWaste
```

## 13.4 Event Utama

```text
ProductionOrderCreated
ProductionStarted
MaterialsConsumed
ProductionCompleted
ProductionWasteRecorded
ProductionCancelled
```

`MaterialsConsumed` diproses oleh Inventory.

`ProductionCompleted` diproses oleh:

* Inventory;
* Costing;
* Quality Control;
* Reporting;
* Notification.

---

# 14. Quality Control Context

## 14.1 Tanggung Jawab

Mengelola QC pada:

* bahan masuk;
* penyimpanan;
* proses produksi;
* produk jadi;
* pengemasan;
* distribusi.

## 14.2 Aggregate Utama

```text
QCPlan
QCInspection
QCInspectionLine
QCParameter
QCResult
NonConformity
CorrectiveAction
```

## 14.3 Integrasi Produksi

Production Batch tidak dapat masuk status siap distribusi apabila QC wajib belum selesai atau hasilnya tidak memenuhi syarat.

---

# 15. Distribution Context

## 15.1 Tanggung Jawab

Mengelola:

* sekolah atau titik penerima;
* beneficiary group;
* delivery plan;
* route;
* manifest;
* delivery;
* proof of delivery;
* jumlah diterima;
* retur;
* selisih distribusi.

## 15.2 Aggregate Utama

```text
DeliveryPoint
BeneficiaryGroup
DeliveryPlan
DeliveryRoute
DeliveryManifest
Delivery
DeliveryItem
ProofOfDelivery
DeliveryReturn
```

## 15.3 Hubungan GIS

Setiap Delivery Point memiliki koordinat.

```text
Kitchen
   ↓
Delivery Route
   ↓
Delivery Point
```

Domain Distribution menggunakan layanan GIS untuk:

* menghitung jarak;
* mengurutkan titik;
* menilai cakupan layanan;
* mendeteksi titik di luar radius.

---

# 16. Fleet Context

## 16.1 Tanggung Jawab

Mengelola:

* kendaraan;
* jenis kendaraan;
* pengemudi;
* penugasan;
* kapasitas;
* jadwal;
* bahan bakar;
* maintenance;
* biaya perjalanan.

## 16.2 Aggregate Utama

```text
Vehicle
VehicleType
Driver
VehicleAssignment
Trip
FuelUsage
VehicleMaintenance
```

Fleet menyediakan informasi kendaraan kepada Distribution, tetapi Delivery tetap dimiliki domain Distribution.

---

# 17. Budget Control Context

## 17.1 Tanggung Jawab

Mengelola anggaran secara ketat melalui tahap:

```text
Budget Allocation
Budget Reservation
Budget Commitment
Budget Actual
Budget Release
Budget Adjustment
```

## 17.2 Aggregate Utama

```text
Budget
BudgetVersion
BudgetLine
BudgetAllocation
BudgetReservation
BudgetCommitment
BudgetActual
BudgetTransfer
BudgetAdjustment
BudgetPeriod
```

## 17.3 Dimensi Budget

Budget dapat menggunakan dimensi:

```text
tenant_id
program_id
regional_id
kitchen_id
account_id
cost_category_id
funding_source_id
period_id
```

Tidak semua dimensi wajib terisi.

Contoh:

* Budget Tenant: hanya `tenant_id`;
* Budget Program: `program_id`;
* Budget Kitchen: `tenant_id`, `program_id`, dan `kitchen_id`;
* Budget bahan baku: ditambah `account_id` atau `cost_category_id`.

## 17.4 Tahapan Kontrol

```text
Available Budget
    = Allocation
    + Adjustment In
    - Adjustment Out
    - Reservation
    - Commitment
    - Actual
```

Definisi final formula harus mencegah nilai terhitung ganda ketika Reservation dikonversi menjadi Commitment dan Commitment dikonversi menjadi Actual.

Pola status yang disarankan:

```text
Reservation:
ACTIVE → CONVERTED → RELEASED

Commitment:
ACTIVE → REALIZED → CANCELLED
```

---

# 18. Accounting Context

## 18.1 Tanggung Jawab

Mengelola:

* Chart of Accounts;
* fiscal period;
* journal;
* journal entry;
* journal line;
* general ledger;
* payable;
* receivable klaim;
* closing;
* financial statement.

## 18.2 Aggregate Utama

```text
Account
AccountGroup
Journal
FiscalPeriod
JournalEntry
JournalEntryLine
LedgerPosting
AccountingRule
```

## 18.3 Dimensi Accounting

Setiap journal line dapat membawa dimensi:

```text
tenant_id
program_id
regional_id
kitchen_id
funding_source_id
cost_center_id
```

Dimensi sebaiknya berada pada `journal_entry_line`, karena satu jurnal dapat memiliki line dengan dimensi berbeda.

## 18.4 Source Document

Setiap jurnal otomatis wajib memiliki:

```text
source_module
source_document_type
source_document_id
source_event_id
```

Contoh:

```text
source_module        = procurement
source_document_type = purchase_receipt
source_document_id   = UUID
```

Hal ini memastikan jurnal dapat ditelusuri kembali ke transaksi asal.

---

# 19. Costing Context

## 19.1 Tanggung Jawab

Menghitung:

* planned cost;
* actual material cost;
* labor cost;
* utility cost;
* fuel cost;
* packaging cost;
* distribution cost;
* overhead;
* waste cost;
* cost per portion.

## 19.2 Aggregate Utama

```text
CostPolicy
CostPool
CostAllocationRule
ProductionCost
MealCost
CostPerPortion
CostVariance
```

## 19.3 Formula Dasar

```text
Total Actual Cost =
    Material Cost
  + Direct Labor
  + Utility Cost
  + Packaging
  + Distribution
  + Allocated Overhead
  + Waste Cost
```

```text
Cost per Portion =
    Total Actual Cost
    ÷
    Accepted Production Portions
```

Jumlah porsi untuk pembagi harus menggunakan porsi hasil produksi yang lolos QC, bukan semata-mata target meal plan.

---

# 20. Government Claim Context

## 20.1 Tanggung Jawab

Mengelola proses penagihan kepada pemerintah berdasarkan:

* pembelian bahan;
* biaya tenaga kerja;
* utilitas;
* jumlah porsi;
* dokumen pendukung;
* periode pertanggungjawaban;
* hasil verifikasi.

## 20.2 Aggregate Utama

```text
GovernmentClaim
GovernmentClaimLine
ClaimEvidence
ClaimVerification
ClaimAdjustment
ClaimPayment
```

## 20.3 Alur

```text
Actual Cost
    ↓
Claim Preparation
    ↓
Evidence Validation
    ↓
Submission
    ↓
Government Verification
    ↓
Approved / Adjusted / Rejected
    ↓
Payment
```

Government Claim tidak boleh menghitung biaya langsung dari Purchase Order. Klaim harus menggunakan biaya yang telah direalisasikan atau kebijakan khusus yang didefinisikan.

---

# 21. Investor & Funding Context

## 21.1 Tanggung Jawab

Mengelola:

* investor;
* perjanjian pendanaan;
* modal awal;
* pencairan;
* penggunaan dana;
* pengembalian modal;
* distribusi keuntungan.

## 21.2 Aggregate Utama

```text
Investor
FundingAgreement
CapitalContribution
FundDisbursement
CapitalReturn
ProfitDistribution
```

Investor bukan pengganti Account atau Journal. Semua pergerakan dana tetap dicatat melalui Accounting.

Domain ini mengelola kontrak dan posisi pendanaan, sedangkan Accounting menjadi sumber pencatatan keuangan.

---

# 22. Workforce Context

## 22.1 Tanggung Jawab

Mengelola:

* employee;
* posisi;
* penempatan Kitchen;
* shift;
* attendance;
* tenaga harian;
* biaya tenaga kerja.

## 22.2 Aggregate Utama

```text
Employee
Position
EmployeeAssignment
WorkShift
Attendance
Timesheet
LaborCost
```

Employee dapat berada pada Tenant dan ditempatkan pada satu atau beberapa Kitchen berdasarkan periode.

---

# 23. Workflow Context

## 23.1 Tujuan

Workflow Engine mengelola alur persetujuan generik untuk berbagai dokumen.

## 23.2 Aggregate Utama

```text
WorkflowDefinition
WorkflowVersion
WorkflowState
WorkflowTransition
WorkflowAction
WorkflowInstance
WorkflowHistory
ApprovalRequest
ApprovalDecision
```

## 23.3 Prinsip

Workflow Engine mengelola:

* transisi;
* approval;
* permission;
* history;
* SLA;
* notifikasi.

Namun domain tetap memiliki status bisnis ringkas pada aggregate-nya untuk menjaga integritas dan performa query.

Contoh:

```text
purchase_order.status = APPROVED
```

Workflow Engine tidak menggantikan seluruh state domain. Ia mengendalikan bagaimana state tersebut dapat berubah.

## 23.4 Alasan

Menyimpan semua status hanya di Workflow Engine akan menyebabkan:

* query bisnis menjadi kompleks;
* integritas aggregate sulit dijaga;
* reporting bergantung pada join generik;
* domain kehilangan invariannya.

Karena itu digunakan pendekatan hibrida:

```text
Domain Status
+
Workflow Instance
+
Workflow History
```

---

# 24. Notification Context

## 24.1 Tanggung Jawab

Mengelola:

* template;
* channel;
* recipient;
* queue;
* delivery;
* retry;
* failure log;
* read status.

## 24.2 Aggregate Utama

```text
NotificationTemplate
Notification
NotificationRecipient
NotificationDelivery
NotificationPreference
```

Channel:

```text
IN_APP
EMAIL
WHATSAPP
SMS
PUSH
TELEGRAM
```

Domain lain hanya menerbitkan permintaan notifikasi, bukan mengirim pesan secara langsung.

---

# 25. Audit & Compliance Context

## 25.1 Tanggung Jawab

Mengelola audit untuk:

* login;
* perubahan master;
* perubahan anggaran;
* koreksi stok;
* approval;
* posting jurnal;
* penghapusan;
* ekspor data;
* perubahan permission.

## 25.2 Aggregate Utama

```text
AuditEvent
AuditChange
SecurityEvent
AccessLog
DataExportLog
```

Audit log harus bersifat append-only.

Data audit penting tidak boleh ikut terhapus ketika transaksi menggunakan soft delete.

---

# 26. Document Management Context

## 26.1 Tanggung Jawab

Mengelola:

* attachment;
* document type;
* version;
* checksum;
* metadata;
* source entity;
* retention;
* approval document.

## 26.2 Aggregate Utama

```text
Document
DocumentVersion
DocumentLink
DocumentType
DocumentRetentionPolicy
```

File fisik dapat disimpan di:

* local object storage;
* MinIO;
* S3-compatible storage.

Database hanya menyimpan metadata dan object key.

---

# 27. Reporting & Dashboard Context

## 27.1 Tanggung Jawab

Domain Reporting menyediakan read model untuk:

* dashboard nasional;
* dashboard program;
* dashboard Tenant;
* dashboard Kitchen;
* budget report;
* stock report;
* production report;
* distribution report;
* financial report;
* GIS dashboard.

## 27.2 Pendekatan

Reporting tidak menjadi source of truth transaksi.

Reporting membangun:

* materialized view;
* summary table;
* read model;
* cached aggregation.

## 27.3 Contoh Read Model

```text
daily_kitchen_operation_summary
monthly_budget_realization_summary
production_cost_summary
delivery_performance_summary
program_financial_summary
```

---

# 28. AI & Forecasting Context

## 28.1 Tanggung Jawab

Mengelola model dan hasil prediksi:

* forecast kebutuhan bahan;
* forecast jumlah porsi;
* forecast budget;
* risiko stockout;
* risiko waste;
* anomali biaya;
* rekomendasi procurement;
* optimasi distribusi.

## 28.2 Prinsip

AI tidak boleh langsung mengubah transaksi operasional.

Output AI disimpan sebagai rekomendasi:

```text
Forecast
Recommendation
Anomaly
ModelRun
ModelVersion
```

Perubahan transaksi tetap memerlukan service domain dan workflow yang berlaku.

---

# 29. Integration Context

## 29.1 Tanggung Jawab

Mengelola:

* API key;
* external system;
* webhook;
* inbound message;
* outbound message;
* mapping;
* retry;
* idempotency;
* synchronization log.

## 29.2 Aggregate Utama

```text
ExternalSystem
IntegrationCredential
InboundMessage
OutboundMessage
WebhookSubscription
DataMapping
SyncJob
SyncLog
```

Setiap integrasi wajib menggunakan `external_reference` dan idempotency key untuk mencegah transaksi ganda.

---

# 30. Context Map

Hubungan tingkat tinggi antardomain:

```text
Identity & Access
        │
        ├──────────────┐
        ▼              ▼
Organization      Workflow
        │              │
        ├──────┬───────┴─────────────┐
        ▼      ▼                     ▼
     Program  GIS              Audit/Notification
        │
        ├───────────────┐
        ▼               ▼
 Meal Planning     Budget Control
        │               │
        ▼               ▼
Recipe/Nutrition   Procurement
        │               │
        └──────┬────────┘
               ▼
           Inventory
               │
               ▼
           Production
          ┌────┼─────┐
          ▼    ▼     ▼
         QC  Costing Distribution
                    │
                    ▼
                   Fleet

Procurement ───────────────► Accounting
Inventory ─────────────────► Accounting
Production/Costing ────────► Accounting
Government Claim ──────────► Accounting
Investor & Funding ────────► Accounting

Semua domain ──────────────► Reporting
Semua domain ──────────────► Audit
Semua domain ──────────────► Notification
```

---

# 31. Event Catalog Utama

## Organization

```text
TenantCreated
KitchenCreated
KitchenLocationUpdated
KitchenActivated
KitchenDeactivated
```

## Program

```text
ProgramCreated
TenantAssignedToProgram
KitchenAssignedToProgram
ProgramPeriodOpened
ProgramPeriodClosed
```

## Meal Planning

```text
MealPlanCreated
MealPlanSubmitted
MealPlanApproved
MaterialRequirementGenerated
```

## Procurement

```text
PurchaseRequested
BudgetReservationRequested
PurchaseOrderApproved
GoodsReceived
PurchaseCancelled
```

## Inventory

```text
StockReceived
StockReserved
StockIssued
StockTransferred
StockAdjusted
StockBelowMinimum
StockExpired
```

## Production

```text
ProductionOrderCreated
ProductionStarted
MaterialsConsumed
ProductionCompleted
ProductionWasteRecorded
```

## Quality

```text
QCInspectionCompleted
QCRejected
CorrectiveActionRequired
BatchReleased
```

## Distribution

```text
DeliveryPlanned
DeliveryDispatched
DeliveryCompleted
DeliveryFailed
ProofOfDeliveryRecorded
```

## Budget

```text
BudgetAllocated
BudgetReserved
BudgetCommitted
BudgetActualized
BudgetReleased
BudgetExceeded
```

## Accounting

```text
JournalEntryCreated
JournalEntryPosted
JournalEntryReversed
FiscalPeriodClosed
```

## Government Claim

```text
ClaimPrepared
ClaimSubmitted
ClaimApproved
ClaimAdjusted
ClaimPaid
```

---

# 32. Standar Scope Data

Tidak semua tabel harus memiliki seluruh kolom scope secara fisik.

Standar yang lebih tepat adalah:

## 32.1 Tabel Tenant-Owned

Wajib memiliki:

```text
tenant_id
```

Contoh:

* Kitchen;
* Warehouse;
* Employee;
* Supplier khusus Tenant.

## 32.2 Tabel Kitchen-Owned

Wajib memiliki:

```text
tenant_id
kitchen_id
```

Contoh:

* Stock Movement;
* Production Batch;
* Delivery;
* Kitchen Budget.

## 32.3 Tabel Program-Owned

Wajib memiliki:

```text
program_id
```

Dapat ditambah:

```text
tenant_id
kitchen_id
```

sesuai konteks.

## 32.4 Global Master

Tidak memerlukan `tenant_id` apabila benar-benar global.

Contoh:

* Province;
* City;
* standard nutrition unit;
* global UoM.

## 32.5 Tenant-Specific Master

Memiliki:

```text
tenant_id
```

Contoh:

* product;
* supplier;
* account;
* budget category.

Dengan demikian, penggunaan kolom:

```text
tenant_id
program_id
regional_id
kitchen_id
```

tidak dipaksakan pada semua tabel. Kolom hanya digunakan berdasarkan ownership dan kebutuhan query.

---

# 33. Standar Base Model

## 33.1 Base Entity

```text
id UUID
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
created_by UUID NULL
updated_by UUID NULL
version INTEGER
```

## 33.2 Soft Delete Entity

Hanya digunakan pada entitas yang memang boleh dinonaktifkan atau dihapus secara logis.

```text
deleted_at TIMESTAMPTZ NULL
deleted_by UUID NULL
```

Tidak semua tabel harus menggunakan soft delete.

Tabel berikut sebaiknya tidak menggunakan soft delete biasa:

* journal entry yang sudah diposting;
* stock movement;
* audit event;
* budget actual;
* approval history.

Koreksi dilakukan melalui reversal atau adjustment.

---

# 34. Struktur Modul FastAPI

```text
app/
├── core/
│   ├── config.py
│   ├── database.py
│   ├── security.py
│   ├── logging.py
│   ├── cache.py
│   └── lifespan.py
│
├── shared/
│   ├── database/
│   ├── events/
│   ├── responses/
│   ├── pagination/
│   ├── exceptions/
│   ├── audit/
│   ├── storage/
│   └── utilities/
│
└── modules/
    ├── identity/
    ├── organization/
    ├── program/
    ├── gis/
    ├── product/
    ├── recipe/
    ├── meal_planning/
    ├── procurement/
    ├── inventory/
    ├── production/
    ├── quality/
    ├── distribution/
    ├── fleet/
    ├── budget/
    ├── accounting/
    ├── costing/
    ├── government_claim/
    ├── funding/
    ├── workforce/
    ├── workflow/
    ├── notification/
    ├── audit/
    ├── documents/
    ├── reporting/
    ├── ai/
    └── integration/
```

Struktur internal domain:

```text
organization/
├── models/
├── schemas/
├── repositories/
├── services/
├── routes/
├── commands/
├── queries/
├── events/
├── handlers/
├── permissions/
├── validators/
├── exceptions/
├── constants/
└── dependencies/
```

---

# 35. Aturan Dependensi Modul

## Diperbolehkan

```text
routes
  ↓
services
  ↓
repositories
  ↓
models
```

```text
services
  ↓
domain interface
  ↓
event bus
```

## Tidak Diperbolehkan

```text
routes → models langsung
service A → repository domain B
model A → service domain B
repository → route
```

## Shared Layer

Shared layer tidak boleh bergantung pada domain bisnis.

```text
Domain → Shared
```

bukan:

```text
Shared → Domain
```

---

# 36. Transaction Boundary

Satu command harus memiliki transaction boundary yang jelas.

Contoh:

```text
Complete Production Batch
```

Transaksi utama Production meliputi:

* validasi batch;
* pencatatan hasil;
* perubahan status;
* penyimpanan event outbox.

Pemrosesan Inventory, Costing, Notification, dan Reporting dilakukan melalui event setelah transaksi Production berhasil.

Untuk keandalan, event disimpan menggunakan **Transactional Outbox Pattern**.

```text
Business Transaction
        +
Outbox Event
        ↓
Commit
        ↓
Event Dispatcher
```

---

# 37. Kesimpulan Arsitektur

Enterprise Domain Model ini menetapkan bahwa:

1. Tenant adalah organisasi pengelola.
2. Satu Tenant dapat memiliki banyak Kitchen/SPPG.
3. Setiap Kitchen mempunyai lokasi GPS dan dapat ditampilkan melalui GIS.
4. Program memiliki hubungan banyak-ke-banyak dengan Tenant dan Kitchen.
5. Kitchen tetap menjadi pusat transaksi operasional.
6. Setiap bounded context mempunyai source of truth sendiri.
7. Accounting dan Budget Control dipisahkan tetapi terintegrasi.
8. Workflow Engine mengendalikan transisi, tetapi tidak menggantikan status bisnis domain.
9. Reporting menggunakan read model dan bukan sumber transaksi.
10. Event antardomain menggunakan transactional outbox.
11. Kolom scope tidak dipaksakan pada seluruh tabel.
12. FastAPI dibangun sebagai modular monolith yang siap dipisahkan secara bertahap.

Dokumen ini menjadi dasar penyusunan **ERD Final ERP MBG v3.0**.
