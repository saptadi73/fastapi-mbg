# Frontend API Reference

Dokumentasi ini merangkum endpoint backend ERP MBG FastAPI yang aktif per 19 Juli 2026, dengan fokus kebutuhan integrasi frontend.

## Base URL

```text
http://127.0.0.1:8000
```

## Table of Contents

### Health

1. `GET /health/live`
2. `GET /health/ready`
3. `GET /health/database`

### Identity

1. `POST /api/v1/identity/login`
2. `GET /api/v1/identity/me`
3. `POST /api/v1/identity/switch-active-sppg`
4. `GET /api/v1/identity/users`
5. `GET /api/v1/identity/users/{user_id}`
6. `POST /api/v1/identity/users`
7. `PUT /api/v1/identity/users/{user_id}`
8. `GET /api/v1/identity/users/{user_id}/sppg-access`
9. `PUT /api/v1/identity/users/{user_id}/sppg-access`

### Master Data

1. `GET /api/v1/tenants/`
2. `GET /api/v1/tenants/{tenant_id}`
3. `POST /api/v1/tenants/`
4. `GET /api/v1/sppg/`
5. `GET /api/v1/sppg/{sppg_id}`
6. `POST /api/v1/sppg/`
7. `GET /api/v1/programs/`
8. `GET /api/v1/programs/{program_id}`
9. `POST /api/v1/programs/`
10. `POST /api/v1/programs/{program_id}/periods`
11. `POST /api/v1/programs/{program_id}/tenants`
12. `POST /api/v1/programs/{program_id}/sppg`
13. `GET /api/v1/quality/inspections/`
14. `GET /api/v1/quality/inspections/{inspection_id}`
15. `POST /api/v1/quality/inspections/`
16. `POST /api/v1/quality/inspections/{inspection_id}/lines`
17. `POST /api/v1/quality/inspections/{inspection_id}/finalize`
18. `GET /api/v1/workflows/definitions`
19. `GET /api/v1/workflows/definitions/{definition_id}`
20. `POST /api/v1/workflows/definitions`
21. `POST /api/v1/workflows/definitions/{definition_id}/transitions`
22. `GET /api/v1/workflows/documents/{document_type}/{document_id}`
23. `GET /api/v1/audit/events/`
24. `GET /api/v1/audit/events/{event_id}`
25. `GET /api/v1/geography/schools/`
26. `GET /api/v1/geography/schools/{school_id}`
27. `POST /api/v1/geography/schools/`
28. `GET /api/v1/beneficiaries/`
29. `GET /api/v1/beneficiaries/{beneficiary_id}`
30. `POST /api/v1/beneficiaries/`
31. `GET /api/v1/uoms/`
32. `GET /api/v1/uoms/{uom_id}`
33. `POST /api/v1/uoms/`
34. `GET /api/v1/products/`
35. `GET /api/v1/products/{product_id}`
36. `POST /api/v1/products/`
37. `GET /api/v1/recipes/`
38. `GET /api/v1/recipes/{recipe_id}`
39. `POST /api/v1/recipes/`
40. `GET /api/v1/recipes/{recipe_id}/lines`
41. `POST /api/v1/recipes/{recipe_id}/lines`

### Meal Plan

1. `GET /api/v1/meal-plans/`
2. `GET /api/v1/meal-plans/{meal_plan_id}`
3. `POST /api/v1/meal-plans/`
4. `POST /api/v1/meal-plans/{meal_plan_id}/submit`
5. `POST /api/v1/meal-plans/{meal_plan_id}/approve`
6. `POST /api/v1/meal-plans/{meal_plan_id}/calculate-requirements`
7. `POST /api/v1/meal-plans/{meal_plan_id}/reserve-materials`
8. `GET /api/v1/meal-plans/{meal_plan_id}/cost-preview`

### Inventory

1. `GET /api/v1/inventory/warehouses/`
2. `GET /api/v1/inventory/warehouses/{warehouse_id}`
3. `POST /api/v1/inventory/warehouses/`
4. `GET /api/v1/inventory/transactions/`
5. `POST /api/v1/inventory/transactions/`
6. `GET /api/v1/inventory/balances/`

### Procurement

1. `GET /api/v1/procurement/purchase-requests/`
2. `GET /api/v1/procurement/purchase-requests/{purchase_request_id}`
3. `POST /api/v1/procurement/purchase-requests/from-meal-plan/{meal_plan_id}`
4. `GET /api/v1/procurement/purchase-requests/goods-receipts/`
5. `GET /api/v1/procurement/purchase-requests/goods-receipts/{goods_receipt_id}`
6. `POST /api/v1/procurement/purchase-requests/goods-receipts/from-purchase-request/{purchase_request_id}`
7. `GET /api/v1/procurement/purchase-requests/supplier-invoices/`
8. `GET /api/v1/procurement/purchase-requests/supplier-invoices/{supplier_invoice_id}`
9. `POST /api/v1/procurement/purchase-requests/supplier-invoices/from-goods-receipt/{goods_receipt_id}`
10. `GET /api/v1/procurement/purchase-requests/supplier-payments/`
11. `GET /api/v1/procurement/purchase-requests/supplier-payments/{supplier_payment_id}`
12. `POST /api/v1/procurement/purchase-requests/supplier-payments/from-supplier-invoice/{supplier_invoice_id}`

### Production

