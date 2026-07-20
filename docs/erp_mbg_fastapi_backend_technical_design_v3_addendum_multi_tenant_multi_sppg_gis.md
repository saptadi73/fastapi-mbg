# ERP MBG FastAPI Backend Technical Design v3 Addendum

## Multi-Tenant, Multi-SPPG, dan GIS Scope

Dokumen addendum ini melengkapi `erp_mbg_fastapi_backend_technical_design_v3_multi_tenant_multi_sppg.md` dan menjadi referensi keputusan desain terbaru untuk implementasi backend.

**Tanggal pembaruan:** 2026-07-20
**Status:** berlaku untuk implementasi backend saat ini dan tahap refactor berikutnya

---

# 1. Keputusan Desain Inti

Keputusan desain yang harus dianggap final:

* satu `tenant` dapat memiliki banyak `sppg`
* satu `sppg` hanya dimiliki oleh satu `tenant`
* setiap `sppg` wajib memiliki data lokasi GPS
* transaksi operasional berjalan pada scope `tenant_id` dan `sppg_id`
* user berada pada satu tenant, tetapi dapat diberi akses ke satu atau beberapa SPPG

Model relasi utamanya:

```text
Tenant 1 --- N SPPG
Tenant 1 --- N User
User N --- N SPPG
Program N --- N Tenant
Program N --- N SPPG
```

---

# 2. SPPG sebagai Unit Operasional

`SPPG` adalah unit operasional utama sistem. Istilah `Kitchen` dan `SPPG` untuk implementasi backend diperlakukan sebagai entitas yang sama, dengan nama teknis yang direkomendasikan adalah `sppg`.

Semua transaksi berikut wajib terkait ke `sppg_id`:

* warehouse
* inventory transaction
* inventory balance
* meal plan
* purchase request
* goods receipt
* supplier invoice
* supplier payment
* production order
* delivery order
* costing
* budget operasional level dapur

Pengecualian hanya berlaku untuk data yang memang sah berada pada level tenant, misalnya:

* tenant master
* user tenant
* chart of account tenant
* budget korporat level tenant

---

# 3. Data Wajib pada SPPG

Minimal field yang wajib dimiliki model `sppg`:

```text
id
tenant_id
regional_id
code
name
address
province_id
city_id
district_id
village_id
latitude
longitude
service_radius_meter
timezone
is_active
```

Untuk kebutuhan GIS dan spatial query, tambahkan field:

```text
geom
```

Rekomendasi tipe PostgreSQL/PostGIS:

```sql
GEOGRAPHY(Point, 4326)
```

atau:

```sql
Geometry(Point, 4326)
```

`geom` harus konsisten dengan nilai `latitude` dan `longitude`.

---

# 4. Scope Akses User

Setiap user wajib memiliki `tenant_id`.

Untuk akses SPPG, backend v3 harus mendukung salah satu atau kedua pola berikut:

1. `default_sppg_id` atau `active_sppg_id` pada user/JWT
2. tabel relasi `user_sppg`

Aturan akses:

* user tidak boleh mengakses data tenant lain
* user tidak boleh mengakses data SPPG di luar tenant-nya
* bila user dibatasi pada beberapa SPPG saja, endpoint operasional harus memvalidasi `sppg_id` terhadap daftar akses user

Claim JWT yang direkomendasikan:

```json
{
  "sub": "user-id",
  "tenant_id": "tenant-id",
  "active_sppg_id": "sppg-id",
  "roles": ["tenant_admin", "operations_manager"]
}
```

---

# 5. Aturan Query dan Repository

Standar implementasi repository:

* `list` tidak boleh default lintas tenant
* semua `list` minimal memakai filter `tenant_id`
* endpoint operasional berbasis dapur sebaiknya mendukung filter `sppg_id`
* `get_by_id` untuk entity tenant-owned sebaiknya punya validasi tenant
* entity yang direferensikan lintas modul harus dicek konsistensi `tenant_id` dan, bila relevan, `sppg_id`

Contoh aturan validasi:

