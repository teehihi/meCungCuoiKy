import pygame
import random
from player import Player
from enemy import Hunter
from background import ScrollingBackground 
from constants import (
    CELL_SIZE, VIEWPORT_W, VIEWPORT_H, MAP_COLS, MAP_ROWS,
    CAMERA_LERP, available_themes, asset_path
)
from utils import (
    load_theme, generate_maze, farthest_cell,
    draw_maze, draw_path, draw_control_panel, get_control_buttons, draw_minimap,
    clamp, screen, clock
)


# Khởi tạo các biến toàn cục cho game loop
wall_mapping = {}
ruin_images = []
bg_ruin_img = None

# =================== ÂM THANH ===================
# init mixer an toàn
try:
    pygame.mixer.init()
except Exception as e:
    print("Warning: pygame.mixer.init() failed:", e)

# SFX channels (sẽ được khởi tạo nếu mixer hoạt động)
LOSE_CHANNEL_IDX = 6
FOOT_CHANNEL_IDX = 5
lose_channel = None
foot_channel = None

win_sound = None
lose_sound = None
foot_sound = None

# Load background music (nhạc nền xử lý ở nơi khác / đã ok)
try:
    pygame.mixer.music.load(asset_path("sounds/bg_music.mp3"))
    pygame.mixer.music.set_volume(0.5)
except Exception as e:
    print("Không tìm thấy nhạc nền:", e)

# Load SFX (thử mp3 rồi wav)
def try_load_sound(*paths):
    for p in paths:
        try:
            return pygame.mixer.Sound(asset_path(p))
        except Exception:
            continue
    return None

win_sound = try_load_sound("sounds/win.mp3", "sounds/win.wav")
lose_sound = try_load_sound("sounds/lose.mp3", "sounds/lose.wav")
foot_sound = try_load_sound("sounds/foot.mp3", "sounds/step.mp3", "sounds/foot.wav")

# Tạo channel riêng cho lose & foot nếu có
if pygame.mixer.get_init():
    try:
        lose_channel = pygame.mixer.Channel(LOSE_CHANNEL_IDX)
    except Exception:
        lose_channel = None
    try:
        foot_channel = pygame.mixer.Channel(FOOT_CHANNEL_IDX)
    except Exception:
        foot_channel = None

def stop_all_sfx():
    """
    Dừng tất cả sound effects (không dừng pygame.mixer.music).
    Gọi khi bấm Retry / Exit để chắc chắn lose_sound không còn kêu.
    """
    try:
        # dừng kênh riêng nếu tồn tại
        if lose_channel:
            lose_channel.stop()
        if foot_channel:
            foot_channel.stop()
        # nếu không, dừng tất cả channels (không ảnh hưởng music)
        pygame.mixer.stop()
    except Exception:
        pass

