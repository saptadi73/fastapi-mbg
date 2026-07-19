# Frontend API Quick Reference

Ringkasan cepat untuk integrasi frontend ke backend ERP MBG per 19 Juli 2026.

## Base URL

```text
http://127.0.0.1:8000
```

## Demo Accounts

| Role | Email | Password |
|---|---|---|
| `super_admin` | `operator@example.com` | `mbg12345` |
| `viewer` | `viewer@example.com` | `viewer123` |

## Auth Flow

1. `POST /api/v1/identity/login`
2. Ambil `data.access_token`
3. Kirim:

```http
Authorization: Bearer <access_token>
```

## Endpoint Matrix

| Method | Endpoint | Auth | Role | Kegunaan |
|---|---|---|---|---|
| `GET` | `/health/live` | No | - | Health check ringan |
| `GET` | `/health/ready` | No | - | Readiness check |
| `GET` | `/health/database` | No | - | Check database |
| `POST` | `/api/v1/identity/login` | No | - | Login JWT |
| `GET` | `/api/v1/identity/me` | Yes | Any | Profil user aktif |
| `POST` | `/api/v1/identity/switch-active-sppg` | Yes | Any | Pindah context SPPG aktif |
| `GET` | `/api/v1/identity/users` | Yes | `super_admin`, `tenant_admin` | List user admin |
| `GET` | `/api/v1/identity/users/{user_id}` | Yes | `super_admin`, `tenant_admin` | Detail user admin |
| `POST` | `/api/v1/identity/users` | Yes | `super_admin`, `tenant_admin` | Buat user baru |
| `PUT` | `/api/v1/identity/users/{user_id}` | Yes | `super_admin`, `tenant_admin` | Update profil, role, dan scope user |
| `GET` | `/api/v1/identity/users/{user_id}/sppg-access` | Yes | `super_admin`, `tenant_admin` | Lihat akses SPPG user |
| `PUT` | `/api/v1/identity/users/{user_id}/sppg-access` | Yes | `super_admin`, `tenant_admin` | Ubah akses SPPG user |
| `GET` | `/api/v1/ai/forecasts` | No | - | List AI forecast |
| `POST` | `/api/v1/ai/forecasts` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `finance_manager` | Simpan AI forecast |
| `GET` | `/api/v1/ai/forecasts/{forecast_id}` | No | - | Detail AI forecast |
| `GET` | `/api/v1/ai/recommendations` | No | - | List AI recommendation |
| `POST` | `/api/v1/ai/recommendations` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `finance_manager` | Simpan AI recommendation |
| `GET` | `/api/v1/ai/recommendations/{recommendation_id}` | No | - | Detail AI recommendation |
| `GET` | `/api/v1/ai/daily-summaries` | No | - | List AI daily summary |
| `POST` | `/api/v1/ai/daily-summaries` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `finance_manager` | Simpan AI daily summary |
| `GET` | `/api/v1/ai/daily-summaries/{summary_id}` | No | - | Detail AI daily summary |
| `GET` | `/api/v1/ai/overview` | No | - | Ringkasan AI forecast/recommendation/summary |
| `GET` | `/api/v1/ai/providers/status` | No | - | Cek status konfigurasi OpenAI NL2SQL dan Google AI |
| `POST` | `/api/v1/ai/nl2sql/query` | Yes | `super_admin`, `tenant_admin`, `finance_manager`, `operations_manager` | Ubah pertanyaan analitik menjadi SQL aman |
| `POST` | `/api/v1/ai/media/analyze-image` | Yes | `super_admin`, `tenant_admin`, `quality_officer`, `operations_manager` | Analisa foto dengan Google AI |
| `POST` | `/api/v1/ai/media/analyze-video` | Yes | `super_admin`, `tenant_admin`, `quality_officer`, `operations_manager` | Analisa video dengan Google AI |
| `GET` | `/api/v1/gis/sppg-map` | No | - | Marker dan radius layanan SPPG |
| `GET` | `/api/v1/gis/kitchens` | No | - | Layer GeoJSON dapur dalam bbox |
| `GET` | `/api/v1/gis/schools` | No | - | Layer GeoJSON sekolah dengan filter spasial dan operasional |
| `GET` | `/api/v1/gis/service-coverage` | No | - | Analisa coverage sekolah terhadap radius layanan SPPG |
| `GET` | `/api/v1/gis/delivery-routes` | No | - | Garis rute delivery dari SPPG ke sekolah |
| `GET` | `/api/v1/gis/deliveries/{delivery_id}/route` | No | - | Detail rute untuk satu delivery |
| `GET` | `/api/v1/gis/unserved-schools` | No | - | Daftar sekolah yang belum tercakup radius layanan |
| `GET` | `/api/v1/gis/sppg-risk-heatmap` | No | - | Heatmap risiko operasional berbasis coverage GIS |
| `GET` | `/api/v1/gis/heatmaps/distribution` | No | - | Heatmap distribusi per sekolah |
| `GET` | `/api/v1/gis/service-areas` | No | - | List polygon area layanan PostGIS |
| `GET` | `/api/v1/gis/service-areas/{service_area_id}` | No | - | Detail polygon area layanan |
| `GET` | `/api/v1/gis/kitchens/{kitchen_id}/service-area` | No | - | Ambil service area terbaru dapur |
| `POST` | `/api/v1/gis/service-areas` | Yes | `super_admin`, `tenant_admin`, `operations_manager` | Buat polygon area layanan |
| `PUT` | `/api/v1/gis/kitchens/{kitchen_id}/service-area` | Yes | `super_admin`, `tenant_admin`, `operations_manager` | Simpan service area `MultiPolygon` dapur |
| `GET` | `/api/v1/gis/schools/{school_id}/nearest-kitchens` | No | - | Cari dapur terdekat |
| `POST` | `/api/v1/gis/assignments/validate` | No | - | Validasi spasial assignment sekolah ke dapur |
| `GET` | `/api/v1/tenants/` | No | - | List tenant |
| `GET` | `/api/v1/sppg/` | No | - | List SPPG |
| `GET` | `/api/v1/programs/` | No | - | List program |
| `GET` | `/api/v1/programs/{program_id}` | No | - | Detail program beserta assignment |
| `POST` | `/api/v1/programs/` | Yes | `super_admin`, `tenant_admin` | Buat program |
| `POST` | `/api/v1/programs/{program_id}/periods` | Yes | `super_admin`, `tenant_admin` | Buat periode program |
| `POST` | `/api/v1/programs/{program_id}/tenants` | Yes | `super_admin`, `tenant_admin` | Assign tenant ke program |
| `POST` | `/api/v1/programs/{program_id}/sppg` | Yes | `super_admin`, `tenant_admin` | Assign SPPG ke program |
| `GET` | `/api/v1/costing/policies` | No | - | List cost policy |
| `POST` | `/api/v1/costing/policies` | Yes | `super_admin`, `tenant_admin`, `finance_manager` | Buat cost policy |
| `GET` | `/api/v1/costing/production-costs/{production_order_id}` | No | - | Ringkasan costing produksi dan variance |
| `GET` | `/api/v1/notifications/templates` | No | - | List notification template |
| `POST` | `/api/v1/notifications/templates` | Yes | `super_admin`, `tenant_admin`, `operations_manager` | Buat notification template |
| `GET` | `/api/v1/notifications/preferences/me` | Yes | login | Ambil preferensi notifikasi user aktif |
| `PUT` | `/api/v1/notifications/preferences/me` | Yes | login | Simpan preferensi notifikasi user aktif |
| `GET` | `/api/v1/notifications/inbox` | Yes | login | Ambil inbox notifikasi user aktif |
| `POST` | `/api/v1/notifications` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `quality_officer`, `finance_manager` | Buat/enqueue notification |
| `GET` | `/api/v1/notifications/{notification_id}` | No | - | Detail notification, recipient, delivery |
| `POST` | `/api/v1/notifications/inbox/{recipient_id}/mark-read` | Yes | login | Tandai inbox item sudah dibaca |
| `GET` | `/api/v1/government-claims` | No | - | List government claim |
| `GET` | `/api/v1/government-claims/{claim_id}` | No | - | Detail government claim |
| `POST` | `/api/v1/government-claims` | Yes | `super_admin`, `tenant_admin`, `finance_manager` | Buat government claim dari delivery aktual |
| `POST` | `/api/v1/government-claims/{claim_id}/submit` | Yes | `super_admin`, `tenant_admin`, `finance_manager` | Submit government claim |
| `POST` | `/api/v1/government-claims/{claim_id}/verify` | Yes | `super_admin`, `tenant_admin`, `finance_manager` | Verifikasi government claim |
| `POST` | `/api/v1/government-claims/{claim_id}/adjustments` | Yes | `super_admin`, `tenant_admin`, `finance_manager` | Tambah adjustment claim |
| `POST` | `/api/v1/government-claims/{claim_id}/payments` | Yes | `super_admin`, `tenant_admin`, `finance_manager` | Catat pembayaran claim dan posting jurnal |
| `GET` | `/api/v1/funding/sources` | No | - | List funding source |
| `POST` | `/api/v1/funding/sources` | Yes | `super_admin`, `tenant_admin`, `finance_manager` | Buat funding source |
| `GET` | `/api/v1/funding/agreements` | No | - | List funding agreement |
| `GET` | `/api/v1/funding/agreements/{agreement_id}` | No | - | Detail funding agreement, source, disbursement, repayment |
| `POST` | `/api/v1/funding/agreements` | Yes | `super_admin`, `tenant_admin`, `finance_manager` | Buat funding agreement |
| `GET` | `/api/v1/funding/disbursements` | No | - | List funding disbursement |
| `POST` | `/api/v1/funding/agreements/{agreement_id}/disbursements` | Yes | `super_admin`, `tenant_admin`, `finance_manager` | Catat pencairan dana dan posting jurnal |
| `GET` | `/api/v1/funding/repayments` | No | - | List funding repayment |
| `POST` | `/api/v1/funding/agreements/{agreement_id}/repayments` | Yes | `super_admin`, `tenant_admin`, `finance_manager` | Catat pengembalian pokok/margin dan posting jurnal |
| `GET` | `/api/v1/funding/summary` | No | - | Ringkasan funding tenant |
| `GET` | `/api/v1/fleet/vehicle-types` | No | - | List tipe kendaraan |
| `POST` | `/api/v1/fleet/vehicle-types` | Yes | `super_admin`, `tenant_admin`, `operations_manager` | Buat tipe kendaraan |
| `GET` | `/api/v1/fleet/vehicles` | No | - | List kendaraan |
| `GET` | `/api/v1/fleet/vehicles/{vehicle_id}` | No | - | Detail kendaraan, assignment, maintenance |
| `POST` | `/api/v1/fleet/vehicles` | Yes | `super_admin`, `tenant_admin`, `operations_manager` | Buat kendaraan |
| `GET` | `/api/v1/fleet/drivers` | No | - | List driver |
| `POST` | `/api/v1/fleet/drivers` | Yes | `super_admin`, `tenant_admin`, `operations_manager` | Buat driver |
| `GET` | `/api/v1/fleet/assignments` | No | - | List assignment kendaraan |
| `POST` | `/api/v1/fleet/vehicles/{vehicle_id}/assignments` | Yes | `super_admin`, `tenant_admin`, `operations_manager` | Assign kendaraan ke SPPG/driver |
| `GET` | `/api/v1/fleet/maintenances` | No | - | List maintenance kendaraan |
| `POST` | `/api/v1/fleet/vehicles/{vehicle_id}/maintenances` | Yes | `super_admin`, `tenant_admin`, `operations_manager` | Catat maintenance kendaraan |
| `GET` | `/api/v1/feedback/submissions` | No | - | List feedback submission |
| `GET` | `/api/v1/feedback/submissions/{submission_id}` | No | - | Detail feedback, item, complaint terkait |
| `POST` | `/api/v1/feedback/submissions` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `quality_officer`, `delivery_officer` | Buat feedback submission |
| `GET` | `/api/v1/feedback/complaints` | No | - | List complaint |
| `POST` | `/api/v1/feedback/complaints` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `quality_officer`, `delivery_officer` | Catat complaint |
| `GET` | `/api/v1/feedback/service-quality-scores` | No | - | List service quality score |
| `POST` | `/api/v1/feedback/service-quality-scores` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `quality_officer` | Catat service quality score |
| `GET` | `/api/v1/feedback/summary` | No | - | Ringkasan feedback dan complaint |
| `GET` | `/api/v1/assets/categories` | No | - | List kategori asset |
| `POST` | `/api/v1/assets/categories` | Yes | `super_admin`, `tenant_admin`, `finance_manager`, `operations_manager` | Buat kategori asset |
| `GET` | `/api/v1/assets/` | No | - | List asset |
| `GET` | `/api/v1/assets/{asset_id}` | No | - | Detail asset, assignment, depresiasi |
| `POST` | `/api/v1/assets/` | Yes | `super_admin`, `tenant_admin`, `finance_manager`, `operations_manager` | Buat asset |
| `GET` | `/api/v1/assets/assignments/` | No | - | List assignment asset |
| `POST` | `/api/v1/assets/{asset_id}/assignments` | Yes | `super_admin`, `tenant_admin`, `operations_manager` | Assign asset ke SPPG |
| `GET` | `/api/v1/assets/depreciations/` | No | - | List depresiasi asset |
| `POST` | `/api/v1/assets/{asset_id}/depreciations` | Yes | `super_admin`, `tenant_admin`, `finance_manager` | Catat depresiasi asset dan posting jurnal |
| `GET` | `/api/v1/workforce/positions` | No | - | List posisi kerja |
| `POST` | `/api/v1/workforce/positions` | Yes | `super_admin`, `tenant_admin`, `operations_manager` | Buat posisi kerja |
| `GET` | `/api/v1/workforce/employees` | No | - | List employee |
| `GET` | `/api/v1/workforce/employees/{employee_id}` | No | - | Detail employee dan assignment |
| `POST` | `/api/v1/workforce/employees` | Yes | `super_admin`, `tenant_admin`, `operations_manager` | Buat employee |
| `POST` | `/api/v1/workforce/employees/{employee_id}/assignments` | Yes | `super_admin`, `tenant_admin`, `operations_manager` | Assign employee ke SPPG |
| `GET` | `/api/v1/workforce/shifts` | No | - | List shift kerja |
| `POST` | `/api/v1/workforce/shifts` | Yes | `super_admin`, `tenant_admin`, `operations_manager` | Buat shift kerja |
| `GET` | `/api/v1/workforce/attendance` | No | - | List attendance |
| `POST` | `/api/v1/workforce/attendance` | Yes | `super_admin`, `tenant_admin`, `operations_manager` | Catat attendance |
| `GET` | `/api/v1/workforce/timesheets` | No | - | List timesheet |
| `POST` | `/api/v1/workforce/timesheets` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `finance_manager` | Buat timesheet |
| `GET` | `/api/v1/workforce/labor-costs` | No | - | List labor cost |
| `POST` | `/api/v1/workforce/labor-costs` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `finance_manager` | Catat labor cost |
| `GET` | `/api/v1/quality/inspections/` | No | - | List inspeksi QC |
| `GET` | `/api/v1/quality/inspections/{inspection_id}` | No | - | Detail inspeksi QC |
| `POST` | `/api/v1/quality/inspections/` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `quality_officer` | Buat inspeksi QC |
| `POST` | `/api/v1/quality/inspections/{inspection_id}/lines` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `quality_officer` | Tambah parameter hasil QC |
| `POST` | `/api/v1/quality/inspections/{inspection_id}/finalize` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `quality_officer` | Finalisasi hasil QC |
| `GET` | `/api/v1/workflows/definitions` | No | - | List workflow definition per tenant |
| `GET` | `/api/v1/workflows/definitions/{definition_id}` | No | - | Detail workflow definition |
| `POST` | `/api/v1/workflows/definitions` | Yes | `super_admin`, `tenant_admin` | Buat workflow definition |
| `POST` | `/api/v1/workflows/definitions/{definition_id}/versions` | Yes | `super_admin`, `tenant_admin` | Tambah workflow version |
| `POST` | `/api/v1/workflows/versions/{version_id}/states` | Yes | `super_admin`, `tenant_admin` | Tambah workflow state pada version |
| `POST` | `/api/v1/workflows/versions/{version_id}/actions` | Yes | `super_admin`, `tenant_admin` | Tambah workflow action pada version |
| `POST` | `/api/v1/workflows/definitions/{definition_id}/transitions` | Yes | `super_admin`, `tenant_admin` | Tambah transisi workflow |
| `GET` | `/api/v1/workflows/documents/{document_type}/{document_id}` | No | - | Lihat instance workflow dan history dokumen |
| `POST` | `/api/v1/workflows/instances/{workflow_instance_id}/approval-requests` | Yes | `super_admin`, `tenant_admin` | Buat approval request manual untuk instance workflow |
| `POST` | `/api/v1/workflows/approval-requests/{approval_request_id}/decisions` | Yes | `super_admin`, `tenant_admin` | Catat approval decision |
| `GET` | `/api/v1/audit/events/` | Yes | `super_admin`, `tenant_admin` | List audit event |
| `GET` | `/api/v1/audit/events/{event_id}` | Yes | `super_admin`, `tenant_admin` | Detail audit event |
| `GET` | `/api/v1/documents` | No | - | List dokumen berdasarkan scope tenant/SPPG |
| `GET` | `/api/v1/documents/{document_id}` | No | - | Detail dokumen, versi, dan link |
| `POST` | `/api/v1/documents` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `quality_officer`, `finance_manager` | Buat metadata dokumen |
| `POST` | `/api/v1/documents/{document_id}/versions` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `quality_officer`, `finance_manager` | Tambah versi dokumen |
| `POST` | `/api/v1/documents/{document_id}/links` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `quality_officer`, `finance_manager` | Link dokumen ke entity bisnis |
| `GET` | `/api/v1/reporting/dashboard/tenant` | No | - | Dashboard tenant |
| `GET` | `/api/v1/reporting/dashboard/sppg` | No | - | Dashboard SPPG |
| `GET` | `/api/v1/reporting/dashboard/finance` | No | - | Dashboard finance khusus |
| `GET` | `/api/v1/reporting/stock-summary` | No | - | Ringkasan stok |
| `GET` | `/api/v1/reporting/delivery-performance` | No | - | Ringkasan performa delivery |
| `GET` | `/api/v1/reporting/budget-summary` | No | - | Ringkasan budget |
| `GET` | `/api/v1/reporting/finance/cash-flow` | No | - | Cash flow dari jurnal kas/bank |
| `GET` | `/api/v1/reporting/finance/government-receivable-aging` | No | - | Aging piutang government claim |
| `GET` | `/api/v1/reporting/finance/investor-funding-position` | No | - | Posisi pendanaan investor |
| `GET` | `/api/v1/reporting/finance/roi-by-sppg` | No | - | ROI per SPPG |
| `GET` | `/api/v1/integration/external-systems` | No | - | List external system |
| `GET` | `/api/v1/integration/external-systems/{external_system_id}` | No | - | Detail external system dan credential |
| `POST` | `/api/v1/integration/external-systems` | Yes | `super_admin`, `tenant_admin` | Buat external system |
| `POST` | `/api/v1/integration/external-systems/{external_system_id}/credentials` | Yes | `super_admin`, `tenant_admin` | Buat credential metadata |
| `GET` | `/api/v1/integration/webhook-subscriptions` | Yes | `super_admin`, `tenant_admin` | List webhook subscription |
| `POST` | `/api/v1/integration/webhook-subscriptions` | Yes | `super_admin`, `tenant_admin` | Buat webhook subscription |
| `POST` | `/api/v1/integration/webhook-subscriptions/{subscription_id}/receive` | No | - | Terima inbound webhook dan buat inbound message |
| `GET` | `/api/v1/integration/data-mappings` | Yes | `super_admin`, `tenant_admin` | List data mapping |
| `POST` | `/api/v1/integration/data-mappings` | Yes | `super_admin`, `tenant_admin` | Buat data mapping |
| `GET` | `/api/v1/integration/sync-jobs` | Yes | `super_admin`, `tenant_admin` | List sync job |
| `GET` | `/api/v1/integration/sync-jobs/{sync_job_id}` | Yes | `super_admin`, `tenant_admin` | Detail sync job |
| `POST` | `/api/v1/integration/sync-jobs` | Yes | `super_admin`, `tenant_admin` | Buat sync job |
| `POST` | `/api/v1/integration/sync-jobs/{sync_job_id}/run` | Yes | `super_admin`, `tenant_admin` | Jalankan sync job dan buat outbound message |
| `GET` | `/api/v1/integration/inbound-messages` | Yes | `super_admin`, `tenant_admin` | List inbound message |
| `GET` | `/api/v1/integration/inbound-messages/{inbound_message_id}` | Yes | `super_admin`, `tenant_admin` | Detail inbound message |
| `POST` | `/api/v1/integration/inbound-messages` | Yes | `super_admin`, `tenant_admin` | Buat inbound message manual |
| `GET` | `/api/v1/integration/outbound-messages` | Yes | `super_admin`, `tenant_admin` | List outbound message |
| `GET` | `/api/v1/integration/outbound-messages/{outbound_message_id}` | Yes | `super_admin`, `tenant_admin` | Detail outbound message |
| `POST` | `/api/v1/integration/outbound-messages` | Yes | `super_admin`, `tenant_admin` | Buat outbound message manual |
| `GET` | `/api/v1/integration/sync-logs` | Yes | `super_admin`, `tenant_admin` | List sync log |
| `GET` | `/api/v1/integration/sync-logs/{sync_log_id}` | Yes | `super_admin`, `tenant_admin` | Detail sync log |
| `POST` | `/api/v1/integration/sync-logs` | Yes | `super_admin`, `tenant_admin` | Buat sync log outbound/inbound |
| `GET` | `/api/v1/platform/background-jobs` | Yes | `super_admin`, `tenant_admin` | List background job internal |
| `POST` | `/api/v1/platform/background-jobs` | Yes | `super_admin`, `tenant_admin` | Buat background job internal |
| `POST` | `/api/v1/platform/background-jobs/{job_id}/run` | Yes | `super_admin`, `tenant_admin` | Jalankan background job manual |
| `GET` | `/api/v1/platform/outbox-events` | Yes | `super_admin`, `tenant_admin` | List transactional outbox |
| `POST` | `/api/v1/platform/outbox-events` | Yes | `super_admin`, `tenant_admin` | Buat outbox event manual |
| `POST` | `/api/v1/platform/outbox-events/dispatch` | Yes | `super_admin`, `tenant_admin` | Dispatch pending outbox event |
| `GET` | `/api/v1/platform/read-models/daily-kitchen-operations` | Yes | `super_admin`, `tenant_admin` | List summary table operasi dapur harian |
| `POST` | `/api/v1/platform/read-models/daily-kitchen-operations/refresh` | Yes | `super_admin`, `tenant_admin` | Refresh summary table operasi dapur harian |
| `GET` | `/api/v1/platform/read-models/monthly-budget-realizations` | Yes | `super_admin`, `tenant_admin` | List summary table budget bulanan |
| `POST` | `/api/v1/platform/read-models/monthly-budget-realizations/refresh` | Yes | `super_admin`, `tenant_admin` | Refresh summary table budget bulanan |
| `GET` | `/api/v1/platform/materialized-views/delivery-performance` | Yes | `super_admin`, `tenant_admin` | Baca materialized view delivery performance |
| `POST` | `/api/v1/platform/materialized-views/delivery-performance/refresh` | Yes | `super_admin`, `tenant_admin` | Refresh materialized view delivery performance |
| `GET` | `/api/v1/geography/schools/` | No | - | List sekolah |
| `GET` | `/api/v1/beneficiaries/` | No | - | List beneficiary |
| `GET` | `/api/v1/uoms/` | No | - | List UoM |
| `GET` | `/api/v1/products/` | No | - | List produk |
| `GET` | `/api/v1/recipes/` | No | - | List recipe |
| `GET` | `/api/v1/meal-plans/` | No | - | List meal plan |
| `POST` | `/api/v1/meal-plans/{meal_plan_id}/submit` | Yes | `super_admin`, `tenant_admin`, `operations_manager` | Submit meal plan |
| `POST` | `/api/v1/meal-plans/{meal_plan_id}/approve` | Yes | `super_admin`, `tenant_admin`, `operations_manager` | Approve meal plan |
| `POST` | `/api/v1/meal-plans/{meal_plan_id}/reserve-materials` | Yes | `super_admin`, `tenant_admin`, `operations_manager` | Reserve stok bahan |
| `GET` | `/api/v1/meal-plans/{meal_plan_id}/cost-preview` | No | - | Preview biaya meal plan |
| `GET` | `/api/v1/inventory/warehouses/` | No | - | List warehouse |
| `POST` | `/api/v1/inventory/warehouses/` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `warehouse_operator`, `procurement_officer` | Buat warehouse |
| `GET` | `/api/v1/inventory/locations/` | No | - | List stock location |
| `POST` | `/api/v1/inventory/locations/` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `warehouse_operator`, `procurement_officer` | Buat stock location |
| `GET` | `/api/v1/inventory/batches/` | No | - | List batch inventory |
| `POST` | `/api/v1/inventory/batches/` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `warehouse_operator`, `procurement_officer` | Buat batch/lot inventory |
| `GET` | `/api/v1/inventory/transactions/` | No | - | List ledger inventory |
| `POST` | `/api/v1/inventory/transactions/` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `warehouse_operator`, `procurement_officer` | Post transaksi inventory |
| `GET` | `/api/v1/inventory/balances/` | No | - | List saldo stok |
| `GET` | `/api/v1/inventory/expiry-alerts` | No | - | Batch yang mendekati expiry |
| `POST` | `/api/v1/inventory/issues/fefo-preview` | No | - | Preview pemilihan batch FEFO |
| `GET` | `/api/v1/procurement/purchase-requests/suppliers` | No | - | List supplier |
| `GET` | `/api/v1/procurement/purchase-requests/suppliers/{supplier_id}` | No | - | Detail supplier |
| `POST` | `/api/v1/procurement/purchase-requests/suppliers` | Yes | `super_admin`, `tenant_admin`, `procurement_officer`, `operations_manager` | Buat supplier |
| `GET` | `/api/v1/procurement/purchase-requests/supplier-products` | No | - | List mapping supplier-produk |
| `POST` | `/api/v1/procurement/purchase-requests/supplier-products` | Yes | `super_admin`, `tenant_admin`, `procurement_officer`, `operations_manager` | Buat mapping supplier-produk |
| `GET` | `/api/v1/procurement/purchase-requests/supplier-price-histories` | No | - | List histori harga supplier |
| `POST` | `/api/v1/procurement/purchase-requests/supplier-price-histories` | Yes | `super_admin`, `tenant_admin`, `procurement_officer`, `operations_manager` | Simpan histori harga supplier |
| `GET` | `/api/v1/procurement/purchase-requests/` | No | - | List purchase request |
| `POST` | `/api/v1/procurement/purchase-requests/from-meal-plan/{meal_plan_id}` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `procurement_officer` | Buat PR dari shortage |
| `GET` | `/api/v1/procurement/purchase-requests/purchase-orders/` | No | - | List purchase order/RFQ |
| `GET` | `/api/v1/procurement/purchase-requests/purchase-orders/{purchase_order_id}` | No | - | Detail purchase order/RFQ |
| `POST` | `/api/v1/procurement/purchase-requests/purchase-orders/from-purchase-request/{purchase_request_id}` | Yes | `super_admin`, `tenant_admin`, `procurement_officer`, `operations_manager` | Buat PO/RFQ dari PR |
| `GET` | `/api/v1/procurement/purchase-requests/goods-receipts/` | No | - | List goods receipt |
| `POST` | `/api/v1/procurement/purchase-requests/goods-receipts/from-purchase-request/{purchase_request_id}` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `procurement_officer` | Terima barang dan tambah stok |
| `POST` | `/api/v1/procurement/purchase-requests/goods-receipts/from-purchase-order/{purchase_order_id}` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `procurement_officer` | Terima barang dari PO dengan batch/expiry opsional |
| `GET` | `/api/v1/procurement/purchase-requests/supplier-invoices/` | No | - | List supplier invoice |
| `GET` | `/api/v1/procurement/purchase-requests/supplier-invoices/{supplier_invoice_id}` | No | - | Detail supplier invoice |
| `POST` | `/api/v1/procurement/purchase-requests/supplier-invoices/from-goods-receipt/{goods_receipt_id}` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `procurement_officer`, `finance_manager` | Buat invoice supplier dari goods receipt |
| `GET` | `/api/v1/procurement/purchase-requests/supplier-payments/` | No | - | List supplier payment |
| `GET` | `/api/v1/procurement/purchase-requests/supplier-payments/{supplier_payment_id}` | No | - | Detail supplier payment |
| `POST` | `/api/v1/procurement/purchase-requests/supplier-payments/from-supplier-invoice/{supplier_invoice_id}` | Yes | `super_admin`, `tenant_admin`, `finance_manager` | Bayar invoice supplier |
| `GET` | `/api/v1/production-orders/` | No | - | List production order |
| `POST` | `/api/v1/production-orders/from-meal-plan/{meal_plan_id}` | Yes | `super_admin`, `tenant_admin`, `operations_manager` | Buat production order |
| `POST` | `/api/v1/production-orders/{production_order_id}/complete` | Yes | `super_admin`, `tenant_admin`, `operations_manager` | Selesaikan produksi |
| `GET` | `/api/v1/production-orders/{production_order_id}/cost-sheet` | No | - | Lihat actual cost produksi |
| `GET` | `/api/v1/delivery-orders/` | No | - | List delivery order |
| `GET` | `/api/v1/delivery-orders/routes` | No | - | List route planning delivery |
| `GET` | `/api/v1/delivery-orders/routes/{route_id}` | No | - | Detail route, stop, dan incident delivery |
| `POST` | `/api/v1/delivery-orders/routes` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `delivery_officer` | Buat route planning delivery |
| `POST` | `/api/v1/delivery-orders/from-production-order/{production_order_id}` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `delivery_officer` | Buat delivery order |
| `POST` | `/api/v1/delivery-orders/{delivery_order_id}/incidents` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `delivery_officer` | Catat incident distribution |
| `POST` | `/api/v1/delivery-orders/{delivery_order_id}/proof` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `delivery_officer` | Catat proof of delivery |
| `GET` | `/api/v1/accounts` | No | - | List chart of accounts |
| `POST` | `/api/v1/accounts` | Yes | `super_admin`, `tenant_admin`, `finance_manager` | Buat account |
| `GET` | `/api/v1/journal-entries` | No | - | List journal entry |
| `GET` | `/api/v1/journal-entries/{journal_entry_id}` | No | - | Detail journal entry |
| `POST` | `/api/v1/journal-entries` | Yes | `super_admin`, `tenant_admin`, `finance_manager` | Buat jurnal draft |
| `POST` | `/api/v1/journal-entries/{journal_entry_id}/post` | Yes | `super_admin`, `tenant_admin`, `finance_manager` | Post jurnal |
| `GET` | `/api/v1/budgets` | No | - | List budget |
| `GET` | `/api/v1/budgets/{budget_id}` | No | - | Detail budget |
| `POST` | `/api/v1/budgets` | Yes | `super_admin`, `tenant_admin`, `finance_manager` | Buat budget |
| `POST` | `/api/v1/budgets/{budget_id}/submit` | Yes | `super_admin`, `tenant_admin`, `finance_manager` | Submit budget |
| `POST` | `/api/v1/budgets/{budget_id}/approve` | Yes | `super_admin`, `tenant_admin`, `finance_manager` | Approve budget |
| `GET` | `/api/v1/budgets/{budget_id}/availability` | No | - | Lihat sisa budget |

