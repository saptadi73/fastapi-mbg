# Frontend Screen Matrix

Dokumen ini memetakan layar frontend ERP MBG berdasarkan modul, tujuan, role utama, dan dependensi API.

Dokumen ini melengkapi:

- [frontend_functional_reference.md](C:/projek/fastapi-mbg/docs/frontend_functional_reference.md)
- [frontend_api_reference.md](C:/projek/fastapi-mbg/docs/frontend_api_reference.md)

## 1. Cara Membaca

Kolom:

- `Module`: bounded context atau area produk
- `Screen`: nama layar
- `Type`: `list`, `detail`, `form`, `dashboard`, `tool`, `map`, `drawer`, atau `modal`
- `Primary Users`: role utama yang paling sering memakai layar
- `Main Purpose`: kegunaan utama layar
- `Key API`: endpoint inti yang biasa dipakai layar tersebut

## 2. Global Screens

| Module | Screen | Type | Primary Users | Main Purpose | Key API |
|---|---|---|---|---|---|
| Global | Login | form | Semua user | Masuk ke aplikasi dan ambil token | `POST /api/v1/identity/login` |
| Global | App Shell | layout | Semua user | Navigasi global, header, context bar, inbox | `GET /api/v1/identity/me`, `GET /api/v1/notifications/inbox` |
| Global | Context Switcher | drawer | Semua user multi-SPPG | Ganti SPPG aktif | `POST /api/v1/identity/switch-active-sppg` |
| Global | Notification Inbox | list | Semua user | Lihat dan tandai notifikasi | `GET /api/v1/notifications/inbox`, `POST /api/v1/notifications/inbox/{recipient_id}/mark-read` |
| Global | My Profile | detail | Semua user | Lihat identitas dan akses aktif | `GET /api/v1/identity/me` |

## 3. Dashboard Screens

| Module | Screen | Type | Primary Users | Main Purpose | Key API |
|---|---|---|---|---|---|
| Dashboard | Tenant Dashboard | dashboard | `tenant_admin`, `super_admin` | Ringkasan lintas SPPG dan modul | `GET /api/v1/reporting/dashboard/tenant` |
| Dashboard | SPPG Dashboard | dashboard | `operations_manager` | Ringkasan operasional per SPPG | `GET /api/v1/reporting/dashboard/sppg` |
| Dashboard | Finance Dashboard | dashboard | `finance_manager`, `tenant_admin` | Ringkasan finance dan funding | `GET /api/v1/reporting/dashboard/finance` |

## 4. Identity & Access Screens

| Module | Screen | Type | Primary Users | Main Purpose | Key API |
|---|---|---|---|---|---|
| Identity | User List | list | `super_admin`, `tenant_admin` | Lihat semua user dalam tenant | `GET /api/v1/identity/users` |
| Identity | User Detail | detail | `super_admin`, `tenant_admin` | Lihat profil, role, dan scope user | `GET /api/v1/identity/users/{user_id}` |
| Identity | Create User | form | `super_admin`, `tenant_admin` | Buat user baru | `POST /api/v1/identity/users` |
| Identity | Edit User | form | `super_admin`, `tenant_admin` | Ubah user, role, dan status | `PUT /api/v1/identity/users/{user_id}` |
| Identity | User SPPG Access | detail | `super_admin`, `tenant_admin` | Kelola daftar SPPG yang bisa diakses user | `GET /api/v1/identity/users/{user_id}/sppg-access`, `PUT /api/v1/identity/users/{user_id}/sppg-access` |

## 5. Master Data Screens

