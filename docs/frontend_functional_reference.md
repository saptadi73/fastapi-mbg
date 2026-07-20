# Frontend Functional Reference

Dokumentasi ini menjadi acuan fungsional untuk tim frontend ERP MBG per **20 Juli 2026**.

Dokumen ini melengkapi:

- [frontend_api_reference.md](C:/projek/fastapi-mbg/docs/frontend_api_reference.md)
- [frontend_api_quick_reference.md](C:/projek/fastapi-mbg/docs/frontend_api_quick_reference.md)

Fokus dokumen ini bukan detail payload API, tetapi:

- struktur layar dan navigasi
- perilaku UI/UX per modul
- workflow bisnis yang harus terlihat di frontend
- status, badge, dan aksi yang relevan
- relasi antarhalaman
- kebutuhan state management frontend

## Demo Context Lokal

Untuk pairing frontend-backend di environment lokal, asumsi demo yang sekarang tersedia adalah:

- `8` SPPG/dapur demo aktif
- `24` sekolah demo
- `475` beneficiary demo
- data GIS, service area, delivery route, proof, incident, feedback, complaint, dan service quality score sudah terisi

Tanggal demo yang direkomendasikan untuk UX testing:

- `2026-07-18`
- `2026-07-19`
- `2026-07-20`
- `2026-07-21`

Implikasi ke frontend:

- filter tanggal default yang aman untuk demo sebaiknya tidak selalu `today only`
- layar GIS, delivery, feedback, dan reporting sebaiknya menyediakan preset cepat seperti `Hari ini`, `3 hari terakhir`, dan `Besok`
- context switch `tenant` dan `SPPG` perlu terlihat jelas karena data demo sekarang tersebar di beberapa dapur
- peta sebaiknya menampilkan marker dan polygon per klaster agar perpindahan Jakarta Pusat, Barat, Timur, Utara, dan Selatan langsung terbaca

## 1. Tujuan

Frontend ERP MBG harus mendukung tiga kebutuhan utama:

1. operasi harian SPPG
2. kontrol approval dan keuangan tenant
3. monitoring lintas modul melalui dashboard, reporting, dan GIS

Frontend tidak boleh hanya menjadi form CRUD. UI harus membantu user memahami:

- konteks tenant dan SPPG aktif
- status proses saat ini
- langkah berikutnya yang bisa dilakukan
- dampak approval terhadap modul berikutnya

## 2. Prinsip UX Utama

### 2.1 Context First

Setiap halaman operasional harus selalu menampilkan:

- `tenant` aktif
- `SPPG` aktif
- role user aktif
- tanggal/jam sinkron sistem bila relevan

Karena backend sudah multi-tenant dan multi-SPPG, kehilangan konteks ini akan membuat user mudah salah input.

### 2.2 Workflow Visible

Untuk modul transaksi utama, status workflow harus selalu terlihat sebagai elemen utama, bukan sekadar field kecil di detail.

Contoh:

- meal plan: `DRAFT`, `SUBMITTED`, `APPROVED`, `MATERIAL_RESERVED`
- budget: `DRAFT`, `SUBMITTED`, `APPROVED`
- workflow approval: `PENDING`, `APPROVED`, `REJECTED`
- delivery: `PLANNED`, `IN_TRANSIT`, `RECEIVED`, `REJECTED`

### 2.3 Action by Role

UI tidak perlu hanya menunggu error `403` dari backend.

Frontend sebaiknya:

- menyembunyikan aksi yang jelas tidak tersedia untuk role user
- menonaktifkan tombol bila state belum memenuhi syarat
- tetap menyiapkan fallback bila backend mengembalikan `403`, `409`, atau `400`

### 2.4 Lists for Work, Detail for Decisions

Pola halaman yang direkomendasikan:

- halaman list untuk triage kerja
- halaman detail untuk keputusan, approval, dan penelusuran histori

### 2.5 Auditability

Untuk modul yang memiliki approval, posting, proof, incident, atau sync log, UI detail harus menyediakan:

- timeline
- metadata actor
- timestamp
- referensi entity terkait

## 3. Persona dan Peran

Peran utama yang perlu dijadikan acuan UI:

### 3.1 Super Admin

Kebutuhan:

- melihat semua tenant
- konfigurasi master lintas tenant
- troubleshooting integrasi dan platform

Menu dominan:

- tenant
- SPPG
- workflow
- integration
- platform ops
- audit

### 3.2 Tenant Admin

Kebutuhan:

- mengelola user tenant
- approval operasional dan budget
- melihat dashboard tenant

Menu dominan:

