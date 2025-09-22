import pygame, os, random, math
from pathfinding import bfs, dfs, greedy, astar
from collections import deque
from constants import (
    CELL_SIZE, VIEWPORT_W, VIEWPORT_H, MAP_COLS, MAP_ROWS,
    asset_path
)
from PIL import Image, ImageFilter
import numpy as np

from background import ScrollingBackground 
from constants import CELL_SIZE, VIEWPORT_W, VIEWPORT_H, path_tile


# Khởi tạo Pygame và màn hình ban đầu
pygame.init()
pygame.mixer.init()
pygame.display.set_caption("Maze Hunter")
os.environ['SDL_VIDEO_CENTERED'] = '1'
screen = pygame.display.set_mode((1, 1))

# Tải fonts và hình ảnh chung
font_path = asset_path("font/Pixeboy.ttf")
font = pygame.font.SysFont("Segoe UI", 22)
big_font = pygame.font.SysFont("Segoe UI", 48, bold=True)
menu_font = pygame.font.Font(font_path, 80)
treasure_img = pygame.transform.scale(pygame.image.load(asset_path("treasure.png")).convert_alpha(), (CELL_SIZE, CELL_SIZE))
clock = pygame.time.Clock()
path_tile = pygame.image.load(asset_path("path.png")).convert_alpha()
path_tile = pygame.transform.scale(path_tile, (CELL_SIZE, CELL_SIZE))

# Các hàm tải sprites và assets
def load_spritesheet_rows(path, frame_width, frame_height, rows, cols):
    sheet = pygame.image.load(path).convert_alpha()
    frames_by_row = []
    for r in range(rows):
        row_frames = []
        for c in range(cols):
            rect = pygame.Rect(c*frame_width, r*frame_height, frame_width, frame_height)
            frame = sheet.subsurface(rect).copy()
            try:
                crop = frame.subsurface(pygame.Rect(8, 8, frame_width-16, frame_height-16)).copy()
            except Exception:
                crop = frame
            row_frames.append(pygame.transform.scale(crop, (CELL_SIZE, CELL_SIZE)))
        frames_by_row.append(row_frames)
    return frames_by_row

def load_spritesheet_flat(path, frame_width, frame_height, rows, cols):
    sheet = pygame.image.load(path).convert_alpha()
    frames = []
    for r in range(rows):
        for c in range(cols):
            rect = pygame.Rect(c*frame_width, r*frame_height, frame_width, frame_height)
            frame = sheet.subsurface(rect).copy()
            try:
                crop = frame.subsurface(pygame.Rect(8, 8, frame_width-16, frame_height-16)).copy()
            except Exception:
                crop = frame
            frames.append(pygame.transform.scale(crop, (CELL_SIZE, CELL_SIZE)))
    return frames

def load_theme(theme_name):
    theme_dir = os.path.join(asset_path("ruin"), theme_name)
    wall_images = []
    if os.path.isdir(theme_dir):
        for fname in os.listdir(theme_dir):
            if fname.lower().endswith((".png", ".jpg")) and not fname.startswith("bg_"):
                img = pygame.image.load(os.path.join(theme_dir, fname)).convert_alpha()
                img = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
                wall_images.append(img)
    bg_path = os.path.join(theme_dir, f"bg_{theme_name}.png")
    if os.path.exists(bg_path):
        bg_img = pygame.transform.scale(pygame.image.load(bg_path).convert(), (CELL_SIZE, CELL_SIZE))
    else:
        default_bg_path = os.path.join(asset_path("ruin"), "bg_ruin.png")
        if os.path.exists(default_bg_path):
            bg_img = pygame.transform.scale(pygame.image.load(default_bg_path).convert(), (CELL_SIZE, CELL_SIZE))
        else:
            bg_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
            bg_img.fill((50, 50, 50))
    
    # Thêm logic tải hình ảnh road ở đây
    road_path = asset_path(f"road/road_{theme_name}.png")
    if not os.path.exists(road_path):
        road_path = asset_path("road/road_white.png")
        
    road_img = pygame.transform.scale(pygame.image.load(road_path).convert(), (CELL_SIZE, CELL_SIZE))
    
    return wall_images, bg_img, road_img


