# Frontend Status And CTA Matrix

Dokumen ini memetakan status bisnis, badge UI, aksi utama, dan transisi layar untuk frontend ERP MBG.

Dokumen ini melengkapi:

- [frontend_functional_reference.md](C:/projek/fastapi-mbg/docs/frontend_functional_reference.md)
- [frontend_screen_matrix.md](C:/projek/fastapi-mbg/docs/frontend_screen_matrix.md)
- [frontend_api_reference.md](C:/projek/fastapi-mbg/docs/frontend_api_reference.md)

## 1. Tujuan

Frontend sering gagal konsisten bukan karena API kurang, tetapi karena:

- status tidak dipetakan ke badge UI
- CTA tidak dipetakan ke role
- user tidak tahu langkah berikutnya

Dokumen ini menjadi acuan untuk:

- badge dan warna
- tombol utama
- tombol sekunder
- kondisi disable
- next action

## 2. Standar Badge UI

| Status | Tone | Rekomendasi Warna |
|---|---|---|
| `DRAFT` | neutral | abu-abu |
| `SUBMITTED` | info | biru |
| `PENDING` | warning | kuning |
| `APPROVED` | success | hijau |
| `REJECTED` | danger | merah |
| `POSTED` | success | hijau tua |
| `OPEN` | warning | oranye |
| `FAILED` | danger | merah tua |
| `SUCCESS` | success | hijau |
| `IN_PROGRESS` | info | biru muda |
| `CANCELLED` | neutral | abu tua |

## 3. Global CTA Rules

Aturan umum:

1. hanya satu `primary CTA` per state utama
2. CTA destruktif tidak dijadikan primary
3. jika aksi tidak boleh dilakukan karena state, tombol tampil disabled dengan helper text
4. jika aksi tidak boleh dilakukan karena role, tombol sebaiknya tidak tampil

## 4. Meal Plan Matrix

| Current Status | Badge | Primary CTA | Secondary CTA | Allowed Roles | Next Status | Notes |
|---|---|---|---|---|---|---|
| `DRAFT` | neutral | `Submit` | `Calculate Requirements`, `Cost Preview`, `Edit` | `super_admin`, `tenant_admin`, `operations_manager` | `SUBMITTED` | Entry awal |
| `SUBMITTED` | info | `Approve` | `View Workflow`, `Cost Preview` | `super_admin`, `tenant_admin`, `operations_manager` | `APPROVED` atau pending approval workflow | UI harus cek workflow |
| `APPROVED` | success | `Reserve Materials` | `Create Production Order`, `View Workflow`, `Cost Preview` | `super_admin`, `tenant_admin`, `operations_manager` | `MATERIAL_RESERVED` | Tombol reserve disable bila stok tidak cukup |
| `MATERIAL_RESERVED` | success | `Create Production Order` | `View Requirements`, `View Workflow` | `super_admin`, `tenant_admin`, `operations_manager` | modul berikutnya `Production Order` | Final state meal plan operasional |

## 5. Workflow Approval Matrix

| Workflow State | Badge | Primary CTA | Secondary CTA | Allowed Roles | Notes |
|---|---|---|---|---|---|
| `PENDING` approval request | warning | `Approve` | `Reject`, `View History` | `super_admin`, `tenant_admin` | Reject sebaiknya minta notes |
| `APPROVED` approval request | success | `View Result` | `View Decision History` | semua role baca | Tidak ada CTA write |
| `REJECTED` approval request | danger | `Review Document` | `View Reason` | role pemilik dokumen | Reason wajib terbaca jelas |

## 6. Budget Matrix

| Current Status | Badge | Primary CTA | Secondary CTA | Allowed Roles | Next Status | Notes |
|---|---|---|---|---|---|---|
| `DRAFT` | neutral | `Submit` | `Edit`, `View Availability` | `super_admin`, `tenant_admin`, `finance_manager` | `SUBMITTED` | Budget masih bisa berubah |
| `SUBMITTED` | info | `Approve` | `View Availability` | `super_admin`, `tenant_admin`, `finance_manager` | `APPROVED` atau pending workflow | Approval dapat memicu workflow |
| `APPROVED` | success | `View Availability` | `Open Related PR`, `Open Journal Impact` | `super_admin`, `tenant_admin`, `finance_manager` | tetap `APPROVED` | Fokus monitoring availability |

