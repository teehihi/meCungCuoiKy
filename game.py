import pygame
import random
import utils
from player import Player, load_player_theme_sprites 
from enemy import Hunter
from background import ScrollingBackground 
from quiz import show_question_popup 
from constants import (
    CELL_SIZE, VIEWPORT_W, VIEWPORT_H, MAP_COLS, MAP_ROWS,
    CAMERA_LERP, available_themes, asset_path
)

# Khởi tạo các biến toàn cục cho game loop
wall_mapping = {}
ruin_images = []
bg_ruin_img = None

# =================== ÂM THANH ===================
try:
    pygame.mixer.init()
except Exception as e:
    print("Warning: pygame.mixer.init() failed:", e)

LOSE_CHANNEL_IDX, FOOT_CHANNEL_IDX = 6, 5
lose_channel, foot_channel = None, None
win_sound, lose_sound, foot_sound = None, None, None

try:
    pygame.mixer.music.load(asset_path("sounds/bg_music.mp3"))
    pygame.mixer.music.set_volume(0.5)
except Exception as e:
    print("Không tìm thấy nhạc nền:", e)

def try_load_sound(*paths):
    for p in paths:
        try: return pygame.mixer.Sound(asset_path(p))
        except Exception: continue
    return None

win_sound = try_load_sound("sounds/win.mp3", "sounds/win.wav")
lose_sound = try_load_sound("sounds/lose.mp3", "sounds/lose.wav")
shout_sound = try_load_sound("sounds/shout.mp3")
foot_sound = try_load_sound("sounds/foot.mp3", "sounds/step.mp3", "sounds/foot.wav")
coin_collect = try_load_sound("sounds/coin_collect.mp3")
quiz_sound = try_load_sound("sounds/quizzSound.mp3")

if pygame.mixer.get_init():
    try: lose_channel = pygame.mixer.Channel(LOSE_CHANNEL_IDX)
    except Exception: lose_channel = None
    try: foot_channel = pygame.mixer.Channel(FOOT_CHANNEL_IDX)
    except Exception: foot_channel = None

def stop_all_sfx():
    try:
        if lose_channel: lose_channel.stop()
        if foot_channel: foot_channel.stop()
        pygame.mixer.stop()
        pygame.mixer.music.stop() 
    except Exception: pass