## Common Error Handling

| Code | UI Action |
|---|---|
| `AUTHENTICATION_REQUIRED` | Redirect login |
| `INVALID_ACCESS_TOKEN` | Hapus token lalu login ulang |
| `INSUFFICIENT_ROLE` | Tampilkan unauthorized |
| `USER_SPPG_ACCESS_DENIED` | Blok akses bila user memilih SPPG di luar hak aksesnya |
| `ACTIVE_SPPG_NOT_IN_ACCESS_LIST` | Validasi form admin akses user sebelum submit |
| `ACTIVE_SPPG_NOT_ACCESSIBLE` | Blok switch SPPG bila user tidak punya akses ke target SPPG |
| `USER_EMAIL_ALREADY_EXISTS` | Validasi email user admin agar tidak duplikat |
| `INSUFFICIENT_STOCK_FOR_MEAL_PLAN` | Tampilkan shortage dan arahkan ke procurement |
| `NO_SHORTAGE_FOR_PURCHASE_REQUEST` | Info bahwa stok sudah cukup |
| `MEAL_PLAN_NOT_READY_FOR_PRODUCTION` | Minta user reserve material dulu |
| `PRODUCTION_ORDER_NOT_READY_FOR_DELIVERY` | Minta user selesaikan produksi dulu |
| `DELIVERY_RECEIPT_EXCEEDS_SHIPPED` | Validasi form proof delivery |
| `JOURNAL_ENTRY_NOT_BALANCED` | Minta user samakan total debit dan credit |
| `JOURNAL_ENTRY_POST_INVALID_STATUS` | Nonaktifkan tombol post bila status bukan `DRAFT` |
| `BUDGET_SUBMIT_INVALID_STATUS` | Nonaktifkan submit bila budget bukan `DRAFT` |
| `BUDGET_APPROVE_INVALID_STATUS` | Nonaktifkan approve bila budget bukan `SUBMITTED` |
| `PROGRAM_CODE_ALREADY_EXISTS` | Validasi kode program agar tidak duplikat |
| `PROGRAM_TENANT_ASSIGNMENT_REQUIRED` | Assign tenant program lebih dulu sebelum assign SPPG |
| `PROGRAM_SPPG_TENANT_MISMATCH` | Validasi tenant pada form assignment SPPG |
| `QC_INSPECTION_LINES_REQUIRED` | Minta user isi minimal satu parameter QC sebelum finalize |
| `QC_INSPECTION_ALREADY_FINALIZED` | Disable tambah line bila QC sudah final |
| `PRODUCTION_QC_RELEASE_BLOCKED` | Blok pembuatan delivery bila QC wajib produksi belum lolos |
| `WORKFLOW_TENANT_CONTEXT_REQUIRED` | Kirim `X-Tenant-ID` saat membuka workflow dokumen |
| `WORKFLOW_TRANSITION_NOT_ALLOWED` | Nonaktifkan tombol aksi bila transisi tidak tersedia |
| `WORKFLOW_INSTANCE_STATE_MISMATCH` | Refresh detail dokumen jika state workflow sudah berubah |
| `AUDIT_EVENT_NOT_FOUND` | Refresh daftar audit bila detail event sudah tidak sesuai scope |
| `DOCUMENT_NOT_FOUND` | Refresh detail dokumen atau cek scope tenant/SPPG |
| `DOCUMENT_OBJECT_KEY_REQUIRED` | Validasi object key sebelum submit metadata versi |
| `DOCUMENT_LINK_ALREADY_EXISTS` | Nonaktifkan aksi link ulang pada entity yang sama |
| `EXTERNAL_SYSTEM_CODE_ALREADY_EXISTS` | Validasi kode external system agar tidak duplikat |
| `INTEGRATION_CREDENTIAL_ALREADY_EXISTS` | Hindari nama credential yang sama pada system yang sama |
| `INTEGRATION_IDEMPOTENCY_KEY_REQUIRED` | idempotency key wajib saat buat sync log |
| `SYNC_LOG_IDEMPOTENCY_CONFLICT` | Jangan kirim ulang sync log dengan key yang sama |
| `COST_POLICY_CODE_ALREADY_EXISTS` | Validasi kode cost policy agar tidak duplikat |
| `INVALID_COST_POLICY_DATE_RANGE` | Validasi tanggal aktif cost policy |
| `NOTIFICATION_TEMPLATE_CODE_ALREADY_EXISTS` | Validasi kode notification template agar tidak duplikat |
| `NOTIFICATION_TEMPLATE_NOT_FOUND` | Notification template tidak ditemukan |
| `NOTIFICATION_RECIPIENT_REQUIRED` | Minimal satu recipient wajib diisi |
| `NOTIFICATION_RECIPIENT_ADDRESS_REQUIRED` | Alamat recipient wajib diisi jika tanpa `user_id` |
| `NOTIFICATION_CHANNEL_DISABLED` | Channel notifikasi untuk user sedang dinonaktifkan |
| `NOTIFICATION_NOT_FOUND` | Notification tidak ditemukan |
| `NOTIFICATION_RECIPIENT_NOT_FOUND` | Inbox notification item tidak ditemukan |
| `labor_cost_source = ACTUAL` | Costing memakai labor cost aktual dari modul workforce |
| `labor_cost_source = POLICY` | Costing fallback ke labor cost dari cost policy |
| `labor_cost_source = NONE` | Belum ada labor cost aktual maupun policy aktif |
| `actual_labor_cost_amount` | Total biaya tenaga kerja aktual pada tenant dashboard reporting |
| `workforce.attendance_records` | Jumlah attendance pada dashboard SPPG |
| `workforce.worked_hours` | Total jam kerja pada dashboard SPPG |
| `workforce.labor_cost_amount` | Total labor cost aktual pada dashboard SPPG |
| `INVALID_CLAIM_PERIOD` | Periode government claim tidak valid |
| `CLAIM_DELIVERY_REQUIRED` | Minimal satu delivery order wajib dipilih |
| `DELIVERY_ORDER_NOT_RECEIVED` | Delivery order belum memiliki proof penerimaan |
| `GOVERNMENT_CLAIM_NOT_FOUND` | Government claim tidak ditemukan |
| `CLAIM_SUBMIT_INVALID_STATUS` | Claim belum berada pada status yang dapat disubmit |
| `CLAIM_EMPTY_AMOUNT` | Claim belum memiliki nilai yang bisa diajukan |
| `CLAIM_EVIDENCE_REQUIRED` | Claim wajib memiliki evidence |
| `CLAIM_VERIFY_INVALID_STATUS` | Claim belum berada pada status yang dapat diverifikasi |
| `CLAIM_PAYMENT_INVALID_STATUS` | Claim belum berada pada status yang dapat dibayar |
| `INVALID_CLAIM_PAYMENT_AMOUNT` | Jumlah pembayaran claim tidak valid |
| `POSITION_CODE_ALREADY_EXISTS` | Kode posisi workforce sudah digunakan |
| `EMPLOYEE_CODE_ALREADY_EXISTS` | Kode employee sudah digunakan |
| `POSITION_NOT_FOUND` | Posisi workforce tidak ditemukan |
| `EMPLOYEE_NOT_FOUND` | Employee workforce tidak ditemukan |
| `INVALID_ASSIGNMENT_DATE_RANGE` | Rentang tanggal assignment employee tidak valid |
| `EMPLOYEE_ALREADY_ASSIGNED` | Employee sudah aktif di SPPG tersebut |
| `EMPLOYEE_ASSIGNMENT_NOT_FOUND` | Assignment employee tidak ditemukan |
| `INVALID_SHIFT_TIME_RANGE` | Rentang waktu shift tidak valid |
| `WORK_SHIFT_NOT_FOUND` | Shift kerja tidak ditemukan |
| `INVALID_ATTENDANCE_TIME_RANGE` | Rentang waktu attendance tidak valid |
| `INVALID_TIMESHEET_PERIOD` | Periode timesheet tidak valid |
| `TIMESHEET_NOT_FOUND` | Timesheet tidak ditemukan |
| `INVALID_LABOR_COST_VALUE` | Nilai labor cost tidak valid |
| `SUPPLIER_INVOICE_ALREADY_EXISTS_FOR_RECEIPT` | Disable tombol create invoice jika GR sudah punya invoice |
| `SUPPLIER_PAYMENT_ALREADY_EXISTS_FOR_INVOICE` | Disable tombol bayar jika invoice sudah punya payment |

