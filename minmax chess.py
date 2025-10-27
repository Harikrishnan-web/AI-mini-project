import chess
import pygame
import random
import math
import os # Used for loading images

# --- 1. (Keep) Piece Values for Evaluation ---
# (Your existing PieceValues class remains the same)
class PieceValues:
    # ... (Keep all existing code from your PAWN_W, PAWN_B, and MATERIAL_VALUES) ...
    PAWN_W = [
        0, 0, 0, 0, 0, 0, 0, 0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5, 5, 10, 25, 25, 10, 5, 5,
        0, 0, 0, 20, 20, 0, 0, 0,
        5, -5, -10, 0, 0, -10, -10, -5, 5,
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
# (Your existing MinimaxAI class remains the same)
class MinimaxAI:
    # ... (Keep all existing methods: __init__, evaluate_board, minimax, get_move_value, find_best_move) ...
    def __init__(self, depth=3):
        self.depth = depth
    
    # ... (evaluate_board, minimax, get_move_value are the same) ...

    def evaluate_board(self, board):
        # ... (Existing evaluation logic) ...
        if board.is_checkmate():
            if board.turn == chess.BLACK:
                return 100000000
            else:
                return -100000000
        if board.is_stalemate() or board.is_insufficient_material() or board.is_fivefold_repetition():
            return 0
        
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
        # ... (Existing minimax logic with alpha-beta pruning) ...
        if depth == 0 or board.is_game_over(): return self.evaluate_board(board)
        moves = list(board.legal_moves)
        moves.sort(key=lambda move: self.get_move_value(board, move), reverse=True)
        if maximizing_player:
            max_eval = -math.inf
            for move in moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, max_eval)
                if beta <= alpha: break
            return max_eval
        else:
            min_eval = math.inf
            for move in moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, min_eval)
                if beta <= alpha: break
            return min_eval
    
    def get_move_value(self, board, move):
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            if captured_piece: return PieceValues.MATERIAL_VALUES.get(captured_piece.piece_type, 0) + 1000
            return 1000
        return 0

    def find_best_move(self, board):
        # ... (Existing find_best_move logic) ...
        best_move = None
        if board.turn == chess.WHITE:
            max_eval = -math.inf
            maximizing_player = True
        else:
            max_eval = math.inf
            maximizing_player = False

        moves = list(board.legal_moves)
        random.shuffle(moves)
        moves.sort(key=lambda move: self.get_move_value(board, move), reverse=True)

        for move in moves:
            board.push(move)
            current_eval = self.minimax(board, self.depth - 1, -math.inf, math.inf, not maximizing_player)
            board.pop()

            if maximizing_player and current_eval > max_eval:
                max_eval = current_eval
                best_move = move
            elif not maximizing_player and current_eval < max_eval:
                max_eval = current_eval
                best_move = move

        return best_move

# --- 3. Chess GUI with Pygame ---

