# Dokumentasi Teknis Backend ERP Pengelolaan Dapur MBG
## Versi 2 — Accounting, Budget Control, Product, UoM, Recipe, Production, Inventory, dan Costing

## 1. Status Dokumen

Dokumen ini merupakan revisi dan perluasan dari dokumentasi teknis backend ERP Pengelolaan Dapur MBG berbasis FastAPI. Bagian baru dan bagian yang diperbarui berfokus pada:

1. General Ledger dan double-entry accounting.
2. Budget controlling berbasis planned, reserved, committed, actual, dan available.
3. Multi-dimensional journal tanpa ketergantungan pada analytic account.
4. Pendanaan investor dan klaim pemerintah.
5. Master produk dan kategori produk.
6. Unit of Measure (UoM) dan konversi satuan.
7. Packaging pembelian yang spesifik per produk.
8. Recipe, menu component, dan paket MBG.
9. Material requirement planning.
10. Produksi, konsumsi aktual, waste, yield, dan cost per porsi.
11. Inventory ledger, batch, expiry, FEFO, dan valuasi persediaan.
12. Integrasi transaksi operasional dengan budget dan jurnal accounting.

Seluruh primary key dan foreign key entitas utama menggunakan PostgreSQL native `UUID`.

---

# Bagian A — Prinsip Desain Keuangan

## 2. Karakter Accounting ERP Dapur MBG

ERP Dapur MBG tidak dirancang sebagai sistem penjualan retail. Sumber pengembalian dana berasal dari pembayaran pemerintah atas pelaksanaan program, sementara modal kerja awal dapat berasal dari investor atau sumber pendanaan lain.

Pusat proses finansial adalah:

```text
Pendanaan Investor
        ↓
Alokasi Anggaran
        ↓
Reservasi dan Komitmen
        ↓
Pengadaan / Biaya Operasional
        ↓
Produksi dan Distribusi
        ↓
Laporan Realisasi
        ↓
Klaim Pemerintah
        ↓
Pembayaran Pemerintah
        ↓
Pengembalian Modal dan Pembagian Keuntungan
```

Sistem keuangan dipisahkan menjadi tiga lapisan:

```text
General Ledger
    └── sumber kebenaran akuntansi resmi

Budget Control
    └── planned, reserved, committed, actual, available

Operational Costing
    └── biaya produksi, distribusi, waste, dan cost per porsi
```

Ketiga nilai tersebut saling berhubungan tetapi tidak boleh dianggap identik.

Contoh:

- Pembelian beras dapat menjadi `actual budget` ketika invoice supplier diposting.
- Nilai beras belum menjadi `production cost` sampai bahan benar-benar dikonsumsi.
- Pembayaran supplier mengubah kas dan hutang, tetapi tidak menambah biaya produksi lagi.

---

## 3. Mengapa CoA Saja Tidak Cukup

Chart of Accounts hanya menentukan klasifikasi finansial:

```text
Uang dicatat pada akun apa?
```

Budget control harus menjawab:

```text
Dapur mana?
Periode mana?
Sumber dana mana?
Kontrak mana?
Kategori anggaran mana?
Berapa anggaran tersedia?
Berapa yang sudah dipesan?
Berapa yang sudah direalisasikan?
```

Karena itu, sistem menggunakan:

1. `accounts` untuk klasifikasi General Ledger.
2. `budget_categories` untuk klasifikasi kontrol anggaran.
3. dimensi pada jurnal untuk dapur, fund, kontrak, meal plan, dan produksi.
4. tabel mapping akun ke kategori anggaran.
5. detail reservation, commitment, dan actual link untuk audit.

---

# Bagian B — Struktur Modul FastAPI

## 4. Modul yang Diperbarui

```text
app/modules/
├── product/
├── uom/
├── recipe/
├── meal_plan/
├── procurement/
├── inventory/
├── production/
├── costing/
├── budget/
├── funding/
├── government_claim/
├── accounting/
└── reporting/
```

Setiap modul mengikuti pola:

```text
module_name/
├── routes/
├── services/
├── repositories/
├── models/
├── schemas/
├── policies/
├── events/
├── exceptions/
├── dependencies.py
├── constants.py
├── manifest.py
└── tests/
```

Aturan dependensi:

```text
routes
  ↓
services
  ↓
repositories
  ↓
models / database
```

Komunikasi antar-domain dilakukan melalui:

- application service;
- domain event;
- transactional event handler;
- outbox event untuk proses asynchronous.

Modul tidak boleh mengimpor router modul lain atau melakukan query ad-hoc langsung ke tabel domain lain.

---

# Bagian C — Master Accounting

## 5. `account_types`

```text
account_types
- id UUID PK
- code VARCHAR(30) UNIQUE
- name VARCHAR(100)
- category ENUM
- normal_balance ENUM('DEBIT','CREDIT')
- is_balance_sheet BOOLEAN
- is_active BOOLEAN
```

Nilai `category`:

```text
ASSET
LIABILITY
EQUITY
REVENUE
COST_OF_SERVICE
EXPENSE
MEMORANDUM
```

---

## 6. `accounts`

```text
accounts
- id UUID PK
- tenant_id UUID FK
- parent_id UUID FK nullable
- account_type_id UUID FK
- code VARCHAR(30)
- name VARCHAR(255)
- allow_posting BOOLEAN
- requires_kitchen BOOLEAN
- requires_fund BOOLEAN
- requires_budget_category BOOLEAN
- requires_government_contract BOOLEAN
- is_reconciliation BOOLEAN
- is_active BOOLEAN
- created_at TIMESTAMPTZ
- updated_at TIMESTAMPTZ
```

Constraint:

```text
UNIQUE (tenant_id, code)
```

Contoh CoA:

```text
100000 ASET
110000 Kas dan Bank
120000 Piutang Pemerintah
130000 Persediaan Bahan
131000 Persediaan Kemasan
140000 Uang Muka Supplier

200000 LIABILITAS
210000 Hutang Supplier
220000 Hutang Tenaga Kerja
230000 Hutang Pajak
240000 Barang Diterima Belum Ditagih

300000 EKUITAS
310000 Modal Investor
320000 Saldo Laba
330000 Distribusi Laba Investor

400000 PENDAPATAN
410000 Pendapatan Klaim Pemerintah
420000 Pendapatan Hibah
430000 Pendapatan Lain

500000 BIAYA LAYANAN
510000 Biaya Bahan
520000 Biaya Tenaga Kerja
530000 Biaya Utilitas
540000 Biaya Kemasan
550000 Biaya Distribusi
560000 Biaya Pemeliharaan
570000 Penyusutan
580000 Waste dan Selisih Produksi
```

---

## 7. `fiscal_years` dan `fiscal_periods`

```text
fiscal_years
- id UUID PK
- tenant_id UUID FK
- name VARCHAR(100)
- date_start DATE
- date_end DATE
- status ENUM('DRAFT','OPEN','CLOSED')
```

```text
fiscal_periods
- id UUID PK
- tenant_id UUID FK
- fiscal_year_id UUID FK
- period_number SMALLINT
- name VARCHAR(100)
- date_start DATE
- date_end DATE
- status ENUM('OPEN','SOFT_CLOSED','CLOSED')
```

