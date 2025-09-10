import pygame

class ScrollingBackground:
    def __init__(self, image_path, screen_height, speed=1):
        self.bg = pygame.image.load(image_path).convert()
        self.bg_width = self.bg.get_width()
        self.bg = pygame.transform.scale(self.bg, (self.bg_width, screen_height))
        self.scroll_x = 0
        self.speed = speed
        self.height = screen_height

    def draw(self, screen):
        # Cuộn ngang
        self.scroll_x -= self.speed
        if abs(self.scroll_x) > self.bg_width:
            self.scroll_x = 0

        # Vẽ 2 lần để loop
        screen.blit(self.bg, (self.scroll_x, 0))
        screen.blit(self.bg, (self.scroll_x + self.bg_width, 0))
