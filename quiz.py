
import pygame
import random
from utils import screen, menu_font, asset_path, font_path

# SAMPLE QUESTION BANK
QUESTION_BANK = [
    {
        "q": "What is the past tense of 'go'?",
        "choices": ["goed", "went", "gone", "goes"],
        "answer_idx": 1
    },
    {
        "q": "Choose the correct article: ___ apple",
        "choices": ["a", "an", "the", "no article"],
        "answer_idx": 1
    },
    {
        "q": "Which is a synonym of 'big'?",
        "choices": ["small", "huge", "tiny", "short"],
        "answer_idx": 1
    },
]

DEFAULT_SKIP_COST = 10

# Tải font
small_font = pygame.font.Font(font_path, 24)
question_font = pygame.font.Font(font_path, 60)  # chữ câu hỏi to hơn
def try_load_sound(*paths):
    for p in paths:
        try:
            return pygame.mixer.Sound(asset_path(p))
        except Exception:
            continue
    return None
correct_sound = try_load_sound("sounds/correctSound.mp3", "sounds/sfx_correct.wav")
wrong_sound = try_load_sound("sounds/wrongSound.mp3", "sounds/sfx_wrong.wav")

# Tải icon coin + quiz
try:
    coin_img = pygame.image.load(asset_path("coin.png")).convert_alpha()
    coin_img = pygame.transform.scale(coin_img, (40, 40))
except Exception as e:
    print("Lỗi load coin.png:", e)
    coin_img = None

try:
    quiz_img = pygame.image.load(asset_path("scroll.png"))
    quiz_img = pygame.transform.scale(quiz_img, (32, 32))
except Exception as e:
    print("Lỗi load scroll.png:", e)
    quiz_img = None

# Tải background cho popup
try:
    popup_bg = pygame.image.load(asset_path("question_crate.jpg")).convert()
except Exception as e:
    print("Lỗi load question_crate.jpg:", e)
    popup_bg = None


def pick_random_question():
    return random.choice(QUESTION_BANK)


def draw_button(surface, rect, text, font, bg_color, text_color=(255, 255, 255), hover=False):
    """Vẽ 1 nút với text căn giữa"""
    color = bg_color
    if hover:
        color = tuple(min(255, c + 30) for c in bg_color)  # hiệu ứng hover sáng hơn
    pygame.draw.rect(surface, color, rect, border_radius=8)
    txt = font.render(text, True, text_color)
    txt_rect = txt.get_rect(center=rect.center)
    surface.blit(txt, txt_rect)


def render_popup(question_obj, coins, skip_cost=DEFAULT_SKIP_COST, background_snapshot=None):
    clock = pygame.time.Clock()
    w, h = screen.get_size()

    # Kích thước panel
    panel_w, panel_h = int(w * 0.75), int(h * 0.6)
    panel_x, panel_y = (w - panel_w) // 2, (h - panel_h) // 2
    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

    # Overlay bán trong suốt
    semi_transparent_overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    semi_transparent_overlay.fill((0, 0, 0, 120))

    # Các nút chọn đáp án
    btn_w, btn_h = int(panel_w * 0.8), 48
    btn_x = panel_x + (panel_w - btn_w) // 2
    gap = 12
    START_CHOICE_Y = panel_y + 150
    choice_rects = [
        pygame.Rect(btn_x, START_CHOICE_Y + i * (btn_h + gap), btn_w, btn_h)
        for i in range(4)
    ]

    # Skip button
    SKIP_Y_OFFSET = -90
    skip_rect = pygame.Rect(panel_x + panel_w - 140,
                            panel_y + panel_h + SKIP_Y_OFFSET, 120, 40)

    question = question_obj["q"]
    choices = question_obj["choices"]
    answer_idx = question_obj["answer_idx"]

    selected = None
    result = None

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return "wrong"
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                for idx, rect in enumerate(choice_rects):
                    if rect.collidepoint((mx, my)):
                        selected = idx
                        result = "correct" if selected == answer_idx else "wrong"
                        break
                if skip_rect.collidepoint((mx, my)) and coins >= skip_cost:
                    return "skip"
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_1, pygame.K_KP1):
                    selected = 0
                elif ev.key in (pygame.K_2, pygame.K_KP2):
                    selected = 1
                elif ev.key in (pygame.K_3, pygame.K_KP3):
                    selected = 2
                elif ev.key in (pygame.K_4, pygame.K_KP4):
                    selected = 3
                if selected is not None:
                    result = "correct" if selected == answer_idx else "wrong"

        # Nền game (nếu có snapshot)
        if background_snapshot:
            screen.blit(background_snapshot, (0, 0))

        # Overlay
        screen.blit(semi_transparent_overlay, (0, 0))

        # Panel
        if popup_bg:
            bg = pygame.transform.scale(popup_bg, (panel_w, panel_h))
            screen.blit(bg, (panel_x, panel_y))
        else:
            pygame.draw.rect(screen, (30, 30, 40), panel_rect, border_radius=12)

        pygame.draw.rect(screen, (200, 200, 200), panel_rect, 2, border_radius=12)

        # Câu hỏi
        q_surf = question_font.render(question, True, (255, 220, 100))
        q_rect = q_surf.get_rect(midtop=(panel_x + panel_w // 2, panel_y + 50))
        screen.blit(q_surf, q_rect)

        # Các lựa chọn
        for i, rect in enumerate(choice_rects):
            hover = rect.collidepoint(pygame.mouse.get_pos())
            draw_button(screen, rect, f"{i+1}. {choices[i]}", small_font,
                        (50, 90, 120), (255, 255, 255), hover=hover)

        # Skip button
        skip_col = (180, 120, 40) if coins >= skip_cost else (80, 80, 80)
        draw_button(screen, skip_rect, f"Skip ({skip_cost})", small_font,
                    skip_col, (255, 255, 255))

        # Coin icon + số coin
        if coin_img:
            COIN_X = panel_x + 20
            COIN_Y = panel_y + panel_h - 60
            screen.blit(coin_img, (COIN_X, COIN_Y))
            coin_txt = small_font.render(str(coins), True, (255, 255, 0))
            coin_txt_rect = coin_txt.get_rect(midleft=(COIN_X + 45, COIN_Y + 20))
            screen.blit(coin_txt, coin_txt_rect)

        # Feedback khi trả lời
        if result:
            feedback = "Correct!" if result == "correct" else "Wrong!"
            color = (50, 200, 50) if result == "correct" else (200, 60, 60)
            
            # --- PHÁT ÂM THANH DỰA TRÊN KẾT QUẢ (PHẦN SỬA CHỮA) ---
            if result == "correct" and correct_sound:
                correct_sound.play()
            elif result == "wrong" and wrong_sound:
                wrong_sound.play()
            # -------------------------------------------------------

            fb_surf = menu_font.render(feedback, True, color)
            fb_rect = fb_surf.get_rect(center=(panel_x + panel_w // 2,
                                            panel_y + panel_h - 100))
            screen.blit(fb_surf, fb_rect)
            pygame.display.flip()
            
            # Delay để người chơi thấy kết quả và nghe âm thanh
            pygame.time.delay(700) 
            
            return result

        pygame.display.flip()
        clock.tick(60)


def show_question_popup(coins, skip_cost=DEFAULT_SKIP_COST, question_obj=None, background_snapshot=None):
    if question_obj is None:
        question_obj = pick_random_question()
    return render_popup(question_obj, coins, skip_cost=skip_cost, background_snapshot=background_snapshot)