## 7. Purchase Request Matrix

| Current Status | Badge | Primary CTA | Secondary CTA | Allowed Roles | Notes |
|---|---|---|---|---|---|
| `DRAFT` | neutral | `Create PO/RFQ` | `View Lines`, `Open Meal Plan` | `super_admin`, `tenant_admin`, `operations_manager`, `procurement_officer` | Status list harus mudah difilter |
| `SUBMITTED` jika nanti ada | info | `Create PO/RFQ` | `View Lines` | `procurement_officer`, `tenant_admin` | Disiapkan untuk ekspansi |
| `CLOSED` jika nanti ada | success | `View Related Documents` | `Open Goods Receipts` | role baca | Lebih ke histori |

## 8. Purchase Order Matrix

| Current Status | Badge | Primary CTA | Secondary CTA | Allowed Roles | Notes |
|---|---|---|---|---|---|
| `DRAFT` | neutral | `Receive Goods` | `View Supplier`, `View Lines` | `super_admin`, `tenant_admin`, `procurement_officer`, `operations_manager` | Bila order_type = RFQ, label CTA bisa disesuaikan |
| `POSTED` atau aktif | info | `Receive Goods` | `View Related GR` | `procurement_officer`, `operations_manager` | Default operasional |
| `COMPLETED` jika nanti ada | success | `View Goods Receipts` | `View Supplier Invoice` | role baca | Histori |

## 9. Goods Receipt Matrix

| Current Status | Badge | Primary CTA | Secondary CTA | Allowed Roles | Notes |
|---|---|---|---|---|---|
| `DRAFT` jika nanti ada | neutral | `Post Receipt` | `Edit Batches` | `procurement_officer`, `warehouse_operator` | Tahap ekspansi |
| `POSTED` | success | `Create Supplier Invoice` | `View Inventory Impact`, `View Batches` | `super_admin`, `tenant_admin`, `procurement_officer`, `finance_manager` | UI detail harus tampilkan line dan batch |

## 10. Supplier Invoice Matrix

| Current Status | Badge | Primary CTA | Secondary CTA | Allowed Roles | Notes |
|---|---|---|---|---|---|
| `POSTED` | info | `Create Payment` | `View Journal`, `View Goods Receipt` | `super_admin`, `tenant_admin`, `finance_manager` | Belum lunas |
| `PAID` | success | `View Payment` | `View Journal` | semua role finance baca | CTA write hilang |

## 11. Supplier Payment Matrix

| Current Status | Badge | Primary CTA | Secondary CTA | Allowed Roles | Notes |
|---|---|---|---|---|---|
| `POSTED` | success | `View Journal` | `Open Supplier Invoice` | `super_admin`, `tenant_admin`, `finance_manager` | Dokumen final |

## 12. Inventory Batch Matrix

| Current Condition | Badge | Primary CTA | Secondary CTA | Allowed Roles | Notes |
|---|---|---|---|---|---|
| `quality_status = PENDING` | warning | `Review Batch` | `Open Product` | `warehouse_operator`, `quality_officer` | Perlu tindak lanjut QC |
| `quality_status = PASSED` | success | `Use in FEFO Preview` | `Open Warehouse` | `warehouse_operator`, `operations_manager` | Batch aktif |
| `is_blocked = true` | danger | `View Reason` | `Open Batch Detail` | `warehouse_operator`, `quality_officer` | Tidak boleh dipakai |
| `near expiry` | warning | `Review Consumption Plan` | `Open Expiry Alert` | `warehouse_operator`, `operations_manager` | Ditentukan dari expiry horizon |

## 13. Production Order Matrix

