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
7. `GET /api/v1/geography/schools/`
8. `GET /api/v1/geography/schools/{school_id}`
9. `POST /api/v1/geography/schools/`
10. `GET /api/v1/beneficiaries/`
11. `GET /api/v1/beneficiaries/{beneficiary_id}`
12. `POST /api/v1/beneficiaries/`
13. `GET /api/v1/uoms/`
14. `GET /api/v1/uoms/{uom_id}`
15. `POST /api/v1/uoms/`
16. `GET /api/v1/products/`
17. `GET /api/v1/products/{product_id}`
18. `POST /api/v1/products/`
19. `GET /api/v1/recipes/`
20. `GET /api/v1/recipes/{recipe_id}`
21. `POST /api/v1/recipes/`
22. `GET /api/v1/recipes/{recipe_id}/lines`
23. `POST /api/v1/recipes/{recipe_id}/lines`
24. `GET /api/v1/programs/`
25. `GET /api/v1/programs/{program_id}`
26. `POST /api/v1/programs/`
27. `POST /api/v1/programs/{program_id}/periods`
28. `POST /api/v1/programs/{program_id}/tenants`
29. `POST /api/v1/programs/{program_id}/sppg`
30. `GET /api/v1/quality/inspections/`
31. `GET /api/v1/quality/inspections/{inspection_id}`
32. `POST /api/v1/quality/inspections/`
33. `POST /api/v1/quality/inspections/{inspection_id}/lines`
34. `POST /api/v1/quality/inspections/{inspection_id}/finalize`
35. `GET /api/v1/costing/policies`
36. `POST /api/v1/costing/policies`
37. `GET /api/v1/costing/production-costs/{production_order_id}`
38. `GET /api/v1/notifications/templates`
39. `POST /api/v1/notifications/templates`
40. `GET /api/v1/notifications/preferences/me`
41. `PUT /api/v1/notifications/preferences/me`
42. `GET /api/v1/notifications/inbox`
43. `POST /api/v1/notifications`
44. `GET /api/v1/notifications/{notification_id}`
45. `POST /api/v1/notifications/inbox/{recipient_id}/mark-read`
46. `GET /api/v1/government-claims`
47. `GET /api/v1/government-claims/{claim_id}`
48. `POST /api/v1/government-claims`
49. `POST /api/v1/government-claims/{claim_id}/submit`
50. `POST /api/v1/government-claims/{claim_id}/verify`
51. `POST /api/v1/government-claims/{claim_id}/adjustments`
52. `POST /api/v1/government-claims/{claim_id}/payments`
53. `GET /api/v1/funding/sources`
54. `POST /api/v1/funding/sources`
55. `GET /api/v1/funding/agreements`
56. `GET /api/v1/funding/agreements/{agreement_id}`
57. `POST /api/v1/funding/agreements`
58. `GET /api/v1/funding/disbursements`
59. `POST /api/v1/funding/agreements/{agreement_id}/disbursements`
60. `GET /api/v1/funding/repayments`
61. `POST /api/v1/funding/agreements/{agreement_id}/repayments`
62. `GET /api/v1/funding/summary`
63. `GET /api/v1/fleet/vehicle-types`
64. `POST /api/v1/fleet/vehicle-types`
65. `GET /api/v1/fleet/vehicles`
66. `GET /api/v1/fleet/vehicles/{vehicle_id}`
67. `POST /api/v1/fleet/vehicles`
68. `GET /api/v1/fleet/drivers`
69. `POST /api/v1/fleet/drivers`
70. `GET /api/v1/fleet/assignments`
71. `POST /api/v1/fleet/vehicles/{vehicle_id}/assignments`
72. `GET /api/v1/fleet/maintenances`
73. `POST /api/v1/fleet/vehicles/{vehicle_id}/maintenances`
74. `GET /api/v1/feedback/submissions`
75. `GET /api/v1/feedback/submissions/{submission_id}`
76. `POST /api/v1/feedback/submissions`
77. `GET /api/v1/feedback/complaints`
78. `POST /api/v1/feedback/complaints`
79. `GET /api/v1/feedback/service-quality-scores`
80. `POST /api/v1/feedback/service-quality-scores`
81. `GET /api/v1/feedback/summary`
82. `GET /api/v1/assets/categories`
83. `POST /api/v1/assets/categories`
84. `GET /api/v1/assets/`
85. `GET /api/v1/assets/{asset_id}`
86. `POST /api/v1/assets/`
87. `GET /api/v1/assets/assignments/`
88. `POST /api/v1/assets/{asset_id}/assignments`
89. `GET /api/v1/assets/depreciations/`
90. `POST /api/v1/assets/{asset_id}/depreciations`
91. `GET /api/v1/workforce/positions`
92. `POST /api/v1/workforce/positions`
93. `GET /api/v1/workforce/employees`
94. `GET /api/v1/workforce/employees/{employee_id}`
95. `POST /api/v1/workforce/employees`
96. `POST /api/v1/workforce/employees/{employee_id}/assignments`
97. `GET /api/v1/workforce/shifts`
98. `POST /api/v1/workforce/shifts`
99. `GET /api/v1/workforce/attendance`
100. `POST /api/v1/workforce/attendance`
101. `GET /api/v1/workforce/timesheets`
102. `POST /api/v1/workforce/timesheets`
103. `GET /api/v1/workforce/labor-costs`
104. `POST /api/v1/workforce/labor-costs`
105. `GET /api/v1/workflows/definitions`
106. `GET /api/v1/workflows/definitions/{definition_id}`
107. `POST /api/v1/workflows/definitions`
108. `POST /api/v1/workflows/definitions/{definition_id}/transitions`
109. `GET /api/v1/workflows/documents/{document_type}/{document_id}`
110. `GET /api/v1/audit/events/`
111. `GET /api/v1/audit/events/{event_id}`
112. `GET /api/v1/documents`
113. `GET /api/v1/documents/{document_id}`
114. `POST /api/v1/documents`
115. `POST /api/v1/documents/{document_id}/versions`
116. `POST /api/v1/documents/{document_id}/links`
117. `GET /api/v1/reporting/dashboard/tenant`
118. `GET /api/v1/reporting/dashboard/sppg`
119. `GET /api/v1/reporting/stock-summary`
120. `GET /api/v1/reporting/delivery-performance`
121. `GET /api/v1/reporting/budget-summary`
122. `GET /api/v1/integration/external-systems`
123. `GET /api/v1/integration/external-systems/{external_system_id}`
124. `POST /api/v1/integration/external-systems`
125. `POST /api/v1/integration/external-systems/{external_system_id}/credentials`
126. `GET /api/v1/integration/sync-logs`
127. `GET /api/v1/integration/sync-logs/{sync_log_id}`
128. `POST /api/v1/integration/sync-logs`

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
| `404` | `DOCUMENT_NOT_FOUND` | Dokumen tidak ditemukan |
| `404` | `EXTERNAL_SYSTEM_NOT_FOUND` | External system tidak ditemukan |
| `404` | `SYNC_LOG_NOT_FOUND` | Sync log tidak ditemukan |
| `404` | `COST_POLICY_NOT_FOUND` | Cost policy tidak ditemukan |
| `404` | `NOTIFICATION_TEMPLATE_NOT_FOUND` | Notification template tidak ditemukan |
| `404` | `NOTIFICATION_NOT_FOUND` | Notification tidak ditemukan |
| `404` | `NOTIFICATION_RECIPIENT_NOT_FOUND` | Inbox notification item tidak ditemukan |
| `404` | `GOVERNMENT_CLAIM_NOT_FOUND` | Government claim tidak ditemukan |
| `404` | `POSITION_NOT_FOUND` | Posisi workforce tidak ditemukan |
| `404` | `EMPLOYEE_NOT_FOUND` | Employee workforce tidak ditemukan |
| `404` | `EMPLOYEE_ASSIGNMENT_NOT_FOUND` | Assignment employee tidak ditemukan |
| `404` | `WORK_SHIFT_NOT_FOUND` | Shift kerja tidak ditemukan |
| `404` | `TIMESHEET_NOT_FOUND` | Timesheet tidak ditemukan |
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
| `409` | `DOCUMENT_LINK_ALREADY_EXISTS` | Link dokumen ke entity ini sudah ada |
| `409` | `EXTERNAL_SYSTEM_CODE_ALREADY_EXISTS` | Kode external system tenant ini sudah ada |
| `409` | `INTEGRATION_CREDENTIAL_ALREADY_EXISTS` | Nama credential untuk external system ini sudah ada |
| `409` | `SYNC_LOG_IDEMPOTENCY_CONFLICT` | idempotency key sync log sudah pernah dipakai |
| `409` | `COST_POLICY_CODE_ALREADY_EXISTS` | Kode cost policy tenant ini sudah ada |
| `409` | `NOTIFICATION_TEMPLATE_CODE_ALREADY_EXISTS` | Kode notification template tenant ini sudah ada |
| `409` | `POSITION_CODE_ALREADY_EXISTS` | Kode posisi workforce tenant ini sudah ada |
| `409` | `EMPLOYEE_CODE_ALREADY_EXISTS` | Kode employee workforce tenant ini sudah ada |
| `409` | `EMPLOYEE_ALREADY_ASSIGNED` | Employee sudah aktif di SPPG tersebut |
| `400` | `QC_INSPECTION_LINES_REQUIRED` | QC belum punya line saat finalize |
| `400` | `QC_INSPECTION_ALREADY_FINALIZED` | QC sudah final |
| `400` | `QC_RESULT_STATUS_INVALID` | Status result QC bukan PASS/FAIL |
| `400` | `PRODUCTION_QC_RELEASE_BLOCKED` | Production order belum lolos QC wajib |
| `400` | `WORKFLOW_TENANT_CONTEXT_REQUIRED` | Header `X-Tenant-ID` wajib untuk baca workflow dokumen |
| `400` | `WORKFLOW_TRANSITION_NOT_ALLOWED` | Action tidak terdaftar di workflow definition |
| `400` | `WORKFLOW_INSTANCE_STATE_MISMATCH` | State workflow instance tidak cocok |
| `400` | `DOCUMENT_OBJECT_KEY_REQUIRED` | `object_key` versi dokumen wajib diisi |
| `400` | `INTEGRATION_IDEMPOTENCY_KEY_REQUIRED` | `idempotency_key` sync log wajib diisi |
| `400` | `INVALID_COST_POLICY_DATE_RANGE` | Tanggal aktif cost policy tidak valid |
| `400` | `NOTIFICATION_RECIPIENT_REQUIRED` | Minimal satu recipient wajib diisi |
| `400` | `NOTIFICATION_RECIPIENT_ADDRESS_REQUIRED` | `recipient_address` wajib diisi bila `user_id` kosong |
| `400` | `NOTIFICATION_CHANNEL_DISABLED` | User mematikan channel notifikasi yang dipilih |
| `400` | `INVALID_CLAIM_PERIOD` | Periode government claim tidak valid |
| `400` | `CLAIM_DELIVERY_REQUIRED` | Minimal satu delivery order wajib dipilih |
| `400` | `DELIVERY_ORDER_NOT_RECEIVED` | Delivery belum memiliki proof penerimaan |
| `400` | `CLAIM_SUBMIT_INVALID_STATUS` | Status claim tidak valid untuk submit |
| `400` | `CLAIM_EMPTY_AMOUNT` | Claim belum memiliki amount yang bisa diajukan |
| `400` | `CLAIM_EVIDENCE_REQUIRED` | Claim wajib punya dokumen evidence |
| `400` | `CLAIM_VERIFY_INVALID_STATUS` | Status claim tidak valid untuk verifikasi |
| `400` | `CLAIM_PAYMENT_INVALID_STATUS` | Status claim tidak valid untuk pembayaran |
| `400` | `INVALID_CLAIM_PAYMENT_AMOUNT` | Nilai pembayaran claim tidak valid |
| `400` | `INVALID_ASSIGNMENT_DATE_RANGE` | Rentang tanggal assignment employee tidak valid |
| `400` | `INVALID_SHIFT_TIME_RANGE` | Rentang waktu shift tidak valid |
| `400` | `INVALID_ATTENDANCE_TIME_RANGE` | Rentang waktu attendance tidak valid |
| `400` | `INVALID_TIMESHEET_PERIOD` | Periode timesheet tidak valid |
| `400` | `INVALID_LABOR_COST_VALUE` | Nilai labor cost tidak valid |
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

