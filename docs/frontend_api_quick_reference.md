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
| `GET` | `/api/v1/tenants/` | No | - | List tenant |
| `GET` | `/api/v1/sppg/` | No | - | List SPPG |
| `GET` | `/api/v1/programs/` | No | - | List program |
| `GET` | `/api/v1/programs/{program_id}` | No | - | Detail program beserta assignment |
| `POST` | `/api/v1/programs/` | Yes | `super_admin`, `tenant_admin` | Buat program |
| `POST` | `/api/v1/programs/{program_id}/periods` | Yes | `super_admin`, `tenant_admin` | Buat periode program |
| `POST` | `/api/v1/programs/{program_id}/tenants` | Yes | `super_admin`, `tenant_admin` | Assign tenant ke program |
| `POST` | `/api/v1/programs/{program_id}/sppg` | Yes | `super_admin`, `tenant_admin` | Assign SPPG ke program |
| `GET` | `/api/v1/quality/inspections/` | No | - | List inspeksi QC |
| `GET` | `/api/v1/quality/inspections/{inspection_id}` | No | - | Detail inspeksi QC |
| `POST` | `/api/v1/quality/inspections/` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `quality_officer` | Buat inspeksi QC |
| `POST` | `/api/v1/quality/inspections/{inspection_id}/lines` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `quality_officer` | Tambah parameter hasil QC |
| `POST` | `/api/v1/quality/inspections/{inspection_id}/finalize` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `quality_officer` | Finalisasi hasil QC |
| `GET` | `/api/v1/workflows/definitions` | No | - | List workflow definition per tenant |
| `GET` | `/api/v1/workflows/definitions/{definition_id}` | No | - | Detail workflow definition |
| `POST` | `/api/v1/workflows/definitions` | Yes | `super_admin`, `tenant_admin` | Buat workflow definition |
| `POST` | `/api/v1/workflows/definitions/{definition_id}/transitions` | Yes | `super_admin`, `tenant_admin` | Tambah transisi workflow |
| `GET` | `/api/v1/workflows/documents/{document_type}/{document_id}` | No | - | Lihat instance workflow dan history dokumen |
| `GET` | `/api/v1/audit/events/` | Yes | `super_admin`, `tenant_admin` | List audit event |
| `GET` | `/api/v1/audit/events/{event_id}` | Yes | `super_admin`, `tenant_admin` | Detail audit event |
| `GET` | `/api/v1/documents` | No | - | List dokumen berdasarkan scope tenant/SPPG |
| `GET` | `/api/v1/documents/{document_id}` | No | - | Detail dokumen, versi, dan link |
| `POST` | `/api/v1/documents` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `quality_officer`, `finance_manager` | Buat metadata dokumen |
| `POST` | `/api/v1/documents/{document_id}/versions` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `quality_officer`, `finance_manager` | Tambah versi dokumen |
| `POST` | `/api/v1/documents/{document_id}/links` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `quality_officer`, `finance_manager` | Link dokumen ke entity bisnis |
| `GET` | `/api/v1/reporting/dashboard/tenant` | No | - | Dashboard tenant |
| `GET` | `/api/v1/reporting/dashboard/sppg` | No | - | Dashboard SPPG |
| `GET` | `/api/v1/reporting/stock-summary` | No | - | Ringkasan stok |
| `GET` | `/api/v1/reporting/delivery-performance` | No | - | Ringkasan performa delivery |
| `GET` | `/api/v1/reporting/budget-summary` | No | - | Ringkasan budget |
| `GET` | `/api/v1/integration/external-systems` | No | - | List external system |
| `GET` | `/api/v1/integration/external-systems/{external_system_id}` | No | - | Detail external system dan credential |
| `POST` | `/api/v1/integration/external-systems` | Yes | `super_admin`, `tenant_admin` | Buat external system |
| `POST` | `/api/v1/integration/external-systems/{external_system_id}/credentials` | Yes | `super_admin`, `tenant_admin` | Buat credential metadata |
| `GET` | `/api/v1/integration/sync-logs` | Yes | `super_admin`, `tenant_admin` | List sync log |
| `GET` | `/api/v1/integration/sync-logs/{sync_log_id}` | Yes | `super_admin`, `tenant_admin` | Detail sync log |
| `POST` | `/api/v1/integration/sync-logs` | Yes | `super_admin`, `tenant_admin` | Buat sync log outbound/inbound |
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
| `GET` | `/api/v1/inventory/transactions/` | No | - | List ledger inventory |
| `POST` | `/api/v1/inventory/transactions/` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `warehouse_operator`, `procurement_officer` | Post transaksi inventory |
| `GET` | `/api/v1/inventory/balances/` | No | - | List saldo stok |
| `GET` | `/api/v1/procurement/purchase-requests/` | No | - | List purchase request |
| `POST` | `/api/v1/procurement/purchase-requests/from-meal-plan/{meal_plan_id}` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `procurement_officer` | Buat PR dari shortage |
| `GET` | `/api/v1/procurement/purchase-requests/goods-receipts/` | No | - | List goods receipt |
| `POST` | `/api/v1/procurement/purchase-requests/goods-receipts/from-purchase-request/{purchase_request_id}` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `procurement_officer` | Terima barang dan tambah stok |
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
| `POST` | `/api/v1/delivery-orders/from-production-order/{production_order_id}` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `delivery_officer` | Buat delivery order |
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
  "received_portions": 98,
  "rejected_portions": 2,
  "temperature_celsius": 62.5,
  "condition_notes": "Diterima dengan sedikit reject"
}
```

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
