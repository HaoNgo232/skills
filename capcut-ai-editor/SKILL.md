---
name: capcut-ai-editor
description: Professional AI Video Editor for CapCut / JianYing. Automates the full video editing workflow from raw footage to a ready-to-render CapCut project, including silence removal, retake detection, subtitle generation (via Gemini audio or local Whisper), zoom/Ken-Burns motion, sound design (BGM/SFX), and multi-track draft generation. Trigger this skill whenever the user wants to edit raw video, automate CapCut/JianYing, create video drafts, cut video pauses/stutters, add subtitles, or asks for AI video editing assistance in English or Vietnamese (edit video, dựng video, cắt video thô, capcut, jianying, làm phụ đề, lọc vấp).
---

# CapCut AI Editor

Skill biến AI thành trợ lý Video Editor chuyên nghiệp, tự động chuyển hóa file video thô thành một dự án CapCut hoàn chỉnh với đầy đủ các track: cắt thô, phụ đề, âm thanh và hiệu ứng chuyển động.

> **Gặp lỗi môi trường hoặc cần kiểm tra phần cứng?** 
> Xem ngay tài liệu tham chiếu chi tiết tại: [setup-and-troubleshooting.md](references/setup-and-troubleshooting.md)

---

## 1. Quy trình Dựng Video Thô Chuẩn (5 Bước)

Khi nhận file video thô từ người dùng (ví dụ: `raw_video.mp4`), AI thực hiện theo 5 bước tuần tự:

```
[Video thô] ──► 1. Phân tích âm thanh ──► 2. Lọc khoảng lặng & Nói vấp
                                                   │
[Dự án CapCut] ◄── 5. Ghi vào CapCut ◄── 4. SFX & Zoom ◄── 3. Tạo phụ đề
```

---

### Bước 1: Khởi tạo Dự án & Lựa chọn Engine Âm thanh
1. Tạo một dự án CapCut mới bằng lệnh:
   ```bash
   npx capcut-cli quickstart <Project_Name> --video "<path_to_raw_video.mp4>"
   ```
2. Xác định phương án xử lý âm thanh:
   - **Ưu tiên 1 (Thông minh nhất - Khuyên dùng):** Trích xuất audio nhanh bằng FFmpeg:
     ```bash
     ffmpeg -i "<raw_video.mp4>" -vn -ac 1 -ar 16000 -b:a 64k "temp_audio.mp3"
     ```
     Đọc file `temp_audio.mp3` vào mô hình (như Gemini) để phân tích nội dung, cảm xúc, lọc vấp và lấy mốc thời gian (timestamp).
   - **Ưu tiên 2 (Offline / Local):** Dùng `faster-whisper` hoặc Whisper local theo hướng dẫn trong [setup-and-troubleshooting.md](references/setup-and-troubleshooting.md).

---

### Bước 2: Lọc Khoảng lặng (Silence) & Cắt Đoạn Nói Vấp (Retakes)
1. **Phát hiện và cắt khoảng lặng chết:**
   ```bash
   npx capcut-cli detect-silence "<path_to_raw_video.mp4>"
   ```
   Lệnh này quét sóng âm thanh và xuất ra danh sách các phân đoạn cần giữ lại (keep segments).
2. **Loại bỏ các lần quay bị vấp / lặp lại (Retakes):**
   ```bash
   npx capcut-cli detect-retakes <Project_Name> --window 30 --similarity 0.8
   ```
   Nếu người nói thử lại một câu nhiều lần, công cụ sẽ tự động giữ lại lần nói sau cùng trôi chảy nhất.

---

### Bước 3: Tạo Phụ đề Động (Captions)
1. **Trường hợp dùng Whisper:**
   ```bash
   npx capcut-cli caption <Project_Name> --audio "temp_audio.mp3"
   ```
2. **Trường hợp nhận kết quả SRT từ AI / Script:**
   ```bash
   npx capcut-cli import-srt <Project_Name> "subtitles.srt"
   ```

---

### Bước 4: Tạo Nhịp điệu (Motion / Zoom) & Thiết kế Âm thanh (SFX / BGM)
1. **Thêm chuyển động phóng to/thu nhỏ (Ken Burns / Dynamic Zoom):**
   Gắn hiệu ứng chuyển động vào các phân đoạn điểm nhấn để tránh khung hình bị tĩnh:
   ```bash
   # Gắn hoạt ảnh zoom nhẹ vào segment video/ảnh cụ thể
   npx capcut-cli image-anim <Project_Name> <segment_id> --intro zoom-in

   # Hoặc thêm hiệu ứng chuyển động chữ cho subtitle:
   npx capcut-cli text-anim <Project_Name> <text_segment_id> --intro pop-up
   ```
2. **Chèn hiệu ứng âm thanh (SFX) & Scene Effects:**
   Chèn hiệu ứng âm thanh hoặc hiệu ứng hình ảnh (tra cứu slug bằng `npx capcut-cli enums --audio-effects` hoặc `--scene-effects`):
   ```bash
   npx capcut-cli add-sfx <Project_Name> synth <start_seconds> <duration_seconds>
   npx capcut-cli add-effect <Project_Name> tv-lines <start_seconds> <duration_seconds>
   ```
3. **Thêm nhạc nền (BGM) và làm mờ âm thanh (Fade):**
   ```bash
   npx capcut-cli audio-fade <Project_Name> <audio_segment_id> --in 1.0 --fade-out 2.0
   ```

---

### Bước 5: Kiểm tra & Đồng bộ vào CapCut Desktop
1. Chạy lệnh kiểm tra cấu trúc timeline:
   ```bash
   npx capcut-cli timeline <Project_Name> -H
   ```
2. Thông báo cho người dùng mở ứng dụng **CapCut Desktop**. Dự án `<Project_Name>` đã hiển thị ngay trên màn hình chính, người dùng chỉ cần mở lên, xem lướt qua để duyệt lần cuối và bấm nút **Export**.

---

## 2. Các Lệnh Tra cứu Nhanh Thường Dùng

| Nhu cầu thao tác | Lệnh thực thi |
| :--- | :--- |
| **Xem TOÀN BỘ trợ giúp & danh sách lệnh CLI** | `npx capcut-cli --help` (hoặc `capcut --help`) |
| **Xem chi tiết tham số của 1 lệnh cụ thể** | `npx capcut-cli <command> --help` |
| **Xuất toàn bộ schema/đặc tả lệnh dạng JSON cho AI** | `npx capcut-cli describe` |
| **Xem tổng quan dự án** | `npx capcut-cli info <project> -H` |
| **Liệt kê các track trong timeline** | `npx capcut-cli tracks <project> -H` |
| **Xem danh sách hiệu ứng có sẵn** | `npx capcut-cli enums --transitions -H` hoặc `--scene-effects` |
| **Chẩn đoán an toàn file dự án** | `npx capcut-cli diagnose <project> -H` |
| **Xóa phông xanh (Chroma key)** | `npx capcut-cli chroma <project> <segment_id> --color "#00FF00"` |
| **Tách nền thông minh (Smart matting)** | `npx capcut-cli matting <project> <segment_id>` |

