import pygame
import random
import math
from collections import deque
from background import ScrollingBackground
import os

# =================== SETUP ===================
CELL_SIZE = 80
pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'

# BASE DIR + helper path
BASE_DIR = os.path.dirname(__file__)
def asset_path(filename):
    return os.path.join(BASE_DIR, "assets", filename)

# create a tiny temporary display so convert_alpha() won't fail
screen = pygame.display.set_mode((1, 1))
pygame.display.set_caption("Maze Hunter with BFS & DFS")
clock = pygame.time.Clock()

hunter_speed = 8   # càng lớn => hunter càng chậm
player_speed = 2   # càng lớn => player animation càng chậm
hunter_anim_speed = 2   # càng lớn => hunter animation càng chậm

# ================= VIEW / MAP SIZES =================
# số ô hiển thị (viewport) — giữ nguyên như "như bây giờ"
VIEW_TILES_X = 16
VIEW_TILES_Y = 10
VIEWPORT_W = VIEW_TILES_X * CELL_SIZE
VIEWPORT_H = VIEW_TILES_Y * CELL_SIZE

# kích thước map thực tế (lớn hơn)
MAP_COLS = 51  # nên là số lẻ để maze generator ổn; bạn có thể tăng giảm
MAP_ROWS = 31  # nên là số lẻ

# Camera smoothing factor (0..1). Nhỏ hơn => mượt hơn / trễ hơn
CAMERA_LERP = 0.07

# =================== MENU ===================
font_path = asset_path("font/Pixeboy.ttf")
font = pygame.font.SysFont("Segoe UI", 22)
big_font = pygame.font.SysFont("Segoe UI", 48, bold=True)
menu_font = pygame.font.Font(font_path, 80)

