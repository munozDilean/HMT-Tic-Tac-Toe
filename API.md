# Tic-Tac-Toe DRL API — Django Backend

A Django REST Framework backend for a Tic-Tac-Toe AI that uses Deep Reinforcement Learning.

## Architecture

```
tictactoe_api/          ← Django project
game/
  ai.py                 ← Encoding, minimax, neural net, move selector
  views.py              ← REST endpoints
  serializers.py        ← Request/response validation
  urls.py               ← Route definitions
  weights.json          ← Trained model weights (created after training)
train.py                ← Supervised + DRL training script
```

## Board Encoding

Each cell is a 2-bit one-hot vector:

| Cell  | Encoding |
|-------|----------|
| X     | `[1, 0]` |
| O     | `[0, 1]` |
| empty | `[0, 0]` |

Full board → 18-dimensional float32 vector (9 cells × 2 bits).

Example:
```
["X","O",null, null,"X","O", "O",null,"X"]
 →  [1,0, 0,1, 0,0,  0,0, 1,0, 0,1,  0,1, 0,0, 1,0]
```


## API Endpoints

### `POST /api/move/`
Request the AI to play a move.

**Request:**
```json
{
  "board":  ["X","O","O", null,"X","O", "O",null,"X"],
  "player": "X",
  "mode":   "auto"
}
```

| Field    | Type   | Description |
|----------|--------|-------------|
| `board`  | array  | 9 cells: `"X"`, `"O"`, or `null` |
| `player` | string | `"X"` or `"O"` — which side the AI plays |
| `mode`   | string | `"auto"` (default) · `"minimax"` · `"neural"` |

**Response:**
```json
{
  "move":          7,
  "board":         ["X","O","O", null,"X","O", "O","X","X"],
  "winner":        "X",
  "game_over":     true,
  "ai_type":       "minimax",
  "encoded_state": [1,0, 0,1, 0,1, 0,0, 1,0, 0,1, 0,1, 1,0, 1,0]
}
```

---

### `POST /api/validate/`
Validate a board state.

**Request:**
```json
{ "board": ["X","O","O", null,"X","O", "O",null,"X"] }
```

**Response:**
```json
{
  "valid":           true,
  "winner":          "X",
  "game_over":       true,
  "available_moves": [],
  "encoded_state":   [...]
}
```

---

### `GET /api/health/`
Liveness check — shows whether trained neural weights are loaded.

---

### `GET /api/encoding/`
Returns documentation on the encoding scheme.

---

## AI Modes

| Mode       | Behaviour |
|------------|-----------|
| `minimax`  | Perfect play — unbeatable, deterministic |
| `neural`   | MLP policy network (random weights if untrained) |
| `auto`     | Uses neural if `game/weights.json` exists, else minimax |

## Model Architecture

```
Input  (18)  → Dense(64, ReLU) → Dense(32, ReLU) → Output(9)
```

- Input: 18-dim one-hot board encoding  
- Output: logit score per board position (illegal moves masked to −∞)

## Training

`train.py` implements two phases:

1. **Supervised pretraining** — generates positions via minimax self-play, trains the network to imitate optimal moves using cross-entropy loss.  
2. **Deep Q-Learning** — self-play with ε-greedy exploration and experience replay (DQN). The network learns a Q-value for each (state, action) pair.

Weights are saved to `game/weights.json` and hot-loaded on the next server restart.
