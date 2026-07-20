# Frontend Wireframe Text Spec

Dokumen ini berisi blueprint wireframe berbasis teks untuk halaman utama frontend ERP MBG.

Dokumen ini melengkapi:

- [frontend_functional_reference.md](C:/projek/fastapi-mbg/docs/frontend_functional_reference.md)
- [frontend_screen_matrix.md](C:/projek/fastapi-mbg/docs/frontend_screen_matrix.md)
- [frontend_status_and_cta_matrix.md](C:/projek/fastapi-mbg/docs/frontend_status_and_cta_matrix.md)

Tujuan dokumen ini:

- memberi struktur visual awal sebelum mockup hi-fi
- menyamakan ekspektasi antara product, UI/UX, dan frontend engineer
- mempercepat implementasi layout dan state UI

## 1. Notasi

Format blok:

- `Header`: judul halaman dan context
- `Toolbar`: filter, search, action utama
- `Content`: tabel, cards, map, form, atau tabs
- `Side Panel`: drawer atau panel tambahan
- `Footer State`: pagination, summary, helper text

## 2. Global App Shell

```text
+----------------------------------------------------------------------------------+
| Logo | App Name | Quick Search | Notifications | Context Switcher | User Menu    |
+----------------------------------------------------------------------------------+
| Sidebar                                                                        |
| - Dashboard                                                                    |
| - Operasional                                                                  |
| - Supply Chain                                                                 |
| - Quality & Distribution                                                       |
| - Finance                                                                      |
| - Master Data                                                                  |
| - Governance                                                                   |
| - AI & Analytics                                                               |
| - System                                                                       |
|--------------------------------------------------------------------------------|
| Main Content Area                                                              |
|  Header                                                                        |
|  Toolbar                                                                       |
|  Page Content                                                                  |
+----------------------------------------------------------------------------------+
```

### Komponen Wajib

- tenant/SPPG context di header
- notifikasi unread count
- user menu untuk profile dan logout
- sidebar collapse/expand

## 3. Login Page

```text
+------------------------------------------------------+
| ERP MBG                                              |
| Login                                                |
|------------------------------------------------------|
| Email                                                |
| [______________________________]                     |
| Password                                             |
| [______________________________]                     |
|                                                      |
| [ Login ]                                            |
|                                                      |
| Helper text: gunakan akun sesuai role                |
+------------------------------------------------------+
```

### States

- loading pada tombol login
- invalid credential message
- server unavailable message

## 4. Tenant Dashboard

```text
+----------------------------------------------------------------------------------+
| Header: Dashboard Tenant                                                         |
| Subtitle: ringkasan operasional dan keuangan lintas SPPG                         |
| Context: Tenant A | Semua SPPG / SPPG aktif                                      |
+----------------------------------------------------------------------------------+
| Toolbar: [Date Range] [SPPG Filter] [Refresh]                                    |
+----------------------------------------------------------------------------------+
| KPI Row                                                                          |
| [Meal Plans] [Production Orders] [Delivery Orders] [Budget Utilization]          |
+----------------------------------------------------------------------------------+
| Chart Row                                                                        |
| [Meal Plan Status Chart]     [Delivery Performance Chart]                        |
+----------------------------------------------------------------------------------+
| Summary Row                                                                      |
| [Government Receivable]       [Funding Position]                                 |
+----------------------------------------------------------------------------------+
| Bottom Row                                                                       |
| [Recent Audit/Alerts]          [Pending Approvals]                               |
+----------------------------------------------------------------------------------+
```

## 5. SPPG Dashboard

```text
+----------------------------------------------------------------------------------+
| Header: Dashboard SPPG                                                           |
| Subtitle: ringkasan operasional harian dapur                                     |
| Context: Tenant A | SPPG Jakarta Pusat 01                                        |
+----------------------------------------------------------------------------------+
| Toolbar: [Date] [Refresh]                                                        |
+----------------------------------------------------------------------------------+
| KPI Row                                                                          |
| [Meal Plans Today] [Stock Critical] [Production Complete] [Delivery On Time]     |
+----------------------------------------------------------------------------------+
| Main Row                                                                         |
| [Production Progress]                [Delivery Status Today]                     |
+----------------------------------------------------------------------------------+
| Bottom Row                                                                       |
| [Feedback/Complaint Summary]         [Inventory Risk / Expiry]                   |
+----------------------------------------------------------------------------------+
```

## 6. Meal Plan List