| Current Status | Badge | Primary CTA | Secondary CTA | Allowed Roles | Next Status | Notes |
|---|---|---|---|---|---|---|
| `PLANNED` atau awal | info | `Complete Production` | `View Materials`, `Open Meal Plan` | `super_admin`, `tenant_admin`, `operations_manager` | `COMPLETED` | Gunakan label final sesuai data backend |
| `COMPLETED` | success | `Create Delivery Order` | `View Cost Sheet`, `View Materials` | `super_admin`, `tenant_admin`, `operations_manager` | ke delivery | CTA berikutnya pindah modul |

## 14. Delivery Order Matrix

| Current Status | Badge | Primary CTA | Secondary CTA | Allowed Roles | Next Status | Notes |
|---|---|---|---|---|---|---|
| `PLANNED` | info | `Record Proof` | `Create Route`, `Record Incident` | `super_admin`, `tenant_admin`, `operations_manager`, `delivery_officer` | `RECEIVED` atau lainnya | Cocok untuk mobile |
| `LOADING` | info | `Record Proof` | `Record Incident` | `delivery_officer` | lanjut delivery | Opsional bila dipakai |
| `IN_TRANSIT` | info | `Record Proof` | `Record Incident` | `delivery_officer` | `ARRIVED`/`RECEIVED` | Incident bisa muncul kapan saja |
| `ARRIVED` | info | `Record Proof` | `Record Incident` | `delivery_officer` | `RECEIVED` | Tahap sebelum bukti diterima |
| `RECEIVED` | success | `View Proof` | `Open Claim`, `Open Feedback` | semua role terkait | final operasional | Tampilkan foto dan tanda tangan |
| `PARTIALLY_RECEIVED` | warning | `View Proof` | `Record Incident`, `Open Feedback` | delivery/quality | Perlu follow-up |
| `REJECTED` | danger | `Record Incident` | `Open Feedback` | delivery/quality | Eskalasi |
| `CANCELLED` | neutral | `View History` | - | role baca | Final |

## 15. Delivery Route Matrix

| Current Status | Badge | Primary CTA | Secondary CTA | Allowed Roles | Notes |
|---|---|---|---|---|---|
| `PLANNED` | info | `Open Route Detail` | `Open Delivery Stops` | `delivery_officer`, `operations_manager` | List route planning |
| `IN_PROGRESS` jika nanti ada | info | `Open Active Stops` | `Record Incident` | `delivery_officer` | Tahap ekspansi |
| `COMPLETED` jika nanti ada | success | `View Performance` | `Open Related Deliveries` | role baca | Histori |

## 16. QC Inspection Matrix

| Current Status | Badge | Primary CTA | Secondary CTA | Allowed Roles | Notes |
|---|---|---|---|---|---|
| `DRAFT` | neutral | `Add Lines` | `Edit Inspection` | `quality_officer`, `operations_manager` | Awal inspeksi |
| `IN_PROGRESS` jika nanti ada | info | `Finalize Inspection` | `Add Lines` | `quality_officer`, `operations_manager` | Tahap ekspansi |
| `PASSED` | success | `View Result` | `Open Related Production` | semua role baca | Tidak ada write |
| `FAILED` | danger | `View Corrective Action` | `Open Related Production` | quality, operations | Harus menonjol |

## 17. Feedback Matrix

| Current Status | Badge | Primary CTA | Secondary CTA | Allowed Roles | Notes |
|---|---|---|---|---|---|
| Submission masuk | info | `Open Detail` | `Create Complaint` | `quality_officer`, `operations_manager`, `delivery_officer` | Hubungkan dengan delivery |
| Complaint `OPEN` | warning | `Review Complaint` | `Open Related Submission` | `quality_officer`, `operations_manager` | Tampilkan severity |
| Complaint resolved jika nanti ada | success | `View Resolution` | `Open History` | role baca | Tahap ekspansi |

## 18. Government Claim Matrix

