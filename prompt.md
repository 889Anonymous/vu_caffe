# 🧠 URY ERP — VIBE CODE MASTER PROMPT
> **Cách dùng:** Copy TOÀN BỘ file này, paste vào đầu mỗi conversation với AI.  
> File này là "luật chơi" — AI phải tuân theo mọi rule khi viết/sửa code cho dự án này.

---

## 📌 PROJECT CONTEXT

```
Project:  URY ERP — Fork cá nhân từ https://github.com/ury-erp/ury (AGPL-3.0)
Stack:    Frappe v15 + ERPNext | Python 3.11 | Vue 3 + TypeScript | MariaDB
Apps:     ury/ (DocTypes + API) | urypos/ (POS Vue app) | URYMosaic/ (KDS Vue app)
Mục tiêu: Chuẩn hóa cho nghiệp vụ nhà hàng Việt Nam
```

---

# PHẦN 1 — ⛔ TUYỆT ĐỐI CẤM: NO HARDCODE

> **Rule #0:** Mọi magic value phải có tên. Mọi config phải có chỗ thay đổi được.  
> AI vi phạm rule này → phải viết lại trước khi đưa code.

### 1.1 Cấm Magic String / Number
```python
# ❌ CẤM
if status == "3": ...
if tax == 0.1: ...
time.sleep(5)
limit = 100

# ✅ ĐÚNG — constants.py
from ury.ury.constants import KOTStatus, TaxRate, DEFAULT_QUERY_LIMIT
if status == KOTStatus.IN_PROGRESS: ...
if tax == TaxRate.STANDARD_10_PERCENT: ...
time.sleep(SYNC_RETRY_DELAY_SECONDS)
limit = DEFAULT_QUERY_LIMIT
```

### 1.2 Cấm Hardcode Company / Branch / Outlet
```python
# ❌ CẤM — data leak cross-outlet, không scale
filters = {"company": "My Restaurant"}
filters = {"branch": "Branch 1"}

# ✅ ĐÚNG — lấy từ user context
company = frappe.defaults.get_user_default("company")
branch = frappe.defaults.get_user_default("branch")
```

### 1.3 Cấm Hardcode URL / IP / Credential
```python
# ❌ CẤM — commit lên git là lộ secret
requests.post("http://192.168.1.10:8080/einvoice")
API_KEY = "sk-abc123xyz"
MOMO_SECRET = "secretkey2024"

# ✅ ĐÚNG — lấy từ Settings DocType hoặc site_config
settings = frappe.get_single("URY Settings")
requests.post(settings.einvoice_api_url)
api_key = frappe.conf.get("einvoice_api_key")
momo_secret = frappe.utils.password.get_decrypted_password(
    "URY Payment Settings", "ury_payment_settings", "momo_secret_key"
)
```

### 1.4 Cấm Hardcode trong Frontend (Vue/TS)
```typescript
// ❌ CẤM
const API_BASE = "http://localhost:8000"
const MAX_ITEMS = 50
if (order.branch === "Chi nhánh 1") { ... }

// ✅ ĐÚNG
const API_BASE = window.frappe?.boot?.server_url || ""
const MAX_ITEMS = window.frappe?.boot?.ury_config?.max_items || 50
// Branch check: luôn so sánh với user default, không hardcode string
```

### 1.5 Cấm Text VN trong Logic (dùng _() wrapper)
```python
# ❌ CẤM
raise frappe.ValidationError("Bàn đang có khách")
return {"message": "Đặt món thành công"}

# ✅ ĐÚNG — Frappe tự handle translation
raise frappe.ValidationError(_("Table is currently occupied"))
return {"message": _("Order placed successfully")}
# Translation VN: ury/translations/vi.csv
```

### 1.6 File Constants Bắt Buộc
```python
# ury/ury/constants.py — TẤT CẢ magic value phải về đây

class KOTStatus:
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    READY = "Ready"
    SERVED = "Served"
    CANCELLED = "Cancelled"

class InvoiceStatus:
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    PAID = "Paid"
    CANCELLED = "Cancelled"

class TaxRate:
    ZERO = 0.0
    FIVE_PERCENT = 0.05
    EIGHT_PERCENT = 0.08
    STANDARD_10_PERCENT = 0.10

class EInvoiceStatus:
    PENDING = "Pending"
    ISSUED = "Issued"
    CANCELLED = "Cancelled"

class OrderType:
    DINE_IN = "Dine In"
    TAKEAWAY = "Takeaway"
    DELIVERY = "Delivery"

DEFAULT_QUERY_LIMIT = 50
MAX_ITEMS_PER_ORDER = 100
SYNC_RETRY_DELAY_SECONDS = 2
SHIFT_OVERLAP_MINUTES = 15
KDS_REFRESH_INTERVAL_MS = 5000
```

---

# PHẦN 2 — 🧹 CLEAN CODE RULES