```text
+----------------------------------------------------------------------------------+
| Header: Meal Plans                                                               |
| Subtitle: rencana menu dan siklus persiapan produksi                             |
+----------------------------------------------------------------------------------+
| Toolbar: [Search] [Date Range] [Status] [Recipe] [Create Meal Plan]              |
+----------------------------------------------------------------------------------+
| Table                                                                            |
| Date | Meal Type | Recipe | Portions | Budget/Portion | Status | Workflow | CTA  |
|-------------------------------------------------------------------------------   |
| 2026-07-21 | LUNCH | Nasi Ayam | 500 | 15000 | DRAFT | DRAFT | Submit          |
| 2026-07-22 | LUNCH | Nasi Ikan | 600 | 15500 | APPROVED | PENDING | Reserve    |
+----------------------------------------------------------------------------------+
| Footer State: pagination | total count                                           |
+----------------------------------------------------------------------------------+
```

### Row Actions

- open detail
- submit
- approve
- reserve materials
- open workflow

## 7. Meal Plan Detail

```text
+----------------------------------------------------------------------------------+
| Header: Meal Plan Detail                                                         |
| Meta: Plan Date | Meal Type | Recipe | SPPG | Status Badge | Workflow Badge      |
+----------------------------------------------------------------------------------+
| Action Bar: [Submit] [Approve] [Reserve Materials] [View Workflow] [Cost Preview]|
+----------------------------------------------------------------------------------+
| Summary Cards                                                                    |
| [Planned Portions] [Budget per Portion] [Estimated Total Cost]                   |
+----------------------------------------------------------------------------------+
| Tabs                                                                             |
| [Summary] [Material Requirements] [Cost Preview] [Workflow] [Related Docs]       |
+----------------------------------------------------------------------------------+
| Summary Tab                                                                      |
| - basic meal plan fields                                                         |
| - notes                                                                          |
| - linked recipe                                                                  |
|----------------------------------------------------------------------------------|
| Material Requirements Tab                                                        |
| Product | Net Qty | Gross Qty | UoM                                              |
|----------------------------------------------------------------------------------|
| Cost Preview Tab                                                                 |
| Product | Gross Qty | Unit Cost | Total Cost                                     |
|----------------------------------------------------------------------------------|
| Workflow Tab                                                                     |
| current state                                                                    |
| approval requests                                                                |
| history timeline                                                                 |
+----------------------------------------------------------------------------------+
```

## 8. Purchase Request List

```text
+----------------------------------------------------------------------------------+
| Header: Purchase Requests                                                        |
| Subtitle: kebutuhan pembelian dari meal plan dan shortage stok                   |
+----------------------------------------------------------------------------------+
| Toolbar: [Search] [Status] [SPPG] [Date Range] [Create from Meal Plan]           |
+----------------------------------------------------------------------------------+
| Table                                                                            |
| PR Number | Meal Plan | SPPG | Estimated Total | Status | Notes | CTA            |
+----------------------------------------------------------------------------------+
| Side Panel on row click                                                          |
| - purchase request summary                                                       |
| - line items                                                                     |
| - related meal plan                                                              |
| - create PO/RFQ button                                                           |
+----------------------------------------------------------------------------------+
```

## 9. Purchase Order Detail

```text
+----------------------------------------------------------------------------------+
| Header: Purchase Order Detail                                                    |
| Meta: Order Number | Supplier | Order Date | Expected Date | Status              |
+----------------------------------------------------------------------------------+
| Action Bar: [Receive Goods] [Open Supplier] [View Purchase Request]              |
+----------------------------------------------------------------------------------+
| Summary Block                                                                    |
| supplier info                                                                    |
| notes                                                                            |
+----------------------------------------------------------------------------------+
| Lines Table                                                                      |
| Product | Qty | UoM | Unit Price | Total | Line Status                           |
+----------------------------------------------------------------------------------+
| Related Block                                                                    |
| linked goods receipts                                                            |
| linked supplier invoices                                                         |
+----------------------------------------------------------------------------------+
```

## 10. Goods Receipt Form

```text
+----------------------------------------------------------------------------------+
| Header: Create Goods Receipt                                                     |
| Context: from Purchase Order / from Purchase Request                             |
+----------------------------------------------------------------------------------+
| Form                                                                             |
| Warehouse [dropdown]                                                             |
| Stock Location [dropdown]                                                        |
| Receipt Date [date]                                                              |
| Notes [textarea]                                                                 |
+----------------------------------------------------------------------------------+
| Lines / Batch Section                                                            |
| Product | Ordered Qty | Receive Qty | Batch Number | Expiry | Quality Status     |
+----------------------------------------------------------------------------------+
| Footer Actions                                                                   |
| [Cancel] [Create Goods Receipt]                                                  |
+----------------------------------------------------------------------------------+
```

