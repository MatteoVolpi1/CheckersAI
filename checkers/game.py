import pygame
from .constants import RED, WHITE, BLUE, SQUARE_SIZE
from checkers.board import Board

class Game:
    def __init__(self, win):
        self._init()
        self.win = win

    def update(self):
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    #privato con underscore davanti
    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = RED
        self.valid_moves = {}

    def reset(self):
        self._init()

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            #print("is attacking pawn: ", self.board.is_attacking_pawn(self.board.get_piece(row,col)))
            if not result:
                #deselect piece, player selected an empty tile
                self.selected = None
                self.select(row, col)
                self._remove_valid_moves()

        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            #print("piece: ", piece, " moves: ", self.valid_moves)
            return True
        
        return False

    def _move(self, row, col): 
        piece = self.board.get_piece(row, col)
        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
            self.change_turn()
        else:
            return False
        
        return True
    
    def change_turn(self):
        self._remove_valid_moves()
        if self.turn == RED:
            self.turn = WHITE
        else:
            self.turn = RED

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.win, BLUE, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), 15)

    def _remove_valid_moves(self):
        self.valid_moves = {}

    def winner(self):
        return self.board.winner()
    
    def match_is_draw(self, piece):
        if len(self.board.get_valid_moves(piece)) == 0:
            return True
        return False

    
    def get_board(self):
        return self.board
    
    def ai_move(self, board): #returns the new updated board object
        self.board = board
        self.change_turn()