### 2.1 Function Size — Giới hạn cứng
```
Python:     Hàm > 30 dòng → PHẢI tách    |  Hàm > 50 dòng → BẮT BUỘC refactor ngay
TypeScript: Component > 150 dòng → tách  |  Function > 20 dòng → xem xét tách
```

```python
# ❌ God function
@frappe.whitelist()
def process_order(order_data):
    # validate 20 dòng + tính tax 15 dòng + tạo KOT 20 dòng + print 10 dòng...

# ✅ Orchestrator nhỏ gọn, delegate ra helpers
@frappe.whitelist()
def process_order(order_data: dict) -> dict:
    validated = _validate_order(order_data)
    kot = _create_kot(validated)
    _notify_kitchen(kot)
    _update_table_status(validated["table"])
    return {"kot": kot.name, "status": "created"}
```

### 2.2 Naming — Tên phải tự nói được
```python
# ❌
def do_it(d): x = calc(a,b); tmp = get(n)

# ✅
def create_kitchen_order(order_data: dict) -> "KOT": ...
tax_amount = calculate_vat(subtotal, tax_rate)
active_kots = get_open_kots(branch=branch, limit=DEFAULT_QUERY_LIMIT)
```

### 2.3 Error Handling — KHÔNG im lặng
```python
# ❌ CẤM — nuốt error
try:
    sync_einvoice(name)
except:
    pass

# ✅ ĐÚNG — log đầy đủ context
except Exception:
    frappe.log_error(
        title=f"eInvoice Sync Failed: {invoice_name}",
        message=frappe.get_traceback()
    )
    # Critical → raise lại | Non-critical → return error dict
```

### 2.4 Type Hints — BẮT BUỘC
```python
# ❌
def get_orders(branch, date, status):

# ✅
from typing import Optional, List
def get_orders(branch: str, date: str, status: Optional[str] = None, limit: int = 50) -> List[dict]:
```

### 2.5 No Dead Code / No Comment-Explain-Code
```python
# ❌ CẤM
# x = old_function()  ← code commented out
# Hàm này dùng để lấy đơn hàng  ← giải thích code làm gì

# ✅ Code tự nói, comment giải thích WHY (không phải WHAT)
# Frappe không tự tạo index cho Link field nên phải dùng SQL trực tiếp ở đây
def get_open_kots_optimized(...):
```

---

# PHẦN 3 — 🏗️ SOLID + DESIGN PATTERNS

### 3.1 Single Responsibility — Cấu trúc modules
```
ury/ury/
├── api.py              ← CHỈ expose @frappe.whitelist() endpoints (mỗi fn ≤ 10 dòng)
├── constants.py        ← Tất cả magic values
├── repositories/
│   ├── kot_repo.py     ← Mọi DB query về KOT
│   ├── invoice_repo.py ← Mọi DB query về Invoice
│   └── table_repo.py   ← Mọi DB query về Table
├── utils/
│   ├── billing.py      ← Tính tiền, tax, discount
│   ├── kitchen.py      ← KOT creation, routing, status
│   ├── payment.py      ← Payment processing
│   ├── einvoice.py     ← Hoá đơn điện tử VN
│   └── table_mgmt.py   ← Table status, occupancy
└── events/
    └── kot_events.py   ← Frappe hooks handlers
```

### 3.2 Open/Closed — Extend qua hooks, không sửa core
```python
# ❌ Sửa trực tiếp core
# kot.py: thêm if-else cho từng order type

# ✅ hooks.py + Strategy pattern
doc_events = {"KOT": {"before_submit": "ury.ury.events.kot_events.before_kot_submit"}}

# kot_events.py
def before_kot_submit(doc, method):
    handler = ORDER_TYPE_HANDLERS.get(doc.order_type, DefaultHandler())
    handler.on_submit(doc)
```

### 3.3 Dependency Inversion — Inject không new() trong business
```python
# ❌ Coupled
class OrderService:
    def __init__(self):
        self.payment = MomoGateway()  # cannot swap!

# ✅ Injected
class OrderService:
    def __init__(self, payment: PaymentGateway, printer: PrinterInterface):
        self.payment = payment
        self.printer = printer
```

### 3.4 Repository Pattern — Tập trung DB queries
```python
# ury/ury/repositories/kot_repo.py
class KOTRepository:
    def get_open_kots(self, branch: str, limit: int = DEFAULT_QUERY_LIMIT) -> List[dict]:
        """Lấy KOT đang mở — 1 query JOIN, không N+1."""
        return frappe.db.sql("""
            SELECT k.name, k.status, k.table_no, k.posting_time,
                   ki.item_code, ki.item_name, ki.qty, ki.status as item_status
            FROM `tabKOT` k
            JOIN `tabKOT Item` ki ON ki.parent = k.name
            WHERE k.branch = %s AND k.status IN ('Open','In Progress')
            ORDER BY k.posting_time ASC LIMIT %s
        """, (branch, limit), as_dict=True)
```