def draw_button_adv(rect, text, base_color, hover_color):
    mouse = pygame.mouse.get_pos()
    color = hover_color if rect.collidepoint(mouse) else base_color
    pygame.draw.rect(screen, color, rect, border_radius=15)
    label = font.render(text, True, (255, 255, 255))
    screen.blit(label, (rect.centerx - label.get_width()//2,
                        rect.centery - label.get_height()//2))

def main_menu():
    global screen
    screen = pygame.display.set_mode((600, 400))
    try:
        bg = ScrollingBackground(asset_path("background.png"), 400, speed=1)
    except Exception:
        bg = None

    while True:
        if bg:
            bg.draw(screen)
            overlay = pygame.Surface((600, 400))
            overlay.set_alpha(120)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill((30, 30, 40))

        title_text = "Maze Hunter"
        title_color = (255, 215, 0)
        title = menu_font.render(title_text, True, title_color)
        screen.blit(title, (300 - title.get_width()//2, 80))

        button_font = pygame.font.Font(font_path, 28)
        def draw_button(text, x, y, w, h, color, hover_color, text_color=(255,255,255)):
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

        bfs_btn = draw_button("Play BFS Mode", 180, 160, 240, 50, (70,130,180), (100,160,220))
        dfs_btn = draw_button("Play DFS Mode", 180, 220, 240, 50, (34,139,34), (60,179,60))
        exit_btn = draw_button("Exit",          180, 280, 240, 50, (178,34,34),(220,50,50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if bfs_btn.collidepoint(event.pos):
                    return "bfs"
                elif dfs_btn.collidepoint(event.pos):
                    return "dfs"
                elif exit_btn.collidepoint(event.pos):
                    return "exit"
        clock.tick(30)

# =================== HELPERS TO LOAD SPRITES ===================
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

# =================== LOAD ASSETS ===================
# player sheet (4 rows x 8 cols)
sprite_rows, sprite_cols = 4, 8
player_frames = load_spritesheet_rows(asset_path("player_run.png"), 64, 64, sprite_rows, sprite_cols)
animations = {
    "down":  player_frames[0],
    "up":    player_frames[1],
    "left":  player_frames[2],
    "right": player_frames[3],
}

# Enemy: try to load spritesheet with rows x cols, then map first 4 rows -> directions
enemy_sheet_candidates = ["enemy_run.png", "enemy_sheet.png", "enemy.png"]
enemy_animations = None
enemy_single = None
for fname in enemy_sheet_candidates:
    path = asset_path(fname)
    if not os.path.exists(path):
        continue
    surf = pygame.image.load(path).convert_alpha()
    w,h = surf.get_size()
    cols = max(1, w // 64)
    rows = max(1, h // 64)
    if rows >= 1 and cols >= 1:
        try:
            frames_by_row = load_spritesheet_rows(path, 64, 64, rows, cols)
            def get_row(i):
                if i < len(frames_by_row):
                    return frames_by_row[i]
                return frames_by_row[0]
            enemy_animations = {
                "down": get_row(0),
                "up":   get_row(1) if rows > 1 else get_row(0),
                "left": get_row(2) if rows > 2 else get_row(0),
                "right":get_row(3) if rows > 3 else get_row(0),
            }
            break
        except Exception:
            enemy_single = pygame.transform.scale(surf, (CELL_SIZE, CELL_SIZE))
            break

if enemy_animations is None:
    if enemy_single is None:
        try:
            enemy_single = pygame.transform.scale(pygame.image.load(asset_path("enemy.png")).convert_alpha(), (CELL_SIZE, CELL_SIZE))
        except Exception:
            enemy_single = None
    if enemy_single:
        enemy_animations = {
            "down":  [enemy_single],
            "up":    [enemy_single],
            "left":  [enemy_single],
            "right": [enemy_single],
        }
    else:
        surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        surf.fill((0,200,0))
        enemy_animations = {"down":[surf],"up":[surf],"left":[surf],"right":[surf]}

# =================== THEME / RUIN LOADING ===================
def load_theme(theme_name):
    theme_dir = os.path.join(BASE_DIR, "assets", "ruin", theme_name)
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
        default_bg_path = os.path.join(BASE_DIR, "assets", "ruin", "bg_ruin.png")
        if os.path.exists(default_bg_path):
            bg_img = pygame.transform.scale(pygame.image.load(default_bg_path).convert(), (CELL_SIZE, CELL_SIZE))
        else:
            bg_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
            bg_img.fill((50, 50, 50))
    return wall_images, bg_img

available_themes = ["sand", "snow", "water", "blue", "brown", "white", "yellow"]

floor_img = pygame.transform.scale(pygame.image.load(asset_path("floor.png")).convert(), (CELL_SIZE, CELL_SIZE))
treasure_img = pygame.transform.scale(pygame.image.load(asset_path("treasure.jpg")).convert(), (CELL_SIZE, CELL_SIZE))

# =================== MAZE GEN ===================
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

# =================== PATHFINDING ===================
def bfs(start, goal, maze):
    ROWS, COLS = len(maze), len(maze[0])
    q = deque([(start, [start])])
    visited = {start}
    while q:
        (r, c), path = q.popleft()
        if (r, c) == goal:
            return path
        for dr, dc in [(1,0), (0,1), (-1,0), (0,-1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0 and (nr,nc) not in visited:
                visited.add((nr,nc))
                q.append(((nr,nc), path + [(nr,nc)]))
    return []

def dfs(start, goal, maze):
    ROWS, COLS = len(maze), len(maze[0])
    stack = [(start, [start])]
    visited = {start}
    while stack:
        (r, c), path = stack.pop()
        if (r, c) == goal:
            return path
        for dr, dc in [(1,0), (0,1), (-1,0), (0,-1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0 and (nr,nc) not in visited:
                visited.add((nr,nc))
                stack.append(((nr,nc), path + [(nr,nc)]))
    return []

# =================== VẼ (camera-aware) ===================
wall_mapping = {}

def clamp(v, a, b):
    return max(a, min(b, v))

def draw_maze(maze, goal, offset_x, offset_y):
    rows, cols = len(maze), len(maze[0])
    # find visible tile range to optimize drawing
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
    # treasure
    tr_x = goal[1]*CELL_SIZE - offset_x
    tr_y = goal[0]*CELL_SIZE - offset_y
    if -CELL_SIZE <= tr_x <= VIEWPORT_W and -CELL_SIZE <= tr_y <= VIEWPORT_H:
        screen.blit(treasure_img, (tr_x, tr_y))

def draw_entity(pos, img, offset_x, offset_y):
    x = pos[1]*CELL_SIZE - offset_x
    y = pos[0]*CELL_SIZE - offset_y
    screen.blit(img, (x, y))

def draw_player(pos, direction, index, offset_x, offset_y):
    frames = animations[direction]
    img = frames[index % len(frames)]
    x = pos[1]*CELL_SIZE - offset_x
    y = pos[0]*CELL_SIZE - offset_y
    screen.blit(img, (x, y))

def draw_path(path, color, offset_x, offset_y):
    for (r, c) in path:
        sx = c*CELL_SIZE - offset_x + CELL_SIZE//4
        sy = r*CELL_SIZE - offset_y + CELL_SIZE//4
        if -CELL_SIZE <= sx <= VIEWPORT_W and -CELL_SIZE <= sy <= VIEWPORT_H:
            rect = pygame.Rect(sx, sy, CELL_SIZE//2, CELL_SIZE//2)
            pygame.draw.rect(screen, color, rect)

def draw_button(rect, text, color=(50, 50, 200)):
    pygame.draw.rect(screen, color, rect, border_radius=10)
    label = font.render(text, True, (255, 255, 255))
    screen.blit(label, (rect.centerx - label.get_width()//2,
                        rect.centery - label.get_height()//2))

# =================== MINI MAP ===================
def draw_minimap(maze, player_pos, hunter_pos, goal, panel_rect, offset_x, offset_y, map_w_pix, map_h_pix):
    # dimensions inside panel
    MINI_W, MINI_H = 120, 120
    mini_x = panel_rect.x + (panel_rect.width - MINI_W) // 2
    mini_y = 10
    rows, cols = len(maze), len(maze[0])
    # scale from map pixels to minimap pixels
    sx = MINI_W / map_w_pix
    sy = MINI_H / map_h_pix

    # background + border
    pygame.draw.rect(screen, (20,20,20), (mini_x-2, mini_y-2, MINI_W+4, MINI_H+4))
    pygame.draw.rect(screen, (120,120,120), (mini_x-2, mini_y-2, MINI_W+4, MINI_H+4), 2)

    # draw cells (coarse: map is large so draw by checking 1 cell -> rectangle)
    # We draw by iterating cells but scaling by CELL_SIZE*sx, CELL_SIZE*sy
    cell_w = CELL_SIZE * sx
    cell_h = CELL_SIZE * sy
    for r in range(rows):
        for c in range(cols):
            color = (50,50,50) if maze[r][c] == 1 else (220,220,220)
            rx = mini_x + c * cell_w
            ry = mini_y + r * cell_h
            # skip if outside minimap due to rounding
            if rx > mini_x + MINI_W or ry > mini_y + MINI_H:
                continue
            pygame.draw.rect(screen, color, (rx, ry, cell_w+1, cell_h+1))

    # === Treasure highlight ===
    pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.5  # dao động 0..1
    bright = int(200 + 55 * pulse)  # dao động 200..255

    tx = mini_x + goal[1] * CELL_SIZE * sx
    ty = mini_y + goal[0] * CELL_SIZE * sy

    # Kích thước cố định để dễ thấy (ít nhất 6x6)
    tre_w = max(6, cell_w)
    tre_h = max(6, cell_h)

    # Viền đỏ để nổi bật
    pygame.draw.rect(screen, (255, 0, 0), (tx-2, ty-2, tre_w+4, tre_h+4))

    # Treasure vàng nhấp nháy
    pygame.draw.rect(screen, (bright, bright, 0), (tx, ty, tre_w, tre_h))

    # player
    px = mini_x + player_pos[1] * CELL_SIZE * sx
    py = mini_y + player_pos[0] * CELL_SIZE * sy
    pygame.draw.rect(screen, (50,150,255), (px, py, max(3, cell_w), max(3, cell_h)))

    # hunter
    hx = mini_x + hunter_pos[1] * CELL_SIZE * sx
    hy = mini_y + hunter_pos[0] * CELL_SIZE * sy
    pygame.draw.rect(screen, (200,50,50), (hx, hy, max(3, cell_w), max(3, cell_h)))

    # draw viewport rectangle on minimap
    view_rx = mini_x + (offset_x) * sx
    view_ry = mini_y + (offset_y) * sy
    view_rw = VIEWPORT_W * sx
    view_rh = VIEWPORT_H * sy
    pygame.draw.rect(screen, (0,200,0), (view_rx, view_ry, view_rw, view_rh), 2)

# =================== CONTROL PANEL ===================
def draw_control_panel(view_w, view_h, paused):
    panel_w = 160
    panel_rect = pygame.Rect(view_w, 0, panel_w, view_h)
    pygame.draw.rect(screen, (40, 40, 40), panel_rect)
    btn_w, btn_h, gap = 120, 50, 20
    x = view_w + 20
    y = 160
    buttons = {}
    if not paused:
        pause_btn = pygame.Rect(x, y, btn_w, btn_h)
        draw_button(pause_btn, "Pause", (80, 80, 200))
        buttons["pause"] = pause_btn
    else:
        cont_btn = pygame.Rect(x, y, btn_w, btn_h)
        draw_button(cont_btn, "Continue", (50, 180, 100))
        buttons["continue"] = cont_btn
    y += btn_h + gap
    reset_btn = pygame.Rect(x, y, btn_w, btn_h)
    draw_button(reset_btn, "Reset", (200, 150, 50))
    buttons["reset"] = reset_btn
    y += btn_h + gap
    surrender_btn = pygame.Rect(x, y, btn_w, btn_h)
    draw_button(surrender_btn, "Surrender", (200, 60, 60))
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

# =================== LOADING / TRANSITION / END SCREENS ===================
def loading_screen():
    global screen
    screen = pygame.display.set_mode((600, 400))
    clock = pygame.time.Clock()
    progress, tip_text = 0, random.choice([
        "Mẹo: Hunter luôn đuổi theo bạn!",
        "Mẹo: Dùng phím mũi tên để di chuyển.",
        "Mỗi màn có bản đồ khác nhau.",
    ])
    while True:
        screen.fill((20, 20, 20))
        title = font.render("Loading Maze Hunter...", True, (255, 255, 255))
        screen.blit(title, (180, 120))
        bar_w, bar_h, bar_x, bar_y = 400, 30, 100, 200
        pygame.draw.rect(screen, (255,255,255), (bar_x, bar_y, bar_w, bar_h), 2)
        pygame.draw.rect(screen, (0,200,0), (bar_x+2, bar_y+2, int(progress*(bar_w-4)), bar_h-4))
        hint = font.render(tip_text, True, (200,200,200))
        screen.blit(hint, (120, 260))
        pygame.display.flip()
        clock.tick(60)
        progress += 0.01
        if progress >= 1: break

def transition_screen(text, color=(0,200,0)):
    global screen
    screen.fill((0,0,0))
    label = big_font.render(text, True, color)
    screen.blit(label, (100, 150))
    info = font.render("Nhấn SPACE để tiếp tục...", True, (200,200,200))
    screen.blit(info, (120, 250))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "exit"
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
        clock.tick(30)
    return "next"

def end_screen(result):
    global screen
    screen.fill((30,30,30))
    label = big_font.render("Bạn đã thua!" if result=="lose" else "Bạn đã thắng!",
                            True, (200,50,50) if result=="lose" else (50,200,50))
    screen.blit(label, (100, 150))
    retry_btn = pygame.Rect(120, 250, 120, 50)
    exit_btn = pygame.Rect(260, 250, 120, 50)
    draw_button(retry_btn, "Retry", (50,150,200))
    draw_button(exit_btn, "Exit", (200,50,50))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "exit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if retry_btn.collidepoint(event.pos): return "retry"
                elif exit_btn.collidepoint(event.pos): return "exit"
        clock.tick(30)

# =================== GAME LOOP ===================
def game_loop(mode="bfs"):
    global screen, hunter_timer, wall_mapping, ruin_images, bg_ruin_img
    hunter_timer = 0
    # reset mapping mỗi màn
    wall_mapping = {}

    # chọn theme random mỗi level
    theme = random.choice(available_themes)
    ruin_images, bg_ruin_img = load_theme(theme)

    # hunter animation state (per-direction)
    hunter_dir = "down"
    hunter_frame_index = 0
    hunter_frame_timer = 0

    # tạo map lớn hơn nhưng viewport cố định
    maze = generate_maze(MAP_COLS, MAP_ROWS)
    ROWS, COLS = len(maze), len(maze[0])
    MAP_W_PIX = COLS * CELL_SIZE
    MAP_H_PIX = ROWS * CELL_SIZE

    # màn hình = viewport + panel
    panel_w = 160
    screen = pygame.display.set_mode((VIEWPORT_W + panel_w, VIEWPORT_H))

    start, goal = (1,1), farthest_cell(maze, (1,1))
    player_pos = list(start)
    player_dir = "down"
    frame_index, frame_timer = 0, 0

    hunter_pos = [ROWS//2, COLS//2]
    if maze[hunter_pos[0]][hunter_pos[1]] == 1:
        for r in range(ROWS):
            for c in range(COLS):
                if maze[r][c] == 0:
                    hunter_pos = [r, c]
                    break

    path, running, paused = [], True, False

    # initial camera offsets (center on player if possible)
    # offset variables are floats now for smooth lerp
    offset_x = float(clamp(player_pos[1]*CELL_SIZE - VIEWPORT_W//2, 0, max(0, MAP_W_PIX - VIEWPORT_W)))
    offset_y = float(clamp(player_pos[0]*CELL_SIZE - VIEWPORT_H//2, 0, max(0, MAP_H_PIX - VIEWPORT_H)))

    # target offsets that camera will interpolate towards
    target_off_x = offset_x
    target_off_y = offset_y

    while running:
        # Compute button rects first
        buttons = get_control_buttons(paused)

        # ---- handle events first (for responsive UI) ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if buttons.get("reset") and buttons["reset"].collidepoint(event.pos):
                    return "reset"
                elif "pause" in buttons and buttons["pause"].collidepoint(event.pos):
                    paused = True
                elif "continue" in buttons and buttons["continue"].collidepoint(event.pos):
                    paused = False
                elif buttons.get("surrender") and buttons["surrender"].collidepoint(event.pos):
                    return "exit"

        # fill background for viewport
        screen.fill((10,0,0), rect=pygame.Rect(0,0,VIEWPORT_W, VIEWPORT_H))

        # ==== player input ====
        keys = pygame.key.get_pressed()
        nr, nc = player_pos
        moved = False
        if not paused:
            if keys[pygame.K_UP]:
                nr -= 1; player_dir = "up"; moved = True
            elif keys[pygame.K_DOWN]:
                nr += 1; player_dir = "down"; moved = True
            elif keys[pygame.K_LEFT]:
                nc -= 1; player_dir = "left"; moved = True
            elif keys[pygame.K_RIGHT]:
                nc += 1; player_dir = "right"; moved = True
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0:
                player_pos = [nr, nc]
                # update camera target (not immediate offset)
                target_off_x = clamp(player_pos[1]*CELL_SIZE - VIEWPORT_W//2 + CELL_SIZE//2, 0, max(0, MAP_W_PIX - VIEWPORT_W))
                target_off_y = clamp(player_pos[0]*CELL_SIZE - VIEWPORT_H//2 + CELL_SIZE//2, 0, max(0, MAP_H_PIX - VIEWPORT_H))

        # player animation
        if moved:
            frame_timer += 1
            if frame_timer >= player_speed:
                frame_index = (frame_index + 1) % len(animations[player_dir])
                frame_timer = 0
        else:
            frame_timer += 1
            if frame_timer >= player_speed * 4:
                frame_index = (frame_index + 1) % len(animations[player_dir])
                frame_timer = 0

        # ==== smooth camera update (lerp towards target_off) ====
        # move offset_x/offset_y towards target_off_x/target_off_y
        offset_x += (target_off_x - offset_x) * CAMERA_LERP
        offset_y += (target_off_y - offset_y) * CAMERA_LERP

        # draw maze region (camera-aware)
        draw_maze(maze, goal, offset_x, offset_y)

        # ==== hunter pathfinding & movement + animation ====
        if not paused:
            hunter_timer += 1
            if hunter_timer >= hunter_speed:
                if not path or path[-1] != tuple(player_pos):
                    path = bfs(tuple(hunter_pos), tuple(player_pos), maze) if mode=="bfs" else dfs(tuple(hunter_pos), tuple(player_pos), maze)

                moved_hunter = False
                if len(path) > 1:
                    prev = tuple(hunter_pos)
                    nxt = path[1]
                    dr = nxt[0] - prev[0]
                    dc = nxt[1] - prev[1]
                    # set hunter_dir based on movement vector
                    if abs(dc) > abs(dr):
                        hunter_dir = "right" if dc > 0 else "left"
                    else:
                        hunter_dir = "down" if dr > 0 else "up"

                    hunter_pos = list(nxt)
                    path = path[1:]
                    moved_hunter = True

                # animate hunter
                if moved_hunter:
                    hunter_frame_timer += 1
                    if hunter_frame_timer >= hunter_anim_speed:
                        hunter_frame_index = (hunter_frame_index + 1) % len(enemy_animations[hunter_dir])
                        hunter_frame_timer = 0
                else:
                    hunter_frame_timer += 1
                    if hunter_frame_timer >= hunter_anim_speed * 6:
                        hunter_frame_index = (hunter_frame_index + 1) % len(enemy_animations[hunter_dir])
                        hunter_frame_timer = 0

                hunter_timer = 0

        # draw path (on top of maze)
        if path:
            color = (0,255,255) if mode=="bfs" else (255,128,0)
            draw_path(path, color, offset_x, offset_y)

        # draw player & hunter (camera-aware)
        draw_player(player_pos, player_dir, frame_index, offset_x, offset_y)
        hunter_frames = enemy_animations.get(hunter_dir, enemy_animations["down"])
        hunter_img = hunter_frames[hunter_frame_index % len(hunter_frames)]
        draw_entity(hunter_pos, hunter_img, offset_x, offset_y)

        # draw panel and buttons
        _, panel_w = draw_control_panel(VIEWPORT_W, VIEWPORT_H, paused)
        panel_rect = pygame.Rect(VIEWPORT_W, 0, panel_w, VIEWPORT_H)

        # draw minimap on panel
        draw_minimap(maze, player_pos, hunter_pos, goal, panel_rect, offset_x, offset_y, MAP_W_PIX, MAP_H_PIX)

        pygame.display.flip()
        clock.tick(30)

        # collision / win checks (positions in tile coords)
        if not paused:
            if tuple(player_pos) == tuple(hunter_pos): return "lose"
            if tuple(player_pos) == goal: return "win"
    return "exit"

# =================== MAIN ===================
while True:
    mode = main_menu()
    if mode == "exit": break
    loading_screen()
    while True:
        result = game_loop(mode)
        if result == "reset": continue
        elif result == "lose":
            choice = end_screen("lose")
            if choice == "retry": continue
            else: break
        elif result == "win":
            transition = transition_screen("Level Up!", (0,200,200))
            if transition == "next": continue
            else: break
        else:
            break

pygame.quit()