1. `GET /api/v1/production-orders/`
2. `GET /api/v1/production-orders/{production_order_id}`
3. `POST /api/v1/production-orders/from-meal-plan/{meal_plan_id}`
4. `POST /api/v1/production-orders/{production_order_id}/complete`
5. `GET /api/v1/production-orders/{production_order_id}/cost-sheet`

### Delivery

1. `GET /api/v1/delivery-orders/`
2. `GET /api/v1/delivery-orders/{delivery_order_id}`
3. `POST /api/v1/delivery-orders/from-production-order/{production_order_id}`
4. `POST /api/v1/delivery-orders/{delivery_order_id}/proof`

### Accounting

1. `GET /api/v1/accounts`
2. `POST /api/v1/accounts`
3. `GET /api/v1/journal-entries`
4. `GET /api/v1/journal-entries/{journal_entry_id}`
5. `POST /api/v1/journal-entries`
6. `POST /api/v1/journal-entries/{journal_entry_id}/post`

### Budget

1. `GET /api/v1/budgets`
2. `GET /api/v1/budgets/{budget_id}`
3. `POST /api/v1/budgets`
4. `POST /api/v1/budgets/{budget_id}/submit`
5. `POST /api/v1/budgets/{budget_id}/approve`
6. `GET /api/v1/budgets/{budget_id}/availability`

## Authentication

Backend memakai bearer token JWT.

1. Login ke `POST /api/v1/identity/login`
2. Ambil `data.access_token`
3. Kirim header:

```http
Authorization: Bearer <access_token>
```

Endpoint write saat ini butuh token:

- seluruh `POST` selain `/api/v1/identity/login`
- `GET /api/v1/identity/me`

## Standard JSON Response

### Success Envelope

```json
{
  "success": true,
  "code": "SOME_SUCCESS_CODE",
  "message": "Human readable message",
  "data": {},
  "meta": {
    "timestamp": "2026-07-19T14:28:44.668195+00:00",
    "request_id": "uuid"
  }
}
```

### Error Envelope

```json
{
  "success": false,
  "code": "SOME_ERROR_CODE",
  "message": "Human readable message",
  "errors": [],
  "meta": {
    "timestamp": "2026-07-19T14:28:44.668195+00:00",
    "request_id": "uuid"
  }
}
```

## Common Error Codes

| HTTP | Code | Arti |
|---|---|---|
| `401` | `AUTHENTICATION_REQUIRED` | Token belum dikirim |
| `401` | `INVALID_ACCESS_TOKEN` | Token invalid atau expired |
| `403` | `INSUFFICIENT_ROLE` | Role user tidak cukup |
| `404` | `TENANT_NOT_FOUND` | Tenant tidak ditemukan |
| `404` | `SPPG_NOT_FOUND` | SPPG tidak ditemukan |
| `404` | `SCHOOL_NOT_FOUND` | Sekolah tidak ditemukan |
| `404` | `BENEFICIARY_NOT_FOUND` | Beneficiary tidak ditemukan |
| `404` | `UOM_NOT_FOUND` | UoM tidak ditemukan |
| `404` | `PRODUCT_NOT_FOUND` | Produk tidak ditemukan |
| `404` | `RECIPE_NOT_FOUND` | Recipe tidak ditemukan |
| `404` | `MEAL_PLAN_NOT_FOUND` | Meal plan tidak ditemukan |
| `404` | `WAREHOUSE_NOT_FOUND` | Warehouse tidak ditemukan |
| `404` | `PURCHASE_REQUEST_NOT_FOUND` | Purchase request tidak ditemukan |
| `404` | `GOODS_RECEIPT_NOT_FOUND` | Goods receipt tidak ditemukan |
| `404` | `SUPPLIER_INVOICE_NOT_FOUND` | Supplier invoice tidak ditemukan |
| `404` | `PRODUCTION_ORDER_NOT_FOUND` | Production order tidak ditemukan |
| `404` | `DELIVERY_ORDER_NOT_FOUND` | Delivery order tidak ditemukan |
| `404` | `ACCOUNT_NOT_FOUND` | Account tidak ditemukan |
| `404` | `JOURNAL_ENTRY_NOT_FOUND` | Journal entry tidak ditemukan |
| `404` | `BUDGET_NOT_FOUND` | Budget tidak ditemukan |
| `404` | `PROGRAM_NOT_FOUND` | Program tidak ditemukan |
| `404` | `QC_INSPECTION_NOT_FOUND` | Inspeksi QC tidak ditemukan |
| `404` | `WORKFLOW_DEFINITION_NOT_FOUND` | Workflow definition tidak ditemukan |
| `404` | `WORKFLOW_INSTANCE_NOT_FOUND` | Workflow instance tidak ditemukan |
| `404` | `AUDIT_EVENT_NOT_FOUND` | Audit event tidak ditemukan |
| `409` | `TENANT_CODE_ALREADY_EXISTS` | Kode tenant sudah dipakai |
| `409` | `SPPG_CODE_ALREADY_EXISTS` | Kode SPPG sudah dipakai |
| `409` | `PROGRAM_CODE_ALREADY_EXISTS` | Kode program sudah dipakai |
| `409` | `PROGRAM_PERIOD_CODE_ALREADY_EXISTS` | Kode periode program sudah dipakai di program yang sama |
| `409` | `PROGRAM_TENANT_ALREADY_ASSIGNED` | Tenant sudah pernah diassign ke program |
| `409` | `PROGRAM_SPPG_ALREADY_ASSIGNED` | SPPG sudah pernah diassign ke program |
| `409` | `SCHOOL_CODE_ALREADY_EXISTS` | Kode sekolah sudah dipakai |
| `409` | `BENEFICIARY_EXTERNAL_REFERENCE_ALREADY_EXISTS` | External reference beneficiary sudah dipakai |
| `409` | `UOM_CODE_ALREADY_EXISTS` | Kode UoM sudah dipakai |
| `409` | `PRODUCT_CODE_ALREADY_EXISTS` | Kode produk sudah dipakai |
| `409` | `RECIPE_CODE_VERSION_ALREADY_EXISTS` | Code dan version recipe sudah dipakai |
| `409` | `ACCOUNT_CODE_ALREADY_EXISTS` | Kode account sudah dipakai |
| `409` | `WORKFLOW_DEFINITION_ALREADY_EXISTS` | Workflow definition untuk document type tenant ini sudah ada |
| `409` | `WORKFLOW_TRANSITION_ALREADY_EXISTS` | Workflow transition yang sama sudah ada |
| `400` | `QC_INSPECTION_LINES_REQUIRED` | QC belum punya line saat finalize |
| `400` | `QC_INSPECTION_ALREADY_FINALIZED` | QC sudah final |
| `400` | `QC_RESULT_STATUS_INVALID` | Status result QC bukan PASS/FAIL |
| `400` | `PRODUCTION_QC_RELEASE_BLOCKED` | Production order belum lolos QC wajib |
| `400` | `WORKFLOW_TENANT_CONTEXT_REQUIRED` | Header `X-Tenant-ID` wajib untuk baca workflow dokumen |
| `400` | `WORKFLOW_TRANSITION_NOT_ALLOWED` | Action tidak terdaftar di workflow definition |
| `400` | `WORKFLOW_INSTANCE_STATE_MISMATCH` | State workflow instance tidak cocok |
| `422` | `REQUEST_VALIDATION_ERROR` | Payload tidak valid |

