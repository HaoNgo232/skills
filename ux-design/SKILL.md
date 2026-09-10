---
name: ux-design
description: >-
  Design and audit user workflows and interaction flows, in any domain.
  Use when: designing a new user flow or task flow (from scratch),
  auditing usability of an existing flow (heuristic evaluation,
  cognitive walkthrough), reviewing flow states and transitions,
  finding friction, confusion, or dark patterns in a user journey.
---

# UX Design & Interaction Flow Skill (`/ux-design`)

Thiết kế luồng tác vụ người dùng (user flow / task flow), kiến trúc tương tác và hành trình sử dụng cho **bất kỳ hệ thống nào** (phần mềm, ứng dụng di động, hệ thống doanh nghiệp B2B, thiết bị phần cứng/IoT, dịch vụ đời thực, hoặc tác tử AI/hội thoại). 

Mục tiêu cốt lõi: **Biến sự phức tạp thành trải nghiệm tự nhiên, thỏa mãn bản năng con người, loại bỏ triệt để ma sát nhận thức (Cognitive Friction) và tối ưu hóa sự hài lòng.**

---

## 1. Adaptive Context Engine (Ma trận thích ứng ngữ cảnh tự động)

Trước khi đề xuất bất kỳ giải pháp nào, Agent **bắt buộc** phải tự động định vị bài toán trên Ma trận 3 Trục Độc lập:

```
                      [Mức độ Rủi ro (Risk)]
                      Cao (High-Stakes)
                             ▲
                             │
                             │
                             │
                             │
 [Trình độ Người dùng]       ┼────────────────────────► [Phương tiện Tương tác]
 Novice / Casual             │                         Expert / Specialist
                             │
                             ▼
                      Thấp (Low-Stakes)
```