- dashboard
- identity user management
- workflow approval
- budget
- reporting

### 3.3 Operations Manager

Kebutuhan:

- merencanakan meal plan
- memproses procurement
- memantau produksi dan delivery
- melihat KPI harian

Menu dominan:

- meal plan
- procurement
- inventory
- production
- delivery
- GIS

### 3.4 Finance Manager

Kebutuhan:

- budget
- funding
- government claim
- accounting
- cash flow dan receivable

Menu dominan:

- budget
- accounting
- funding
- government claim
- reporting finance

### 3.5 Quality Officer

Kebutuhan:

- QC inspection
- feedback dan complaint
- proof/incident review
- AI media analysis

Menu dominan:

- quality
- feedback
- delivery
- AI media

### 3.6 Delivery Officer / Warehouse Operator / Procurement Officer

Kebutuhan:

- eksekusi operasional harian
- update stok
- proof of delivery
- penerimaan barang

Menu dominan:

- inventory
- procurement
- delivery

## 4. Struktur Navigasi yang Direkomendasikan

### 4.1 Global Navigation

Struktur menu sidebar yang disarankan:

1. Dashboard
2. Operasional
3. Supply Chain
4. Quality & Distribution
5. Finance
6. Master Data
7. Governance
8. AI & Analytics
9. System

### 4.2 Mapping Menu

#### Dashboard

- Dashboard Tenant
- Dashboard SPPG
- Dashboard Finance

#### Operasional

- Meal Plans
- Production Orders
- Workforce
- Program

#### Supply Chain

- Inventory Balances
- Inventory Transactions
- Warehouses
- Stock Locations
- Inventory Batches
- Purchase Requests
- Purchase Orders
- Goods Receipts
- Supplier Invoices
- Supplier Payments
- Suppliers

#### Quality & Distribution

- QC Inspections
- Delivery Orders
- Delivery Routes
- Delivery Incidents
- Delivery Proof
- Feedback
- Government Claims
- GIS

#### Finance

- Budgets
- Accounts
- Journal Entries
- Funding
- Reporting Finance

#### Master Data

- Tenants
- SPPG
- Schools
- Beneficiaries
- UoM
- Products
- Recipes
- Assets
- Fleet
- Notification Templates

#### Governance

- Workflow Definitions
- Documents
- Audit Events
- Integration

#### AI & Analytics

- AI Forecasts
- AI Recommendations
- AI Daily Summaries
- NL2SQL
- Media Analysis

#### System

- Users
- Platform Jobs
- Outbox Events
- Read Models

## 5. Global Layout Rules

Setiap halaman frontend sebaiknya memiliki layout konsisten:

1. page title
2. subtitle singkat
3. context bar tenant/SPPG
4. filter bar
5. primary actions
6. content area
7. side panel atau detail drawer bila perlu

Komponen global yang direkomendasikan:

- app shell
- context switcher tenant/SPPG
- global notification bell
- quick search
- workflow badge
- status chip
- audit timeline

## 6. Cross-Cutting UI Components

### 6.1 Context Switcher

Wajib tersedia minimal di header.

Perilaku:

- tampilkan tenant aktif
- tampilkan SPPG aktif
- izinkan pindah SPPG bila user memiliki lebih dari satu akses
- setelah ganti SPPG, data list harus refresh

### 6.2 Status Badge

Standar warna yang direkomendasikan:

- `DRAFT`: abu-abu
- `SUBMITTED`: biru
- `PENDING`: kuning
- `APPROVED`: hijau
- `REJECTED`: merah
- `POSTED`: hijau tua
- `FAILED`: merah tua
- `OPEN`: oranye
- `IN_PROGRESS`: biru muda

### 6.3 Timeline

Dipakai pada:

- workflow document
- audit event detail
- government claim
- delivery detail
- integration sync log

### 6.4 Empty State

Setiap list harus punya empty state yang menjelaskan:

- data belum ada
- user belum punya akses
- filter terlalu sempit
- context tenant/SPPG salah

### 6.5 Error State

Frontend sebaiknya membedakan:

- validation error
- permission error
- conflict error
- network error
- integration/provider error

## 7. Dashboard Functional Reference

### 7.1 Dashboard Tenant

Tujuan:

- ringkasan operasional lintas SPPG dalam satu tenant

Widget utama:

- total meal plan per status
- total production order aktif
- total delivery order hari ini
- budget utilization
- claim receivable
- feedback summary

Interaksi:

- klik card membuka list terfilter
- filter tanggal dan SPPG

### 7.2 Dashboard SPPG

Tujuan:

- dashboard operasional harian untuk satu SPPG

Widget utama:

- meal plan hari ini
- stok kritis
- produksi selesai/belum
- delivery on-time
- issue quality/delivery

### 7.3 Dashboard Finance

Tujuan:

- pandangan finance manager

Widget utama:

- cash flow
- government receivable aging
- investor funding position
- ROI by SPPG
- budget actual vs available

Catatan demo frontend:

- seed demo finansial sudah mengisi aging, funding position, ROI, dan cash flow dengan referensi tanggal `2026-07-20`
- untuk screen demo, default filter paling aman adalah `as_of_date=2026-07-20` dan periode Juli 2026

## 8. Workflow Umum Antar Modul

Alur operasional inti yang harus tercermin di UI:

1. `Meal Plan`
2. `Purchase Request`
3. `Purchase Order`
4. `Goods Receipt`
5. `Supplier Invoice`
6. `Supplier Payment`
7. `Production Order`
8. `Delivery Order`
9. `Government Claim`
10. `Feedback / Reporting`

Frontend harus menampilkan relasi ini dalam bentuk:

- linked records
- breadcrumb bisnis
- tab “related documents”
- shortcut action berikutnya

## 9. Modul Fungsional

### 9.1 Identity & Access

#### Halaman

- Login
- My Profile
- Switch Active SPPG
- User List
- User Detail
- User SPPG Access

#### Aturan UI

- setelah login, frontend simpan `access_token`, `active_sppg_id`, dan daftar `accessible_sppg_ids`
- halaman user management hanya tampil untuk `super_admin` dan `tenant_admin`
- ubah SPPG aktif harus memicu refresh context global

#### Workflow

1. login
2. ambil profile
3. tentukan tenant dan SPPG aktif
4. render menu sesuai role

### 9.2 Meal Plan

#### Halaman

- Meal Plan List
- Meal Plan Detail
- Create Meal Plan
- Material Requirements Preview
- Cost Preview

#### Kolom List yang Disarankan

- plan date
- meal type
- recipe
- planned portions
- cost per portion budget
- status
- workflow badge

#### Aksi Utama

- create
- calculate requirements
- submit
- approve
- reserve materials
- open workflow

#### Workflow UI

1. `DRAFT`
2. `SUBMITTED`
3. `APPROVED`
4. `MATERIAL_RESERVED`

Catatan:

- approval meal plan dapat menghasilkan approval request di workflow engine
- status bisnis meal plan dan status workflow harus bisa dibaca bersama

### 9.3 Procurement

#### Halaman

- Purchase Request List
- Purchase Request Detail
- Purchase Order List
- Purchase Order Detail
- Goods Receipt List
- Goods Receipt Detail
- Supplier Invoice List
- Supplier Payment List
- Supplier List
- Supplier Detail

#### Supplier & Vendor UX

Tab yang disarankan di supplier detail:

- profile
- supplier products
- price histories
- purchase orders

#### Purchase Request UX

Aksi utama:

- create from meal plan
- view lines
- create PO/RFQ

#### Purchase Order UX

Aksi utama:

- review lines
- receive goods

#### Goods Receipt UX

Field UI penting:

- warehouse
- stock location
- receipt date
- line quantities
- batch/expiry details

Jika produk batch-tracked:

- UI harus mendukung entry `batch_number`
- expiry date
- quality status

### 9.4 Inventory

#### Halaman

- Inventory Balance List
- Inventory Transaction List
- Warehouse List
- Warehouse Detail
- Stock Location List
- Inventory Batch List
- Expiry Alert
- FEFO Preview Tool

#### List Balance UI

Kolom penting:

- warehouse
- location
- product
- quantity on hand
- reserved
- available
- average cost

#### Batch UI

Kolom penting:

- batch number
- product
- warehouse
- location
- expiry date
- quality status
- blocked flag
- quantity available

#### Expiry Alert UX

- filter `days_ahead`
- sort by expiry paling dekat
- badge warna untuk near expiry

#### FEFO Preview UX

Input:

- product
- warehouse
- required quantity

Output:

- candidate batches
- fulfilled quantity
- shortage quantity

### 9.5 Production

#### Halaman

- Production Order List
- Production Order Detail
- Production Cost Sheet

#### Detail Tabs yang Disarankan

- summary
- material consumption
- cost sheet
- related meal plan

#### Aksi Utama

- create from meal plan
- complete production

#### UX Notes

- tampilkan accepted vs rejected portions
- tampilkan material lines yang terkonsumsi
- tampilkan cost per portion aktual

### 9.6 Delivery & Distribution

#### Halaman

