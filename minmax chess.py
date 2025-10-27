import sys
import math
import copy
import time
import random
from enum import Enum

# Define enums and pieces
class PieceType(Enum):
    PAWN = 1
    ROOK = 2
    KNIGHT = 3
    BISHOP = 4
    QUEEN = 5
    KING = 6

class Color(Enum):
    WHITE = 1
    BLACK = 2

class Piece:
    def __init__(self, piece_type, color):
        self.type = piece_type
        self.color = color
        self.has_moved = False

    def __repr__(self):
        symbols = {
            (PieceType.PAWN, Color.WHITE): '♙',
            (PieceType.ROOK, Color.WHITE): '♖',
            (PieceType.KNIGHT, Color.WHITE): '♘',
            (PieceType.BISHOP, Color.WHITE): '♗',
            (PieceType.QUEEN, Color.WHITE): '♕',
            (PieceType.KING, Color.WHITE): '♔',
            (PieceType.PAWN, Color.BLACK): '♟',
            (PieceType.ROOK, Color.BLACK): '♜',
            (PieceType.KNIGHT, Color.BLACK): '♞',
            (PieceType.BISHOP, Color.BLACK): '♝',
            (PieceType.QUEEN, Color.BLACK): '♛',
            (PieceType.KING, Color.BLACK): '♚',
        }
        return symbols.get((self.type, self.color), '?')

class Move:
    def __init__(self, from_pos, to_pos, captured_piece=None):
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.captured_piece = captured_piece

