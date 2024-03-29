import pygame
import datetime
from checkers.constants import WIDTH, HEIGHT, SQUARE_SIZE, RED, WHITE
from checkers.game import Game
from minimax.algorithm import minimax_alpha_beta

#Inspired by Paulo Padrao and TechWithTim

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Checkers')

FPS = 45
AI_DEPTH = 5    # how many moves ahead the AI looks at (careful! I reccomend 5)
AI_ENABLED = True  #play with/without AI

def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def main():
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)

    while run:
        clock.tick(FPS)

        if game.board.is_winner(RED):
            print("game over, RED won!")
            run = False
            break

        if game.turn == WHITE and AI_ENABLED:
            start = datetime.datetime.now()
            value, new_board = minimax_alpha_beta(game.get_board(), AI_DEPTH, float('-inf'), float('inf'), WHITE, game)
            end = datetime.datetime.now()
            print("[",(end - start).total_seconds()," s] value: ", value)
            game.ai_move(new_board)

        if game.board.is_winner(WHITE):
            print("game over, WHITE won!")
            run = False
            break
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                #if game.turn == RED:
                game.select(row, col)
        
        game.update()

    pygame.quit()
         

main()