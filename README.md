# 🧠 Chạy ngay đi - Maze Hunter

## 👑 Giới Thiệu Dự Án
**Maze Hunter** là một trò chơi học thuật được xây dựng bằng **Python (Pygame)**, nơi người chơi phải sinh tồn trong mê cung và thu thập chìa khoá để vượt qua màn.  
Điểm đặc biệt nằm ở **AI Hunter** — một đối thủ được điều khiển bằng các **thuật toán Trí tuệ Nhân tạo (AI)**, có khả năng **tự tìm đường và truy đuổi người chơi thông minh**.

### 🎯 Mục tiêu chính của dự án:
- Giúp người học trực quan hoá cách hoạt động của các thuật toán tìm kiếm và heuristic.  
- Kết hợp giữa AI, trò chơi, và giáo dục, tạo trải nghiệm học tập sinh động.

---

## 🎮 Gameplay

### 🧍‍♂️ Vai trò người chơi
- Di chuyển nhân vật trong mê cung để nhặt **xu 💰** và **chìa khoá 🔑**.  
- Khi đi vào vị trí chìa khoá, một **câu hỏi tiếng Anh** hiện lên.  
  - ✅ Trả lời đúng → Nhận chìa khoá.  
  - ❌ Trả lời sai → Mất cơ hội lấy chìa.  
- Khi có đủ **3 chìa khoá**, bạn có thể mở **rương báu 🗝️** để qua màn.

### 🤖 Vai trò AI Hunter
- **Hunter** sử dụng các thuật toán AI như:  
  `BFS`, `DFS`, `A*`, `UCS`, `Hill Climbing`, `Genetic Algorithm`, v.v.  
- Tự động tìm đường ngắn nhất hoặc tối ưu nhất để bắt người chơi.  
- Khi Hunter chạm vào bạn → **-1 mạng.**

### ❤️ Mạng sống & Tiền xu
- Người chơi bắt đầu với **5 mạng**.  
- Mỗi lần bị Hunter bắt: **-1 mạng**.  
- Mất hết 5 mạng → **Game Over.**  
- Thu thập **10 xu** có thể **bỏ qua 1 câu hỏi tiếng Anh** nếu không biết đáp án.

---

## ✨ Tính Năng Nổi Bật
- 🎨 **Giao diện trực quan**: được thiết kế bằng Pygame, mượt mà và thân thiện.  
- 🧠 **AI truy đuổi thông minh**: mỗi thuật toán mang phong cách truy tìm khác nhau.  
- 🧩 **Minh hoạ sinh động**: giúp người chơi hiểu cách hoạt động của từng giải thuật.  
- 🔊 **Âm thanh & hiệu ứng sống động**: tạo cảm giác chân thật và cuốn hút.  
- ⚙️ **Tùy chỉnh dễ dàng**: thay đổi tốc độ, bản đồ, chủ đề (theme) hoặc chế độ AI.

---

## 🧩 Các Thuật Toán AI Được Tích Hợp

| Nhóm thuật toán | Mô tả |
|------------------|-------|
| **Tìm kiếm mù (Uninformed Search)** | BFS, DFS, UCS, DLS, IDS |
| **Tìm kiếm có thông tin (Informed Search)** | Greedy Search, A* |
| **Tối ưu cục bộ / Metaheuristic** | Hill Climbing, Simulated Annealing, Genetic Algorithm |
| **CSP / Ràng buộc** | Backtracking, Forward Checking, AC-3 |
| **Tùy chỉnh** | Partial Search, And-Or Search, Belief Space Search |

> Mỗi thuật toán mang lại một hành vi khác nhau của Hunter — từ truy đuổi theo đường ngắn nhất (A*) đến leo đồi, di truyền, hoặc tìm kiếm ngẫu nhiên.

---

## 🗺️ Cấu Trúc Dự Án

