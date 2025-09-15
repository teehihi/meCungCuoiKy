import pygame
import random
import os
import math
from constants import (
    CELL_SIZE, VIEWPORT_W, VIEWPORT_H, MAP_COLS, MAP_ROWS,
    CAMERA_LERP, available_themes
)
from utils import (
    load_theme, generate_maze, farthest_cell,
    draw_maze, draw_path, draw_control_panel, get_control_buttons, draw_minimap,
    clamp, screen, clock
)
from player import Player
from enemy import Hunter
from background import ScrollingBackground 

# Khởi tạo các biến toàn cục cho game loop
wall_mapping = {}
ruin_images = []
bg_ruin_img = None



def game_loop(mode):
    dragging = False
    dragging_minimap = False
    last_mouse_pos = None
    global wall_mapping, ruin_images, bg_ruin_img
    
    wall_mapping = {}
    
    theme = random.choice(available_themes)
    ruin_images, bg_ruin_img = load_theme(theme)

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
    hunter = Hunter(hunter_start_pos)

    running, paused = True, False
    
    offset_x = float(clamp(player.pos[1]*CELL_SIZE - VIEWPORT_W//2, 0, max(0, MAP_W_PIX - VIEWPORT_W)))
    offset_y = float(clamp(player.pos[0]*CELL_SIZE - VIEWPORT_H//2, 0, max(0, MAP_H_PIX - VIEWPORT_H)))
    target_off_x = offset_x
    target_off_y = offset_y
    
    panel_rect = pygame.Rect(VIEWPORT_W, 0, 160, VIEWPORT_H)

    while running:
        buttons = get_control_buttons(paused)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if buttons.get("reset") and buttons["reset"].collidepoint(event.pos): 
                    return "reset"
                elif "pause" in buttons and buttons["pause"].collidepoint(event.pos): 
                    paused = True
                elif "continue" in buttons and buttons["continue"].collidepoint(event.pos): 
                    paused = False
                elif buttons.get("surrender") and buttons["surrender"].collidepoint(event.pos): 
                    return "exit"

                # --- Kéo map chính (phải trong vùng bản đồ) ---
                if event.button == 1 and event.pos[0] < VIEWPORT_W and event.pos[1] < VIEWPORT_H:
                    dragging = True
                    last_mouse_pos = event.pos

                # --- Điều khiển minimap ---
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
                # --- Kéo map chính ---
                if dragging and last_mouse_pos:
                    dx = event.pos[0] - last_mouse_pos[0]
                    dy = event.pos[1] - last_mouse_pos[1]
                    offset_x = clamp(offset_x - dx, 0, max(0, MAP_W_PIX - VIEWPORT_W))
                    offset_y = clamp(offset_y - dy, 0, max(0, MAP_H_PIX - VIEWPORT_H))
                    target_off_x = offset_x
                    target_off_y = offset_y
                    last_mouse_pos = event.pos

                # --- Kéo minimap ---
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
            player.update(maze)
            hunter.update(player.pos, maze, mode)

            # Camera auto follow khi không kéo
            if not dragging and not dragging_minimap:
                target_off_x = clamp(player.pos[1]*CELL_SIZE - VIEWPORT_W//2 + CELL_SIZE//2, 0, max(0, MAP_W_PIX - VIEWPORT_W))
                target_off_y = clamp(player.pos[0]*CELL_SIZE - VIEWPORT_H//2 + CELL_SIZE//2, 0, max(0, MAP_H_PIX - VIEWPORT_H))

        # --- Camera lerp ---
        offset_x += (target_off_x - offset_x) * CAMERA_LERP
        offset_y += (target_off_y - offset_y) * CAMERA_LERP

        # --- Draw ---
        draw_maze(maze, goal, offset_x, offset_y, wall_mapping, ruin_images, bg_ruin_img)
        
        if hunter.path:
            color = (0,255,255) if mode=="bfs" else (255,128,0)
            draw_path(screen, hunter.path, offset_x, offset_y)

        player.draw(screen, offset_x, offset_y)
        hunter.draw(screen, offset_x, offset_y)

        draw_control_panel(VIEWPORT_W, VIEWPORT_H, paused)

        draw_minimap(maze, player.pos, hunter.pos, goal, panel_rect, offset_x, offset_y, MAP_W_PIX, MAP_H_PIX)

        pygame.display.flip()
        clock.tick(30)

        if not paused:
            if tuple(player.pos) == tuple(hunter.pos): 
                return "lose"
            if tuple(player.pos) == goal: 
                return "win"

    return "exit"