| Module | Screen | Type | Primary Users | Main Purpose | Key API |
|---|---|---|---|---|---|
| Tenant | Tenant List | list | `super_admin` | Lihat tenant | `GET /api/v1/tenants/` |
| Tenant | Tenant Detail | detail | `super_admin` | Lihat detail tenant | `GET /api/v1/tenants/{tenant_id}` |
| Tenant | Create Tenant | form | `super_admin` | Buat tenant | `POST /api/v1/tenants/` |
| SPPG | SPPG List | list | `super_admin`, `tenant_admin` | Lihat daftar SPPG | `GET /api/v1/sppg/` |
| SPPG | SPPG Detail | detail | `super_admin`, `tenant_admin` | Lihat profil dan lokasi SPPG | `GET /api/v1/sppg/{sppg_id}` |
| SPPG | Create SPPG | form | `super_admin`, `tenant_admin` | Buat SPPG baru | `POST /api/v1/sppg/` |
| Geography | School List | list | `operations_manager` | Lihat sekolah | `GET /api/v1/geography/schools/` |
| Geography | School Detail | detail | `operations_manager` | Lihat detail sekolah | `GET /api/v1/geography/schools/{school_id}` |
| Geography | Create School | form | `tenant_admin`, `operations_manager` | Tambah sekolah | `POST /api/v1/geography/schools/` |
| Beneficiary | Beneficiary List | list | `operations_manager` | Lihat penerima manfaat | `GET /api/v1/beneficiaries/` |
| Beneficiary | Beneficiary Detail | detail | `operations_manager` | Detail penerima | `GET /api/v1/beneficiaries/{beneficiary_id}` |
| Beneficiary | Create Beneficiary | form | `tenant_admin`, `operations_manager` | Tambah penerima manfaat | `POST /api/v1/beneficiaries/` |
| UoM | UoM List | list | `tenant_admin` | Lihat UoM | `GET /api/v1/uoms/` |
| Product | Product List | list | `tenant_admin`, `operations_manager`, `procurement_officer` | Lihat master produk | `GET /api/v1/products/` |
| Product | Product Detail | detail | `tenant_admin`, `operations_manager`, `procurement_officer` | Lihat detail produk | `GET /api/v1/products/{product_id}` |
| Product | Create Product | form | `tenant_admin` | Tambah produk | `POST /api/v1/products/` |
| Recipe | Recipe List | list | `tenant_admin`, `operations_manager` | Lihat resep | `GET /api/v1/recipes/` |
| Recipe | Recipe Detail | detail | `tenant_admin`, `operations_manager` | Lihat header resep dan line | `GET /api/v1/recipes/{recipe_id}`, `GET /api/v1/recipes/{recipe_id}/lines` |
| Recipe | Create Recipe | form | `tenant_admin`, `operations_manager` | Buat resep | `POST /api/v1/recipes/` |
| Recipe | Add Recipe Lines | form | `tenant_admin`, `operations_manager` | Tambah komponen resep | `POST /api/v1/recipes/{recipe_id}/lines` |

## 6. Program & Workforce Screens

| Module | Screen | Type | Primary Users | Main Purpose | Key API |
|---|---|---|---|---|---|
| Program | Program List | list | `tenant_admin`, `super_admin` | Lihat program | `GET /api/v1/programs/` |
| Program | Program Detail | detail | `tenant_admin`, `super_admin` | Detail program, tenant, SPPG, period | `GET /api/v1/programs/{program_id}` |
| Program | Create Program | form | `tenant_admin`, `super_admin` | Buat program | `POST /api/v1/programs/` |
| Program | Add Period | modal | `tenant_admin`, `super_admin` | Tambah periode program | `POST /api/v1/programs/{program_id}/periods` |
| Program | Assign Tenant | modal | `tenant_admin`, `super_admin` | Assign tenant ke program | `POST /api/v1/programs/{program_id}/tenants` |
| Program | Assign SPPG | modal | `tenant_admin`, `super_admin` | Assign SPPG ke program | `POST /api/v1/programs/{program_id}/sppg` |
| Workforce | Position List | list | `tenant_admin`, `operations_manager` | Lihat posisi | `GET /api/v1/workforce/positions` |
| Workforce | Employee List | list | `tenant_admin`, `operations_manager` | Lihat employee | `GET /api/v1/workforce/employees` |
| Workforce | Employee Detail | detail | `tenant_admin`, `operations_manager` | Detail employee dan assignment | `GET /api/v1/workforce/employees/{employee_id}` |
| Workforce | Employee Form | form | `tenant_admin`, `operations_manager` | Tambah employee | `POST /api/v1/workforce/employees` |
| Workforce | Assignment Form | modal | `tenant_admin`, `operations_manager` | Assign employee ke SPPG | `POST /api/v1/workforce/employees/{employee_id}/assignments` |
| Workforce | Shift List | list | `tenant_admin`, `operations_manager` | Lihat shift | `GET /api/v1/workforce/shifts` |
| Workforce | Attendance List | list | `operations_manager` | Lihat attendance | `GET /api/v1/workforce/attendance` |
| Workforce | Timesheet List | list | `operations_manager`, `finance_manager` | Lihat timesheet | `GET /api/v1/workforce/timesheets` |
| Workforce | Labor Cost List | list | `operations_manager`, `finance_manager` | Lihat labor cost | `GET /api/v1/workforce/labor-costs` |