### 3.5 Strategy Pattern — Tax VN
```python
# utils/tax_strategy.py
VAT_STRATEGIES = {
    "0":  ZeroVAT(),
    "8":  ReducedVAT8(),
    "10": StandardVAT(),
}

def get_vat_strategy(rate: str) -> VATStrategy:
    return VAT_STRATEGIES.get(rate, ZeroVAT())
```

### 3.6 Factory Pattern — Payment Gateway
```python
# Thêm gateway mới: chỉ cần tạo class mới, không sửa gì khác
PAYMENT_GATEWAYS: dict[str, type[PaymentGateway]] = {
    "Momo":    MomoGateway,
    "VietQR":  VietQRGateway,
    "ZaloPay": ZaloPayGateway,
    "Cash":    CashGateway,
}

def get_payment_gateway(gateway_type: str) -> PaymentGateway:
    cls = PAYMENT_GATEWAYS.get(gateway_type)
    if not cls:
        raise frappe.ValidationError(_("Unsupported gateway: {0}").format(gateway_type))
    return cls()
```

---

# PHẦN 4 — 🔴 DEBUG: N+1 & PERFORMANCE

### 4.1 Phân biệt Root Cause — Code hay DB?

**Code sai (fix ở tầng code):**
- Gọi `frappe.get_all()` / `frappe.get_doc()` trong loop
- Lazy load child table trong vòng lặp
- Frontend gọi 2 API riêng cho data có thể JOIN

**DB Design sai (fix ở tầng DB + migration):**
- Thiếu index trên `status`, `branch`, `table_no`, `posting_date`  
  *(Frappe CHỈ tự tạo index cho: `name`, `modified`, `owner`)*
- Thiếu composite index `(branch, posting_date, status)` cho multi-outlet
- Child table quá nhiều cột không dùng

**Cả hai sai (phải fix đồng thời):**
- Fix code lazy load → giảm số query
- Fix thiếu index → mỗi query đó không còn full table scan
- Bỏ sót 1 tầng → vẫn chậm

### 4.2 N+1 Patterns — Detect & Fix
```python
# ❌ N+1 — Frappe lazy load
for kot in frappe.get_all("KOT", filters={"branch": branch}):
    items = frappe.get_all("KOT Item", filters={"parent": kot.name})  # N queries!

# ❌ N+1 — get_doc trong loop
docs = frappe.get_all("KOT", ...)
for d in docs:
    full_doc = frappe.get_doc("KOT", d.name)  # 1 query mỗi iteration!
    item = frappe.get_doc("Item", full_doc.items[0].item_code)  # N+1 thêm!

# ✅ Fix — 1 query JOIN
frappe.db.sql("""
    SELECT k.name, k.table_no, ki.item_code, ki.qty
    FROM `tabKOT` k JOIN `tabKOT Item` ki ON ki.parent = k.name
    WHERE k.branch = %s AND k.status = %s
""", (branch, KOTStatus.OPEN), as_dict=True)

# ✅ Fix — frappe.get_all với child fields
frappe.get_all("KOT",
    fields=["name", "table_no", "items.item_code", "items.qty"],
    filters={"branch": branch, "status": KOTStatus.OPEN})
```

### 4.3 DB Index — Thêm bắt buộc
```json
// Trong DocType JSON field definition, thêm:
{"fieldname": "branch", "search_index": 1},
{"fieldname": "status", "search_index": 1},
{"fieldname": "posting_date", "search_index": 1},
{"fieldname": "table_no", "search_index": 1}
```
```python
# Composite index → migration script:
# ury/patches/YYYYMMDD_add_composite_index.py
def execute():
    frappe.db.sql("""
        ALTER TABLE `tabKOT`
        ADD INDEX IF NOT EXISTS idx_branch_date_status (branch, posting_date, status)
    """)
```

### 4.4 Cronjob — Rules bắt buộc
```python
# hooks.py scheduler_events: mọi job phải có scope rõ ràng
def sync_pending_einvoices():
    """Cronjob example chuẩn."""
    frappe.logger().info("eInvoice sync started")
    
    # BẮT BUỘC: filter theo ngày, không full table scan
    invoices = frappe.get_all("URY POS Invoice",
        filters={
            "einvoice_status": EInvoiceStatus.PENDING,
            "posting_date": [">=", frappe.utils.add_days(frappe.utils.today(), -7)],
            "docstatus": 1
        },
        fields=["name"],
        limit=50  # BẮT BUỘC: có limit
    )
    
    for inv in invoices:
        try:
            _sync_single_invoice(inv.name)
        except Exception:
            frappe.log_error(title=f"eInvoice Sync: {inv.name}", message=frappe.get_traceback())
    
    frappe.logger().info(f"eInvoice sync done: {len(invoices)} processed")
```

---

# PHẦN 5 — 🇻🇳 CHUẨN HÓA VIỆT NAM