### Master Data

`GET /api/v1/tenants/`

Mengembalikan daftar tenant.

`GET /api/v1/tenants/{tenant_id}`

Mengembalikan detail satu tenant berdasarkan `tenant_id`.

`POST /api/v1/tenants/`

Membuat tenant baru.

Payload:

```json
{
  "name": "Yayasan MBG Jawa Barat",
  "code": "MBG-JABAR",
  "description": "Tenant operasional wilayah Jawa Barat",
  "is_active": true
}
```

`GET /api/v1/sppg/`

Mengembalikan daftar SPPG aktif lintas tenant atau sesuai scope tenant.

`GET /api/v1/sppg/{sppg_id}`

Mengembalikan detail satu SPPG.

`POST /api/v1/sppg/`

Membuat SPPG baru berikut identitas lokasi dan geo tagging dasar.

Payload:

```json
{
  "tenant_id": "tenant-uuid",
  "code": "SPPG-BDG-01",
  "name": "SPPG Bandung 01",
  "address": "Jl. Asia Afrika No. 10, Bandung",
  "latitude": -6.921757,
  "longitude": 107.607611,
  "radius_km": 5,
  "is_active": true
}
```

`GET /api/v1/geography/schools/`

Mengembalikan daftar sekolah penerima manfaat berdasarkan scope tenant dan opsional SPPG.