## 7. Meal Plan & Production Screens

| Module | Screen | Type | Primary Users | Main Purpose | Key API |
|---|---|---|---|---|---|
| Meal Plan | Meal Plan List | list | `operations_manager`, `tenant_admin` | Triage rencana menu | `GET /api/v1/meal-plans/` |
| Meal Plan | Meal Plan Detail | detail | `operations_manager`, `tenant_admin` | Lihat status, workflow, dan biaya | `GET /api/v1/meal-plans/{meal_plan_id}`, `GET /api/v1/workflows/documents/meal_plan/{meal_plan_id}` |
| Meal Plan | Create Meal Plan | form | `operations_manager`, `tenant_admin` | Buat rencana menu | `POST /api/v1/meal-plans/` |
| Meal Plan | Requirements Preview | tool | `operations_manager` | Hitung kebutuhan bahan | `POST /api/v1/meal-plans/{meal_plan_id}/calculate-requirements` |
| Meal Plan | Cost Preview | detail | `operations_manager`, `finance_manager` | Lihat estimasi biaya | `GET /api/v1/meal-plans/{meal_plan_id}/cost-preview` |
| Production | Production Order List | list | `operations_manager` | Lihat order produksi | `GET /api/v1/production-orders/` |
| Production | Production Order Detail | detail | `operations_manager` | Lihat summary dan material | `GET /api/v1/production-orders/{production_order_id}` |
| Production | Create from Meal Plan | action | `operations_manager` | Buat production order | `POST /api/v1/production-orders/from-meal-plan/{meal_plan_id}` |
| Production | Complete Production | modal | `operations_manager` | Tutup produksi dan posting biaya | `POST /api/v1/production-orders/{production_order_id}/complete` |
| Production | Cost Sheet | detail | `operations_manager`, `finance_manager` | Rincian biaya aktual | `GET /api/v1/production-orders/{production_order_id}/cost-sheet` |

## 8. Supply Chain Screens

