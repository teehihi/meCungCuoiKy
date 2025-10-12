# visualizer.py
import time
import pygame
from collections import deque
import pathfinding
import utils
from constants import CELL_SIZE, VIEWPORT_W, VIEWPORT_H

# === Mapping chế độ chơi -> tên hàm tương ứng trong pathfinding.py ===
MODE_TO_FUNC = {
    "bfs": "bfs",
    "dfs": "dfs",
    "greedy": "greedy",
    "astar": "astar",
    "ucs": "ucs",
    "ids": "ids",
    "hillclimbing": "hill_climbing",
    "sa": "simulated_annealing",
    "genetic": "genetic",
    "backtracking": "backtracking",
    "forwardchecking": "forward_checking",
    "ac3": "ac3",
    "and_or": "and_or_graph_search",
    "online": "online_dfs",
    "minimax": "minimax_maze",
    "alphabeta": "alpha_beta",
}

# === Hiệu ứng hiển thị ===
VIS_BG_ALPHA = 90
WAVE_BASE_COLOR = (40, 200, 160)
PATH_COLOR = (255, 220, 100)
START_COLOR = (255, 140, 0)
GOAL_COLOR = (255, 70, 70)
NUMBER_COLOR = (0, 0, 0)
NUMBER_BG_ALPHA = 200
ANIM_DELAY = 25

