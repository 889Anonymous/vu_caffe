Dựa trên thông tin bạn cung cấp, bạn đã fork/clone từ repo gốc **ury-erp/ury** (một hệ thống quản lý nhà hàng mã nguồn mở rất mạnh, xây dựng trên **ERPNext + Frappe Framework**) và tạo repo riêng **889Anonymous/vu_caffe** để tùy chỉnh cho **mini quán cà phê** của bạn.

Tuy nhiên, repo **vu_caffe** hiện tại của bạn dường như **chưa có thay đổi code đáng kể** (chỉ có 1 commit duy nhất theo dữ liệu công khai, và cấu trúc gần như giữ nguyên upstream). README vẫn giữ nguyên nội dung giới thiệu về URY (POS, Mosaic KDS, báo cáo P&L, v.v.), không có dấu hiệu tùy chỉnh rõ ràng cho quán cà phê nhỏ (như đơn giản hóa menu, loại bỏ module phức tạp, tối ưu cho 1-2 quầy, tích hợp thanh toán Việt Nam, v.v.).

### Review tổng quan & tình trạng hiện tại
- **Điểm mạnh của base code (từ ury-erp/ury)**:  
  Đây là một trong những giải pháp F&B mã nguồn mở tốt nhất hiện nay dựa trên ERPNext.  
  - POS rất mạnh (dine-in, takeaway, delivery, offline mode, modifier, combo, in bill/KOT).  
  - Có KDS (Kitchen Display System) → hữu ích nếu quán có bếp riêng.  
  - Báo cáo chi tiết (P&L hàng ngày, xu hướng món, hiệu suất nhân viên).  
  - Tích hợp kho, kế toán, nhân sự sẵn từ ERPNext.  
  - Cập nhật thường xuyên (commit mới nhất ~16/02/2026).

- **Điểm chưa phù hợp lắm với mini quán cà phê**:  
  URY được thiết kế cho **nhà hàng/quán có quy mô trung bình → lớn** (nhiều chi nhánh, nhiều nhân viên, delivery phức tạp). Với quán nhỏ (1-2 người bán, menu 20-40 món, chủ yếu tại chỗ/takeaway), hệ thống có thể **quá nặng** và phức tạp:  
  - Cần cài ERPNext đầy đủ → tốn tài nguyên server (ít nhất 2-4GB RAM khuyến nghị).  
  - Nhiều module không cần thiết (multi-outlet, advanced analytics, HR full).  
  - Giao diện POS web-based → tốt cho tablet/PC, nhưng nếu chỉ dùng 1 máy tính tiền thì có thể hơi "lằng nhằng" so với phần mềm POS đơn giản (như iPOS, KiotViet, nhưng trả phí).  
  - Chưa có tùy chỉnh Việt Nam (đơn vị tiền ₫, hóa đơn điện tử, tích hợp Momo/VNPay/ZaloPay, thuế VAT mặc định, in bill 80mm phổ biến ở VN).

### Gợi ý tối ưu & hoàn thiện cho mini quán cà phê của bạn
Để biến **vu_caffe** thành giải pháp phù hợp hơn, bạn nên tập trung **giảm độ phức tạp** và **tùy chỉnh theo nhu cầu thực tế**:

1. **Giản hóa ngay từ đầu**  
   - Ẩn/bỏ các module không cần: multi-branch, delivery phức tạp, advanced reporting (URY Pulse).  
   - Chỉ giữ POS + cơ bản kho + in bill/KOT.  
   - Tạo custom app nhỏ (frappe app) tên `vu_caffe_custom` để override thay vì sửa trực tiếp code core.