class ChessGUI:
    def __init__(self, ai_depth=3):
        # Initialize Game State and AI
        self.board = chess.Board()
        self.ai_agent = MinimaxAI(depth=ai_depth)
        self.ai_color = chess.BLACK
        self.square_selected = None  # Tracks the square of the piece clicked
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
        self.LIGHT_SQUARE = (240, 217, 181) # Light Wood
        self.DARK_SQUARE = (181, 136, 99)   # Dark Wood
        self.HIGHLIGHT_COLOR = (100, 255, 100) # Green for selected square

        # Load Piece Images
        self.PIECES = self.load_pieces()
        print(f"🤖 Chess Game Initialized! You are White. AI Depth: {ai_depth}")


    def load_pieces(self):
        """Loads piece images and scales them to fit the square size."""
        # You'll need a 'pieces' directory with images named 'wP.png', 'bN.png', etc.
        piece_dir = "pieces" 
        piece_map = {}
        piece_symbols = {'P': 'wP', 'N': 'wN', 'B': 'wB', 'R': 'wR', 'Q': 'wQ', 'K': 'wK',
                         'p': 'bP', 'n': 'bN', 'b': 'bB', 'r': 'bR', 'q': 'bQ', 'k': 'bK'}
        
        for symbol, name in piece_symbols.items():
            try:
                # Assuming images are in an accessible path
                img = pygame.image.load(os.path.join(piece_dir, f"{name}.png")).convert_alpha()
                img = pygame.transform.scale(img, (self.SQUARE_SIZE, self.SQUARE_SIZE))
                piece_map[symbol] = img
            except pygame.error:
                print(f"Warning: Could not load image for {name}. Make sure you have a 'pieces' folder with images.")
                # Fallback to a simple text if images are missing
                piece_map[symbol] = None 
        return piece_map


    def draw_board(self):
        """Draws the chessboard grid."""
        for r in range(8):
            for c in range(8):
                color = self.LIGHT_SQUARE if (r + c) % 2 == 0 else self.DARK_SQUARE
                pygame.draw.rect(self.SCREEN, color, 
                                 (c * self.SQUARE_SIZE, r * self.SQUARE_SIZE, 
                                  self.SQUARE_SIZE, self.SQUARE_SIZE))
        
        # Highlight the selected square
        if self.square_selected is not None:
            r, c = divmod(self.square_selected, 8)
            # Flip row for display (chess.Square 0=a1 is bottom-left, pygame (0,0) is top-left)
            display_r = 7 - r 
            pygame.draw.rect(self.SCREEN, self.HIGHLIGHT_COLOR, 
                             (c * self.SQUARE_SIZE, display_r * self.SQUARE_SIZE, 
                              self.SQUARE_SIZE, self.SQUARE_SIZE), 3) # 3 is line thickness

    def draw_pieces(self):
        """Draws the pieces on the board based on the current FEN."""
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                symbol = piece.symbol()
                image = self.PIECES.get(symbol)
                
                if image:
                    r, c = divmod(square, 8)
                    # Flip row for display
                    display_r = 7 - r
                    self.SCREEN.blit(image, (c * self.SQUARE_SIZE, display_r * self.SQUARE_SIZE))


    def get_square_from_coords(self, pos):
        """Converts mouse (x, y) coordinates to a chess.Square index (0-63)."""
        x, y = pos
        c = x // self.SQUARE_SIZE
        r = y // self.SQUARE_SIZE
        # Convert Pygame row (0=top/8th rank) to chess row (0=bottom/1st rank)
        return chess.square(c, 7 - r)


    def handle_click(self, pos):
        """Handles human move selection logic."""
        clicked_square = self.get_square_from_coords(pos)
        
        if self.square_selected is None:
            # First click: Select a piece
            piece = self.board.piece_at(clicked_square)
            if piece and piece.color == self.board.turn:
                self.square_selected = clicked_square
        else:
            # Second click: Attempt to make a move
            from_square = self.square_selected
            to_square = clicked_square
            
            try:
                # Form move in UCI format (e.g., 'e2e4')
                uci_move = chess.square_name(from_square) + chess.square_name(to_square)
                move = chess.Move.from_uci(uci_move)
                
                # Handle promotion: Default to Queen for simplicity
                if move in self.board.generate_legal_moves():
                    if self.board.piece_at(from_square).piece_type == chess.PAWN and \
                       (chess.square_rank(to_square) == 7 or chess.square_rank(to_square) == 0):
                        move = chess.Move(from_square, to_square, promotion=chess.QUEEN)

                if move in self.board.legal_moves:
                    self.board.push(move)
                else:
                    print("Illegal move.")
                
            except ValueError:
                # This catches if the move format is somehow invalid (though unlikely here)
                print("Invalid move.")

            # Reset selection
            self.square_selected = None


    def run_ai_turn(self):
        """Executes the AI's move."""
        print("AI is thinking...")
        pygame.display.set_caption("Minimax Chess AI - AI Thinking...")
        
        # Use a clock to show "thinking" time (can be removed if you want instant move)
        self.CLOCK.tick(1) 
        
        ai_move = self.ai_agent.find_best_move(self.board)
        
        if ai_move:
            self.board.push(ai_move)
            print(f"AI plays: {ai_move.uci()}")
        else:
            # Game should be over if AI has no moves
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

            self.CLOCK.tick(60) # Limits game FPS

        pygame.quit()


# --- Run the Graphical Game ---
if __name__ == "__main__":
    # You will need to create a 'pieces' folder containing images 
    # (e.g., wP.png, bN.png, etc.) for this to display correctly.
    # If not, the code will just print a warning and draw an empty board.
    gui_game = ChessGUI(ai_depth=3) 
    gui_game.run()