### 5.1 Localisation Mặc Định
```python
# hooks.py / fixtures
# Currency: VND | Timezone: Asia/Ho_Chi_Minh
# Date format: dd-mm-yyyy | Number: #.###,##
```

### 5.2 VAT & Hoá Đơn Điện Tử (Nghị định 123/2020)
```
Fields thêm vào URY POS Invoice:
- tax_rate_vn       Select: 0|5|8|10
- einvoice_status   (Pending/Issued/Cancelled)
- einvoice_serial   Ký hiệu: "1C25TAA"
- einvoice_number   Số thứ tự
- buyer_tax_id      MST người mua (optional)

Provider tích hợp: VNPT / MISA / Viettel (qua Settings DocType)
```

### 5.3 Payment VN
```
Thêm vào Payment Gateway Settings:
- VietQR (vietqr.io API — QR tạo từ số tài khoản)
- Momo (Partner API)
- ZaloPay (Merchant API)
- VNPay (Merchant API)
- Napas (thẻ nội địa)
- Công nợ nội bộ (staff meal allowance)
```

### 5.4 Báo Cáo VN
```
- Doanh thu theo ca (Sáng/Chiều/Tối)
- Báo cáo VAT tháng → xuất XML nộp thuế
- Tiêu hao nguyên liệu (chống thất thoát)
- So sánh chi nhánh
```

---

# PHẦN 6 — 📋 CHECKLIST TRƯỚC KHI COMMIT

> AI PHẢI tự check và báo kết quả trước khi đưa code:

```
⛔ HARDCODE:
□ Không có company/branch string hardcode
□ Không có URL/IP/port hardcode
□ Không có API key/password trong code
□ Không có magic number (0.1, 100...) — phải dùng constant có tên
□ Text VN dùng _() wrapper, không inline
□ Không có date/timezone hardcode

🧹 CLEAN CODE:
□ Mọi function có type hint (Python) / interface (TypeScript)
□ Không có function > 30 dòng (Python) hoặc > 20 dòng (TS function)
□ Không có code commented-out
□ Không có try/except im lặng (pass)
□ Tên biến/function tự nói được ý nghĩa

🏗️ SOLID:
□ Function/class chỉ có 1 responsibility
□ KHÔNG sửa file trong frappe/ hoặc erpnext/ core
□ Dependency được inject, không new() trong business logic
□ Thêm gateway/handler mới không cần sửa code cũ

🔴 PERFORMANCE:
□ Không có frappe.get_all() trong vòng lặp for
□ Không có frappe.get_doc() khi chỉ cần 1-2 field
□ Field filter thông dụng đã có search_index
□ Cronjob có limit và filter ngày
□ Frontend không gọi 2 API riêng cho data có thể JOIN

🔒 SECURITY:
□ Mọi @frappe.whitelist() có frappe.has_permission()
□ Mọi query filter theo company và branch
□ SQL dùng %s placeholder, không f-string/format
□ Không có data leak cross-outlet
```

---

# PHẦN 7 — 📝 CHANGELOG FORMAT

> Điền sau MỖI lần thay đổi. ROOT CAUSE bắt buộc — không được bỏ trống.

```markdown
## [YYYY-MM-DD] — Tiêu đề

### 🔴 BUG / 🟡 PERF / 🟢 FEATURE-VN / 🔵 REFACTOR / 🟣 DB / ⚫ SECURITY
- **File:** `path/to/file.py` line X
- **Vấn đề:** Mô tả người dùng thấy gì
- **Root Cause CODE:** [Có/Không] — lý do cụ thể
- **Root Cause DB:** [Có/Không] — lý do cụ thể
- **Fix:** Đã làm gì cụ thể
- **Test:** Kiểm tra với dữ liệu nào
- **Perf:** [nếu đo được] Trước Xms → Sau Yms
```

---

# PHẦN 8 — 🚀 QUICK COMMANDS

Paste một trong các lệnh này để trigger đúng mode:

```
[AUDIT] Audit file sau theo PHẦN 4 — xác định root cause tầng Code hay DB,
đề xuất fix đúng tầng, không fix tầng ngọn:
[paste code]

[CLEAN] Refactor code sau theo PHẦN 2 + PHẦN 3 — clean code + SOLID.
Sau khi xong, tự check CHECKLIST PHẦN 6 và báo kết quả:
[paste code]

[FEATURE-VN] Implement [tính năng] theo PHẦN 5 — chuẩn hóa Việt Nam.
Áp dụng đầy đủ PHẦN 1 no-hardcode + PHẦN 2 clean code.

[REVIEW] Review code sau, báo vi phạm từng rule cụ thể (dòng nào, rule nào):
[paste code]

[CRONJOB] Viết/review scheduled task này — check theo PHẦN 4.4:
[mô tả hoặc paste code]
```

---

*URY ERP Vietnam Fork — Master Prompt v2.0*  
*Cập nhật: điền ngày thực tế khi bắt đầu dùng*