pygame.font.init()
_number_font = pygame.font.SysFont("Segoe UI", max(12, CELL_SIZE // 3), bold=True)
_continue_btn = None
_last_hunter = None


# === API để game truyền hunter vào ===
def register_hunter(hunter):
    global _last_hunter
    _last_hunter = hunter


def _to_tuple(pos):
    if pos is None:
        return None
    if isinstance(pos, (tuple, list)):
        return (int(pos[0]), int(pos[1]))
    return tuple(map(int, pos))


def _draw_overlay_cell(screen, cell, offset_x, offset_y, color, alpha=180):
    x = cell[1] * CELL_SIZE - offset_x
    y = cell[0] * CELL_SIZE - offset_y
    s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    r, g, b = [max(0, min(255, int(v))) for v in color]
    s.fill((r, g, b, max(0, min(255, int(alpha)))))
    screen.blit(s, (x, y))


def _draw_number(screen, cell, offset_x, offset_y, number):
    txt = str(number)
    surf = _number_font.render(txt, True, NUMBER_COLOR)
    bg = pygame.Surface((surf.get_width() + 6, surf.get_height() + 6), pygame.SRCALPHA)
    bg.fill((255, 255, 255, NUMBER_BG_ALPHA))
    x = int(cell[1] * CELL_SIZE - offset_x + CELL_SIZE / 2)
    y = int(cell[0] * CELL_SIZE - offset_y + CELL_SIZE / 2)
    screen.blit(bg, (x - bg.get_width() // 2, y - bg.get_height() // 2))
    screen.blit(surf, (x - surf.get_width() // 2, y - surf.get_height() // 2))


def _draw_path_highlight(screen, path, offset_x, offset_y):
    if not path:
        return
    for (r, c) in path:
        s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        s.fill((*PATH_COLOR, 160))
        screen.blit(s, (c * CELL_SIZE - offset_x, r * CELL_SIZE - offset_y))
    for i, (r, c) in enumerate(path):
        _draw_number(screen, (r, c), offset_x, offset_y, i)
    sr, sc = path[0]
    gr, gc = path[-1]
    pygame.draw.circle(screen, START_COLOR,
                       (int(sc * CELL_SIZE - offset_x + CELL_SIZE / 2),
                        int(sr * CELL_SIZE - offset_y + CELL_SIZE / 2)),
                       max(6, CELL_SIZE // 4))
    pygame.draw.circle(screen, GOAL_COLOR,
                       (int(gc * CELL_SIZE - offset_x + CELL_SIZE / 2),
                        int(gr * CELL_SIZE - offset_y + CELL_SIZE / 2)),
                       max(6, CELL_SIZE // 4))


def _draw_continue_button(screen):
    global _continue_btn
    panel_w = 160
    btn_w, btn_h = 120, 40
    x = VIEWPORT_W + (panel_w - btn_w) // 2
    y = VIEWPORT_H - 80
    rect = pygame.Rect(x, y, btn_w, btn_h)
    pygame.draw.rect(screen, (90, 170, 230), rect, border_radius=8)
    label = pygame.font.SysFont("Segoe UI", 20).render("Continue", True, (20, 20, 20))
    screen.blit(label,
                (rect.centerx - label.get_width() // 2,
                 rect.centery - label.get_height() // 2))
    _continue_btn = rect
    return rect


def visualize_path(maze, start, goal, mode, offset_x=0.0, offset_y=0.0, speed_ms=ANIM_DELAY):
    """
    Hiển thị hiệu ứng loang đúng kiểu duyệt thuật toán (dừng khi tới goal, không cần sửa pathfinding).
    """
    global _last_hunter
    import types
    start, goal = _to_tuple(start), _to_tuple(goal)
    if _last_hunter is not None:
        start = _to_tuple(_last_hunter.pos)

    screen = utils.screen
    clock = pygame.time.Clock()
    base_frame = screen.copy()

    func_name = MODE_TO_FUNC.get(mode.lower(), None)
    algo_func = getattr(pathfinding, func_name, None)
    explored = []

    # Monkey-patch print_maze_step để ghi lại các bước duyệt
    old_print = getattr(pathfinding, "print_maze_step", None)

    def record_print(maze, path=None, current=None, start=None, goal=None):
        if current and current not in explored:
            explored.append(current)
            # Dừng khi đến goal
            if goal and current == goal:
                raise StopIteration("Goal reached")

    pathfinding.print_maze_step = record_print

    result = []
    try:
        try:
            result = algo_func(start, goal, maze, visualize=True, delay=0)
        except TypeError:
            result = algo_func(start, goal, maze)
    except StopIteration:
        pass
    except Exception as e:
        print(f"[visualizer] {mode} error: {e}")
    finally:
        if old_print:
            pathfinding.print_maze_step = old_print

    if not explored:
        explored = [start]

    # --- Vẽ hiệu ứng ---
    running, step, finished = True, 0, False
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if finished and _continue_btn and _continue_btn.collidepoint(ev.pos):
                    running = False
                    break

        screen.blit(base_frame, (0, 0))
        dim = pygame.Surface((VIEWPORT_W + 160, VIEWPORT_H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, VIS_BG_ALPHA))
        screen.blit(dim, (0, 0))

        limit = min(step, len(explored))
        for i, cell in enumerate(explored[:limit]):
            color = (WAVE_BASE_COLOR[0],
                     WAVE_BASE_COLOR[1] - (i * 3 % 100),
                     WAVE_BASE_COLOR[2])
            alpha = 120 + int(80 * (i / max(1, len(explored))))
            _draw_overlay_cell(screen, cell, offset_x, offset_y, color, alpha)
            _draw_number(screen, cell, offset_x, offset_y, i)

        if finished and result:
            _draw_path_highlight(screen, result, offset_x, offset_y)

        if not finished:
            pct = int((limit / len(explored)) * 100)
            bar_x, bar_y = VIEWPORT_W + 20, 40
            pygame.draw.rect(screen, (50, 50, 50),
                             (bar_x, bar_y, 120, 40), border_radius=6)
            lbl = pygame.font.SysFont("Segoe UI", 16).render(
                f"{mode.upper()}... {pct}%", True, (230, 230, 230))
            screen.blit(lbl, (bar_x + 6, bar_y + 6))
        else:
            _draw_continue_button(screen)

        pygame.display.flip()

        if not finished:
            if step < len(explored):
                step += 1
                pygame.time.delay(speed_ms)
            else:
                finished = True
        clock.tick(60)

    return