Jurnal tidak dapat diposting pada periode `CLOSED`.

---

## 8. `journal_types`, `journals`, `journal_entries`, dan `journal_lines`

### 8.1 `journal_types`

```text
journal_types
- id UUID PK
- code VARCHAR(30)
- name VARCHAR(100)
```

Contoh:

```text
GENERAL
PURCHASE
PAYMENT
INVENTORY
PRODUCTION
PAYROLL
CLAIM
ADJUSTMENT
CLOSING
```

### 8.2 `journals`

```text
journals
- id UUID PK
- tenant_id UUID FK
- journal_type_id UUID FK
- code VARCHAR(30)
- name VARCHAR(255)
- sequence_prefix VARCHAR(30)
- default_debit_account_id UUID FK nullable
- default_credit_account_id UUID FK nullable
- is_active BOOLEAN
```

### 8.3 `journal_entries`

```text
journal_entries
- id UUID PK
- tenant_id UUID FK
- journal_id UUID FK
- fiscal_period_id UUID FK
- entry_number VARCHAR(50)
- entry_date DATE
- reference VARCHAR(255) nullable
- description TEXT
- source_module VARCHAR(50)
- source_document_type VARCHAR(50)
- source_document_id UUID nullable
- status ENUM('DRAFT','POSTED','REVERSED')
- reversal_entry_id UUID FK nullable
- posted_at TIMESTAMPTZ nullable
- posted_by UUID FK nullable
- created_at TIMESTAMPTZ
- updated_at TIMESTAMPTZ
```

Unique idempotency:

```text
UNIQUE (
    tenant_id,
    source_module,
    source_document_type,
    source_document_id
)
```

### 8.4 `journal_lines`

```text
journal_lines
- id UUID PK
- tenant_id UUID FK
- journal_entry_id UUID FK
- account_id UUID FK
- description VARCHAR(255)
- debit NUMERIC(20,2)
- credit NUMERIC(20,2)
- currency_id UUID FK
- amount_currency NUMERIC(20,2) nullable

- kitchen_id UUID FK nullable
- fund_id UUID FK nullable
- budget_category_id UUID FK nullable
- government_contract_id UUID FK nullable
- meal_plan_id UUID FK nullable
- production_order_id UUID FK nullable

- product_id UUID FK nullable
- supplier_id UUID FK nullable
- employee_id UUID FK nullable

- due_date DATE nullable
- reconciliation_status ENUM('OPEN','PARTIAL','RECONCILED')
- created_at TIMESTAMPTZ
```

Constraint line:

```sql
CHECK (
    (debit > 0 AND credit = 0)
    OR
    (credit > 0 AND debit = 0)
);
```

Constraint entry pada saat posting:

```text
SUM(debit) = SUM(credit)
```

Jurnal `POSTED` tidak boleh diedit atau dihapus. Koreksi dilakukan dengan reversal dan replacement entry.

---

## 9. Multi-Dimensional Journal

Sistem tidak memerlukan konsep analytic account tunggal. Dimensi disimpan langsung pada journal line.

Dimensi utama:

```text
kitchen_id
fund_id
budget_category_id
government_contract_id
meal_plan_id
production_order_id
product_id
supplier_id
employee_id
```

Manfaat:

- profit and loss per dapur;
- biaya per kontrak;
- biaya per meal plan;
- penggunaan dana per investor/fund;
- cost per production order;
- biaya per produk atau kategori produk.

Apabila satu journal line perlu dibagi ke banyak dapur atau fund, gunakan:

```text
journal_line_allocations
- id UUID PK
- tenant_id UUID FK
- journal_line_id UUID FK
- kitchen_id UUID FK nullable
- fund_id UUID FK nullable
- budget_category_id UUID FK nullable
- government_contract_id UUID FK nullable
- meal_plan_id UUID FK nullable
- production_order_id UUID FK nullable
- percentage NUMERIC(8,4) nullable
- allocated_amount NUMERIC(20,2)
```

Aturan:

- journal line sederhana memakai dimensi langsung;
- journal line yang di-split memakai allocation;
- dua pendekatan tidak digunakan bersamaan pada line yang sama.

---

# Bagian D — Funding dan Investor

## 10. `investors`

```text
investors
- id UUID PK
- tenant_id UUID FK
- code VARCHAR(50)
- name VARCHAR(255)
- investor_type ENUM('INDIVIDUAL','COMPANY','INSTITUTION')
- tax_number VARCHAR(100) nullable
- contact_data JSONB nullable
- is_active BOOLEAN
```

## 11. `funds`

Fund adalah kumpulan sumber pembiayaan operasional.

```text
funds
- id UUID PK
- tenant_id UUID FK
- code VARCHAR(50)
- name VARCHAR(255)
- fund_type ENUM('INVESTOR','GOVERNMENT','GRANT','INTERNAL')
- currency_id UUID FK
- date_start DATE
- date_end DATE nullable
- status ENUM('DRAFT','ACTIVE','CLOSED')
```

## 12. `fund_investors`

```text
fund_investors
- id UUID PK
- tenant_id UUID FK
- fund_id UUID FK
- investor_id UUID FK
- committed_amount NUMERIC(20,2)
- paid_amount NUMERIC(20,2)
- ownership_percentage NUMERIC(8,4) nullable
- profit_share_percentage NUMERIC(8,4) nullable
- date_joined DATE
```

Jurnal penerimaan modal:

```text
Dr Bank
    Cr Modal Investor
```

`fund_id` dibawa pada journal line terkait.

---

# Bagian E — Budget Control

## 13. `budget_categories`

Budget category tidak sama dengan CoA.

```text
budget_categories
- id UUID PK
- tenant_id UUID FK
- parent_id UUID FK nullable
- code VARCHAR(50)
- name VARCHAR(255)
- category_group ENUM(
    'MATERIAL',
    'LABOR',
    'UTILITY',
    'PACKAGING',
    'DISTRIBUTION',
    'MAINTENANCE',
    'ADMINISTRATION',
    'CAPEX',
    'OTHER'
  )
- default_control_mode ENUM('NONE','WARNING','APPROVAL','BLOCKING')
- is_active BOOLEAN
```

Contoh:

```text
MATERIAL
├── MATERIAL_RICE
├── MATERIAL_ANIMAL_PROTEIN
├── MATERIAL_PLANT_PROTEIN
├── MATERIAL_VEGETABLE
├── MATERIAL_FRUIT
└── MATERIAL_SEASONING

LABOR
├── LABOR_PRODUCTION
└── LABOR_DISTRIBUTION

UTILITY
├── ELECTRICITY
├── GAS
└── WATER
```

---

## 14. `account_budget_mappings`

```text
account_budget_mappings
- id UUID PK
- tenant_id UUID FK
- account_id UUID FK
- budget_category_id UUID FK
- effective_from DATE
- effective_to DATE nullable
- is_active BOOLEAN
```

Untuk versi awal, satu akun biaya hanya memiliki satu mapping aktif dalam tanggal yang sama.

---

## 15. `budgets` dan `budget_lines`

### 15.1 `budgets`

