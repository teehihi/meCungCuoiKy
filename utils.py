import pygame, os, random, math
from pathfinding import *
from collections import deque
from constants import (
    CELL_SIZE, VIEWPORT_W, VIEWPORT_H, MAP_COLS, MAP_ROWS,
    asset_path
)
from PIL import Image, ImageFilter
import numpy as np
from io import BytesIO

from background import ScrollingBackground
from constants import CELL_SIZE, VIEWPORT_W, VIEWPORT_H, path_tile

# Khởi tạo Pygame và màn hình ban đầu
pygame.init()
pygame.mixer.init()
pygame.display.set_caption("Maze Hunter")
os.environ['SDL_VIDEO_CENTERED'] = '1'
screen = pygame.display.set_mode((1, 1))

# Tải fonts và hình ảnh chung
font_path = asset_path("font/Pixeboy.ttf")
font = pygame.font.SysFont("Segoe UI", 22)
big_font = pygame.font.SysFont("Segoe UI", 48)
menu_font = pygame.font.Font(font_path, 80)
treasure_img = pygame.transform.scale(pygame.image.load(asset_path("treasure.png")).convert_alpha(), (CELL_SIZE, CELL_SIZE))
clock = pygame.time.Clock()
path_tile = pygame.image.load(asset_path("path.png")).convert_alpha()
path_tile = pygame.transform.scale(path_tile, (CELL_SIZE, CELL_SIZE))

# --- KHAI BÁO BIẾN LƯU FRAME ANIMATION ---
animated_coin_frames = []
animated_key_frames = []
animated_coin_icon_frames = []
animated_key_icon_frames = []

# ----------------------------
# 🧩 HÀM HỖ TRỢ CẮT VIỀN TRONG SUỐT
# ----------------------------
def crop_transparent_borders(surface):
    """Tự động cắt vùng trong suốt xung quanh hình bằng Pillow."""
    try:
        width, height = surface.get_size()
        raw_str = pygame.image.tostring(surface, "RGBA", False)
        pil_img = Image.frombytes("RGBA", (width, height), raw_str)
        bbox = pil_img.getbbox()
        if bbox:
            pil_cropped = pil_img.crop(bbox)
            cropped_str = pil_cropped.tobytes("raw", "RGBA")
            cropped_surf = pygame.image.fromstring(cropped_str, pil_cropped.size, "RGBA")
            return cropped_surf
        return surface
    except Exception as e:
        print(f"⚠️ Error cropping transparent borders: {e}")
        return surface

# --- HÀM HỖ TRỢ CĂN CHỈNH SPRITE ---
def create_centered_surface(source_surface, scale_factor=0.9, nudge=(0, 0)):
    """
    Tạo một surface mới bằng CELL_SIZE, chứa source_surface đã được scale và căn giữa.
    Thêm tham số 'nudge' để tinh chỉnh vị trí.
    """
    pixel_size = int(CELL_SIZE * scale_factor)
    
    original_w, original_h = source_surface.get_size()
    if original_w > original_h:
        new_w = pixel_size
        new_h = int(original_h * (new_w / original_w))
    else:
        new_h = pixel_size
        new_w = int(original_w * (new_h / original_h))

    scaled_image = pygame.transform.scale(source_surface, (new_w, new_h))
    
    container = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    
    x_offset = (CELL_SIZE - new_w) // 2 + nudge[0]
    y_offset = (CELL_SIZE - new_h) // 2 + nudge[1]
    
    container.blit(scaled_image, (x_offset, y_offset))
    return container

# ----------------------------
# CÁC HÀM TẢI SPRITE
# ----------------------------
def load_spritesheet_rows(path, frame_width, frame_height, rows, cols, crop_margin=8):
    try:
        sheet = pygame.image.load(path).convert_alpha()
        frames_by_row = []
        
        for r in range(rows):
            row_frames = []
            for c in range(cols):
                rect = pygame.Rect(c * frame_width, r * frame_height, frame_width, frame_height)
                frame = sheet.subsurface(rect).copy()
                
                cropped_frame = crop_transparent_borders(frame)
                centered_frame = create_centered_surface(cropped_frame, scale_factor=0.8)
                row_frames.append(centered_frame)
            frames_by_row.append(row_frames)
        return frames_by_row
    except Exception as e:
        print(f"⚠️ Error loading spritesheet {path}: {e}")
        return []

