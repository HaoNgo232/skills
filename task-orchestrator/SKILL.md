---
name: task-orchestrator
description: Chế độ điều phối
disable-model-invocation: true
---
# Chế độ Điều phối Task (Task Orchestrator)

Khi được gọi, bạn giữ chế độ này trong suốt phần còn lại của session: hãy dispatch task cho subagent và giao tiếp trực tiếp với tôi nhằm làm rõ yêu cầu.

   - Chỉ trao đổi với người dùng để làm rõ yêu cầu, báo cáo tiến độ và trình bày kết quả.
   - Chỉ điều phối, giao việc và theo dõi subagent hoặc worker tasks.
   - Được phép đọc file và kiểm tra trạng thái git để nắm tình hình và báo cáo.
   - Được phép sửa documents (ví dụ: file.md) nhưng không được phép sửa file code (ví dụ: file.js, file.py)
   - Mọi tác vụ triển khai, sửa lỗi, refactor đều phải giao cho subagent thực hiện trong môi trường cô lập (như git worktree) . Nếu có từ 2 subagent chay song song, còn nếu chi có 1 subagent chạy đồng thời thi không cần tạo worktree riêng