```text
budgets
- id UUID PK
- tenant_id UUID FK
- budget_number VARCHAR(50)
- name VARCHAR(255)
- fiscal_year_id UUID FK
- kitchen_id UUID FK nullable
- fund_id UUID FK nullable
- government_contract_id UUID FK nullable
- date_start DATE
- date_end DATE
- version_number INTEGER
- parent_budget_id UUID FK nullable
- status ENUM(
    'DRAFT',
    'SUBMITTED',
    'APPROVED',
    'ACTIVE',
    'CLOSED',
    'CANCELLED'
  )
- approved_by UUID FK nullable
- approved_at TIMESTAMPTZ nullable
- notes TEXT nullable
```

### 15.2 `budget_lines`

```text
budget_lines
- id UUID PK
- tenant_id UUID FK
- budget_id UUID FK
- fiscal_period_id UUID FK nullable
- budget_category_id UUID FK
- account_id UUID FK nullable
- planned_amount NUMERIC(20,2)
- revised_amount NUMERIC(20,2) nullable
- control_mode ENUM('NONE','WARNING','APPROVAL','BLOCKING')
- tolerance_percentage NUMERIC(8,4) DEFAULT 0
- cached_reserved_amount NUMERIC(20,2) DEFAULT 0
- cached_committed_amount NUMERIC(20,2) DEFAULT 0
- cached_actual_amount NUMERIC(20,2) DEFAULT 0
- notes TEXT nullable
```

Rumus:

```text
Effective Budget =
COALESCE(revised_amount, planned_amount)

Available Budget =
Effective Budget
- Active Reservation
- Active Commitment
- Actual Realization
```

Kolom cached bukan sumber audit. Sumber audit tetap berasal dari tabel detail.

---

## 16. Reservasi Budget

### 16.1 `budget_reservations`

```text
budget_reservations
- id UUID PK
- tenant_id UUID FK
- reservation_number VARCHAR(50)
- reservation_date DATE
- kitchen_id UUID FK
- fund_id UUID FK nullable
- source_document_type VARCHAR(50)
- source_document_id UUID
- status ENUM(
    'DRAFT',
    'SUBMITTED',
    'APPROVED',
    'PARTIALLY_CONSUMED',
    'CONSUMED',
    'RELEASED',
    'REJECTED',
    'CANCELLED'
  )
- requested_by UUID FK
- approved_by UUID FK nullable
- approved_at TIMESTAMPTZ nullable
- description TEXT nullable
```

### 16.2 `budget_reservation_lines`

```text
budget_reservation_lines
- id UUID PK
- tenant_id UUID FK
- reservation_id UUID FK
- budget_line_id UUID FK
- budget_category_id UUID FK
- account_id UUID FK nullable
- requested_amount NUMERIC(20,2)
- approved_amount NUMERIC(20,2)
- consumed_amount NUMERIC(20,2) DEFAULT 0
- released_amount NUMERIC(20,2) DEFAULT 0
- description TEXT nullable
```

Reservasi tidak membuat jurnal accounting.

---

## 17. Commitment Budget

### 17.1 `budget_commitments`

```text
budget_commitments
- id UUID PK
- tenant_id UUID FK
- commitment_number VARCHAR(50)
- commitment_date DATE
- kitchen_id UUID FK
- fund_id UUID FK nullable
- source_document_type VARCHAR(50)
- source_document_id UUID
- supplier_id UUID FK nullable
- employee_id UUID FK nullable
- status ENUM(
    'ACTIVE',
    'PARTIALLY_ACTUALIZED',
    'ACTUALIZED',
    'RELEASED',
    'CANCELLED'
  )
```

### 17.2 `budget_commitment_lines`

```text
budget_commitment_lines
- id UUID PK
- tenant_id UUID FK
- commitment_id UUID FK
- budget_line_id UUID FK
- reservation_line_id UUID FK nullable
- account_id UUID FK
- budget_category_id UUID FK
- committed_amount NUMERIC(20,2)
- actualized_amount NUMERIC(20,2) DEFAULT 0
- released_amount NUMERIC(20,2) DEFAULT 0
```

Transisi:

```text
Reservation approved
        ↓
Purchase Order approved
        ↓
reserved berkurang
committed bertambah
```

---

## 18. Actual Budget

```text
budget_actual_links
- id UUID PK
- tenant_id UUID FK
- budget_line_id UUID FK
- journal_line_id UUID FK
- commitment_line_id UUID FK nullable
- actual_amount NUMERIC(20,2)
- recognized_date DATE
- reversal_of_id UUID FK nullable
```

Tabel ini memungkinkan satu journal line di-split ke lebih dari satu budget line.

---

## 19. Revisi dan Transfer Budget

```text
budget_revisions
- id UUID PK
- tenant_id UUID FK
- budget_id UUID FK
- revision_number INTEGER
- revision_date DATE
- reason TEXT
- status ENUM('DRAFT','SUBMITTED','APPROVED','REJECTED')
- requested_by UUID FK
- approved_by UUID FK nullable
- approved_at TIMESTAMPTZ nullable
```

```text
budget_revision_lines
- id UUID PK
- tenant_id UUID FK
- budget_revision_id UUID FK
- budget_line_id UUID FK
- previous_amount NUMERIC(20,2)
- change_amount NUMERIC(20,2)
- new_amount NUMERIC(20,2)
- reason TEXT nullable
```

```text
budget_transfers
- id UUID PK
- tenant_id UUID FK
- transfer_number VARCHAR(50)
- transfer_date DATE
- source_budget_line_id UUID FK
- destination_budget_line_id UUID FK
- amount NUMERIC(20,2)
- reason TEXT
- status ENUM('DRAFT','SUBMITTED','APPROVED','REJECTED','POSTED')
- approved_by UUID FK nullable
```

Budget transfer tidak membuat jurnal GL karena tidak terjadi perubahan aset, liabilitas, ekuitas, pendapatan, atau biaya.

---

# Bagian F — Master Produk dan UoM

## 20. UoM Wajib Digunakan

UoM merupakan komponen inti, karena:

- bahan dibeli dalam sak, dus, karton, tray, atau botol;
- stock disimpan dalam kg, liter, atau pcs;
- recipe memakai gram, ml, atau porsi;
- produksi menghasilkan porsi atau paket;
- biaya harus dihitung dalam satuan stock yang konsisten.

Contoh:

```text
Beras dibeli: sak 25 kg
Stock: kilogram
Recipe: gram
Output: porsi
```

Tanpa UoM dan konversi, inventory serta cost calculation tidak dapat dijaga akurasinya.

---

## 21. `uom_categories`

```text
uom_categories
- id UUID PK
- tenant_id UUID FK nullable
- code VARCHAR(30)
- name VARCHAR(100)
- dimension ENUM('WEIGHT','VOLUME','UNIT','LENGTH','AREA','TIME')
- is_active BOOLEAN
```

Kategori global dapat memiliki `tenant_id = NULL`.

---

## 22. `uoms`

```text
uoms
- id UUID PK
- tenant_id UUID FK nullable
- category_id UUID FK
- code VARCHAR(30)
- name VARCHAR(100)
- symbol VARCHAR(20)
- factor_to_base NUMERIC(20,10)
- rounding NUMERIC(20,10)
- is_base BOOLEAN
- is_active BOOLEAN
```

