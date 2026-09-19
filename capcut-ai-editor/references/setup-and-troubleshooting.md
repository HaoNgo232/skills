# Hướng dẫn Thiết lập Môi trường & Xử lý Lỗi (CapCut AI Editor)

Tài liệu này dành cho AI Agent hoặc người dùng khi cần kiểm tra, cài đặt môi trường, chẩn đoán phần cứng và khắc phục sự cố trong quá trình tự động hóa CapCut.

---

## 1. Kiểm tra Phần cứng & Lựa chọn Engine Âm thanh Phù hợp

Trước khi xử lý video, AI cần kiểm tra cấu hình máy tính để quyết định phương án bóc tách âm thanh / phụ đề tối ưu:

### Lệnh PowerShell kiểm tra phần cứng:
```powershell
# Kiểm tra CPU (Số nhân, số luồng)
Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors

# Kiểm tra tổng dung lượng RAM (GB)
[Math]::Round((Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum).Sum / 1GB, 1)

# Kiểm tra Card đồ họa rời (GPU NVIDIA / AMD)
Get-CimInstance Win32_VideoController | Select-Object Name, AdapterRAM
```

### Ma trận Đề xuất Engine Âm thanh (Audio / Transcription Engine Matrix):

| Cấu hình máy tính | Phương án đề xuất hàng đầu | Phương án dự phòng (Offline) | Ghi chú hiệu năng |
| :--- | :--- | :--- | :--- |
| **CPU-only (4-8 nhân, >= 8GB RAM)** *(Như Core i5/i7 gen 8-12, Ryzen 5/7)* | **Gemini Audio API** (Tách mp3 bằng FFmpeg gửi lên Gemini) | **faster-whisper** (Model `base` hoặc `small`) | Tận dụng AVX2/12 luồng, video 10 phút xử lý trong 40 - 90 giây. Không dùng `openai-whisper` vì nặng CPU. |
| **Máy yếu (CPU 2-4 nhân, RAM <= 8GB)** | **Gemini Audio API** | **whisper.cpp** (Model `tiny` hoặc `base`) | `whisper.cpp` viết bằng C thuần, chiếm dưới 300MB RAM, không làm đơ máy. |
| **Có GPU NVIDIA (VRAM >= 4GB)** | **faster-whisper** với `device="cuda"` | **Whisper Large-v3-Turbo** | Tốc độ siêu thanh: Video 10 phút xử lý trong 10 - 20 giây. |

---

## 2. Hướng dẫn Cài đặt Môi trường Chuẩn (Windows Setup)

### Bước 1: Kiểm tra các công cụ cơ sở
Chạy lệnh kiểm tra nhanh:
```powershell
node -v
python --version
ffmpeg -version
Test-Path "$env:LOCALAPPDATA\CapCut\User Data\Projects\com.lveditor.draft"
```

### Bước 2: Cài đặt các thành phần nếu còn thiếu
1. **FFmpeg** (Bắt buộc để trích xuất âm thanh và đo sóng âm):
   ```powershell
   winget install "Gyan.FFmpeg"
   ```
2. **CapCut CLI** (Gói lõi thao tác file dự án):
   ```powershell
   npm install -g capcut-cli
   ```
3. **Faster-Whisper (Cho CPU Intel/AMD):**
   ```powershell
   pip install faster-whisper
   ```
   *Lưu ý:* Nếu muốn dùng tính năng `capcut caption` trực tiếp từ CLI, cài đặt thêm bản nhẹ:
   ```powershell
   pip install openai-whisper
   ```

---

## 3. Kiểm tra Sức khỏe Hệ thống (Health Check)

Chạy lệnh kiểm tra môi trường của CapCut CLI:
```powershell
npx capcut-cli doctor -H
```
* **Node & FFmpeg:** Bắt buộc phải hiện `ok`.
* **draft-dir:** Phải tìm thấy đường dẫn `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft`.
* **Whisper:** Nếu báo `warn`, chuyển sang dùng script `faster-whisper` hoặc tách audio gửi Gemini.

---

## 4. Bảng Tra cứu & Xử lý Lỗi Phổ biến (Troubleshooting Guide)

### Lỗi 1: `Draft path not found` hoặc `Projects directory does not exist`
* **Nguyên nhân:** Người dùng mới cài CapCut Desktop nhưng chưa từng mở ứng dụng hoặc chưa từng bấm "Create project" lần nào, nên Windows chưa sinh thư mục dữ liệu.
* **Cách khắc phục:** 
  1. Hướng dẫn người dùng mở CapCut Desktop lên.
  2. Bấm nút **"Create project"** (Tạo dự án mới) rồi tắt đi.
  3. Hoặc chạy lệnh PowerShell tự tạo thư mục:
     ```powershell
     New-Item -ItemType Directory -Force -Path "$env:LOCALAPPDATA\CapCut\User Data\Projects\com.lveditor.draft"
     ```

### Lỗi 2: Không đồng bộ tiếng Việt có dấu (Lỗi Font / Mojibake trong phụ đề)
* **Nguyên nhân:** File JSON lưu dưới định dạng ANSI hoặc encoding không phải UTF-8 chuẩn.
* **Cách khắc phục:** Khi tạo hoặc sửa phụ đề, luôn đảm bảo text được mã hóa chuẩn `utf-8`:
  ```python
  with open("subtitles.srt", "w", encoding="utf-8") as f:
      f.write(content)
  ```
  Trong CapCut, nên ưu tiên các font Unicode thông dụng hỗ trợ tiếng Việt tốt: *Arial, Be Vietnam Pro, Montserrat, Roboto*.

### Lỗi 3: Lỗi khi vừa mở CapCut Desktop vừa cho AI ghi đè file dự án
* **Nguyên nhân:** CapCut Desktop giữ khóa file (`file lock`) khi đang mở một project. Nếu AI ghi đè `draft_content.json` cùng lúc, CapCut có thể ghi đè lại dữ liệu cũ khi tắt.
* **Cách khắc phục:**
  - AI phải nhắc người dùng thoát ra màn hình chính của CapCut (Homepage) hoặc tắt app trước khi AI chạy lệnh ghi dự án.
  - Sau khi AI báo *"Hoàn tất"*, người dùng mới bấm mở dự án để thấy timeline mới.

### Lỗi 4: `whisper binary not found on PATH` khi chạy `capcut caption`
* **Nguyên nhân:** Máy chưa cài `openai-whisper` hoặc đường dẫn Scripts của Python chưa nằm trong biến môi trường PATH.
* **Cách khắc phục:**
  - Thêm thư mục Scripts của Python vào PATH: `C:\Users\<User>\AppData\Local\Programs\Python\Python312\Scripts`.
  - Hoặc dùng giải pháp thay thế: Cho Python chạy `faster-whisper` xuất ra file `.srt`, sau đó dùng lệnh:
    ```powershell
    npx capcut-cli import-srt <project_name> subtitles.srt
    ```