`GET /api/v1/geography/schools/{school_id}`

Mengembalikan detail sekolah.

`POST /api/v1/geography/schools/`

Membuat master sekolah baru.

Payload:

```json
{
  "tenant_id": "tenant-uuid",
  "sppg_id": "sppg-uuid",
  "npsn": "20202020",
  "name": "SDN Merdeka 01",
  "school_level": "SD",
  "address": "Jl. Merdeka No. 1, Bandung",
  "latitude": -6.9,
  "longitude": 107.61,
  "is_active": true
}
```

`GET /api/v1/beneficiaries/`

Mengembalikan daftar beneficiary/penerima manfaat.

`GET /api/v1/beneficiaries/{beneficiary_id}`

Mengembalikan detail beneficiary.

`POST /api/v1/beneficiaries/`

Membuat beneficiary baru yang terhubung ke sekolah.

Payload:

```json
{
  "tenant_id": "tenant-uuid",
  "sppg_id": "sppg-uuid",
  "school_id": "school-uuid",
  "full_name": "Siswa Demo",
  "beneficiary_type": "STUDENT",
  "gender": "M",
  "date_of_birth": "2015-01-10",
  "classroom_name": "3A",
  "is_active": true
}
```

`GET /api/v1/uoms/`

Mengembalikan daftar unit of measure.

`GET /api/v1/uoms/{uom_id}`

Mengembalikan detail satu UoM.

`POST /api/v1/uoms/`

Membuat UoM baru.

Payload:

```json
{
  "tenant_id": "tenant-uuid",
  "code": "KG",
  "name": "Kilogram",
  "category": "WEIGHT",
  "is_active": true
}
```

`GET /api/v1/products/`

Mengembalikan daftar produk atau bahan.

`GET /api/v1/products/{product_id}`

Mengembalikan detail produk.

`POST /api/v1/products/`

Membuat master produk baru.

Payload:

```json
{
  "tenant_id": "tenant-uuid",
  "code": "BERAS-01",
  "name": "Beras Medium",
  "product_type": "RAW_MATERIAL",
  "uom_id": "uom-uuid",
  "category_name": "Bahan Pokok",
  "is_active": true
}
```