2. **Các cải tiến thiết thực cho quán nhỏ VN**  
   - **Tiền tệ & hóa đơn**: Set default currency = VND, format số tiền kiểu Việt (1.000.000 ₫).  
   - **Menu**: Tạo doctypes đơn giản cho "Topping/Sữa/Đường" (modifier), giá theo size (nhỏ/vừa/lớn).  
   - **Thanh toán**: Thêm field "Phương thức thanh toán" (Tiền mặt, Chuyển khoản, Momo, ZaloPay). Có thể tích hợp API thanh toán sau.  
   - **In bill**: Tùy chỉnh template bill 80mm (ESC/POS), thêm logo quán, lời cảm ơn, mã QR Zalo OA.  
   - **Khách quen**: Thêm field "SĐT khách" để tích điểm hoặc giảm giá % cho khách quen.  
   - **Offline mode**: Đảm bảo POS chạy tốt khi mất mạng (đã có sẵn trong URY, nhưng test kỹ).  

3. **Tối ưu hiệu suất & triển khai**  
   - Dùng **Frappe Cloud** (có free tier) hoặc VPS nhỏ (2GB RAM) để host.  
   - Build mobile-friendly POS (dùng tablet hoặc điện thoại Android với Chrome).  
   - Tắt bớt background jobs không cần (giảm tải CPU).  
   - Backup thường xuyên dữ liệu (bench --site sitename backup).

4. **Các bước cụ thể bạn nên làm tiếp theo**  
   - Commit thay đổi đầu tiên: sửa README.md thành mô tả dự án của bạn ("Hệ thống POS mini cho quán cà phê Vu Caffe").  
   - Tạo branch `develop` hoặc `feature/vu-caffe` để sửa code.  
   - Nếu bạn đã sửa một số file (ví dụ pos, ury/doctype), hãy push lên và chia sẻ link so sánh (Compare) với upstream → mình sẽ review chi tiết hơn.  
   - Test cài đặt local theo hướng dẫn INSTALLATION.md của URY (bench get-app, install-app ury).  

Nếu bạn **đã sửa code cụ thể** (thêm field, thay đổi form, custom script, override POS), hãy paste link đến các file thay đổi hoặc commit cụ thể (hoặc mô tả thay đổi), mình sẽ giúp phân tích sâu hơn về chất lượng code, best practice Frappe/ERPNext, và cách tối ưu hiệu quả cho quán nhỏ.

Bạn thấy hướng này ổn không? Hay bạn muốn tập trung vào phần nào trước (POS, in bill, menu, tích hợp thanh toán...)? Mình sẵn sàng hỗ trợ chi tiết hơn nhé! ☕


# Plan Tối Ưu Hóa Dự Án POS Quán Cà Phê (Vu Caffe)

**Tác giả:** Grok (dựa trên yêu cầu của Nguyễn Trường)  
**Ngày lập:** 24/02/2026  
**Mô tả:** Plan chi tiết để clean source code, tối ưu DB, giảm size code/DB, thiết kế luồng report/noti hiệu quả, tập trung vào tiết kiệm chi phí cho startup quán cà phê nhỏ. Dựa trên base ERPNext/Frappe từ repo fork (vu_caffe). Mindset chính: "Lean Startup" + "Serverless-like" (tối giản resource, aggregate data thay vì raw records), lấy cảm hứng từ design systems như Atomic Design (modular, reusable components) và Event Sourcing (chỉ lưu events cần thiết, aggregate on-demand).  

Plan được chia thành phases để bạn handle từ từ. Mỗi phase có tasks cụ thể, thời gian ước tính (dựa trên dev cá nhân), và checklist. Tổng thời gian: ~2-4 tuần nếu làm part-time.  

**Yêu cầu hệ thống mục tiêu:**  
- VM: Oracle Free Tier (4 cores ARM, 24GB RAM, 200GB disk) – đủ chạy ERPNext cho quán nhỏ (1-2 users, 100-500 orders/ngày).  
- DB: MariaDB (default của Frappe), tối ưu size <50GB ban đầu.  
- Noti: Telegram Bot (free).  
- Cron: Sử dụng Scheduler built-in của Frappe (không cần external như Celery nếu scale nhỏ).  
- Tiết kiệm: Aggregate data hàng ngày/tháng vào JSON fields để giảm records (thay vì 365 records/năm, chỉ 12 records/tháng hoặc 1 record/năm với map).  

