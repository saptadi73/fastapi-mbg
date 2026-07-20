# Frontend Component Inventory

Dokumen ini menjadi acuan komponen reusable untuk frontend ERP MBG agar implementasi UI konsisten lintas modul.

Dokumen ini melengkapi:

- [frontend_api_reference.md](C:/projek/fastapi-mbg/docs/frontend_api_reference.md)
- [frontend_functional_reference.md](C:/projek/fastapi-mbg/docs/frontend_functional_reference.md)
- [frontend_screen_matrix.md](C:/projek/fastapi-mbg/docs/frontend_screen_matrix.md)
- [frontend_status_and_cta_matrix.md](C:/projek/fastapi-mbg/docs/frontend_status_and_cta_matrix.md)
- [frontend_wireframe_text_spec.md](C:/projek/fastapi-mbg/docs/frontend_wireframe_text_spec.md)

## 1. Tujuan

- menyatukan bahasa antara UI/UX, frontend, dan backend
- mempercepat delivery dengan reusable component
- mengurangi inkonsistensi label, state, badge, dan action
- memudahkan test automation berbasis selector dan role

## 2. Prinsip Umum

- semua komponen harus mendukung `loading`, `empty`, `error`, dan `disabled`
- semua komponen form harus punya `label`, `helperText`, dan `errorMessage`
- semua komponen data harus mendukung role-based visibility
- semua action penting harus mendukung permission check dan business-state check
- semua komponen harus siap mobile collapse bila dipakai pada alur lapangan

## 3. App Shell Components

### 3.1 `AppShell`

Fungsi:

- layout utama aplikasi
- mengelola header, sidebar, content, dan responsive collapse

Props inti:

- `tenantOptions`
- `selectedTenantId`
- `sppgOptions`
- `selectedSppgId`
- `notificationCount`
- `userProfile`
- `sidebarItems`

States:

- `default`
- `sidebar-collapsed`
- `mobile-drawer-open`

### 3.2 `ContextSwitcher`

Fungsi:

- mengganti tenant dan SPPG aktif
- memicu reload screen yang context-sensitive

Props inti:

- `tenantOptions`
- `sppgOptions`
- `value`
- `onChange`

Validation:

- tenant wajib dipilih untuk user multi-tenant
- SPPG bisa optional untuk layar tenant-wide

### 3.3 `NotificationBell`

Fungsi:

- menampilkan unread count
- membuka drawer notifikasi

Isi minimal:

- judul notifikasi
- modul
- waktu
- CTA buka dokumen

## 4. Navigation Components

### 4.1 `SidebarNav`

Sections:

- dashboard
- operasional
- procurement & inventory
- production & distribution
- finance
- governance
- analytics & AI
- system

Behavior:

- highlight active route
- collapse per section pada mobile
- hide item bila role tidak punya izin

### 4.2 `Breadcrumbs`

Contoh:

- `Dashboard / Procurement / Purchase Orders / PO-2026-0001`
- `Governance / Workflows / Meal Plan Approval / Version 2`

## 5. Common Data Components

### 5.1 `PageHeader`

Isi:

- title
- subtitle
- context chips
- top-level action group

Props inti:

- `title`
- `subtitle`
- `badges`
- `actions`

### 5.2 `ToolbarFilters`

Komposisi umum:

- search input
- date range picker
- status select
- tenant/SPPG select
- advanced filter toggle

Rules:

- filter primer selalu terlihat
- filter sekunder masuk drawer pada mobile

### 5.3 `DataTable`

Fungsi:

- tabel generik untuk listing modul

Fitur minimal:

- sortable columns
- pagination
- sticky header
- empty state
- row click
- row actions
- skeleton loading

Props inti:

- `columns`
- `rows`
- `rowKey`
- `loading`
- `pagination`
- `onSort`
- `onRowClick`
- `rowActions`

### 5.4 `SummaryCard`

Dipakai untuk:

- KPI dashboard
- count status
- finance summary
- stock summary

Isi:

- label
- main value
- optional delta
- optional trend caption

### 5.5 `StatusBadge`

Fungsi:

- representasi status proses secara konsisten

Variant minimal:

- `draft`
- `pending`
- `in-progress`
- `approved`
- `completed`
- `rejected`
- `cancelled`
- `failed`
- `warning`

Rules:

- badge status workflow dibedakan dari badge status dokumen bila keduanya tampil bersamaan

### 5.6 `EmptyStatePanel`

Isi:

- icon/illustration ringan
- title
- explanatory text
- CTA utama

Contoh:

- belum ada meal plan
- belum ada batch inventory
- belum ada approval request

### 5.7 `ErrorStatePanel`

Isi:

- error title
- human-readable description
- technical reference optional
- retry button