```bash
📁 meCungCuoiKy/
├── 📁 __pycache__/            # Cache Python tự động sinh
├── 📁 assets/                 # Tài nguyên trò chơi (ảnh, âm thanh, sprite,...)
│
├── __main__.py                # Điểm khởi chạy chính của game
├── background.py              # Vẽ nền và hiệu ứng khung cảnh trong menu.
├── constants.py               # Chứa hằng số, kích thước, tốc độ, màu sắc, theme,...
├── enemy.py                   # Xử lý AI Hunter (điều khiển kẻ đuổi theo)
├── game.py                    # Logic chính: vòng lặp game, xử lý sự kiện, cập nhật màn chơi
├── menu.py                    # Menu chính: chọn chế độ, chọn thuật toán AI, thoát,...
├── pathfinding.py             # Tập hợp các thuật toán AI (BFS, DFS, A*, UCS, Hill Climbing, v.v.)
├── player.py                  # Xử lý hành vi và hoạt ảnh của người chơi
├── quiz.py                    # Câu hỏi tiếng Anh & cơ chế kiểm tra đáp án khi lấy chìa khoá
├── utils.py                   # Hàm hỗ trợ: vẽ, xử lý giao diện, âm thanh, ảnh,...
├── visualizer.py              # Trực quan hoá đường đi của AI Hunter trên bản đồ
└── README.md                  # Tài liệu mô tả dự án
```

---

## 🕹️ Cách Chơi

| Phím | Chức năng |
|------|------------|
| ⬆️ ⬇️ ⬅️ ➡️ | Di chuyển nhân vật |
| **Nhấn nút Pause** | Tạm dừng game |
| **Nhấn nút Continue** | Tiếp tục chơi |
| **Nhấn nút Exit** | Thoát trò chơi |
| **Chọn số tương ứng với đáp án (1-4)** | Trả lời câu hỏi |

---

## ⚙️ Cách Cài Đặt & Chạy

### 🔧 Yêu cầu
- Python ≥ 3.8  
- Thư viện: `pygame`, `tkinter`, `random`, `time`, `os`

### 🚀 Chạy game:
```bash
git clone https://github.com/teehihi/meCungCuoiKy.git
cd meCungCuoiKy
python -m __main__
```

---

## 📚 Mục Tiêu Học Tập
Dự án này hướng tới việc:
- Trực quan hoá các thuật toán tìm kiếm & tối ưu trong AI.  
- Củng cố kiến thức về Python, Pygame, heuristic search, CSP.  
- Giúp sinh viên hoặc người học trải nghiệm lập trình AI trong môi trường tương tác.

---

## 💡 Gợi Ý Mở Rộng
- Thêm nhiều bản đồ (maze) hoặc độ khó khác nhau.  
- Cho phép người chơi chọn thuật toán AI để “đấu trí” với Hunter.  
- Tích hợp chế độ nhiều người chơi hoặc thi đấu **AI vs AI**.

---

## 🎬 Demo
### 🟨 Menu của Maze Hunter
<table align="center">
  <tr>
    <td align="center">
      <img src="https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcTZ0ZjdtZ3FpMW5lN2J6bDUxOGtrdXd5YXMyaGF3Zms4NDc3OWdoZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/h7HDVPzJgUBZ3UHAfA/giphy.gif" width="320"><br>
      <strong>🏠 Menu Chính</strong>
    </td>
    <td align="center">
      <img src="https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExeWVqbjdpN3pzN3Y1NzNicXZjZTA3cHNvZDcxMTI4amRtcmFlNGVmNSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/quSGsK4tryxNRz9GKS/giphy.gif" width="320"><br>
      <strong>🎮 Menu Chọn Chế Độ</strong>
    </td>
    <td align="center">
      <img src="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ2RoajJ6cGNuZzA4NnV3MTNzNTNkNzYyMmJoYXBodG9jaTRkMG5kMSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/1V9czVH90fJ3WwSU3A/giphy.gif" width="320"><br>
      <strong>⚙️ Màn Hình Loading</strong>
    </td>
  </tr>