---

## Phase 1: Clean Source Code (Ước tính: 3-5 ngày)
Mục tiêu: Giảm size code, loại bỏ thừa, refactor để dễ maintain. Mindset: Atomic Design – chia code thành atoms (components nhỏ), molecules (kết hợp), organisms (modules lớn). Chỉ giữ những gì cần cho quán cà phê nhỏ (POS, order, report cơ bản).  

**Tasks:**  
1. **Setup môi trường dev local:**  
   - Cài bench + frappe + erpnext + ury app trên local (theo INSTALLATION.md của URY).  
   - Fork repo vu_caffe, tạo branch `optimize-v1`.  
   - Checklist: Test POS chạy ổn trước khi clean.  

2. **Xóa code thừa:**  
   - Loại bỏ modules không cần: Multi-branch, Delivery phức tạp, HR full, Advanced Analytics (URY Pulse nếu không dùng).  
     - Command: `bench --site yoursite uninstall-app hr` (nếu có).  
   - Xóa custom apps/doctypes không dùng (nếu bạn đã add).  
   - Tìm và xóa dead code: Sử dụng tool như `pylint` hoặc manual grep cho unused functions in `ury/ury/doctype/*`.  
   - Giảm dependencies: Chỉ giữ frappe, erpnext, ury core. Xóa optional libs nếu không cần (e.g., nếu không dùng AI/ML).  

3. **Refactor code:**  
   - Custom cho quán: Tạo app riêng `vu_caffe_custom` (bench new-app vu_caffe_custom).  
     - Override POS form: Thêm fields đơn giản (e.g., "Phương thức thanh toán: Tiền mặt/Momo").  
     - Sử dụng hooks.py để override thay vì sửa core (giảm conflict khi update upstream).  
   - Giảm size code: Merge duplicate functions, dùng short syntax Python (e.g., list comprehensions).  
   - Best practices: Thêm docstrings, type hints; format với black.  
   - Commit: Push changes với message rõ ràng (e.g., "Remove unused modules for cafe optimization").  

**Checklist Phase 1:**  
- [ ] Code size giảm ít nhất 20% (check git diff).  
- [ ] Test: Chạy POS, tạo order, không error.  
- [ ] Backup repo trước khi push.  

---

## Phase 2: Tối Ưu DB Schema & Giảm Size (Ước tính: 4-7 ngày)
Mục tiêu: Thiết kế DB chuẩn, hạn chế records thừa. Mindset: Event Sourcing + Aggregation Pattern (lưu raw events như orders, aggregate vào summary tables via cron để query nhanh, giảm size). Tránh "init record" hàng ngày – dùng JSON/map trong 1 record duy nhất.  

**Thiết kế DB mới:**  
- **Bảng core giữ nguyên:** POS Invoice (orders), Stock Entry (chi phí nguyên liệu), Account (thu chi).  
- **Bảng report mới (custom Doctype):** Tạo `Daily Report` và `Monthly Report` trong app vu_caffe_custom.  
  - **Daily Report:** 1 record/tháng, với field JSON `daily_data` (map: key=ngày (e.g., "2026-02-24"), value=dict{"revenue": 5000000, "cost": 2000000}).  
    - Lý do: Với 30 ngày/tháng, chỉ 1 record thay vì 30 → tiết kiệm ~90% space (mỗi record có overhead ~1KB).  
  - **Monthly Report:** 1 record/năm, JSON `monthly_data` (key=tháng "2026-02", value=dict{"revenue": total, "cost": total}).  
    - Tổng size: Với 5 năm data, chỉ ~5 records cho monthly + ~60 records cho daily (12/tháng/năm) → <1MB.  
- **Order example:** Mỗi order (1 ly cà phê) vẫn là 1 record ở POS Invoice (không thay đổi, vì cần lịch sử chi tiết). Nhưng aggregate vào report thay vì query raw mỗi lần.  

