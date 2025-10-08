import pygame
from constants import CELL_SIZE, player_speed, asset_path
from utils import load_spritesheet_rows

# --- CẬP NHẬT: KHAI BÁO BIẾN TRƯỚC ---
player_animations = {}
player_hit_animations = {}

HIT_STUN_DURATION = 1000
FLICKER_SPEED = 6

direction_keys = ["down", "left", "right", "up"]

# --- HÀM TẢI SPRITE THEO THEME (ĐÃ CẬP NHẬT) ---
def load_player_theme_sprites(theme):
    """
    Tải spritesheet của player dựa vào theme được chọn.
    Bao gồm cả sprite thường (run) và sprite bị trúng đòn (hit).
    """
    global player_animations, player_hit_animations

    # ---- Chọn file sprite theo theme ----
    if theme == "conan":
        player_sprite_filename = "player_run_conan.png"
        player_hit_filename = "player_hit_conan.png"
    else:
        player_sprite_filename = "player_run.png"
        player_hit_filename = "player_hit.png"

    # ---- 1. Tải spritesheet THƯỜNG ----
    try:
        sprite_rows, sprite_cols = 4, 8
        player_frames_normal = load_spritesheet_rows(
            asset_path(player_sprite_filename), 64, 64, sprite_rows, sprite_cols
        )
        player_animations = {}
        for i, direction in enumerate(direction_keys):
            player_animations[direction] = player_frames_normal[i]
    except Exception as e:
        print(f"Lỗi tải {player_sprite_filename}: {e}")
        player_animations = {d: [] for d in direction_keys}

    # ---- 2. Tải spritesheet BỊ ĐAU ----
    try:
        sprite_rows_hit, sprite_cols_hit = 4, 5
        player_frames_hit = load_spritesheet_rows(
            asset_path(player_hit_filename), 64, 64, sprite_rows_hit, sprite_cols_hit
        )

        player_hit_animations = {}
        for i, direction in enumerate(direction_keys):
            # Nếu spritesheet có >=4 cột thì chọn frame thứ 3 (vì màu đỏ dễ thấy)
            if sprite_cols_hit >= 4:
                player_hit_animations[direction] = [player_frames_hit[i][3]]
            else:
                player_hit_animations[direction] = [player_frames_hit[i][0]]

    except Exception as e:
        print(f"Lỗi tải {player_hit_filename}: {e}. Dùng sprite thường làm fallback.")
        player_hit_animations = player_animations


# ------------------------------------------------------------------

class Player:
    def __init__(self, start_pos, initial_lives=5):
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
        self.lives = initial_lives
        
        # --- BIẾN TRẠNG THÁI KHI BỊ CHẠM ---
        self.hit_stun_timer = 0       
        self.flicker_counter = 0      
        # ----------------------------------------

    # ... (Phần còn lại của class Player giữ nguyên, không cần thay đổi)
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

    def lose_life(self):
        """Trừ 1 mạng và kích hoạt hiệu ứng bị đau."""
        self.lives -= 1
        # Kích hoạt hiệu ứng bị đau khi mất máu
        self.hit_stun_timer = pygame.time.get_ticks() + HIT_STUN_DURATION
        return self.lives # Trả về số mạng còn lại

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
            # Animation luôn dựa trên độ dài của animation BÌNH THƯỜNG
            # Đảm bảo self.frame_index không vượt quá frames của player_animations
            if player_animations[self.direction]: # Kiểm tra list không rỗng
                self.frame_index = (self.frame_index + 1) % len(player_animations[self.direction])
            self.frame_timer = 0
        self.last_direction = self.direction

    def draw(self, screen, offset_x, offset_y):
        now = pygame.time.get_ticks()
        
        # 1. KIỂM TRA HIỆU ỨNG BỊ ĐAU
        if now < self.hit_stun_timer:
            self.flicker_counter += 1
            if (self.flicker_counter // FLICKER_SPEED) % 2 == 0:
                current_animations = player_animations 
            else:
                current_animations = player_hit_animations
            
            frames = current_animations.get(self.direction, current_animations.get("down", []))
            if frames:
                img = frames[self.frame_index % len(frames)]
            else:
                return # Không vẽ gì nếu không có frame
            
        else:
            # Player bình thường
            current_animations = player_animations
            self.flicker_counter = 0
            
            frames = current_animations.get(self.direction, current_animations.get("down", []))
            if frames:
                img = frames[self.frame_index % len(frames)]
            else:
                return # Không vẽ gì nếu không có frame
        
        # Vẽ lên màn hình
        x = self.pixel_pos[0] - offset_x
        y = self.pixel_pos[1] - offset_y
        screen.blit(img, (x, y))