## Operational Notes

- Purchase request dari meal plan dapat otomatis menambah `reserved_amount` budget untuk account `510000` jika ada budget `APPROVED` yang aktif pada tanggal meal plan.
- Goods receipt otomatis membuat jurnal `POSTED` debit `130000` dan kredit `240000`.
- Goods receipt juga memindahkan budget dari `reserved_amount` ke `committed_amount` untuk flow procurement yang sama.
- Supplier invoice otomatis membuat jurnal `POSTED` debit `240000` dan kredit `210000`.
- Supplier invoice dapat menambah `budget actual` jika `budget_account_id` dikirim dan budget sudah `APPROVED`, sekaligus melepas `committed_amount` yang terkait.
- Supplier payment otomatis membuat jurnal `POSTED` debit `210000` dan kredit `110000`, lalu mengubah status supplier invoice menjadi `PAID`.
- Production completion otomatis membuat jurnal `POSTED` debit `510000` dan kredit `130000`.
- Frontend sebaiknya treat field `status` journal entry sebagai workflow sederhana: `DRAFT` lalu `POSTED`.
- Endpoint identity sekarang juga mengembalikan `accessible_sppg_ids` agar frontend bisa membatasi pilihan SPPG aktif sesuai hak akses user.

## Example Requests

### Create Goods Receipt