| Module | Screen | Type | Primary Users | Main Purpose | Key API |
|---|---|---|---|---|---|
| Inventory | Warehouse List | list | `warehouse_operator`, `operations_manager` | Lihat gudang | `GET /api/v1/inventory/warehouses/` |
| Inventory | Warehouse Detail | detail | `warehouse_operator`, `operations_manager` | Detail warehouse | `GET /api/v1/inventory/warehouses/{warehouse_id}` |
| Inventory | Warehouse Form | form | `warehouse_operator`, `operations_manager` | Buat warehouse | `POST /api/v1/inventory/warehouses/` |
| Inventory | Stock Location List | list | `warehouse_operator`, `operations_manager` | Lihat lokasi stok | `GET /api/v1/inventory/locations/` |
| Inventory | Stock Location Form | form | `warehouse_operator`, `operations_manager` | Buat stock location | `POST /api/v1/inventory/locations/` |
| Inventory | Batch List | list | `warehouse_operator`, `procurement_officer` | Lihat lot/batch | `GET /api/v1/inventory/batches/` |
| Inventory | Batch Form | form | `warehouse_operator`, `procurement_officer` | Buat batch | `POST /api/v1/inventory/batches/` |
| Inventory | Transaction List | list | `warehouse_operator`, `operations_manager` | Ledger inventory | `GET /api/v1/inventory/transactions/` |
| Inventory | Transaction Form | form | `warehouse_operator`, `operations_manager` | Post transaksi inventory | `POST /api/v1/inventory/transactions/` |
| Inventory | Balance List | list | `warehouse_operator`, `operations_manager` | Lihat saldo stok | `GET /api/v1/inventory/balances/` |
| Inventory | Expiry Alert | list | `warehouse_operator`, `quality_officer` | Pantau batch near expiry | `GET /api/v1/inventory/expiry-alerts` |
| Inventory | FEFO Preview | tool | `warehouse_operator`, `operations_manager` | Simulasi pengambilan batch | `POST /api/v1/inventory/issues/fefo-preview` |
| Procurement | Supplier List | list | `procurement_officer`, `tenant_admin` | Lihat supplier | `GET /api/v1/procurement/purchase-requests/suppliers` |
| Procurement | Supplier Detail | detail | `procurement_officer`, `tenant_admin` | Detail supplier dan relasi | `GET /api/v1/procurement/purchase-requests/suppliers/{supplier_id}` |
| Procurement | Supplier Form | form | `procurement_officer`, `tenant_admin` | Tambah supplier | `POST /api/v1/procurement/purchase-requests/suppliers` |
| Procurement | Supplier Product List | list | `procurement_officer` | Lihat mapping supplier-produk | `GET /api/v1/procurement/purchase-requests/supplier-products` |
| Procurement | Supplier Product Form | form | `procurement_officer` | Tambah mapping supplier-produk | `POST /api/v1/procurement/purchase-requests/supplier-products` |
| Procurement | Supplier Price History List | list | `procurement_officer` | Histori harga supplier | `GET /api/v1/procurement/purchase-requests/supplier-price-histories` |
| Procurement | Supplier Price History Form | form | `procurement_officer` | Tambah histori harga | `POST /api/v1/procurement/purchase-requests/supplier-price-histories` |
| Procurement | Purchase Request List | list | `procurement_officer`, `operations_manager` | Triage kebutuhan pembelian | `GET /api/v1/procurement/purchase-requests/` |
| Procurement | Purchase Request Detail | detail | `procurement_officer`, `operations_manager` | Detail PR dan lines | `GET /api/v1/procurement/purchase-requests/{purchase_request_id}` |
| Procurement | Purchase Order List | list | `procurement_officer`, `operations_manager` | Lihat PO/RFQ | `GET /api/v1/procurement/purchase-requests/purchase-orders/` |
| Procurement | Purchase Order Detail | detail | `procurement_officer`, `operations_manager` | Detail PO dan line | `GET /api/v1/procurement/purchase-requests/purchase-orders/{purchase_order_id}` |
| Procurement | Goods Receipt List | list | `procurement_officer`, `warehouse_operator` | Lihat GR | `GET /api/v1/procurement/purchase-requests/goods-receipts/` |
| Procurement | Goods Receipt Detail | detail | `procurement_officer`, `warehouse_operator` | Detail GR | `GET /api/v1/procurement/purchase-requests/goods-receipts/{goods_receipt_id}` |
| Procurement | Supplier Invoice List | list | `finance_manager`, `procurement_officer` | Lihat invoice supplier | `GET /api/v1/procurement/purchase-requests/supplier-invoices/` |
| Procurement | Supplier Invoice Detail | detail | `finance_manager`, `procurement_officer` | Detail invoice | `GET /api/v1/procurement/purchase-requests/supplier-invoices/{supplier_invoice_id}` |
| Procurement | Supplier Payment List | list | `finance_manager` | Lihat pembayaran supplier | `GET /api/v1/procurement/purchase-requests/supplier-payments/` |
| Procurement | Supplier Payment Detail | detail | `finance_manager` | Detail pembayaran | `GET /api/v1/procurement/purchase-requests/supplier-payments/{supplier_payment_id}` |

