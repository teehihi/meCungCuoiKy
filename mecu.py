import pygame
import random
from collections import deque

# =================== SETUP ===================
CELL_SIZE = 32

pygame.init()
screen = None
pygame.display.set_caption("🎯 Maze Hunter with Assets")
clock = pygame.time.Clock()

hunter_speed = 5   # càng lớn thì hunter càng chậm
hunter_timer = 0

font = pygame.font.SysFont("Arial", 22)
big_font = pygame.font.SysFont("Arial", 48, bold=True)

# =================== LOAD ASSETS ===================
player_img = pygame.transform.scale(pygame.image.load("assets/player.png"), (CELL_SIZE, CELL_SIZE))
enemy_img = pygame.transform.scale(pygame.image.load("assets/enemy.png"), (CELL_SIZE, CELL_SIZE))
wall_img = pygame.transform.scale(pygame.image.load("assets/wall.png"), (CELL_SIZE, CELL_SIZE))
floor_img = pygame.transform.scale(pygame.image.load("assets/floor.jpg"), (CELL_SIZE, CELL_SIZE))
treasure_img = pygame.transform.scale(pygame.image.load("assets/treasure.jpg"), (CELL_SIZE, CELL_SIZE))

# =================== ĐỌC MÊ CUNG ===================
def load_maze(filename):
    maze = []
    with open(filename, "r") as f:
        for line in f:
            row = [int(ch) for ch in line.strip()]
            maze.append(row)
    return maze

map_files = ["maze1.txt", "maze2.txt", "maze3.txt"]

def random_map():
    chosen = random.choice(map_files)
    maze = load_maze(chosen)
    return maze, chosen

# =================== PATHFINDING ===================
def bfs(start, goal, maze):
    ROWS, COLS = len(maze), len(maze[0])
    q = deque([(start, [start])])
    visited = set()
    while q:
        (r, c), path = q.popleft()
        if (r, c) == goal:
            return path
        if (r, c) in visited:
            continue
        visited.add((r, c))
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0:
                q.append(((nr, nc), path + [(nr, nc)]))
    return []

# =================== VẼ ===================
def draw_maze(maze, goal):
    for r in range(len(maze)):
        for c in range(len(maze[0])):
            if maze[r][c] == 1:
                screen.blit(wall_img, (c * CELL_SIZE, r * CELL_SIZE))
            else:
                screen.blit(floor_img, (c * CELL_SIZE, r * CELL_SIZE))
    screen.blit(treasure_img, (goal[1] * CELL_SIZE, goal[0] * CELL_SIZE))

def draw_entity(pos, img):
    screen.blit(img, (pos[1] * CELL_SIZE, pos[0] * CELL_SIZE))

def draw_button(rect, text, color=(50, 50, 200)):
    pygame.draw.rect(screen, color, rect)
    label = font.render(text, True, (255, 255, 255))
    screen.blit(label, (rect.x + 10, rect.y + 5))

# =================== LOADING SCREEN ===================
def loading_screen():
    global screen
    screen = pygame.display.set_mode((600, 400))
    clock = pygame.time.Clock()
    progress = 0
    tips = [
        "💡 Mẹo: Hunter luôn dùng BFS để tìm bạn!",
        "💡 Mẹo: Dùng phím mũi tên để di chuyển.",
        "💡 Mẹo: Mỗi màn có bản đồ khác nhau.",
    ]

    tip_text = random.choice(tips)

    while True:
        screen.fill((20, 20, 20))

        title = font.render("🔄 Loading Maze Hunter...", True, (255, 255, 255))
        screen.blit(title, (120, 120))

        # Progress bar frame
        bar_w, bar_h = 400, 30
        bar_x, bar_y = 100, 200
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 2)

        # Progress bar fill
        pygame.draw.rect(screen, (0, 200, 0), (bar_x+2, bar_y+2, int(progress*(bar_w-4)), bar_h-4))

        # Hint text
        hint_label = font.render(tip_text, True, (200, 200, 200))
        screen.blit(hint_label, (120, 250))

        pygame.display.flip()
        clock.tick(60)

        progress += 0.01   # tốc độ load (≈ 4 giây)
        if progress >= 1:
            break

# =================== TRANSITION SCREEN ===================
def transition_screen(text, color=(0, 200, 0)):
    global screen
    screen.fill((0, 0, 0))
    label = big_font.render(text, True, color)
    screen.blit(label, (100, 150))

    info = font.render("Nhấn SPACE để tiếp tục...", True, (200, 200, 200))
    screen.blit(info, (120, 250))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
        clock.tick(30)
    return "next"

# =================== LOSE/WIN SCREEN ===================
def end_screen(result):
    global screen
    screen.fill((30, 30, 30))
    if result == "lose":
        label = big_font.render("💀 Bạn đã thua!", True, (200, 50, 50))
    else:
        label = big_font.render("🏆 Bạn đã thắng!", True, (50, 200, 50))

    screen.blit(label, (100, 150))

    retry_btn = pygame.Rect(120, 250, 120, 50)
    exit_btn = pygame.Rect(260, 250, 120, 50)

    draw_button(retry_btn, "Retry", (50, 150, 200))
    draw_button(exit_btn, "Exit", (200, 50, 50))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if retry_btn.collidepoint(event.pos):
                    return "retry"
                elif exit_btn.collidepoint(event.pos):
                    return "exit"
        clock.tick(30)

# =================== GAME LOOP ===================
def game_loop():
    global hunter_timer
    maze, chosen_map = random_map()
    ROWS, COLS = len(maze), len(maze[0])
    WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE + 60
    global screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    start = (0, 0)
    goal = (ROWS - 1, COLS - 1)
    player_pos = list(start)

    hunter_pos = [ROWS // 2, COLS // 2]
    if maze[hunter_pos[0]][hunter_pos[1]] == 1:
        for r in range(ROWS):
            for c in range(COLS):
                if maze[r][c] == 0:
                    hunter_pos = [r, c]
                    break

    running = True
    while running:
        screen.fill((0, 0, 0))
        draw_maze(maze, goal)
        draw_entity(player_pos, player_img)
        draw_entity(hunter_pos, enemy_img)

        pygame.display.flip()
        clock.tick(10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Player control
        keys = pygame.key.get_pressed()
        nr, nc = player_pos
        if keys[pygame.K_UP]: nr -= 1
        elif keys[pygame.K_DOWN]: nr += 1
        elif keys[pygame.K_LEFT]: nc -= 1
        elif keys[pygame.K_RIGHT]: nc += 1
        if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0:
            player_pos = [nr, nc]

        # Hunter AI
        hunter_timer += 1
        if hunter_timer >= hunter_speed:
            path = bfs(tuple(hunter_pos), tuple(player_pos), maze)
            if len(path) > 1:
                hunter_pos = list(path[1])
            hunter_timer = 0

        # Lose check
        if tuple(player_pos) == tuple(hunter_pos):
            return "lose"

        # Win check
        if tuple(player_pos) == goal:
            return "win"

    return "exit"

# =================== MAIN ===================
loading_screen()

while True:
    result = game_loop()

    if result == "lose":
        choice = end_screen("lose")
        if choice == "retry":
            continue
        else:
            break
    elif result == "win":
        transition = transition_screen("🎉 Level Up!", (0, 200, 200))
        if transition == "next":
            continue
        else:
            break
    else:  # exit
        break

pygame.quit()