```json
{
  "warehouse_id": "{{warehouse_id}}",
  "receipt_date": "2026-07-19",
  "notes": "Received from supplier"
}
```

### Create Supplier Payment

```json
{
  "payment_date": "2026-07-19",
  "bank_account_id": "{{account_id_2}}",
  "notes": "Supplier payment posted"
}
```

### Update User SPPG Access

```json
{
  "accessible_sppg_ids": ["{{sppg_id}}"],
  "active_sppg_id": "{{sppg_id}}"
}
```

### Create User Admin

```json
{
  "tenant_id": "{{tenant_id}}",
  "full_name": "QA Admin User",
  "email": "qa-admin@example.com",
  "password": "qa12345",
  "role_names": ["tenant_admin"],
  "is_active": true,
  "accessible_sppg_ids": ["{{sppg_id}}"],
  "active_sppg_id": "{{sppg_id}}"
}
```

### Create Program

```json
{
  "code": "PRG-MBG-APBD-2026",
  "name": "Program MBG APBD 2026",
  "description": "Program bantuan gizi daerah",
  "program_type": "PUBLIC",
  "funding_source_name": "APBD Provinsi",
  "start_date": "2026-07-19",
  "end_date": "2026-12-31",
  "status": "DRAFT",
  "is_active": true
}
```