1. **Trục 1 — Trình độ & Nhận thức (User Expertise):**
   * *Novice / Casual (Người dùng vãng lai, phổ thông, ít dùng):* Ưu tiên tính trực quan tự giải thích (Self-descriptive), giảm thiểu lựa chọn (Hick's Law), chia nhỏ từng bước (Linear Wizard).
   * *Expert / Specialist (Chuyên gia, nhân viên vận hành hàng ngày):* Ưu tiên tốc độ, phím tắt (Accelerators/Hotkeys), mật độ dữ liệu cao, thao tác hàng loạt (Bulk), và các lối đi tắt (Shunting theo Thang quyết định Rasmussen).
2. **Trục 2 — Mức độ Rủi ro & Hậu quả Lỗi (Failure Consequence):**
   * *Thấp (Low-Stakes: Mua sắm, Mạng xã hội, Giải trí):* Ưu tiên khám phá tự do, mượt mà (Frictionless), hoàn tác nhanh (Undo-first thay vì hỏi xác nhận liên tục).
   * *Cao (High-Stakes: Tài chính, Y tế khẩn cấp, Hàng không, An toàn lao động):* Ưu tiên phòng ngừa lỗi triệt để, hiển thị minh bạch trạng thái hệ thống, xác nhận 2 lớp cho thao tác nguy hiểm, bảo tồn dữ liệu tuyệt đối.
3. **Trục 3 — Phương tiện Tương tác (Interaction Medium):**
   * *Màn hình số (GUI: Web, Mobile, Desktop)*
   * *Giao diện Hội thoại (CUI: Voice, AI Chat, Agent)*
   * *Phần cứng / Không gian Vật lý (Hardware, Nút bấm cơ học, IoT)*
   * *Hành trình Dịch vụ Con người (Service Design, Quy trình nghiệp vụ)*

---

## 2. Cognitive Bias Checklist (8 thiên kiến nhận thức cần loại trừ)

Agent tuyệt đối không được thiết kế theo tư duy máy móc/lập trình viên vô cảm. Bắt buộc tuân thủ nền tảng sinh học thần kinh và Cognitive Bias Checklist (8 thiên kiến nhận thức cần loại trừ) (tham khảo toàn văn nghiên cứu tại `references/cognitive-biases.md`):

1. **Tôn trọng Bản chất Sinh học Thần kinh:**
   * *Não bộ là Kẻ bủn xỉn nhận thức (Cognitive Miser - Fiske & Taylor 1984):* Não chỉ nặng 2% nhưng tiêu thụ 20% năng lượng cơ thể. Con người luôn vô thức chọn lối tắt (heuristics) để tiết kiệm calo. Mọi ma sát vô lý đều kích hoạt ức chế và chán nản.
   * *Nút thắt Bộ nhớ làm việc 4-Chunks (Nelson Cowan 2001):* Con người chỉ giữ được 3–5 chunks (trung bình 4) thông tin cùng lúc. Cấm bắt người dùng ghi nhớ dữ liệu từ bước trước sang bước sau.
   * *Mô hình 3 lớp của Alan Cooper:* Tuyệt đối không bê nguyên **Implementation Model** (cách code/database chạy) lên UI. Phải kiến tạo **Represented Model** ăn khớp 100% với **Mental Model** (mô hình tư duy tự nhiên) của con người.
2. **Triệt tiêu "Lời nguyền Tri thức" (Curse of Knowledge & False-Consensus):** Không dùng thuật ngữ nội bộ, mã lỗi backend (`UUID invalid`, `NullPointer`). Những gì hiển nhiên với kỹ sư là bí hiểm với người dùng.
3. **Rational Agent Fallacy (Ngụy biện người dùng duy lý):** Con người chỉ đọc quét 20-28% từ ngữ (chữ F của Nielsen), luôn vội vã và mệt mỏi. Phải thiết kế vị tha (*Forgiving UI*), phân định rõ giữa lỗi vô thức (*Slips* $\rightarrow$ Undo) và sai lầm nhận thức (*Mistakes*).
4. **Không rò rỉ Cấu trúc Cơ sở Dữ liệu (No Database Leakage / Leaky Abstractions):** Không ép người dùng điền theo thứ tự khóa ngoại (Foreign Keys), phân trang giới hạn `LIMIT/OFFSET`, hay bắt bấm "Lưu" thủ công vì nỗi lo commit ACID.
5. **Thu hẹp 2 Khoảng cách của Don Norman:**
   * *Gulf of Execution:* Affordances và Signifiers rõ ràng để người dùng biết ngay mình có thể làm gì.
   * *Gulf of Evaluation:* Phản hồi trạng thái tức thời dưới 100ms, không biến hệ thống thành "hộp đen câm nín".
6. **Bảo vệ Hệ tư duy Số 1 (Protect System 1 - Daniel Kahneman):** Tạo ra trạng thái Dễ dàng Nhận thức (*Cognitive Ease*). Không bắt người dùng dùng não phân tích (System 2) để tính nhẩm thuế phí hay giải mã icon vô nghĩa (*Mystery Meat Navigation*).
7. **Tránh Nghịch lý Lựa chọn (The Paradox of Choice - Barry Schwartz & Hick's Law):** Cung cấp *Progressive Disclosure* và *Opinionated Defaults* (thiết lập mặc định tối ưu sẵn cho 85% người dùng) thay vì nhồi nhét hàng tá nút bấm gây tê liệt quyết định.
8. **Alert Fatigue (Kiệt quệ cảnh báo) & Cry-Wolf Effect:** Cấm popup "Bạn có chắc không?" cho các thao tác thông thường. Áp dụng quy tắc **Undo-first** (cho phép thực thi ngay và hiển thị thanh Hoàn tác trong 5-10s).
9. **Cấm Bẫy Mất Dữ liệu (State Wipeout Prohibition):** Tự động lưu nháp (Autosave liên tục) khi người dùng lỡ bấm Back, Reload hoặc mất mạng tạm thời.

---

## 3. Flow Anatomy — 7 Elements of a User Flow (7 yếu tố cấu thành luồng trải nghiệm)

Mọi luồng tác vụ (user flow / task flow) được thiết kế ra phải làm rõ 7 yếu tố cấu thành:
1. **Actor & Context (Chủ thể & Ngữ cảnh):** Ai thao tác? Tâm lý ra sao? Thiết bị gì?
2. **Trigger & Pre-conditions (Cò kích hoạt & Điều kiện tiên quyết):** Sự kiện gì bắt đầu luồng? Cần chuẩn bị gì trước?
3. **Input / Intent Transmission (Hành vi truyền ý định):** Thao tác tối giản để người dùng đưa ý định vào hệ thống.
4. **Decision Points (Điểm rẽ nhánh):** Logic phân nhánh `If/Else` xử lý các tình huống khác nhau.
5. **System Feedback & State (Phản hồi & Trạng thái):** Trạng thái tức thời (`0.1s`, `1s`, `>10s`) đảm bảo người dùng luôn biết chuyện gì đang xảy ra.
6. **Error Boundaries & Fallbacks (Khả năng chịu lỗi & Lối thoát an toàn):** Đường lui an toàn khi phát sinh lỗi, luôn có nút Hủy/Quay lại/Hoàn tác.
7. **Exit & Post-conditions (Kết thúc & Chuyển trạng thái):** Xác nhận thành công và định hướng hành động tiếp theo (*Next Best Action*).

---

## 4. Dual Operational Modes (Hai chế độ vận hành)

Agent tự động nhận diện ngữ cảnh hoặc dựa trên yêu cầu của người dùng:

### From-Scratch Design Mode (Thiết kế mới từ đầu)
* Áp dụng khi người dùng yêu cầu thiết kế một tính năng mới, ứng dụng mới, quy trình mới.
* Các bước triển khai:
  1. Phân tích bối cảnh & Phân rã mục tiêu (Task Analysis).
  2. Xây dựng Sơ đồ luồng quyết định & flow states and transitions (trạng thái và bước chuyển trong luồng).
  3. Lắp ghép Flow Anatomy (7 yếu tố cấu thành luồng trải nghiệm) vào từng bước.
  4. Áp dụng Mẫu thiết kế tương ứng từ `references/workflow-patterns.md`.

### Existing-Flow Audit Mode (Kiểm toán & cải tiến luồng hiện có)
* Tự động kích hoạt khi người dùng cung cấp code, ảnh chụp giao diện, mô tả một luồng sẵn có kèm câu hỏi "audit", "đánh giá", "kiểm tra", "review", hoặc "tái thiết kế / redesign".
* **Hành động bắt buộc:** Không cần skill riêng — Agent tự động nạp và thực thi toàn bộ quy trình trong `references/ux-audit.md`:
  1. Chạy Cognitive Walkthrough Questions (4 câu hỏi kiểm chứng từng bước) và Heuristic Evaluation.
  2. Đối chiếu Cognitive Bias Checklist (8 thiên kiến nhận thức cần loại trừ) từ `references/cognitive-biases.md`.
  3. Phân loại lỗi theo Severity Rating (Critical / Major / Minor): 🔴 Critical, 🟡 Major, 🟢 Minor.
  4. Đề xuất giải pháp khắc phục cụ thể (Actionable Redesign Fix) cho từng lỗi.

---

## 5. Output Constraints (Quy tắc phản hồi)

Để câu trả lời vừa súc tích, vừa có giá trị thực thi cao nhất:

1. **Phản hồi Trực tiếp & Linh hoạt (Markdown):**
   * Trình bày trực tiếp, gãy gọn, không ép khuôn cứng nhắc, ngôn ngữ tự nhiên và nhân bản.
   * Sử dụng sơ đồ Mermaid khi cần trực quan hóa luồng tác vụ (user flow / task flow / flow states and transitions).
2. **Yêu cầu Bắt buộc Không thể Bỏ qua:**
   * **Đề xuất Giải pháp Cụ thể + Impact Đo lường được:** Bắt buộc phải chỉ rõ giải pháp giải quyết tận gốc vấn đề gì và đem lại tác động cụ thể nào (Ví dụ: giảm bao nhiêu % thao tác thừa, tiết kiệm bao nhiêu giây/phút thực hiện tác vụ, triệt tiêu rủi ro mất dữ liệu ra sao).
   * **Khi thực hiện Existing-Flow Audit Mode:** Bắt buộc xuất danh sách phát hiện theo Severity Rating (Critical / Major / Minor) kèm bảng tổng kết so sánh Trước (As-Is) vs Sau (To-Be) và cột Impact dự kiến ngay trong phản hồi Markdown.