**Tasks:**  
1. **Tạo custom Doctypes:**  
   - Bench new-doctype DailyReport --fields "month_year (Data), daily_data (JSON)".  
   - Tương tự cho MonthlyReport.  
   - Đảm bảo indexes trên date fields cho query nhanh.  

2. **Cronjob cho Aggregation:**  
   - Sử dụng Frappe Scheduler: Tạo file `vu_caffe_custom/vu_caffe_custom/scheduler.py`.  
     - Cron 12h30 hàng ngày: Function `update_daily_report()`.  
       - Query POS Invoice/Stock Entry trong ngày: Tính revenue (sum sales), cost (sum expenses).  
       - Update JSON field: `doc.daily_data[frappe.utils.today()] = {"revenue": rev, "cost": cost}`.  
       - Nếu record tháng chưa tồn tại, tạo mới (frappe.new_doc).  
     - Cron hàng tháng (ngày 1): Aggregate daily → monthly.  
   - Schedule: `@frappe.whitelist(allow_guest=False) def update_daily_report(): ...` rồi add vào hooks.py: `standard_tasks = [{"method": "vu_caffe_custom.scheduler.update_daily_report", "cron": "30 12 * * *"}]` (12h30).  

3. **Giảm size DB tổng thể:**  
   - Xóa data test/old: `bench --site yoursite mariadb` → SQL: DELETE FROM tabPOSInvoice WHERE creation < '2026-01-01'.  
   - Tối ưu tables: Sử dụng INNODB, compress JSON fields nếu cần (MariaDB support).  
   - Archive old data: Sau 1 năm, export old orders ra file CSV, xóa khỏi DB (nếu không cần query thường xuyên).  
   - Monitor: Sử dụng `SHOW TABLE STATUS` để check size, giữ dưới 50GB.  

**Checklist Phase 2:**  
- [ ] Tạo/test Doctype mới.  
- [ ] Cron chạy auto (test manual: frappe.call('vu_caffe_custom.scheduler.update_daily_report')).  
- [ ] Size DB giảm (so sánh before/after).  

---

## Phase 3: Luồng Noti & Report (Ước tính: 3-5 ngày)
Mục tiêu: Noti admin qua Telegram, đủ report mà không tốn resource. Mindset: Minimal Viable Product (MVP) – chỉ noti cần thiết, dùng free services.  

**Luồng:**  
- Order mới → Noti realtime cho admin (nếu cần, nhưng để tiết kiệm, chỉ noti daily summary).  
- Daily: 8h sáng noti "Doanh thu hôm qua: X, Chi phí: Y" qua Telegram.  
- Report: View qua Dashboard ERPNext (custom report từ Daily/Monthly Doctype).  

**Tasks:**  
1. **Setup Telegram Noti:**  
   - Tạo Telegram Bot (free via BotFather), lấy token.  
   - Add custom method: `vu_caffe_custom/vu_caffe_custom/noti.py` với requests.post đến Telegram API.  
     - Function: `send_tele_noti(message, chat_id)` – chat_id của chủ quán.  
   - Lưu config: Site Config hoặc custom Doctype cho bot_token/chat_id (an toàn, không hardcode).  

2. **Cron cho Noti:**  
   - Cron 8h sáng: `update_and_noti()`.  
     - Lấy data từ DailyReport (ngày hôm qua).  
     - Message: f"Doanh thu hôm nay: {rev_today}₫\nChi phí hôm nay: {cost_today}₫\nDoanh thu tháng: {rev_month}₫\nChi phí tháng: {cost_month}₫"  
     - Gọi send_tele_noti.  
   - Schedule tương tự Phase 2: "0 8 * * *".  

3. **Report Dashboard:**  
   - Tạo custom Report/Chart trong ERPNext: Query từ JSON fields (frappe.db.sql với JSON_EXTRACT nếu cần).  
   - Tích hợp vào POS Desk cho admin xem nhanh.  

