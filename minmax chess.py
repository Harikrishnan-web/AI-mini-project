import chess
import pygame
import random
import math
# os import is no longer strictly needed but kept for potential future use

# --- 1. (Keep) Piece Values for Evaluation ---
class PieceValues:
    """
    Simple piece-square table values for chess evaluation. 
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
    PAWN_B = PAWN_W[::-1] 
    MATERIAL_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }

# --- 2. (Keep) Minimax AI Agent ---
class MinimaxAI:
    """A simple AI agent using the Minimax algorithm with Alpha-Beta Pruning."""
    def __init__(self, depth=3):
        self.depth = depth

    def evaluate_board(self, board):
        if board.is_checkmate():
            if board.turn == chess.BLACK: return 100000000
            else: return -100000000
        if board.is_stalemate() or board.is_insufficient_material() or board.is_fivefold_repetition(): return 0
        
        score = 0
        for piece_type in PieceValues.MATERIAL_VALUES:
            for square in board.pieces(piece_type, chess.WHITE):
                score += PieceValues.MATERIAL_VALUES[piece_type]
                if piece_type == chess.PAWN: score += PieceValues.PAWN_W[square]
            for square in board.pieces(piece_type, chess.BLACK):
                score -= PieceValues.MATERIAL_VALUES[piece_type]
                if piece_type == chess.PAWN: score -= PieceValues.PAWN_B[square]
        return score

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0 or board.is_game_over(): return self.evaluate_board(board)
        moves = list(board.legal_moves)
        moves.sort(key=lambda move: self.get_move_value(board, move), reverse=True)
        if maximizing_player:
            max_eval = -math.inf
            for move in moves:
                board.push(move); eval = self.minimax(board, depth - 1, alpha, beta, False); board.pop()
                max_eval = max(max_eval, eval); alpha = max(alpha, max_eval)
                if beta <= alpha: break
            return max_eval
        else:
            min_eval = math.inf
            for move in moves:
                board.push(move); eval = self.minimax(board, depth - 1, alpha, beta, True); board.pop()
                min_eval = min(min_eval, eval); beta = min(beta, min_eval)
                if beta <= alpha: break
            return min_eval
    
    def get_move_value(self, board, move):
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            if captured_piece: return PieceValues.MATERIAL_VALUES.get(captured_piece.piece_type, 0) + 1000
            return 1000
        return 0

    def find_best_move(self, board):
        best_move = None
        maximizing_player = board.turn == chess.WHITE
        max_eval = -math.inf if maximizing_player else math.inf

        moves = list(board.legal_moves)
        random.shuffle(moves)
        moves.sort(key=lambda move: self.get_move_value(board, move), reverse=True)

        for move in moves:
            board.push(move)
            current_eval = self.minimax(board, self.depth - 1, -math.inf, math.inf, not maximizing_player)
            board.pop()

            if maximizing_player and current_eval > max_eval:
                max_eval = current_eval; best_move = move
            elif not maximizing_player and current_eval < max_eval:
                max_eval = current_eval; best_move = move

        return best_move

## Chess GUI (Text-Based Pieces)

class ChessGUI:
    def __init__(self, ai_depth=3):
        # Initialize Game State and AI
        self.board = chess.Board()
        self.ai_agent = MinimaxAI(depth=ai_depth)
        self.ai_color = chess.BLACK
        self.square_selected = None
        self.game_running = True

        # Pygame Constants
        pygame.init()
        self.SQUARE_SIZE = 80
        self.WIDTH = 8 * self.SQUARE_SIZE
        self.HEIGHT = 8 * self.SQUARE_SIZE
        self.SCREEN = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Minimax Chess AI")
        self.CLOCK = pygame.time.Clock()
        
        # Colors
        self.LIGHT_SQUARE = (240, 217, 181)
        self.DARK_SQUARE = (181, 136, 99)
        self.HIGHLIGHT_COLOR = (100, 255, 100)
        self.TEXT_COLOR_WHITE = (255, 255, 255)
        self.TEXT_COLOR_BLACK = (0, 0, 0)

        # Font and Piece Mapping for Text Rendering
        try:
            # Use a standard font for simplicity
            self.FONT = pygame.font.SysFont("segoeuisymbol", int(self.SQUARE_SIZE * 0.7))
        except:
            # Fallback for systems without the specific font
            self.FONT = pygame.font.Font(None, int(self.SQUARE_SIZE * 0.7)) 
            
        self.PIECE_SYMBOLS = self.load_unicode_pieces()
        print(f"🤖 Chess Game Initialized! You are White. AI Depth: {ai_depth}")


    def load_unicode_pieces(self):
        """Maps chess piece symbols to their Unicode representation."""
        return {
            'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
            'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
        }


    def draw_board(self):
        """Draws the chessboard grid and highlights the selected square."""
        for r in range(8):
            for c in range(8):
                color = self.LIGHT_SQUARE if (r + c) % 2 == 0 else self.DARK_SQUARE
                pygame.draw.rect(self.SCREEN, color, 
                                 (c * self.SQUARE_SIZE, r * self.SQUARE_SIZE, 
                                  self.SQUARE_SIZE, self.SQUARE_SIZE))
        
        if self.square_selected is not None:
            r, c = divmod(self.square_selected, 8)
            display_r = 7 - r # Convert chess rank (0-7) to pygame row (7-0)
            pygame.draw.rect(self.SCREEN, self.HIGHLIGHT_COLOR, 
                             (c * self.SQUARE_SIZE, display_r * self.SQUARE_SIZE, 
                              self.SQUARE_SIZE, self.SQUARE_SIZE), 3)


    def draw_pieces(self):
        """Draws the pieces on the board using Unicode text."""
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                # Get the Unicode symbol
                text_symbol = self.PIECE_SYMBOLS.get(piece.symbol())
                
                # Choose color: Black symbols for White pieces, White symbols for Black pieces 
                # (to ensure visibility on dark/light squares)
                color = self.TEXT_COLOR_BLACK if piece.color == chess.WHITE else self.TEXT_COLOR_BLACK 
                
                # Render the text
                text_surface = self.FONT.render(text_symbol, True, color)
                
                r, c = divmod(square, 8)
                display_r = 7 - r

                # Center the text within the square
                text_rect = text_surface.get_rect(
                    center=(c * self.SQUARE_SIZE + self.SQUARE_SIZE // 2, 
                            display_r * self.SQUARE_SIZE + self.SQUARE_SIZE // 2)
                )
                self.SCREEN.blit(text_surface, text_rect)


    def get_square_from_coords(self, pos):
        """Converts mouse (x, y) coordinates to a chess.Square index (0-63)."""
        x, y = pos
        c = x // self.SQUARE_SIZE
        r = y // self.SQUARE_SIZE
        return chess.square(c, 7 - r)


    def handle_click(self, pos):
        """Handles human move selection logic."""
        clicked_square = self.get_square_from_coords(pos)
        
        if self.square_selected is None:
            # First click: Select a piece of the current player's color
            piece = self.board.piece_at(clicked_square)
            if piece and piece.color == self.board.turn:
                self.square_selected = clicked_square
        else:
            # Second click: Attempt to make a move
            from_square = self.square_selected
            to_square = clicked_square
            self.square_selected = None # Reset selection immediately

            # Form move in UCI format (e.g., 'e2e4')
            uci_move = chess.square_name(from_square) + chess.square_name(to_square)
            
            # Simple handling for promotion: default to Queen
            piece_at_from = self.board.piece_at(from_square)
            if piece_at_from and piece_at_from.piece_type == chess.PAWN and \
               (chess.square_rank(to_square) == 7 or chess.square_rank(to_square) == 0):
                uci_move += 'q'
            
            try:
                move = chess.Move.from_uci(uci_move)
                if move in self.board.legal_moves:
                    self.board.push(move)
                else:
                    print(f"Illegal move: {uci_move}")
            except ValueError:
                print("Invalid move format.")
                

    def run_ai_turn(self):
        """Executes the AI's move."""
        print("AI is thinking...")
        pygame.display.set_caption("Minimax Chess AI - AI Thinking...")
        
        # Ensures the GUI updates while AI is calculating
        pygame.event.pump() 
        
        ai_move = self.ai_agent.find_best_move(self.board)
        
        if ai_move:
            self.board.push(ai_move)
            print(f"AI plays: {ai_move.uci()}")
        else:
            print("AI found no legal moves. Game over.")
            self.game_running = False

        pygame.display.set_caption("Minimax Chess AI")


    def display_game_over(self):
        """Draws game over text on the screen."""
        font = pygame.font.Font(None, 74)
        result = self.board.result()
        
        if result == '1-0':
            text = font.render('WHITE WINS!', True, (255, 0, 0))
        elif result == '0-1':
            text = font.render('BLACK WINS (AI WINS)!', True, (255, 0, 0))
        else:
            text = font.render('DRAW!', True, (255, 0, 0))
        
        # Draw a semi-transparent background box
        s = pygame.Surface((self.WIDTH, 100))
        s.set_alpha(180)  # Transparency
        s.fill((100, 100, 100))
        self.SCREEN.blit(s, (0, self.HEIGHT // 2 - 50))

        text_rect = text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
        self.SCREEN.blit(text, text_rect)
        pygame.display.flip()
        
        # Keep the game over screen visible for a few seconds
        pygame.time.wait(5000)


    def run(self):
        """The main game loop for the GUI."""
        while self.game_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_running = False
                
                if self.board.turn == chess.WHITE and event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    self.handle_click(pos)

            # AI Turn
            if self.board.turn == self.ai_color and self.game_running:
                self.run_ai_turn()

            # Drawing
            self.draw_board()
            self.draw_pieces()
            pygame.display.flip()

            # Check for Game Over after any move
            if self.board.is_game_over():
                self.display_game_over()
                self.game_running = False

            self.CLOCK.tick(60)

        pygame.quit()


# --- Run the Graphical Game ---
if __name__ == "__main__":
    # Ensure Pygame is installed: pip install pygame
    # Adjust the depth for stronger/weaker AI (higher = slower/stronger)
    gui_game = ChessGUI(ai_depth=3) 
    gui_game.run()