### Assign SPPG To Program

```json
{
  "tenant_id": "{{tenant_id}}",
  "sppg_id": "{{sppg_id}}",
  "start_date": "2026-07-19",
  "end_date": "2026-12-31",
  "is_active": true,
  "notes": "SPPG masuk program APBD"
}
```

### Create QC Inspection

```json
{
  "tenant_id": "{{tenant_id}}",
  "sppg_id": "{{sppg_id}}",
  "inspection_type": "PRODUCTION",
  "stage": "PRODUCTION_OUTPUT",
  "reference_type": "PRODUCTION_ORDER",
  "reference_id": "{{production_order_id}}",
  "inspection_at": "2026-07-19T08:00:00Z",
  "inspector_name": "Petugas QC",
  "is_mandatory_for_release": true,
  "notes": "QC batch produksi"
}
```

### Add QC Inspection Line

```json
{
  "parameter_name": "Suhu makanan",
  "expected_value": ">=60C",
  "actual_value": "65C",
  "result_status": "PASS",
  "notes": "Aman"
}
```

### Create Workflow Definition

```json
{
  "tenant_id": "{{tenant_id}}",
  "code": "CUSTOM-WF-DEMO",
  "name": "Workflow Dokumen Demo",
  "document_type": "custom_document_demo",
  "initial_state": "DRAFT",
  "is_active": true
}
```

