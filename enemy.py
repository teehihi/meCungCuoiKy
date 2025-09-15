import pygame
import os
from collections import deque
from constants import CELL_SIZE, hunter_speed, hunter_anim_speed, asset_path
from pathfinding import bfs  # dùng bfs như connector ngắn
from utils import load_spritesheet_rows

# =================== Load animation (giữ nguyên) ===================
enemy_sheet_candidates = ["enemy_run.png", "enemy_sheet.png", "enemy.png"]
enemy_animations = None
enemy_single = None

for fname in enemy_sheet_candidates:
    path = asset_path(fname)
    if not os.path.exists(path):
        continue
    surf = pygame.image.load(path).convert_alpha()
    w, h = surf.get_size()
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
                "up": get_row(1) if rows > 1 else get_row(0),
                "left": get_row(2) if rows > 2 else get_row(0),
                "right": get_row(3) if rows > 3 else get_row(0),
            }
            break
        except Exception:
            enemy_single = pygame.transform.scale(surf, (CELL_SIZE, CELL_SIZE))
            break

if enemy_animations is None:
    if enemy_single is None:
        try:
            enemy_single = pygame.transform.scale(
                pygame.image.load(asset_path("enemy.png")).convert_alpha(),
                (CELL_SIZE, CELL_SIZE),
            )
        except Exception:
            enemy_single = None
    if enemy_single:
        enemy_animations = {
            "down": [enemy_single],
            "up": [enemy_single],
            "left": [enemy_single],
            "right": [enemy_single],
        }
    else:
        surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        surf.fill((0, 200, 0))
        enemy_animations = {
            "down": [surf],
            "up": [surf],
            "left": [surf],
            "right": [surf],
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
        # thứ tự duyệt: down, right, up, left (bạn có thể thay đổi để khác kết quả)
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
            # chuẩn hoá old_path: nếu old_path[0] != start mà start nằm trong old_path, cắt cho đúng
            if old_path[0] != start:
                if start in old_path:
                    idx = old_path.index(start)
                    old_path = old_path[idx:]
                else:
                    # không tương thích, bỏ old_path
                    old_path = None

        if old_path:
            # nếu goal chính là đích cũ
            if goal == old_path[-1]:
                return old_path

            # nếu goal nằm trên old_path (player đi ngược về đường cũ)
            if goal in old_path:
                idx = old_path.index(goal)
                return old_path[: idx + 1]

            # nếu goal kề đích cũ -> nối tail -> goal bằng bfs
            tail = old_path[-1]
            if abs(tail[0] - goal[0]) + abs(tail[1] - goal[1]) == 1:
                connector = bfs(tail, goal, maze)
                if connector:
                    return old_path + connector[1:]

            # thử nối từ một vài node cuối (backwards) bằng BFS nếu connector ngắn
            max_back = min(4, len(old_path))
            for back in range(1, max_back + 1):
                node = old_path[-back]
                connector = bfs(node, goal, maze)
                if connector and 1 < len(connector) <= 6:
                    idx = len(old_path) - back
                    return old_path[: idx + 1] + connector[1:]
    except Exception:
        # nếu có lỗi gì, fallback xuống dfs
        pass

    # fallback: tìm đường mặc định bằng DFS
    return dfs_local(start, goal, maze)


# =================== Hunter Class ===================
class Hunter:
    def __init__(self, start_pos):
        self.pos = list(start_pos)
        self.path = []  # list of (r,c) từ vị trí hiện tại đến target
        self.direction = "down"
        self.frame_index = 0
        self.frame_timer = 0
        self.timer = 0
        self.last_pos = None
        self.last_player_pos = None  # để biết player có đổi ô hay không

    def update(self, player_pos, maze, mode):
        """Cập nhật vị trí hunter để đuổi player."""
        self.timer += 1
        if self.timer >= hunter_speed:
            # chuẩn hoá player_pos / self.pos
            player_t = tuple(player_pos)
            start_t = tuple(self.pos)
            pathfinding_func = None

            if mode == "bfs":
                pathfinding_func = bfs
                # BFS: luôn tính lại (bởi BFS cho đường ngắn nhất)
                self.path = pathfinding_func(start_t, player_t, maze)
                self.last_player_pos = player_t
            else:
                # DFS mode: dùng dfs_adjusted với old_path nếu có
                # chuẩn hoá old_path: nếu self.path không bắt đầu tại self.pos mà self.pos nằm trong self.path thì cắt
                old_path = self.path if self.path else None
                if old_path:
                    if old_path[0] != start_t:
                        if start_t in old_path:
                            idx = old_path.index(start_t)
                            old_path = old_path[idx:]
                        else:
                            old_path = None

                # nếu player đã đổi ô so với last_player_pos -> cố gắng điều chỉnh đường cũ
                if self.last_player_pos is None or self.last_player_pos != player_t:
                    # gọi dfs_adjusted (nó tự quyết định dùng old_path hoặc dfs full)
                    self.path = dfs_adjusted(start_t, player_t, maze, old_path=old_path)
                    self.last_player_pos = player_t
                else:
                    # player không đổi ô: tiếp tục dùng path cũ (nếu có), nếu không có thì tính mới
                    if not self.path:
                        self.path = dfs_adjusted(start_t, player_t, maze, old_path=None)

            # Di chuyển 1 bước theo path nếu có >1 node
            if len(self.path) > 1:
                nxt = self.path[1]

                # tránh quay lại ô ngay trước đó
                if self.last_pos is not None and nxt == self.last_pos:
                    # nếu còn bước tiếp theo thì nhảy qua (bỏ qua) bước lùi
                    if len(self.path) > 2:
                        nxt = self.path[2]
                        # cập nhật path: bỏ 2 phần đầu
                        self.path = self.path[2:]
                    else:
                        # chỉ còn 1 bước -> tiến tới nó
                        nxt = self.path[1]
                        self.path = self.path[1:]
                else:
                    # bình thường: bỏ phần đầu (vì đã đi qua)
                    self.path = self.path[1:]

                self.last_pos = tuple(self.pos)

                # cập nhật hướng
                dr = nxt[0] - self.pos[0]
                dc = nxt[1] - self.pos[1]
                if abs(dc) > abs(dr):
                    self.direction = "right" if dc > 0 else "left"
                else:
                    self.direction = "down" if dr > 0 else "up"

                # di chuyển
                self.pos = list(nxt)

            self.timer = 0

        # cập nhật animation (luôn chạy)
        self.update_animation()

    def update_animation(self):
        """Cập nhật animation ngay cả khi không di chuyển."""
        animation_speed = hunter_anim_speed if len(self.path) > 1 else hunter_anim_speed * 6

        self.frame_timer += 1
        if self.frame_timer >= animation_speed:
            self.frame_index = (self.frame_index + 1) % len(enemy_animations[self.direction])
            self.frame_timer = 0

    def draw(self, screen, offset_x, offset_y):
        frames = enemy_animations.get(self.direction, enemy_animations["down"])
        img = frames[self.frame_index % len(frames)]
        x = self.pos[1] * CELL_SIZE - offset_x
        y = self.pos[0] * CELL_SIZE - offset_y
        screen.blit(img, (x, y))