## Demo Credentials

- `operator@example.com` / `mbg12345`
- `viewer@example.com` / `viewer123`

## Endpoint Details

### Health

`GET /health/live`, `GET /health/ready`, dan `GET /health/database` tidak membutuhkan token dan dipakai untuk health check aplikasi serta database.

### Identity

`POST /api/v1/identity/login`

Content type:

```http
application/x-www-form-urlencoded
```

Payload:

```text
username=operator@example.com&password=mbg12345
```

`GET /api/v1/identity/me`

Mengembalikan profil user aktif dari token saat ini.

Response penting:

- `tenant_id`
- `active_sppg_id`
- `accessible_sppg_ids`

`POST /api/v1/identity/switch-active-sppg`

Mengganti `active_sppg_id` user yang sedang login dan mengembalikan token baru.

Payload:

```json
{
  "sppg_id": "uuid"
}
```

Aturan:

- `sppg_id` harus termasuk dalam `accessible_sppg_ids` user
- setelah berhasil, frontend sebaiknya mengganti access token lama dengan token baru dari response

Error:

- `ACTIVE_SPPG_NOT_ACCESSIBLE`

Contoh response sukses:

```json
{
  "success": true,
  "code": "IDENTITY_ACTIVE_SPPG_SWITCHED",
  "message": "SPPG aktif berhasil diganti.",
  "data": {
    "access_token": "jwt-token-baru",
    "token_type": "bearer",
    "active_sppg_id": "uuid",
    "accessible_sppg_ids": ["uuid"]
  },
  "meta": {
    "path": "/api/v1/identity/switch-active-sppg",
    "method": "POST",
    "timestamp": "2026-07-19T11:40:00Z"
  }
}
```

`GET /api/v1/identity/users`

Role:

- `super_admin`
- `tenant_admin`

Mengembalikan daftar user. Bila request membawa `X-Tenant-ID`, hasil akan terfilter per tenant.

`GET /api/v1/identity/users/{user_id}`

Role:

- `super_admin`
- `tenant_admin`

Mengembalikan detail satu user admin, termasuk:

- `role_names`
- `is_active`
- `active_sppg_id`
- `accessible_sppg_ids`

`POST /api/v1/identity/users`

Role:

- `super_admin`
- `tenant_admin`

Payload:

```json
{
  "tenant_id": "uuid",
  "full_name": "QA Admin User",
  "email": "qa-admin@example.com",
  "password": "qa12345",
  "role_names": ["tenant_admin"],
  "is_active": true,
  "accessible_sppg_ids": ["uuid"],
  "active_sppg_id": "uuid"
}
```

Aturan:

- `tenant_id` harus sesuai dengan context tenant bila `X-Tenant-ID` dikirim
- `active_sppg_id` harus ada di `accessible_sppg_ids`
- email user harus unik

`PUT /api/v1/identity/users/{user_id}`

Role:

- `super_admin`
- `tenant_admin`

Payload:

```json
{
  "full_name": "QA Admin User Updated",
  "role_names": ["operations_manager"],
  "is_active": true,
  "password": null,
  "accessible_sppg_ids": ["uuid"],
  "active_sppg_id": "uuid"
}
```

Jika `password` diisi, backend akan mengganti password user.

`GET /api/v1/identity/users/{user_id}/sppg-access`

Role:

- `super_admin`
- `tenant_admin`

Mengembalikan konfigurasi akses SPPG untuk user tertentu.