FE


# 🎨 URY ERP — FRONTEND PROMPT (Vue 3 + CSS Chuẩn)
> Paste file này khi làm bất kỳ task nào liên quan đến UI/UX, component, layout, styling.

---

## 📌 FE STACK CONTEXT

```
Framework:    Vue 3 (Composition API + <script setup>)
Language:     TypeScript — không dùng any, mọi prop/emit có interface
Styling:      CSS thuần (scoped) + CSS Custom Properties — KHÔNG dùng inline style
State:        Pinia stores
Build:        Vite
Target:       POS dùng tablet/desktop | KDS dùng màn hình bếp | Report dùng desktop
Font:         Google Fonts — chọn theo context (không dùng Arial, Inter, Roboto mặc định)
Icons:        Frappe Icons hoặc SVG inline — không import thư viện icon nặng
```

---

## 🖥️ RESPONSIVE — BREAKPOINT CHUẨN URY

> URY phục vụ 3 loại thiết bị khác nhau. PHẢI handle đủ cả 3.

```css
/* === BREAKPOINT SYSTEM === */
/* Mobile first — viết style mobile trước, override lên */

/* 📱 Mobile / Cashier cầm tay */
/* Default — không cần media query */

/* 📟 Tablet / POS counter / Waiter tablet */
@media (min-width: 768px) { }

/* 🖥️ Desktop / KDS kitchen screen / Manager dashboard */
@media (min-width: 1024px) { }

/* 📺 Large screen / Wall-mounted KDS */
@media (min-width: 1440px) { }

/* ⚠️ Touch device — POS/KDS đều là touch */
@media (hover: none) and (pointer: coarse) {
  /* Button min 48x48px, spacing rộng hơn */
}

/* 🌙 Dark mode — KDS bếp thường dùng dark */
@media (prefers-color-scheme: dark) { }
```

---

## 🎨 CSS DESIGN SYSTEM — BẮT BUỘC DÙNG

### 1. CSS Custom Properties (Design Tokens)
```css
/* ury/public/css/design-tokens.css */
/* Paste vào đầu mỗi component hoặc global style */

:root {
  /* === COLORS === */
  --color-primary:        #E8472A;   /* URY brand — đỏ nhà hàng */
  --color-primary-dark:   #C73A20;
  --color-primary-light:  #FF6B50;
  --color-primary-ghost:  rgba(232, 71, 42, 0.10);

  --color-success:        #2ECC71;
  --color-warning:        #F39C12;
  --color-danger:         #E74C3C;
  --color-info:           #3498DB;

  /* KOT Status Colors */
  --color-status-open:        #3498DB;
  --color-status-in-progress: #F39C12;
  --color-status-ready:       #2ECC71;
  --color-status-served:      #95A5A6;
  --color-status-cancelled:   #E74C3C;

  /* === NEUTRAL SCALE === */
  --color-bg:             #F8F7F4;   /* Background ấm — không dùng trắng tinh */
  --color-surface:        #FFFFFF;
  --color-surface-raised: #FEFEFE;
  --color-border:         #E8E4DF;
  --color-border-strong:  #CDC7BF;
  --color-text:           #1A1A18;
  --color-text-secondary: #6B6460;
  --color-text-muted:     #9B9490;
  --color-text-inverse:   #FFFFFF;

  /* === TYPOGRAPHY === */
  --font-display:   'Sora', sans-serif;        /* Heading, số lớn, tên món */
  --font-body:      'DM Sans', sans-serif;     /* Body text, label */
  --font-mono:      'JetBrains Mono', monospace; /* Giá tiền, mã đơn, số bàn */

  --text-xs:    0.75rem;    /* 12px */
  --text-sm:    0.875rem;   /* 14px */
  --text-base:  1rem;       /* 16px */
  --text-lg:    1.125rem;   /* 18px */
  --text-xl:    1.25rem;    /* 20px */
  --text-2xl:   1.5rem;     /* 24px */
  --text-3xl:   1.875rem;   /* 30px */
  --text-4xl:   2.25rem;    /* 36px */

  --font-normal:  400;
  --font-medium:  500;
  --font-semibold: 600;
  --font-bold:    700;
  --line-height-tight:  1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;

  /* === SPACING === */
  --space-1:   0.25rem;   /* 4px */
  --space-2:   0.5rem;    /* 8px */
  --space-3:   0.75rem;   /* 12px */
  --space-4:   1rem;      /* 16px */
  --space-5:   1.25rem;   /* 20px */
  --space-6:   1.5rem;    /* 24px */
  --space-8:   2rem;      /* 32px */
  --space-10:  2.5rem;    /* 40px */
  --space-12:  3rem;      /* 48px */
  --space-16:  4rem;      /* 64px */

  /* === BORDER RADIUS === */
  --radius-sm:   4px;
  --radius-md:   8px;
  --radius-lg:   12px;
  --radius-xl:   16px;
  --radius-2xl:  24px;
  --radius-full: 9999px;

  /* === SHADOW === */
  --shadow-sm:  0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md:  0 4px 12px rgba(0,0,0,0.10), 0 2px 4px rgba(0,0,0,0.06);
  --shadow-lg:  0 10px 30px rgba(0,0,0,0.12), 0 4px 8px rgba(0,0,0,0.06);
  --shadow-xl:  0 20px 50px rgba(0,0,0,0.15);

  /* === TRANSITIONS === */
  --transition-fast:   120ms ease;
  --transition-base:   200ms ease;
  --transition-slow:   350ms ease;
  --transition-spring: 400ms cubic-bezier(0.34, 1.56, 0.64, 1); /* Bounce nhẹ */

  /* === Z-INDEX SCALE === */
  --z-base:    0;
  --z-raised:  10;
  --z-overlay: 100;
  --z-modal:   200;
  --z-toast:   300;
  --z-tooltip: 400;

  /* === TOUCH TARGET === */
  --touch-min: 48px;  /* Minimum tap target iOS/Android */
}

/* Dark mode override */
[data-theme="dark"] {
  --color-bg:             #111110;
  --color-surface:        #1C1C1A;
  --color-surface-raised: #242422;
  --color-border:         #2E2E2C;
  --color-border-strong:  #3D3D3B;
  --color-text:           #F0EDE8;
  --color-text-secondary: #A09A94;
  --color-text-muted:     #706A64;
}
```

