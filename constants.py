import os

import pygame

# =================== SETUP ===================
CELL_SIZE = 80
hunter_speed = 12   # càng lớn => hunter càng chậm
player_speed = 2   # càng lớn => player animation càng chậm
hunter_anim_speed = 2   # càng lớn => hunter animation càng chậm
KEY_REPEAT_DELAY = 150  # milliseconds
KEY_REPEAT_INTERVAL = 50 # milliseconds
# ================= VIEW / MAP SIZES =================
VIEW_TILES_X = 16
VIEW_TILES_Y = 10
VIEWPORT_W = VIEW_TILES_X * CELL_SIZE
VIEWPORT_H = VIEW_TILES_Y * CELL_SIZE

MAP_COLS = 51  # nên là số lẻ
MAP_ROWS = 31  # nên là số lẻ

# Camera smoothing factor (0..1). Nhỏ hơn => mượt hơn / trễ hơn
CAMERA_LERP = 0.07

# BASE DIR + helper path
BASE_DIR = os.path.dirname(__file__)
def asset_path(filename):
    return os.path.join(BASE_DIR, "assets", filename)

# Các themes có sẵn
available_themes = ["sand", "snow", "water", "blue", "brown", "white", "yellow"]

# ================= PATH TILE =================
try:
    path_tile = pygame.image.load(asset_path("path.png")).convert_alpha()
    path_tile = pygame.transform.scale(path_tile, (CELL_SIZE, CELL_SIZE))
except Exception:
    # fallback nếu không có file path.png
    path_tile = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    path_tile.fill((0, 255, 255, 100))  # màu cyan trong suốt
