import pygame
from constants import CELL_SIZE, player_speed, asset_path
from utils import load_spritesheet_rows

# Load spritesheet
sprite_rows, sprite_cols = 4, 8
player_frames = load_spritesheet_rows(asset_path("player_run.png"), 64, 64, sprite_rows, sprite_cols)
player_animations = {
    "down": player_frames[0],
    "up": player_frames[1],
    "left": player_frames[2],
    "right": player_frames[3],
}

class Player:
    def __init__(self, start_pos):
        # Vị trí logic (ô trong maze)
        self.grid_pos = list(start_pos)   # [row, col]

        # Vị trí thực để vẽ (pixel)
        self.pixel_pos = [
            self.grid_pos[1] * CELL_SIZE,
            self.grid_pos[0] * CELL_SIZE
        ]

        self.direction = "down"
        self.frame_index = 0
        self.frame_timer = 0
        self.is_moving = False
        self.last_move_time = 0
        self.move_interval_ms = 1000 // 3
        self.last_direction = "down"

    @property
    def pos(self):
        return self.grid_pos

    def handle_input_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.is_moving = True
            if event.key == pygame.K_UP:
                self.direction = "up"
            elif event.key == pygame.K_DOWN:
                self.direction = "down"
            elif event.key == pygame.K_LEFT:
                self.direction = "left"
            elif event.key == pygame.K_RIGHT:
                self.direction = "right"

        elif event.type == pygame.KEYUP:
            self.is_moving = False

    def update(self, maze):
        current_time = pygame.time.get_ticks()

        # Thử move theo grid (nhưng pixel sẽ di chuyển từ từ)
        if self.is_moving and current_time - self.last_move_time >= self.move_interval_ms:
            self._move(maze)

        # Animation luôn chạy
        self.handle_animation()

        # Cập nhật pixel_pos (lerp mượt về ô mới)
        target_x = self.grid_pos[1] * CELL_SIZE
        target_y = self.grid_pos[0] * CELL_SIZE
        lerp_factor = 0.2  # càng nhỏ càng mượt
        self.pixel_pos[0] += (target_x - self.pixel_pos[0]) * lerp_factor
        self.pixel_pos[1] += (target_y - self.pixel_pos[1]) * lerp_factor

    def _move(self, maze):
        new_pos = list(self.grid_pos)
        if self.direction == "up":
            new_pos[0] -= 1
        elif self.direction == "down":
            new_pos[0] += 1
        elif self.direction == "left":
            new_pos[1] -= 1
        elif self.direction == "right":
            new_pos[1] += 1

        if self._can_move_to(new_pos, maze):
            self.grid_pos = new_pos
            self.last_move_time = pygame.time.get_ticks()

    def _can_move_to(self, new_pos, maze):
        nr, nc = new_pos
        rows, cols = len(maze), len(maze[0])
        return 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 0

    def handle_animation(self):
        animation_speed = player_speed if self.is_moving else player_speed * 2
        self.frame_timer += 1
        if self.frame_timer >= animation_speed:
            self.frame_index = (self.frame_index + 1) % len(player_animations[self.direction])
            self.frame_timer = 0
        self.last_direction = self.direction

    def draw(self, screen, offset_x, offset_y):
        frames = player_animations[self.direction]
        img = frames[self.frame_index % len(frames)]
        x = self.pixel_pos[0] - offset_x
        y = self.pixel_pos[1] - offset_y
        screen.blit(img, (x, y))