`GET /api/v1/recipes/`

Mengembalikan daftar recipe.

`GET /api/v1/recipes/{recipe_id}`

Mengembalikan detail recipe.

`POST /api/v1/recipes/`

Membuat header recipe baru.

Payload:

```json
{
  "tenant_id": "tenant-uuid",
  "code": "RCP-NASI-GORENG",
  "name": "Nasi Goreng Telur",
  "yield_portions": 100,
  "notes": "Menu sarapan",
  "is_active": true
}
```

`GET /api/v1/recipes/{recipe_id}/lines`

Mengembalikan daftar komponen recipe.

`POST /api/v1/recipes/{recipe_id}/lines`

Menambahkan komponen bahan ke recipe.

Payload:

```json
{
  "component_product_id": "product-uuid",
  "quantity": 25,
  "uom_id": "uom-uuid",
  "waste_percentage": 2.5,
  "notes": "Komponen utama"
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

### Costing

`GET /api/v1/costing/policies`

Mengembalikan daftar cost policy berdasarkan scope tenant dan opsional SPPG.

`POST /api/v1/costing/policies`

Role:

- `super_admin`
- `tenant_admin`
- `finance_manager`

Payload:

```json
{
  "tenant_id": "uuid",
  "sppg_id": "uuid",
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

`GET /api/v1/costing/production-costs/{production_order_id}`

Mengembalikan:

- actual material cost
- labor, utility, packaging, distribution, overhead, waste cost
- total actual cost
- actual cost per accepted portion
- budget cost per portion meal plan
- variance total dan variance per portion

Catatan:

- pembagi cost per portion memakai `accepted_portions`
- `labor_cost_source` bernilai `ACTUAL` bila ada `workforce.labor_cost` pada tanggal produksi yang sama
- `labor_cost_source` bernilai `POLICY` bila labor cost aktual belum ada dan sistem fallback ke `cost_policy`
- `labor_cost_source` bernilai `NONE` bila tidak ada labor cost aktual dan tidak ada policy aktif
- bila ada `cost policy` aktif pada tanggal produksi, komponen utility, packaging, distribution, overhead, waste, dan fallback labor akan ikut dihitung

### Notification

`GET /api/v1/notifications/templates`

Mengembalikan daftar template notifikasi berdasarkan scope tenant.

`POST /api/v1/notifications/templates`

Membuat template notifikasi baru. Endpoint ini dipakai frontend admin untuk menyiapkan body atau subject reusable per channel.

Payload:

```json
{
  "tenant_id": "tenant-uuid",
  "code": "NTF-MEALPLAN-APPROVAL",
  "name": "Meal Plan Approval",
  "channel": "IN_APP",
  "subject_template": "Meal plan menunggu approval",
  "body_template": "Meal plan {{meal_plan_id}} membutuhkan approval.",
  "variables_json": ["meal_plan_id"],
  "is_active": true
}
```

`GET /api/v1/notifications/preferences/me`

Mengambil preferensi notifikasi milik user aktif.

`PUT /api/v1/notifications/preferences/me`

Menyimpan preferensi notifikasi user aktif untuk satu channel.

Payload:

```json
{
  "channel": "IN_APP",
  "is_enabled": true,
  "quiet_hours_json": {
    "start": "22:00",
    "end": "05:00"
  },
  "config_json": {
    "sound": "default"
  }
}
```

`GET /api/v1/notifications/inbox`

Mengambil daftar inbox notifikasi untuk user yang sedang login. Setiap item berisi `recipient` dan `notification`.

`POST /api/v1/notifications`

Membuat notification baru lalu mendaftarkan recipient dan delivery queue.

Payload:

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

`GET /api/v1/notifications/{notification_id}`

Mengambil detail notification lengkap dengan recipient dan delivery.

`POST /api/v1/notifications/inbox/{recipient_id}/mark-read`

Menandai item inbox milik user aktif sebagai sudah dibaca.

### Government Claim

`GET /api/v1/government-claims`

Mengambil daftar government claim sesuai scope tenant dan opsional SPPG.

`GET /api/v1/government-claims/{claim_id}`

Mengambil detail government claim beserta lines, evidence, verification, adjustment, dan payment.

`POST /api/v1/government-claims`

Membuat draft government claim dari delivery order yang sudah memiliki proof penerimaan. Nilai klaim dihitung dari `received_portions * production_order.actual_cost_per_portion`, sehingga basisnya adalah biaya aktual yang sudah terealisasi.

Payload:

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

`POST /api/v1/government-claims/{claim_id}/submit`

Submit claim ke tahap pengajuan. Claim harus punya amount dan minimal satu evidence.

Payload:

```json
{
  "submitted_at": "2026-08-09"
}
```

`POST /api/v1/government-claims/{claim_id}/verify`

Mencatat hasil verifikasi pemerintah atau verifikator internal.

Payload:

```json
{
  "verification_date": "2026-08-12",
  "verification_status": "APPROVED",
  "verified_amount": 82500,
  "verifier_name": "Tim Verifikator",
  "notes": "Sesuai dokumen"
}
```

`POST /api/v1/government-claims/{claim_id}/adjustments`

Menambahkan adjustment nominal terhadap claim.

`POST /api/v1/government-claims/{claim_id}/payments`

Mencatat pembayaran claim dan otomatis membuat jurnal accounting ter-posting.

Payload:

```json
{
  "payment_date": "2026-08-15",
  "amount": 82500,
  "payment_reference": "SP2D-2026-0001",
  "notes": "Dana diterima penuh",
  "debit_account_code": "110000",
  "credit_account_code": "120500"
}
```

### Funding

`GET /api/v1/funding/sources`

Mengambil daftar funding source sesuai scope tenant aktif.

`POST /api/v1/funding/sources`

Membuat sumber pendanaan tenant seperti APBN/APBD, investor bridge fund, atau sumber lain.

Payload:

```json
{
  "tenant_id": "tenant-uuid",
  "code": "FUND-INV-001",
  "source_type": "INVESTOR_BRIDGE_FUND",
  "name": "Investor Bridge Fund Batch 1",
  "party_name": "PT Investor Demo",
  "contract_number": "PKS-2026-001",
  "start_date": "2026-07-19",
  "end_date": "2027-07-19",
  "status": "DRAFT",
  "is_active": true,
  "notes": "Skema pendanaan awal tenant"
}
```

`GET /api/v1/funding/agreements`

Mengambil daftar funding agreement tenant.

`GET /api/v1/funding/agreements/{agreement_id}`

Mengembalikan bundle:

- `agreement`
- `source`
- `disbursements`
- `repayments`
- `principal_disbursed`
- `principal_repaid`
- `outstanding_principal`
- `realized_margin`

`POST /api/v1/funding/agreements`

Membuat agreement pendanaan turunan dari funding source.

Payload:

```json
{
  "funding_source_id": "funding-source-uuid",
  "agreement_type": "MUDHARABAH",
  "principal_amount": 10000000,
  "margin_method": "PERCENTAGE",
  "margin_rate": 12,
  "fixed_margin_amount": null,
  "disbursement_schedule": {
    "phase": "single"
  },
  "repayment_terms": {
    "tenor_months": 6
  },
  "status": "DRAFT",
  "notes": "Perjanjian pendanaan awal"
}
```

`GET /api/v1/funding/disbursements`

Mengambil daftar pencairan dana tenant.

`POST /api/v1/funding/agreements/{agreement_id}/disbursements`

Mencatat pencairan principal dan otomatis membuat jurnal `POSTED`.

Payload:

```json
{
  "sppg_id": "sppg-uuid",
  "disbursement_date": "2026-07-19",
  "amount": 4000000,
  "bank_account_id": null,
  "reference_number": "FDB-2026-0001",
  "status": "POSTED",
  "notes": "Pencairan tahap pertama",
  "debit_account_code": "110000",
  "credit_account_code": "230500"
}
```

`GET /api/v1/funding/repayments`

Mengambil daftar pengembalian funding tenant.

`POST /api/v1/funding/agreements/{agreement_id}/repayments`

Mencatat pengembalian principal, margin, dan penalty. Backend otomatis membuat jurnal `POSTED`.

Payload:

```json
{
  "repayment_date": "2026-08-19",
  "principal_amount": 1500000,
  "margin_amount": 150000,
  "penalty_amount": 0,
  "payment_reference": "FRP-2026-0001",
  "status": "POSTED",
  "notes": "Pembayaran cicilan pertama",
  "debit_account_code": "230500",
  "credit_account_code": "110000"
}
```

`GET /api/v1/funding/summary`

Mengembalikan ringkasan tenant:

- total funding source
- total funding agreement
- principal committed
- principal disbursed
- principal repaid
- outstanding principal
- realized margin
- breakdown agreement aktif/closed

Frontend sebaiknya mengirim `X-Tenant-ID` untuk hasil yang spesifik tenant.

### Fleet

`GET /api/v1/fleet/vehicle-types`

Mengambil daftar tipe kendaraan per tenant.

`POST /api/v1/fleet/vehicle-types`

Membuat master tipe kendaraan.

Payload:

```json
{
  "tenant_id": "tenant-uuid",
  "code": "VAN-COLD",
  "name": "Van Pendingin",
  "description": "Kendaraan berpendingin untuk distribusi makanan",
  "capacity_portions": 1200,
  "capacity_kg": 850,
  "temperature_controlled": true,
  "is_active": true
}
```

`GET /api/v1/fleet/vehicles`

Mengambil daftar kendaraan sesuai scope tenant dan opsional `X-SPPG-ID`.

`GET /api/v1/fleet/vehicles/{vehicle_id}`

Mengembalikan bundle:

- `vehicle`
- `assignments`
- `maintenances`

`POST /api/v1/fleet/vehicles`

Membuat master kendaraan.

Payload:

```json
{
  "tenant_id": "tenant-uuid",
  "home_sppg_id": "sppg-uuid",
  "vehicle_type_id": "vehicle-type-uuid",
  "vehicle_code": "VH-001",
  "plate_number": "B 1234 MBG",
  "ownership_status": "OWNED",
  "brand_name": "Toyota",
  "model_name": "HiAce",
  "manufacture_year": 2024,
  "capacity_portions": 1000,
  "fuel_type": "DIESEL",
  "status": "ACTIVE",
  "is_active": true,
  "notes": "Unit distribusi utama"
}
```

`GET /api/v1/fleet/drivers`

Mengambil daftar driver tenant.

`POST /api/v1/fleet/drivers`

Membuat master driver.

Payload:

```json
{
  "tenant_id": "tenant-uuid",
  "driver_code": "DRV-001",
  "full_name": "Agus Supir",
  "phone_number": "081234567890",
  "license_number": "SIMB-00112233",
  "license_type": "B1",
  "license_expiry_date": "2027-07-19",
  "status": "ACTIVE",
  "is_active": true,
  "notes": "Driver distribusi utama"
}
```

`GET /api/v1/fleet/assignments`

Mengambil daftar assignment kendaraan ke SPPG.

`POST /api/v1/fleet/vehicles/{vehicle_id}/assignments`

Menugaskan kendaraan ke SPPG dan opsional ke driver.

Payload:

```json
{
  "sppg_id": "sppg-uuid",
  "driver_id": "driver-uuid",
  "assignment_date": "2026-07-19",
  "end_date": null,
  "assignment_role": "DELIVERY",
  "status": "ASSIGNED",
  "is_active": true,
  "notes": "Unit aktif untuk distribusi pagi"
}
```

`GET /api/v1/fleet/maintenances`

Mengambil daftar maintenance kendaraan.

`POST /api/v1/fleet/vehicles/{vehicle_id}/maintenances`

Mencatat maintenance kendaraan.

Payload:

```json
{
  "sppg_id": "sppg-uuid",
  "maintenance_date": "2026-07-19",
  "maintenance_type": "SERVICE_BERKALA",
  "odometer_km": 15250,
  "cost_amount": 1250000,
  "vendor_name": "Bengkel Armada Sejahtera",
  "status": "COMPLETED",
  "notes": "Ganti oli dan pengecekan rem"
}
```

Frontend sebaiknya mengirim `X-Tenant-ID` untuk semua operasi fleet, dan `X-SPPG-ID` saat ingin membatasi kendaraan/assignment/maintenance pada satu dapur tertentu.

### Feedback

`GET /api/v1/feedback/submissions`

Mengambil daftar feedback submission sesuai scope tenant dan opsional SPPG.

`GET /api/v1/feedback/submissions/{submission_id}`

Mengembalikan bundle:

- `submission`
- `items`
- `complaints`

`POST /api/v1/feedback/submissions`

Membuat feedback submission lengkap dengan item penilaian detail.

Payload:

```json
{
  "tenant_id": "tenant-uuid",
  "sppg_id": "sppg-uuid",
  "school_id": "school-uuid",
  "meal_plan_id": "meal-plan-uuid",
  "delivery_order_id": "delivery-order-uuid",
  "feedback_date": "2026-07-19",
  "source_type": "SCHOOL",
  "respondent_name": "Ibu Rina",
  "respondent_role": "KEPALA_SEKOLAH",
  "overall_rating": 88,
  "acceptance_rate": 92,
  "food_waste_portions": 4,
  "delivery_timeliness_rating": 90,
  "temperature_rating": 85,
  "comment_text": "Menu diterima baik oleh siswa",
  "status": "SUBMITTED",
  "items": [
    {
      "item_type": "TASTE",
      "metric_name": "taste_rating",
      "score": 89,
      "sentiment": "POSITIVE",
      "comment_text": "Rasa cukup enak"
    }
  ]
}
```

`GET /api/v1/feedback/complaints`

Mengambil daftar complaint sesuai scope tenant dan SPPG.

`POST /api/v1/feedback/complaints`

Mencatat complaint operasional atau kualitas layanan.

Payload:

```json
{
  "feedback_submission_id": "feedback-submission-uuid",
  "complaint_date": "2026-07-19T09:30:00",
  "category": "TEMPERATURE",
  "severity": "MEDIUM",
  "complaint_text": "Makanan tiba dalam kondisi kurang hangat.",
  "resolution_status": "OPEN",
  "resolved_at": null,
  "notes": "Perlu evaluasi proses loading"
}
```

`GET /api/v1/feedback/service-quality-scores`

Mengambil daftar service quality score.

`POST /api/v1/feedback/service-quality-scores`

Mencatat indeks kualitas layanan per tanggal dan SPPG.

Payload:

```json
{
  "tenant_id": "tenant-uuid",
  "sppg_id": "sppg-uuid",
  "score_date": "2026-07-19",
  "acceptance_score": 92,
  "waste_score": 88,
  "delivery_score": 90,
  "temperature_score": 85,
  "taste_score": 89,
  "nutrition_score": 91,
  "complaint_score": 80,
  "total_score": 87.857143,
  "score_status": "CALCULATED",
  "notes": "SQI harian"
}
```

`GET /api/v1/feedback/summary`

Mengembalikan ringkasan:

- jumlah submission
- jumlah complaint
- jumlah service quality score
- rata-rata overall rating
- rata-rata acceptance rate
- rata-rata food waste
- rata-rata service quality score
- complaint open/resolved/high severity

Frontend sebaiknya mengirim `X-Tenant-ID` untuk seluruh endpoint feedback dan `X-SPPG-ID` untuk data level dapur.

### Asset

`GET /api/v1/assets/categories`

Mengambil daftar kategori asset tenant.

`POST /api/v1/assets/categories`

Membuat master kategori asset dan akun-akun default depresiasi.

Payload:

```json
{
  "tenant_id": "tenant-uuid",
  "code": "EQP",
  "name": "Peralatan Dapur",
  "asset_account_id": "asset-account-uuid",
  "depreciation_expense_account_id": "expense-account-uuid",
  "accumulated_depreciation_account_id": "contra-account-uuid",
  "useful_life_months": 60,
  "depreciation_method": "STRAIGHT_LINE",
  "is_active": true
}
```

`GET /api/v1/assets/`

Mengambil daftar asset sesuai scope tenant dan opsional `X-SPPG-ID`.

`GET /api/v1/assets/{asset_id}`

Mengembalikan bundle:

- `asset`
- `assignments`
- `depreciations`

`POST /api/v1/assets/`

Membuat asset register.

Payload:

```json
{
  "tenant_id": "tenant-uuid",
  "sppg_id": "sppg-uuid",
  "asset_category_id": "asset-category-uuid",
  "asset_code": "AST-001",
  "asset_name": "Oven Industri",
  "acquisition_date": "2026-07-19",
  "acquisition_cost": 24000000,
  "residual_value": 2000000,
  "useful_life_months": 60,
  "depreciation_method": "STRAIGHT_LINE",
  "status": "ACTIVE",
  "serial_number": "OVN-2026-001",
  "condition_status": "GOOD",
  "location_name": "Dapur Utama",
  "is_active": true,
  "notes": "Asset produksi utama"
}
```

`GET /api/v1/assets/assignments/`

Mengambil daftar assignment asset.

`POST /api/v1/assets/{asset_id}/assignments`

Menempatkan asset ke SPPG atau PIC operasional tertentu.

Payload:

```json
{
  "sppg_id": "sppg-uuid",
  "assigned_to_name": "Koordinator Produksi",
  "assignment_date": "2026-07-19",
  "end_date": null,
  "assignment_role": "OPERATIONAL",
  "status": "ASSIGNED",
  "is_active": true,
  "notes": "Dipakai untuk lini produksi utama"
}
```

`GET /api/v1/assets/depreciations/`

Mengambil daftar depresiasi asset.

`POST /api/v1/assets/{asset_id}/depreciations`

Mencatat depresiasi asset dan otomatis membuat jurnal `POSTED`.

Payload:

```json
{
  "depreciation_date": "2026-07-31",
  "depreciation_amount": 366666.666667,
  "debit_account_code": "520100",
  "credit_account_code": "170100",
  "status": "POSTED",
  "notes": "Depresiasi bulan Juli 2026"
}
```

Jika `depreciation_amount` tidak dikirim, backend menghitung nilai straight-line dari `acquisition_cost - residual_value` dibagi `useful_life_months`.

Frontend sebaiknya selalu mengirim `X-Tenant-ID` untuk modul asset dan `X-SPPG-ID` saat bekerja pada asset spesifik dapur.

### Workforce

`GET /api/v1/workforce/positions`

Mengambil daftar posisi kerja per tenant.

`POST /api/v1/workforce/positions`

Membuat master posisi kerja.

`GET /api/v1/workforce/employees`

Mengambil daftar employee sesuai scope tenant dan opsional SPPG.

`GET /api/v1/workforce/employees/{employee_id}`

Mengambil detail employee beserta assignment ke SPPG.

`POST /api/v1/workforce/employees`

Membuat employee baru.

Payload:

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

`POST /api/v1/workforce/employees/{employee_id}/assignments`

Menempatkan employee ke SPPG dalam rentang periode tertentu.

`GET /api/v1/workforce/shifts`

Mengambil daftar shift kerja.

`POST /api/v1/workforce/shifts`

Membuat jadwal shift kerja.

`GET /api/v1/workforce/attendance`

Mengambil daftar attendance.

`POST /api/v1/workforce/attendance`

Mencatat attendance dan menghitung `worked_hours` otomatis bila `check_in_at` dan `check_out_at` diisi.

`GET /api/v1/workforce/timesheets`

Mengambil daftar timesheet.

`POST /api/v1/workforce/timesheets`

Membuat timesheet periodik untuk employee.

`GET /api/v1/workforce/labor-costs`

Mengambil daftar labor cost.

`POST /api/v1/workforce/labor-costs`

Mencatat biaya tenaga kerja aktual. `total_cost` dihitung dari `hours_worked * hourly_rate`.
- variance dibandingkan terhadap `meal_plan.budget_cost_per_portion`

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

### Document Management

`GET /api/v1/documents`

Mengembalikan daftar dokumen berdasarkan scope `X-Tenant-ID` dan opsional `X-SPPG-ID`.

`GET /api/v1/documents/{document_id}`

Mengembalikan bundle:

- `document`
- `versions`
- `links`

`POST /api/v1/documents`

Role:

- `super_admin`
- `tenant_admin`
- `operations_manager`
- `quality_officer`
- `finance_manager`

Payload:

```json
{
  "tenant_id": "uuid",
  "sppg_id": "uuid",
  "document_type": "QC_ATTACHMENT",
  "title": "Checklist QC Batch 1",
  "description": "Lampiran checklist quality control",
  "owner_entity_type": "meal_plan",
  "owner_entity_id": "uuid",
  "tags": ["qc", "checklist"]
}
```

`POST /api/v1/documents/{document_id}/versions`

Payload:

```json
{
  "file_name": "qc-checklist-20260719.pdf",
  "file_mime_type": "application/pdf",
  "file_size_bytes": 204800,
  "checksum_sha256": "abc123checksum",
  "storage_backend": "LOCAL",
  "object_key": "documents/qc/qc-checklist-20260719.pdf",
  "version_notes": "Versi awal",
  "metadata_json": {
    "source": "manual-upload"
  },
  "uploaded_at": "2026-07-19T10:30:00Z"
}
```

`POST /api/v1/documents/{document_id}/links`

Payload:

```json
{
  "linked_entity_type": "meal_plan",
  "linked_entity_id": "uuid",
  "relation_type": "ATTACHMENT"
}
```

Implementasi saat ini menyimpan metadata database dan `object_key` saja. Jadi backend sudah siap dipakai baik untuk local storage, MinIO, maupun S3-compatible storage tanpa mengubah kontrak API metadata.

### Reporting

`GET /api/v1/reporting/dashboard/tenant`

Mengembalikan ringkasan tenant:

- total meal plan
- total budget
- total production order
- total delivery order
- total document
- total employee
- status operasional utama
- ringkasan finance termasuk `approved_budget_amount`, `actual_budget_amount`, dan `actual_labor_cost_amount`
- ringkasan governance seperti workflow dan audit

Contoh struktur response `data`:

```json
{
  "totals": {
    "meal_plans": 12,
    "budgets": 2,
    "production_orders": 10,
    "delivery_orders": 10,
    "documents": 25,
    "employees": 8
  },
  "statuses": {
    "meal_plan_approved": 9,
    "meal_plan_material_reserved": 8,
    "budget_approved": 2,
    "delivery_received": 10
  },
  "finance": {
    "approved_budget_amount": 250000000,
    "actual_budget_amount": 120500000,
    "actual_labor_cost_amount": 18500000
  },
  "governance": {
    "workflow_instances": 14,
    "audit_events": 320
  }
}
```

Frontend sebaiknya mengirim `X-Tenant-ID`.

`GET /api/v1/reporting/dashboard/sppg`

Mengembalikan ringkasan level SPPG:

- produksi
- delivery
- quality
- stok
- workforce

Contoh struktur response `data`:

```json
{
  "totals": {
    "production_orders": 10,
    "delivery_orders": 10,
    "qc_inspections": 10
  },
  "production": {
    "completed_orders": 10,
    "accepted_portions": 1200,
    "rejected_portions": 15
  },
  "delivery": {
    "received_orders": 10,
    "partially_received_orders": 1,
    "received_portions": 1185
  },
  "quality": {
    "passed_inspections": 9,
    "failed_inspections": 1
  },
  "stock": {
    "quantity_on_hand": 89202.222215,
    "quantity_available": 89127.777776
  },
  "workforce": {
    "attendance_records": 35,
    "worked_hours": 271.5,
    "labor_cost_amount": 5425000
  }
}
```

Frontend sebaiknya mengirim `X-Tenant-ID` dan `X-SPPG-ID`.

`GET /api/v1/reporting/stock-summary`

Mengembalikan:

- total stok on hand
- total reserved
- total available
- `top_items` berdasarkan kuantitas on hand

`GET /api/v1/reporting/delivery-performance`

Mengembalikan:

- total delivery order
- total shipped/received/rejected portions
- breakdown status delivery

`GET /api/v1/reporting/budget-summary`

Mengembalikan:

- total effective budget
- reserved/committed/actual amount
- breakdown status budget

Catatan:

- read model ini masih dihitung langsung dari tabel transaksi
- belum menggunakan materialized view atau cached summary table
- cocok untuk dashboard internal tahap awal, lalu bisa dioptimasi pada fase reporting berikutnya

### Integration

`GET /api/v1/integration/external-systems`

Mengembalikan daftar external system untuk tenant aktif.

`GET /api/v1/integration/external-systems/{external_system_id}`

Mengembalikan bundle:

- `external_system`
- `credentials`

`POST /api/v1/integration/external-systems`

Role:

- `super_admin`
- `tenant_admin`

Payload:

```json
{
  "tenant_id": "uuid",
  "code": "EXT-PARTNER-ERP",
  "name": "Partner ERP Demo",
  "system_type": "ERP",
  "base_url": "https://partner.example.com/api",
  "is_active": true,
  "notes": "Sistem partner demo"
}
```

`POST /api/v1/integration/external-systems/{external_system_id}/credentials`

Payload:

```json
{
  "credential_name": "primary-api-key",
  "credential_type": "API_KEY",
  "secret_masked": "****demo",
  "config_json": {
    "header_name": "X-API-Key"
  },
  "is_active": true
}
```

`GET /api/v1/integration/sync-logs`

Role:

- `super_admin`
- `tenant_admin`

Query opsional:

- `external_system_id`
- `direction`

`POST /api/v1/integration/sync-logs`

Payload:

```json
{
  "external_system_id": "uuid",
  "direction": "OUTBOUND",
  "message_type": "meal_plan.export",
  "entity_type": "meal_plan",
  "entity_id": null,
  "external_reference": "REF-ERP-001",
  "idempotency_key": "idem-mealplan-001",
  "status": "PENDING",
  "payload_json": {
    "sample": true
  },
  "response_json": {},
  "processed_at": null,
  "notes": "Sinkronisasi awal"
}
```

Aturan penting:

- setiap sync log wajib memiliki `idempotency_key`
- kombinasi tenant + external system + idempotency key harus unik
- fondasi ini belum mengirim request HTTP sungguhan; yang dibangun sekarang adalah metadata integrasi, credential metadata, dan jejak sinkronisasi yang aman

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