## 9. Quality, Delivery, Fleet, Asset Screens

| Module | Screen | Type | Primary Users | Main Purpose | Key API |
|---|---|---|---|---|---|
| Quality | QC Inspection List | list | `quality_officer`, `operations_manager` | Lihat inspeksi | `GET /api/v1/quality/inspections/` |
| Quality | QC Inspection Detail | detail | `quality_officer`, `operations_manager` | Detail inspeksi dan line | `GET /api/v1/quality/inspections/{inspection_id}` |
| Quality | QC Inspection Form | form | `quality_officer`, `operations_manager` | Buat inspeksi | `POST /api/v1/quality/inspections/` |
| Delivery | Delivery Order List | list | `delivery_officer`, `operations_manager` | Lihat delivery order | `GET /api/v1/delivery-orders/` |
| Delivery | Delivery Order Detail | detail | `delivery_officer`, `operations_manager`, `quality_officer` | Detail order, route, proof, incident | `GET /api/v1/delivery-orders/{delivery_order_id}` |
| Delivery | Route List | list | `delivery_officer`, `operations_manager` | Lihat route planning | `GET /api/v1/delivery-orders/routes` |
| Delivery | Route Detail | detail | `delivery_officer`, `operations_manager` | Detail route, stop, incident | `GET /api/v1/delivery-orders/routes/{route_id}` |
| Delivery | Route Create | form | `delivery_officer`, `operations_manager` | Buat route | `POST /api/v1/delivery-orders/routes` |
| Delivery | Delivery Proof | form | `delivery_officer` | Rekam proof of delivery | `POST /api/v1/delivery-orders/{delivery_order_id}/proof` |
| Delivery | Delivery Incident | form | `delivery_officer`, `quality_officer` | Catat incident delivery | `POST /api/v1/delivery-orders/{delivery_order_id}/incidents` |
| Fleet | Vehicle Type List | list | `operations_manager`, `tenant_admin` | Lihat tipe kendaraan | `GET /api/v1/fleet/vehicle-types` |
| Fleet | Vehicle List | list | `operations_manager` | Lihat kendaraan | `GET /api/v1/fleet/vehicles` |
| Fleet | Vehicle Detail | detail | `operations_manager` | Detail kendaraan | `GET /api/v1/fleet/vehicles/{vehicle_id}` |
| Fleet | Driver List | list | `operations_manager` | Lihat driver | `GET /api/v1/fleet/drivers` |
| Asset | Asset Category List | list | `finance_manager`, `operations_manager` | Lihat kategori asset | `GET /api/v1/assets/categories` |
| Asset | Asset List | list | `finance_manager`, `operations_manager` | Lihat asset | `GET /api/v1/assets/` |
| Asset | Asset Detail | detail | `finance_manager`, `operations_manager` | Detail asset, assignment, depresiasi | `GET /api/v1/assets/{asset_id}` |

## 10. Finance Screens