### Audit Filter Example

```text
GET /api/v1/audit/events/?module_name=meal_plan&event_type=APPROVAL
```

### Create Document Metadata

```json
{
  "tenant_id": "{{tenant_id}}",
  "sppg_id": "{{sppg_id}}",
  "document_type": "QC_ATTACHMENT",
  "title": "Checklist QC Batch 1",
  "description": "Lampiran checklist quality control",
  "owner_entity_type": "meal_plan",
  "owner_entity_id": "{{meal_plan_id}}",
  "tags": ["qc", "checklist"]
}
```

### Reporting Notes

- `/api/v1/reporting/dashboard/tenant` sebaiknya dipanggil dengan `X-Tenant-ID`
- `/api/v1/reporting/dashboard/sppg` sebaiknya dipanggil dengan `X-Tenant-ID` dan `X-SPPG-ID`
- `/api/v1/reporting/dashboard/finance` cocok untuk summary layar finance manager
- `/api/v1/reporting/finance/cash-flow` mendukung `period_start` dan `period_end`
- `/api/v1/reporting/finance/government-receivable-aging` dan `/api/v1/reporting/finance/investor-funding-position` mendukung `as_of_date`
- `/api/v1/reporting/finance/roi-by-sppg` menghitung ROI dari claim approved/claimed amount dibanding total biaya produksi dan biaya pendanaan teralokasi
- read model ini belum menjadi source of truth, hanya agregasi dari modul transaksi yang sudah ada