Contoh:

```text
WEIGHT, base = KG
KG = 1
GRAM = 0.001
TON = 1000

VOLUME, base = LITER
LITER = 1
ML = 0.001
```

Konversi langsung hanya diperbolehkan dalam kategori yang sama.

---

## 23. `product_categories`

```text
product_categories
- id UUID PK
- tenant_id UUID FK
- parent_id UUID FK nullable
- code VARCHAR(50)
- name VARCHAR(255)
- category_type ENUM(
    'MATERIAL',
    'PACKAGING',
    'SEMI_FINISHED',
    'FINISHED',
    'OPERATIONAL',
    'SERVICE'
  )
- inventory_account_id UUID FK nullable
- consumption_account_id UUID FK nullable
- expense_account_id UUID FK nullable
- variance_account_id UUID FK nullable
- budget_category_id UUID FK nullable
- is_stockable BOOLEAN
- is_active BOOLEAN
```

Kategori menyimpan default accounting dan budget mapping.

Contoh hierarki:

```text
BAHAN BAKU
├── Karbohidrat
├── Protein Hewani
├── Protein Nabati
├── Sayur
├── Buah
├── Bumbu
└── Minuman

KEMASAN
├── Kotak Makan
├── Sendok
├── Plastik
└── Label

SETENGAH JADI
├── Nasi Matang
├── Ayam Marinasi
└── Saus

PRODUK JADI
├── Menu Component
└── Paket MBG

OPERASIONAL
├── Gas
├── Kebersihan
└── Peralatan Kecil
```

---

## 24. `products`

```text
products
- id UUID PK
- tenant_id UUID FK
- category_id UUID FK
- code VARCHAR(100)
- barcode VARCHAR(100) nullable
- name VARCHAR(255)
- product_type ENUM(
    'MATERIAL',
    'PACKAGING',
    'SEMI_FINISHED',
    'MENU_COMPONENT',
    'MEAL_PACKAGE',
    'OPERATIONAL',
    'SERVICE'
  )
- stock_uom_id UUID FK
- purchase_uom_id UUID FK nullable
- consumption_uom_id UUID FK nullable
- costing_method ENUM('STANDARD','MOVING_AVERAGE','FIFO')
- standard_cost NUMERIC(20,6) DEFAULT 0
- minimum_stock NUMERIC(20,6) DEFAULT 0
- maximum_stock NUMERIC(20,6) nullable
- reorder_point NUMERIC(20,6) nullable
- shelf_life_days INTEGER nullable
- requires_lot BOOLEAN
- requires_expiry BOOLEAN
- is_perishable BOOLEAN
- is_purchasable BOOLEAN
- is_producible BOOLEAN
- is_claimable BOOLEAN
- is_stockable BOOLEAN
- is_active BOOLEAN
- created_at TIMESTAMPTZ
- updated_at TIMESTAMPTZ
```

Constraint:

```text
UNIQUE (tenant_id, code)
```

Rekomendasi costing:

- bahan pangan: FIFO atau moving average;
- bahan expiry: FEFO untuk pengeluaran fisik, FIFO/moving average untuk valuasi;
- kemasan: moving average;
- produk hasil: actual production cost atau standard cost dengan variance.

---

## 25. Packaging Produk

Packaging seperti sak, dus, karton, dan tray sering bersifat spesifik per produk.

```text
product_packagings
- id UUID PK
- tenant_id UUID FK
- product_id UUID FK
- name VARCHAR(100)
- packaging_uom_id UUID FK
- contained_quantity NUMERIC(20,6)
- contained_uom_id UUID FK
- barcode VARCHAR(100) nullable
- is_purchase_default BOOLEAN
- is_active BOOLEAN
```

Contoh:

```text
Produk: Beras
Packaging: Sak 25 kg
contained_quantity = 25
contained_uom = KG
```

---

## 26. Konversi UoM Spesifik Produk

Digunakan untuk konversi lintas kategori yang bergantung pada produk.

```text
product_uom_conversions
- id UUID PK
- tenant_id UUID FK
- product_id UUID FK
- from_uom_id UUID FK
- to_uom_id UUID FK
- conversion_factor NUMERIC(20,10)
- effective_from DATE
- effective_to DATE nullable
- notes TEXT nullable
```

Contoh:

```text
1 butir telur = 0.06 kg
1 tray telur = 30 butir
```

Konversi spesifik harus mempunyai periode berlaku karena berat aktual dapat berubah.

---

## 27. Supplier dan Harga Produk

```text
product_suppliers
- id UUID PK
- tenant_id UUID FK
- product_id UUID FK
- supplier_id UUID FK
- supplier_product_code VARCHAR(100) nullable
- purchase_uom_id UUID FK
- minimum_order_qty NUMERIC(20,6)
- lead_time_days INTEGER
- is_preferred BOOLEAN
- is_active BOOLEAN
```

```text
product_purchase_prices
- id UUID PK
- tenant_id UUID FK
- product_supplier_id UUID FK
- price NUMERIC(20,6)
- currency_id UUID FK
- effective_from DATE
- effective_to DATE nullable
```

---

# Bagian G — Recipe, Menu, dan Paket MBG

## 28. Pemisahan Konsep

```text
Recipe
    └── formula untuk menghasilkan menu component

Menu Component
    └── nasi, lauk, sayur, buah, minuman

Meal Package
    └── kombinasi menu component dan kemasan untuk satu penerima

Meal Plan
    └── jadwal penggunaan meal package per dapur dan tanggal
```

---

## 29. `recipes`

```text
recipes
- id UUID PK
- tenant_id UUID FK
- product_id UUID FK
- code VARCHAR(50)
- name VARCHAR(255)
- version INTEGER
- output_quantity NUMERIC(20,6)
- output_uom_id UUID FK
- effective_from DATE
- effective_to DATE nullable
- status ENUM('DRAFT','APPROVED','OBSOLETE')
- is_active BOOLEAN
- approved_by UUID FK nullable
- approved_at TIMESTAMPTZ nullable
```

Satu produk dapat memiliki banyak versi recipe, tetapi hanya satu versi aktif pada tanggal tertentu.

---

## 30. `recipe_lines`

```text
recipe_lines
- id UUID PK
- tenant_id UUID FK
- recipe_id UUID FK
- component_product_id UUID FK
- quantity NUMERIC(20,6)
- uom_id UUID FK
- waste_percentage NUMERIC(8,4) DEFAULT 0
- yield_percentage NUMERIC(8,4) nullable
- sequence INTEGER
- is_optional BOOLEAN
```

Contoh recipe ayam kecap untuk 100 porsi:

```text
Ayam       8.0 kg
Kecap      1.5 liter
Bawang     0.5 kg
Minyak     0.8 liter
```

---

## 31. `meal_package_components`

```text
meal_package_components
- id UUID PK
- tenant_id UUID FK
- meal_package_product_id UUID FK
- component_product_id UUID FK
- quantity NUMERIC(20,6)
- uom_id UUID FK
- sequence INTEGER
- is_mandatory BOOLEAN
```