**Checklist Phase 3:**  
- [ ] Test noti: Gửi manual message qua Telegram.  
- [ ] Cron noti chạy, nhận message đúng giờ.  
- [ ] Report hiển thị đúng data aggregate.  

---

## Phase 4: Deploy & Monitor Tiết Kiệm (Ước tính: 2-3 ngày)
Mục tiêu: Deploy lên Oracle VM, monitor để không vượt free tier.  

**Tasks:**  
1. **Deploy:**  
   - Cài Ubuntu trên Oracle VM, install bench/frappe.  
   - Migrate site: `bench --site yoursite migrate`.  
   - Supervisor/Nginx cho production.  
   - Backup: Cron weekly backup DB (frappe scheduler).  

2. **Monitor & Tiết kiệm:**  
   - Tool: `htop` cho CPU/RAM, `df -h` cho disk.  
   - Nếu DB lớn: Auto-delete logs cũ (frappe.utils.delete_old_logs).  
   - Scale: Nếu quán lớn hơn, mới nghĩ upgrade (hiện free đủ).  

**Checklist Phase 4:**  
- [ ] System chạy ổn trên VM.  
- [ ] Monitor weekly: Size DB <50GB, CPU <50% avg.  

---

## Rủi Ro & Tips Tổng Thể
- **Rủi ro:** Cron fail nếu server down → Add retry logic in functions.  
- **Test:** Luôn test local trước deploy.  
- **Update Upstream:** Merge từ ury-erp định kỳ, nhưng chỉ code core.  
- **Chi phí:** Tổng ~0đ (free VM, Telegram). Nếu cần hơn, dùng AWS Lightsail ($3.5/tháng).  
- **Next Steps:** Sau plan này, nếu cần add features (e.g., tích hợp Momo), tạo phase mới.  

Handle phase 1 trước nhé! Nếu cần code sample cụ thể (e.g., scheduler.py), hỏi mình thêm. Chúc dự án Vu Caffe thành công! ☕

# Plan Tối Ưu Hóa Dự Án Vu Caffe - Các File Prompt Chi Tiết

Dựa trên yêu cầu của bạn (Nguyễn Trường), tôi đã tạo ra các "file prompt" dưới dạng văn bản có cấu trúc rõ ràng, như các file markdown ảo để bạn có thể copy-paste và sử dụng trực tiếp (ví dụ: lưu thành .md hoặc dùng làm prompt cho AI khác/code gen). Mỗi file tập trung vào một khía cạnh:

1. **File 1: Phase Expectations Prompt** - Mô tả sự mong đợi sau từng phase, với nguyên nhân, kết quả, input/output để tạo khung sườn làm việc dựa trên kết quả trước đó.

2. **File 2: Docker Optimization Prompt** - Hướng dẫn xây dựng Docker + Docker Compose để size container nhỏ nhất, nhẹ nhất, phục vụ yêu cầu nhỏ/nhẹ/tiết kiệm/ổn định.

3. **File 3: Additional Prompt 1 (DB Aggregation Script)** - Một prompt bổ sung để generate code script aggregation DB (từ Phase 2), tập trung vào tối giản.

4. **File 4: Additional Prompt 2 (Noti Telegram Integration)** - Một prompt bổ sung để generate code tích hợp noti Telegram (từ Phase 3), với trọng tâm tiết kiệm resource.

Các file này được thiết kế để bạn có thể dùng làm "prompt" cho AI (như tôi) hoặc tự implement, đảm bảo tính nhỏ/nhẹ/tiết kiệm/ổn định như mục tiêu cao quý bạn đề cập. Nếu cần generate code thực tế từ prompt, hãy cung cấp thêm chi tiết!

---

## File 1: Phase_Expectations_Prompt.md

