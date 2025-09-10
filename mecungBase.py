import pygame
import random
from collections import deque
from background import ScrollingBackground


# =================== SETUP ===================
CELL_SIZE = 32
pygame.init()
screen = None
pygame.display.set_caption("Maze Hunter with BFS & DFS")
clock = pygame.time.Clock()

import os
os.environ['SDL_VIDEO_CENTERED'] = '1'

hunter_speed = 5   # càng lớn thì hunter càng chậm
hunter_timer = 0

# =================== MENU ===================
font_path = "assets/font/Pixeboy.ttf"
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

    # Load background từ class riêng
    try:
        bg = ScrollingBackground("assets/background.png", 400, speed=1)
    except:
        bg = None

    while True:
        if bg:
            bg.draw(screen)

            # Thêm lớp overlay tối
            overlay = pygame.Surface((600, 400))
            overlay.set_alpha(120)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill((30, 30, 40))

        
        # --- Title ---
        title_text = "Maze Hunter"
        title_color = (255, 215, 0)  # vàng
        outline_color = (0, 0, 0)    # đen

        title = menu_font.render(title_text, True, title_color)
        screen.blit(title, (300 - title.get_width()//2, 80))

    
        # --- Buttons ---
        # Load font
        button_font = pygame.font.Font("assets/font/Pixeboy.ttf", 28)

        def draw_button(text, x, y, w, h, color, hover_color, text_color=(255,255,255)):
            rect = pygame.Rect(x, y, w, h)
            mouse_pos = pygame.mouse.get_pos()

            # Nếu chuột nằm trong nút thì đổi màu
            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, hover_color, rect, border_radius=10)
            else:
                pygame.draw.rect(screen, color, rect, border_radius=10)

            # Render chữ với font custom
            label = button_font.render(text, True, text_color)
            screen.blit(label, (x + (w - label.get_width()) // 2,
                                y + (h - label.get_height()) // 2))
            return rect


        bfs_btn = draw_button("Play BFS Mode", 180, 160, 240, 50, (70,130,180), (100,160,220))
        dfs_btn = draw_button("Play DFS Mode", 180, 220, 240, 50, (34,139,34), (60,179,60))
        exit_btn = draw_button("Exit",          180, 280, 240, 50, (178,34,34),(220,50,50))


        pygame.display.flip()

        # --- Sự kiện ---
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

# =================== LOAD ASSETS ===================
player_img = pygame.transform.scale(pygame.image.load("assets/player.png"), (CELL_SIZE, CELL_SIZE))
enemy_img = pygame.transform.scale(pygame.image.load("assets/enemy.png"), (CELL_SIZE, CELL_SIZE))
wall_img = pygame.transform.scale(pygame.image.load("assets/wall.png"), (CELL_SIZE, CELL_SIZE))
floor_img = pygame.transform.scale(pygame.image.load("assets/floor.jpg"), (CELL_SIZE, CELL_SIZE))
treasure_img = pygame.transform.scale(pygame.image.load("assets/treasure.jpg"), (CELL_SIZE, CELL_SIZE))

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

        # Duyệt theo thứ tự cố định (xuống, phải, lên, trái)
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
def draw_maze(maze, goal):
    for r in range(len(maze)):
        for c in range(len(maze[0])):
            if maze[r][c] == 1:
                screen.blit(wall_img, (c*CELL_SIZE, r*CELL_SIZE))
            else:
                screen.blit(floor_img, (c*CELL_SIZE, r*CELL_SIZE))
    screen.blit(treasure_img, (goal[1]*CELL_SIZE, goal[0]*CELL_SIZE))

def draw_entity(pos, img):
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

# =================== LOADING SCREEN ===================
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

# =================== TRANSITION SCREEN ===================
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

# =================== END SCREEN ===================
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
    hunter_path = []
    global hunter_timer
    hunter_timer += 1
    if hunter_timer >= hunter_speed:
        path = dfs(tuple(hunter_pos), tuple(player_pos), maze)
        if len(path) > 1:
            next_step = path[1]
            # tránh quay lại ô ngay trước
            if len(path) > 2 and tuple(path[1]) == tuple(player_pos):
                next_step = path[1]
            hunter_pos = list(next_step)
        hunter_timer = 0
    maze = generate_maze(21, 21)
    ROWS, COLS = len(maze), len(maze[0])
    WIDTH, HEIGHT = COLS*CELL_SIZE, ROWS*CELL_SIZE
    panel_w = 160
    global screen
    screen = pygame.display.set_mode((WIDTH + panel_w, HEIGHT))
    start, goal = (1,1), farthest_cell(maze, (1,1))
    player_pos = list(start)

    hunter_pos = [ROWS//2, COLS//2]
    if maze[hunter_pos[0]][hunter_pos[1]] == 1:
        for r in range(ROWS):
            for c in range(COLS):
                if maze[r][c]==0: hunter_pos=[r,c]; break

    path, running, paused = [], True, False
    while running:
        screen.fill((10,0,0))
        draw_maze(maze, goal)
        if path:
            color = (0,255,255) if mode=="bfs" else (255,128,0)
            draw_path(path, color)
        draw_entity(player_pos, player_img)
        draw_entity(hunter_pos, enemy_img)

        # bảng điều khiển bên phải
        buttons, panel_w = draw_control_panel(WIDTH, HEIGHT, paused)

        pygame.display.flip()
        clock.tick(10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if buttons["reset"].collidepoint(event.pos):
                    return "reset"
                elif "pause" in buttons and buttons["pause"].collidepoint(event.pos):
                    paused = True
                elif "continue" in buttons and buttons["continue"].collidepoint(event.pos):
                    paused = False
                elif buttons["surrender"].collidepoint(event.pos):
                    return "exit"

        if paused:
            continue  # dừng update logic khi pause

        # Player move
        keys = pygame.key.get_pressed()
        nr, nc = player_pos
        if keys[pygame.K_UP]: nr -= 1
        elif keys[pygame.K_DOWN]: nr += 1
        elif keys[pygame.K_LEFT]: nc -= 1
        elif keys[pygame.K_RIGHT]: nc += 1
        if 0<=nr<ROWS and 0<=nc<COLS and maze[nr][nc]==0:
            player_pos = [nr,nc]

        # Hunter AI
        hunter_timer += 1
        if hunter_timer >= hunter_speed:
            if not path or path[-1] != tuple(player_pos):
                if mode == "bfs":
                    path = bfs(tuple(hunter_pos), tuple(player_pos), maze)
                else:
                    path = dfs(tuple(hunter_pos), tuple(player_pos), maze)

            if len(path) > 1:
                hunter_pos = list(path[1])
                path = path[1:]  # bỏ bước đã đi

            hunter_timer = 0


        if tuple(player_pos)==tuple(hunter_pos): return "lose"
        if tuple(player_pos)==goal: return "win"
    return "exit"

# =================== MAIN ===================
while True:
    mode = main_menu()
    if mode == "exit": break
    loading_screen()
    while True:
        result = game_loop(mode)
        if result=="reset":
            continue
        elif result=="lose":
            choice=end_screen("lose")
            if choice=="retry": continue
            else: break
        elif result=="win":
            transition=transition_screen("Level Up!", (0,200,200))
            if transition=="next": continue
            else: break
        else: break

pygame.quit()
# =================== THE END ===================