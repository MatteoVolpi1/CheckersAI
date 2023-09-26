import pygame
from .constants import BLACK, ROWS, RED, SQUARE_SIZE, COLS, WHITE, BEIGE
from .piece import Piece

class Board:
    def __init__(self):
        self.board = []
        self.red_left = self.white_left = 12
        self.red_kings = self.white_kings = 0
        self.create_board()
    
    def draw_squares(self, win):
        win.fill(BLACK)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, BEIGE, (row*SQUARE_SIZE, col *SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def get_all_pieces(self, color):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        return pieces

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

        if row == ROWS - 1 or row == 0:
            piece.make_king()
            if piece.color == WHITE:
                self.white_kings += 1
            else:
                self.red_kings += 1 

    def get_piece(self, row, col):
        if row < 0 or row > ROWS - 1 or col < 0 or col > COLS - 1:
            return None
        return self.board[row][col]

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row +  1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, col, WHITE))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, RED))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)
        
    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece != 0:
                if piece.color == RED:
                    self.red_left -= 1
                else:
                    self.white_left -= 1
    
    def winner(self):
        if self.red_left <= 0:
            return WHITE
        elif self.white_left <= 0:
            return RED
        
        return None 
    
    def get_valid_moves(self, piece):
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == RED or piece.king:
            moves.update(self._traverse_left(row -1, max(row-3, -1), -1, piece.color, left, piece.king))
            moves.update(self._traverse_right(row -1, max(row-3, -1), -1, piece.color, right, piece.king))
        if piece.color == WHITE or piece.king:
            moves.update(self._traverse_left(row +1, min(row+3, ROWS), 1, piece.color, left, piece.king))
            moves.update(self._traverse_right(row +1, min(row+3, ROWS), 1, piece.color, right, piece.king))
        
        return moves

    def _traverse_left(self, start, stop, step, color, left, king, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break
            
            current = self.board[r][left]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last
                
                if last:
                    if step == -1:
                        row = max(r-3, -1)
                    else:
                        row = min(r+3, ROWS)
                    moves.update(self._traverse_left(r+step, row, step, color, left-1, king, skipped=last))
                    moves.update(self._traverse_right(r+step, row, step, color, left+1, king, skipped=last))
                    if king:
                        if step == -1:
                            moves.update(self._traverse_left(r-step, min(r+3, ROWS), -step, color, left-1, king, skipped=last))
                        else:
                            moves.update(self._traverse_left(r-step, max(r-3, -1), -step, color, left-1, king, skipped=last))
                        
                break
            elif current.color == color:
                break
            else:
                last = [current]

            left -= 1
        
        return moves

    def _traverse_right(self, start, stop, step, color, right, king, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break
            
            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r,right)] = last + skipped
                else:
                    moves[(r, right)] = last
                
                if last:
                    if step == -1:
                        row = max(r-3, -1)
                    else:
                        row = min(r+3, ROWS)
                    moves.update(self._traverse_left(r+step, row, step, color, right-1, king, skipped=last))
                    moves.update(self._traverse_right(r+step, row, step, color, right+1, king, skipped=last))
                    if king:
                        if king:
                            if step == -1:
                                moves.update(self._traverse_right(r-step, min(r+3, ROWS), -step, color, right+1, king, skipped=last))
                            else:
                                moves.update(self._traverse_right(r-step, max(r-3, -1), -step, color, right+1, king, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            right += 1
        
        return moves

    #doesn't check if is in danger in a chain of captures
    # TODO refactor
    def is_protected(self, piece):
        if piece.col == 0 or piece.col == COLS-1 or piece.row == 0 or piece.row == ROWS-1:
            return True
        attacker = self.get_piece(piece.row-1, piece.col-1)
        if attacker != 0:
            if piece.color != attacker.color and attacker.color == WHITE or attacker.king and self.get_piece(piece.row+1, piece.col+1) == 0:
                return False
        attacker = self.get_piece(piece.row-1, piece.col+1)
        if attacker != 0:
            if piece.color != attacker.color and attacker.color == WHITE or attacker.king and self.get_piece(piece.row+1, piece.col-1) == 0:
                return False
        attacker = self.get_piece(piece.row+1, piece.col-1)
        if attacker != 0:
            if piece.color != attacker.color and attacker.color == RED or attacker.king and self.get_piece(piece.row-1, piece.col+1) == 0:
                return False
        attacker = self.get_piece(piece.row+1, piece.col+1)
        if attacker != 0:
            if piece.color != attacker.color and attacker.color == RED or attacker.king and self.get_piece(piece.row-1, piece.col-1) == 0:
                return False
        return True
    
    def is_attacking_pawn(self, piece):
        res = False

        if piece.color == RED or piece.king:
            if piece.row - 2 >= 0 and (piece.col >= 2 or piece.col < COLS - 2):
                left_diagonal = self.get_piece(piece.row-1, piece.col-1)
                left_diagonal_next = self.get_piece(piece.row-2, piece.col-2)
                right_diagonal = self.get_piece(piece.row-1, piece.col+1)
                right_diagonal_next = self.get_piece(piece.row-2, piece.col+2)
                res = (left_diagonal is not None and left_diagonal != 0 and left_diagonal.color != piece.color and left_diagonal_next is not None and left_diagonal_next == 0) or (right_diagonal is not None and right_diagonal != 0 and right_diagonal.color != piece.color and right_diagonal_next is not None and right_diagonal_next == 0)
                if res or not piece.king:
                    return res
        
        if piece.color == WHITE or piece.king:
            if piece.row + 2 <= ROWS - 1 and (piece.col >= 2 or piece.col < COLS - 2):
                left_diagonal = self.get_piece(piece.row+1, piece.col-1)
                left_diagonal_next = self.get_piece(piece.row+2, piece.col-2)
                right_diagonal = self.get_piece(piece.row+1, piece.col+1)
                right_diagonal_next = self.get_piece(piece.row+2, piece.col+2)
                res = (left_diagonal is not None and left_diagonal != 0 and left_diagonal.color != piece.color and left_diagonal_next is not None and left_diagonal_next == 0) or (right_diagonal is not None and right_diagonal != 0 and right_diagonal.color != piece.color and right_diagonal_next is not None and right_diagonal_next == 0)
                if res or not piece.king:
                    return res
                
        return False
    
    #if is an attacking piece, it also movable. Could be removed from this function if used smartly
    def is_movable(self, piece):
        left_upper_diagonal = self.get_piece(piece.row-1, piece.col-1)
        right_upper_diagonal = self.get_piece(piece.row-1, piece.col+1)
        if piece.king or piece.color == RED and (left_upper_diagonal is not None and left_upper_diagonal == 0) or (right_upper_diagonal is not None and right_upper_diagonal == 0):
            return True
        left_lower_diagonal = self.get_piece(piece.row+1, piece.col-1)
        right_lower_diagonal = self.get_piece(piece.row+1, piece.col+1)
        if piece.king or piece.color == WHITE and (left_lower_diagonal is not None and left_lower_diagonal == 0)  or (right_lower_diagonal is not None and right_lower_diagonal == 0):
            return True
        else:
            return self.is_attacking_pawn(piece)

    #controllare correttezza da qui in poi

    def is_promotable(self, piece):
        if piece.king or piece.color == RED and piece.row != 1 or piece.color == WHITE and piece.row != 6:
            return False
        left_upper_diagonal = self.get_piece(piece.row-1, piece.col-1)
        right_upper_diagonal = self.get_piece(piece.row-1, piece.col+1)
        if piece.color == RED and (left_upper_diagonal is not None and left_upper_diagonal == 0) or (right_upper_diagonal is not None and right_upper_diagonal == 0):
            return True
        left_lower_diagonal = self.get_piece(piece.row+1, piece.col-1)
        right_lower_diagonal = self.get_piece(piece.row+1, piece.col+1)
        if piece.color == WHITE and (left_lower_diagonal is not None and left_lower_diagonal == 0)  or (right_lower_diagonal is not None and right_lower_diagonal == 0):
            return True
        return False

    def count_defender_pieces(self, color):
        count = 0
        if color == WHITE:
            for row in range(ROWS-2, ROWS):
                for col in range(0, COLS):
                    piece = self.get_piece(row, col)
                    if piece != 0 and piece.color == WHITE:
                        count += 1
            return count
        elif color == RED:
            for row in range(0, 2):
                for col in range(0, COLS):
                    piece = self.get_piece(row, col)
                    if piece != 0 and piece.color == RED:
                        count += 1
            return count
        return -1

    def count_unoccupied_promotion_tiles(self, color):   
        count = 0
        if color == WHITE:
            for col in range(0, COLS):
                if col % 2 == 0 and self.get_piece(ROWS-1, col) != 0:
                    count += 1
            return count
        elif color == RED:
            for col in range(0, COLS):
                if col % 2 == 1 and self.get_piece(0, col) != 0:
                    count += 1
            return count
        return -1 

    def is_loner_piece(self, piece):
        row, col = piece.row, piece.col
        neighbors = [(row-1, col-1), (row-1, col+1), (row+1, col-1), (row+1, col+1)]
        for r, c in neighbors:
            if r < 0 or r >= len(self.board) or c < 0 or c >= len(self.board[0]):
                continue  # Skip if neighbor is out of bounds
            neighbor_piece = self.get_piece(r, c)
            if neighbor_piece is not None and neighbor_piece != 0 and neighbor_piece.color == piece.color:
                return False  # Not a loner piece
        return True  # Loner piece

    def evaluate(self):
        return self.white_left - self.red_left + (self.white_kings * 0.5 - self.red_kings * 0.5)
    
    #Evaluates the given checkers board and returns a score representing the advantage of the current player
    def advanced_evaluate(self):
        
        num_pawns = 0
        num_kings = 0
        num_back_row = 0
        num_middle_4 = 0
        num_middle_2_rows = 0
        num_pawns_protected = 0

        for row in range(ROWS):
            for col in range(COLS):
                piece = self.get_piece(row, col)
                if piece != 0:  # not empty tile

                    if piece.color == WHITE:    # AI piece
                        num_pawns += 1
                        if piece.king:
                            num_kings += 1
                        if row == 0:
                            num_back_row += 1
                        if 2 <= row <= 5 and 2 <= col <= 5:
                            num_middle_4 += 1
                        if 3 <= row <= 4:
                            num_middle_2_rows += 1
                        if self.is_protected(piece):
                            num_pawns_protected += 1

                    elif piece.color == RED:    # player piece
                        num_pawns -= 1
                        if piece.king:
                            num_kings -= 1
                        if row == 0:
                            num_back_row -= 1
                        if 2 <= row <= 5 and 2 <= col <= 5:
                            num_middle_4 -= 1
                        if 3 <= row <= 4:
                            num_middle_2_rows -= 1
                        if self.is_protected(piece):
                            num_pawns_protected -= 1

        # Calculate the total score based on the factors
        score = 0
        score += num_pawns * 1
        score += num_kings * 3
        score += num_back_row * 2
        score += num_middle_4 * 1
        score += num_middle_2_rows * 2
        score += num_pawns_protected * 1

        return score
    
    #detects a bridge situation (RED has cells 30 and 32 occupied, or WHITE has cells 1 and 3 occupied)
    def is_bridge(self, color):
        piece1 = self.get_piece(7, 2)
        piece2 = self.get_piece(7, 6)
        piece3 = self.get_piece(0, 1)
        piece4 = self.get_piece(0, 5)
        if (color == RED and piece1 != 0 and piece1.color == RED and piece2 != 0 and piece2.color == RED) or \
            (color == WHITE and piece3 != 0 and piece3.color == WHITE and piece4 != 0 and piece4.color == WHITE):
            return True
        return False

    #detects a dog situation (RED in cell 32 and WHITE in cell 28, or WHITE in cell 1 and RED in cell 5)
    def is_dog(self, color):
        piece1 = self.get_piece(6, 7)
        piece2 = self.get_piece(7, 6)
        piece3 = self.get_piece(0, 1)
        piece4 = self.get_piece(1, 0)
        if (color == RED and piece1 != 0 and piece1.color == WHITE and piece2 != 0 and piece2.color == RED) or \
            (color == WHITE and piece3 != 0 and piece3.color == WHITE and piece4 != 0 and piece4.color == RED):
            return True
        return False
    
    #counts kings in corner situation (king in 4 or 29). Returns 2 - 0
    def king_in_corner(self, color):
        piece1 = self.get_piece(0, 7)
        piece2 = self.get_piece(7, 0)
        if (piece1 != 0 and piece1.color == color and piece1.king):
            if (piece2 != 0 and piece2.color == color and piece2.king):
                return 2
            return 1
        return 0
    
    #counts pawns in corner situation (RED pawn in 4 or WHITE pawn in 29)
    def is_pawn_in_corner(self, color):
        piece1 = self.get_piece(0, 7)
        piece2 = self.get_piece(7, 0)
        if (color == WHITE and piece1 != 0 and piece1.color == WHITE) or (color == RED and piece2 != 0 and piece2.color == RED):
            return True
        return False
    
    #detects a winning situation. A player wins when the opponent has no more pieces, or canno't move
    def is_winner(self, color):
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.get_piece(row, col)
                if piece != 0 and piece.color != color and self.is_movable(piece):
                    return False
        return True

    """
    Board rappresentation with cell numbers
    _______________________
    |   | 1 |   | 2 |   | 3 |   | 4 |
    |_______________________|
    | 5 |   | 6 |   | 7 |   | 8 |   |
    |_______________________|
    |   | 9 |   | 10|   | 11|   | 12|
    |_______________________|
    |13 |   |14 |   |15 |   |16 |   |
    |_______________________|
    |   |17 |   |18 |   |19 |   |20|
    |_______________________|
    |21 |   |22 |   |23 |   |24 |   |
    |_______________________|
    |   |25 |   |26 |   |27 |   |28|
    |_______________________|
    |29 |   |30 |   |31 |   |32 |   |
    |_______________________|
    """

    def evaluate_22F(self):

        """
        Evaluates the current state of the checkers board for the given player.

        Args:
        - board: A list of lists representing the checkers board.

        Returns:
        - score: A float representing the score of the board for the given player.
        """

        # Define some weights for the different features we will evaluate
        pawn_weight = 4  # Weight for the number of pawns 1.5 2.5 4 
        king_weight = 7.25  # Weight for the number of kings 2 4 7.25
        distance_weight = 0.2  # Weight for the aggregated distance to promotion line
        save_pawn_weight = 0.2  # Weight for saving pawns
        save_king_weight = 0.4  # Weight for saving kings
        attacking_pawn_weight = 0.1  # Weight for attacking pawns
        central_pawn_weight = 0.3  # Weight for centrally positioned pawns
        central_king_weight = 0.5  # Weight for centrally positioned kings
        movable_pawn_weight = 0.1  # Weight for movable pawns
        movable_king_weight = 0.2  # Weight for movable kings
        unoccupied_promotion_weight = 0.4  # Weight for unoccupied fields on promotion line
        defender_weight = 0.1  # Weight for defender pieces
        main_diagonal_pawn_weight = 0.2  # Weight for pawns on the main diagonal
        main_diagonal_king_weight = 0.3  # Weight for kings on the main diagonal
        double_diagonal_pawn_weight = 0.1  # Weight for pawns on the double diagonal
        double_diagonal_king_weight = 0.2  # Weight for kings on the double diagonal
        loner_pawn_weight = 0.2  # Weight for loner pawns
        loner_king_weight = 0.3  # Weight for loner kings

        #Boolean conditions
        blitz_weight = 0.5 # Weight for a blitz situation
        bridge_weight = 0.5 # Weight for a bridge situation
        dog_weight = -0.5 # Weight for a dog situation
        king_in_corner_weight = -0.5 # Weight for a king in corner situation
        pawn_in_corner_weight = -0.3 # Weight for a pawn in corner situation
        winning_weight = 10000 # Weight for a winning situation

        num_pawns = 0
        num_kings = 0
        distance_score = 0
        save_pawn_score = 0
        save_king_score = 0
        attacking_pawn_score = 0
        central_pawn_score = 0
        central_king_score = 0
        movable_pawn_score = 0
        movable_king_score = 0
        unoccupied_promotion_score = self.count_unoccupied_promotion_tiles(WHITE) - self.count_unoccupied_promotion_tiles(WHITE)
        defender_score = self.count_defender_pieces(WHITE) - self.count_defender_pieces(RED)
        main_diagonal_pawn_score = 0
        main_diagonal_king_score = 0
        double_diagonal_pawn_score = 0
        double_diagonal_king_score = 0
        loner_pawn_score = 0
        loner_king_score = 0

        #Boolean conditions
        bridge_score = (1 if self.is_bridge(WHITE) else 0) - (1 if self.is_bridge(RED) else 0)
        bridge_score *= bridge_weight
        dog_score = (1 if self.is_dog(RED) else 0) - (1 if self.is_dog(WHITE) else 0)
        dog_score *= dog_weight
        king_in_corner_score = self.king_in_corner(RED) - self.king_in_corner(WHITE)
        king_in_corner_score *= king_in_corner_weight
        pawn_in_corner_score = (1 if self.is_pawn_in_corner(RED) else 0) - (1 if self.is_pawn_in_corner(WHITE) else 0)
        pawn_in_corner_score *= pawn_in_corner_weight
        winning_score = (1 if self.is_winner(WHITE) else 0) - (1 if self.is_winner(RED) else 0)
        winning_score *= winning_weight


        for row in range(ROWS):
            for col in range(COLS):
                piece = self.get_piece(row, col)
                if piece != 0:  # not empty tile

                    if piece.color == WHITE:    # AI piece
                        num_pawns += 1
                        if self.is_attacking_pawn(piece):
                            attacking_pawn_score += 1
                        if piece.king:  #king
                            num_kings += 1
                            if self.is_protected(piece):
                                save_king_score += 1
                            if row in [2,5] and col in [2,5]:
                                central_king_score += 1
                            if self.is_movable(piece):
                                movable_king_score += 1
                            if row == col:
                                main_diagonal_king_score += 1
                            if abs(row + col - 7) == 2:
                                double_diagonal_king_score += 1
                            if self.is_loner_piece(piece):
                                loner_king_score -= 1
                                
                        else:   #pawn
                            distance_score -= ROWS - 1 - row 
                            if self.is_protected(piece):
                                save_pawn_score += 1
                            if row in [2,5] and col in [2,5]:
                                central_pawn_score += 1
                            if self.is_movable(piece):
                                movable_pawn_score += 1
                            if row == col:
                                main_diagonal_pawn_score += 1
                            if abs(row + col - 7) == 2:
                                double_diagonal_pawn_score += 1
                            if self.is_loner_piece(piece):
                                loner_pawn_score -= 1

                    elif piece.color == RED:    # player piece
                        num_pawns -= 1
                        if self.is_attacking_pawn(piece):
                            attacking_pawn_score -= 1
                        if piece.king:  #king
                            num_kings -= 1
                            if self.is_protected(piece):
                                save_king_score -= 1
                            if row in [2,5] and col in [2,5]:
                                central_king_score -= 1
                            if self.is_movable(piece):
                                movable_king_score -= 1
                            if row == col:
                                main_diagonal_king_score -= 1
                            if abs(row + col - 7) == 2:
                                double_diagonal_king_score -= 1
                            if self.is_loner_piece(piece):
                                loner_king_score += 1
                        else:   #pawn
                            distance_score += row
                            if self.is_protected(piece):
                                save_pawn_score -= 1
                            if row in [2,5] and col in [2,5]:
                                central_pawn_score -= 1
                            if self.is_movable(piece):
                                movable_pawn_score -= 1
                            if row == col:
                                main_diagonal_pawn_score -= 1
                            if abs(row + col - 7) == 2:
                                double_diagonal_pawn_score -= 1
                            if self.is_loner_piece(piece):
                                loner_pawn_score += 1


        # Calculate the score based on the number of pieces and kings
        pawn_score = pawn_weight * num_pawns
        king_score = king_weight * num_kings
        score = pawn_score + king_score

        # Calculate the score based on the aggregated distance to promotion line
        distance_score *= distance_weight
        score += distance_score

        # Calculate the score based on saving pawns and kings
        save_pawn_score *= save_pawn_weight
        save_king_score *= save_king_weight
        score += save_pawn_score + save_king_score

        # Calculate the score based on attacking pawns
        attacking_pawn_score *= attacking_pawn_weight
        score += attacking_pawn_score

        # Calculate the score based on centrally positioned pawns and kings
        central_pawn_score *= central_pawn_weight
        central_king_score *= central_king_weight
        score += central_pawn_score + central_king_score

        # Calculate the score based on movable pawns and kings
        movable_pawn_score *= movable_pawn_weight
        movable_king_score *= movable_king_weight
        score += movable_pawn_score + movable_king_score

        # Calculate the score based on unoccupied fields on promotion line
        unoccupied_promotion_score *= unoccupied_promotion_weight
        score += unoccupied_promotion_score

        # Calculate the score based on defender pieces
        defender_score *= defender_weight
        score += defender_score

        # Calculate the score based on pieces on the main diagonal
        main_diagonal_pawn_score *= main_diagonal_pawn_weight
        main_diagonal_king_score *= main_diagonal_king_weight
        score += main_diagonal_pawn_score + main_diagonal_king_score

        # Calculate the score based on pieces on the double diagonal
        double_diagonal_pawn_score *= double_diagonal_pawn_weight
        double_diagonal_king_score *= double_diagonal_king_weight
        score += double_diagonal_pawn_score + double_diagonal_king_score

        # Calculate the score based on loner pieces
        loner_pawn_score *= loner_pawn_weight
        loner_king_score *= loner_king_weight
        score += loner_pawn_score + loner_king_score

        # Calculate the score based on bridge situation
        score += bridge_score

        # Calculate the score based on dog situation
        score += dog_score

        # Calculate the score based on king in corner situation
        score += king_in_corner_score

        # Calculate the score based on king in corner situation
        score += pawn_in_corner_score

        # Calculate the score based on winning situation
        score += winning_score

        return score