def load_spritesheet_flat(path, frame_width, frame_height, rows, cols, spacing_x=0):
    """Nâng cấp: Thêm spacing_x để xử lý khoảng trống giữa các frame."""
    try:
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        for r in range(rows):
            for c in range(cols):
                x = c * (frame_width + spacing_x)
                y = r * frame_height
                rect = pygame.Rect(x, y, frame_width, frame_height)
                frame = sheet.subsurface(rect).copy()
                frames.append(frame)
        return frames
    except Exception as e:
        print(f"⚠️ Error loading flat spritesheet {path}: {e}")
        return []

# ----------------------------
# 🪙 LOAD ANIMATION COIN + KEY
# ----------------------------
def load_equal_frames(sheet_path, num_frames, scale_factor):
    """Tự động chia sprite sheet thành num_frames khung bằng nhau"""
    full_path = asset_path(sheet_path)
    try:
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Sprite sheet not found at {full_path}")
        sheet = pygame.image.load(full_path).convert_alpha()
        sheet_w, sheet_h = sheet.get_size()
        frame_w = sheet_w // num_frames
        if frame_w == 0:
            raise ValueError(f"Invalid sprite sheet width {sheet_w} for {num_frames} frames")
        frame_h = sheet_h  # 1 hàng
        frames = []
        for i in range(num_frames):
            rect = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
            frame = sheet.subsurface(rect).copy()
            frame_centered = create_centered_surface(frame, scale_factor=scale_factor)
            frames.append(frame_centered)
        print(f"✅ Successfully loaded {num_frames} frames from {sheet_path}")
        return frames
    except Exception as e:
        print(f"⚠️ Error loading sprite sheet {full_path}: {e}")
        return []