Contoh response:

```json
{
  "success": true,
  "code": "IDENTITY_USER_SPPG_ACCESS_FOUND",
  "message": "Akses SPPG user berhasil diambil.",
  "data": {
    "user_id": "uuid",
    "tenant_id": "uuid",
    "active_sppg_id": "uuid",
    "accessible_sppg_ids": ["uuid"]
  },
  "meta": {
    "path": "/api/v1/identity/users/uuid/sppg-access",
    "method": "GET",
    "timestamp": "2026-07-19T11:30:00Z"
  }
}
```

`PUT /api/v1/identity/users/{user_id}/sppg-access`

Role:

- `super_admin`
- `tenant_admin`

Payload:

```json
{
  "accessible_sppg_ids": ["uuid"],
  "active_sppg_id": "uuid"
}
```

Aturan:

- semua `accessible_sppg_ids` harus milik tenant yang sama dengan user
- `active_sppg_id` harus ada di dalam `accessible_sppg_ids`
- bila context request memakai `X-SPPG-ID`, user juga harus punya akses ke SPPG itu

Error yang perlu ditangani frontend:

- `USER_SPPG_ACCESS_DENIED`
- `ACTIVE_SPPG_NOT_IN_ACCESS_LIST`
- `USER_EMAIL_ALREADY_EXISTS`

Contoh response sukses:

```json
{
  "success": true,
  "code": "IDENTITY_USER_SPPG_ACCESS_UPDATED",
  "message": "Akses SPPG user berhasil diperbarui.",
  "data": {
    "user_id": "uuid",
    "tenant_id": "uuid",
    "active_sppg_id": "uuid",
    "accessible_sppg_ids": ["uuid"]
  },
  "meta": {
    "path": "/api/v1/identity/users/uuid/sppg-access",
    "method": "PUT",
    "timestamp": "2026-07-19T11:35:00Z"
  }
}
```

### Program Management

`GET /api/v1/programs/`

Mengembalikan daftar program. Endpoint ini mendukung filter context:

- `X-Tenant-ID` untuk hanya menampilkan program yang sudah terhubung ke tenant tersebut
- `X-SPPG-ID` untuk hanya menampilkan program yang sudah terhubung ke SPPG tersebut

Contoh response item:

```json
{
  "id": "uuid",
  "code": "PRG-MBG-APBD-2026",
  "name": "Program MBG APBD 2026",
  "description": "Program bantuan gizi daerah",
  "program_type": "PUBLIC",
  "funding_source_name": "APBD Provinsi",
  "start_date": "2026-07-19",
  "end_date": "2026-12-31",
  "status": "DRAFT",
  "is_active": true,
  "created_at": "2026-07-19T10:00:00Z",
  "updated_at": "2026-07-19T10:00:00Z"
}
```

`GET /api/v1/programs/{program_id}`

Mengembalikan bundle detail program:

- `program`
- `periods`
- `tenant_assignments`
- `sppg_assignments`

Frontend bisa memakai endpoint ini sebagai halaman detail program tunggal.

`POST /api/v1/programs/`

Role:

- `super_admin`
- `tenant_admin`

Payload:

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

Error penting:

- `PROGRAM_CODE_ALREADY_EXISTS`
- `INVALID_PROGRAM_DATE_RANGE`

`POST /api/v1/programs/{program_id}/periods`

Role:

- `super_admin`
- `tenant_admin`

Payload:

```json
{
  "code": "2026-H2",
  "name": "Semester 2 2026",
  "date_start": "2026-07-19",
  "date_end": "2026-12-31",
  "status": "OPEN",
  "notes": "Periode operasional semester dua"
}
```

Error penting:

- `PROGRAM_NOT_FOUND`
- `PROGRAM_PERIOD_CODE_ALREADY_EXISTS`
- `INVALID_PROGRAM_PERIOD_DATE_RANGE`
- `PROGRAM_PERIOD_BEFORE_PROGRAM_START`
- `PROGRAM_PERIOD_AFTER_PROGRAM_END`

`POST /api/v1/programs/{program_id}/tenants`

Role:

- `super_admin`
- `tenant_admin`

Payload:

```json
{
  "tenant_id": "uuid",
  "start_date": "2026-07-19",
  "end_date": "2026-12-31",
  "is_active": true,
  "notes": "Tenant mengikuti program APBD"
}
```

Aturan:

- bila frontend mengirim `X-Tenant-ID`, maka `tenant_id` payload harus sama
- tenant tidak boleh diassign dua kali ke program yang sama

`POST /api/v1/programs/{program_id}/sppg`

Role:

- `super_admin`
- `tenant_admin`

Payload:

```json
{
  "tenant_id": "uuid",
  "sppg_id": "uuid",
  "start_date": "2026-07-19",
  "end_date": "2026-12-31",
  "is_active": true,
  "notes": "SPPG aktif pada program APBD"
}
```

Aturan:

- tenant pemilik SPPG harus sudah diassign ke program lebih dulu
- bila frontend mengirim `X-SPPG-ID`, maka `sppg_id` payload harus sama
- bila `tenant_id` dikirim, nilainya harus sama dengan tenant pemilik SPPG

Error penting:

- `PROGRAM_TENANT_ASSIGNMENT_REQUIRED`
- `PROGRAM_SPPG_TENANT_MISMATCH`
- `PROGRAM_SPPG_ALREADY_ASSIGNED`

### Quality Control

