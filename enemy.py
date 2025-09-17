import pygame
import os
from collections import deque
from constants import CELL_SIZE, hunter_speed, hunter_anim_speed, asset_path
from pathfinding import bfs  # dùng bfs như connector ngắn
from utils import load_spritesheet_rows

# =================== Load animation ===================
def load_enemy_sprites(theme_name):
    """
    Tải sprite cho Hunter dựa trên theme.
    Sẽ tìm file theo định dạng: 'enemy_run_<theme_name>.png'.
    Nếu không có, sẽ dùng sprite mặc định 'enemy_run.png'.
    """
    # Tạo danh sách các file có thể có
    sprite_file_candidates = [
        f"enemy_run_{theme_name}.png",
        "enemy_run.png",
        "enemy.png"
    ]

    for fname in sprite_file_candidates:
        path = asset_path(os.path.join("enemy", fname))
        if os.path.exists(path):
            try:
                surf = pygame.image.load(path).convert_alpha()
                w, h = surf.get_size()
                # Giả định spritesheet có các khung hình 64x64
                cols = max(1, w // 64)
                rows = max(1, h // 64)
                
                if rows >= 1 and cols >= 1:
                    frames_by_row = load_spritesheet_rows(path, 64, 64, rows, cols)
                    def get_row(i):
                        # Đảm bảo index hợp lệ, nếu không trả về hàng đầu tiên
                        return frames_by_row[i] if i < len(frames_by_row) else frames_by_row[0]
                    return {
                        "down": get_row(0),
                        "up": get_row(1) if rows > 1 else get_row(0),
                        "left": get_row(2) if rows > 2 else get_row(0),
                        "right": get_row(3) if rows > 3 else get_row(0),
                    }
            except Exception as e:
                print(f"Lỗi khi tải sprite {path}: {e}")
                continue # Thử file tiếp theo

    # Fallback cuối cùng nếu không tìm thấy bất kỳ file nào
    default_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    default_surf.fill((0, 200, 0)) # Màu xanh lá cây mặc định
    return {
        "down": [default_surf],
        "up": [default_surf],
        "left": [default_surf],
        "right": [default_surf],
    }

# =================== DFS local (không dùng MAP_* ) ===================
def dfs_local(start, goal, maze):
    """DFS dùng stack, trả về path từ start->goal (list of (r,c))."""
    ROWS, COLS = len(maze), len(maze[0])
    stack = [(start, [start])]
    visited = set()

    while stack:
        current, path = stack.pop()
        if current == goal:
            return path
        if current in visited:
            continue
        visited.add(current)
        r, c = current
        for dr, dc in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0:
                if (nr, nc) not in visited:
                    stack.append(((nr, nc), path + [(nr, nc)]))
    return []

# =================== DFS adjusted ===================
def dfs_adjusted(start, goal, maze, old_path=None):
    """
    Nếu có old_path (từ start tới old_goal), cố gắng điều chỉnh:
    - Nếu goal == old_path[-1]: trả old_path.
    - Nếu goal kề (adjacent) old_path[-1]: nối bằng bfs tail->goal.
    - Nếu goal nằm trên old_path: cắt path tới goal.
    - Nếu tìm được connector ngắn từ 1 node cuối của old_path -> goal (dài <= 4), nối.
    Nếu các cách trên không tìm được, fallback sang dfs_local full.
    """
    try:
        if old_path:
            if old_path[0] != start:
                if start in old_path:
                    idx = old_path.index(start)
                    old_path = old_path[idx:]
                else:
                    old_path = None

        if old_path:
            if goal == old_path[-1]:
                return old_path
            if goal in old_path:
                idx = old_path.index(goal)
                return old_path[: idx + 1]
            tail = old_path[-1]
            if abs(tail[0] - goal[0]) + abs(tail[1] - goal[1]) == 1:
                connector = bfs(tail, goal, maze)
                if connector:
                    return old_path + connector[1:]
            max_back = min(4, len(old_path))
            for back in range(1, max_back + 1):
                node = old_path[-back]
                connector = bfs(node, goal, maze)
                if connector and 1 < len(connector) <= 6:
                    idx = len(old_path) - back
                    return old_path[: idx + 1] + connector[1:]
    except Exception:
        pass
    return dfs_local(start, goal, maze)

# =================== Hunter Class (Đã chỉnh sửa) ===================
class Hunter:
    def __init__(self, start_pos, theme):
        self.pos = list(start_pos)
        self.path = []
        self.direction = "down"
        self.frame_index = 0
        self.frame_timer = 0
        self.timer = 0
        self.last_pos = None
        self.last_player_pos = None
        self.theme = theme
        self.animations = load_enemy_sprites(self.theme)

    def update(self, player_pos, maze, mode, theme=None):
        if theme and theme != self.theme:
            self.theme = theme
            self.animations = load_enemy_sprites(self.theme)

        self.timer += 1
        if self.timer >= hunter_speed:
            player_t = tuple(player_pos)
            start_t = tuple(self.pos)
            pathfinding_func = None
            if mode == "bfs":
                pathfinding_func = bfs
                self.path = pathfinding_func(start_t, player_t, maze)
                self.last_player_pos = player_t
            else:
                old_path = self.path if self.path else None
                if old_path:
                    if old_path[0] != start_t:
                        if start_t in old_path:
                            idx = old_path.index(start_t)
                            old_path = old_path[idx:]
                        else:
                            old_path = None
                if self.last_player_pos is None or self.last_player_pos != player_t:
                    self.path = dfs_adjusted(start_t, player_t, maze, old_path=old_path)
                    self.last_player_pos = player_t
                else:
                    if not self.path:
                        self.path = dfs_adjusted(start_t, player_t, maze, old_path=None)
            if len(self.path) > 1:
                nxt = self.path[1]
                if self.last_pos is not None and nxt == self.last_pos:
                    if len(self.path) > 2:
                        nxt = self.path[2]
                        self.path = self.path[2:]
                    else:
                        nxt = self.path[1]
                        self.path = self.path[1:]
                else:
                    self.path = self.path[1:]
                self.last_pos = tuple(self.pos)
                dr = nxt[0] - self.pos[0]
                dc = nxt[1] - self.pos[1]
                if abs(dc) > abs(dr):
                    self.direction = "right" if dc > 0 else "left"
                else:
                    self.direction = "down" if dr > 0 else "up"
                self.pos = list(nxt)
            self.timer = 0
        self.update_animation()

    def update_animation(self):
        animation_speed = hunter_anim_speed if len(self.path) > 1 else hunter_anim_speed * 6
        self.frame_timer += 1
        if self.frame_timer >= animation_speed:
            self.frame_index = (self.frame_index + 1) % len(self.animations[self.direction])
            self.frame_timer = 0

    def draw(self, screen, offset_x, offset_y):
        frames = self.animations.get(self.direction, self.animations["down"])
        img = frames[self.frame_index % len(frames)]
        x = self.pos[1] * CELL_SIZE - offset_x
        y = self.pos[0] * CELL_SIZE - offset_y
        screen.blit(img, (x, y))