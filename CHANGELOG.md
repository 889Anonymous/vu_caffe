# CHANGELOG — URY Cafe Management System (Vietnam Fork)

> Format: `[YYYY-MM-DD] [TYPE] [SEVERITY] Description`  
> **TYPE**: `FIX` | `FEAT` | `PERF` | `REFACTOR` | `DOCS` | `SECURITY`  
> **SEVERITY**: 🔴 Critical | 🟠 High | 🟡 Medium | 🟢 Low

---

## [Unreleased] — Phase 2: Việt hóa i18n

### 🟠 High — Ưu tiên cao
- [x] `[FEAT]` 🟠 **Thêm i18n cho Frontend POS** — Toàn bộ `pos/src/` — 2026-02-24
  Tất cả strings UI hardcoded tiếng Anh. Đã tích hợp `react-i18next` và khai báo trong `vi.json`.
- [x] `[FEAT]` 🟠 **Thêm file translation backend** — `ury/translations/vi.csv` — 2026-02-24
  Frappe hỗ trợ `translations/vi.csv`. Tạo file với toàn bộ labels của URY doctypes dịch sang tiếng Việt.

### 🟡 Medium — Kế hoạch sắp tới

- [x] `[REFACTOR]` 🟡 **`any` types trong Frontend** — `pos-store.ts`, `PaymentDialog.tsx` — 2026-02-24
  Sử dụng `any` làm mất type safety. Đã định nghĩa interface rõ ràng `{ name: string }` và `PaymentMode` mappings.

- [x] `[REFACTOR]` 🟡 **`inner_bom_process()` vs `inner_inner_bom_process()`** — `ury_daily_p_and_l.py:10-57` — 2026-02-24
  Hai hàm gần giống nhau, khác chỉ ở chỗ `inner_bom_process` có đệ quy BOM lồng. Đã dùng đệ quy thật sự (`max_depth=2` parameter) và xóa hẳn `inner_inner_bom_process`.

- [x] `[FEAT]` 🟡 **Vu Caffe Database Aggregation** — `scheduler_vu_caffe.py` — 2026-02-24
  Thêm `Vu Caffe Daily Report` và `Monthly Report` dùng kiểu dữ liệu JSON gom nhóm doanh thu theo ngày/tháng để tối ưu dung lượng Database.

- [x] `[FEAT]` 🟡 **Vu Caffe Telegram Notification** — `noti_telegram.py` — 2026-02-24
  Thiết lập Single Doctype `Vu Caffe Config` lưu Token, tạo cron job gửi báo cáo doanh thu/chi phí vào 8h sáng hàng ngày qua Telegram.

### 🟢 Low — Backlog

- [ ] `[DOCS]` 🟢 Thiếu inline documentation cho toàn bộ API functions Python
- [ ] `[PERF]` 🟢 `sessionStorage` caching trong Frontend không có TTL/invalidation strategy
- [ ] `[FEAT]` 🟢 Tích hợp thanh toán VN: VietQR, MoMo, ZaloPay
- [ ] `[FEAT]` 🟢 Báo cáo xuất Excel theo định dạng Việt Nam
- [ ] `[FEAT]` 🟢 Hỗ trợ VAT 10% theo quy định Việt Nam (hiện chỉ có tax generic)
- [ ] `[FEAT]` 🟢 In hóa đơn theo mẫu Bộ Tài Chính Việt Nam

---

## [v0.1.0-vn] — 2026-02-23 — Phase 1: Bug Fixes & Performance ✅

### Fixed / Performance

- [x] `[PERF]` 🔴 **N+1 Query trong Cronjob** — `ury_kot_validation.py` — 2026-02-23  
  Refactor `kotValidationThread()` từ N+1 (150+ queries/phút) xuống ~6 batch queries. Batch-load POS Invoices, POS Profiles, Productions, Item Groups, và existing KOTs trước vòng lặp.

- [x] `[PERF]` 🔴 **N+1 Query trong KOT Generate** — `ury_kot_generate.py` — 2026-02-23  
  `process_items_for_kot()`: batch-fetch item groups trước loop, thêm `get_production_item_group_map()` để 1 query thay cho N queries. Batch check existing KOTs per production.

- [x] `[PERF]` 🔴 **N+1 trong KOT Display** — `ury_kot_display.py` — 2026-02-23  
  Dùng `fields=[...]` đầy đủ trong `frappe.get_list()`. Batch-fetch tất cả `URY KOT Items` trong 1 query, group by parent. Không còn loop `frappe.get_doc()`.