`GET /api/v1/quality/inspections/`

Mengembalikan daftar inspeksi QC. Endpoint ini mendukung context:

- `X-Tenant-ID`
- `X-SPPG-ID`

Contoh item:

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "sppg_id": "uuid",
  "inspection_number": "QC-20260719-0001",
  "inspection_type": "PRODUCTION",
  "stage": "PRODUCTION_OUTPUT",
  "reference_type": "PRODUCTION_ORDER",
  "reference_id": "uuid",
  "inspection_at": "2026-07-19T08:00:00Z",
  "inspector_name": "Petugas QC",
  "status": "DRAFT",
  "overall_result": null,
  "is_mandatory_for_release": true,
  "notes": "QC batch produksi"
}
```

`GET /api/v1/quality/inspections/{inspection_id}`

Mengembalikan bundle:

- `inspection`
- `lines`

`POST /api/v1/quality/inspections/`

Role:

- `super_admin`
- `tenant_admin`
- `operations_manager`
- `quality_officer`

Payload:

```json
{
  "tenant_id": "uuid",
  "sppg_id": "uuid",
  "inspection_type": "PRODUCTION",
  "stage": "PRODUCTION_OUTPUT",
  "reference_type": "PRODUCTION_ORDER",
  "reference_id": "uuid",
  "inspection_at": "2026-07-19T08:00:00Z",
  "inspector_name": "Petugas QC",
  "is_mandatory_for_release": true,
  "notes": "QC batch produksi"
}
```

Aturan:

- untuk `reference_type = PRODUCTION_ORDER`, referensinya harus milik tenant dan SPPG yang sama
- bila frontend mengirim `X-Tenant-ID` dan `X-SPPG-ID`, nilainya harus sama dengan payload

`POST /api/v1/quality/inspections/{inspection_id}/lines`

Payload:

```json
{
  "parameter_name": "Suhu makanan",
  "expected_value": ">=60C",
  "actual_value": "65C",
  "result_status": "PASS",
  "notes": "Aman"
}
```

Aturan:

- `result_status` hanya boleh `PASS` atau `FAIL`
- inspeksi yang sudah final tidak boleh ditambah line lagi

`POST /api/v1/quality/inspections/{inspection_id}/finalize`

Aturan:

- minimal harus ada satu line
- bila ada minimal satu line `FAIL`, maka hasil akhir inspeksi menjadi `FAILED`
- bila semua line `PASS`, hasil akhir menjadi `PASSED`
- inspection yang `is_mandatory_for_release = true` akan memblokir pembuatan delivery order dari production order bila hasilnya belum `PASSED`

### Workflow

`GET /api/v1/workflows/definitions`

Mengembalikan daftar workflow definition untuk tenant aktif. Frontend sebaiknya selalu mengirim `X-Tenant-ID`.

`GET /api/v1/workflows/definitions/{definition_id}`

Mengembalikan:

- `definition`
- `transitions`

`POST /api/v1/workflows/definitions`

Role:

- `super_admin`
- `tenant_admin`

Payload:

```json
{
  "tenant_id": "uuid",
  "code": "CUSTOM-WF-DEMO",
  "name": "Workflow Dokumen Demo",
  "document_type": "custom_document_demo",
  "initial_state": "DRAFT",
  "is_active": true
}
```

`POST /api/v1/workflows/definitions/{definition_id}/transitions`

Payload:

```json
{
  "from_state": "DRAFT",
  "action_name": "SUBMIT",
  "to_state": "SUBMITTED",
  "allowed_role": "tenant_admin",
  "requires_approval": false
}
```

`GET /api/v1/workflows/documents/{document_type}/{document_id}`

Header wajib:

```http
X-Tenant-ID: <tenant_uuid>
```

Response mengembalikan:

- `definition`
- `instance`
- `transitions`
- `history`

Implementasi saat ini sudah otomatis dipakai oleh:

- `meal_plan`
- `budget`

Artinya setiap create, submit, dan approve pada dua domain itu langsung menambah workflow history tanpa menghilangkan field `status` bisnis di tabel utamanya.

### Audit

`GET /api/v1/audit/events/`

Role:

- `super_admin`
- `tenant_admin`

Query opsional:

- `module_name`
- `event_type`

Contoh:

```text
GET /api/v1/audit/events/?module_name=meal_plan&event_type=APPROVAL
```

Response item:

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "sppg_id": "uuid",
  "actor_user_id": "uuid",
  "actor_name": "Demo Operator MBG",
  "event_type": "OPERATIONS",
  "module_name": "meal_plan",
  "action_name": "CREATE",
  "entity_type": "meal_plan",
  "entity_id": "uuid",
  "request_id": "uuid",
  "success": true,
  "ip_address": "testclient",
  "summary": "Meal plan dibuat.",
  "metadata_json": {
    "plan_date": "2026-08-03",
    "planned_portions": 10
  },
  "occurred_at": "2026-07-19T10:00:00Z"
}
```

`GET /api/v1/audit/events/{event_id}`

Mengembalikan satu event audit lengkap. Frontend admin dapat memakai endpoint ini untuk halaman detail aktivitas.

Implementasi audit saat ini sudah mencatat aksi penting pada:

- `identity`
- `meal_plan`
- `budget`
- `quality`
- `workflow`

### Meal Plan Workflow

`POST /api/v1/meal-plans/`

