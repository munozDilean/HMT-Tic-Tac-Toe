"""
train.py — PyTorch GPU Training for Tic-Tac-Toe AI
=====================================================
Automatically uses CUDA if available, falls back to CPU.

Usage:
    python train.py --phase both --epochs 300 --episodes 5000
    python train.py --phase supervised --epochs 500
    python train.py --phase drl --episodes 10000

Weights saved to game/weights.json (same format as before —
Django API does not need any changes).
"""

import os
import sys
import json
import math
import random
import argparse
import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from collections import deque

# Bootstrap Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tictactoe_api.settings")
import django
django.setup()

from game.ai import (
    encode_board, check_winner, get_available_moves,
    minimax_move, _weights_path,
)

# Device setup (Allows for GPU usage)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}", end="")
if device.type == "cuda":
    print(f" ({torch.cuda.get_device_name(0)})")
else:
    print()

# Neural network witched to PyTorch
class TicTacToeNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(18, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 9),
        )
        
        for layer in self.net:
            if isinstance(layer, nn.Linear):
                nn.init.xavier_uniform_(layer.weight)
                nn.init.zeros_(layer.bias)

    def forward(self, x):
        return self.net(x)


def board_to_tensor(board: list) -> torch.Tensor:
    """Convert board list to float tensor on the correct device."""
    encoded = encode_board(board)
    return torch.tensor(encoded, dtype=torch.float32, device=device)


# Weight serialisation — keeps game/weights.json compatible with ai.py
def save_weights(model: TicTacToeNet, path: str):
    """Save PyTorch weights to JSON in the numpy format ai.py expects."""
    state = model.state_dict()
    mapping = {
        "net.0.weight": "W1", 
        "net.0.bias":   "b1",
        "net.2.weight": "W2",  
        "net.2.bias":   "b2",
        "net.4.weight": "W3", 
        "net.4.bias":   "b3",
    }
    data = {}
    for pt_key, np_key in mapping.items():
        tensor = state[pt_key].cpu().numpy()
        if tensor.ndim == 2:
            tensor = tensor.T  
        data[np_key] = tensor.tolist()

    with open(path, "w") as f:
        json.dump(data, f)
    print(f"Weights saved to {path}")


def load_weights(model: TicTacToeNet, path: str):
    """Load weights from game/weights.json into the PyTorch model."""
    with open(path) as f:
        data = json.load(f)

    mapping = {
        "W1": "net.0.weight",
        "b1": "net.0.bias",
        "W2": "net.2.weight",
        "b2": "net.2.bias",
        "W3": "net.4.weight",
        "b3": "net.4.bias",
    }
    state = model.state_dict()
    for np_key, pt_key in mapping.items():
        arr = np.array(data[np_key], dtype=np.float32)
        if arr.ndim == 2:
            arr = arr.T  # transpose back
        state[pt_key] = torch.tensor(arr)

    model.load_state_dict(state)
    print(f"Loaded existing weights from {path}")



# Phase 1 — Supervised pretraining
def generate_supervised_data(n_games: int):
    """Generate (encoded_board, best_move) pairs via minimax self-play."""
    data = []
    for _ in range(n_games):
        board = [None] * 9
        player = random.choice(["X", "O"])
        while True:
            if check_winner(board) or not get_available_moves(board):
                break
            move = minimax_move(board, player)
            data.append((encode_board(board), move))
            board[move] = player
            player = "O" if player == "X" else "X"
    return data


def train_supervised(model: TicTacToeNet, epochs=300, lr=1e-3, n_games=5000):
    print(f"Generating {n_games} supervised positions via minimax...")
    data = generate_supervised_data(n_games)
    print(f"  → {len(data)} (state, move) pairs collected")

    optimizer = optim.Adam(model.parameters(), lr=lr)
    model.train()

    for epoch in range(1, epochs + 1):
        random.shuffle(data)
        total_loss = 0.0

        # Batching
        states  = torch.tensor(np.array([d[0] for d in data]), dtype=torch.float32, device=device)
        targets = torch.tensor([d[1] for d in data], dtype=torch.long, device=device)

        # Mini-batch SGD
        batch_size = 256
        for i in range(0, len(data), batch_size):
            s = states[i:i+batch_size]
            t = targets[i:i+batch_size]

            optimizer.zero_grad()
            logits = model(s)
            loss = F.cross_entropy(logits, t)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * len(s)

        if epoch % 50 == 0 or epoch == 1:
            print(f"  Epoch {epoch:4d}/{epochs}  avg_loss={total_loss/len(data):.4f}")

    print("Supervised pretraining complete.")


# Phase 2 — Deep Q-Learning