### Create External System

```json
{
  "tenant_id": "{{tenant_id}}",
  "code": "EXT-PARTNER-ERP",
  "name": "Partner ERP Demo",
  "system_type": "ERP",
  "base_url": "https://partner.example.com/api",
  "is_active": true,
  "notes": "Sistem partner demo"
}
```

### Create Cost Policy

```json
{
  "tenant_id": "{{tenant_id}}",
  "sppg_id": "{{sppg_id}}",
  "code": "COST-SPPG-2026",
  "name": "Cost Policy Demo",
  "effective_from": "2026-07-19",
  "effective_to": null,
  "labor_cost_per_portion": 1200,
  "utility_cost_per_portion": 300,
  "packaging_cost_per_portion": 250,
  "distribution_cost_per_portion": 400,
  "overhead_cost_per_portion": 500,
  "waste_cost_percentage": 5,
  "is_active": true
}
```

Catatan `GET /api/v1/costing/production-costs/{production_order_id}`:

- `labor_cost_source` bernilai `ACTUAL` bila ada `workforce.labor_cost` pada tanggal produksi yang sama.
- `labor_cost_source` bernilai `POLICY` bila tidak ada data aktual dan sistem memakai `cost_policy`.
- `labor_cost_source` bernilai `NONE` bila keduanya tidak tersedia.

### Dispatch Notification

```json
{
  "tenant_id": "tenant-uuid",
  "sppg_id": "sppg-uuid",
  "template_id": "template-uuid",
  "source_module": "meal_plan",
  "source_entity_type": "meal_plan",
  "source_entity_id": "meal-plan-uuid",
  "title": "Meal Plan Butuh Persetujuan",
  "message": "Silakan review meal plan untuk besok pagi.",
  "priority": "HIGH",
  "recipients": [
    {
      "user_id": "user-uuid",
      "channel": "IN_APP"
    }
  ]
}
```

### Create Government Claim

