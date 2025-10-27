Here’s a **plagiarism-free, professional `README.md`** for your chess project.
It clearly explains the **purpose, algorithm, structure, and usage** of your code.

---

# ♟️ Minimax Chess AI with Pygame

A visually interactive chess game built using **Python**, **Pygame**, and **python-chess**.
It features a **Minimax AI with Alpha-Beta Pruning** that evaluates positions using **piece-square tables** and **material scoring**.

---

## 🧠 Project Overview

This project implements a playable chess interface where:

* The **human plays as White**.
* The **AI (Black)** makes moves using the **Minimax algorithm**.
* The board and pieces are rendered using **Pygame**.
* The AI evaluates moves based on **material balance**, **positional value**, and **capture prioritization**.

---

## ⚙️ Core Features

✅ **Full Chess Rules:**
Supports legal moves, captures, castling, promotions, and checkmates using the `python-chess` library.

✅ **Minimax Algorithm with Alpha-Beta Pruning:**
Efficiently searches the game tree to find the most promising move within a given search depth.

✅ **Heuristic Evaluation:**
Each position is scored based on material and piece placement using **piece-square tables**.

✅ **Interactive GUI:**
Play directly via mouse clicks on a clean, color-coded chessboard.

✅ **AI Move Ordering:**
Captures are evaluated first to speed up pruning and improve decision quality.

---

## 🧩 Algorithm Explanation

### 🔹 1. Evaluation Function

The **evaluation function** estimates how good a board position is for White.

It combines:

* **Material Value:** Each piece type has a numeric worth (e.g., Queen = 900).
* **Positional Value:** A piece-square table rewards strategic positions (e.g., central pawns).

Example scoring snippet:

```python
score += PieceValues.MATERIAL_VALUES[piece_type]
if piece_type == chess.PAWN:
    score += PieceValues.PAWN_W[square]
```

If the board is checkmate, stalemate, or repetition, large positive or negative scores are used accordingly.

---

### 🔹 2. Minimax with Alpha-Beta Pruning

The **Minimax algorithm** recursively explores possible move sequences to a certain depth.

* The **maximizing player** (White) tries to maximize the evaluation score.
* The **minimizing player** (Black) tries to minimize it.
* **Alpha-Beta pruning** skips branches that cannot influence the final decision.

Pseudo-logic:

```python
if depth == 0 or game over:
    return evaluate(board)

if maximizing_player:
    for move in legal_moves:
        make move
        eval = minimax(next_state, depth-1, alpha, beta, False)
        undo move
        alpha = max(alpha, eval)
        if beta <= alpha: break
else:
    for move in legal_moves:
        make move
        eval = minimax(next_state, depth-1, alpha, beta, True)
        undo move
        beta = min(beta, eval)
        if beta <= alpha: break
```

This allows the AI to think several moves ahead without checking every single possibility.

---

### 🔹 3. Move Ordering

To improve efficiency, moves that capture higher-value pieces are checked first:

```python
if board.is_capture(move):
    captured_piece = board.piece_at(move.to_square)
    return PieceValues.MATERIAL_VALUES.get(captured_piece.piece_type, 0) + 1000
```

This helps pruning occur earlier in the game tree, speeding up the AI’s decision process.

---

### 🔹 4. Graphical Interface (Pygame)

The chessboard is drawn using an 8×8 grid of alternating light and dark squares.
Pieces are rendered as **Unicode characters** (♔♕♖♗♘♙ for White, ♚♛♜♝♞♟ for Black).

The GUI handles:

* Mouse clicks for selecting and moving pieces.
* Highlighting selected squares.
* Displaying game results (checkmate, stalemate, etc.).

---

## 🧰 Project Structure

```
chess_minimax/
│
├── main.py            # Main entry point (contains GUI + AI logic)
├── README.md           # Project documentation (this file)
└── requirements.txt    # Dependencies list
```

---

## 🐍 Requirements

To run this project, install dependencies:

```bash
pip install pygame python-chess
```

---

## ▶️ How to Run

1. **Clone or download** the repository.
2. Run the main script:

   ```bash
   python main.py
   ```
3. The Pygame window will open — you play **White**, and the AI plays **Black**.

---

## 🧠 Adjustable AI Difficulty

You can modify the AI’s thinking depth when creating the `ChessGUI` object:

```python
if __name__ == "__main__":
    gui_game = ChessGUI(ai_depth=3)  # Increase depth for stronger AI
    gui_game.run()
```

* `ai_depth=2`: Faster but weaker AI
* `ai_depth=4+`: Slower but much stronger

---

## 🧩 Libraries Used

| Library          | Purpose                                             |
| ---------------- | --------------------------------------------------- |
| **python-chess** | Handles chess rules, move legality, and board logic |
| **pygame**       | GUI and user interaction                            |
| **math, random** | Used for evaluation and move ordering               |
| **sys**          | Ensures a clean exit after quitting                 |

---

## 🏁 Game End Conditions

The game automatically detects:

* **Checkmate**
* **Stalemate**
* **Insufficient Material**
* **Repetition**

When the game ends, a message (e.g., “WHITE WINS!” or “DRAW!”) appears before the window closes.

---

## 📈 Possible Improvements

* Implement **iterative deepening** or **transposition tables** for performance.
* Add **move hints** or **undo functionality**.
* Include **opening books** or **endgame heuristics**.
* Introduce **sound effects** and **move highlighting animations**.

---

## 👨‍💻 Author

**Your Name**
Python Developer | AI & Game Enthusiast

---

## 📜 License

This project is released under the **MIT License**.
You are free to modify, distribute, and use it for educational or personal purposes.

---

Would you like me to include a **formatted `requirements.txt`** and **diagram of the algorithm (flowchart)** in the README as well? I can append that for better documentation.