Contoh paket:

```text
Paket MBG A
├── Nasi putih 150 gram
├── Ayam kecap 1 porsi
├── Sayur 1 porsi
├── Pisang 1 pcs
├── Susu 200 ml
└── Kotak makan 1 pcs
```

---

## 32. Meal Plan

```text
meal_plans
- id UUID PK
- tenant_id UUID FK
- kitchen_id UUID FK
- government_contract_id UUID FK nullable
- plan_date DATE
- meal_session ENUM('BREAKFAST','LUNCH','DINNER','OTHER')
- recipient_group_id UUID FK nullable
- target_portions INTEGER
- budget_cost_per_portion NUMERIC(20,6) nullable
- status ENUM(
    'DRAFT',
    'SUBMITTED',
    'APPROVED',
    'MATERIAL_RESERVED',
    'IN_PRODUCTION',
    'COMPLETED',
    'CANCELLED'
  )
- notes TEXT nullable
```

```text
meal_plan_lines
- id UUID PK
- tenant_id UUID FK
- meal_plan_id UUID FK
- meal_package_product_id UUID FK
- planned_portions INTEGER
- claim_price_per_portion NUMERIC(20,6) nullable
- planned_cost_per_portion NUMERIC(20,6) nullable
```

---

# Bagian H — Material Requirement

## 33. Perhitungan Kebutuhan Bahan

Kebutuhan teoritis:

```text
Required Material =
Recipe Quantity
× Target Output
÷ Recipe Base Output
```

Kebutuhan gross:

```text
Gross Requirement =
Required Material
÷ (1 - Waste Percentage)
```

Contoh:

```text
Recipe: 8 kg ayam / 100 porsi
Target: 1.000 porsi
Waste: 10%

Net = 8 × 1000 / 100 = 80 kg
Gross = 80 / 0.90 = 88.8889 kg
```

---

## 34. `material_requirements`

```text
material_requirements
- id UUID PK
- tenant_id UUID FK
- kitchen_id UUID FK
- meal_plan_id UUID FK
- calculation_version INTEGER
- status ENUM('DRAFT','CALCULATED','APPROVED','RESERVED','CLOSED')
- calculated_at TIMESTAMPTZ
- approved_by UUID FK nullable
```

```text
material_requirement_lines
- id UUID PK
- tenant_id UUID FK
- material_requirement_id UUID FK
- product_id UUID FK
- recipe_id UUID FK nullable
- net_quantity NUMERIC(20,6)
- waste_quantity NUMERIC(20,6)
- gross_quantity NUMERIC(20,6)
- uom_id UUID FK
- stock_quantity NUMERIC(20,6)
- stock_uom_id UUID FK
- available_stock NUMERIC(20,6)
- shortage_quantity NUMERIC(20,6)
- estimated_unit_cost NUMERIC(20,6)
- estimated_total_cost NUMERIC(20,2)
```

Material requirement dapat menghasilkan:

- stock reservation;
- purchase request;
- shortage report;
- planned material cost.

---

# Bagian I — Inventory

## 35. Lokasi Stock

```text
stock_locations
- id UUID PK
- tenant_id UUID FK
- kitchen_id UUID FK nullable
- parent_id UUID FK nullable
- code VARCHAR(50)
- name VARCHAR(255)
- location_type ENUM(
    'SUPPLIER',
    'WAREHOUSE',
    'DRY_STORAGE',
    'CHILLER',
    'FREEZER',
    'PRODUCTION',
    'FINISHED_GOODS',
    'DELIVERY',
    'CONSUMPTION',
    'WASTE',
    'ADJUSTMENT'
  )
- is_active BOOLEAN
```

---

## 36. Lot dan Expiry

```text
stock_lots
- id UUID PK
- tenant_id UUID FK
- product_id UUID FK
- lot_number VARCHAR(100)
- supplier_id UUID FK nullable
- production_date DATE nullable
- expiry_date DATE nullable
- received_date DATE
- quality_status ENUM('PENDING','PASSED','REJECTED','QUARANTINED')
- is_blocked BOOLEAN
```

Bahan pangan menggunakan FEFO untuk pemilihan lot:

```text
First Expired, First Out
```

---

## 37. `stock_moves`

```text
stock_moves
- id UUID PK
- tenant_id UUID FK
- kitchen_id UUID FK nullable
- product_id UUID FK
- source_location_id UUID FK
- destination_location_id UUID FK
- lot_id UUID FK nullable

- transaction_quantity NUMERIC(20,6)
- transaction_uom_id UUID FK
- stock_quantity NUMERIC(20,6)
- stock_uom_id UUID FK

- unit_cost NUMERIC(20,6)
- total_cost NUMERIC(20,2)

- move_type ENUM(
    'RECEIPT',
    'ISSUE_TO_PRODUCTION',
    'PRODUCTION_OUTPUT',
    'PRODUCTION_RETURN',
    'INTERNAL_TRANSFER',
    'DELIVERY_ISSUE',
    'ADJUSTMENT_IN',
    'ADJUSTMENT_OUT',
    'WASTE',
    'EXPIRED'
  )

- move_date TIMESTAMPTZ
- source_document_type VARCHAR(50)
- source_document_id UUID
- status ENUM('DRAFT','POSTED','CANCELLED')
- posted_by UUID FK nullable
```

Simpan kuantitas transaksi dan kuantitas stock:

```text
transaction_quantity + transaction_uom_id
stock_quantity + stock_uom_id
```

---

## 38. `stock_balances`

```text
stock_balances
- id UUID PK
- tenant_id UUID FK
- kitchen_id UUID FK nullable
- product_id UUID FK
- location_id UUID FK
- lot_id UUID FK nullable
- quantity_on_hand NUMERIC(20,6)
- reserved_quantity NUMERIC(20,6)
- available_quantity NUMERIC(20,6)
- average_cost NUMERIC(20,6)
- updated_at TIMESTAMPTZ
```

Constraint:

```text
available_quantity =
quantity_on_hand - reserved_quantity
```

`stock_moves` adalah sumber audit. `stock_balances` adalah read model/cache yang dapat direbuild.

---

## 39. Stock Reservation

```text
stock_reservations
- id UUID PK
- tenant_id UUID FK
- kitchen_id UUID FK
- source_document_type VARCHAR(50)
- source_document_id UUID
- status ENUM('ACTIVE','PARTIALLY_CONSUMED','CONSUMED','RELEASED','CANCELLED')
- reserved_at TIMESTAMPTZ
```

```text
stock_reservation_lines
- id UUID PK
- tenant_id UUID FK
- reservation_id UUID FK
- product_id UUID FK
- location_id UUID FK
- lot_id UUID FK nullable
- reserved_quantity NUMERIC(20,6)
- stock_uom_id UUID FK
- consumed_quantity NUMERIC(20,6)
- released_quantity NUMERIC(20,6)
```

---

# Bagian J — Production

## 40. `production_orders`