### UX Notes

- batch fields hanya tampil untuk produk yang butuh tracking
- expiry dan quality cocok dibuat inline editable row

## 11. Inventory Balance List

```text
+----------------------------------------------------------------------------------+
| Header: Inventory Balances                                                       |
| Subtitle: saldo stok aktual per warehouse dan lokasi                             |
+----------------------------------------------------------------------------------+
| Toolbar: [Search Product] [Warehouse] [Location] [Low Stock Only] [Export]       |
+----------------------------------------------------------------------------------+
| Table                                                                            |
| Warehouse | Location | Product | On Hand | Reserved | Available | Avg Cost       |
+----------------------------------------------------------------------------------+
| Side Panel                                                                       |
| product summary                                                                  |
| recent transactions                                                              |
| open FEFO preview                                                                |
+----------------------------------------------------------------------------------+
```

## 12. Inventory Batch List

```text
+----------------------------------------------------------------------------------+
| Header: Inventory Batches                                                        |
| Subtitle: FEFO, expiry, dan traceability                                         |
+----------------------------------------------------------------------------------+
| Toolbar: [Search Batch] [Product] [Warehouse] [Near Expiry] [Blocked Only]       |
+----------------------------------------------------------------------------------+
| Table                                                                            |
| Batch | Product | Warehouse | Expiry | Quality | Blocked | Available | CTA       |
+----------------------------------------------------------------------------------+
| CTA: Open Detail / FEFO Preview                                                  |
+----------------------------------------------------------------------------------+
```

## 13. FEFO Preview Tool

```text
+--------------------------------------------------------------+
| Header: FEFO Preview                                         |
|--------------------------------------------------------------|
| Product [dropdown]                                           |
| Warehouse [dropdown]                                         |
| Required Quantity [number]                                   |
| [ Preview ]                                                  |
|--------------------------------------------------------------|
| Result                                                       |
| Fulfilled Quantity: 10                                       |
| Shortage Quantity: 0                                         |
|--------------------------------------------------------------|
| Candidate Batches                                            |
| Batch | Expiry | Available | Suggested Issue Qty            |
+--------------------------------------------------------------+
```

## 14. Production Order List

```text
+----------------------------------------------------------------------------------+
| Header: Production Orders                                                        |
| Toolbar: [Search] [Status] [SPPG] [Date Range]                                   |
+----------------------------------------------------------------------------------+
| Table                                                                            |
| Prod Number | Meal Plan | SPPG | Portions | Status | Actual Cost | CTA           |
+----------------------------------------------------------------------------------+
| CTA: Open Detail / Complete Production / Create Delivery                         |
+----------------------------------------------------------------------------------+
```

## 15. Production Order Detail

```text
+----------------------------------------------------------------------------------+
| Header: Production Order Detail                                                  |
| Meta: Order Number | SPPG | Status | Meal Plan Link                              |
+----------------------------------------------------------------------------------+
| Action Bar: [Complete Production] [View Cost Sheet] [Create Delivery Order]      |
+----------------------------------------------------------------------------------+
| Summary Cards                                                                    |
| [Actual Portions] [Accepted Portions] [Rejected Portions] [Actual Cost/Portion]  |
+----------------------------------------------------------------------------------+
| Tabs                                                                             |
| [Summary] [Materials] [Cost Sheet] [Related Meal Plan]                           |
+----------------------------------------------------------------------------------+
```

## 16. Delivery Order List

```text
+----------------------------------------------------------------------------------+
| Header: Delivery Orders                                                          |
| Subtitle: pengiriman dari produksi ke sekolah                                    |
+----------------------------------------------------------------------------------+
| Toolbar: [Search] [Status] [SPPG] [Date] [Only With Incident]                    |
+----------------------------------------------------------------------------------+
| Table                                                                            |
| Delivery No | School | Production Order | Planned Arrival | Status | CTA         |
+----------------------------------------------------------------------------------+
| CTA: Open Detail / Record Proof / Record Incident                                |
+----------------------------------------------------------------------------------+
```

## 17. Delivery Order Detail

