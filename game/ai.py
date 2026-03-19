"""
Tic-Tac-Toe AI Module
======================
Board encoding:
  X    -> [1, 0]
  O    -> [0, 1]
  null -> [0, 0]

Full board state = 9 squares × 2 bits = 18-dimensional input vector.
"""

import numpy as np
import json
import os
import math

# Encoding helpers
CELL_ENCODING = {
    "X":   [1, 0],
    "O":   [0, 1],
    None:  [0, 0],
}

CELL_DECODING = {
    (1, 0): "X",
    (0, 1): "O",
    (0, 0): None,
}


def encode_board(board: list) -> np.ndarray:
    if len(board) != 9:
        raise ValueError("Board must have exactly 9 cells.")
    flat = []
    for cell in board:
        flat.extend(CELL_ENCODING[cell])
    return np.array(flat, dtype=np.float32)


def decode_board(encoded: np.ndarray) -> list:
    board = []
    for i in range(9):
        pair = tuple(int(x) for x in encoded[i*2:i*2+2])
        board.append(CELL_DECODING.get(pair))
    return board


def get_available_moves(board: list) -> list:
    """Return indices of empty cells."""
    return [i for i, cell in enumerate(board) if cell is None]



# Win condition check
WIN_LINES = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8],  # cols
    [0, 4, 8], [2, 4, 6],             # diagonals
]


def check_winner(board: list) -> str | None:
    """Return 'X', 'O', 'draw', or None if game is ongoing."""
    for line in WIN_LINES:
        vals = [board[i] for i in line]
        if vals[0] and vals[0] == vals[1] == vals[2]:
            return vals[0]
    if all(cell is not None for cell in board):
        return "draw"
    return None


# Minimax AI (perfect play, used as fallback / training target)
def _minimax(board: list, is_maximizing: bool, ai_player: str, human_player: str) -> int:
    winner = check_winner(board)
    if winner == ai_player:
        return 10
    if winner == human_player:
        return -10
    if winner == "draw":
        return 0

    moves = get_available_moves(board)
    if is_maximizing:
        best = -math.inf
        for move in moves:
            board[move] = ai_player
            score = _minimax(board, False, ai_player, human_player)
            board[move] = None
            best = max(best, score)
        return best
    else:
        best = math.inf
        for move in moves:
            board[move] = human_player
            score = _minimax(board, True, ai_player, human_player)
            board[move] = None
            best = min(best, score)
        return best


def minimax_move(board: list, ai_player: str) -> int:
    """Return the best move index using minimax (perfect play)."""
    human_player = "O" if ai_player == "X" else "X"
    best_score = -math.inf
    best_move = None

    for move in get_available_moves(board):
        board[move] = ai_player
        score = _minimax(board, False, ai_player, human_player)
        board[move] = None
        if score > best_score:
            best_score = score
            best_move = move

    return best_move



# Neural Network AI stub (plug in trained weights here)
class NeuralAI:
    def __init__(self):
        self.weights = None
        self._init_random_weights()

    def _init_random_weights(self):
        """random weights — replace with trained weights."""
        rng = np.random.default_rng(42)
        self.weights = {
            "W1": rng.normal(0, np.sqrt(2/18),  (18, 64)).astype(np.float32),
            "b1": np.zeros(64, dtype=np.float32),
            "W2": rng.normal(0, np.sqrt(2/64),  (64, 32)).astype(np.float32),
            "b2": np.zeros(32, dtype=np.float32),
            "W3": rng.normal(0, np.sqrt(2/32),  (32,  9)).astype(np.float32),
            "b3": np.zeros(9,  dtype=np.float32),
        }

    def load(self, path: str):
        """Load weights from a JSON file saved during training."""
        with open(path) as f:
            data = json.load(f)
        self.weights = {k: np.array(v, dtype=np.float32) for k, v in data.items()}

    def save(self, path: str):
        """Save weights to JSON for persistence."""
        data = {k: v.tolist() for k, v in self.weights.items()}
        with open(path, "w") as f:
            json.dump(data, f)

    def _forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass — returns raw logits (shape 9)."""
        h1 = np.maximum(0, x @ self.weights["W1"] + self.weights["b1"])
        h2 = np.maximum(0, h1 @ self.weights["W2"] + self.weights["b2"])
        return h2 @ self.weights["W3"] + self.weights["b3"]

    def predict(self, board: list, player: str) -> int:
        """
        Return the AI's chosen move index.
        Illegal moves (occupied cells) are masked to -inf before argmax.
        """
        x = encode_board(board)
        logits = self._forward(x)

        # Mask occupied squares
        mask = np.array([0.0 if cell is None else -np.inf for cell in board])
        masked = logits + mask

        return int(np.argmax(masked))

    @property
    def is_trained(self) -> bool:
        """Returns True once real weights have been loaded."""
        weights_path = os.path.join(os.path.dirname(__file__), "weights.json")
        return os.path.exists(weights_path)



# Top-level move selector
# Singleton neural AI instance (weights loaded once at startup)
_neural_ai = NeuralAI()
_weights_path = os.path.join(os.path.dirname(__file__), "weights.json")
if os.path.exists(_weights_path):
    _neural_ai.load(_weights_path)


def get_ai_move(board: list, player: str, mode: str = "auto") -> dict:
    available = get_available_moves(board)
    if not available:
        raise ValueError("No moves available — game is already over.")

    use_neural = (mode == "neural") or (mode == "auto" and _neural_ai.is_trained)

    if use_neural:
        move = _neural_ai.predict(board, player)
        ai_type = "neural"
    else:
        move = minimax_move(board, player)
        ai_type = "minimax"

    # Apply move
    new_board = board.copy()
    new_board[move] = player
    winner = check_winner(new_board)

    return {
        "move": move,
        "board": new_board,
        "winner": winner,
        "game_over": winner is not None,
        "ai_type": ai_type,
        "encoded_state": encode_board(new_board).tolist(),
    }