# ------------------ Game loop ------------------
def game_loop(mode, initial_coins=0, initial_keys=0,  initial_lives=5):
    mode_titles = {
        "bfs": "Maze Hunter - BFS Mode", "dfs": "Maze Hunter - DFS Mode",
        "greedy": "Maze Hunter - Greedy Mode", "astar": "Maze Hunter - A* Mode",
        "hillclimbing": "Maze Hunter - Hill Climbing Mode", "sa" : "Maze Hunter - Simulated Annealing Mode"
    }
    pygame.display.set_caption(mode_titles.get(mode, "Maze Hunter"))

    dragging, dragging_minimap, last_mouse_pos = False, False, None
    global wall_mapping, ruin_images, bg_ruin_img, lose_channel, foot_channel
    wall_mapping = {}
    
    theme = random.choice(available_themes)
    load_player_theme_sprites(theme)
    # load animations via utils module
    utils.load_coin_sprites(theme)
    utils.load_key_sprites(theme)

    ruin_images, bg_ruin_img, floor_img = utils.load_theme(theme)

    maze = utils.generate_maze(MAP_COLS, MAP_ROWS)
    ROWS, COLS = len(maze), len(maze[0])
    MAP_W_PIX, MAP_H_PIX = COLS * CELL_SIZE, ROWS * CELL_SIZE
    panel_w = 160
    pygame.display.set_mode((VIEWPORT_W + panel_w, VIEWPORT_H))
    
    start, goal = (1,1), utils.farthest_cell(maze, (1,1))
    player = Player(start, initial_lives)
    
    hunter_start_pos = [ROWS//2, COLS//2]
    if maze[hunter_start_pos[0]][hunter_start_pos[1]] == 1:
        for r in range(ROWS):
            for c in range(COLS):
                if maze[r][c] == 0:
                    hunter_start_pos = [r, c]
                    break
    hunter = Hunter(hunter_start_pos, theme)

    hunter_stun_timer, STUN_DURATION, RESPAWN_DISTANCE = 0, 1000, 5
    coins, keys = initial_coins, initial_keys   
    items = []
    floor_cells = [(r,c) for r in range(ROWS) for c in range(COLS) if maze[r][c] == 0]
    for ban in (start, goal, tuple(hunter_start_pos)):
        if ban in floor_cells:
            try: floor_cells.remove(ban)
            except ValueError: pass

    NUM_COINS, NUM_QUIZ = max(6, (ROWS*COLS)//120), max(4, (ROWS*COLS)//300)
    random.shuffle(floor_cells)
    idx = 0
    for i in range(NUM_COINS):
        if idx >= len(floor_cells): break
        items.append({"type":"coin", "pos": floor_cells[idx]}); idx += 1
    for i in range(NUM_QUIZ):
        if idx >= len(floor_cells): break
        items.append({"type":"quiz", "pos": floor_cells[idx]}); idx += 1

    running, paused = True, False
    offset_x = float(utils.clamp(player.pos[1]*CELL_SIZE - VIEWPORT_W//2, 0, max(0, MAP_W_PIX - VIEWPORT_W)))
    offset_y = float(utils.clamp(player.pos[0]*CELL_SIZE - VIEWPORT_H//2, 0, max(0, MAP_H_PIX - VIEWPORT_H)))
    target_off_x, target_off_y = offset_x, offset_y
    panel_rect = pygame.Rect(VIEWPORT_W, 0, 160, VIEWPORT_H)

    try:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)
    except Exception: pass

    last_foot_play, foot_cooldown_ms = 0, 120

    while running:
        buttons = utils.get_control_buttons(paused)
        mouse_pos = pygame.mouse.get_pos()
        hovering = any(rect.collidepoint(mouse_pos) for name, rect in buttons.items() if rect)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if hovering else pygame.SYSTEM_CURSOR_ARROW)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_all_sfx(); running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if buttons.get("reset") and buttons["reset"].collidepoint(event.pos): stop_all_sfx(); return "reset", coins, keys
                if buttons.get("pause") and buttons["pause"].collidepoint(event.pos): paused = True
                if buttons.get("continue") and buttons["continue"].collidepoint(event.pos): paused = False
                if buttons.get("surrender") and buttons["surrender"].collidepoint(event.pos): stop_all_sfx(); return "exit", coins, keys
                if event.button == 1 and event.pos[0] < VIEWPORT_W and event.pos[1] < VIEWPORT_H:
                    dragging, last_mouse_pos = True, event.pos
                elif event.button == 1 and panel_rect.collidepoint(event.pos):
                    dragging_minimap = True
                    mx, my = event.pos[0] - panel_rect.x, event.pos[1] - panel_rect.y
                    mw, mh = panel_rect.size
                    map_x, map_y = (mx / mw) * MAP_W_PIX, (my / mh) * MAP_H_PIX
                    target_off_x = utils.clamp(map_x - VIEWPORT_W//2, 0, max(0, MAP_W_PIX - VIEWPORT_W))
                    target_off_y = utils.clamp(map_y - VIEWPORT_H//2, 0, max(0, MAP_H_PIX - VIEWPORT_H))
                    offset_x, offset_y = target_off_x, target_off_y
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: dragging, dragging_minimap, last_mouse_pos = False, False, None
            elif event.type == pygame.MOUSEMOTION:
                if dragging and last_mouse_pos:
                    dx, dy = event.pos[0] - last_mouse_pos[0], event.pos[1] - last_mouse_pos[1]
                    offset_x = utils.clamp(offset_x - dx, 0, max(0, MAP_W_PIX - VIEWPORT_W))
                    offset_y = utils.clamp(offset_y - dy, 0, max(0, MAP_H_PIX - VIEWPORT_H))
                    target_off_x, target_off_y, last_mouse_pos = offset_x, offset_y, event.pos
                elif dragging_minimap and panel_rect.collidepoint(event.pos):
                    mx, my = event.pos[0] - panel_rect.x, event.pos[1] - panel_rect.y
                    mw, mh = panel_rect.size
                    map_x, map_y = (mx / mw) * MAP_W_PIX, (my / mh) * MAP_H_PIX
                    target_off_x = utils.clamp(map_x - VIEWPORT_W//2, 0, max(0, MAP_W_PIX - VIEWPORT_W))
                    target_off_y = utils.clamp(map_y - VIEWPORT_H//2, 0, max(0, MAP_H_PIX - VIEWPORT_H))
                    offset_x, offset_y = target_off_x, target_off_y
            if not paused:
                player.handle_input_event(event)

        utils.screen.fill((10,0,0), rect=pygame.Rect(0,0,VIEWPORT_W, VIEWPORT_H))

        if not paused:
            prev_pos = tuple(player.pos)
            player.update(maze)
            hunter.update(player.pos, maze, mode, theme)

            p_pos, picked = tuple(player.pos), None
            for it in items:
                if p_pos == it["pos"]: picked = it; break
            
            if picked:
                if picked["type"] == "coin":
                    coins += 1; items.remove(picked)
                    if coin_collect: 
                        try: coin_collect.play() 
                        except Exception: pass
                elif picked["type"] == "quiz":
                    try:
                        pygame.mixer.music.pause()
                        if quiz_sound: quiz_sound.play()
                    except Exception: pass
                    utils.draw_maze(maze, goal, offset_x, offset_y, wall_mapping, ruin_images, bg_ruin_img, floor_img)
                    player.draw(utils.screen, offset_x, offset_y)
                    hunter.draw(utils.screen, offset_x, offset_y)
                    background_snapshot = utils.screen.copy()
                    SKIP_COST = 10
                    res = show_question_popup(coins, skip_cost=SKIP_COST, background_snapshot=background_snapshot)
                    try:
                        if quiz_sound: quiz_sound.stop()
                        pygame.mixer.music.unpause()
                    except Exception: pass
                    if res == "correct": keys += 1
                    elif res == "skip": coins -= SKIP_COST
                    items.remove(picked)

            if tuple(player.pos) != prev_pos and foot_sound:
                now = pygame.time.get_ticks()
                if now - last_foot_play >= foot_cooldown_ms:
                    try:
                        if foot_channel: foot_channel.play(foot_sound)
                        else: foot_sound.play()
                    except Exception: pass
                    last_foot_play = now

            if not dragging and not dragging_minimap:
                target_off_x = utils.clamp(player.pos[1]*CELL_SIZE - VIEWPORT_W//2 + CELL_SIZE//2, 0, max(0, MAP_W_PIX - VIEWPORT_W))
                target_off_y = utils.clamp(player.pos[0]*CELL_SIZE - VIEWPORT_H//2 + CELL_SIZE//2, 0, max(0, MAP_H_PIX - VIEWPORT_H))

        offset_x += (target_off_x - offset_x) * CAMERA_LERP
        offset_y += (target_off_y - offset_y) * CAMERA_LERP

        utils.draw_maze(maze, goal, offset_x, offset_y, wall_mapping, ruin_images, bg_ruin_img, floor_img)
        
        if hunter.path:
            color = (0,255,255) if mode=="bfs" else (255,128,0)
            utils.draw_path(utils.screen, hunter.path, offset_x, offset_y)

        player.draw(utils.screen, offset_x, offset_y)
        hunter.draw(utils.screen, offset_x, offset_y)

        # --- THAY ĐỔI: LOGIC VẼ ITEM SỬ DỤNG ANIMATION ---
        num_frames = 6
        anim_speed_ms = 150
        current_frame_index = (pygame.time.get_ticks() // anim_speed_ms) % num_frames
        
        for it in items:
            r, c = it["pos"]
            if it["type"] == "coin":
                # tham chiếu trực tiếp tới utils.animated_coin_frames
                if getattr(utils, "animated_coin_frames", None):
                    frames = utils.animated_coin_frames
                    # bảo đảm index an toàn nếu số frame khác num_frames
                    idx = current_frame_index % len(frames)
                    img_to_draw = frames[idx]
                    utils.draw_entity((r, c), img_to_draw, offset_x, offset_y)
                else: # Fallback
                    x, y = c*CELL_SIZE - offset_x, r*CELL_SIZE - offset_y
                    pygame.draw.circle(utils.screen, (212,175,55), (int(x+CELL_SIZE/2), int(y+CELL_SIZE/2)), CELL_SIZE//3)
            else:  # quiz item (key/scroll)
                if getattr(utils, "animated_key_frames", None):
                    frames = utils.animated_key_frames
                    idx = current_frame_index % len(frames)
                    img_to_draw = frames[idx]
                    utils.draw_entity((r, c), img_to_draw, offset_x, offset_y)
                else: # Fallback
                    x, y = c*CELL_SIZE - offset_x, r*CELL_SIZE - offset_y
                    pygame.draw.rect(utils.screen, (150,100,200), (x+CELL_SIZE*0.15, y+CELL_SIZE*0.15, CELL_SIZE*0.7, CELL_SIZE*0.7), border_radius=6)
        
        utils.draw_control_panel(VIEWPORT_W, VIEWPORT_H, paused, mode, coins=coins, keys=keys, lives=player.lives)
        utils.draw_minimap(maze, player.pos, hunter.pos, goal, panel_rect, offset_x, offset_y, MAP_W_PIX, MAP_H_PIX)

        pygame.display.flip()
        utils.clock.tick(30)

        if not paused:
            if tuple(player.pos) == tuple(hunter.pos):
                remaining_lives = player.lose_life()
                sound_to_play = shout_sound if remaining_lives > 0 else lose_sound
                if sound_to_play:
                    try:
                        if lose_channel: lose_channel.play(sound_to_play)
                        else: sound_to_play.play()
                    except Exception: pass
                
                hunter_stun_timer = pygame.time.get_ticks() + STUN_DURATION
                hunter.pos = hunter.respawn_safely(maze, player.pos, RESPAWN_DISTANCE)
                hunter.path = None 
                
                if remaining_lives <= 0:
                    stop_all_sfx()

                    if lose_sound:
                        try:
                            if lose_channel:
                                lose_channel.play(lose_sound)
                            else:
                                lose_sound.play()
                        except Exception as e:
                            print("Lose sound error:", e)

                    return "lose", coins, keys

            
            if pygame.time.get_ticks() >= hunter_stun_timer:
                hunter.update(player.pos, maze, mode, theme) 

            if tuple(player.pos) == goal:
                if utils.can_unlock_level(keys):
                    if win_sound: 
                        try: win_sound.play() 
                        except Exception: pass
                    stop_all_sfx(); return "win", coins, keys
                else:
                    font = pygame.font.SysFont("Segoe UI", 24, bold=True)
                    msg = f"Cần {3 - keys} key nữa để qua màn!"
                    label = font.render(msg, True, (255, 50, 50))
                    utils.screen.blit(label, (VIEWPORT_W//2 - label.get_width()//2, VIEWPORT_H//2 - 20))
                    pygame.display.flip()
                    pygame.time.delay(1000)

    stop_all_sfx()
    return "exit", coins, keys