GAMMA         = 0.95
EPSILON_START = 1.0
EPSILON_MIN   = 0.05
EPSILON_DECAY = 0.995
LR_DRL        = 1e-4
BATCH_SIZE    = 256
BUFFER_SIZE   = 20_000
TARGET_UPDATE = 100  


class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, n):
        batch = random.sample(self.buffer, n)
        states, actions, rewards, next_states, dones = zip(*batch)
        return (
            torch.tensor(np.array(states),      dtype=torch.float32, device=device),
            torch.tensor(actions,               dtype=torch.long,    device=device),
            torch.tensor(rewards,               dtype=torch.float32, device=device),
            torch.tensor(np.array(next_states), dtype=torch.float32, device=device),
            torch.tensor(dones,                 dtype=torch.float32, device=device),
        )

    def __len__(self):
        return len(self.buffer)


def select_action(model, board, epsilon):
    available = get_available_moves(board)
    if random.random() < epsilon:
        return random.choice(available)
    with torch.no_grad():
        x = board_to_tensor(board).unsqueeze(0)
        logits = model(x).squeeze(0)
        # Mask illegal moves
        mask = torch.full((9,), float("-inf"), device=device)
        for i in available:
            mask[i] = 0.0
        return int((logits + mask).argmax().item())


def step_env(board, move, player):
    new_board = board.copy()
    new_board[move] = player
    winner = check_winner(new_board)
    if winner == player:
        return new_board, 1.0, True
    if winner == "draw":
        return new_board, 0.5, True
    if winner:
        return new_board, -1.0, True
    return new_board, 0.0, False


def train_drl(model: TicTacToeNet, episodes=5000, lr=LR_DRL):
    target_model = TicTacToeNet().to(device)
    target_model.load_state_dict(model.state_dict())
    target_model.eval()

    optimizer = optim.Adam(model.parameters(), lr=lr)
    replay = ReplayBuffer(BUFFER_SIZE)
    epsilon = EPSILON_START

    for ep in range(1, episodes + 1):
        board = [None] * 9
        player = random.choice(["X", "O"])
        opponent = "O" if player == "X" else "X"

        while True:
            # AI move
            move = select_action(model, board, epsilon)
            new_board, reward, done = step_env(board, move, player)

            state_enc      = encode_board(board)
            next_state_enc = encode_board(new_board)
            replay.push(state_enc, move, reward, next_state_enc, done)

            board = new_board

            if not done:
                opp_moves = get_available_moves(board)
                if opp_moves:
                    opp_move = random.choice(opp_moves)
                    board, opp_reward, done = step_env(board, opp_move, opponent)
                    if done:
                        replay.push(next_state_enc, opp_move, -opp_reward, encode_board(board), done)

            # Train on a batch
            if len(replay) >= BATCH_SIZE:
                model.train()
                s, a, r, ns, d = replay.sample(BATCH_SIZE)

                with torch.no_grad():
                    next_q = target_model(ns).max(dim=1).values
                    target_q = r + GAMMA * next_q * (1 - d)

                current_q = model(s).gather(1, a.unsqueeze(1)).squeeze(1)
                loss = F.smooth_l1_loss(current_q, target_q)  # Huber loss — more stable than Mean Squared Error

                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()

            if done:
                break

        epsilon = max(EPSILON_MIN, epsilon * EPSILON_DECAY)

        if ep % TARGET_UPDATE == 0:
            target_model.load_state_dict(model.state_dict())

        if ep % 1000 == 0 or ep == 1:
            print(f"  Episode {ep:6d}/{episodes}  epsilon={epsilon:.3f}")

    print("DRL training complete.")



# CLI parsing
def main():
    parser = argparse.ArgumentParser(description="Train Tic-Tac-Toe AI (PyTorch)")
    parser.add_argument("--phase",    choices=["supervised", "drl", "both"], default="both")
    parser.add_argument("--epochs",   type=int, default=300)
    parser.add_argument("--episodes", type=int, default=5000)
    parser.add_argument("--games",    type=int, default=5000)
    parser.add_argument("--lr",       type=float, default=1e-3)
    args = parser.parse_args()

    model = TicTacToeNet().to(device)

    if os.path.exists(_weights_path):
        load_weights(model, _weights_path)

    if args.phase in ("supervised", "both"):
        print("\n=== Phase 1: Supervised Pretraining ===")
        train_supervised(model, epochs=args.epochs, lr=args.lr, n_games=args.games)

    if args.phase in ("drl", "both"):
        print("\n=== Phase 2: Deep Q-Learning ===")
        train_drl(model, episodes=args.episodes)

    save_weights(model, _weights_path)
    print("\nRestart the Django server to load the new weights.")


if __name__ == "__main__":
    main()