- Delivery Order List
- Delivery Order Detail
- Delivery Route List
- Delivery Route Detail
- Delivery Incident Form
- Delivery Proof Form

#### Delivery Status UI

- `PLANNED`
- `LOADING`
- `IN_TRANSIT`
- `ARRIVED`
- `RECEIVED`
- `PARTIALLY_RECEIVED`
- `REJECTED`
- `CANCELLED`

#### Detail Tabs yang Disarankan

- summary
- route
- proof
- incidents
- related production order

#### Proof of Delivery UX

Field penting:

- receiver name
- receiver GPS
- portions received/rejected
- temperature
- condition status
- photo URLs
- signature
- linked incidents

Frontend mobile/tablet sebaiknya menjadikan proof form ini prioritas tinggi.

### 9.7 Quality

#### Halaman

- QC Inspection List
- QC Inspection Detail
- Add QC Lines
- Finalize Inspection

#### UX Notes

- parameter inspection sebaiknya tampil dalam tabel editable
- hasil `PASS` dan `FAIL` harus langsung terlihat
- inspection mandatory untuk release harus diberi penanda kuat

### 9.8 Feedback

#### Halaman

- Feedback Submission List
- Feedback Detail
- Complaint List
- Service Quality Score List
- Feedback Summary

#### UX Notes

- gabungkan feedback item dan complaint terkait dalam satu detail page
- tampilkan score agregat harian

### 9.9 Government Claim

#### Halaman

- Claim List
- Claim Detail
- Submit Claim
- Verify Claim
- Claim Adjustment
- Claim Payment

#### Workflow

1. create claim
2. submit
3. verify
4. adjust bila perlu
5. payment

#### UX Notes

- tampilkan nilai claim, paid amount, outstanding
- tampilkan bukti delivery terkait

### 9.10 Funding & Accounting

#### Halaman

- Funding Source List
- Funding Agreement List/Detail
- Disbursement List
- Repayment List
- Account List
- Journal Entry List
- Journal Entry Detail
- Budget List
- Budget Detail
- Budget Availability

#### UX Notes

- journal entry detail wajib menampilkan header dan lines
- budget detail wajib menampilkan line-level utilization
- funding agreement detail sebaiknya punya tab:

tab:
- agreement
- disbursements
- repayments

### 9.11 Workforce

#### Halaman

- Position List
- Employee List
- Employee Detail
- Assignment Form
- Shift List
- Attendance List
- Timesheet List
- Labor Cost List

#### UX Notes

- employee detail perlu tab assignment history
- timesheet dan labor cost perlu filter tanggal dan SPPG

### 9.12 Fleet & Asset

#### Fleet Pages

- Vehicle Type List
- Vehicle List
- Vehicle Detail
- Fleet Map Live Tracking
- Driver List
- Vehicle Assignment List
- Maintenance List

#### Fleet UX Notes

- vehicle detail sebaiknya menampilkan current GPS, histori ping terbaru, dan status pergerakan
- fleet map perlu marker berbeda untuk status `LOADING`, `IN_TRANSIT`, `ARRIVED`, dan `MAINTENANCE`
- dispatch board sebaiknya bisa filter per SPPG, status armada, dan waktu update terakhir

#### Asset Pages

- Asset Category List
- Asset List
- Asset Detail
- Asset Assignment List
- Depreciation List

### 9.13 Workflow Engine

#### Halaman

- Workflow Definition List
- Workflow Definition Detail
- Workflow Version Create
- Workflow State Create
- Workflow Action Create
- Workflow Transition Create
- Document Workflow Viewer
- Approval Queue

#### UX Notes

- tampilkan versi workflow aktif
- tampilkan state, action, transition dalam layout bertab
- document workflow viewer harus memperlihatkan:

viewer:
- definition
- version
- current state
- history
- approval requests
- approval decisions

### 9.14 Documents & Audit

#### Halaman

- Document List
- Document Detail
- Upload Version
- Link Document
- Audit Event List
- Audit Event Detail

#### UX Notes

- dokumen sebaiknya reusable lintas modul
- audit event detail perlu raw metadata viewer

### 9.15 Integration & Platform Ops

#### Integration Pages

- External System List/Detail
- Webhook Subscription List
- Data Mapping List
- Sync Job List/Detail
- Inbound Message List/Detail
- Outbound Message List/Detail
- Sync Log List/Detail

#### Platform Pages

- Background Job List
- Outbox Event List
- Read Model Viewer
- Materialized View Status

#### UX Notes

- halaman sync log dan outbound message cocok memakai drawer JSON viewer
- tampilkan `status`, `idempotency_key`, `processed_at`, `response_json`

### 9.16 GIS

