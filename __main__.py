import pygame
from game import game_loop
from menu import main_menu   
from utils import loading_screen, transition_screen, end_screen
from constants import VIEWPORT_W, VIEWPORT_H, CELL_SIZE, MAP_COLS, MAP_ROWS

# Vòng lặp chính của ứng dụng
def main():
    while True:
        # chạy menu để lấy mode
        mode = main_menu()
        if mode == "exit":
            break   # thoát game

        # màn hình loading
        loading_screen()

        # vòng chơi
        while True:
            result = game_loop(mode)

            if result == "reset":
                continue

            elif result == "lose":
                choice = end_screen("lose")
                if choice == "retry":
                    continue
                else:
                    break

            elif result == "win":
                transition = transition_screen("Level Up!")
                if transition == "next":
                    continue
                else:
                    break

            else:
                break

    pygame.quit()

if __name__ == "__main__":
    main()
