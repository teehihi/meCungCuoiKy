
import pygame
import random
from utils import screen, menu_font, asset_path, font_path

QUESTION_BANK = [
    {
        "q": "Its_____into Brazil has given Darrow Textiles Ltd. an advantage over much of its competition.",
        "choices": ["expansion", "process", "creation", "action"],
        "answer_idx": 0
    },
    {
        "q": "Employees at NC media co., Ltd_____donate to local charities by hosting Fund-raising parties.",
        "choices": ["regularity", "regularize", "regularities", "regularly"],
        "answer_idx": 3
    },
    {
        "q": "From winning an Olympic gold medal in 2000 to becoming an NBA champion in 2008, Kevin Garnet has shown_____to be one of the most talented players.",
        "choices": ["he", "him", "himself", "his"],
        "answer_idx": 2
    },
    {
        "q": "An accurate_____of surveys is imperative to building a good understanding of customer needs.",
        "choices": ["opportunity", "contract", "destination", "analysis"],
        "answer_idx": 3
    },
    {
        "q": "QIB will work_____to maintain sustainable growth and expansion plans.",
        "choices": ["Persisted", "Persistent", "Persistently", "Persistence"],
        "answer_idx": 2
    },
    {
        "q": "The president has just realized that the launch of our new product must be postponed owing to_____conditions in the market.",
        "choices": ["unwilling", "unfavorable", "opposing", "reluctant"],
        "answer_idx": 1
    },
    {
        "q": "A letter_____by a copy of the press release was mailed to the public relations department yesterday.",
        "choices": ["accompanies", "accompanying", "accompanied", "will accompany"],
        "answer_idx": 2
    },
    {
        "q": "The announcement of John Stanton's retirement was not well received by most of the staff members, but Leslie, his long time friend and colleague, was extremely …….to hear that Mr Stanton will now be able to enjoy some leisure time.",
        "choices": ["happiest", "happily", "happier", "happy"],
        "answer_idx": 3
    },
    {
        "q": "Nevada Jobfind Inc. is planning to host a career fair for college graduates seeking_____in the healthcare sector.",
        "choices": ["employ", "employment", "employee", "employing"],
        "answer_idx": 1
    },
    {
        "q": "The manager has asked Mr. Lim to submit his final report on the sales of the new washing machine_____April 30th.",
        "choices": ["with", "toward", "between", "by"],
        "answer_idx": 3
    },
    {
        "q": "Following the visit to your production facility in Hong Kong next week, we_____. a comprehensive factory automation program to meet your company's needs.",
        "choices": ["will create", "was created", "having created", "had been creating"],
        "answer_idx": 0
    },
    {
        "q": "Any employers or contractors who are found to have_____safety laws will be subject to a heavy fine.",
        "choices": ["complied", "observed", "breached", "adhered"],
        "answer_idx": 2
    },
    {
        "q": "Mr. Tanaka decided to resign, because a significant drop in customer satisfaction has had an adverse impact on sales_____",
        "choices": ["grower", "grow", "grown", "growth"],
        "answer_idx": 3
    },
    {
        "q": "_____his appointment as our head of accounting services, Paul Robinson was working as a high-powered merchant banker in London.",
        "choices": ["Since", "Prior to", "Except", "Because"],
        "answer_idx": 1
    },
    {
        "q": "We believe that the popularity of _____products is the result of a combination of beauty and functionality.",
        "choices": ["Us", "We", "Our", "Ours"],
        "answer_idx": 2
    },
    {
        "q": "_____his falling out with his former employer, Mr. Lee still meets with some of his old co-workers from time to time.",
        "choices": ["Subsequently", "However", "Meanwhile", "Despite"],
        "answer_idx": 3
    },
    {
        "q": "Library users must remove all_____belongings when they leave the library for more than a half hour.",
        "choices": ["unlimited", "personal", "accurate", "believable"],
        "answer_idx": 1
    },
    {
        "q": "Personnel changes within the marketing department _____no surprise, as it completely failed to meet the target on the most recent project.",
        "choices": ["made of", "came as", "spoke of", "came across"],
        "answer_idx": 1
    },
    {
        "q": "_____anyone wish to access the information on the status of his or her order, the password should be entered.",
        "choices": ["If", "Should", "Whether", "As though"],
        "answer_idx": 1
    },
    {
        "q": "The latest training_____contains tips on teaching a second language to international students.",
        "choices": ["method", "guide", "staff", "role"],
        "answer_idx": 1
    },
    {
        "q": "The more we spent with the sales team, the more_____we were with their innovative marketing skills.",
        "choices": ["impression", "impress", "impresses", "impressed"],
        "answer_idx": 3
    },
    {
        "q": "_____Mega Foods imports only one kind of cheese now, the company will be importing a total of five varieties by next year.",
        "choices": ["Until", "Once", "Unless", "Although"],
        "answer_idx": 3
    },
    {
        "q": "Anyone_____experiences complications with the new software is encouraged to bring this matter to Mr. Gruber's attention in room 210.",
        "choices": ["Who", "Which", "Whom", "whose"],
        "answer_idx": 0
    },
    {
        "q": "Fast_____.in computer technology have made it possible for the public to access a second-to-none amount of news and information.",
        "choices": ["Inspections", "Belongings", "Advances", "Commitments"],
        "answer_idx": 2
    },
    {
        "q": "Whether it is_____.to register for a student discount card depends on the needs of the individual.",
        "choices": ["necessary", "necessarily", "necessitate", "necessity"],
        "answer_idx": 0
    },
    {
        "q": "As space is limited, be sure to contact Bill in the personnel department a minimum of three days in advance to_____for a workshop.",
        "choices": ["approve", "express", "register", "record"],
        "answer_idx": 2
    },
    {
        "q": "Ms. Walters was_____to make a presentation on how to increase revenue when I entered the room.",
        "choices": ["nearly", "off", "close", "about"],
        "answer_idx": 3
    },
    {
        "q": "Considering her ability, dedication, and expertise, I am_____that Ms. Yoko will be the most suitable person for the position of marketing manager.",
        "choices": ["Confident", "Obvious", "Noticeable", "Intelligent"],
        "answer_idx": 0
    },
    {
        "q": "_____the workload is very high at the moment, all the team members are optimistic that they will be able to finish the required work on time.",
        "choices": ["Even though", "According to", "As if", "In order for"],
        "answer_idx": 0
    },
    {
        "q": "Because the store was_____ located, it had a huge advantage in exposing its goods to the public, which had an impact on its increase in sales.",
        "choices": ["center", "central", "centrally", "centered"],
        "answer_idx": 2
    },
    {
        "q": "_____the city council has approved the urban renewal project, we need to recruit several new workers.",
        "choices": ["If so", "Rather than", "Owing to", "Given that"],
        "answer_idx": 3
    },
    {
        "q": "The technicians_____tested all air-conditioning units to ensure that the cooling system is running smoothly.",
        "choices": ["systematically", "exceedingly", "increasingly", "lastly"],
        "answer_idx": 0
    },
    {
        "q": "We have_____confidence in the product's ability to provide unrivaled protection in an exposed blast environment.",
        "choices": ["productive", "eventual", "informative", "absolute"],
        "answer_idx": 3
    },
    {
        "q": "The marketers make an_____of products that attract a wide variety of potential customers.",
        "choices": ["array", "alleviation", "origin", "extension"],
        "answer_idx": 0
    },
    {
        "q": "Newer branches can be opened worldwide_____we can properly translate our marketing goals.",
        "choices": ["as soon as", "right away", "promptly", "in time for"],
        "answer_idx": 0
    },
    {
        "q": "Despite the fact that the new_____was developed by MIN Communications, its parent company received all the credit for it.",
        "choices": ["technology", "technologies", "technological", "technologists"],
        "answer_idx": 0
    },
    {
        "q": "Greg O'Leary has been leading research in our laboratories_____over eighteen years.",
        "choices": ["in", "for", "up", "from"],
        "answer_idx": 1
    },
    {
        "q": "Library and information science majors should be reminded of the seminar beginning_____at 6:00 p.m in room 212B.",
        "choices": ["promptly", "prompts", "prompter", "prompted"],
        "answer_idx": 0
    },
    {
        "q": "The meteorological agency recommended that tourists to the region be_____dressed for frigid conditions.",
        "choices": ["suitable", "suitably", "suitability", "suitableness"],
        "answer_idx": 1
    },
    {
        "q": "The letter from Ms. Win seems to have disappeared without a_____",
        "choices": ["whisper", "peep", "trace", "flash"],
        "answer_idx": 2
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

                # ===== CÂU HỎI (PHIÊN BẢN MỚI) =====
        # Font nhỏ hơn cho câu hỏi
        wrapped_font = pygame.font.Font(font_path, 36)

        # Hàm chia văn bản tự động xuống dòng
        def wrap_text(text, font, max_width):
            words = text.split(" ")
            lines, current = [], ""
            for w_ in words:
                test = current + w_ + " "
                if font.size(test)[0] <= max_width:
                    current = test
                else:
                    lines.append(current.strip())
                    current = w_ + " "
            if current:
                lines.append(current.strip())
            return lines

        # Giới hạn chiều rộng tối đa
        max_text_width = panel_w - 100
        lines = wrap_text(question, wrapped_font, max_text_width)

        # Nền riêng cho vùng câu hỏi
        q_bg_height = len(lines) * 42 + 30
        q_bg_rect = pygame.Rect(panel_x + 50, panel_y + 30, panel_w - 100, q_bg_height)

        # Vẽ nền (gradient tím đậm -> xanh navy nhẹ)
        q_bg_surface = pygame.Surface((q_bg_rect.width, q_bg_rect.height), pygame.SRCALPHA)
        for y in range(q_bg_rect.height):
            r = int(30 + (y / q_bg_rect.height) * 20)
            g = int(20 + (y / q_bg_rect.height) * 40)
            b = int(60 + (y / q_bg_rect.height) * 60)
            pygame.draw.line(q_bg_surface, (r, g, b, 210), (0, y), (q_bg_rect.width, y))
        screen.blit(q_bg_surface, q_bg_rect.topleft)
        pygame.draw.rect(screen, (255, 255, 255), q_bg_rect, 2, border_radius=10)

        # Hiển thị từng dòng câu hỏi căn giữa
        y_offset = q_bg_rect.y + 15
        for line in lines:
            text_surf = wrapped_font.render(line, True, (255, 230, 120))
            text_rect = text_surf.get_rect(centerx=panel_x + panel_w // 2, y=y_offset)
            screen.blit(text_surf, text_rect)
            y_offset += 42
        # ===== HẾT PHẦN CÂU HỎI =====


        # Các lựa chọn
        for i, rect in enumerate(choice_rects):
            hover = rect.collidepoint(pygame.mouse.get_pos())

            # Màu mặc định
            bg_col = (50, 90, 120)

            # Nếu đã chọn -> tô màu theo đúng/sai
            if result is not None:
                if i == answer_idx:
                    bg_col = (60, 180, 80)  # xanh lá cho đáp án đúng
                elif i == selected and selected != answer_idx:
                    bg_col = (200, 60, 60)  # đỏ cho đáp án sai
                else:
                    bg_col = (70, 70, 70)   # xám mờ cho các nút còn lại

            draw_button(screen, rect, f"{i+1}. {choices[i]}", small_font,
                        bg_col, (255, 255, 255), hover=(hover and result is None))

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