#### Halaman

- SPPG Map
- Service Coverage Map
- Delivery Route Map
- Unserved Schools Map
- Risk Heatmap
- Service Area Editor

#### UX Notes

- gunakan mode peta penuh layar untuk GIS
- layer panel perlu checkbox per layer
- polygon editor untuk service area harus mendukung create/update
- nearest kitchens dan assignment validation cocok dijadikan side panel tindakan cepat

### 9.17 AI & Analytics

#### Halaman

- AI Overview
- Forecast List/Detail
- Recommendation List/Detail
- Daily Summary List/Detail
- NL2SQL Workspace
- Image Analysis
- Video Analysis

#### NL2SQL UX

Frontend sebaiknya memisahkan:

- natural language question
- generated SQL
- explanation
- assumptions
- safety notes

Jangan langsung eksekusi query tanpa konfirmasi bila mode execution belum diizinkan.

## 10. Approval UX Reference

Approval yang ada sekarang tersebar minimal pada:

- workflow engine
- meal plan workflow
- budget workflow
- government claim verification

Pola UI yang direkomendasikan:

1. status chip
2. pending approval banner
3. approval history timeline
4. decision modal
5. notes wajib untuk reject

## 11. Header dan State Management

Frontend perlu memelihara state global:

- `access_token`
- `current_user`
- `tenant_id`
- `active_sppg_id`
- `accessible_sppg_ids`
- `roles`
- `request_id` terakhir bila perlu debug

Header yang sering dipakai:

```http
Authorization: Bearer <token>
X-Tenant-ID: <tenant_uuid>
X-SPPG-ID: <sppg_uuid>
```

## 12. Notifikasi dan Inbox

Jenis notifikasi yang layak tampil di frontend:

- approval pending
- meal plan gagal reserve
- stok kritis
- expiry alert
- delivery incident
- sync job failed
- claim paid

Inbox sebaiknya punya:

- unread/read tabs
- deep link ke entity terkait
- mark as read

## 13. Search, Filter, dan Sorting

Standar filter yang disarankan:

- date range
- tenant
- SPPG
- status
- document number
- actor/user

Standar sorting:

- newest first untuk event/log/timeline
- nearest expiry first untuk batches
- most urgent first untuk approval queue

## 14. Error Handling Guide

Frontend sebaiknya punya tabel perilaku umum:

- `400`: tampilkan validasi bisnis
- `401`: redirect login / refresh session
- `403`: akses ditolak
- `404`: data tidak ditemukan atau scope salah
- `409`: conflict workflow atau duplicate action
- `500`: fallback generic error

Contoh conflict yang harus diberi pesan khusus:

- approval request masih pending
- workflow transition tidak diizinkan
- workflow definition sudah ada
- stok tidak cukup

## 15. Responsive Strategy

### Desktop First

Modul yang paling cocok untuk desktop:

- accounting
- budget
- integration
- workflow definition
- reporting

### Tablet/Mobile Priority

Modul yang wajib nyaman di tablet/mobile:

- delivery proof
- delivery incidents
- QC inspection
- attendance
- feedback submission
- AI media analysis

## 16. Referensi Implementasi per Modul

Urutan prioritas implementasi frontend yang disarankan:

1. login dan context switcher
2. dashboard tenant/SPPG
3. meal plan
4. inventory balances dan warehouses
5. procurement minimal
6. production
7. delivery proof dan incidents
8. budget dan finance
9. workflow viewer
10. GIS
11. AI tools
12. platform/integration admin

## 17. Hubungan dengan API Reference

Gunakan dokumen ini untuk menjawab:

- halaman apa saja yang perlu dibuat
- status apa yang perlu divisualkan
- urutan aksi user
- hubungan antar modul
- kebutuhan komponen reusable

Gunakan API reference untuk menjawab:

- endpoint apa yang dipanggil
- payload dan response detail
- code sukses dan error
- header yang wajib dikirim

## 18. Definition of Done Frontend

Sebuah modul frontend dianggap siap bila:

1. list page tersedia
2. detail page tersedia
3. status dan workflow terlihat jelas
4. primary actions sesuai role dan state
5. error state tertangani
6. loading dan empty state tersedia
7. linked records bisa dibuka
8. integrasi API mengikuti envelope backend

## 19. Dokumen Lanjutan yang Disarankan

Setelah dokumen ini, artefak frontend yang layak dibuat berikutnya:

1. sitemap dan navigation tree
2. wireframe low fidelity per modul
3. design token dan component inventory
4. state machine UI untuk meal plan, procurement, delivery, dan workflow approval
5. table of status/badge/CTA per modul