### 2. Utility Classes Chuẩn
```css
/* Responsive container */
.ury-container {
  width: 100%;
  padding-inline: var(--space-4);
  margin-inline: auto;
}
@media (min-width: 768px)  { .ury-container { padding-inline: var(--space-6); } }
@media (min-width: 1024px) { .ury-container { max-width: 1280px; padding-inline: var(--space-8); } }

/* Visually hidden (accessibility) */
.sr-only {
  position: absolute; width: 1px; height: 1px;
  padding: 0; margin: -1px; overflow: hidden;
  clip: rect(0,0,0,0); white-space: nowrap; border: 0;
}

/* Touch-friendly tap target wrapper */
.touch-target {
  min-width: var(--touch-min);
  min-height: var(--touch-min);
  display: flex; align-items: center; justify-content: center;
}
```

---

## 🧩 COMPONENT RULES — Vue 3

### Rule F1: Component Template Chuẩn
```vue
<script setup lang="ts">
// 1. Imports (external → internal → types)
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useOrderStore } from '@/stores/orderStore'
import type { KOTItem, OrderStatus } from '@/types/order'

// 2. Props & Emits — PHẢI có interface, không dùng any
interface Props {
  kotId: string
  branchId: string
  initialStatus?: OrderStatus
}
interface Emits {
  (e: 'status-change', kotId: string, status: OrderStatus): void
  (e: 'item-ready', itemIdx: number): void
}

const props = withDefaults(defineProps<Props>(), {
  initialStatus: 'Open'
})
const emit = defineEmits<Emits>()

// 3. Stores
const orderStore = useOrderStore()

// 4. Reactive state — tên rõ nghĩa
const isLoading = ref(false)
const activeStatus = ref<OrderStatus>(props.initialStatus)

// 5. Computed
const displayItems = computed(() =>
  orderStore.getKOTItems(props.kotId).filter(i => i.status !== 'Cancelled')
)

// 6. Methods — action verb + noun
async function updateItemStatus(itemIdx: number, status: OrderStatus) {
  isLoading.value = true
  try {
    await orderStore.updateKOTItem(props.kotId, itemIdx, status)
    emit('item-ready', itemIdx)
  } finally {
    isLoading.value = false
  }
}

// 7. Lifecycle — LUÔN cleanup interval/listener
onMounted(() => { /* ... */ })
onUnmounted(() => { /* cleanup timers, sockets */ })
</script>

<template>
  <!-- Root element 1 thôi, dùng semantic HTML -->
  <article class="kot-card" :class="[`kot-card--${activeStatus.toLowerCase().replace(' ','-')}`]">
    <header class="kot-card__header">
      <span class="kot-card__id font-mono">{{ kotId }}</span>
      <StatusBadge :status="activeStatus" />
    </header>
    
    <ul class="kot-card__items" role="list">
      <li v-for="item in displayItems" :key="item.idx" class="kot-item">
        <!-- ... -->
      </li>
    </ul>
  </article>
</template>

<style scoped>
/* BEM naming: block__element--modifier */
.kot-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--transition-base);
}

/* Status modifier — màu từ design token */
.kot-card--in-progress { border-left: 3px solid var(--color-status-in-progress); }
.kot-card--ready       { border-left: 3px solid var(--color-status-ready); }
.kot-card--cancelled   { opacity: 0.5; }

/* Responsive */
.kot-card { padding: var(--space-3); }
@media (min-width: 768px) {
  .kot-card { padding: var(--space-4); }
}
</style>
```