# Các hàm tạo maze
def generate_maze(width, height):
    if width % 2 == 0: width += 1
    if height % 2 == 0: height += 1
    maze = [[1 for _ in range(width)] for _ in range(height)]
    def carve(x, y):
        dirs = [(2,0), (-2,0), (0,2), (0,-2)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x+dx, y+dy
            if 1 <= nx < width-1 and 1 <= ny < height-1 and maze[ny][nx] == 1:
                maze[ny - dy//2][nx - dx//2] = 0
                maze[ny][nx] = 0
                carve(nx, ny)
    maze[1][1] = 0
    carve(1, 1)
    add_loops(maze, 0.08)
    return maze

def add_loops(maze, chance=0.05):
    rows, cols = len(maze), len(maze[0])
    for r in range(1, rows-1):
        for c in range(1, cols-1):
            if maze[r][c] == 1 and random.random() < chance:
                maze[r][c] = 0

def farthest_cell(maze, start):
    rows, cols = len(maze), len(maze[0])
    q = deque([(start, 0)])
    visited = set([start])
    farthest, max_dist = start, 0
    while q:
        (r, c), d = q.popleft()
        if d > max_dist:
            farthest, max_dist = (r, c), d
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 0 and (nr,nc) not in visited:
                visited.add((nr,nc))
                q.append(((nr,nc), d+1))
    return farthest

# Các hàm vẽ UI
def clamp(v, a, b):
    return max(a, min(b, v))

button_font = pygame.font.Font(font_path, 22)

def draw_button(rect, text, color):
    pygame.draw.rect(screen, color, rect, border_radius=10)
    label = button_font.render(text, True, (255, 255, 255))
    screen.blit(label, (rect.centerx - label.get_width() // 2,
                        rect.centery - label.get_height() // 2))

# Thay đổi hàm draw_maze để nhận floor_img từ tham số
def draw_maze(maze, goal, offset_x, offset_y, wall_mapping, ruin_images, bg_ruin_img, floor_img):
    rows, cols = len(maze), len(maze[0])
    start_col = max(0, int(offset_x) // CELL_SIZE)
    end_col = min(cols, (int(offset_x) + VIEWPORT_W) // CELL_SIZE + 2)
    start_row = max(0, int(offset_y) // CELL_SIZE)
    end_row = min(rows, (int(offset_y) + VIEWPORT_H) // CELL_SIZE + 2)

    for r in range(start_row, end_row):
        for c in range(start_col, end_col):
            screen_x = c*CELL_SIZE - offset_x
            screen_y = r*CELL_SIZE - offset_y
            if maze[r][c] == 1:
                if (r, c) not in wall_mapping:
                    wall_mapping[(r, c)] = random.choice(ruin_images) if ruin_images else None
                screen.blit(bg_ruin_img, (screen_x, screen_y))
                if wall_mapping[(r, c)]:
                    screen.blit(wall_mapping[(r, c)], (screen_x, screen_y))
            else:
                screen.blit(floor_img, (screen_x, screen_y))
    tr_x = goal[1]*CELL_SIZE - offset_x
    tr_y = goal[0]*CELL_SIZE - offset_y
    if -CELL_SIZE <= tr_x <= VIEWPORT_W and -CELL_SIZE <= tr_y <= VIEWPORT_H:
        screen.blit(treasure_img, (tr_x, tr_y))

def draw_entity(pos, img, offset_x, offset_y):
    x = pos[1]*CELL_SIZE - offset_x
    y = pos[0]*CELL_SIZE - offset_y
    screen.blit(img, (x, y))

def draw_player(pos, direction, index, offset_x, offset_y, animations):
    frames = animations[direction]
    img = frames[index % len(frames)]
    x = pos[1]*CELL_SIZE - offset_x
    y = pos[0]*CELL_SIZE - offset_y
    screen.blit(img, (x, y))

def draw_path(screen, path, offset_x, offset_y):
    if not path: 
        return
    for (r, c) in path:
        x = c * CELL_SIZE - offset_x
        y = r * CELL_SIZE - offset_y
        screen.blit(path_tile, (x, y))

# Tạo font riêng cho control panel
control_font = pygame.font.Font(font_path, 22) 

def draw_control_panel(view_w, view_h, paused):
    panel_w = 160
    panel_rect = pygame.Rect(view_w, 0, panel_w, view_h)
    pygame.draw.rect(screen, (40, 40, 40), panel_rect)

    btn_w, btn_h, gap = 120, 50, 20
    x = view_w + 20
    y = 160
    buttons = {}

    # Pause / Continue
    if not paused:
        pause_btn = pygame.Rect(x, y, btn_w, btn_h)
        draw_control_button(pause_btn, "Pause", (80, 80, 200))
        buttons["pause"] = pause_btn
    else:
        cont_btn = pygame.Rect(x, y, btn_w, btn_h)
        draw_control_button(cont_btn, "Continue", (50, 180, 100))
        buttons["continue"] = cont_btn
    y += btn_h + gap

    # Reset
    reset_btn = pygame.Rect(x, y, btn_w, btn_h)
    draw_control_button(reset_btn, "Reset", (200, 150, 50))
    buttons["reset"] = reset_btn
    y += btn_h + gap

    # Surrender
    surrender_btn = pygame.Rect(x, y, btn_w, btn_h)
    draw_control_button(surrender_btn, "Surrender", (200, 60, 60))
    buttons["surrender"] = surrender_btn

    return buttons, panel_w

def get_control_buttons(paused):
    btn_w, btn_h, gap = 120, 50, 20
    x = VIEWPORT_W + 20
    y = 160
    buttons = {}
    if not paused:
        pause_btn = pygame.Rect(x, y, btn_w, btn_h)
        buttons["pause"] = pause_btn
    else:
        cont_btn = pygame.Rect(x, y, btn_w, btn_h)
        buttons["continue"] = cont_btn
    y += btn_h + gap

    reset_btn = pygame.Rect(x, y, btn_w, btn_h)
    buttons["reset"] = reset_btn
    y += btn_h + gap

    surrender_btn = pygame.Rect(x, y, btn_w, btn_h)
    buttons["surrender"] = surrender_btn

    return buttons

def draw_control_button(rect, text, color):
    pygame.draw.rect(screen, color, rect, border_radius=10)
    label = control_font.render(text, True, (255, 255, 255))
    screen.blit(label, (rect.centerx - label.get_width() // 2,
                        rect.centery - label.get_height() // 2))

def main_menu():
    screen_w, screen_h = 800, 600
    screen = pygame.display.set_mode((screen_w, screen_h))
    
    try:
        bg = ScrollingBackground(asset_path("background.png"), 600, speed = 1)
    except Exception:
        bg = None

    button_font = pygame.font.Font(font_path, 28)

    def draw_menu_button(text, x, y, w, h, color, hover_color, text_color=(255,255,255)):
        rect = pygame.Rect(x, y, w, h)
        mouse_pos = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, rect, border_radius=10)
        else:
            pygame.draw.rect(screen, color, rect, border_radius=10)
        label = button_font.render(text, True, text_color)
        screen.blit(label, (x + (w - label.get_width()) // 2,
                            y + (h - label.get_height()) // 2))
        return rect

    MENU_W = screen_w
    BUTTON_W = 200
    BUTTON_H = 50
    GAP = 40

    # tọa độ căn 2 nút trên 1 hàng
    left_x  = (MENU_W - (BUTTON_W * 2 + GAP)) // 2
    right_x = left_x + BUTTON_W + GAP

    y1 = 200
    y2 = 280
    y_exit = 380

    while True:
        # vẽ background
        if bg:
            bg.draw(screen)
            overlay = pygame.Surface((screen_w, screen_h))
            overlay.set_alpha(120)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill((30, 30, 40))

        # Title
        title_text = "Maze Hunter"
        title_color = (255, 215, 0)
        title = menu_font.render(title_text, True, title_color)
        screen.blit(title, (screen_w // 2 - title.get_width() // 2, 80))

        # Buttons
        bfs_btn    = draw_menu_button("PLAY BFS MODE", left_x,  y1, BUTTON_W, BUTTON_H, (70,130,180), (100,160,220))
        dfs_btn    = draw_menu_button("PLAY DFS MODE", right_x, y1, BUTTON_W, BUTTON_H, (34,139,34),  (60,179,60))
        greedy_btn = draw_menu_button("PLAY GREEDY",   left_x,  y2, BUTTON_W, BUTTON_H, (218,165,32), (238,201,0))
        astar_btn  = draw_menu_button("PLAY A* MODE",  right_x, y2, BUTTON_W, BUTTON_H, (138,43,226), (160,82,255))
        exit_btn   = draw_menu_button("EXIT", (MENU_W-BUTTON_W)//2, y_exit, BUTTON_W, BUTTON_H, (178,34,34), (220,50,50))

        # update
        pygame.display.flip()
        clock.tick(30)

        # xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if bfs_btn.collidepoint(event.pos):
                    return "bfs"
                elif dfs_btn.collidepoint(event.pos):
                    return "dfs"
                elif greedy_btn.collidepoint(event.pos):
                    return "greedy"
                elif astar_btn.collidepoint(event.pos):
                    return "astar"
                elif exit_btn.collidepoint(event.pos):
                    return "exit"

def loading_screen():
    screen = pygame.display.set_mode((600, 400))
   
    # Font title
    title_font = pygame.font.Font(font_path, 40)  
    tip_font = pygame.font.SysFont("segoeui", 22, bold = True)
    bar_font = pygame.font.SysFont("segoeui", 20)

    # Load ảnh nền, scale theo chiều cao (400)
    bg_img = pygame.image.load(asset_path("background.png")).convert()
    bg_width, bg_height = bg_img.get_size()
    scale_factor = 400 / bg_height
    bg_width_scaled = int(bg_width * scale_factor)
    bg_img = pygame.transform.scale(bg_img, (bg_width_scaled, 400))

    scroll_x = 0
    speed = 0.3  # chậm lại cho mượt

    progress = 0
    tip_text = random.choice([
        "Mẹo: Hunter luôn đuổi theo bạn!",
        "Mẹo: Dùng phím mũi tên để di chuyển.",
        "Mỗi màn có bản đồ khác nhau.",
    ])

    running = True
    while running:
        # Vẽ background cuộn ngang
        scroll_x -= speed
        if scroll_x <= -bg_width_scaled:
            scroll_x = 0

        screen.blit(bg_img, (scroll_x, 0))
        screen.blit(bg_img, (scroll_x + bg_width_scaled, 0))

        # Overlay làm mờ
        overlay = pygame.Surface((600, 400))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Title (màu vàng sáng)
        title = title_font.render("Loading Maze Hunter...", True, (255, 215, 0))
        screen.blit(title, (300 - title.get_width() // 2, 100))

        # Thanh progress
        bar_w, bar_h, bar_x, bar_y = 400, 30, 100, 200
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 3)
        pygame.draw.rect(
            screen, (50, 255, 120),  # xanh neon
            (bar_x + 3, bar_y + 3, int(progress * (bar_w - 6)), bar_h - 6)
        )
        bar_label = bar_font.render(f"{int(progress*100)}%", True, (255, 255, 0))
        screen.blit(bar_label, (300 - bar_label.get_width() // 2, bar_y + bar_h + 10))

        # Hint text (Segoe UI, vàng nhạt)
        hint = tip_font.render(tip_text, True, (255, 220, 100))
        screen.blit(hint, (300 - hint.get_width() // 2, 280))

        pygame.display.flip()
        clock.tick(60)

        # Tăng tiến độ
        progress += 0.006
        if progress >= 1:
            running = False


def transition_screen(text, color=(255, 215, 0)):
    screen_w, screen_h = screen.get_size()

    # Font
    title_font = pygame.font.Font(font_path, 48)
    info_font = pygame.font.SysFont("segoeui", 22)

    # Load ảnh nền & scale theo chiều cao màn hình
    bg_img = pygame.image.load(asset_path("background.png")).convert()
    bg_width, bg_height = bg_img.get_size()
    scale_factor = screen_h / bg_height
    bg_width_scaled = int(bg_width * scale_factor)
    bg_img = pygame.transform.scale(bg_img, (bg_width_scaled, screen_h))

    scroll_x = 0
    speed = 0.6

    # Panel settings
    panel_w, panel_h = 400, 200
    panel_x = (screen_w - panel_w) // 2
    panel_y = (screen_h - panel_h) // 2

    # Fade-in alpha
    alpha = 0
    waiting = True
    while waiting:
        # Cuộn background
        scroll_x -= speed
        if scroll_x <= -bg_width_scaled:
            scroll_x = 0
        screen.blit(bg_img, (scroll_x, 0))
        screen.blit(bg_img, (scroll_x + bg_width_scaled, 0))

        # Overlay tối
        overlay = pygame.Surface((screen_w, screen_h))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # ----- Panel -----
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (30, 30, 40, alpha), panel.get_rect(), border_radius=15)   # nền mờ
        pygame.draw.rect(panel, (200, 200, 200, alpha), panel.get_rect(), 3, border_radius=15) # viền
        screen.blit(panel, (panel_x, panel_y))

        # ----- Text trong panel -----
        if alpha > 150:  # hiện chữ khi panel đã đủ rõ
            label = title_font.render(text, True, color)
            label_rect = label.get_rect(center=(screen_w // 2, panel_y + 70))
            screen.blit(label, label_rect)

            info = info_font.render("Nhấn SPACE để tiếp tục...", True, (220,220,220))
            info_rect = info.get_rect(center=(screen_w // 2, panel_y + panel_h - 40))
            screen.blit(info, info_rect)

        # Cập nhật
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and alpha >= 180:
                waiting = False

        # Tăng alpha cho hiệu ứng fade-in
        if alpha < 220:
            alpha += 5

        clock.tick(60)

    return "next"

def blur_surface(surface, radius=5):
    arr = pygame.surfarray.array3d(surface)
    img = Image.fromarray(np.transpose(arr, (1, 0, 2)))  # đổi trục (x,y)
    img = img.filter(ImageFilter.GaussianBlur(radius=radius))  # làm mờ
    arr = np.transpose(np.array(img), (1, 0, 2))  # đổi lại
    return pygame.surfarray.make_surface(arr)

def end_screen(result):
    global screen, clock, big_font

    screen_w, screen_h = screen.get_size()

    snapshot = screen.copy()
    blurred = blur_surface(snapshot, radius=8)
    screen.blit(blurred, (0, 0))

    # ----- Label -----
    text = "GAME OVER" if result == "lose" else "Bạn đã thắng!"

    color = (255, 215, 0) if result == "lose" else (180, 0, 0)
    label = menu_font.render(text, True, color)
    label_rect = label.get_rect(center=(screen_w // 2, screen_h // 2 - 60))
    screen.blit(label, label_rect)

    # ----- Buttons -----
    button_width, button_height = 120, 50
    spacing = 20
    total_width = button_width * 2 + spacing
    start_x = (screen_w - total_width) // 2
    y = screen_h // 2 + 20

    retry_btn = pygame.Rect(start_x, y, button_width, button_height)
    exit_btn = pygame.Rect(start_x + button_width + spacing, y, button_width, button_height)

    draw_button(retry_btn, "Retry", (50, 150, 200))
    draw_button(exit_btn, "Exit", (200, 50, 50))

    pygame.display.flip()

    # ----- Vòng lặp sự kiện -----
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                return "exit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if retry_btn.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    pygame.mixer.stop()
                    return "retry"
                elif exit_btn.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    pygame.mixer.stop()
                    return "exit"
        clock.tick(30)

  
def draw_minimap(maze, player_pos, hunter_pos, goal, panel_rect, offset_x, offset_y, map_w_pix, map_h_pix):
    MINI_W, MINI_H = 120, 120
    mini_x = panel_rect.x + (panel_rect.width - MINI_W) // 2
    mini_y = 10
    rows, cols = len(maze), len(maze[0])
    sx = MINI_W / map_w_pix
    sy = MINI_H / map_h_pix

    pygame.draw.rect(screen, (20,20,20), (mini_x-2, mini_y-2, MINI_W+4, MINI_H+4))
    pygame.draw.rect(screen, (120,120,120), (mini_x-2, mini_y-2, MINI_W+4, MINI_H+4), 2)

    cell_w = CELL_SIZE * sx
    cell_h = CELL_SIZE * sy
    for r in range(rows):
        for c in range(cols):
            color = (50,50,50) if maze[r][c] == 1 else (220,220,220)
            rx = mini_x + c * cell_w
            ry = mini_y + r * cell_h
            if rx > mini_x + MINI_W or ry > mini_y + MINI_H:
                continue
            pygame.draw.rect(screen, color, (rx, ry, cell_w+1, cell_h+1))

    pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.5
    bright = int(200 + 55 * pulse)

    tx = mini_x + goal[1] * CELL_SIZE * sx
    ty = mini_y + goal[0] * CELL_SIZE * sy
    tre_w = max(6, cell_w)
    tre_h = max(6, cell_h)
    pygame.draw.rect(screen, (255, 0, 0), (tx-2, ty-2, tre_w+4, tre_h+4))
    pygame.draw.rect(screen, (bright, bright, 0), (tx, ty, tre_w, tre_h))

    px = mini_x + player_pos[1] * CELL_SIZE * sx
    py = mini_y + player_pos[0] * CELL_SIZE * sy
    pygame.draw.rect(screen, (50,150,255), (px, py, max(3, cell_w), max(3, cell_h)))

    hx = mini_x + hunter_pos[1] * CELL_SIZE * sx
    hy = mini_y + hunter_pos[0] * CELL_SIZE * sy
    pygame.draw.rect(screen, (200,50,50), (hx, hy, max(3, cell_w), max(3, cell_h)))

    view_rx = mini_x + (offset_x) * sx
    view_ry = mini_y + (offset_y) * sy
    view_rw = VIEWPORT_W * sx
    view_rh = VIEWPORT_H * sy
    pygame.draw.rect(screen, (0,200,0), (view_rx, view_ry, view_rw, view_rh), 2)