* `warehouse.sppg_id` harus milik tenant yang sama
* `purchase_request.sppg_id` harus sama dengan `meal_plan.sppg_id`
* `goods_receipt.sppg_id` harus sama dengan `purchase_request.sppg_id`
* `delivery_order.sppg_id` harus sama dengan `production_order.sppg_id`

---

# 6. Dampak ke Backend Saat Ini

Kondisi implementasi saat addendum ini dibuat:

* banyak tabel operasional sudah memiliki `sppg_id`
* model `sppg` baru menyimpan `city`, `latitude`, dan `longitude`
* middleware tenancy baru membaca `X-Tenant-ID`
* pembatasan `X-SPPG-ID` atau `active_sppg_id` belum diterapkan menyeluruh
* query list di beberapa modul masih belum tenant-aware secara konsisten

Artinya, fondasi multi-SPPG sudah ada, tetapi enforcement scope dan metadata GIS masih perlu dirapikan.

---

# 7. Pembaruan Implementasi per 20 Juli 2026

Status implementasi backend saat ini yang sudah tersedia:

* middleware tenancy sudah menormalisasi placeholder header seperti `undefined`, `null`, `none`, dan string kosong agar tidak memicu scope error palsu
* endpoint GIS utama untuk coverage, service area, rute distribusi, dan heatmap sudah tersedia
* modul Fleet sudah memiliki master `vehicle_type`, `vehicle`, `driver`, `vehicle_assignment`, dan `vehicle_maintenance`
* backend kini memiliki tracking lokasi armada melalui tabel `vehicle_locations`
* endpoint fleet live tracking yang tersedia:
  * `GET /api/v1/fleet/vehicle-locations/live`
  * `GET /api/v1/fleet/vehicles/{vehicle_id}/locations`
  * `POST /api/v1/fleet/vehicles/{vehicle_id}/locations`
* detail kendaraan sekarang dapat mengembalikan `current_location` dan `recent_locations`

Tracking armada ini menjadi penghubung operasional antara domain Fleet, GIS, dan Delivery:

* Fleet menyimpan identitas kendaraan, driver, assignment, maintenance, dan histori GPS
* GIS memakai koordinat kendaraan untuk peta armada aktif, status pergerakan, dan dispatch board
* Delivery tetap menjadi pemilik delivery order, route, stop, proof, dan incident

---

# 8. Urutan Implementasi yang Direkomendasikan

1. Lengkapi model dan schema `sppg`.
2. Tambahkan migration field lokasi dan GIS.
3. Tambahkan `X-SPPG-ID` atau `active_sppg_id` pada auth context.
4. Rapikan repository agar tenant-aware dan SPPG-aware.
5. Tambahkan relasi akses user ke banyak SPPG.
6. Tambahkan test isolation antar tenant dan antar SPPG.

---

# 9. Seed Demo Operasional

Untuk kebutuhan demo dan frontend lokal, paket seed backend saat ini sebaiknya dianggap sebagai baseline resmi:

* `8` SPPG demo
* `24` sekolah demo
* polygon service area untuk setiap SPPG
* data distribusi, route, proof, feedback, complaint, dan claim keuangan
* `40` kendaraan demo atau minimal `5` armada per SPPG
* `40` driver demo
* `40` assignment armada
* `120` histori titik GPS armada pada `2026-07-20`

Konvensi kode demo yang aman dipakai integrasi:

* kendaraan: `VH-JKT01-01` sampai `VH-JKT08-05`
* driver: `DRV-JKT01-01` sampai `DRV-JKT08-05`

---

# 10. Definition of Done

Perubahan dianggap sesuai desain v3 bila:

* satu tenant dapat mengelola banyak SPPG tanpa kebocoran data
* semua endpoint operasional tervalidasi oleh `tenant_id` dan `sppg_id`
* model `sppg` menyimpan GPS dan metadata lokasi minimum
* JWT atau request context mendukung active SPPG
* test backend mencakup skenario lintas tenant dan lintas SPPG
* armada dapat dipantau melalui histori GPS dan posisi live per tenant/SPPG
