import chess
import chess.engine
import random
import math

# --- 1. Piece Values for Evaluation ---
class PieceValues:
    """
    Simple piece-square table values for chess evaluation. 
    These values are crucial for the AI's "understanding" of the board.
    Values are from White's perspective.
    """
    PAWN_W = [
        0, 0, 0, 0, 0, 0, 0, 0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5, 5, 10, 25, 25, 10, 5, 5,
        0, 0, 0, 20, 20, 0, 0, 0,
        5, -5, -10, 0, 0, -10, -5, 5,
        5, 10, 10, -20, -20, 10, 10, 5,
        0, 0, 0, 0, 0, 0, 0, 0
    ]
    # Reverse the tables for Black's pieces since the board is flipped
    PAWN_B = PAWN_W[::-1] 

    # General piece values
    MATERIAL_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000  # King value is high to ensure we protect it
    }

# --- 2. Minimax AI Agent ---
class MinimaxAI:
    """
    A simple AI agent using the Minimax algorithm with Alpha-Beta Pruning.
    """
    def __init__(self, depth=3):
        self.depth = depth

    def evaluate_board(self, board):
        """
        Calculates the material advantage for the current board state.
        A positive score is good for White (maximizer), a negative score 
        is good for Black (minimizer).
        """
        if board.is_checkmate():
            # Checkmate is the highest/lowest score possible
            if board.turn == chess.BLACK:
                return 100000000  # White checkmated Black (White wins)
            else:
                return -100000000 # Black checkmated White (Black wins)
        
        if board.is_stalemate() or board.is_insufficient_material() or board.is_fivefold_repetition():
            return 0 # Draw

        score = 0
        
        for piece_type in PieceValues.MATERIAL_VALUES:
            # White pieces
            for square in board.pieces(piece_type, chess.WHITE):
                score += PieceValues.MATERIAL_VALUES[piece_type]
                # Add piece-square table bonus for pawns
                if piece_type == chess.PAWN:
                    score += PieceValues.PAWN_W[square]
            
            # Black pieces
            for square in board.pieces(piece_type, chess.BLACK):
                score -= PieceValues.MATERIAL_VALUES[piece_type]
                # Add piece-square table bonus for pawns (subtracted)
                if piece_type == chess.PAWN:
                    score -= PieceValues.PAWN_B[square]
        
        # Simple bonus for center control, etc., can be added here
        
        return score

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        """
        The core recursive Minimax algorithm with Alpha-Beta Pruning.
        """
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board)

        # Iterate through moves in a random order to avoid predictable play patterns
        moves = list(board.legal_moves)
        # Simple move ordering: captures first
        moves.sort(key=lambda move: self.get_move_value(board, move), reverse=True) 

        if maximizing_player:
            max_eval = -math.inf
            for move in moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, max_eval)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval
        else:
            min_eval = math.inf
            for move in moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, min_eval)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval
    
    def get_move_value(self, board, move):
        """A simple heuristic to prioritize captures."""
        if board.is_capture(move):
            # Assign a high value to captures (higher for more valuable pieces)
            captured_piece = board.piece_at(move.to_square)
            if captured_piece:
                return PieceValues.MATERIAL_VALUES.get(captured_piece.piece_type, 0) + 1000 # +1000 to prioritize captures
            return 1000
        return 0

    def find_best_move(self, board):
        """
        Searches for the best move using Minimax.
        """
        best_move = None
        
        # White is the maximizing player, Black is the minimizing player
        if board.turn == chess.WHITE:
            max_eval = -math.inf
            maximizing_player = True
        else:
            max_eval = math.inf
            maximizing_player = False

        # Randomize moves initially to break ties and make openings less predictable
        moves = list(board.legal_moves)
        random.shuffle(moves)
        
        # Simple move ordering: captures first
        moves.sort(key=lambda move: self.get_move_value(board, move), reverse=True)

        for move in moves:
            board.push(move)
            # Alpha and Beta start at the worst possible values for both players
            current_eval = self.minimax(board, self.depth - 1, -math.inf, math.inf, not maximizing_player)
            board.pop()

            if maximizing_player and current_eval > max_eval:
                max_eval = current_eval
                best_move = move
            elif not maximizing_player and current_eval < max_eval:
                max_eval = current_eval
                best_move = move

        return best_move

# --- 3. Main Game Loop ---
class ChessGame:
    def __init__(self, ai_depth=3):
        self.board = chess.Board()
        self.ai_agent = MinimaxAI(depth=ai_depth)
        print("🤖 Chess Game Initialized! You are White.")
        print(f"AI Depth: {ai_depth}")

    def play(self):
        """
        Main loop for the human-vs-AI game.
        """
        while not self.board.is_game_over():
            print("\n" + "="*20)
            print(self.board)
            print("="*20)

            if self.board.turn == chess.WHITE:
                # Human Player (White)
                try:
                    uci_move = input("Your move (e.g., e2e4): ")
                    move = chess.Move.from_uci(uci_move)
                    
                    if move in self.board.legal_moves:
                        self.board.push(move)
                    else:
                        print("Illegal move. Try again.")
                        continue
                except ValueError:
                    print("Invalid move format. Use UCI format (e.g., e2e4).")
                    continue
            
            else:
                # AI Player (Black)
                print("AI is thinking...")
                ai_move = self.ai_agent.find_best_move(self.board)
                if ai_move:
                    print(f"AI plays: {ai_move.uci()}")
                    self.board.push(ai_move)
                else:
                    # Should only happen if the game is over but not yet detected
                    print("AI couldn't find a move.")
                    break
        
        # Game Over
        print("\n*** GAME OVER ***")
        print(self.board.result())
        print(self.board)


# --- Run the Game ---
if __name__ == "__main__":
    # A depth of 3 is a good balance for a quick demonstration.
    # Higher depth (4 or 5) will make the AI much stronger but slower.
    game = ChessGame(ai_depth=3) 
    game.play()