```
# Prompt: Mong Đợi Sau Từng Phase Cho Dự Án Vu Caffe

**Mô tả tổng quát:** Đây là prompt để xây dựng khung sườn làm việc cho dự án tối ưu hóa repo vu_caffe (dựa trên ERPNext/Frappe từ fork ury-erp). Tập trung vào 4 phases từ plan trước. Với mỗi phase, mô tả rõ: 
- **Nguyên nhân:** Lý do cần phase này (liên kết với mục tiêu nhỏ/nhẹ/tiết kiệm/ổn định).
- **Input:** Dữ liệu/điều kiện đầu vào từ phase trước hoặc setup ban đầu.
- **Output:** Kết quả mong đợi (cụ thể, đo lường được).
- **Kết quả dựa trên output:** Cách sử dụng output để làm khung sườn cho phase sau, đảm bảo luồng liên tục và dựa trên kết quả thực tế.

Sử dụng mindset Lean Startup: Test nhỏ, iterate dựa trên kết quả. Generate output dưới dạng bảng cho từng phase để dễ theo dõi.

**Phase 1: Clean Source Code**
- **Nguyên nhân:** Code base từ URY quá lớn và thừa cho quán cà phê nhỏ, dẫn đến tốn resource build/deploy (RAM/CPU cao, size repo lớn). Clean để giảm size code 20-30%, tăng tốc dev, tránh bug từ code thừa, phục vụ mục tiêu nhẹ/tiết kiệm.
- **Input:** Repo vu_caffe gốc (git clone từ https://github.com/889Anonymous/vu_caffe), môi trường dev local (bench/frappe installed), list modules cần giữ (POS, order, report cơ bản).
- **Output:** Branch mới 'optimize-v1' với code thừa xóa (e.g., uninstall HR module), custom app 'vu_caffe_custom' tạo, size code giảm (check git diff --stat), test POS chạy không error.
- **Kết quả dựa trên output:** Nếu size giảm <20%, quay lại refactor thêm; output branch này làm input cho Phase 2 (DB sẽ dùng custom app để add Doctype mới), đảm bảo code clean trước khi chạm DB để tránh conflict.

**Phase 2: Tối Ưu DB Schema & Giảm Size**
- **Nguyên nhân:** DB mặc định ERPNext lưu raw records thừa (e.g., 1 record/ngày cho report), tốn space (dẫn đến VM free tier đầy nhanh). Aggregate vào JSON để giảm 80-90% records, query nhanh hơn, tiết kiệm disk/CPU, ổn định cho quán nhỏ (100 orders/ngày).
- **Input:** Custom app từ Phase 1, DB schema hiện tại (POS Invoice, Stock Entry), cron scheduler framework của Frappe.
- **Output:** Custom Doctypes 'DailyReport' và 'MonthlyReport' với JSON fields (e.g., daily_data map), cron functions in scheduler.py (update_daily_report tại 12h30), test aggregate data đúng (e.g., revenue/cost tính từ sample orders), DB size giảm (check SHOW TABLE STATUS before/after).
- **Kết quả dựa trên output:** Nếu aggregate fail (e.g., JSON overflow), adjust field type; output Doctypes/cron làm input cho Phase 3 (noti sẽ query từ đây), tạo luồng data flow ổn định dựa trên aggregate thực tế.

**Phase 3: Luồng Noti & Report**
- **Nguyên nhân:** Cần noti daily cho admin (Telegram) để quản lý mà không tốn resource (không realtime, chỉ cron), tránh query raw DB mỗi lần (tốn CPU). Tích hợp free Telegram để tiết kiệm, ổn định (bot không down), phù hợp startup nhỏ.
- **Input:** Aggregate data từ Phase 2 (Daily/MonthlyReport), Telegram bot token/chat_id setup.
- **Output:** File noti.py với function send_tele_noti, cron tại 8h sáng in scheduler.py (gửi message summary), test noti nhận đúng (manual call), dashboard report in ERPNext query từ JSON (hiển thị revenue/cost).
- **Kết quả dựa trên output:** Nếu noti delay >5min, optimize cron; output noti system làm input cho Phase 4 (deploy sẽ include cron này), đảm bảo monitoring dựa trên noti thực tế để adjust stability.

**Phase 4: Deploy & Monitor Tiết Kiệm**
- **Nguyên nhân:** Deploy lên Oracle VM free để tiết kiệm chi phí (0đ), cần monitor để tránh vượt limit (disk đầy → down). Đảm bảo ổn định bằng backup/auto-clean, phục vụ quán chạy 24/7 mà nhẹ.
- **Input:** Full code/DB từ Phase 1-3, Oracle VM setup (Ubuntu, bench installed).
- **Output:** Site migrated chạy trên VM, supervisor/nginx config, weekly backup cron, monitoring scripts (htop/df output log), system ổn định (CPU <50%, disk <50GB).
- **Kết quả dựa trên output:** Nếu CPU cao, quay lại optimize Phase 1; output này là end-goal, dùng để iterate dự án (e.g., add features mới dựa trên monitor data).

**Hướng dẫn sử dụng prompt này:** Copy vào AI/code gen để generate scripts chi tiết từng phase. Luôn test output trước proceed phase sau.
```