| Module | Screen | Type | Primary Users | Main Purpose | Key API |
|---|---|---|---|---|---|
| Budget | Budget List | list | `finance_manager`, `tenant_admin` | Lihat budget | `GET /api/v1/budgets` |
| Budget | Budget Detail | detail | `finance_manager`, `tenant_admin` | Detail budget dan line | `GET /api/v1/budgets/{budget_id}` |
| Budget | Budget Form | form | `finance_manager`, `tenant_admin` | Buat budget | `POST /api/v1/budgets` |
| Budget | Budget Availability | detail | `finance_manager`, `tenant_admin` | Lihat available/reserved/committed/actual | `GET /api/v1/budgets/{budget_id}/availability` |
| Accounting | Account List | list | `finance_manager`, `tenant_admin` | Chart of accounts | `GET /api/v1/accounts` |
| Accounting | Account Form | form | `finance_manager`, `tenant_admin` | Buat account | `POST /api/v1/accounts` |
| Accounting | Journal Entry List | list | `finance_manager`, `tenant_admin` | Lihat jurnal | `GET /api/v1/journal-entries` |
| Accounting | Journal Entry Detail | detail | `finance_manager`, `tenant_admin` | Lihat header dan lines | `GET /api/v1/journal-entries/{journal_entry_id}` |
| Accounting | Journal Entry Form | form | `finance_manager`, `tenant_admin` | Buat jurnal manual | `POST /api/v1/journal-entries` |
| Funding | Funding Source List | list | `finance_manager`, `tenant_admin` | Lihat sumber dana | `GET /api/v1/funding/sources` |
| Funding | Funding Agreement List | list | `finance_manager`, `tenant_admin` | Lihat agreement | `GET /api/v1/funding/agreements` |
| Funding | Funding Agreement Detail | detail | `finance_manager`, `tenant_admin` | Detail agreement, disbursement, repayment | `GET /api/v1/funding/agreements/{agreement_id}` |
| Government Claim | Claim List | list | `finance_manager`, `tenant_admin` | Lihat claim | `GET /api/v1/government-claims` |
| Government Claim | Claim Detail | detail | `finance_manager`, `tenant_admin` | Detail claim, adjustment, payment | `GET /api/v1/government-claims/{claim_id}` |

## 11. Governance, Integration, and AI Screens

| Module | Screen | Type | Primary Users | Main Purpose | Key API |
|---|---|---|---|---|---|
| Workflow | Workflow Definition List | list | `tenant_admin`, `super_admin` | Lihat workflow definition | `GET /api/v1/workflows/definitions` |
| Workflow | Workflow Definition Detail | detail | `tenant_admin`, `super_admin` | Lihat version, state, action, transition | `GET /api/v1/workflows/definitions/{definition_id}` |
| Workflow | Workflow Document Viewer | detail | `tenant_admin`, `operations_manager`, `finance_manager` | Lihat workflow instance dokumen | `GET /api/v1/workflows/documents/{document_type}/{document_id}` |
| Workflow | Approval Queue | list | `tenant_admin`, `super_admin` | Lihat approval pending | `GET /api/v1/workflows/documents/{document_type}/{document_id}` |
| Documents | Document List | list | `tenant_admin`, `operations_manager`, `finance_manager` | Lihat metadata dokumen | `GET /api/v1/documents` |
| Documents | Document Detail | detail | `tenant_admin`, `operations_manager`, `finance_manager` | Lihat versi dan relasi dokumen | `GET /api/v1/documents/{document_id}` |
| Audit | Audit Event List | list | `tenant_admin`, `super_admin` | Lihat audit event | `GET /api/v1/audit/events/` |
| Audit | Audit Event Detail | detail | `tenant_admin`, `super_admin` | Detail event audit | `GET /api/v1/audit/events/{event_id}` |
| Integration | External System List | list | `tenant_admin`, `super_admin` | Lihat sistem eksternal | `GET /api/v1/integration/external-systems` |
| Integration | External System Detail | detail | `tenant_admin`, `super_admin` | Lihat credential, mapping, webhook, sync jobs | `GET /api/v1/integration/external-systems/{external_system_id}` |
| Integration | Sync Job List | list | `tenant_admin`, `super_admin` | Lihat sync jobs | `GET /api/v1/integration/sync-jobs` |
| Integration | Sync Job Detail | detail | `tenant_admin`, `super_admin` | Detail sync job | `GET /api/v1/integration/sync-jobs/{sync_job_id}` |
| Integration | Inbound Message List | list | `tenant_admin`, `super_admin` | Lihat inbound messages | `GET /api/v1/integration/inbound-messages` |
| Integration | Outbound Message List | list | `tenant_admin`, `super_admin` | Lihat outbound messages | `GET /api/v1/integration/outbound-messages` |
| Integration | Sync Log List | list | `tenant_admin`, `super_admin` | Lihat sync log | `GET /api/v1/integration/sync-logs` |
| Integration | Sync Log Detail | detail | `tenant_admin`, `super_admin` | Detail sync log | `GET /api/v1/integration/sync-logs/{sync_log_id}` |
| Platform | Background Job List | list | `super_admin`, `tenant_admin` | Lihat background jobs | `GET /api/v1/platform/background-jobs` |
| Platform | Outbox Event List | list | `super_admin`, `tenant_admin` | Lihat outbox | `GET /api/v1/platform/outbox-events` |
| Platform | Read Model Monitor | list | `super_admin`, `tenant_admin` | Lihat read models/materialized view | `GET /api/v1/platform/read-models/daily-kitchen-operations`, `GET /api/v1/platform/materialized-views/delivery-performance` |
| AI | AI Overview | dashboard | `tenant_admin`, `operations_manager`, `finance_manager` | Ringkasan AI | `GET /api/v1/ai/overview` |
| AI | Forecast List | list | `operations_manager`, `finance_manager` | Lihat forecast | `GET /api/v1/ai/forecasts` |
| AI | Recommendation List | list | `operations_manager`, `finance_manager` | Lihat rekomendasi | `GET /api/v1/ai/recommendations` |
| AI | Daily Summary List | list | `operations_manager`, `finance_manager` | Lihat summary harian | `GET /api/v1/ai/daily-summaries` |
| AI | NL2SQL Workspace | tool | `finance_manager`, `tenant_admin`, `operations_manager` | Analisa data dengan bahasa natural | `POST /api/v1/ai/nl2sql/query` |
| AI | Image Analysis | tool | `quality_officer`, `operations_manager` | Analisa foto | `POST /api/v1/ai/media/analyze-image` |
| AI | Video Analysis | tool | `quality_officer`, `operations_manager` | Analisa video | `POST /api/v1/ai/media/analyze-video` |