```text
production_orders
- id UUID PK
- tenant_id UUID FK
- kitchen_id UUID FK
- meal_plan_id UUID FK
- production_number VARCHAR(100)
- production_date DATE
- status ENUM(
    'DRAFT',
    'PLANNED',
    'MATERIAL_RESERVED',
    'IN_PROGRESS',
    'COMPLETED',
    'CANCELLED'
  )
- planned_portions INTEGER
- actual_portions INTEGER
- accepted_portions INTEGER
- rejected_portions INTEGER
- started_at TIMESTAMPTZ nullable
- completed_at TIMESTAMPTZ nullable
```

---

## 41. Konsumsi Material

```text
production_material_consumptions
- id UUID PK
- tenant_id UUID FK
- production_order_id UUID FK
- product_id UUID FK
- planned_quantity NUMERIC(20,6)
- actual_quantity NUMERIC(20,6)
- transaction_uom_id UUID FK
- stock_quantity NUMERIC(20,6)
- stock_uom_id UUID FK
- unit_cost NUMERIC(20,6)
- total_cost NUMERIC(20,2)
- lot_id UUID FK nullable
- stock_move_id UUID FK nullable
```

---

## 42. Output Produksi

```text
production_order_outputs
- id UUID PK
- tenant_id UUID FK
- production_order_id UUID FK
- product_id UUID FK
- planned_quantity NUMERIC(20,6)
- actual_quantity NUMERIC(20,6)
- uom_id UUID FK
- accepted_quantity NUMERIC(20,6)
- rejected_quantity NUMERIC(20,6)
- unit_cost NUMERIC(20,6)
- total_cost NUMERIC(20,2)
- stock_move_id UUID FK nullable
```

---

## 43. Waste Produksi

```text
production_wastes
- id UUID PK
- tenant_id UUID FK
- production_order_id UUID FK
- product_id UUID FK
- quantity NUMERIC(20,6)
- uom_id UUID FK
- waste_type ENUM(
    'TRIMMING',
    'SPOILED',
    'EXPIRED',
    'OVERCOOKED',
    'DAMAGED',
    'PORTION_REJECTED',
    'LEFTOVER',
    'OTHER'
  )
- reason TEXT
- unit_cost NUMERIC(20,6)
- total_cost NUMERIC(20,2)
- stock_move_id UUID FK nullable
```

Yield:

```text
Yield % =
Accepted Output
÷ Expected Output
× 100%
```

---

# Bagian K — Production Costing

## 44. Komponen Cost

```text
Material Cost
+ Packaging Cost
+ Direct Labor
+ Utilities
+ Distribution
+ Allocated Overhead
+ Waste Cost
= Total Production Cost
```

Cost per porsi:

```text
Actual Cost per Accepted Portion =
Total Production Cost
÷ Accepted Portions
```

Gunakan `accepted_portions`, bukan `planned_portions`.

---

## 45. `production_cost_sheets`

```text
production_cost_sheets
- id UUID PK
- tenant_id UUID FK
- kitchen_id UUID FK
- production_order_id UUID FK
- meal_plan_id UUID FK
- status ENUM('DRAFT','CALCULATED','FINALIZED')
- material_cost NUMERIC(20,2)
- packaging_cost NUMERIC(20,2)
- direct_labor_cost NUMERIC(20,2)
- utility_cost NUMERIC(20,2)
- distribution_cost NUMERIC(20,2)
- overhead_cost NUMERIC(20,2)
- waste_cost NUMERIC(20,2)
- total_cost NUMERIC(20,2)
- accepted_portions INTEGER
- cost_per_portion NUMERIC(20,6)
- calculated_at TIMESTAMPTZ
```

```text
production_cost_components
- id UUID PK
- tenant_id UUID FK
- cost_sheet_id UUID FK
- cost_type ENUM(
    'MATERIAL',
    'PACKAGING',
    'LABOR',
    'UTILITY',
    'DISTRIBUTION',
    'OVERHEAD',
    'WASTE'
  )
- source_document_type VARCHAR(50)
- source_document_id UUID
- account_id UUID FK nullable
- product_id UUID FK nullable
- amount NUMERIC(20,2)
```

---

## 46. Planned vs Actual Cost

```text
cost_variances
- id UUID PK
- tenant_id UUID FK
- production_order_id UUID FK
- cost_type VARCHAR(30)
- planned_amount NUMERIC(20,2)
- actual_amount NUMERIC(20,2)
- variance_amount NUMERIC(20,2)
- variance_percentage NUMERIC(10,4)
- reason_code VARCHAR(50) nullable
- notes TEXT nullable
```

Penyebab variance:

- harga beli berubah;
- pemakaian bahan melebihi standar;
- yield rendah;
- waste tinggi;
- porsi reject;
- biaya tenaga kerja tinggi;
- utilitas tidak efisien.

---

# Bagian L — Integrasi Budget, Inventory, dan Accounting

## 47. Kebijakan Pengakuan

Rekomendasi:

```text
Budget Reservation
    saat Purchase Request disetujui

Budget Commitment
    saat Purchase Order disetujui

Budget Actual
    saat Vendor Invoice diposting

Inventory Cost
    saat barang diterima dan dinilai

Production Cost
    saat material dikonsumsi dan biaya dialokasikan
```

Dengan demikian:

```text
Budget Actual ≠ Production Cost
```

---

## 48. Jurnal Penerimaan Bahan

Saat barang diterima sebelum invoice:

```text
Dr Persediaan Bahan
    Cr Barang Diterima Belum Ditagih
```

Saat supplier invoice:

```text
Dr Barang Diterima Belum Ditagih
    Cr Hutang Supplier
```

Jika invoice langsung tanpa interim account:

```text
Dr Persediaan Bahan
    Cr Hutang Supplier
```

---

## 49. Jurnal Pemakaian Bahan

```text
Dr Biaya Bahan Produksi
    Cr Persediaan Bahan
```

Dimensi wajib:

```text
kitchen_id
fund_id
budget_category_id
government_contract_id
meal_plan_id
production_order_id
product_id
```

---

## 50. Jurnal Produk Hasil

Pilihan desain:

### Opsi A — Produk hasil tidak disimpan

Jika paket langsung didistribusikan pada hari yang sama, sistem dapat mencatat biaya produksi tanpa menjadikan paket sebagai inventory bernilai.

```text
Dr Biaya Produksi / Cost of Service
    Cr Persediaan Bahan
```

### Opsi B — Produk hasil disimpan sementara

```text
Dr Persediaan Produk Jadi
    Cr WIP / Biaya Produksi Terkapitalisasi
```

Saat didistribusikan:

```text
Dr Cost of Service
    Cr Persediaan Produk Jadi
```

Untuk MBG harian, opsi A lebih sederhana. Opsi B digunakan apabila produk jadi benar-benar disimpan, dipindahkan, atau memerlukan traceability stock.

---

## 51. Biaya Tenaga Kerja dan Utilitas

Payroll:

```text
Dr Biaya Tenaga Kerja
    Cr Hutang Tenaga Kerja
```

Utilitas:

```text
Dr Biaya Listrik / Gas / Air
    Cr Hutang Supplier / Bank
```

Biaya kemudian dialokasikan ke production order berdasarkan driver:

- jumlah porsi;
- jam kerja;
- jam mesin;
- luas dapur;
- konsumsi meter;
- persentase tetap.