```json
{
  "tenant_id": "uuid",
  "sppg_id": "uuid",
  "recipe_id": "uuid",
  "plan_date": "2026-07-21",
  "meal_type": "LUNCH",
  "status": "DRAFT",
  "planned_portions": 500,
  "budget_cost_per_portion": 15000,
  "notes": "Rencana makan siang"
}
```

`POST /api/v1/meal-plans/{meal_plan_id}/submit`

Transisi status `DRAFT -> SUBMITTED`.

`POST /api/v1/meal-plans/{meal_plan_id}/approve`

Transisi status `SUBMITTED -> APPROVED`.

`POST /api/v1/meal-plans/{meal_plan_id}/calculate-requirements`

Menghasilkan kebutuhan bahan per komponen recipe.

`POST /api/v1/meal-plans/{meal_plan_id}/reserve-materials`

Reservasi stok dari `inventory_balances` dan mengubah status ke `MATERIAL_RESERVED`.

Contoh response:

```json
{
  "success": true,
  "code": "MEAL_PLAN_MATERIALS_RESERVED",
  "message": "Material meal plan berhasil direservasi.",
  "data": {
    "meal_plan_id": "uuid",
    "status": "MATERIAL_RESERVED",
    "reserved_items": [
      {
        "warehouse_id": "uuid",
        "product_id": "uuid",
        "product_code": "MAT-BERAS",
        "product_name": "Beras",
        "reserved_quantity": 5.555556,
        "uom_id": "uuid"
      }
    ]
  },
  "meta": {
    "timestamp": "2026-07-19T16:00:00+00:00",
    "request_id": "uuid",
    "total": 1
  }
}
```

`GET /api/v1/meal-plans/{meal_plan_id}/cost-preview`

Preview biaya berdasarkan `gross_quantity * product.standard_cost`.

### Inventory

`POST /api/v1/inventory/warehouses/`

```json
{
  "tenant_id": "uuid",
  "sppg_id": "uuid",
  "code": "WH-JKT-01",
  "name": "Gudang Utama",
  "warehouse_type": "MAIN",
  "location": "Area SPPG Jakarta Pusat 01",
  "is_active": true
}
```

`POST /api/v1/inventory/transactions/`

```json
{
  "tenant_id": "uuid",
  "sppg_id": "uuid",
  "transaction_type": "RECEIPT",
  "reference_type": "SEEDING",
  "reference_id": null,
  "product_id": "uuid",
  "destination_warehouse_id": "uuid",
  "quantity": 100,
  "uom_id": "uuid",
  "unit_cost": 12000,
  "transaction_at": "2026-07-19T10:00:00Z",
  "notes": "Initial stock"
}
```

`GET /api/v1/inventory/balances/`

Mengembalikan `quantity_on_hand`, `quantity_reserved`, `quantity_available`, dan `average_cost`.

### Procurement

`POST /api/v1/procurement/purchase-requests/from-meal-plan/{meal_plan_id}`

Membuat purchase request dari shortage stock meal plan.
Jika tersedia account `510000` dan ada budget `APPROVED` yang periodenya mencakup `plan_date`, endpoint ini juga otomatis menambah `reserved_amount` pada budget terkait.

Contoh response sukses:

```json
{
  "success": true,
  "code": "PURCHASE_REQUEST_CREATED",
  "message": "Purchase request berhasil dibuat dari meal plan.",
  "data": {
    "purchase_request": {
      "id": "uuid",
      "tenant_id": "uuid",
      "sppg_id": "uuid",
      "meal_plan_id": "uuid",
      "request_number": "PR-20260719-0001",
      "status": "DRAFT",
      "notes": "Generated from meal plan"
    },
    "lines": [
      {
        "id": "uuid",
        "tenant_id": "uuid",
        "purchase_request_id": "uuid",
        "product_id": "uuid",
        "uom_id": "uuid",
        "requested_quantity": 50.0,
        "shortage_quantity": 50.0,
        "estimated_unit_cost": 12000.0,
        "estimated_total_cost": 600000.0
      }
    ]
  },
  "meta": {
    "timestamp": "2026-07-19T16:10:00+00:00",
    "request_id": "uuid",
    "total": 1
  }
}
```

Efek budget:

- mencoba reserve estimasi biaya shortage ke account `510000` Biaya Bahan
- `reserved_amount` bertambah pada `budget availability`

`POST /api/v1/procurement/purchase-requests/goods-receipts/from-purchase-request/{purchase_request_id}`

```json
{
  "warehouse_id": "uuid",
  "receipt_date": "2026-07-19",
  "notes": "Received from supplier"
}
```

Aksi ini membuat goods receipt dan mem-post `RECEIPT` ke inventory.
Aksi ini juga otomatis membuat jurnal `POSTED`:

- debit `130000` Persediaan Bahan
- kredit `240000` Barang Diterima Belum Ditagih

Efek budget:

- jika sebelumnya ada `reserved_amount` dari purchase request, endpoint ini memindahkan nilainya ke `committed_amount`
- dengan demikian nilai reserved berkurang dan committed bertambah

`GET /api/v1/procurement/purchase-requests/supplier-invoices/`

Mengembalikan daftar supplier invoice yang sudah dibuat dari goods receipt.

`GET /api/v1/procurement/purchase-requests/supplier-invoices/{supplier_invoice_id}`

Mengembalikan `supplier_invoice` dan `lines`.

`POST /api/v1/procurement/purchase-requests/supplier-invoices/from-goods-receipt/{goods_receipt_id}`

