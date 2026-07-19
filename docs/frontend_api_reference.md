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
| `409` | `TENANT_CODE_ALREADY_EXISTS` | Kode tenant sudah dipakai |
| `409` | `SPPG_CODE_ALREADY_EXISTS` | Kode SPPG sudah dipakai |
| `409` | `SCHOOL_CODE_ALREADY_EXISTS` | Kode sekolah sudah dipakai |
| `409` | `BENEFICIARY_EXTERNAL_REFERENCE_ALREADY_EXISTS` | External reference beneficiary sudah dipakai |
| `409` | `UOM_CODE_ALREADY_EXISTS` | Kode UoM sudah dipakai |
| `409` | `PRODUCT_CODE_ALREADY_EXISTS` | Kode produk sudah dipakai |
| `409` | `RECIPE_CODE_VERSION_ALREADY_EXISTS` | Code dan version recipe sudah dipakai |
| `409` | `ACCOUNT_CODE_ALREADY_EXISTS` | Kode account sudah dipakai |
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