# Chessboard logic
class ChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.current_turn = Color.WHITE
        self.move_history = []
        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)
        self.setup_initial_position()

    def setup_initial_position(self):
        for col in range(8):
            self.board[1][col] = Piece(PieceType.PAWN, Color.BLACK)
            self.board[6][col] = Piece(PieceType.PAWN, Color.WHITE)
        piece_order = [PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP,
                      PieceType.QUEEN, PieceType.KING, PieceType.BISHOP,
                      PieceType.KNIGHT, PieceType.ROOK]
        for col in range(8):
            self.board[0][col] = Piece(piece_order[col], Color.BLACK)
            self.board[7][col] = Piece(piece_order[col], Color.WHITE)

    def get_piece(self, row, col):
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None

    def set_piece(self, row, col, piece):
        if 0 <= row < 8 and 0 <= col < 8:
            self.board[row][col] = piece

    def is_valid_position(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8

    def print_board(self):
        print("  a b c d e f g h")
        for row in range(8):
            print(f"{8-row} ", end="")
            for col in range(8):
                piece = self.get_piece(row, col)
                print(f"{piece if piece else '.'} ", end="")
            print(f"{8-row}")
        print("  a b c d e f g h")
        print(f"Turn: {'White' if self.current_turn == Color.WHITE else 'Black'}")

    def get_possible_moves(self, row, col):
        piece = self.get_piece(row, col)
        if not piece or piece.color != self.current_turn:
            return []
        moves = []
        if piece.type == PieceType.PAWN:
            moves = self._get_pawn_moves(row, col)
        elif piece.type == PieceType.ROOK:
            moves = self._get_rook_moves(row, col)
        elif piece.type == PieceType.KNIGHT:
            moves = self._get_knight_moves(row, col)
        elif piece.type == PieceType.BISHOP:
            moves = self._get_bishop_moves(row, col)
        elif piece.type == PieceType.QUEEN:
            moves = self._get_queen_moves(row, col)
        elif piece.type == PieceType.KING:
            moves = self._get_king_moves(row, col)
        valid_moves = []
        for move in moves:
            if not self.would_be_in_check_after_move(move):
                valid_moves.append(move)
        return valid_moves

    def _get_pawn_moves(self, row, col):
        moves = []
        piece = self.get_piece(row, col)
        direction = -1 if piece.color == Color.WHITE else 1
        start_row = 6 if piece.color == Color.WHITE else 1
        new_row = row + direction
        if self.is_valid_position(new_row, col) and not self.get_piece(new_row, col):
            moves.append(Move((row, col), (new_row, col)))
            if row == start_row and not self.get_piece(new_row + direction, col):
                moves.append(Move((row, col), (new_row + direction, col)))
        for dc in [-1, 1]:
            new_row, new_col = row + direction, col + dc
            if self.is_valid_position(new_row, new_col):
                target = self.get_piece(new_row, new_col)
                if target and target.color != piece.color:
                    moves.append(Move((row, col), (new_row, new_col), target))
        return moves

    def _get_rook_moves(self, row, col):
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + i * dr, col + i * dc
                if not self.is_valid_position(new_row, new_col):
                    break
                target = self.get_piece(new_row, new_col)
                if not target:
                    moves.append(Move((row, col), (new_row, new_col)))
                else:
                    if target.color != self.get_piece(row, col).color:
                        moves.append(Move((row, col), (new_row, new_col), target))
                    break
        return moves

    def _get_knight_moves(self, row, col):
        moves = []
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            if self.is_valid_position(new_row, new_col):
                target = self.get_piece(new_row, new_col)
                if not target or target.color != self.get_piece(row, col).color:
                    moves.append(Move((row, col), (new_row, new_col), target))
        return moves

    def _get_bishop_moves(self, row, col):
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + i * dr, col + i * dc
                if not self.is_valid_position(new_row, new_col):
                    break
                target = self.get_piece(new_row, new_col)
                if not target:
                    moves.append(Move((row, col), (new_row, new_col)))
                else:
                    if target.color != self.get_piece(row, col).color:
                        moves.append(Move((row, col), (new_row, new_col), target))
                    break
        return moves

    def _get_queen_moves(self, row, col):
        return self._get_rook_moves(row, col) + self._get_bishop_moves(row, col)

    def _get_king_moves(self, row, col):
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0),
                      (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self.is_valid_position(new_row, new_col):
                target = self.get_piece(new_row, new_col)
                if not target or target.color != self.get_piece(row, col).color:
                    moves.append(Move((row, col), (new_row, new_col), target))
        return moves

    def make_move(self, move):
        from_row, from_col = move.from_pos
        to_row, to_col = move.to_pos
        piece = self.get_piece(from_row, from_col)
        if not piece:
            return False
        move.captured_piece = self.get_piece(to_row, to_col)
        self.set_piece(to_row, to_col, piece)
        self.set_piece(from_row, from_col, None)
        if piece.type == PieceType.KING:
            if piece.color == Color.WHITE:
                self.white_king_pos = (to_row, to_col)
            else:
                self.black_king_pos = (to_row, to_col)
        piece.has_moved = True
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        self.move_history.append(move)
        return True

    def undo_move(self, move):
        from_row, from_col = move.from_pos
        to_row, to_col = move.to_pos
        piece = self.get_piece(to_row, to_col)
        self.set_piece(from_row, from_col, piece)
        self.set_piece(to_row, to_col, move.captured_piece)
        if piece and piece.type == PieceType.KING:
            if piece.color == Color.WHITE:
                self.white_king_pos = (from_row, from_col)
            else:
                self.black_king_pos = (from_row, from_col)
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        if self.move_history and self.move_history[-1] == move:
            self.move_history.pop()

    def is_in_check(self, color):
        king_pos = self.white_king_pos if color == Color.WHITE else self.black_king_pos
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color != color:
                    original_turn = self.current_turn
                    self.current_turn = piece.color
                    moves = self._get_raw_moves(row, col)
                    self.current_turn = original_turn
                    for move in moves:
                        if move.to_pos == king_pos:
                            return True
        return False

    def _get_raw_moves(self, row, col):
        piece = self.get_piece(row, col)
        if not piece:
            return []
        if piece.type == PieceType.PAWN: return self._get_pawn_moves(row, col)
        elif piece.type == PieceType.ROOK: return self._get_rook_moves(row, col)
        elif piece.type == PieceType.KNIGHT: return self._get_knight_moves(row, col)
        elif piece.type == PieceType.BISHOP: return self._get_bishop_moves(row, col)
        elif piece.type == PieceType.QUEEN: return self._get_queen_moves(row, col)
        elif piece.type == PieceType.KING: return self._get_king_moves(row, col)
        return []

    def would_be_in_check_after_move(self, move):
        original_board = copy.deepcopy(self.board)
        original_turn = self.current_turn
        original_white_king = self.white_king_pos
        original_black_king = self.black_king_pos
        self.make_move(move)
        previous_color = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        in_check = self.is_in_check(previous_color)
        self.board = original_board
        self.current_turn = original_turn
        self.white_king_pos = original_white_king
        self.black_king_pos = original_black_king
        return in_check

    def get_all_possible_moves(self, color):
        moves = []
        original_turn = self.current_turn
        self.current_turn = color
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    moves.extend(self.get_possible_moves(row, col))
        self.current_turn = original_turn
        return moves

    def is_checkmate(self, color):
        if not self.is_in_check(color): return False
        return len(self.get_all_possible_moves(color)) == 0

    def is_stalemate(self, color):
        if self.is_in_check(color): return False
        return len(self.get_all_possible_moves(color)) == 0

# Minimax AI
class ChessAI:
    def __init__(self, depth=3):
        self.depth = depth
        self.piece_values = {
            PieceType.PAWN: 1,
            PieceType.KNIGHT: 3,
            PieceType.BISHOP: 3,
            PieceType.ROOK: 5,
            PieceType.QUEEN: 9,
            PieceType.KING: 100,
        }

    def evaluate_board(self, board):
        score = 0
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece:
                    value = self.piece_values[piece.type]
                    score += value if piece.color == Color.BLACK else -value
        return score

    def minimax(self, board, depth, alpha, beta, maximizing):
        current_color = Color.BLACK if maximizing else Color.WHITE
        if depth == 0 or board.is_checkmate(current_color) or board.is_stalemate(current_color):
            return self.evaluate_board(board)
        moves = board.get_all_possible_moves(current_color)
        if maximizing:
            max_eval = -math.inf
            for move in moves:
                board.make_move(move)
                eval = self.minimax(board, depth - 1, alpha, beta, False)
                board.undo_move(move)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha: break
            return max_eval
        else:
            min_eval = math.inf
            for move in moves:
                board.make_move(move)
                eval = self.minimax(board, depth - 1, alpha, beta, True)
                board.undo_move(move)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha: break
            return min_eval

    def get_best_move(self, board, color):
        moves = board.get_all_possible_moves(color)
        if not moves: return None
        best_move = None
        if color == Color.BLACK:
            best_val = -math.inf
            for move in moves:
                board.make_move(move)
                value = self.minimax(board, self.depth-1, -math.inf, math.inf, False)
                board.undo_move(move)
                if value > best_val:
                    best_val = value
                    best_move = move
        else:
            best_val = math.inf
            for move in moves:
                board.make_move(move)
                value = self.minimax(board, self.depth-1, -math.inf, math.inf, True)
                board.undo_move(move)
                if value < best_val:
                    best_val = value
                    best_move = move
        return best_move

# Console game driver
class ChessGame:
    def __init__(self):
        self.board = ChessBoard()
        self.ai = ChessAI(depth=3)  # Change depth for stronger/weaker AI
        self.human_color = Color.WHITE
        self.ai_color = Color.BLACK

    def parse_position(self, pos):
        if len(pos) != 2: return None
        col = ord(pos[0]) - ord('a')
        row = 8 - int(pos[1])
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None

    def position_to_notation(self, row, col):
        return chr(ord('a') + col) + str(8 - row)

    def get_human_move(self):
        while True:
            user_input = input("Enter your move (e.g. e2 e4), or 'quit' to exit: ").strip().lower()
            if user_input == 'quit':
                sys.exit()
            parts = user_input.split()
            if len(parts) != 2: print("Use format: e2 e4"); continue
            from_pos = self.parse_position(parts[0])
            to_pos = self.parse_position(parts[1])
            if not from_pos or not to_pos: print("Invalid positions."); continue
            piece = self.board.get_piece(*from_pos)
            if not piece: print("No piece at position."); continue
            if piece.color != self.human_color: print("That's not your piece."); continue
            moves = self.board.get_possible_moves(*from_pos)
            for move in moves:
                if move.to_pos == to_pos:
                    return move
            print("Illegal move! Try again.")

    def play_game(self):
        print("=== Welcome to Chess! ===")
        print("You play as White. Enter moves like 'e2 e4'")
        while True:
            self.board.print_board()
            if self.board.is_checkmate(self.board.current_turn):
                winner = "Black" if self.board.current_turn == Color.WHITE else "White"
                print(f"Checkmate! {winner} wins!")
                break
            if self.board.is_stalemate(self.board.current_turn):
                print("Stalemate! Draw game.")
                break
            if self.board.current_turn == self.human_color:
                move = self.get_human_move()
                self.board.make_move(move)
            else:
                print("AI is thinking...")
                move = self.ai.get_best_move(self.board, self.ai_color)
                if move is None:
                    print("AI has no legal moves!")
                    break
                self.board.make_move(move)
                piece = self.board.get_piece(*move.to_pos)
                print(f"AI moves {piece} from {self.position_to_notation(*move.from_pos)} to {self.position_to_notation(*move.to_pos)}")
                if move.captured_piece:
                    print(f"AI captured your {move.captured_piece}!")

if __name__ == '__main__':
    game = ChessGame()
    game.play_game()