## 12. GIS Screens

| Module | Screen | Type | Primary Users | Main Purpose | Key API |
|---|---|---|---|---|---|
| GIS | SPPG Map | map | `operations_manager`, `tenant_admin` | Lihat marker SPPG | `GET /api/v1/gis/sppg-map` |
| GIS | Kitchens Layer Map | map | `operations_manager` | Layer dapur dalam bbox | `GET /api/v1/gis/kitchens` |
| GIS | Schools Layer Map | map | `operations_manager` | Layer sekolah | `GET /api/v1/gis/schools` |
| GIS | Service Coverage Map | map | `operations_manager`, `tenant_admin` | Cakupan sekolah | `GET /api/v1/gis/service-coverage` |
| GIS | Unserved Schools Map | map | `operations_manager`, `tenant_admin` | Sekolah belum tercakup | `GET /api/v1/gis/unserved-schools` |
| GIS | Delivery Route Map | map | `delivery_officer`, `operations_manager` | Visualisasi rute delivery | `GET /api/v1/gis/delivery-routes`, `GET /api/v1/gis/deliveries/{delivery_id}/route` |
| GIS | Service Area List | list | `operations_manager`, `tenant_admin` | Lihat polygon layanan | `GET /api/v1/gis/service-areas` |
| GIS | Service Area Editor | map | `operations_manager`, `tenant_admin` | Buat/update polygon layanan | `POST /api/v1/gis/service-areas`, `PUT /api/v1/gis/kitchens/{kitchen_id}/service-area` |
| GIS | Nearest Kitchens Tool | tool | `operations_manager` | Cari dapur terdekat ke sekolah | `GET /api/v1/gis/schools/{school_id}/nearest-kitchens` |
| GIS | Assignment Validation Tool | tool | `operations_manager` | Validasi assignment spasial | `POST /api/v1/gis/assignments/validate` |

## 13. Priority Delivery Plan

Prioritas implementasi layar frontend yang disarankan:

1. login, app shell, context switcher
2. dashboard tenant dan SPPG
3. meal plan list/detail/form
4. inventory balance, warehouse, location
5. purchase request, supplier, goods receipt
6. production order
7. delivery order, route, proof, incident
8. budget, journal, funding
9. workflow viewer dan approval queue
10. GIS screens
11. AI screens
12. platform and integration admin
