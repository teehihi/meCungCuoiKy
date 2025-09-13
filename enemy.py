import pygame
import os
import math
from constants import CELL_SIZE, hunter_speed, hunter_anim_speed, asset_path
from pathfinding import bfs, dfs
from utils import load_spritesheet_rows

# Tải animation của hunter
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
                if i < len(frames_by_row): return frames_by_row[i]
                return frames_by_row[0]
            enemy_animations = {
                "down": get_row(0), "up": get_row(1) if rows > 1 else get_row(0),
                "left": get_row(2) if rows > 2 else get_row(0), "right": get_row(3) if rows > 3 else get_row(0),
            }
            break
        except Exception:
            enemy_single = pygame.transform.scale(surf, (CELL_SIZE, CELL_SIZE))
            break
if enemy_animations is None:
    if enemy_single is None:
        try: enemy_single = pygame.transform.scale(pygame.image.load(asset_path("enemy.png")).convert_alpha(), (CELL_SIZE, CELL_SIZE))
        except Exception: enemy_single = None
    if enemy_single:
        enemy_animations = {"down": [enemy_single], "up": [enemy_single], "left": [enemy_single], "right": [enemy_single]}
    else:
        surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA); surf.fill((0,200,0))
        enemy_animations = {"down":[surf],"up":[surf],"left":[surf],"right":[surf]}

class Hunter:
    def __init__(self, start_pos):
        self.pos = list(start_pos)
        self.path = []
        self.direction = "down"
        self.frame_index = 0
        self.frame_timer = 0
        self.timer = 0

    def update(self, player_pos, maze, mode):
        self.timer += 1
        moved_hunter = False
        if self.timer >= hunter_speed:
            pathfinding_func = bfs if mode == "bfs" else dfs
            if not self.path or self.path[-1] != tuple(player_pos):
                self.path = pathfinding_func(tuple(self.pos), tuple(player_pos), maze)

            if len(self.path) > 1:
                prev = tuple(self.pos)
                nxt = self.path[1]
                dr = nxt[0] - prev[0]
                dc = nxt[1] - prev[1]
                
                if abs(dc) > abs(dr):
                    self.direction = "right" if dc > 0 else "left"
                else:
                    self.direction = "down" if dr > 0 else "up"

                self.pos = list(nxt)
                self.path = self.path[1:]
                moved_hunter = True
            
            self.timer = 0
        
        # Sửa lỗi: Gọi update_animation() mà không truyền tham số
        self.update_animation()
        
    def update_animation(self):
        """Cập nhật animation ngay cả khi không di chuyển."""
        # Tốc độ animation khi đứng im sẽ chậm hơn
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