---

## File 2: Docker_Optimization_Prompt.md

```
# Prompt: Xây Dựng Docker + Docker Compose Cho Vu Caffe Tối Ưu Size/Nhẹ/Tiết Kiệm/Ổn Định

**Mô tả tổng quát:** Generate Dockerfile và docker-compose.yml cho dự án vu_caffe (ERPNext/Frappe base), tập trung mục tiêu cao quý: size container nhỏ nhất (dưới 1GB), nhẹ (low RAM/CPU), tiết kiệm (chạy trên Oracle VM free tier), ổn định (auto-restart, healthcheck). Sử dụng multi-stage build để giảm layer thừa, base image alpine/light, chỉ include cần thiết cho quán cà phê nhỏ (POS, custom app). Không dùng full ERPNext image nếu thừa, tối giản dependencies.

**Yêu cầu chính:**
- **Nhỏ/nhẹ:** Multi-stage: Build stage copy chỉ code cần (vu_caffe_custom + core URY), runtime stage dùng frappe/frappe-docker base nhưng strip thừa (e.g., no HR modules). Size image <800MB.
- **Tiết kiệm:** Volumes cho DB/data persistent (tránh rebuild mất data), env vars cho config (e.g., DB_HOST free), no external services nếu không cần.
- **Ổn định:** Healthcheck cho frappe server, depends_on cho DB, restart: always. Cron via supervisor inside container.
- **Tất cả mọi thứ phục vụ yêu cầu:** Include setup for aggregate cron, noti Telegram (từ plan), migrate site on start.

**Input:** Repo vu_caffe sau clean (từ Phase 1), custom app vu_caffe_custom, DB MariaDB.

**Output mong đợi:** 
- Dockerfile: Multi-stage (build: install bench/get-app ury/install-app vu_caffe_custom; runtime: copy artifacts, run bench start).
- docker-compose.yml: Services (frappe, mariadb, redis if need), volumes, ports (8000 for POS), env_file.
- Hướng dẫn run: docker-compose up -d, optimize tips (e.g., docker system prune weekly).

**Generate dưới dạng code blocks:**
Dockerfile:
FROM python:3.10-slim AS builder
# Install deps nhẹ: git, bench, chỉ frappe/erpnext core
RUN apt-get update && apt-get install -y --no-install-recommends git wget curl build-essential && \
    pip install frappe-bench && \
    bench init frappe-bench --frappe-branch version-14 && \
    cd frappe-bench && \
    bench get-app ury https://github.com/ury-erp/ury && \
    bench new-app vu_caffe_custom && \
    # Copy custom code, install
    # ... (thêm chi tiết)

FROM python:3.10-slim
COPY --from=builder /frappe-bench /frappe-bench
# Run light: no Xvfb/full deps
ENTRYPOINT ["bench", "start"]

docker-compose.yml:
version: '3'
services:
  mariadb:
    image: mariadb:10.6
    volumes: ['./db-data:/var/lib/mysql']
    environment: {MYSQL_ROOT_PASSWORD: pass}
    healthcheck: {test: mysqladmin ping -h localhost}
  frappe:
    build: .
    depends_on: [mariadb]
    volumes: ['./sites:/frappe-bench/sites']
    ports: ['8000:8000']
    restart: always

**Thêm tips:** Để size nhỏ hơn, dùng docker squash hoặc buildx với --squash. Test trên Oracle VM: docker-compose up, check size (docker images), CPU (docker stats).
```