---

## 52. Klaim Pemerintah

```text
government_contracts
- id UUID PK
- tenant_id UUID FK
- contract_number VARCHAR(100)
- name VARCHAR(255)
- government_agency_id UUID FK
- date_start DATE
- date_end DATE
- price_per_portion NUMERIC(20,2)
- target_portions NUMERIC(20,2)
- contract_value NUMERIC(20,2)
- status ENUM('DRAFT','ACTIVE','COMPLETED','CANCELLED')
```

```text
government_claims
- id UUID PK
- tenant_id UUID FK
- government_contract_id UUID FK
- kitchen_id UUID FK
- claim_number VARCHAR(100)
- period_start DATE
- period_end DATE
- total_portions NUMERIC(20,2)
- gross_amount NUMERIC(20,2)
- deduction_amount NUMERIC(20,2)
- net_amount NUMERIC(20,2)
- status ENUM(
    'DRAFT',
    'SUBMITTED',
    'VERIFIED',
    'APPROVED',
    'POSTED',
    'PARTIALLY_PAID',
    'PAID',
    'REJECTED'
  )
- journal_entry_id UUID FK nullable
```

Saat klaim diakui:

```text
Dr Piutang Pemerintah
    Cr Pendapatan Klaim Pemerintah
```

Saat pembayaran diterima:

```text
Dr Bank
    Cr Piutang Pemerintah
```

---

# Bagian M — Workflow End-to-End

## 53. Perencanaan

```text
Meal Plan
    ↓
Meal Package
    ↓
Recipe Explosion
    ↓
Material Requirement
    ↓
Planned Cost
    ↓
Budget Validation
```

## 54. Pengadaan

```text
Material Shortage
    ↓
Purchase Request
    ↓
Budget Reservation
    ↓
Approval
    ↓
Purchase Order
    ↓
Budget Commitment
```

## 55. Penerimaan dan Invoice

```text
Goods Receipt
    ↓
Stock Move Receipt
    ↓
Lot / Expiry / Quality
    ↓
Inventory Journal
    ↓
Supplier Invoice
    ↓
Budget Actual
    ↓
Account Payable
```

## 56. Produksi

```text
Production Order
    ↓
Stock Reservation
    ↓
Material Issue
    ↓
Actual Consumption
    ↓
Production Output
    ↓
Waste and Yield
    ↓
Cost Sheet
    ↓
Actual Cost per Portion
```

## 57. Klaim dan Pembayaran

```text
Accepted Portions
    ↓
Distribution Confirmation
    ↓
Government Claim
    ↓
Claim Approval
    ↓
Receivable Journal
    ↓
Government Payment
    ↓
Cash and Investor Return
```

---

# Bagian N — Relasi Utama

## 58. ERD Ringkas

```text
tenants
├── kitchens
├── accounts
├── products
├── budgets
├── funds
├── journal_entries
└── government_contracts

uom_categories
└── uoms

product_categories
└── products
    ├── product_packagings
    ├── product_uom_conversions
    ├── product_suppliers
    ├── recipe_lines
    ├── meal_package_components
    ├── stock_moves
    └── stock_lots

products
└── recipes
    └── recipe_lines
        └── component_product

meal_plans
├── meal_plan_lines
├── material_requirements
└── production_orders
    ├── production_material_consumptions
    ├── production_order_outputs
    ├── production_wastes
    └── production_cost_sheets

budgets
└── budget_lines
    ├── budget_reservation_lines
    ├── budget_commitment_lines
    ├── budget_actual_links
    ├── budget_revision_lines
    └── budget_transfers

journals
└── journal_entries
    └── journal_lines
        ├── accounts
        ├── kitchens
        ├── funds
        ├── budget_categories
        ├── government_contracts
        ├── meal_plans
        ├── production_orders
        └── products
```

---

# Bagian O — Constraint dan Konsistensi

## 59. Constraint Tenant

Semua tabel tenant-scoped wajib memiliki:

```text
tenant_id UUID NOT NULL
```

Untuk relasi kritis, gunakan composite foreign key agar tidak terjadi foreign key lintas tenant.

---

## 60. Constraint UoM

- `stock_uom_id` produk wajib.
- transaction UoM harus dapat dikonversi ke stock UoM.
- konversi global hanya dalam kategori UoM yang sama.
- konversi lintas kategori wajib memakai `product_uom_conversions`.
- seluruh nilai cost dihitung menggunakan stock quantity setelah konversi.

---

## 61. Constraint Inventory

- stock move posted tidak boleh diedit;
- koreksi menggunakan reversal move;
- lot wajib jika `requires_lot = true`;
- expiry wajib jika `requires_expiry = true`;
- lot blocked tidak boleh dikeluarkan;
- negative stock diblokir secara default;
- `stock_balances` harus dapat direkonsiliasi dari `stock_moves`.

---

## 62. Constraint Production

- production tidak dapat dimulai tanpa meal plan approved;
- material consumption tidak boleh melebihi stock available tanpa override;
- production completion wajib memiliki actual output;
- accepted portions tidak boleh melebihi actual portions;
- cost sheet finalized tidak boleh dihitung ulang tanpa reopening.

---

## 63. Constraint Budget

- requested amount tidak boleh melebihi available budget ditambah tolerance;
- status `BLOCKING` menolak transaksi;
- status `APPROVAL` membutuhkan approver khusus;
- reserved berubah menjadi committed, tidak ditambahkan ganda;
- committed berubah menjadi actual, tidak ditambahkan ganda;
- reversal journal harus menghasilkan reversal budget actual.

---

## 64. Constraint Accounting

- setiap posted entry harus balance;
- posted entry immutable;
- period closed menolak posting;
- account non-posting tidak boleh digunakan;
- dimensi wajib mengikuti konfigurasi account;
- source document hanya boleh membuat satu jurnal aktif;
- reversal harus mempunyai referensi ke jurnal asal.

---

# Bagian P — API Utama

## 65. Product dan UoM

```text
GET    /api/v1/uom-categories
POST   /api/v1/uoms
GET    /api/v1/products
POST   /api/v1/products
PATCH  /api/v1/products/{product_id}
POST   /api/v1/products/{product_id}/packagings
POST   /api/v1/products/{product_id}/uom-conversions
GET    /api/v1/products/{product_id}/cost
```

## 66. Recipe dan Paket

```text
POST   /api/v1/recipes
POST   /api/v1/recipes/{recipe_id}/lines
POST   /api/v1/recipes/{recipe_id}/approve
GET    /api/v1/recipes/{recipe_id}/cost-preview
POST   /api/v1/meal-packages
POST   /api/v1/meal-packages/{product_id}/components
```

## 67. Material Requirement

```text
POST   /api/v1/meal-plans/{meal_plan_id}/calculate-requirements
GET    /api/v1/meal-plans/{meal_plan_id}/material-requirements
POST   /api/v1/material-requirements/{id}/approve
POST   /api/v1/material-requirements/{id}/reserve-stock
POST   /api/v1/material-requirements/{id}/create-purchase-request
```

## 68. Inventory

