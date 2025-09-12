import pygame
import random
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

hunter_speed = 5   # càng lớn => hunter càng chậm
hunter_timer = 0

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
    # assume frame size 64x64 as player; compute cols/rows from actual size
    cols = max(1, w // 64)
    rows = max(1, h // 64)
    # require at least 1 row; if rows >= 1 we'll try to extract rows
    if rows >= 1 and cols >= 1:
        try:
            rows_to_use = min(rows, 4)  # we only need up to 4 directional rows
            frames_by_row = load_spritesheet_rows(path, 64, 64, rows, cols)
            # map rows to directions: take first 4 rows (if less, duplicate row 0)
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
            # fallback to single image
            enemy_single = pygame.transform.scale(surf, (CELL_SIZE, CELL_SIZE))
            break

# If not found or failed, fallback to enemy.png single image
if enemy_animations is None:
    if enemy_single is None:
        # try load enemy.png as single
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
        # ultimate fallback: create a colored surface
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

available_themes = ["sand", "snow", "water", "blue", "brown", "white", "yellow", "ruin"]

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

def draw_path(path, color):
    for (r, c) in path:
        rect = pygame.Rect(c*CELL_SIZE+CELL_SIZE//4, r*CELL_SIZE+CELL_SIZE//4,
                           CELL_SIZE//2, CELL_SIZE//2)
        pygame.draw.rect(screen, color, rect)

# =================== VẼ ===================
wall_mapping = {}

def draw_maze(maze, goal):
    for r in range(len(maze)):
        for c in range(len(maze[0])):
            if maze[r][c] == 1:
                if (r, c) not in wall_mapping:
                    wall_mapping[(r, c)] = random.choice(ruin_images) if ruin_images else None
                screen.blit(bg_ruin_img, (c*CELL_SIZE, r*CELL_SIZE))
                if wall_mapping[(r, c)]:
                    screen.blit(wall_mapping[(r, c)], (c*CELL_SIZE, r*CELL_SIZE))
            else:
                screen.blit(floor_img, (c*CELL_SIZE, r*CELL_SIZE))
    screen.blit(treasure_img, (goal[1]*CELL_SIZE, goal[0]*CELL_SIZE))

def draw_entity(pos, img):
    screen.blit(img, (pos[1]*CELL_SIZE, pos[0]*CELL_SIZE))

def draw_player(pos, direction, index):
    frames = animations[direction]
    img = frames[index % len(frames)]
    screen.blit(img, (pos[1]*CELL_SIZE, pos[0]*CELL_SIZE))

def draw_button(rect, text, color=(50, 50, 200)):
    pygame.draw.rect(screen, color, rect, border_radius=10)
    label = font.render(text, True, (255, 255, 255))
    screen.blit(label, (rect.centerx - label.get_width()//2,
                        rect.centery - label.get_height()//2))

# =================== CONTROL PANEL ===================
def draw_control_panel(WIDTH, HEIGHT, paused):
    panel_w = 160
    panel_rect = pygame.Rect(WIDTH, 0, panel_w, HEIGHT)
    pygame.draw.rect(screen, (40, 40, 40), panel_rect)
    btn_w, btn_h, gap = 120, 50, 20
    x = WIDTH + 20
    y = 40
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

    # reset mapping mỗi màn
    wall_mapping = {}

    # chọn theme random mỗi level
    theme = random.choice(available_themes)
    ruin_images, bg_ruin_img = load_theme(theme)

    # hunter animation state (per-direction)
    hunter_dir = "down"
    hunter_frame_index = 0
    hunter_frame_timer = 0
    hunter_frame_speed = 1  # nhỏ hơn => frame change nhanh hơn

    maze = generate_maze(16, 10)
    ROWS, COLS = len(maze), len(maze[0])
    WIDTH, HEIGHT = COLS*CELL_SIZE, ROWS*CELL_SIZE
    panel_w = 160
    screen = pygame.display.set_mode((WIDTH + panel_w, HEIGHT))

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
    while running:
        screen.fill((10,0,0))
        draw_maze(maze, goal)

        if path:
            color = (0,255,255) if mode=="bfs" else (255,128,0)
            draw_path(path, color)

        # draw player
        draw_player(player_pos, player_dir, frame_index)

        # draw hunter using per-direction frames
        hunter_frames = enemy_animations.get(hunter_dir, enemy_animations["down"])
        hunter_img = hunter_frames[hunter_frame_index % len(hunter_frames)]
        draw_entity(hunter_pos, hunter_img)

        buttons, panel_w = draw_control_panel(WIDTH, HEIGHT, paused)
        pygame.display.flip()
        clock.tick(10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if buttons["reset"].collidepoint(event.pos): return "reset"
                elif "pause" in buttons and buttons["pause"].collidepoint(event.pos): paused = True
                elif "continue" in buttons and buttons["continue"].collidepoint(event.pos): paused = False
                elif buttons["surrender"].collidepoint(event.pos): return "exit"
        if paused: continue

        # ==== player input ====
        keys = pygame.key.get_pressed()
        nr, nc = player_pos
        moved = False
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

        # player animation
        if moved:
            frame_timer += 1
            if frame_timer >= 2:
                frame_index = (frame_index + 1) % len(animations[player_dir])
                frame_timer = 0
        else:
            frame_timer += 1
            if frame_timer >= 8:
                frame_index = (frame_index + 1) % len(animations[player_dir])
                frame_timer = 0

        # ==== hunter pathfinding & movement + animation ====
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
                if hunter_frame_timer >= hunter_frame_speed:
                    hunter_frame_index = (hunter_frame_index + 1) % len(enemy_animations[hunter_dir])
                    hunter_frame_timer = 0
            else:
                # idle: vẫn có thể lật chậm frame nếu muốn
                hunter_frame_timer += 1
                if hunter_frame_timer >= hunter_frame_speed * 6:
                    hunter_frame_index = (hunter_frame_index + 1) % len(enemy_animations[hunter_dir])
                    hunter_frame_timer = 0

            hunter_timer = 0

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