Role write:

- `super_admin`
- `tenant_admin`
- `operations_manager`
- `procurement_officer`
- `finance_manager`

Payload:

```json
{
  "invoice_date": "2026-07-19",
  "due_date": "2026-07-26",
  "budget_account_id": "uuid",
  "notes": "Invoice supplier posted"
}
```

Aksi ini:

- membuat supplier invoice dari seluruh line pada goods receipt
- otomatis membuat jurnal hutang `POSTED`
- mengaktualkan `budget actual` jika `budget_account_id` dikirim dan ada budget `APPROVED` yang periodenya cocok
- saat actual diposting, nilai `committed_amount` yang relevan dilepas agar tidak dobel hitung dengan `actual_amount`

Jurnal otomatis:

- debit `240000` Barang Diterima Belum Ditagih
- kredit `210000` Hutang Supplier

Contoh response sukses:

```json
{
  "success": true,
  "code": "SUPPLIER_INVOICE_CREATED",
  "message": "Supplier invoice berhasil dibuat, budget diaktualkan, dan hutang diposting.",
  "data": {
    "supplier_invoice": {
      "id": "uuid",
      "tenant_id": "uuid",
      "sppg_id": "uuid",
      "goods_receipt_id": "uuid",
      "budget_account_id": "uuid",
      "invoice_number": "INV-20260719-0001",
      "invoice_date": "2026-07-19",
      "due_date": "2026-07-26",
      "status": "POSTED",
      "total_amount": 173333.34,
      "notes": "Invoice supplier posted"
    },
    "lines": [
      {
        "id": "uuid",
        "tenant_id": "uuid",
        "supplier_invoice_id": "uuid",
        "goods_receipt_line_id": "uuid",
        "product_id": "uuid",
        "uom_id": "uuid",
        "invoiced_quantity": 14.444445,
        "unit_price": 12000,
        "total_amount": 173333.34,
        "description": "Invoice line for goods receipt GR-20260719-0001"
      }
    ]
  },
  "meta": {
    "timestamp": "2026-07-19T16:50:00+00:00",
    "request_id": "uuid",
    "total": 1
  }
}
```

`GET /api/v1/procurement/purchase-requests/supplier-payments/`

Mengembalikan daftar supplier payment yang dibuat dari supplier invoice.

`GET /api/v1/procurement/purchase-requests/supplier-payments/{supplier_payment_id}`

Mengembalikan detail `supplier_payment`.

`POST /api/v1/procurement/purchase-requests/supplier-payments/from-supplier-invoice/{supplier_invoice_id}`

Role write:

- `super_admin`
- `tenant_admin`
- `finance_manager`

Payload:

```json
{
  "payment_date": "2026-07-19",
  "bank_account_id": "uuid",
  "notes": "Supplier payment posted"
}
```

Aksi ini:

- membuat pembayaran untuk satu supplier invoice berstatus `POSTED`
- otomatis membuat jurnal kas/bank `POSTED`
- mengubah status supplier invoice menjadi `PAID`

Jurnal otomatis:

- debit `210000` Hutang Supplier
- kredit `110000` Kas dan Bank

Contoh response sukses:

```json
{
  "success": true,
  "code": "SUPPLIER_PAYMENT_CREATED",
  "message": "Supplier payment berhasil dibuat, jurnal kas diposting, dan invoice ditandai lunas.",
  "data": {
    "supplier_payment": {
      "id": "uuid",
      "tenant_id": "uuid",
      "sppg_id": "uuid",
      "supplier_invoice_id": "uuid",
      "bank_account_id": "uuid",
      "payment_number": "PAY-20260719-0001",
      "payment_date": "2026-07-19",
      "status": "POSTED",
      "total_amount": 173333.34,
      "notes": "Supplier payment posted"
    }
  },
  "meta": {
    "path": "/api/v1/procurement/purchase-requests/supplier-payments/from-supplier-invoice/uuid",
    "method": "POST",
    "timestamp": "2026-07-19T11:30:00Z"
  }
}
```

### Production

`POST /api/v1/production-orders/from-meal-plan/{meal_plan_id}`

Membuat production order dari meal plan yang sudah `MATERIAL_RESERVED`.

`POST /api/v1/production-orders/{production_order_id}/complete`

```json
{
  "actual_portions": 100,
  "accepted_portions": 98,
  "rejected_portions": 2
}
```

Aksi ini:

- mengkonsumsi stok reserved
- mencatat `ISSUE_TO_PRODUCTION`
- menghitung `actual_total_cost`
- menghitung `actual_cost_per_portion`
- otomatis membuat jurnal `POSTED`:
- debit `510000` Biaya Bahan
- kredit `130000` Persediaan Bahan

`GET /api/v1/production-orders/{production_order_id}/cost-sheet`

Mengembalikan ringkasan biaya material aktual per production order.

### Accounting

`GET /api/v1/accounts`

Mengembalikan daftar chart of accounts yang aktif di tenant.

`POST /api/v1/accounts`

Role write:

- `super_admin`
- `tenant_admin`
- `finance_manager`

Payload:

```json
{
  "tenant_id": "uuid",
  "code": "130000",
  "name": "Persediaan Bahan",
  "category": "ASSET",
  "normal_balance": "DEBIT",
  "allow_posting": true,
  "is_active": true
}
```

`GET /api/v1/journal-entries`