def load_coin_sprites(theme="default"):
    """Load animation frames cho đồng xu. Nếu theme == 'conan' (case-insensitive) sẽ dùng aptx_anim.png."""
    global animated_coin_frames, animated_coin_icon_frames
    ICON_SIZE = 24
    try:
        sheet_name = "aptx_anim.png" if str(theme).lower() == "conan" else "coin_anim.png"
        print(f"[utils] Loading coin spritesheet: {sheet_name}")
        animated_coin_frames = load_equal_frames(sheet_name, num_frames=8, scale_factor=0.75)
        if not animated_coin_frames:
            raise Exception(f"No frames loaded from {sheet_name}")
        animated_coin_icon_frames = [
            pygame.transform.smoothscale(f, (ICON_SIZE, ICON_SIZE)) for f in animated_coin_frames
        ]
        print(f"✅ Coin sprites loaded ({sheet_name})")
    except Exception as e:
        print(f"⚠️ Error loading coin sprites ({theme}): {e}")
        # Fallback placeholder (vẫn đảm bảo có ICON_SIZE)
        placeholder = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(placeholder, (212, 175, 55), (CELL_SIZE // 2, CELL_SIZE // 2), CELL_SIZE // 2)
        animated_coin_frames = [placeholder] * 8
        animated_coin_icon_frames = [
            pygame.transform.smoothscale(placeholder, (ICON_SIZE, ICON_SIZE)) for _ in range(8)
        ]


def load_key_sprites(theme="default"):
    """Load animation frames cho key/quiz item. Nếu theme == 'conan' sẽ dùng find_anim.png."""
    global animated_key_frames, animated_key_icon_frames
    ICON_SIZE = 24
    try:
        sheet_name = "find_anim.png" if str(theme).lower() == "conan" else "key_anim.png"
        print(f"[utils] Loading key spritesheet: {sheet_name}")
        animated_key_frames = load_equal_frames(sheet_name, num_frames=8, scale_factor=0.8)
        if not animated_key_frames:
            raise Exception(f"No frames loaded from {sheet_name}")
        animated_key_icon_frames = [
            pygame.transform.smoothscale(f, (ICON_SIZE, ICON_SIZE)) for f in animated_key_frames
        ]
        print(f"✅ Key sprites loaded ({sheet_name})")
    except Exception as e:
        print(f"⚠️ Error loading key sprites ({theme}): {e}")
        # Fallback placeholder
        placeholder = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(placeholder, (200, 200, 0), (CELL_SIZE // 4, CELL_SIZE // 4, CELL_SIZE // 2, CELL_SIZE // 2))
        animated_key_frames = [placeholder] * 8
        animated_key_icon_frames = [
            pygame.transform.smoothscale(placeholder, (ICON_SIZE, ICON_SIZE)) for _ in range(8)
        ]

# ----------------------------
# LOAD THEME
# ----------------------------
def load_theme(theme_name):
    theme_dir = os.path.join(asset_path("ruin"), theme_name)
    wall_images = []
    if os.path.isdir(theme_dir):
        for fname in os.listdir(theme_dir):
            if fname.lower().endswith((".png", ".jpg")) and not fname.startswith("bg_"):
                img = pygame.image.load(os.path.join(theme_dir, fname)).convert_alpha()
                cropped_img = crop_transparent_borders(img)
                centered_img = create_centered_surface(cropped_img, scale_factor=0.95)
                wall_images.append(centered_img)

    bg_path = os.path.join(theme_dir, f"bg_{theme_name}.png")
    if os.path.exists(bg_path):
        bg_img = pygame.transform.scale(pygame.image.load(bg_path).convert(), (CELL_SIZE, CELL_SIZE))
    else:
        default_bg_path = os.path.join(asset_path("ruin"), "bg_ruin.png")
        if os.path.exists(default_bg_path):
            bg_img = pygame.transform.scale(pygame.image.load(default_bg_path).convert(), (CELL_SIZE, CELL_SIZE))
        else:
            bg_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
            bg_img.fill((50, 50, 50))
    
    road_path = asset_path(f"road/road_{theme_name}.png")
    if not os.path.exists(road_path):
        road_path = asset_path("road/road_white.png")
        
    road_img = pygame.transform.scale(pygame.image.load(road_path).convert(), (CELL_SIZE, CELL_SIZE))
    
    # Load coin and key sprites for the theme
    load_coin_sprites(theme=theme_name)
    load_key_sprites(theme=theme_name)
    
    return wall_images, bg_img, road_img
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

def clamp(v, a, b):
    return max(a, min(b, v))

button_font = pygame.font.Font(font_path, 22)

def draw_button(rect, text, color):
    pygame.draw.rect(screen, color, rect, border_radius=10)
    label = button_font.render(text, True, (255, 255, 255))
    screen.blit(label, (rect.centerx - label.get_width() // 2,
                        rect.centery - label.get_height() // 2))

def draw_maze(maze, goal, offset_x, offset_y, wall_mapping, ruin_images, bg_ruin_img, floor_img):
    rows, cols = len(maze), len(maze[0])
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
    tr_x = goal[1]*CELL_SIZE - offset_x
    tr_y = goal[0]*CELL_SIZE - offset_y
    if -CELL_SIZE <= tr_x <= VIEWPORT_W and -CELL_SIZE <= tr_y <= VIEWPORT_H:
        screen.blit(treasure_img, (tr_x, tr_y))

def draw_entity(pos, img, offset_x, offset_y):
    x = pos[1]*CELL_SIZE - offset_x
    y = pos[0]*CELL_SIZE - offset_y
    screen.blit(img, (x, y))

def draw_player(pos, direction, index, offset_x, offset_y, animations):
    frames = animations[direction]
    img = frames[index % len(frames)]
    x = pos[1]*CELL_SIZE - offset_x
    y = pos[0]*CELL_SIZE - offset_y
    screen.blit(img, (x, y))

def draw_path(screen, path, offset_x, offset_y):
    if not path: 
        return
    for (r, c) in path:
        x = c * CELL_SIZE - offset_x
        y = r * CELL_SIZE - offset_y
        screen.blit(path_tile, (x, y))

control_font = pygame.font.Font(font_path, 22) 

def draw_control_panel(view_w, view_h, paused, mode_name="", coins=0, keys=0, lives=5):
    panel_w = 160
    panel_rect = pygame.Rect(view_w, 0, panel_w, view_h)
    pygame.draw.rect(screen, (40, 40, 40), panel_rect)

    if mode_name:
        max_width = panel_w - 20
        display_name = mode_name
        while control_font.render(f"Mode: {display_name}", True, (255, 215, 0)).get_width() > max_width:
            display_name = display_name[:-1]
        if len(display_name) < len(mode_name):
            display_name = display_name[:-3] + "..."
        text_surface = control_font.render(f"Mode: {display_name}", True, (255, 215, 0))
        screen.blit(text_surface, (view_w + 10, view_h - text_surface.get_height() - 20))

    minimap_bottom = 140
    y = minimap_bottom + 20
    x = view_w + 20
    
    ITEM_GAP = 40 
    icon_size = 28

    num_frames = len(animated_coin_icon_frames) if animated_coin_icon_frames else 1
    anim_speed_ms = 150
    current_frame_index = (pygame.time.get_ticks() // anim_speed_ms) % num_frames

    padding = 10
    frame_w = panel_w - 20 
    frame_h = 130 
    frame_x, frame_y = view_w + 10, y - padding
    pygame.draw.rect(screen, (30, 30, 30), (frame_x, frame_y, frame_w, frame_h), border_radius=8)
    pygame.draw.rect(screen, (80, 80, 80), (frame_x, frame_y, frame_w, frame_h), 2, border_radius=8)

    lx, ly = x, y

    try:
        life_icon_surf = pygame.transform.scale(
            pygame.image.load(asset_path("heart.png")).convert_alpha(), (icon_size, icon_size)
        )
        life_icon_rect = life_icon_surf.get_rect(topleft=(lx, ly))
        screen.blit(life_icon_surf, life_icon_rect)
    except Exception:
        life_icon_rect = pygame.Rect(lx, ly, icon_size, icon_size)
        pygame.draw.circle(screen, (200, 50, 50), life_icon_rect.center, icon_size//2)
    
    life_txt_surf = font.render(f"x {lives}", True, (255, 255, 255))
    life_txt_rect = life_txt_surf.get_rect(left = life_icon_rect.right + 8, centery = life_icon_rect.centery)
    screen.blit(life_txt_surf, life_txt_rect)

    cy = ly + ITEM_GAP
    coin_icon_rect = pygame.Rect(x, cy, icon_size, icon_size)
    if animated_coin_icon_frames:
        current_coin_frame = animated_coin_icon_frames[current_frame_index]
        screen.blit(current_coin_frame, coin_icon_rect.topleft)
    else:
        pygame.draw.circle(screen, (212, 175, 55), coin_icon_rect.center, icon_size//2)

    coin_txt_surf = font.render(f"x {coins}", True, (255, 255, 255))
    coin_txt_rect = coin_txt_surf.get_rect(left = coin_icon_rect.right + 8, centery = coin_icon_rect.centery)
    screen.blit(coin_txt_surf, coin_txt_rect)

    ky = cy + ITEM_GAP
    key_icon_rect = pygame.Rect(x, ky, icon_size, icon_size)
    if animated_key_icon_frames:
        current_key_frame = animated_key_icon_frames[current_frame_index]
        screen.blit(current_key_frame, key_icon_rect.topleft)
    else:
        pygame.draw.rect(screen, (200, 200, 0), (x, ky + icon_size//4, icon_size, icon_size//2))

    key_txt_surf = font.render(f"x {keys}", True, (255, 255, 255))
    key_txt_rect = key_txt_surf.get_rect(left = key_icon_rect.right + 8, centery = key_icon_rect.centery)
    screen.blit(key_txt_surf, key_txt_rect)

    y = frame_y + frame_h + 20
    btn_w, btn_h, gap = 120, 50, 20
    x = view_w + (panel_w - btn_w) // 2
    buttons = {}
    if not paused:
        pause_btn = pygame.Rect(x, y, btn_w, btn_h)
        draw_control_button(pause_btn, "Pause", (80, 80, 200))
        buttons["pause"] = pause_btn
    else:
        cont_btn = pygame.Rect(x, y, btn_w, btn_h)
        draw_control_button(cont_btn, "Continue", (50, 180, 100))
        buttons["continue"] = cont_btn
    y += btn_h + gap
    reset_btn = pygame.Rect(x, y, btn_w, btn_h)
    draw_control_button(reset_btn, "Reset", (200, 150, 50))
    buttons["reset"] = reset_btn
    y += btn_h + gap
    surrender_btn = pygame.Rect(x, y, btn_w, btn_h)
    draw_control_button(surrender_btn, "Surrender", (200, 60, 60))
    buttons["surrender"] = surrender_btn

        # === Visualize Path (chỉ hiện khi pause) ===
    if paused:
        y += btn_h + gap
        visualize_btn = pygame.Rect(x, y, btn_w, btn_h)
        draw_control_button(visualize_btn, "Visualize", (100, 180, 250))
        buttons["visualize"] = visualize_btn

    return buttons, panel_w

def get_control_buttons(paused):
    btn_w, btn_h, gap = 120, 50, 20
    x = VIEWPORT_W + 20
    y = 300
    buttons = {}
    if not paused:
        buttons["pause"] = pygame.Rect(x, y, btn_w, btn_h)
    else:
        buttons["continue"] = pygame.Rect(x, y, btn_w, btn_h)
    y += btn_h + gap
    buttons["reset"] = pygame.Rect(x, y, btn_w, btn_h)
    y += btn_h + gap
    buttons["surrender"] = pygame.Rect(x, y, btn_w, btn_h)
    if paused:
        y += btn_h + gap
        buttons["visualize"] = pygame.Rect(x, y, btn_w, btn_h)
    return buttons

def draw_control_button(rect, text, color):
    pygame.draw.rect(screen, color, rect, border_radius=10)
    label = control_font.render(text, True, (255, 255, 255))
    screen.blit(label, (rect.centerx - label.get_width() // 2,
                        rect.centery - label.get_height() // 2))

def loading_screen():
    screen = pygame.display.set_mode((600, 400))
    title_font = pygame.font.Font(font_path, 40)  
    tip_font = pygame.font.SysFont("segoeui", 22, bold = True)
    bar_font = pygame.font.SysFont("segoeui", 20)
    bg_img = pygame.image.load(asset_path("background.png")).convert()
    bg_width, bg_height = bg_img.get_size()
    scale_factor = 400 / bg_height
    bg_width_scaled = int(bg_width * scale_factor)
    bg_img = pygame.transform.scale(bg_img, (bg_width_scaled, 400))
    scroll_x = 0
    speed = 0.3
    progress = 0
    tip_text = random.choice([
        "Mẹo: Hunter luôn đuổi theo bạn!",
        "Mẹo: Dùng phím mũi tên để di chuyển.",
        "Mỗi màn có bản đồ khác nhau.",
    ])
    running = True
    while running:
        scroll_x -= speed
        if scroll_x <= -bg_width_scaled:
            scroll_x = 0
        screen.blit(bg_img, (scroll_x, 0))
        screen.blit(bg_img, (scroll_x + bg_width_scaled, 0))
        overlay = pygame.Surface((600, 400))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        title = title_font.render("Loading Maze Hunter...", True, (255, 215, 0))
        screen.blit(title, (300 - title.get_width() // 2, 100))
        bar_w, bar_h, bar_x, bar_y = 400, 30, 100, 200
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 3)
        pygame.draw.rect(
            screen, (50, 255, 120),
            (bar_x + 3, bar_y + 3, int(progress * (bar_w - 6)), bar_h - 6)
        )
        bar_label = bar_font.render(f"{int(progress*100)}%", True, (255, 255, 0))
        screen.blit(bar_label, (300 - bar_label.get_width() // 2, bar_y + bar_h + 10))
        hint = tip_font.render(tip_text, True, (255, 220, 100))
        screen.blit(hint, (300 - hint.get_width() // 2, 280))
        pygame.display.flip()
        clock.tick(60)
        progress += 0.006
        if progress >= 1:
            running = False

def transition_screen(text, color=(255, 215, 0)):
    screen_w, screen_h = screen.get_size()
    title_font = pygame.font.Font(font_path, 48)
    info_font = pygame.font.SysFont("segoeui", 22)
    bg_img = pygame.image.load(asset_path("background.png")).convert()
    bg_width, bg_height = bg_img.get_size()
    scale_factor = screen_h / bg_height
    bg_width_scaled = int(bg_width * scale_factor)
    bg_img = pygame.transform.scale(bg_img, (bg_width_scaled, screen_h))
    scroll_x, speed, alpha = 0, 0.6, 0
    panel_w, panel_h = 400, 200
    panel_x, panel_y = (screen_w - panel_w) // 2, (screen_h - panel_h) // 2
    waiting = True
    while waiting:
        scroll_x -= speed
        if scroll_x <= -bg_width_scaled:
            scroll_x = 0
        screen.blit(bg_img, (scroll_x, 0))
        screen.blit(bg_img, (scroll_x + bg_width_scaled, 0))
        overlay = pygame.Surface((screen_w, screen_h))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (30, 30, 40, alpha), panel.get_rect(), border_radius=15)
        pygame.draw.rect(panel, (200, 200, 200, alpha), panel.get_rect(), 3, border_radius=15)
        screen.blit(panel, (panel_x, panel_y))
        if alpha > 150:
            label = title_font.render(text, True, color)
            label_rect = label.get_rect(center=(screen_w // 2, panel_y + 70))
            screen.blit(label, label_rect)
            info = info_font.render("Nhấn SPACE để tiếp tục...", True, (220,220,220))
            info_rect = info.get_rect(center=(screen_w // 2, panel_y + panel_h - 40))
            screen.blit(info, info_rect)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "exit"
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and alpha >= 180: waiting = False
        if alpha < 220: alpha += 5
        clock.tick(60)
    return "next"

def blur_surface(surface, radius=5):
    arr = pygame.surfarray.array3d(surface)
    img = Image.fromarray(np.transpose(arr, (1, 0, 2)))
    img = img.filter(ImageFilter.GaussianBlur(radius=radius))
    arr = np.transpose(np.array(img), (1, 0, 2))
    return pygame.surfarray.make_surface(arr)

def end_screen(result):
    global screen, clock, big_font
    screen_w, screen_h = screen.get_size()
    snapshot = screen.copy()
    blurred = blur_surface(snapshot, radius=8)
    screen.blit(blurred, (0, 0))
    text = "GAME OVER" if result == "lose" else "Bạn đã thắng!"
    color = (255, 80, 80) if result == "lose" else (255, 215, 0)
    label = menu_font.render(text, True, color)
    label_rect = label.get_rect(center=(screen_w // 2, screen_h // 2 - 60))
    screen.blit(label, label_rect)
    button_width, button_height, spacing = 120, 50, 20
    total_width = button_width * 2 + spacing
    start_x, y = (screen_w - total_width) // 2, screen_h // 2 + 20
    retry_btn = pygame.Rect(start_x, y, button_width, button_height)
    exit_btn = pygame.Rect(start_x + button_width + spacing, y, button_width, button_height)
    draw_button(retry_btn, "Retry", (50, 150, 200))
    draw_button(exit_btn, "Exit", (200, 50, 50))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "exit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if retry_btn.collidepoint(event.pos): return "retry"
                elif exit_btn.collidepoint(event.pos): return "exit"
        clock.tick(30)
  
def draw_minimap(maze, player_pos, hunter_pos, goal, panel_rect, offset_x, offset_y, map_w_pix, map_h_pix):
    MINI_W, MINI_H = 120, 120
    mini_x = panel_rect.x + (panel_rect.width - MINI_W) // 2
    mini_y = 10
    rows, cols = len(maze), len(maze[0])
    sx, sy = MINI_W / map_w_pix, MINI_H / map_h_pix
    pygame.draw.rect(screen, (20,20,20), (mini_x-2, mini_y-2, MINI_W+4, MINI_H+4))
    pygame.draw.rect(screen, (120,120,120), (mini_x-2, mini_y-2, MINI_W+4, MINI_H+4), 2)
    cell_w, cell_h = CELL_SIZE * sx, CELL_SIZE * sy
    for r in range(rows):
        for c in range(cols):
            color = (50,50,50) if maze[r][c] == 1 else (220,220,220)
            rx, ry = mini_x + c * cell_w, mini_y + r * cell_h
            if rx > mini_x + MINI_W or ry > mini_y + MINI_H: continue
            pygame.draw.rect(screen, color, (rx, ry, cell_w+1, cell_h+1))
    pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.5
    bright = int(200 + 55 * pulse)
    tx, ty = mini_x + goal[1] * CELL_SIZE * sx, mini_y + goal[0] * CELL_SIZE * sy
    tre_w, tre_h = max(6, cell_w), max(6, cell_h)
    pygame.draw.rect(screen, (255, 0, 0), (tx-2, ty-2, tre_w+4, tre_h+4))
    pygame.draw.rect(screen, (bright, bright, 0), (tx, ty, tre_w, tre_h))
    px, py = mini_x + player_pos[1] * CELL_SIZE * sx, mini_y + player_pos[0] * CELL_SIZE * sy
    pygame.draw.rect(screen, (50,150,255), (px, py, max(3, cell_w), max(3, cell_h)))
    hx, hy = mini_x + hunter_pos[1] * CELL_SIZE * sx, mini_y + hunter_pos[0] * CELL_SIZE * sy
    pygame.draw.rect(screen, (200,50,50), (hx, hy, max(3, cell_w), max(3, cell_h)))
    view_rx, view_ry = mini_x + offset_x * sx, mini_y + offset_y * sy
    view_rw, view_rh = VIEWPORT_W * sx, VIEWPORT_H * sy
    pygame.draw.rect(screen, (0,200,0), (view_rx, view_ry, view_rw, view_rh), 2)

def can_unlock_level(keys, required_keys=3):
    return keys >= required_keys