# ------------------ Game loop ------------------
def game_loop(mode):

    # Đặt tên cửa sổ theo chế độ
    mode_titles = {
        "bfs": "Maze Hunter - BFS Mode",
        "dfs": "Maze Hunter - DFS Mode",
        "greedy": "Maze Hunter - Greedy Mode",
        "astar": "Maze Hunter - A* Mode"
    }
    pygame.display.set_caption(mode_titles.get(mode, "Maze Hunter"))

    dragging = False
    dragging_minimap = False
    last_mouse_pos = None
    global wall_mapping, ruin_images, bg_ruin_img, lose_channel, foot_channel
    
    wall_mapping = {}
    
    theme = random.choice(available_themes)
    ruin_images, bg_ruin_img, floor_img = load_theme(theme)

    maze = generate_maze(MAP_COLS, MAP_ROWS)
    ROWS, COLS = len(maze), len(maze[0])
    MAP_W_PIX = COLS * CELL_SIZE
    MAP_H_PIX = ROWS * CELL_SIZE

    panel_w = 160
    pygame.display.set_mode((VIEWPORT_W + panel_w, VIEWPORT_H))
    
    start, goal = (1,1), farthest_cell(maze, (1,1))
    
    player = Player(start)
    hunter_start_pos = [ROWS//2, COLS//2]
    if maze[hunter_start_pos[0]][hunter_start_pos[1]] == 1:
        for r in range(ROWS):
            for c in range(COLS):
                if maze[r][c] == 0:
                    hunter_start_pos = [r, c]
                    break

    hunter = Hunter(hunter_start_pos, theme)

    running, paused = True, False
    
    offset_x = float(clamp(player.pos[1]*CELL_SIZE - VIEWPORT_W//2, 0, max(0, MAP_W_PIX - VIEWPORT_W)))
    offset_y = float(clamp(player.pos[0]*CELL_SIZE - VIEWPORT_H//2, 0, max(0, MAP_H_PIX - VIEWPORT_H)))
    target_off_x = offset_x
    target_off_y = offset_y
    
    panel_rect = pygame.Rect(VIEWPORT_W, 0, 160, VIEWPORT_H)

    try:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)
    except Exception:
        pass

    last_foot_play = 0
    foot_cooldown_ms = 120

    while running:
        buttons = get_control_buttons(paused)

        mouse_pos = pygame.mouse.get_pos()
        hovering = False

        for name, rect in buttons.items():
            if rect and rect.collidepoint(mouse_pos):
                hovering = True
                break

        if hovering:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                try:
                    pygame.mixer.music.stop()
                except Exception:
                    pass
                stop_all_sfx()
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if buttons.get("reset") and buttons["reset"].collidepoint(event.pos): 
                    try:
                        pygame.mixer.music.stop()
                    except Exception:
                        pass
                    stop_all_sfx()
                    return "reset"

                if buttons.get("pause") and buttons["pause"].collidepoint(event.pos): 
                    paused = True

                if buttons.get("continue") and buttons["continue"].collidepoint(event.pos): 
                    paused = False

                if buttons.get("surrender") and buttons["surrender"].collidepoint(event.pos): 
                    try:
                        pygame.mixer.music.stop()
                    except Exception:
                        pass
                    stop_all_sfx()
                    return "exit"


                if event.button == 1 and event.pos[0] < VIEWPORT_W and event.pos[1] < VIEWPORT_H:
                    dragging = True
                    last_mouse_pos = event.pos
                elif event.button == 1 and panel_rect.collidepoint(event.pos):
                    dragging_minimap = True
                    mx, my = event.pos[0] - panel_rect.x, event.pos[1] - panel_rect.y
                    mw, mh = panel_rect.size
                    map_x = (mx / mw) * MAP_W_PIX
                    map_y = (my / mh) * MAP_H_PIX
                    target_off_x = clamp(map_x - VIEWPORT_W//2, 0, max(0, MAP_W_PIX - VIEWPORT_W))
                    target_off_y = clamp(map_y - VIEWPORT_H//2, 0, max(0, MAP_H_PIX - VIEWPORT_H))
                    offset_x, offset_y = target_off_x, target_off_y

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
                    dragging_minimap = False
                    last_mouse_pos = None

            elif event.type == pygame.MOUSEMOTION:
                if dragging and last_mouse_pos:
                    dx = event.pos[0] - last_mouse_pos[0]
                    dy = event.pos[1] - last_mouse_pos[1]
                    offset_x = clamp(offset_x - dx, 0, max(0, MAP_W_PIX - VIEWPORT_W))
                    offset_y = clamp(offset_y - dy, 0, max(0, MAP_H_PIX - VIEWPORT_H))
                    target_off_x = offset_x
                    target_off_y = offset_y
                    last_mouse_pos = event.pos
                elif dragging_minimap and panel_rect.collidepoint(event.pos):
                    mx, my = event.pos[0] - panel_rect.x, event.pos[1] - panel_rect.y
                    mw, mh = panel_rect.size
                    map_x = (mx / mw) * MAP_W_PIX
                    map_y = (my / mh) * MAP_H_PIX
                    target_off_x = clamp(map_x - VIEWPORT_W//2, 0, max(0, MAP_W_PIX - VIEWPORT_W))
                    target_off_y = clamp(map_y - VIEWPORT_H//2, 0, max(0, MAP_H_PIX - VIEWPORT_H))
                    offset_x, offset_y = target_off_x, target_off_y

            if not paused:
                player.handle_input_event(event)

        # --- Update ---
        screen.fill((10,0,0), rect=pygame.Rect(0,0,VIEWPORT_W, VIEWPORT_H))

        if not paused:
            prev_pos = tuple(player.pos)
            player.update(maze)
            
            # Sửa dòng này để truyền thêm theme
            hunter.update(player.pos, maze, mode, theme)

            if tuple(player.pos) != prev_pos and foot_sound:
                now = pygame.time.get_ticks()
                if now - last_foot_play >= foot_cooldown_ms:
                    try:
                        if foot_channel:
                            foot_channel.play(foot_sound)
                        else:
                            foot_sound.play()
                    except Exception:
                        pass
                    last_foot_play = now

            if not dragging and not dragging_minimap:
                target_off_x = clamp(player.pos[1]*CELL_SIZE - VIEWPORT_W//2 + CELL_SIZE//2, 0, max(0, MAP_W_PIX - VIEWPORT_W))
                target_off_y = clamp(player.pos[0]*CELL_SIZE - VIEWPORT_H//2 + CELL_SIZE//2, 0, max(0, MAP_H_PIX - VIEWPORT_H))

        # --- Camera lerp ---
        offset_x += (target_off_x - offset_x) * CAMERA_LERP
        offset_y += (target_off_y - offset_y) * CAMERA_LERP

        # --- Draw ---
        draw_maze(maze, goal, offset_x, offset_y, wall_mapping, ruin_images, bg_ruin_img, floor_img)
        
        if hunter.path:
            color = (0,255,255) if mode=="bfs" else (255,128,0)
            draw_path(screen, hunter.path, offset_x, offset_y)

        player.draw(screen, offset_x, offset_y)
        hunter.draw(screen, offset_x, offset_y)

        draw_control_panel(VIEWPORT_W, VIEWPORT_H, paused)
        draw_minimap(maze, player.pos, hunter.pos, goal, panel_rect, offset_x, offset_y, MAP_W_PIX, MAP_H_PIX)

        pygame.display.flip()
        clock.tick(30)

        # Kiểm tra win/lose sau update
        if not paused:
            if tuple(player.pos) == tuple(hunter.pos):
                if lose_sound:
                    try:
                        if lose_channel:
                            lose_channel.play(lose_sound)
                        else:
                            lose_sound.play()
                    except Exception:
                        pass
                try:
                    pygame.mixer.music.stop()
                except Exception:
                    pass
                return "lose"

            if tuple(player.pos) == goal:
                if win_sound:
                    try:
                        win_sound.play()
                    except Exception:
                        pass
                try:
                    pygame.mixer.music.stop()
                except Exception:
                    pass
                return "win"

    try:
        pygame.mixer.music.stop()
    except Exception:
        pass
    stop_all_sfx()
    return "exit"