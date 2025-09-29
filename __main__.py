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


        #Lưu coin
        current_coins = 0
        current_keys = 0
        # vòng chơi
        while True:
            result, end_coins, end_keys = game_loop(mode, current_coins, current_keys)

            if result == "reset":
                current_coins = 0 
                current_keys = 0
                continue

            elif result == "lose":
                choice = end_screen("lose")
                if choice == "retry":
                    current_coins = 0
                    current_keys = 0
                    continue
                else:
                    break

            elif result == "win":
                current_coins = end_coins # LƯU TRỮ COIN CUỐI CÙNG
                current_keys = end_keys   # LƯU TRỮ KEY CUỐI CÙNG
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