- [x] `[FIX]` 🔴 **Hardcoded `currency: "INR"` trong P&L** — `ury_daily_p_and_l.py:542` — 2026-02-23  
  Đọc dynamic từ `frappe.get_cached_value("Company", company, "default_currency")`.

- [x] `[FIX]` 🔴 **Hardcoded `'INR'` trong Frontend** — `pos-store.ts` — 2026-02-23  
  Đổi 3 occurrences `|| 'INR'` → `|| 'VND'`.

- [x] `[FIX]` 🟠 **Debug `print()` statements trong Production** — `ury_kot_display.py` — 2026-02-23  
  Xóa 3 `print()` raw debug statements trong `served_kot_list()`.

- [x] `[PERF]` 🟠 **Double `frappe.get_doc("POS Invoice")` trong `create_cancel_kot_doc()`** — `ury_kot_generate.py` — 2026-02-23  
  Thay bằng `frappe.db.get_value()` với multi-field tuple để 1 round-trip.

- [x] `[PERF]` 🟠 **3 Queries riêng biệt cho POS Profile** — `ury_kot_display.py` — 2026-02-23  
  Gộp `kot_alert_time`, `daily_order_number`, `audio_alert` thành 1 `frappe.db.get_value()` multi-field call.

- [x] `[REFACTOR]` 🟠 **Duplicate `kot_list()` / `served_kot_list()`** — `ury_kot_display.py` — 2026-02-23  
  Merge thành `_build_kot_response(order_status)` helper. Public API giữ nguyên.

- [x] `[PERF]` 🟠 **3 `db_set()` riêng biệt trong `serve_kot()`** — `ury_kot_display.py` — 2026-02-23  
  Gộp thành 1 `frappe.db.set_value("URY KOT", name, {...})` với dict.

- [x] `[REFACTOR]` 🟡 **O(n²) `compare_two_array()`** — `ury_kot_generate.py` — 2026-02-23  
  Refactor từ O(n²) nested filter/loop sang O(n) dict lookup.

- [x] `[SECURITY]` 🟡 **Search regex chặn tiếng Việt có dấu** — `pos_extend.py` — 2026-02-23  
  Cập nhật regex thành `[\w\s\-_@.'\u00C0-\u024F\u1E00-\u1EFF]+` với `re.UNICODE`.

- [x] `[FIX]` 🟡 **`formatCurrency()` không format số** — `utils.ts` — 2026-02-23  
  Rewrite dùng `Intl.NumberFormat('vi-VN')`. VND: không có thập phân, dấu chấm phân cách ngàn, symbol sau số `(1.000.000 ₫)`.

---

## Hướng dẫn ghi CHANGELOG

Khi fix xong 1 item, chuyển từ `- [ ]` sang `- [x]` và thêm ngày:  
`- [x] [PERF] 🔴 **Tiêu đề** — Fixed: YYYY-MM-DD`

Khi release version mới, tạo section `## [vX.Y.Z-vn] — YYYY-MM-DD`


v2

# CHANGELOG — URY ERP (Fork cá nhân)
> Format: [Ngày] — [Loại] — [Mô tả] — [Root Cause] — [Impact]
> Luôn điền ROOT CAUSE để tránh fix tầng ngọn

---

## Hướng dẫn điền

| Loại | Ký hiệu | Màu |
|------|---------|-----|
| Bug fix (N+1, crash, security) | 🔴 BUG | Đỏ |
| Performance improvement | 🟡 PERF | Vàng |
| Tính năng mới Việt Nam | 🟢 VN | Xanh lá |
| Refactor / SOLID / Clean code | 🔵 REFACTOR | Xanh |
| DB Schema / Migration | 🟣 DB | Tím |
| Security / Permission | ⚫ SEC | Đen |

---

## [Template — Copy mỗi lần thay đổi]

```
## [YYYY-MM-DD] — Tiêu đề ngắn

### [Loại] Mô tả vấn đề
- **File thay đổi**: `đường/dẫn/file.py` (line X-Y)
- **Vấn đề gốc**: Mô tả vấn đề người dùng thấy
- **Root Cause - Tầng CODE**: [Có/Không] — lý do
- **Root Cause - Tầng DB**: [Có/Không] — lý do  
- **Fix thực hiện**: Mô tả cụ thể đã làm gì
- **Test**: Đã kiểm tra với dữ liệu như thế nào
- **Performance trước/sau**: [nếu có đo được]
- **Liên quan**: #issue hoặc link PR gốc URY nếu có
```