Mengembalikan daftar header jurnal.

`GET /api/v1/journal-entries/{journal_entry_id}`

Mengembalikan `journal_entry` dan `lines`.

`POST /api/v1/journal-entries`

Payload:

```json
{
  "tenant_id": "uuid",
  "entry_date": "2026-07-19",
  "reference": "MANUAL-JE-001",
  "description": "Jurnal koreksi manual",
  "source_module": "accounting",
  "source_document_type": "manual_adjustment",
  "source_document_id": null,
  "lines": [
    {
      "account_id": "uuid-account-debit",
      "line_type": "DEBIT",
      "amount": 500000,
      "description": "Debit line"
    },
    {
      "account_id": "uuid-account-credit",
      "line_type": "CREDIT",
      "amount": 500000,
      "description": "Credit line"
    }
  ]
}
```

Catatan:

- total `DEBIT` dan `CREDIT` harus sama
- jurnal baru dibuat dalam status `DRAFT`

`POST /api/v1/journal-entries/{journal_entry_id}/post`

Mengubah status jurnal dari `DRAFT` menjadi `POSTED`.

Contoh response sukses:

```json
{
  "success": true,
  "code": "JOURNAL_ENTRY_POSTED",
  "message": "Journal entry berhasil diposting.",
  "data": {
    "journal_entry": {
      "id": "uuid",
      "tenant_id": "uuid",
      "entry_number": "JE-20260719-0001",
      "entry_date": "2026-07-19",
      "reference": "MANUAL-JE-001",
      "description": "Jurnal koreksi manual",
      "source_module": "accounting",
      "source_document_type": "manual_adjustment",
      "source_document_id": null,
      "status": "POSTED",
      "posted_at": "2026-07-19T16:30:00+00:00",
      "posted_by": "uuid"
    },
    "lines": []
  },
  "meta": {
    "timestamp": "2026-07-19T16:30:00+00:00",
    "request_id": "uuid",
    "total": 2
  }
}
```

### Budget

`GET /api/v1/budgets`

Mengembalikan daftar header budget.

`GET /api/v1/budgets/{budget_id}`

Mengembalikan `budget` dan `lines`.

`POST /api/v1/budgets`

Role write:

- `super_admin`
- `tenant_admin`
- `finance_manager`

Payload:

```json
{
  "tenant_id": "uuid",
  "name": "Budget Operasional Juli 2026",
  "date_start": "2026-07-01",
  "date_end": "2026-07-31",
  "version_number": 1,
  "notes": "Budget awal Juli",
  "lines": [
    {
      "category_name": "BAHAN_BAKU",
      "account_id": "uuid",
      "planned_amount": 25000000,
      "revised_amount": null,
      "control_mode": "WARNING",
      "tolerance_percentage": 0,
      "notes": "Bahan baku utama"
    }
  ]
}
```

`POST /api/v1/budgets/{budget_id}/submit`

Transisi status `DRAFT -> SUBMITTED`.

`POST /api/v1/budgets/{budget_id}/approve`

Transisi status `SUBMITTED -> APPROVED` dan menyimpan `approved_by`, `approved_at`.

`GET /api/v1/budgets/{budget_id}/availability`

Mengembalikan ringkasan budget yang tersedia per line.
Field penting untuk frontend:

- `reserved_amount`: nilai budget yang sudah direserve dari transaksi seperti purchase request
- `committed_amount`: nilai budget yang sudah menjadi komitmen
- `actual_amount`: nilai budget yang sudah direalisasikan
- `available_budget`: nilai sisa budget yang masih bisa dipakai

Contoh response:

```json
{
  "success": true,
  "code": "BUDGET_AVAILABILITY_FOUND",
  "message": "Availability budget berhasil diambil.",
  "data": {
    "budget_id": "uuid",
    "totals": {
      "effective_budget": 25000000,
      "available_budget": 25000000
    },
    "lines": [
      {
        "budget_line_id": "uuid",
        "category_name": "BAHAN_BAKU",
        "effective_budget": 25000000,
        "reserved_amount": 0,
        "committed_amount": 0,
        "actual_amount": 0,
        "available_budget": 25000000
      }
    ]
  },
  "meta": {
    "timestamp": "2026-07-19T16:35:00+00:00",
    "request_id": "uuid",
    "total": 1
  }
}
```

### Delivery

`POST /api/v1/delivery-orders/from-production-order/{production_order_id}`

```json
{
  "school_id": "uuid",
  "planned_departure": "2026-07-25T07:00:00Z",
  "planned_arrival": "2026-07-25T08:00:00Z",
  "receiver_name": "Petugas Sekolah"
}
```

`POST /api/v1/delivery-orders/{delivery_order_id}/proof`

```json
{
  "received_at": "2026-07-25T08:05:00Z",
  "receiver_name": "Petugas Sekolah",
  "receiver_gps": "-6.1702,106.8283",
  "received_portions": 100,
  "rejected_portions": 0,
  "temperature_celsius": 62.5,
  "condition_notes": "Diterima baik"
}
```

Status akhir delivery:

- `RECEIVED`
- `PARTIALLY_RECEIVED`
- `REJECTED`

## Catatan Frontend

- Gunakan `code` untuk branch logic UI, bukan `message`.
- Semua endpoint list menyertakan `meta.total`.
- Format date: `YYYY-MM-DD`.
- Format datetime: ISO 8601, contoh `2026-07-25T08:05:00Z`.
