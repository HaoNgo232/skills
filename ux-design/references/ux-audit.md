# BỘ QUY TẮC KIỂM TOÁN VÀ TÁI THIẾT KẾ TRẢI NGHIỆM NGƯỜI DÙNG (UX AUDIT & REDESIGN PLAYBOOK)

Tài liệu này là kim chỉ nam bắt buộc khi Agent được triệu hồi để kiểm tra, đánh giá (audit), chẩn đoán lỗi trải nghiệm hoặc tái thiết kế (redesign) một luồng/hệ thống đã tồn tại (Brownfield System).

---

## 1. PHƯƠNG PHÁP LUẬN ĐÁNH GIÁ (AUDIT METHODOLOGY)

Khi tiếp cận một hệ thống hiện hữu (qua code, sơ đồ, ảnh chụp giao diện, tài liệu đặc tả, hoặc mô tả luồng), Agent phải thực hiện đồng thời 2 kỹ thuật kiểm toán tiêu chuẩn quốc tế:

1. **Heuristic Evaluation (Đánh giá theo 10 Heuristics của Nielsen & 7 Nguyên tắc ISO 9241-110):**
   * Soi chiếu từng bước tương tác để tìm các vi phạm về tính nhất quán, phản hồi trạng thái, phòng chống lỗi và quyền kiểm soát của người dùng.
2. **Cognitive Walkthrough (Mô phỏng tư duy từng bước của con người):**
   Tại mỗi bước tương tác của người dùng, tự đặt 4 câu hỏi định mệnh:
   * *Q1:* Người dùng có biết chính xác mình cần làm gì để tiến tới mục tiêu không?
   * *Q2:* Người dùng có nhìn thấy thao tác/nút bấm đúng trên giao diện/bối cảnh không?
   * *Q3:* Người dùng có hiểu thao tác đó tương ứng với mục tiêu của họ không?
   * *Q4:* Sau khi thao tác, hệ thống có phản hồi rõ ràng cho họ biết kết quả và trạng thái mới chưa?

---

## 2. CHỈ SỐ MỨC ĐỘ NGHIÊM TRỌNG (SEVERITY INDEX)

Mọi vấn đề phát hiện đều phải được dán nhãn mức độ nghiêm trọng:

* 🔴 **CRITICAL (Blocker / Dead-End - Điểm nghẽn chí mạng):**
  * *Đặc điểm:* Khiến người dùng bế tắc hoàn toàn, không thể hoàn thành tác vụ; gây mất dữ liệu không thể cứu vãn; gây rủi ro tài chính/tính mạng; bẫy người dùng vào ngõ cụt không có nút thoát/hủy.
  * *Hành động:* Ưu tiên giải quyết hàng đầu trước mọi cải tiến khác.
* 🟡 **MAJOR (High Cognitive Friction - Ma sát nhận thức cao):**
  * *Đặc điểm:* Người dùng vẫn có thể hoàn thành mục tiêu nhưng phải mất nhiều thời gian mò mẫm, dễ nhầm lẫn, phải ghi nhớ nhiều thông tin giữa các màn hình, tỷ lệ bỏ dở (drop-off) cao.
  * *Hành động:* Tái cấu trúc lại luồng logic, tinh gọn bước đi, bổ sung gợi ý ngữ cảnh.
* 🟢 **MINOR (Polish & Cosmetic - Chưa trau chuốt / Tinh chỉnh thẩm mỹ):**
  * *Đặc điểm:* Luồng hoạt động ổn định nhưng vi phạm tính nhất quán từ ngữ, vị trí căn chỉnh chưa chuẩn, thiếu micro-interaction tinh tế để tạo cảm xúc thỏa mãn (delight).
  * *Hành động:* Tối ưu hóa trong các đợt cập nhật định kỳ.

---

## 3. KHUNG BÁO CÁO PHÁT HIỆN & GIẢI PHÁP (MANDATORY AUDIT FINDING SCHEMA)

Khi báo cáo một vấn đề UX, Agent **bắt buộc** phải tuân theo cấu trúc 5 thành phần sau:

```
[Mức độ nghiêm trọng: 🔴 CRITICAL | 🟡 MAJOR | 🟢 MINOR] - Tên vấn đề ngắn gọn
• Vị trí / Điểm chạm: [Màn hình, Bước nào trong luồng, hoặc Thành phần tương tác cụ thể]
• Triệu chứng vi phạm: [Mô tả chính xác khó khăn/ma sát mà người dùng gặp phải]
• Nguyên tắc đối chiếu: [Trích dẫn vi phạm: Nielsen Heuristics / ISO 9241-110 / WCAG 2.2]
• Đề xuất Tái thiết kế (Actionable Solution): [Giải pháp cụ thể: thay đổi cấu trúc, bỏ bước nào, thêm feedback gì, đổi luồng logic ra sao]
• Tác động đo lường được (Expected Impact): [Tác động cụ thể đến chỉ số: giảm % drop-off, giảm x giây Time on Task, triệt tiêu 100% rủi ro mất dữ liệu, v.v.]
```

---

## 4. CHECKLIST PHÁT HIỆN "CÁC LỖI THIẾT KẾ KHÔNG GIỐNG CON NGƯỜI" (ANTI-BIAS AUDIT)

Khi audit, Agent phải đặc biệt quét tìm các "mùi hôi UX" (UX Smells) bắt nguồn từ tư duy máy móc của lập trình viên/nhà thiết kế (đối chiếu chi tiết với tài liệu `references/cognitive-biases.md`):

- [ ] **Lỗi "Bắt ép dùng Não số 2" (System 2 Overload - Kahneman):** Bắt người dùng phải tính toán nhẩm, quy đổi đơn vị, hoặc so sánh quá nhiều thông số phức tạp thay vì hệ thống tự tính và gợi ý trực giác.
- [ ] **Lỗi "Vượt ngưỡng Bộ nhớ làm việc 4-Chunks" (Working Memory Overflow - Cowan):** Bắt người dùng phải nhớ thông tin từ màn hình trước để điền vào màn hình sau.
- [ ] **Lỗi "Rò rỉ Cấu trúc Database lên Giao diện" (Database Leakage / Leaky Abstractions):** Bắt người dùng nhập liệu theo đúng thứ tự khóa ngoại bảng cơ sở dữ liệu thay vì theo trình tự công việc thực tế của họ ngoài đời.
- [ ] **Lỗi "Người dùng Hoàn hảo" (Ideal User Fallacy):** Hệ thống giả định người dùng sẽ đọc toàn bộ đoạn hướng dẫn dài 5 dòng trước khi bấm nút.
- [ ] **Lỗi "Mất dữ liệu khi Back / Reload" (State Wipeout):** Người dùng nhập form 10 trường, ấn nhầm back hoặc bị đứt mạng và toàn bộ dữ liệu bị xóa sạch.
- [ ] **Lỗi "Thông báo lỗi mù mờ" (Cryptic Error - Curse of Knowledge):** Báo lỗi kiểu `Error 500: Invalid transaction state` thay vì chỉ rõ trường nào sai và hướng dẫn cách sửa cụ thể.
- [ ] **Lỗi "Bẫy xác nhận mù quáng" (Alert Fatigue / Confirmation Habituation):** Bật popup cảnh báo "Bạn có chắc chắn không?" cho mọi thao tác vặt vãnh, khiến người dùng hình thành phản xạ bấm "OK" mà không thèm đọc, đến khi có thao tác phá hủy thật thì lại bấm nhầm.

---

## 5. BẢNG TỔNG KẾT IMPACT SAU TÁI THIẾT KẾ

Kết thúc phần Audit & Redesign, Agent phải tổng kết bức tranh so sánh Trước vs. Sau cải tiến ngay trong phản hồi Markdown:

| Chỉ số đo lường (Metric) | Hệ thống hiện tại (As-Is) | Sau khi Tái thiết kế (To-Be) | Tác động dự kiến (Impact) |
|---|---|---|---|
| **Số bước thao tác (Steps to Goal)** | x bước | y bước | Giảm Z% thao tác thừa |
| **Tải nhận thức (Cognitive Load)** | Cao (Cần nhớ x điều kiện) | Thấp (Tự động hóa / Gợi ý ngữ cảnh) | Tránh sai sót nhầm lẫn |
| **Khả năng phục hồi lỗi (Error Recovery)** | Bế tắc / Phải làm lại từ đầu | 1-Click Undo / Lưu nháp tự động | Triệt tiêu 100% ức chế mất dữ liệu |
| **Thời gian chạm giá trị (Time-to-Value)** | ~x phút | ~y giây/phút | Rút ngắn đáng kể |