### Rule F2: KHÔNG ĐƯỢC làm những điều này
```
❌ TUYỆT ĐỐI CẤM:

CSS:
□ style="color: red; margin: 10px"  ← inline style (trừ dynamic binding)
□ !important                         ← dấu hiệu specificity war
□ font-size: 13px / margin: 7px     ← số lẻ không có trong scale
□ color: #e74c3c                     ← dùng var(--color-danger)
□ transition: all 0.3s              ← "all" gây performance issue
□ width: 350px                       ← hardcode width, không responsive

TypeScript:
□ props: { data: any }              ← không có type
□ (e: any) =>                        ← event không typed
□ // @ts-ignore                      ← che error thay vì fix

Vue:
□ v-for without :key               ← sẽ gây bug rendering
□ emit event không khai báo trong Emits interface
□ Gọi frappe.call() trực tiếp trong component ← phải qua store/composable
□ setInterval không clearInterval trong onUnmounted ← memory leak
□ window.location.href thay vì router.push()
```

### Rule F3: Responsive Pattern Chuẩn
```vue
<style scoped>
/* ✅ Mobile first */
.pos-grid {
  display: grid;
  grid-template-columns: 1fr;          /* Mobile: 1 cột */
  gap: var(--space-3);
}

@media (min-width: 768px) {
  .pos-grid {
    grid-template-columns: 1fr 360px;  /* Tablet: menu + cart */
    gap: var(--space-4);
  }
}

@media (min-width: 1024px) {
  .pos-grid {
    grid-template-columns: 240px 1fr 400px; /* Desktop: category + menu + cart */
    gap: var(--space-6);
  }
}

/* ✅ Touch-friendly buttons */
.menu-item-btn {
  min-height: var(--touch-min);  /* 48px touch target */
  padding: var(--space-3) var(--space-4);
  cursor: pointer;
  /* Trên touch: hover state thay bằng :active */
}

@media (hover: hover) {
  .menu-item-btn:hover {
    background: var(--color-primary-ghost);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
  }
}

@media (hover: none) {
  /* Touch device — active thay vì hover */
  .menu-item-btn:active {
    background: var(--color-primary-ghost);
    transform: scale(0.97);
  }
}

/* ✅ Typography responsive */
.section-title {
  font-size: var(--text-xl);
  font-family: var(--font-display);
}
@media (min-width: 1024px) {
  .section-title { font-size: var(--text-2xl); }
}
</style>
```

---

## 📱 RESPONSIVE LAYOUT PATTERNS — URY SCREENS

### POS Layout (Menu + Cart)
```vue
<template>
  <div class="pos-layout">
    <!-- Mobile: stacked, Tablet+: side-by-side -->
    <aside class="pos-layout__sidebar">
      <CategoryNav />
    </aside>
    <main class="pos-layout__menu">
      <MenuGrid />
    </main>
    <section class="pos-layout__cart">
      <!-- Mobile: bottom sheet, Desktop: right panel -->
      <CartPanel />
    </section>
  </div>
</template>

<style scoped>
.pos-layout {
  display: grid;
  grid-template-areas:
    "menu"
    "cart";
  height: 100dvh;               /* dvh thay vh, tránh mobile browser bar */
  overflow: hidden;
}

@media (min-width: 768px) {
  .pos-layout {
    grid-template-areas: "sidebar menu cart";
    grid-template-columns: 72px 1fr 340px;
  }
}

@media (min-width: 1280px) {
  .pos-layout {
    grid-template-columns: 200px 1fr 420px;
  }
}

.pos-layout__sidebar { grid-area: sidebar; }
.pos-layout__menu    { grid-area: menu; overflow-y: auto; }
.pos-layout__cart    { grid-area: cart; }
</style>
```

### KDS Layout (Kitchen Display)
```vue
<style scoped>
/* KDS: nhiều card, scroll ngang trên tablet, grid trên desktop */
.kds-board {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: 280px;
  gap: var(--space-3);
  overflow-x: auto;
  padding: var(--space-4);
  height: 100dvh;
  /* Smooth scroll với momentum iOS */
  -webkit-overflow-scrolling: touch;
  scroll-snap-type: x mandatory;
}

.kds-board .kot-card {
  scroll-snap-align: start;
}

@media (min-width: 1024px) {
  .kds-board {
    grid-auto-flow: row;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    overflow-x: hidden;
    overflow-y: auto;
  }
}
</style>
```

---

## ♿ ACCESSIBILITY — KHÔNG ĐƯỢC BỎ QUA