```text
+----------------------------------------------------------------------------------+
| Header: Delivery Order Detail                                                    |
| Meta: Delivery Number | School | Status | Receiver | Planned Arrival             |
+----------------------------------------------------------------------------------+
| Action Bar: [Record Proof] [Record Incident] [Open Route]                        |
+----------------------------------------------------------------------------------+
| Tabs                                                                             |
| [Summary] [Route] [Proof] [Incidents] [Related Production]                       |
+----------------------------------------------------------------------------------+
| Proof Tab                                                                        |
| photos                                                                           |
| signature                                                                        |
| temperature                                                                      |
| received/rejected portions                                                       |
| receiver GPS                                                                     |
+----------------------------------------------------------------------------------+
| Incidents Tab                                                                    |
| timeline cards per incident                                                      |
+----------------------------------------------------------------------------------+
```

## 18. Delivery Proof Form

```text
+----------------------------------------------------------------------------------+
| Header: Record Delivery Proof                                                    |
+----------------------------------------------------------------------------------+
| Form                                                                             |
| Received At [datetime]                                                           |
| Receiver Name [text]                                                             |
| Receiver GPS [text / device capture]                                             |
| Route Stop [dropdown]                                                            |
| Received Portions [number]                                                       |
| Rejected Portions [number]                                                       |
| Temperature [number]                                                             |
| Condition Status [dropdown]                                                      |
| Condition Notes [textarea]                                                       |
| Photo Upload / URL list                                                          |
| Signature Name [text]                                                            |
| Signature Upload / URL                                                           |
| Signature Time [datetime]                                                        |
| Incident Notes [textarea]                                                        |
| Linked Incidents [multi-select]                                                  |
+----------------------------------------------------------------------------------+
| Footer Actions                                                                   |
| [Cancel] [Submit Proof]                                                          |
+----------------------------------------------------------------------------------+
```

## 19. Budget List

```text
+----------------------------------------------------------------------------------+
| Header: Budgets                                                                  |
| Toolbar: [Search] [Status] [Date Range] [Create Budget]                          |
+----------------------------------------------------------------------------------+
| Table                                                                            |
| Budget Name | Period | Version | Status | Effective Budget | Available | CTA     |
+----------------------------------------------------------------------------------+
| CTA: Open Detail / Submit / Approve / Availability                               |
+----------------------------------------------------------------------------------+
```

## 20. Budget Detail

```text
+----------------------------------------------------------------------------------+
| Header: Budget Detail                                                            |
| Meta: Budget Name | Period | Version | Status                                    |
+----------------------------------------------------------------------------------+
| Action Bar: [Submit] [Approve] [View Availability]                               |
+----------------------------------------------------------------------------------+
| Tabs                                                                             |
| [Summary] [Lines] [Availability] [Workflow]                                      |
+----------------------------------------------------------------------------------+
| Lines Tab                                                                        |
| Category | Account | Planned | Reserved | Committed | Actual | Available         |
+----------------------------------------------------------------------------------+
```

## 21. Journal Entry List

```text
+----------------------------------------------------------------------------------+
| Header: Journal Entries                                                          |
| Toolbar: [Search Reference] [Status] [Date Range] [Create Journal Entry]         |
+----------------------------------------------------------------------------------+
| Table                                                                            |
| Entry Number | Date | Reference | Source Module | Status | CTA                   |
+----------------------------------------------------------------------------------+
| CTA: Open Detail / Post Journal                                                  |
+----------------------------------------------------------------------------------+
```

## 22. Government Claim Detail

```text
+----------------------------------------------------------------------------------+
| Header: Government Claim Detail                                                  |
| Meta: Claim Number | SPPG | Status | Total Amount | Outstanding                  |
+----------------------------------------------------------------------------------+
| Action Bar: [Submit Claim] [Verify Claim] [Record Payment]                       |
+----------------------------------------------------------------------------------+
| Tabs                                                                             |
| [Summary] [Adjustments] [Payments] [Evidence] [Related Deliveries]               |
+----------------------------------------------------------------------------------+
```

## 23. Workflow Definition Detail

```text
+----------------------------------------------------------------------------------+
| Header: Workflow Definition Detail                                               |
| Meta: Code | Document Type | Initial State | Active                              |
+----------------------------------------------------------------------------------+
| Action Bar: [Create Version] [Add Transition] [Add State] [Add Action]           |
+----------------------------------------------------------------------------------+
| Tabs                                                                             |
| [Definition] [Versions] [States] [Actions] [Transitions]                         |
+----------------------------------------------------------------------------------+
| Versions Tab                                                                     |
| Version No | Status | Active | Notes                                             |
+----------------------------------------------------------------------------------+
| States Tab                                                                       |
| State Code | Name | Sequence | Initial | Terminal | SLA                          |
+----------------------------------------------------------------------------------+
| Actions Tab                                                                      |
| Action Code | Name | Allowed Role | Requires Approval | Active                   |
+----------------------------------------------------------------------------------+
| Transitions Tab                                                                  |
| From State | Action | To State | Allowed Role | Requires Approval                |
+----------------------------------------------------------------------------------+
```

