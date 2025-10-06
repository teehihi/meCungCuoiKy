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
        ("Hill Climbing", "hill_climbing"),
        ("Simulated Annealing", "simulated_annealing"),
        ("Genetic", "genetic"),
    ],
    "Tìm kiếm môi trường phức tạp": [
        ("AND-OR", "and_or_tree_search"),
        ("Online DFS", "online_dfs"),
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
    return pygame.font.Font(asset_path("font/Pixeboy.ttf"), int(size))

def _draw_button(screen, font, text, rect, base_color, hover_color, radius=12):
    mouse_pos = pygame.mouse.get_pos()
    is_hover = rect.collidepoint(mouse_pos)
    color = hover_color if is_hover else base_color
    pygame.draw.rect(screen, color, rect, border_radius=radius)

    # Giới hạn độ dài text: nếu vượt quá thì tự xuống dòng
    max_width = rect.w - 20
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = (current_line + " " + word).strip()
        label = font.render(test_line, False, (255, 255, 255))
        if label.get_width() <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)

    # Vẽ text căn giữa theo chiều dọc
    total_height = len(lines) * font.get_height()
    start_y = rect.y + (rect.h - total_height) // 2
    for line in lines:
        label = font.render(line, False, (255, 255, 255))  # False = tắt anti-alias
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
    button_font = pygame.font.SysFont("Segoe UI", 26)  
    clock = pygame.time.Clock()

    try:
        bg = ScrollingBackground(asset_path("background.png"), 600, speed=1)
    except Exception:
        bg = None

    algos = algorithm_groups.get(group_name, [])
    BUTTON_W, BUTTON_H = 360, 60
    GAP_Y = 18

    total_height = len(algos) * (BUTTON_H + GAP_Y)
    start_y = (screen_h - total_height) // 2 + 80
    start_x = (screen_w - BUTTON_W) // 2

    while True:
        draw_background(screen, bg, screen_w, screen_h)

        # Title vẫn dùng cơ chế cũ để tự điều chỉnh size
        title_text = group_name.upper()
        title_font_size = 48
        if len(title_text) > 25:
            title_font_size = 36
        elif len(title_text) > 18:
            title_font_size = 42
        title_font = pygame.font.SysFont("Segoe UI", title_font_size, bold=True)  # title dùng Segoe UI với size linh hoạt
        title = title_font.render(title_text, True, (255, 215, 0))
        screen.blit(title, (screen_w // 2 - title.get_width() // 2, 70))

        buttons = []
        for i, (label, key) in enumerate(algos):
            rect = pygame.Rect(start_x, start_y + i * (BUTTON_H + GAP_Y), BUTTON_W, BUTTON_H)
            _draw_button(screen, button_font, label, rect, (70,130,180), (100,160,220))
            buttons.append((rect, key))

        # Nút quay lại nằm dưới cùng
        back_rect = pygame.Rect(start_x, screen_h - 90, BUTTON_W, BUTTON_H)
        _draw_button(screen, button_font, "BACK", back_rect, (105,105,105), (169,169,169))

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
# MENU CHÍNH – chọn nhóm
# -------------------------
def choose_mode_menu():
    screen_w, screen_h = 800, 600
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("Chọn nhóm thuật toán")

    pygame.font.init()
    title_font = load_pixeboy_font(48)
    button_font = pygame.font.SysFont("Segoe UI", 24, bold=True)  
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

    BUTTON_W, BUTTON_H = 360, 65
    GAP_X, GAP_Y = 30, 25
    start_x = (screen_w - (2 * BUTTON_W + GAP_X)) // 2
    start_y = 180

    while True:
        draw_background(screen, bg, screen_w, screen_h)
        title = title_font.render("ALGORITHMS", True, (255, 215, 0))
        screen.blit(title, (screen_w // 2 - title.get_width() // 2, 80))

        buttons = []
        for i, name in enumerate(groups):
            row = i // 2
            col = i % 2
            rect = pygame.Rect(start_x + col * (BUTTON_W + GAP_X),
                               start_y + row * (BUTTON_H + GAP_Y),
                               BUTTON_W, BUTTON_H)
            base_color, hover_color = colors[i % len(colors)]
            _draw_button(screen, button_font, name, rect, base_color, hover_color)
            buttons.append((rect, name))

        # Nút quay lại nằm dưới cùng
        back_rect = pygame.Rect((screen_w - BUTTON_W)//2,
                                screen_h - 90,
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