```vue
<template>
  <!-- ✅ Semantic HTML -->
  <button                          <!-- không dùng div onClick -->
    type="button"
    :aria-label="`Thêm ${item.name} vào giỏ`"
    :aria-pressed="isSelected"
    :disabled="isLoading"
    @click="addToCart"
  >
    <span aria-hidden="true">+</span>
    <span class="sr-only">Thêm {{ item.name }}</span>
  </button>

  <!-- ✅ Form inputs -->
  <label for="qty-input" class="input-label">Số lượng</label>
  <input
    id="qty-input"
    type="number"
    inputmode="numeric"            <!-- mobile keyboard số -->
    min="1" max="99"
    :aria-describedby="error ? 'qty-error' : undefined"
  />
  <span v-if="error" id="qty-error" role="alert" class="error-text">{{ error }}</span>

  <!-- ✅ Loading state -->
  <div role="status" aria-live="polite" aria-label="Đang tải đơn hàng">
    <LoadingSpinner v-if="isLoading" />
  </div>
</template>
```

---

## ✨ ANIMATION — CÓ CHỪNG MỰC

```css
/* ✅ CSS-only animations — performance > JS animation */
.kot-card {
  animation: slideInUp 200ms ease forwards;
}

@keyframes slideInUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ✅ Stagger list items */
.kot-item { opacity: 0; animation: fadeIn 150ms ease forwards; }
.kot-item:nth-child(1) { animation-delay: 0ms; }
.kot-item:nth-child(2) { animation-delay: 30ms; }
.kot-item:nth-child(3) { animation-delay: 60ms; }

/* ✅ Status badge pulse — draw attention */
.status-badge--ready {
  animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.4); }
  50%       { box-shadow: 0 0 0 6px rgba(46, 204, 113, 0); }
}

/* ✅ LUÔN respect user preference */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 💰 HIỂN THỊ TIỀN VND — CHUẨN VIỆT NAM

```typescript
// utils/currency.ts
export function formatVND(amount: number): string {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0  // VND không có xu
  }).format(amount)
  // Output: "125.000 ₫"
}

export function formatCompactVND(amount: number): string {
  if (amount >= 1_000_000) return `${(amount / 1_000_000).toFixed(1)}M ₫`
  if (amount >= 1_000)     return `${(amount / 1_000).toFixed(0)}k ₫`
  return `${amount} ₫`
  // Output: "1.5M ₫" | "125k ₫"
}
```

```css
/* Số tiền dùng font mono — align đẹp hơn */
.price {
  font-family: var(--font-mono);
  font-weight: var(--font-semibold);
  font-variant-numeric: tabular-nums;  /* Số cùng width, thẳng hàng */
  letter-spacing: -0.01em;
}

.price--large {
  font-size: var(--text-2xl);
  color: var(--color-primary);
}

.price--muted {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  text-decoration: line-through;  /* Giá gốc bị gạch */
}
```

---

## 🔍 FE SELF-REVIEW CHECKLIST

> AI tự check trước khi đưa code — phải pass 100%:

```
RESPONSIVE:
□ Mobile first — style mặc định cho mobile, override lên
□ Có đủ 3 breakpoint: 768px (tablet), 1024px (desktop), 1440px (large)
□ Dùng dvh thay vh cho height màn hình
□ Touch target tối thiểu 48x48px
□ Hover state chỉ apply khi hover: hover (không trên touch)
□ Không có width/height hardcode px (dùng %, fr, min-content...)

CSS:
□ Tất cả màu sắc dùng var(--color-...)
□ Tất cả spacing dùng var(--space-...)
□ Tất cả font-size dùng var(--text-...)
□ Không có !important
□ Không có inline style (trừ dynamic binding)
□ Không có transition: all
□ Không có magic pixel (13px, 7px, 350px...)
□ BEM naming: block__element--modifier
□ prefers-reduced-motion được handle

TypeScript / Vue:
□ Mọi prop có interface, không có any
□ Mọi emit có khai báo trong Emits interface
□ v-for luôn có :key
□ Không gọi frappe.call() trực tiếp trong component
□ Interval/socket cleanup trong onUnmounted
□ Dùng semantic HTML đúng (button, article, section, nav...)
□ Accessibility: aria-label, role, aria-live cho loading/error

VN Specific:
□ Tiền dùng formatVND() — font-mono, tabular-nums
□ Ngày dùng vi-VN locale
□ Input số dùng inputmode="numeric"
```

---

## 🚀 QUICK COMMANDS FE

```
[COMPONENT] Tạo component Vue 3 sau theo FE PROMPT:
Áp dụng đủ: responsive 3 breakpoint, design tokens, BEM CSS, TS interface, a11y.
Self-check checklist trước khi đưa code.
[mô tả component]

[RESPONSIVE-FIX] Fix responsive cho component này.
Đảm bảo: mobile → 768px → 1024px → 1440px, touch-friendly, dvh:
[paste component]

[CSS-AUDIT] Audit CSS sau, báo từng vi phạm (dòng nào, rule nào):
[paste CSS]

[LAYOUT] Tạo layout cho màn hình [POS/KDS/Report/Login]:
Mobile first, responsive, dùng CSS Grid, không hardcode pixel.
```
