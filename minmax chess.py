# Chess game with Minimax AI
import pygame
import sys
import math
from enum import Enum
from typing import List, Tuple, Optional, Dict

# Initialize pygame
pygame.init()

# Constants
BOARD_SIZE = 640
SQUARE_SIZE = BOARD_SIZE // 8
WHITE = (240, 217, 181)
BLACK = (181, 136, 99)
HIGHLIGHT = (255, 255, 0, 128)
POSSIBLE_MOVE = (0, 255, 0, 128)

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
    def __init__(self, piece_type: PieceType, color: Color):
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
    def __init__(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], captured_piece=None):
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.captured_piece = captured_piece
        self.promotion = None
        self.is_castling = False
        self.is_en_passant = False

class ChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.current_turn = Color.WHITE
        self.move_history = []
        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)
        self.en_passant_target = None
        self.setup_initial_position()
    
    def setup_initial_position(self):
        # Set up pawns
        for col in range(8):
            self.board[1][col] = Piece(PieceType.PAWN, Color.BLACK)
            self.board[6][col] = Piece(PieceType.PAWN, Color.WHITE)
        
        # Set up other pieces
        piece_order = [PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, 
                      PieceType.QUEEN, PieceType.KING, PieceType.BISHOP, 
                      PieceType.KNIGHT, PieceType.ROOK]
        
        for col in range(8):
            self.board[0][col] = Piece(piece_order[col], Color.BLACK)
            self.board[7][col] = Piece(piece_order[col], Color.WHITE)
    
    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None
    
    def set_piece(self, row: int, col: int, piece: Optional[Piece]):
        if 0 <= row < 8 and 0 <= col < 8:
            self.board[row][col] = piece
    
    def is_valid_position(self, row: int, col: int) -> bool:
        return 0 <= row < 8 and 0 <= col < 8
    
    def get_possible_moves(self, row: int, col: int) -> List[Move]:
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
        
        # Filter out moves that would put own king in check
        valid_moves = []
        for move in moves:
            if not self.would_be_in_check_after_move(move):
                valid_moves.append(move)
        
        return valid_moves
    
    def _get_pawn_moves(self, row: int, col: int) -> List[Move]:
        moves = []
        piece = self.get_piece(row, col)
        direction = -1 if piece.color == Color.WHITE else 1
        start_row = 6 if piece.color == Color.WHITE else 1
        
        # Move forward one square
        new_row = row + direction
        if self.is_valid_position(new_row, col) and not self.get_piece(new_row, col):
            moves.append(Move((row, col), (new_row, col)))
            
            # Move forward two squares from starting position
            if row == start_row and not self.get_piece(new_row + direction, col):
                moves.append(Move((row, col), (new_row + direction, col)))
        
        # Capture diagonally
        for dc in [-1, 1]:
            new_row, new_col = row + direction, col + dc
            if self.is_valid_position(new_row, new_col):
                target = self.get_piece(new_row, new_col)
                if target and target.color != piece.color:
                    moves.append(Move((row, col), (new_row, new_col), target))
        
        return moves
    
    def _get_rook_moves(self, row: int, col: int) -> List[Move]:
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
    
    def _get_knight_moves(self, row: int, col: int) -> List[Move]:
        moves = []
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), 
                       (1, -2), (1, 2), (2, -1), (2, 1)]
        
        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            if self.is_valid_position(new_row, new_col):
                target = self.get_piece(new_row, new_col)
                if not target or target.color != self.get_piece(row, col).color:
                    moves.append(Move((row, col), (new_row, new_col), target))
        
        return moves
    
    def _get_bishop_moves(self, row: int, col: int) -> List[Move]:
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
    
    def _get_queen_moves(self, row: int, col: int) -> List[Move]:
        return self._get_rook_moves(row, col) + self._get_bishop_moves(row, col)
    
    def _get_king_moves(self, row: int, col: int) -> List[Move]:
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
    
    def make_move(self, move: Move) -> bool:
        from_row, from_col = move.from_pos
        to_row, to_col = move.to_pos
        
        piece = self.get_piece(from_row, from_col)
        if not piece:
            return False
        
        # Store captured piece
        move.captured_piece = self.get_piece(to_row, to_col)
        
        # Move the piece
        self.set_piece(to_row, to_col, piece)
        self.set_piece(from_row, from_col, None)
        
        # Update king position
        if piece.type == PieceType.KING:
            if piece.color == Color.WHITE:
                self.white_king_pos = (to_row, to_col)
            else:
                self.black_king_pos = (to_row, to_col)
        
        # Mark piece as moved
        piece.has_moved = True
        
        # Switch turn
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        
        # Add to move history
        self.move_history.append(move)
        
        return True
    
    def undo_move(self, move: Move):
        from_row, from_col = move.from_pos
        to_row, to_col = move.to_pos
        
        piece = self.get_piece(to_row, to_col)
        
        # Move piece back
        self.set_piece(from_row, from_col, piece)
        self.set_piece(to_row, to_col, move.captured_piece)
        
        # Update king position
        if piece and piece.type == PieceType.KING:
            if piece.color == Color.WHITE:
                self.white_king_pos = (from_row, from_col)
            else:
                self.black_king_pos = (from_row, from_col)
        
        # Switch turn back
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        
        # Remove from move history
        if self.move_history and self.move_history[-1] == move:
            self.move_history.pop()
    
    def is_in_check(self, color: Color) -> bool:
        king_pos = self.white_king_pos if color == Color.WHITE else self.black_king_pos
        
        # Check if any opponent piece can attack the king
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color != color:
                    # Temporarily switch turn to get opponent moves
                    original_turn = self.current_turn
                    self.current_turn = piece.color
                    moves = self._get_raw_moves(row, col)
                    self.current_turn = original_turn
                    
                    for move in moves:
                        if move.to_pos == king_pos:
                            return True
        return False
    
    def _get_raw_moves(self, row: int, col: int) -> List[Move]:
        """Get moves without checking for check (to avoid infinite recursion)"""
        piece = self.get_piece(row, col)
        if not piece:
            return []
        
        if piece.type == PieceType.PAWN:
            return self._get_pawn_moves(row, col)
        elif piece.type == PieceType.ROOK:
            return self._get_rook_moves(row, col)
        elif piece.type == PieceType.KNIGHT:
            return self._get_knight_moves(row, col)
        elif piece.type == PieceType.BISHOP:
            return self._get_bishop_moves(row, col)
        elif piece.type == PieceType.QUEEN:
            return self._get_queen_moves(row, col)
        elif piece.type == PieceType.KING:
            return self._get_king_moves(row, col)
        
        return []
    
    def would_be_in_check_after_move(self, move: Move) -> bool:
        # Make the move temporarily
        self.make_move(move)
        
        # Check if the king would be in check
        opponent_color = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        in_check = self.is_in_check(opponent_color)
        
        # Undo the move
        self.undo_move(move)
        
        return in_check
    
    def get_all_possible_moves(self, color: Color) -> List[Move]:
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    moves.extend(self.get_possible_moves(row, col))
        return moves
    
    def is_checkmate(self, color: Color) -> bool:
        if not self.is_in_check(color):
            return False
        return len(self.get_all_possible_moves(color)) == 0
    
    def is_stalemate(self, color: Color) -> bool:
        if self.is_in_check(color):
            return False
        return len(self.get_all_possible_moves(color)) == 0

print("Chess board and game logic created successfully!")
