# THƯ VIỆN CÁC MẪU THIẾT KẾ WORKFLOW ĐA LĨNH VỰC (WORKFLOW PATTERNS CATALOG)

Tài liệu này cung cấp các mẫu thiết kế luồng tác vụ kinh điển, áp dụng linh hoạt cho phần mềm, dịch vụ, thiết bị hoặc quy trình vận hành con người.

---

## 1. MẪU TUẦN TỰ LŨY TIẾN (LINEAR WIZARD / PROGRESSIVE STEPPING)
* **Bối cảnh phù hợp:** Người dùng mới (Novice), tác vụ phức tạp gồm nhiều trường dữ liệu phụ thuộc nhau, quy trình onboarding, đăng ký, checkout thanh toán, hoặc quy trình làm thủ tục hành chính.
* **Nguyên tắc cốt lõi:**
  * Chia nhỏ một khối công việc đồ sộ thành các bước nhỏ (Chunking - Miller's Law).
  * Hiển thị thanh tiến trình trực quan (Progress Tracker) cho biết: *Đang ở đâu, đã làm được gì, còn bao nhiêu bước nữa*.
  * Cho phép lưu nháp tự động và quay lại các bước trước mà không mất dữ liệu đã điền.
* **Chống chỉ định:** Không áp dụng cho chuyên gia cần nhập liệu với tốc độ cao hoặc các tác vụ làm hàng ngày.

---

## 2. MẪU TRUNG TÂM & NAN HOA (HUB-AND-SPOKE / MASTER-DETAIL)
* **Bối cảnh phù hợp:** Quản lý danh sách, duyệt hồ sơ, xử lý đơn hàng, điều tra sự cố kỹ thuật, dashboard quản trị.
* **Nguyên tắc cốt lõi:**
  * **Hub (Màn hình chính/Danh sách):** Cung cấp bức tranh toàn cảnh (Overview), trạng thái của từng đối tượng, bộ lọc thông minh (Facets/Filters).
  * **Spoke (Chi tiết/Tác vụ xử lý):** Đi sâu vào xem hoặc xử lý từng mục cụ thể. Sau khi xử lý xong, có lối tắt trực tiếp sang mục kế tiếp (ví dụ: *Lưu & Chuyển sang đơn tiếp theo*) mà không bắt người dùng phải lùi về Hub rồi lại nhấp vào Spoke.

---

## 3. MẪU THÔNG TIN LŨY TIẾN (PROGRESSIVE DISCLOSURE)
* **Bối cảnh phù hợp:** Biểu mẫu nâng cao, cài đặt cấu hình, báo cáo phân tích, tài liệu hướng dẫn.
* **Nguyên tắc cốt lõi:**
  * Mặc định chỉ hiển thị 20% thông tin/trường dữ liệu quan trọng nhất (áp dụng cho 80% trường hợp thông thường).
  * Ẩn các tính năng chuyên sâu sau các nút mở rộng ("Cài đặt nâng cao", "Thêm tùy chọn lọc") để tránh gây hoảng loạn nhận thức cho người dùng mới.

---

## 4. MẪU HOÀN TÁC TRƯỚC - THAY VÌ HỎI XÁC NHẬN (UNDO-FIRST PATTERN)
* **Bối cảnh phù hợp:** Hành động xóa, lưu trữ, di chuyển, gửi tin nhắn, thay đổi cấu hình trạng thái.
* **Nguyên tắc cốt lõi:**
  * Thay vì bắt người dùng phải bấm "OK / Xác nhận" trong một modal popup gây đứt gãy luồng cảm xúc (modal interruption), hệ thống thực thi ngay lập tức và hiển thị một thanh thông báo kèm nút **"HOÀN TÁC (UNDO)"** trong 5–10 giây.
  * *Tác động:* Loại bỏ 100% cảm giác khó chịu do bị ngắt quãng, đồng thời giải phóng người dùng khỏi chứng mỏi mệt vì bấm xác nhận (Confirmation Fatigue).
* **Ngoại lệ:** Chỉ dùng modal xác nhận với các thao tác vĩnh viễn, không thể đảo ngược và có rủi ro nghiêm trọng (như xóa tài khoản, hủy hợp đồng, format ổ đĩa).

---

## 5. MẪU ĐI TẮT CHO CHUYÊN GIA (EXPERT ACCELERATOR / SHUNTING)
* **Bối cảnh phù hợp:** Nhân viên nhập liệu kế toán, lập trình viên, trader tài chính, y bác sĩ trực cấp cứu.
* **Nguyên tắc cốt lõi:**
  * Cung cấp toàn bộ phím tắt (Keyboard shortcuts / Command Palette `Cmd+K`), thao tác hàng loạt (Bulk actions), và khả năng bỏ qua các bước trung gian (Shunting - theo Thang quyết định Rasmussen).
  * Hệ thống cho phép người dùng chuyên gia điều khiển bằng phản xạ cơ bắp (Skill-based behavior) mà không bị kẹt trong giao diện trực quan chậm chạp.

---

## 6. MẪU CỘNG TÁC NGƯỜI - AI (HUMAN-AGENT COLLABORATIVE FLOW)
* **Bối cảnh phù hợp:** Ứng dụng tích hợp trợ lý AI, quy trình tự động hóa có con người phê duyệt (Human-in-the-loop).
* **Nguyên tắc cốt lõi:**
  * **AI đề xuất, Con người quyết định (Propose & Confirm):** AI trình bày kết quả dự thảo kèm bằng chứng/nguồn đối chiếu.
  * **Minh bạch trạng thái suy luận:** Hiển thị rõ AI đang làm gì (tránh "hộp đen" im lặng quá 2 giây).
  * **Kiểm soát linh hoạt:** Người dùng có thể chỉnh sửa trực tiếp (inline edit) vào câu trả lời hoặc output của AI bất kỳ lúc nào.
