import pygame
import random
from constants import asset_path
from background import ScrollingBackground

# =========================
# Hàm dùng chung
# =========================
def draw_background(screen, bg, screen_w, screen_h):
    if bg:
        bg.draw(screen)
        overlay = pygame.Surface((screen_w, screen_h))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
    else:
        screen.fill((30, 30, 40))

# =========================
# Menu chọn chế độ
# =========================
def choose_mode_menu():
    screen_w, screen_h = 800, 600
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("Choose Mode")

    font_path = asset_path("font/Pixeboy.ttf")
    title_font = pygame.font.Font(font_path, 60)
    button_font = pygame.font.Font(font_path, 28)

    clock = pygame.time.Clock()

    # Background
    try:
        bg = ScrollingBackground(asset_path("background.png"), 600, speed=1)
    except Exception:
        bg = None

    def draw_button(text, rect, color, hover_color):
        mouse_pos = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, rect, border_radius=10)
        else:
            pygame.draw.rect(screen, color, rect, border_radius=10)
        label = button_font.render(text, True, (255, 255, 255))
        screen.blit(label, (rect.x + (rect.w - label.get_width()) // 2,
                            rect.y + (rect.h - label.get_height()) // 2))
        return rect

    BUTTON_W, BUTTON_H = 250, 60
    GAP_X, GAP_Y = 20, 20
    start_x = (screen_w - (2 * BUTTON_W + GAP_X)) // 2
    start_y = 200

    while True:
        draw_background(screen, bg, screen_w, screen_h)

        # Title
        title = title_font.render("Choose Mode", True, (255, 215, 0))
        screen.blit(title, (screen_w // 2 - title.get_width() // 2, 100))

        # Tạo grid 2 cột
        btn_positions = {
            "bfs":    pygame.Rect(start_x, start_y, BUTTON_W, BUTTON_H),
            "dfs":    pygame.Rect(start_x + BUTTON_W + GAP_X, start_y, BUTTON_W, BUTTON_H),

            "greedy": pygame.Rect(start_x, start_y + BUTTON_H + GAP_Y, BUTTON_W, BUTTON_H),
            "astar":  pygame.Rect(start_x + BUTTON_W + GAP_X, start_y + BUTTON_H + GAP_Y, BUTTON_W, BUTTON_H),

            "hillclimbing": pygame.Rect(start_x, start_y + 2*(BUTTON_H + GAP_Y), BUTTON_W, BUTTON_H),
            "sa":           pygame.Rect(start_x + BUTTON_W + GAP_X, start_y + 2*(BUTTON_H + GAP_Y), BUTTON_W, BUTTON_H),

            "back":   pygame.Rect((screen_w - BUTTON_W)//2, start_y + 3*(BUTTON_H + GAP_Y) + 30, BUTTON_W, BUTTON_H)
        }

        # Vẽ các nút
        bfs_btn    = draw_button("BFS", btn_positions["bfs"], (70,130,180), (100,160,220))
        dfs_btn    = draw_button("DFS", btn_positions["dfs"], (34,139,34), (60,179,60))
        greedy_btn = draw_button("GREEDY", btn_positions["greedy"], (218,165,32), (255,215,0))
        astar_btn  = draw_button("A*", btn_positions["astar"], (178,34,34), (220,50,50))
        hc_btn     = draw_button("HILL CLIMBING", btn_positions["hillclimbing"], (138,43,226), (160,82,255))
        sa_btn     = draw_button("SIMULATED ANNEALING", btn_positions["sa"], (255,140,0), (255,165,0))
        back_btn   = draw_button("BACK", btn_positions["back"], (105,105,105), (169,169,169))

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if bfs_btn.collidepoint(event.pos): return "bfs"
                elif dfs_btn.collidepoint(event.pos): return "dfs"
                elif greedy_btn.collidepoint(event.pos): return "greedy"
                elif astar_btn.collidepoint(event.pos): return "astar"
                elif hc_btn.collidepoint(event.pos): return "hillclimbing"
                elif sa_btn.collidepoint(event.pos): return "sa"
                elif back_btn.collidepoint(event.pos): return "back"

# =========================
# Menu chính
# =========================
def main_menu():
    pygame.init()
    screen_w, screen_h = 800, 600
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("Maze Hunter - Menu")

    font_path = asset_path("font/Pixeboy.ttf")
    menu_font = pygame.font.Font(font_path, 80)
    button_font = pygame.font.Font(font_path, 28)
    clock = pygame.time.Clock()

    # Background
    try:
        bg = ScrollingBackground(asset_path("background.png"), 600, speed=1)
    except Exception:
        bg = None

    def draw_button(text, x, y, w, h, color, hover_color):
        rect = pygame.Rect(x, y, w, h)
        mouse_pos = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, rect, border_radius=10)
        else:
            pygame.draw.rect(screen, color, rect, border_radius=10)
        label = button_font.render(text, True, (255, 255, 255))
        screen.blit(label, (x + (w - label.get_width()) // 2,
                            y + (h - label.get_height()) // 2))
        return rect

    BUTTON_W, BUTTON_H = 250, 60
    GAP = 80
    start_y = 220

    while True:
        draw_background(screen, bg, screen_w, screen_h)

        # Title
        title = menu_font.render("Maze Hunter", True, (255, 215, 0))
        screen.blit(title, (screen_w // 2 - title.get_width() // 2, 100))

        # Buttons
        random_btn = draw_button("PLAY RANDOM", (screen_w - BUTTON_W)//2, start_y,
                                 BUTTON_W, BUTTON_H, (70, 130, 180), (100, 160, 220))
        choose_btn = draw_button("CHOOSE MODE", (screen_w - BUTTON_W)//2, start_y + GAP,
                                 BUTTON_W, BUTTON_H, (34, 139, 34), (60, 179, 60))
        exit_btn   = draw_button("EXIT", (screen_w - BUTTON_W)//2, start_y + 2*GAP,
                                 BUTTON_W, BUTTON_H, (178, 34, 34), (220, 50, 50))

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if random_btn.collidepoint(event.pos):
                    return random.choice(["bfs", "dfs", "greedy", "astar", "hillclimbing", "sa"])
                elif choose_btn.collidepoint(event.pos):
                    mode = choose_mode_menu()
                    if mode == "back":
                        continue
                    return mode
                elif exit_btn.collidepoint(event.pos):
                    return "exit"