## 6. Form Components

### 6.1 `FormFieldText`

Props inti:

- `name`
- `label`
- `placeholder`
- `value`
- `required`
- `helperText`
- `errorMessage`

### 6.2 `FormFieldTextarea`

Dipakai untuk:

- notes
- incident description
- workflow remarks
- AI prompt tambahan

### 6.3 `FormFieldSelect`

Dipakai untuk:

- status
- supplier
- warehouse
- stock location
- account
- workflow action

Behavior:

- searchable bila option lebih dari 10
- async load untuk master data besar

### 6.4 `FormFieldDate`

Dipakai untuk:

- meal plan date
- order date
- expected delivery date
- claim date

### 6.5 `FormFieldDateTime`

Dipakai untuk:

- goods receipt time
- delivery proof received time
- sync processed time

### 6.6 `FormFieldNumber`

Dipakai untuk:

- quantity
- temperature
- budget amount
- service radius
- latitude/longitude manual fallback

Validation umum:

- min/max
- decimal precision
- non-negative untuk qty dan amount bila relevan

### 6.7 `FormFieldMoney`

Format:

- currency label
- thousand separator
- decimal sesuai kebijakan finance

### 6.8 `FormFieldMultiSelect`

Dipakai untuk:

- linked incidents
- roles
- tags
- school targets

### 6.9 `FormSection`

Fungsi:

- membagi form panjang menjadi blok terstruktur

Contoh:

- header summary
- procurement details
- receiver details
- evidence upload

### 6.10 `FormActionFooter`

Isi:

- cancel
- save draft
- submit
- primary async state

Rules:

- tombol destructive dipisah visualnya
- tombol submit disabled saat form invalid atau permission tidak cukup

## 7. Document Workflow Components

### 7.1 `WorkflowStateChip`

Menampilkan:

- current state
- SLA indicator optional
- overdue warning optional

### 7.2 `WorkflowTimeline`

Isi per item:

- action name
- actor
- timestamp
- from state
- to state
- comment

### 7.3 `ApprovalRequestList`

Kolom:

- request number
- requested to
- status
- requested at
- due at
- CTA

### 7.4 `ApprovalDecisionPanel`

Isi:

- decision buttons
- remarks textarea
- current approval status

Rules:

- tampil hanya bila user adalah approver yang valid
- tombol disable bila request sudah bukan `PENDING`

## 8. Procurement Components

### 8.1 `PurchaseRequestLineEditor`

Kolom:

- product
- requested qty
- UoM
- preferred supplier
- needed date
- note

Validation:

- qty harus lebih besar dari 0
- product wajib ada

### 8.2 `SupplierSummaryCard`

Isi:

- supplier name
- contact
- rating optional
- lead time
- last order date

### 8.3 `PurchaseOrderLineTable`

Kolom:

- product
- ordered qty
- received qty
- unit price
- subtotal
- line status

### 8.4 `GoodsReceiptBatchEditor`

Kolom:

- product
- receive qty
- batch no
- expiry date
- quality status
- notes

Rules:

- batch editor wajib untuk tracked product
- expiry wajib untuk bahan expiry-sensitive

## 9. Inventory Components

### 9.1 `InventoryBalanceTable`

Kolom minimal:

- warehouse
- location
- product
- on hand
- reserved
- available
- average cost

### 9.2 `BatchStatusBadge`

Variant:

- `fresh`
- `near-expiry`
- `expired`
- `blocked`
- `quarantined`

### 9.3 `FefoPreviewPanel`

Isi:

- requested quantity
- fulfilled quantity
- shortage quantity
- candidate batch list

### 9.4 `StockMovementTimeline`

Isi:

- movement type
- source reference
- qty
- from location
- to location
- timestamp

## 10. Production Components

### 10.1 `ProductionSummaryCardGroup`

Isi:

- planned portions
- actual portions
- accepted portions
- rejected portions
- actual cost per portion

### 10.2 `MaterialConsumptionTable`

Kolom:

- product
- planned qty
- actual qty
- variance
- batch source

### 10.3 `CostSheetTable`

Kolom:

- component
- planned cost
- actual cost
- variance

## 11. Distribution Components

### 11.1 `RouteMapPanel`

Isi:

- route polyline
- stop markers
- delivery sequence
- current stop status

### 11.2 `DeliveryStopList`

Kolom:

- stop number
- school
- ETA
- actual arrival
- proof status
- incident count

### 11.3 `DeliveryProofUploader`

Fungsi:

- mengelola upload foto, signature, dan evidence lain

Rules:

- preview file sebelum submit
- tampilkan metadata upload
- validasi tipe file dan ukuran

### 11.4 `GpsCaptureField`

Mode:

- auto capture device
- manual fallback

