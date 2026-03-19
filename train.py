#train.py — Trains the Tic-Tac-Toe AI
#Weights saved to: game/weights.json

import numpy as np
import json
import argparse
import random
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

# Bootstrap Django so we can import game.ai
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tictactoe_api.settings")
django.setup()

from game.ai import (
    encode_board, check_winner, get_available_moves,
    minimax_move, NeuralAI, WIN_LINES, _weights_path,
)

# Replay buffer for DQN
class ReplayBuffer:
    def __init__(self, capacity=10_000):
        self.buffer = []
        self.capacity = capacity

    def push(self, state, action, reward, next_state, done):
        if len(self.buffer) >= self.capacity:
            self.buffer.pop(0)
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        return random.sample(self.buffer, min(batch_size, len(self.buffer)))

    def __len__(self):
        return len(self.buffer)


# Gradient helpers (pure numpy, no framework required)
def relu(x):
    return np.maximum(0, x)

def relu_deriv(x):
    return (x > 0).astype(np.float32)

def softmax(x):
    e = np.exp(x - x.max())
    return e / e.sum()

def mse_loss(pred, target):
    diff = pred - target
    return 0.5 * np.sum(diff ** 2), diff   # loss, gradient


def forward_verbose(weights, x):
    """Forward pass that also returns pre-activations for backprop."""
    z1 = x @ weights["W1"] + weights["b1"]
    a1 = relu(z1)
    z2 = a1 @ weights["W2"] + weights["b2"]
    a2 = relu(z2)
    z3 = a2 @ weights["W3"] + weights["b3"]
    return z3, (x, z1, a1, z2, a2, z3)


def backward(weights, cache, grad_out, lr=1e-3):
    x, z1, a1, z2, a2, z3 = cache

    # Layer 3
    dW3 = np.outer(a2, grad_out)
    db3 = grad_out
    da2 = weights["W3"] @ grad_out

    # Layer 2
    dz2 = da2 * relu_deriv(z2)
    dW2 = np.outer(a1, dz2)
    db2 = dz2
    da1 = weights["W2"] @ dz2

    # Layer 1
    dz1 = da1 * relu_deriv(z1)
    dW1 = np.outer(x, dz1)
    db1 = dz1

    # SGD update
    weights["W3"] -= lr * dW3
    weights["b3"] -= lr * db3
    weights["W2"] -= lr * dW2
    weights["b2"] -= lr * db2
    weights["W1"] -= lr * dW1
    weights["b1"] -= lr * db1



# Phase 1 — Supervised pretraining
def generate_supervised_data(n_games=5000):
    """
    Self-play minimax to generate (encoded_board, best_move_index) pairs.
    """
    data = []
    for _ in range(n_games):
        board = [None] * 9
        player = random.choice(["X", "O"])
        while True:
            winner = check_winner(board)
            if winner:
                break
            moves = get_available_moves(board)
            if not moves:
                break
            move = minimax_move(board, player)
            state = encode_board(board)
            data.append((state, move))
            board[move] = player
            player = "O" if player == "X" else "X"
    return data


def train_supervised(ai: NeuralAI, epochs=300, lr=1e-3, n_games=5000):
    print(f"Generating {n_games} supervised training positions via minimax...")
    data = generate_supervised_data(n_games)
    print(f"  → {len(data)} (state, move) pairs collected")

    for epoch in range(1, epochs + 1):
        random.shuffle(data)
        total_loss = 0.0
        for x, target_action in data:
            logits, cache = forward_verbose(ai.weights, x)

            # One-hot target
            target = np.zeros(9, dtype=np.float32)
            target[target_action] = 1.0

            # Softmax cross-entropy gradient
            probs = softmax(logits)
            grad = probs - target

            backward(ai.weights, cache, grad, lr=lr)
            total_loss += float(-np.log(probs[target_action] + 1e-9))

        if epoch % 50 == 0 or epoch == 1:
            print(f"  Epoch {epoch:4d}/{epochs}  avg_loss={total_loss/len(data):.4f}")

    print("Supervised pretraining complete.")



# Phase 2 — Deep Q-Learning (DQN)
GAMMA      = 0.95
EPSILON    = 1.0
EPSILON_MIN= 0.05
EPSILON_DECAY = 0.995
LR         = 5e-4
BATCH      = 64


def dqn_select_action(ai, board, player, epsilon):
    if random.random() < epsilon:
        return random.choice(get_available_moves(board))
    x = encode_board(board)
    logits, _ = forward_verbose(ai.weights, x)
    mask = np.array([0.0 if c is None else -1e9 for c in board])
    return int(np.argmax(logits + mask))


def step_env(board, move, player):
    """Apply move, return (new_board, reward, done, next_player)."""
    new_board = board.copy()
    new_board[move] = player
    winner = check_winner(new_board)
    if winner == player:
        return new_board, +1.0, True, None
    if winner == "draw":
        return new_board, +0.5, True, None
    if winner:
        return new_board, -1.0, True, None
    next_player = "O" if player == "X" else "X"
    return new_board, 0.0, False, next_player


def train_drl(ai: NeuralAI, episodes=5000, lr=LR):
    global EPSILON
    epsilon = EPSILON
    replay = ReplayBuffer()

    for ep in range(1, episodes + 1):
        board = [None] * 9
        player = random.choice(["X", "O"])

        while True:
            move = dqn_select_action(ai, board, player, epsilon)
            new_board, reward, done, next_player = step_env(board, move, player)

            state_enc     = encode_board(board)
            next_state_enc = encode_board(new_board)
            replay.push(state_enc, move, reward, next_state_enc, done)

            # Train on mini-batch
            if len(replay) >= BATCH:
                batch = replay.sample(BATCH)
                for s, a, r, ns, d in batch:
                    q_vals, cache = forward_verbose(ai.weights, s)
                    if d:
                        target_q = r
                    else:
                        next_q, _ = forward_verbose(ai.weights, ns)
                        target_q  = r + GAMMA * float(next_q.max())

                    target = q_vals.copy()
                    target[a] = target_q
                    _, grad = mse_loss(q_vals, target)
                    backward(ai.weights, cache, grad, lr=lr)

            if done:
                break
            board = new_board
            player = next_player

        epsilon = max(EPSILON_MIN, epsilon * EPSILON_DECAY)

        if ep % 1000 == 0 or ep == 1:
            print(f"  Episode {ep:6d}/{episodes}  epsilon={epsilon:.3f}")

    print("DRL training complete.")



# CLI
def main():
    parser = argparse.ArgumentParser(description="Train Tic-Tac-Toe AI")
    parser.add_argument("--phase",    choices=["supervised","drl","both"], default="both")
    parser.add_argument("--epochs",   type=int, default=300)
    parser.add_argument("--episodes", type=int, default=5000)
    parser.add_argument("--games",    type=int, default=5000,
                        help="Number of minimax games for supervised data generation")
    args = parser.parse_args()

    ai = NeuralAI()
    if os.path.exists(_weights_path):
        print(f"Loading existing weights from {_weights_path}")
        ai.load(_weights_path)

    if args.phase in ("supervised", "both"):
        print("\n=== Phase 1: Supervised Pretraining ===")
        train_supervised(ai, epochs=args.epochs, n_games=args.games)

    if args.phase in ("drl", "both"):
        print("\n=== Phase 2: Deep Q-Learning ===")
        train_drl(ai, episodes=args.episodes)

    ai.save(_weights_path)
    print(f"\nWeights saved to {_weights_path}")
    print("Restart the Django server to load the new weights.")


if __name__ == "__main__":
    main()