## 24. Workflow Document Viewer

```text
+----------------------------------------------------------------------------------+
| Header: Workflow Document Viewer                                                 |
| Meta: Document Type | Document ID | Current State | Last Action                  |
+----------------------------------------------------------------------------------+
| Action Bar: [Approve] [Reject] [Create Approval Request]                         |
+----------------------------------------------------------------------------------+
| Top Summary                                                                      |
| Definition | Version | Current State | Last Action                               |
+----------------------------------------------------------------------------------+
| Two Column Layout                                                                |
| Left: History Timeline                                                           |
| Right: Approval Requests / Approval Decisions                                    |
+----------------------------------------------------------------------------------+
```

## 25. Sync Job Detail

```text
+----------------------------------------------------------------------------------+
| Header: Sync Job Detail                                                          |
| Meta: Job Name | Direction | Entity Type | Status | Trigger Mode                 |
+----------------------------------------------------------------------------------+
| Action Bar: [Run Sync Job] [Open External System]                                |
+----------------------------------------------------------------------------------+
| Tabs                                                                             |
| [Summary] [Outbound Messages] [Inbound Messages] [Sync Logs]                     |
+----------------------------------------------------------------------------------+
| Sync Logs Tab                                                                    |
| log cards or table with status, idempotency key, processed time                  |
+----------------------------------------------------------------------------------+
```

## 26. Sync Log Detail

```text
+----------------------------------------------------------------------------------+
| Header: Sync Log Detail                                                          |
| Meta: Direction | Message Type | Status | Idempotency Key                        |
+----------------------------------------------------------------------------------+
| Summary Block                                                                    |
| entity type                                                                      |
| entity id                                                                        |
| external reference                                                               |
| processed at                                                                     |
+----------------------------------------------------------------------------------+
| Two Column Layout                                                                |
| Left: Payload JSON viewer                                                        |
| Right: Response JSON viewer                                                      |
+----------------------------------------------------------------------------------+
```

## 27. GIS Service Area Editor

```text
+----------------------------------------------------------------------------------+
| Header: Service Area Editor                                                      |
| Meta: Kitchen/SPPG | Active Polygon / Draft                                      |
+----------------------------------------------------------------------------------+
| Toolbar: [Select Kitchen] [Draw Polygon] [Import GeoJSON] [Save]                 |
+----------------------------------------------------------------------------------+
| Main Layout                                                                      |
| Left Panel                                                                       |
| - selected kitchen                                                               |
| - service radius                                                                 |
| - polygon metadata                                                               |
| - validation result                                                              |
|----------------------------------------------------------------------------------|
| Right Panel                                                                      |
| full-size map                                                                    |
| polygon drawing/editing                                                          |
+----------------------------------------------------------------------------------+
```

## 28. AI NL2SQL Workspace

```text
+----------------------------------------------------------------------------------+
| Header: NL2SQL Workspace                                                         |
+----------------------------------------------------------------------------------+
| Input Panel                                                                      |
| Natural Language Question [textarea]                                             |
| [ Generate SQL ]                                                                 |
+----------------------------------------------------------------------------------+
| Result Layout                                                                    |
| Left: Generated SQL                                                              |
| Right: Explanation / Assumptions / Safety Notes                                  |
+----------------------------------------------------------------------------------+
| Footer Actions                                                                   |
| [Copy SQL] [Ask Another Question]                                                |
+----------------------------------------------------------------------------------+
```

## 29. Mobile Priorities

Layar yang harus dirancang mobile-first:

- login
- notification inbox
- delivery proof form
- delivery incident form
- QC inspection form
- attendance form
- AI image/video analysis form

## 30. Required UI States Per Screen

Setiap layar minimal harus punya:

1. `loading`
2. `empty`
3. `error`
4. `permission denied`
5. `conflict/business error`

Contoh:

- meal plan approve gagal karena workflow mismatch
- reserve materials gagal karena stok tidak cukup
- approval decision gagal karena request sudah tidak pending

## 31. Next Design Artifacts

Setelah dokumen wireframe ini, artefak berikut yang direkomendasikan:

1. component inventory
2. design token
3. responsive layout grid rules
4. state diagram UI untuk meal plan, procurement, delivery, workflow
