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
| `GET` | `/api/v1/production-orders/` | No | - | List production order |
| `POST` | `/api/v1/production-orders/from-meal-plan/{meal_plan_id}` | Yes | `super_admin`, `tenant_admin`, `operations_manager` | Buat production order |
| `POST` | `/api/v1/production-orders/{production_order_id}/complete` | Yes | `super_admin`, `tenant_admin`, `operations_manager` | Selesaikan produksi |
| `GET` | `/api/v1/production-orders/{production_order_id}/cost-sheet` | No | - | Lihat actual cost produksi |
| `GET` | `/api/v1/delivery-orders/` | No | - | List delivery order |
| `POST` | `/api/v1/delivery-orders/from-production-order/{production_order_id}` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `delivery_officer` | Buat delivery order |
| `POST` | `/api/v1/delivery-orders/{delivery_order_id}/proof` | Yes | `super_admin`, `tenant_admin`, `operations_manager`, `delivery_officer` | Catat proof of delivery |

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

## Example Requests

### Create Goods Receipt

```json
{
  "warehouse_id": "{{warehouse_id}}",
  "receipt_date": "2026-07-19",
  "notes": "Received from supplier"
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