```text
POST   /api/v1/inventory/receipts
POST   /api/v1/inventory/issues
POST   /api/v1/inventory/transfers
POST   /api/v1/inventory/adjustments
GET    /api/v1/inventory/balances
GET    /api/v1/inventory/moves
GET    /api/v1/inventory/expiry-alerts
```

## 69. Production

```text
POST   /api/v1/production-orders
POST   /api/v1/production-orders/{id}/reserve-materials
POST   /api/v1/production-orders/{id}/start
POST   /api/v1/production-orders/{id}/consume
POST   /api/v1/production-orders/{id}/record-output
POST   /api/v1/production-orders/{id}/record-waste
POST   /api/v1/production-orders/{id}/complete
GET    /api/v1/production-orders/{id}/cost-sheet
```

## 70. Budget

```text
POST   /api/v1/budgets
POST   /api/v1/budgets/{id}/submit
POST   /api/v1/budgets/{id}/approve
GET    /api/v1/budgets/{id}/availability
POST   /api/v1/budget-reservations
POST   /api/v1/budget-reservations/{id}/approve
POST   /api/v1/budget-commitments
POST   /api/v1/budget-revisions
POST   /api/v1/budget-transfers
```

## 71. Accounting

```text
GET    /api/v1/accounts
POST   /api/v1/journal-entries
POST   /api/v1/journal-entries/{id}/post
POST   /api/v1/journal-entries/{id}/reverse
GET    /api/v1/general-ledger
GET    /api/v1/trial-balance
GET    /api/v1/profit-loss
GET    /api/v1/balance-sheet
```

---

# Bagian Q — Event Domain

## 72. Event Penting

```text
MealPlanApproved
MaterialRequirementCalculated
StockReserved
PurchaseRequestApproved
PurchaseOrderApproved
GoodsReceiptPosted
SupplierInvoicePosted
ProductionStarted
MaterialConsumed
ProductionCompleted
WasteRecorded
ProductionCostFinalized
GovernmentClaimApproved
GovernmentPaymentReceived
JournalEntryPosted
JournalEntryReversed
```

Contoh orchestration:

```text
ProductionCompleted
    ├── inventory: post output/waste moves
    ├── costing: calculate cost sheet
    ├── accounting: post production journal
    ├── reporting: refresh production KPI
    └── notification: notify kitchen manager
```

Untuk konsekuensi yang wajib konsisten, gunakan satu database transaction. Untuk proses non-kritis gunakan transactional outbox.

---

# Bagian R — Testing

## 73. Unit Test Minimum

- UoM conversion.
- Product packaging conversion.
- Recipe explosion.
- Gross requirement dengan waste.
- FEFO lot selection.
- Moving average cost.
- FIFO valuation.
- Stock reservation.
- Budget availability.
- Reservation to commitment transition.
- Commitment to actual transition.
- Journal balancing.
- Cost per accepted portion.
- Journal reversal dan budget reversal.

## 74. Integration Test Minimum

- Meal plan sampai material requirement.
- Purchase request sampai budget commitment.
- Goods receipt sampai inventory journal.
- Supplier invoice sampai budget actual.
- Production completion sampai cost sheet.
- Government claim sampai receivable journal.
- Payment sampai reconciliation.
- Tenant isolation.
- Period closing.
- Idempotent posting.

---

# Bagian S — Prioritas Implementasi

## 75. Fase 1 — Master dan Fondasi

1. UUID base model.
2. Tenant dan kitchen.
3. CoA dan fiscal period.
4. UoM category dan UoM.
5. Product category dan product.
6. Warehouse dan stock location.
7. Budget category.
8. Audit log.

## 76. Fase 2 — Recipe dan Inventory

1. Recipe/versioning.
2. Meal package components.
3. Lot dan expiry.
4. Stock moves dan balances.
5. Supplier product dan harga.
6. Stock reservation.

## 77. Fase 3 — Meal Plan dan Procurement

1. Meal plan.
2. Material requirement.
3. Purchase request.
4. Budget reservation.
5. Purchase order.
6. Budget commitment.
7. Goods receipt.

## 78. Fase 4 — Production dan Costing

1. Production order.
2. Actual consumption.
3. Production output.
4. Waste dan yield.
5. Cost sheet.
6. Planned vs actual variance.
7. Cost per porsi.

## 79. Fase 5 — Accounting dan Claims

1. Double-entry ledger.
2. Auto journal.
3. Supplier payable.
4. Budget actual link.
5. Government contract.
6. Government claim.
7. Receivable dan payment.
8. Trial balance, P&L, balance sheet, cash flow.

---

# Bagian T — Keputusan Desain Final

## 80. Ringkasan Keputusan

1. CoA tetap menjadi fondasi accounting, tetapi tidak cukup untuk budget control.
2. Budget category dipisahkan dari CoA dan dipetakan melalui account mapping.
3. Sistem menggunakan multi-dimensional journal, bukan satu analytic account.
4. Budget mempunyai planned, reserved, committed, actual, dan available.
5. Reservation, commitment, dan actual disimpan sebagai detail audit, bukan hanya saldo agregat.
6. UoM wajib digunakan.
7. Satu produk memiliki stock UoM baku.
8. Purchase UoM dan consumption UoM dapat berbeda.
9. Packaging pembelian disimpan spesifik per produk.
10. Konversi lintas kategori satuan hanya boleh melalui product-specific conversion.
11. Recipe menghasilkan menu component.
12. Meal package dibentuk dari menu component dan packaging.
13. Meal plan menentukan paket dan target porsi per tanggal.
14. Inventory menggunakan immutable stock transaction ledger.
15. Lot dan expiry menggunakan FEFO untuk pengeluaran fisik.
16. Production cost dihitung berdasarkan actual consumption dan accepted portions.
17. Budget actual dan production cost adalah dua konsep berbeda.
18. Seluruh transaksi penting harus menghasilkan audit trail dan idempotent source reference.
19. Jurnal posted dan stock move posted tidak boleh diedit.
20. Seluruh relasi utama menggunakan UUID dan tenant isolation.

---

## 81. Kesimpulan

Desain ini membentuk ERP Dapur MBG sebagai sistem operasional dan finansial yang terintegrasi tetapi tetap modular. Product, UoM, recipe, inventory, production, budget, funding, government claim, dan accounting memiliki tanggung jawab yang jelas.

Struktur tersebut memungkinkan sistem menjawab secara konsisten:

- berapa kebutuhan bahan untuk setiap meal plan;
- berapa stock tersedia dan yang sudah reserved;
- berapa bahan aktual yang dikonsumsi;
- berapa waste dan yield produksi;
- berapa actual cost per porsi;
- berapa budget planned, reserved, committed, actual, dan remaining;
- sumber dana mana yang membiayai transaksi;
- berapa piutang pemerintah yang belum dibayar;
- berapa laba operasional per dapur, kontrak, dan investor.

Dengan implementasi modular FastAPI, PostgreSQL 18, PostGIS, SQLAlchemy 2.x, Alembic, dan UUID, desain ini dapat digunakan sebagai fondasi teknis SaaS ERP Pengelolaan Dapur MBG yang scalable, auditable, dan siap dikembangkan secara bertahap.
