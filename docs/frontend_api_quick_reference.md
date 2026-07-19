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
| `GET` | `/api/v1/tenants/` | No | - | List tenant |
| `GET` | `/api/v1/sppg/` | No | - | List SPPG |
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
| `INSUFFICIENT_STOCK_FOR_MEAL_PLAN` | Tampilkan shortage dan arahkan ke procurement |
| `NO_SHORTAGE_FOR_PURCHASE_REQUEST` | Info bahwa stok sudah cukup |
| `MEAL_PLAN_NOT_READY_FOR_PRODUCTION` | Minta user reserve material dulu |
| `PRODUCTION_ORDER_NOT_READY_FOR_DELIVERY` | Minta user selesaikan produksi dulu |
| `DELIVERY_RECEIPT_EXCEEDS_SHIPPED` | Validasi form proof delivery |
| `JOURNAL_ENTRY_NOT_BALANCED` | Minta user samakan total debit dan credit |
| `JOURNAL_ENTRY_POST_INVALID_STATUS` | Nonaktifkan tombol post bila status bukan `DRAFT` |
| `BUDGET_SUBMIT_INVALID_STATUS` | Nonaktifkan submit bila budget bukan `DRAFT` |
| `BUDGET_APPROVE_INVALID_STATUS` | Nonaktifkan approve bila budget bukan `SUBMITTED` |
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