</table>

### 🟪 Giao diện chính
<table align="center">
  <tr>
    <td align="center">
      <img src="https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExdTFicW95dnVvcHVxbmc1M204dmVlZDM5emJsN2R0a3FiNzdzOW1xaSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/RTYkOCeh3CXl39f5MB/giphy.gif" width="320"><br>
      <strong>🎮 Game Play Chính</strong>
    </td>
    <td align="center">
      <img src="https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExY3Uxdng3bm85ZDhkeWduMGZrMDJyczhrc3B3NWV4NDZ0OWNuYmx4cCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/AoliG8SixDEgCZe3Hi/giphy.gif" width="320"><br>
      <strong>💥 Va Chạm Khi Chưa Hết Máu</strong>
    </td>
    <td align="center">
      <img src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExYW9jMjMwano3MGVpZ21vdmg5cG1xNno3dDlnMzl1cDUwcGhjdXRyMCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ZhHdVdzx7da7jCVDcN/giphy.gif" width="320"><br>
      <strong>☠️ Hết Máu & Thua</strong>
    </td>
  </tr>
</table>

### 🟧 Giao diện câu hỏi
<table align="center">
  <tr>
    <td align="center">
      <img src="https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExa2JoMmNvcjdnamdidzlzeXZwbnRsb216MXZoa2ZncDNxYTYxdjRxMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/klFNZ0XhJcO8Rk33rz/giphy.gif" width="320"><br>
      <strong>❌ Trả Lời Sai</strong>
    </td>
    <td align="center">
      <img src="https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExamozbTZrZzNob2pyY2VkbnZ5a28yZ2x5MTh6MXRpaDNlY3A1d3FzYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/r5CpASYBt3VdaFHhLM/giphy.gif" width="320"><br>
      <strong>✅ Trả Lời Đúng</strong>
    </td>
    <td align="center">
      <img src="https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmh0dXh4MGV6Z2Q3ZjgzdnRpNDRyaDk3N2w2djc4eHg0cGE4YmlnNCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ceKtX9GfLpP06qqT3V/giphy.gif" width="320"><br>
      <strong>💰 Đủ Xu Để Bỏ Qua Câu Hỏi</strong>
    </td>
  </tr>
</table>

### 🟩 Điều kiện qua màn
<table align="center">
  <tr>
    <td align="center">
      <img src="https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExN2hiNXdiOGdsbXd3aHUyOHgwa2tpcTZ0OHRlNWs1ODA0M2p0dTc4bSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/lM8g9I0z6nSxZUmW1a/giphy.gif" width="320"><br>
      <strong>🔒 Chạm Rương Khi Chưa Đủ Chìa</strong>
    </td>
    <td align="center">
      <img src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExZGRtZnY1Zmp3ZjFqaG13cWc2dHZydnp5aHNwN256ZXl4ZjZueHcxNyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/XUfVeOK1ChAWaH7zob/giphy.gif" width="320"><br>
      <strong>🏆 Đủ Chìa Và Mở Rương Thành Công</strong>
    </td>
  </tr>
</table>

### 🟦 Minh hoạ thuật toán
<table align="center">
  <tr>
    <td align="center">
      <img src="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExcDVoamttc2JzZjhteWI2NDEwbnZ2NnJvaTE1MHI2aXN4b2NocGE2dSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/1WuKxMJwcY1Gecpo08/giphy.gif" width="320"><br>
      <strong>🔍 Minh Hoạ Thuật Toán AI</strong>
    </td>
  </tr>
</table>

---

## 🧑‍💻 Tác Giả
- **Tee** – Phát triển & thiết kế game  
- **Pvhau**  
- **NmTriet**  

🔗 **Know more about Tee:** [linktr.ee/nkqt.tee](https://linktr.ee/nkqt.tee)
