import pygame
import random
import time
import io
import contextlib
import pathfinding
from pathfinding import *

# =========================
# Cấu hình
# =========================
CELL_SIZE = 35
ROWS, COLS = 21, 25  # nên là số lẻ
FPS = 60
WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE

# =========================
# Màu sắc
# =========================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 150, 255)
GREY = (200, 200, 200)
YELLOW = (255, 255, 0)
PURPLE = (180, 0, 255)
LIGHT_BLUE = (0, 200, 255)
ORANGE = (255, 165, 0)

# =========================
# Khởi tạo Pygame (window)
# =========================
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🔍 Pathfinding Visualizer — 18 Algorithms")
font = pygame.font.SysFont("Segoe UI", 22)
clock = pygame.time.Clock()

# =========================
# Sinh mê cung ngẫu nhiên
# =========================
def generate_maze(width, height):
    if width % 2 == 0: width += 1
    if height % 2 == 0: height += 1
    maze = [[1 for _ in range(width)] for _ in range(height)]

    def carve(x, y):
        dirs = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 1 <= nx < width - 1 and 1 <= ny < height - 1 and maze[ny][nx] == 1:
                maze[y + dy // 2][x + dx // 2] = 0
                maze[ny][nx] = 0
                carve(nx, ny)

    maze[1][1] = 0
    carve(1, 1)
    add_loops(maze, 0.08)
    return maze

def add_loops(maze, chance=0.05):
    rows, cols = len(maze), len(maze[0])
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            if maze[r][c] == 1 and random.random() < chance:
                maze[r][c] = 0

# =========================
# Vẽ mê cung
# =========================
def draw_maze(maze, visited=set(), frontier=set(), path=set(), start=None, goal=None):
    screen.fill(WHITE)
    for r in range(len(maze)):
        for c in range(len(maze[0])):
            rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1)
            if maze[r][c] == 1:
                pygame.draw.rect(screen, BLACK, rect)
            elif (r, c) == start:
                pygame.draw.rect(screen, GREEN, rect)
            elif (r, c) == goal:
                pygame.draw.rect(screen, RED, rect)
            elif (r, c) in path:
                pygame.draw.rect(screen, BLUE, rect)
            elif (r, c) in frontier:
                pygame.draw.rect(screen, ORANGE, rect)
            elif (r, c) in visited:
                pygame.draw.rect(screen, LIGHT_BLUE, rect)
            else:
                pygame.draw.rect(screen, GREY, rect, 1)
    pygame.display.flip()

# =========================
# Chạy thuật toán có visualization
# =========================
def visualize_search(algo_func, maze, start, goal, delay=0.02):
    """Nếu hàm trong pathfinding có yield => visualize từng bước."""
    with contextlib.redirect_stdout(io.StringIO()):
        result = algo_func(start, goal, maze)

    if hasattr(result, "__iter__") and not isinstance(result, list):
        for step in result:
            visited = step.get("visited", set())
            frontier = step.get("frontier", set())
            path = step.get("path", set())
            draw_maze(maze, visited, frontier, path, start, goal)
            pygame.time.wait(int(delay * 1000))
    else:
        draw_maze(maze, path=set(result), start=start, goal=goal)

# =========================
# Danh sách thuật toán
# =========================
ALGORITHMS = [
    "BFS", "DFS", "UCS", "IDS", "Astar", "Greedy", "Hill Climbing",
    "Simulated Annealing", "Genetic", "Backtracking", "Forward Checking",
    "Minimax", "Alpha_Beta", "Minimax-Limited", "AC3", "POS",
    "AND_OR_Graph_Search", "Online DFS"
]

# =========================
# Menu chọn thuật toán
# =========================
def draw_menu(selected):
    screen.fill((30, 30, 30))
    title = font.render("Chọn thuật toán (↑/↓, Enter để chạy)", True, YELLOW)
    screen.blit(title, (30, 10))
    y = 60
    for i, algo in enumerate(ALGORITHMS):
        color = YELLOW if i == selected else WHITE
        text = font.render(algo, True, color)
        screen.blit(text, (50, y))
        y += 30
    pygame.display.flip()

# =========================
# Main Loop
# =========================
def main():
    maze = generate_maze(COLS, ROWS)
    start, goal = (1, 1), (ROWS - 2, COLS - 2)
    selected = 0
    running = True
    show_menu = True

    draw_maze(maze, start=start, goal=goal)

    while running:
        if show_menu:
            draw_menu(selected)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if show_menu:
                    if event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(ALGORITHMS)
                    elif event.key == pygame.K_UP:
                        selected = (selected - 1) % len(ALGORITHMS)
                    elif event.key == pygame.K_RETURN:
                        algo_name = ALGORITHMS[selected]
                        func_name = algo_name.lower().replace("-", "_").replace(" ", "_")
                        show_menu = False
                        print(f"▶ Running {algo_name} ...")
                        draw_maze(maze, start=start, goal=goal)
                        try:
                            if hasattr(pathfinding, func_name):
                                algo_func = getattr(pathfinding, func_name)
                                visualize_search(algo_func, maze, start, goal)
                        except KeyError:
                            print(f"[!] Thuật toán {algo_name} chưa có trong pathfinding.py")
                        except Exception as e:
                            print(f"[Lỗi khi chạy {algo_name}]: {e}")
                else:
                    if event.key == pygame.K_r:
                        maze = generate_maze(COLS, ROWS)
                        draw_maze(maze, start=start, goal=goal)
                    elif event.key == pygame.K_ESCAPE:
                        show_menu = True

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()

# =========================
# Run
# =========================
if __name__ == "__main__":
    main()
