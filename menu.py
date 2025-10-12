import pygame
import random
import sys
from constants import asset_path
from background import ScrollingBackground

# -------------------------
# CẤU HÌNH NHÓM & KEY HÀM
# -------------------------
algorithm_groups = {
    "Tìm kiếm không thông tin": [
        ("BFS", "bfs"),
        ("DFS", "dfs"),
        ("IDS", "ids"),
    ],
    "Tìm kiếm có thông tin": [
        ("Greedy", "greedy"),
        ("A*", "astar"),
        ("UCS", "ucs"),
    ],
    "Tìm kiếm cục bộ": [
        ("Hill Climbing", "hillclimbing"),   
        ("Simulated Annealing", "sa"),         
        ("Genetic", "genetic"),
    ],
    "Tìm kiếm môi trường phức tạp": [
        ("AND-OR", "and_or"),             
        ("Online DFS", "online"),          
        ("POS", "pos"),
    ],
    "Tìm kiếm môi trường ràng buộc": [
        ("Backtracking", "backtracking"),
        ("Forward Checking", "forwardchecking"),
        ("AC-3", "ac3"),
    ],
    "Tìm kiếm môi trường đối kháng": [
        ("Minimax", "minimax"),
        ("Alpha-Beta", "alphabeta"),
        ("Minimax-Limited", "minimax_limited"),
    ],
}

# -------------------------
# HELPERS
# -------------------------
def draw_background(screen, bg, screen_w, screen_h):
    if bg:
        bg.draw(screen)
        overlay = pygame.Surface((screen_w, screen_h))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
    else:
        screen.fill((30, 30, 40))


def load_pixeboy_font(size):
    """Tải font PixelBoy (Determination Sans)"""
    try:
        return pygame.font.Font(asset_path("font/SVN-Determination Sans.otf"), int(size))
    except Exception:
        # Fallback sang font mặc định nếu lỗi
        return pygame.font.SysFont("Segoe UI", int(size))


def _draw_button(screen, font, text, rect, base_color, hover_color, radius=12):
    mouse_pos = pygame.mouse.get_pos()
    is_hover = rect.collidepoint(mouse_pos)
    color = hover_color if is_hover else base_color
    pygame.draw.rect(screen, color, rect, border_radius=radius)

    # Tự xuống dòng khi text dài
    max_width = rect.w - 20
    words = text.split()
    lines, current_line = [], ""
    for word in words:
        test_line = (current_line + " " + word).strip()
        label = font.render(test_line, False, (255, 255, 255))
        if label.get_width() <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)

    total_height = len(lines) * font.get_height()
    start_y = rect.y + (rect.h - total_height) // 2
    for line in lines:
        label = font.render(line, False, (255, 255, 255))
        label_rect = label.get_rect(centerx=rect.centerx, y=start_y)
        screen.blit(label, label_rect)
        start_y += font.get_height()

    return is_hover