---

## Lịch sử thay đổi

<!-- Thêm entries mới Ở TRÊN, không ở dưới -->

## [2026-02-24] — Vu Caffe Giảm Tải Database & Cài Đặt Telegram Notifier

### 🟢 VN Tích hợp Cấu Hình Config Single Doctype UI, Aggregator, và Telegram
- **File thay đổi**: `scheduler_vu_caffe.py`, `noti_telegram.py`, `vu_caffe_config.py`
- **Vấn đề gốc**: DB đầy rất nhanh do query / lưu trữ từng record 1 theo ngày làm nặng hệ thống. Không có báo cáo gọn nhẹ cho Admin quán nhỏ.
- **Root Cause - Tầng CODE**: Có — Hệ thống thiếu custom cron cho aggregated map. Thiếu webhook push qua telegram.
- **Root Cause - Tầng DB**: Có — Cần design Doctype JSON map thay vì Row based.
- **Fix thực hiện**: 
  - Khai báo Cron 8h Sáng chạy module EOD Calculator lấy revenue, cost. 
  - Lưu vào `Vu Caffe Daily Report` dạng { day : {rev, cost} }.
  - Trigger API sendMessage của Telegram dùng Token / Chat ID lưu trong Single Config.
- **Test**: Compile python files successfully. Config UI tested qua Single Doctype.
- **Performance trước/sau**: DB Storage Space sẽ giảm đi >80% mỗi tháng do thu gom 30 order rows thành 1 JSON object.

---

## [2026-02-24] — Tích hợp i18n Việt hóa (Phase 2)

### 🟢 VN Thêm i18n cho Frontend POS và Backend Frappe
- **File thay đổi**: `pos/src/pages/POS.tsx`, `ury/translations/vi.csv`, `pos/src/components/*`
- **Vấn đề gốc**: UI POS hiển thị tiếng Anh cứng (hardcoded), không có file dịch cho Backend Frappe.
- **Root Cause - Tầng CODE**: Có — UI thiết kế chưa bọc hooks dịch thuật.
- **Root Cause - Tầng DB**: Không.
- **Fix thực hiện**: 
  - Thay thế hardcoded strings trong `pos/src` bằng `t()` từ hook `useTranslation` của `react-i18next`.
  - Tạo tệp `ury/translations/vi.csv` cung cấp bản dịch chuẩn cho các nhãn, trạng thái, và Doctype của module URY POS.
- **Test**: Khởi chạy Node app và hiển thị đúng ngôn ngữ tiếng Việt theo dictionary `vi.json`.
- **Performance trước/sau**: N/A
- **Liên quan**: Phase 2 Việt hóa

---

## [2025-XX-XX] — Khởi tạo fork từ URY v0.2.1

### 🟢 VN Chuẩn bị nền tảng Việt hoá
- **File thay đổi**: `ury/hooks.py`, `ury/fixtures/`
- **Vấn đề gốc**: Hệ thống dùng USD, timezone UTC, format ngày US
- **Root Cause - Tầng CODE**: Không phải bug, cần cấu hình lại defaults
- **Root Cause - Tầng DB**: N/A
- **Fix thực hiện**: 
  - Set default currency VND
  - Set timezone Asia/Ho_Chi_Minh  
  - Set date format dd-mm-yyyy
  - Set number format #.###,##
- **Test**: Tạo invoice test, kiểm tra hiển thị tiền VND
- **Performance trước/sau**: N/A

---

## Known Issues từ URY gốc (cần theo dõi)

| # | Vấn đề | Tầng | Độ ưu tiên | Trạng thái |
|---|--------|------|------------|------------|
| 1 | N+1 khi load KOT list với nhiều items | Code (lazy load) | 🔴 Cao | Cần audit |
| 2 | Thiếu index trên `status`, `branch`, `posting_date` | DB Design | 🔴 Cao | Cần audit |
| 3 | SQL injection đã fix v0.2.1 nhưng cần review thêm | Security | 🔴 Cao | Cần review |
| 4 | Cronjob scope chưa rõ (filter branch?) | Code | 🟡 Trung | Cần audit |
| 5 | Frontend gọi nhiều API cho 1 màn hình POS | Code | 🟡 Trung | Cần audit |
| 6 | Không có hoá đơn điện tử theo ND123 | Feature | 🟢 Thấp | Cần thêm |
| 7 | Thanh toán VietQR/Momo chưa có | Feature | 🟢 Thấp | Cần thêm |