| Current Status | Badge | Primary CTA | Secondary CTA | Allowed Roles | Notes |
|---|---|---|---|---|---|
| `DRAFT` | neutral | `Submit Claim` | `View Deliveries`, `Edit Claim` | `super_admin`, `tenant_admin`, `finance_manager` | Tahap awal |
| `SUBMITTED` | info | `Verify Claim` | `View Evidence` | `super_admin`, `tenant_admin`, `finance_manager` | Tahap approval |
| `VERIFIED` | success | `Record Payment` | `View Aging` | `super_admin`, `tenant_admin`, `finance_manager` | Siap dibayar |
| `PARTIALLY_PAID` jika nanti ada | warning | `Record Payment` | `View Outstanding` | `finance_manager` | Tahap ekspansi |
| `PAID` | success | `View Payment History` | `View Journal` | role baca | Final |

## 19. Funding Matrix

| Current Status | Badge | Primary CTA | Secondary CTA | Allowed Roles | Notes |
|---|---|---|---|---|---|
| Agreement aktif | info | `Record Disbursement` | `Record Repayment`, `View Summary` | `super_admin`, `tenant_admin`, `finance_manager` | Dua CTA write boleh dibagi primer/sekunder berdasar context |
| Funding closed jika nanti ada | success | `View History` | `View ROI` | role baca | Tahap ekspansi |

## 20. Workflow Definition Matrix

| Current Context | Badge | Primary CTA | Secondary CTA | Allowed Roles | Notes |
|---|---|---|---|---|---|
| Definition list | neutral | `Create Definition` | `Open Definition` | `super_admin`, `tenant_admin` | Admin-only |
| Definition detail | info | `Create Version` | `Add Transition`, `Add State`, `Add Action` | `super_admin`, `tenant_admin` | Pakai tab layout |
| Approval request pending | warning | `Approve` | `Reject` | `super_admin`, `tenant_admin` | Notes reject wajib |

## 21. Integration Matrix

| Current Status | Badge | Primary CTA | Secondary CTA | Allowed Roles | Notes |
|---|---|---|---|---|---|
| Sync job `READY` atau aktif | info | `Run Sync Job` | `View External System` | `super_admin`, `tenant_admin` | Untuk job manual |
| Sync log `SUCCESS` | success | `View Payload` | `View Response` | `super_admin`, `tenant_admin` | JSON viewer |
| Sync log `FAILED` | danger | `Inspect Failure` | `Retry via Job`, `View Payload` | `super_admin`, `tenant_admin` | Error perlu jelas |
| Outbound message `QUEUED` | info | `View Payload` | `Open Sync Job` | `super_admin`, `tenant_admin` | Monitoring |
| Outbound message `FAILED` | danger | `Inspect Response` | `Open Sync Log` | `super_admin`, `tenant_admin` | Monitoring |

## 22. AI Matrix

| Current Context | Badge | Primary CTA | Secondary CTA | Allowed Roles | Notes |
|---|---|---|---|---|---|
| AI overview | info | `Open Forecasts` | `Open Recommendations`, `Open NL2SQL` | `tenant_admin`, `operations_manager`, `finance_manager` | Navigasi analytic |
| NL2SQL result generated | success | `Copy SQL` | `View Explanation`, `View Assumptions` | `tenant_admin`, `finance_manager`, `operations_manager` | Jangan auto-execute bila belum diizinkan |
| AI provider disabled | warning | `View Setup Guide` | - | admin | Ambil dari provider status |
| Media analysis result | success | `View Summary` | `Upload Another File` | `quality_officer`, `operations_manager` | Cocok untuk image/video tools |

## 23. Notification Matrix

| Notification Type | Badge | Primary CTA | Secondary CTA | Notes |
|---|---|---|---|---|
| Approval pending | warning | `Open Approval` | `Mark Read` | Prioritas tinggi |
| Delivery incident | danger | `Open Delivery` | `Mark Read` | Prioritas tinggi |
| Stock critical | warning | `Open Inventory` | `Mark Read` | Prioritas tinggi |
| Expiry alert | warning | `Open Expiry Alert` | `Mark Read` | Prioritas tinggi |
| Sync failed | danger | `Open Sync Log` | `Mark Read` | Untuk admin |

## 24. Recommended Implementation Order

Urutan implementasi komponen status/CTA:

1. global status badge component
2. reusable action bar component
3. workflow banner component
4. approval modal
5. timeline component
6. JSON viewer component
7. mobile proof form action set