Fields:

- latitude
- longitude
- accuracy optional
- capture timestamp

### 11.5 `TemperatureInputCard`

Isi:

- input suhu
- satuan
- threshold indicator
- warning bila di luar batas

### 11.6 `IncidentTimeline`

Isi per card:

- incident type
- severity
- reported by
- reported at
- description
- linked proof

## 12. Finance Components

### 12.1 `BudgetAvailabilityGrid`

Kolom:

- planned
- reserved
- committed
- actual
- available

### 12.2 `JournalEntryTable`

Kolom:

- account code
- account name
- debit
- credit
- line description

### 12.3 `ClaimAdjustmentTable`

Kolom:

- adjustment type
- amount
- reason
- evidence

### 12.4 `ReceivableAgingChart`

Bucket standar:

- current
- 1-30 hari
- 31-60 hari
- 61-90 hari
- 90+ hari

### 12.5 `FundingPositionCard`

Isi:

- investor name
- funded amount
- outstanding usage
- expected return
- ROI progress

## 13. Governance and Integration Components

### 13.1 `JsonViewerPanel`

Dipakai untuk:

- inbound payload
- outbound payload
- sync response
- AI analysis raw response

Features:

- collapse nodes
- copy JSON
- search key

### 13.2 `SyncJobStatusCard`

Isi:

- job name
- direction
- status
- last run
- success rate optional

### 13.3 `WebhookSubscriptionTable`

Kolom:

- name
- event type
- target URL
- secret configured
- active status

### 13.4 `OutboxQueueTable`

Kolom:

- message id
- aggregate type
- aggregate id
- topic
- status
- retry count
- published at

## 14. GIS Components

### 14.1 `MapCanvas`

Fungsi:

- render map dasar
- polygon editing
- marker preview
- geofence visualization

Capabilities:

- zoom
- draw
- edit
- delete draft shape
- fit bounds

### 14.2 `CoordinateFieldGroup`

Fields:

- latitude
- longitude
- elevation optional

Validation:

- latitude `-90` s.d. `90`
- longitude `-180` s.d. `180`

### 14.3 `GeoJsonImportPanel`

Isi:

- upload/import text area
- validation message
- preview summary

### 14.4 `ServiceAreaValidationPanel`

Isi:

- polygon valid/invalid
- overlap detection
- area size
- last updated by

## 15. AI & Analytics Components

### 15.1 `Nl2SqlPromptPanel`

Isi:

- natural language query
- schema hint optional
- safety note

Rules:

- hasil SQL default read-only
- warning bila pertanyaan ambigu

### 15.2 `SqlResultPreview`

Isi:

- SQL text
- explanation
- result preview optional

### 15.3 `MediaAnalysisUploader`

Dipakai untuk:

- upload foto kualitas makanan
- upload video distribusi atau bukti lapangan

States:

- ready
- uploading
- analyzing
- success
- failed

### 15.4 `AiFindingCard`

Isi:

- finding title
- confidence
- severity
- recommendation
- linked asset

## 16. Cross-Cutting Dialogs

### 16.1 `ConfirmActionDialog`

Dipakai untuk:

- submit
- approve
- cancel
- post journal
- rerun sync

Isi:

- action title
- impact summary
- confirm button

### 16.2 `BusinessErrorDialog`

Dipakai saat:

- stok tidak cukup
- workflow state tidak valid
- approval sudah kadaluarsa
- batch blocked tidak bisa dipakai

### 16.3 `AuditHistoryDrawer`

Isi:

- created by/at
- updated by/at
- version changes
- source module references

## 17. Frontend Validation Rules

Aturan yang harus reusable di layer UI:

- quantity tidak boleh negatif
- date akhir tidak boleh sebelum date awal
- received portions tidak boleh lebih besar dari delivered portions
- approved amount tidak boleh lebih besar dari requested amount jika rule bisnis begitu
- latitude/longitude harus valid
- JSON mapping harus valid bila form integrasi dipakai

## 18. Testability Notes

Semua komponen penting sebaiknya punya:

- stable `data-testid`
- semantic role yang benar
- state visual yang bisa diuji
- error message yang deterministik

Komponen prioritas untuk integration test:

- login form
- context switcher
- data table
- workflow action bar
- delivery proof uploader
- GIS polygon editor
- NL2SQL workspace

## 19. Prioritas Implementasi

Urutan implementasi komponen yang direkomendasikan:

1. app shell, page header, toolbar filters, status badge
2. data table, summary card, empty/error state
3. generic form fields dan form footer
4. workflow timeline dan approval panel
5. procurement/inventory reusable tables
6. delivery proof uploader dan GPS capture
7. GIS map canvas dan geojson import
8. AI prompt panel dan media analysis uploader