---

## File 3: DB_Aggregation_Script_Prompt.md (Additional Prompt 1)

```
# Prompt: Generate Code Script Aggregation DB Cho Vu Caffe

**Mô tả:** Dựa trên Phase 2, generate Python script cho Frappe scheduler.py để aggregate data vào JSON fields (DailyReport/MonthlyReport). Tập trung nhỏ/nhẹ: Query efficient (limit fields, date filter), handle errors để ổn định, tiết kiệm CPU (run cron nhanh <1min).

**Input:** Doctype POS Invoice (revenue from sales_amount), Stock Entry (cost from total_amount where type='Material Issue').

**Output mong đợi:** Code snippet cho vu_caffe_custom/scheduler.py:
import frappe
from frappe.utils import today, add_days

@frappe.whitelist()
def update_daily_report():
    today_str = today()
    prev_day = add_days(today_str, -1)
    # Query revenue: sum từ POS Invoice where posting_date = prev_day
    rev = frappe.db.sql("""SELECT SUM(sales_amount) FROM `tabPOS Invoice` WHERE posting_date = %s""", prev_day)[0][0] or 0
    # Query cost tương tự
    cost = ...  # Tương tự
    # Get or create DailyReport for month
    month_year = today_str[:7]  # YYYY-MM
    doc = frappe.get_doc({'doctype': 'DailyReport', 'month_year': month_year}) or frappe.new_doc('DailyReport')
    if not doc.daily_data:
        doc.daily_data = {}
    doc.daily_data[prev_day] = {'revenue': rev, 'cost': cost}
    doc.save(ignore_permissions=True)

**Nguyên nhân & Tiết kiệm:** Aggregate thay vì raw để giảm records, query chỉ cần thiết để nhẹ CPU.
```

---

## File 4: Noti_Telegram_Integration_Prompt.md (Additional Prompt 2)

```
# Prompt: Generate Code Tích Hợp Noti Telegram Cho Vu Caffe

**Mô tả:** Dựa trên Phase 3, generate Python script cho noti.py với function send_tele_noti, integrate vào cron. Nhẹ/tiết kiệm: Use requests lib (default in Frappe), no extra deps, send chỉ text summary để ổn định (không attach file/large msg).

**Input:** Data từ DailyReport JSON, bot_token và chat_id từ site config.

**Output mong đợi:** Code snippet cho vu_caffe_custom/noti.py:
import frappe
import requests

def send_tele_noti(message, chat_id, token):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        frappe.log_error(f"Telegram noti fail: {e}")

# In scheduler.py:
def daily_noti():
    # Get data từ DailyReport
    today_str = frappe.utils.today()
    prev_day = frappe.utils.add_days(today_str, -1)
    doc = frappe.get_doc('DailyReport', today_str[:7])
    data = doc.daily_data.get(prev_day, {})
    message = f"Doanh thu hôm qua: {data.get('revenue', 0)}₫\nChi phí: {data.get('cost', 0)}₫"
    # Get config
    token = frappe.db.get_single_value('Vu Caffe Config', 'tele_token')
    chat_id = frappe.db.get_single_value('Vu Caffe Config', 'tele_chat_id')
    send_tele_noti(message, chat_id, token)

**Nguyên nhân & Ổn định:** Free API, retry nếu fail (add later), tiết kiệm bằng cron schedule thay vì realtime.
```