# -------------------------
# MENU CON – chọn thuật toán trong nhóm
# -------------------------
def choose_sub_menu(group_name):
    screen_w, screen_h = 800, 600
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption(group_name)

    pygame.font.init()
    button_font = load_pixeboy_font(24)
    clock = pygame.time.Clock()

    try:
        bg = ScrollingBackground(asset_path("background.png"), 600, speed=1)
    except Exception:
        bg = None

    algos = algorithm_groups.get(group_name, [])
    BUTTON_W, BUTTON_H = 360, 60
    GAP_Y = 18

    # 👉 Tính toán để căn giữa toàn bộ cụm nút (không +80 như trước)
    total_height = len(algos) * (BUTTON_H + GAP_Y) - GAP_Y
    start_y = (screen_h - total_height) // 2 + 40  # chừa không gian cho tiêu đề
    start_x = (screen_w - BUTTON_W) // 2

    # 👉 Bảng màu cho từng nút (tự động luân phiên)
    colors = [
        ((70, 130, 180), (100, 160, 220)),  # xanh dương
        ((34, 139, 34), (60, 179, 60)),     # xanh lá
        ((218, 165, 32), (255, 215, 0)),    # vàng
        ((138, 43, 226), (160, 82, 255)),   # tím
        ((255, 140, 0), (255, 165, 0)),     # cam
        ((178, 34, 34), (220, 50, 50))      # đỏ
    ]

    while True:
        draw_background(screen, bg, screen_w, screen_h)

        # Tiêu đề
        title_text = group_name.upper()
        title_font_size = 48 if len(title_text) <= 18 else (42 if len(title_text) <= 25 else 36)
        title_font = load_pixeboy_font(title_font_size)
        title = title_font.render(title_text, True, (255, 215, 0))
        title_rect = title.get_rect(center=(screen_w // 2, 90))
        screen.blit(title, title_rect)

        buttons = []
        for i, (label, key) in enumerate(algos):
            rect = pygame.Rect(start_x, start_y + i * (BUTTON_H + GAP_Y), BUTTON_W, BUTTON_H)
            base_color, hover_color = colors[i % len(colors)]
            _draw_button(screen, button_font, label, rect, base_color, hover_color)
            buttons.append((rect, key))

        # Nút Back — đặt dưới cùng, cách cụm chính 50px
        back_rect = pygame.Rect(start_x, start_y + total_height + 50, BUTTON_W, BUTTON_H)
        _draw_button(screen, button_font, "BACK", back_rect, (105, 105, 105), (169, 169, 169))

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, key in buttons:
                    if rect.collidepoint(event.pos):
                        return key
                if back_rect.collidepoint(event.pos):
                    return "back"


# -------------------------
# MENU CHÍNH – chọn nhóm thuật toán
# -------------------------
def choose_mode_menu():
    screen_w, screen_h = 800, 600
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("Chọn nhóm thuật toán")

    pygame.font.init()
    title_font = load_pixeboy_font(48)
    button_font = load_pixeboy_font(22)
    clock = pygame.time.Clock()

    try:
        bg = ScrollingBackground(asset_path("background.png"), 600, speed=1)
    except Exception:
        bg = None

    groups = list(algorithm_groups.keys())
    colors = [
        ((70,130,180),(100,160,220)),
        ((34,139,34),(60,179,60)),
        ((218,165,32),(255,215,0)),
        ((138,43,226),(160,82,255)),
        ((255,140,0),(255,165,0)),
        ((178,34,34),(220,50,50))
    ]

    # Kích thước và bố cục
    BUTTON_W, BUTTON_H = 360, 65
    GAP_X, GAP_Y = 30, 25
    cols = 2
    rows = (len(groups) + 1) // 2  # 6 nhóm -> 3 hàng
    total_height = rows * BUTTON_H + (rows - 1) * GAP_Y

    # Căn giữa theo chiều dọc
    start_y = (screen_h - total_height) // 2 + 40
    start_x = (screen_w - (cols * BUTTON_W + (cols - 1) * GAP_X)) // 2

    while True:
        draw_background(screen, bg, screen_w, screen_h)

        # Tiêu đề
        title = title_font.render("ALGORITHMS GROUP", True, (255, 215, 0))
        screen.blit(title, (screen_w // 2 - title.get_width() // 2, 60))

        buttons = []
        for i, name in enumerate(groups):
            row, col = i // cols, i % cols
            rect = pygame.Rect(start_x + col * (BUTTON_W + GAP_X),
                               start_y + row * (BUTTON_H + GAP_Y),
                               BUTTON_W, BUTTON_H)
            base_color, hover_color = colors[i % len(colors)]
            _draw_button(screen, button_font, name, rect, base_color, hover_color)
            buttons.append((rect, name))

        # Nút Back ở cuối, cách hàng cuối cùng 40px
        back_rect = pygame.Rect((screen_w - BUTTON_W)//2,
                                start_y + total_height + 40,
                                BUTTON_W, BUTTON_H)
        _draw_button(screen, button_font, "BACK", back_rect, (105,105,105), (169,169,169))

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, name in buttons:
                    if rect.collidepoint(event.pos):
                        sub_choice = choose_sub_menu(name)
                        if sub_choice == "back":
                            break
                        return sub_choice
                if back_rect.collidepoint(event.pos):
                    return "back"


# -------------------------
# Helper: tải module thuật toán
# -------------------------
def _load_alg_module():
    try:
        import algorithms as algmod
        return algmod
    except Exception:
        return None


def run_algorithm_by_key(alg_key, start, goal, maze):
    algmod = _load_alg_module()
    func = None
    if algmod and hasattr(algmod, alg_key):
        func = getattr(algmod, alg_key)
    else:
        g = globals()
        if alg_key in g and callable(g[alg_key]):
            func = g[alg_key]
        else:
            mainmod = sys.modules.get("__main__")
            if mainmod and hasattr(mainmod, alg_key):
                func = getattr(mainmod, alg_key)

    if func is None:
        raise RuntimeError(f"Hàm thuật toán '{alg_key}' không tìm thấy.")
    return func(start, goal, maze)


# -------------------------
# MENU CHÍNH GAME
# -------------------------
def main_menu():
    pygame.init()
    screen_w, screen_h = 800, 600
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("Maze Hunter - Menu")

    title_font = load_pixeboy_font(72)
    button_font = load_pixeboy_font(28)
    clock = pygame.time.Clock()

    try:
        bg = ScrollingBackground(asset_path("background.png"), 600, speed=1)
    except Exception:
        bg = None

    BUTTON_W, BUTTON_H = 300, 64
    GAP = 90
    start_y = 220
    start_x = (screen_w - BUTTON_W)//2

    while True:
        draw_background(screen, bg, screen_w, screen_h)
        title = title_font.render("Maze Hunter", True, (255, 215, 0))
        screen.blit(title, (screen_w//2 - title.get_width()//2, 80))

        random_rect = pygame.Rect(start_x, start_y, BUTTON_W, BUTTON_H)
        choose_rect = pygame.Rect(start_x, start_y + GAP, BUTTON_W, BUTTON_H)
        exit_rect   = pygame.Rect(start_x, start_y + 2*GAP, BUTTON_W, BUTTON_H)

        _draw_button(screen, button_font, "PLAY RANDOM", random_rect, (70,130,180),(100,160,220))
        _draw_button(screen, button_font, "CHOOSE MODE", choose_rect, (34,139,34),(60,179,60))
        _draw_button(screen, button_font, "EXIT", exit_rect, (178,34,34),(220,50,50))

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if random_rect.collidepoint(event.pos):
                    all_keys = [key for group in algorithm_groups.values() for _, key in group]
                    return random.choice(all_keys)
                elif choose_rect.collidepoint(event.pos):
                    choice = choose_mode_menu()
                    if choice in (None, "back"):
                        continue
                    return choice
                elif exit_rect.collidepoint(event.pos):
                    return "exit"