```json
{
  "tenant_id": "tenant-uuid",
  "sppg_id": "sppg-uuid",
  "period_start": "2026-08-01",
  "period_end": "2026-08-31",
  "claim_type": "ACTUAL_COST",
  "delivery_order_ids": ["delivery-order-uuid"],
  "evidence_document_ids": ["document-uuid"],
  "notes": "Klaim Agustus 2026"
}
```

### Create Workforce Employee

```json
{
  "tenant_id": "tenant-uuid",
  "position_id": "position-uuid",
  "employee_code": "EMP-0001",
  "full_name": "Budi Santoso",
  "employment_type": "DAILY",
  "join_date": "2026-07-20",
  "phone_number": "081234567890",
  "daily_rate": 150000,
  "is_active": true
}
```

### Switch Active SPPG

```json
{
  "sppg_id": "{{sppg_id}}"
}
```

### Complete Production Order

```json
{
  "actual_portions": 100,
  "accepted_portions": 98,
  "rejected_portions": 2
}
```

### Record Delivery Proof

```json
{
  "received_at": "2026-07-25T08:05:00Z",
  "receiver_name": "Petugas Sekolah",
  "receiver_gps": "-6.1702,106.8283",
  "route_stop_id": "uuid",
  "received_portions": 98,
  "rejected_portions": 2,
  "temperature_celsius": 62.5,
  "condition_status": "GOOD",
  "condition_notes": "Diterima dengan sedikit reject",
  "photo_urls": ["https://example.com/proofs/arrival-1.jpg"],
  "signature_name": "Petugas Sekolah",
  "signature_url": "https://example.com/signatures/receiver-signature.png",
  "signature_signed_at": "2026-07-25T08:05:30Z",
  "incident_notes": "Ada penurunan suhu saat perjalanan namun masih diterima",
  "linked_incident_ids": ["uuid"]
}
```

### Create Delivery Route

```json
{
  "route_name": "Route Sekolah Pagi",
  "planned_departure": "2026-07-25T07:00:00Z",
  "planned_arrival": "2026-07-25T08:00:00Z",
  "notes": "Route planning untuk sekolah utama",
  "stops": [
    {
      "delivery_order_id": "uuid",
      "planned_arrival": "2026-07-25T08:00:00Z",
      "recipient_name": "Petugas Sekolah",
      "stop_gps": "-6.1702,106.8283",
      "notes": "Stop pertama"
    }
  ]
}
```

### Record Delivery Incident

```json
{
  "incident_time": "2026-07-25T07:45:00Z",
  "category": "TEMPERATURE",
  "severity": "MEDIUM",
  "title": "Suhu turun saat transit",
  "description": "Perlu pengecekan box termal",
  "route_stop_id": "uuid",
  "incident_gps": "-6.1702,106.8283",
  "temperature_celsius": 58.4,
  "media_urls": ["https://example.com/incidents/temp-drop.jpg"],
  "status": "OPEN"
}
```

### Generate NL2SQL

```json
{
  "question": "Tampilkan 10 meal plan terbaru untuk tenant aktif beserta total planned_portions.",
  "dialect": "postgresql",
  "auto_schema_context": true,
  "execute_sql": false,
  "max_rows": 10
}
```

### Analyze Image With Google AI

```json
{
  "prompt": "Jelaskan kondisi makanan, kebersihan wadah, dan potensi masalah kualitas pada foto ini.",
  "mime_type": "image/jpeg",
  "source_url": "https://example.com/sample-food-photo.jpg"
}
```

### AI Integration Notes

- Aktifkan OpenAI lewat `OPENAI_ENABLED=true`, isi `OPENAI_API_KEY`, dan gunakan default `OPENAI_NL2SQL_MODEL=gpt-5.6-terra` bila belum punya preferensi lain.
- Aktifkan Google AI lewat `GOOGLE_AI_ENABLED=true`, isi `GOOGLE_AI_API_KEY`, dan gunakan default `GOOGLE_AI_MEDIA_MODEL=gemini-2.5-flash`.
- Untuk browser frontend, pastikan header `X-SPPG-ID` ikut diizinkan CORS karena dipakai luas di modul multi-SPPG.
- Default `OPENAI_NL2SQL_ALLOW_EXECUTION=false`, jadi endpoint NL2SQL aman dipakai dulu untuk generate query tanpa eksekusi database.
- Implementasi Google AI backend saat ini masih memakai `generateContent`; ini tetap didukung, walau dokumentasi Google sekarang merekomendasikan Interactions API untuk implementasi baru.

### GIS Notes

- Seluruh endpoint GIS mendukung `X-Tenant-ID` untuk filter tenant, dan `X-SPPG-ID` untuk fokus ke satu dapur.
- `service-coverage` menerima query opsional `sppg_id`.
- GIS sekarang memakai kolom PostGIS native untuk point SPPG dan sekolah.
- Endpoint `kitchens`, `schools`, dan `heatmaps/distribution` mengembalikan `GeoJSON FeatureCollection`.
- `service-areas` sekarang dinormalisasi menjadi `MultiPolygon` PostGIS dan menerima payload `boundary_geojson` atau `boundary_wkt`.
- Endpoint `delivery-routes` membentuk line geometry dari titik SPPG ke titik sekolah berdasarkan delivery order yang sudah ada.

### Create Account

```json
{
  "tenant_id": "{{tenant_id}}",
  "code": "130000",
  "name": "Persediaan Bahan",
  "category": "ASSET",
  "normal_balance": "DEBIT",
  "allow_posting": true,
  "is_active": true
}
```

### Create Journal Entry

```json
{
  "tenant_id": "{{tenant_id}}",
  "entry_date": "2026-07-19",
  "reference": "MANUAL-JE-001",
  "description": "Jurnal koreksi manual",
  "source_module": "accounting",
  "source_document_type": "manual_adjustment",
  "source_document_id": null,
  "lines": [
    {
      "account_id": "{{account_id}}",
      "line_type": "DEBIT",
      "amount": 500000,
      "description": "Debit line"
    },
    {
      "account_id": "{{account_id_2}}",
      "line_type": "CREDIT",
      "amount": 500000,
      "description": "Credit line"
    }
  ]
}
```

### Create Budget

```json
{
  "tenant_id": "{{tenant_id}}",
  "name": "Budget Operasional Juli 2026",
  "date_start": "2026-07-01",
  "date_end": "2026-07-31",
  "version_number": 1,
  "notes": "Budget awal Juli",
  "lines": [
    {
      "category_name": "BAHAN_BAKU",
      "account_id": "{{account_id}}",
      "planned_amount": 25000000,
      "revised_amount": null,
      "control_mode": "WARNING",
      "tolerance_percentage": 0,
      "notes": "Bahan baku utama"
    }
  ]
}
```

### Create Supplier Invoice

```json
{
  "invoice_date": "2026-07-19",
  "due_date": "2026-07-26",
  "budget_account_id": "{{account_id}}",
  "notes": "Invoice supplier posted"
}
```
