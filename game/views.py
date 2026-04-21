from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
import random

from .ai import get_ai_move, check_winner, get_available_moves, encode_board
from .serializers import MoveRequestSerializer, ValidateBoardSerializer

context = {}

class MoveView(APIView):

    def post(self, request):
        serializer = MoveRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        board = data["board"]
        player = data["player"]
        mode = data.get("mode", "auto")

        winner = check_winner(board)
        if winner:
            return Response(
                {"error": f"Game is already over. Winner: {winner}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not get_available_moves(board):
            return Response(
                {"error": "No moves available."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = get_ai_move(board, player, mode=mode)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(result, status=status.HTTP_200_OK)


class ValidateBoardView(APIView):
    """POST /api/validate/ — check board state and return status."""

    def post(self, request):
        serializer = ValidateBoardSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        board = serializer.validated_data["board"]
        winner = check_winner(board)

        return Response({
            "valid": True,
            "winner": winner,
            "game_over": winner is not None,
            "available_moves": get_available_moves(board),
            "encoded_state": encode_board(board).tolist(),
        })


class HealthView(APIView):
    """GET /api/health/ — liveness probe."""

    def get(self, request):
        import os
        from .ai import _weights_path
        return Response({
            "status": "ok",
            "neural_weights_loaded": os.path.exists(_weights_path),
            "encoding": "one-hot 2-bit per cell | X=[1,0] O=[0,1] empty=[0,0]",
        })

def start(request):
    global context
    start_treatment = random.randint(0,1)
    print(f"Start Treatment: {start_treatment}")
    context = {"startTreatment" : start_treatment}
    return render(request, "start.html", context)

def game(request):
    global context
    return render(request, "game.html", context)

class ChatbotView(APIView):
    def post(self, request):
        message = request.data.get("message", "")
        board = request.data.get("board", [])
        chat_history = request.data.get("history", [])
        
        formatted_board = [str(i) if not cell.strip() else cell.strip() for i, cell in enumerate(board)]
        grid = f"""
{formatted_board[0]} | {formatted_board[1]} | {formatted_board[2]}
---------
{formatted_board[3]} | {formatted_board[4]} | {formatted_board[5]}
---------
{formatted_board[6]} | {formatted_board[7]} | {formatted_board[8]}
"""

        from .ai import minimax_move
        import copy
        
        # Calculate available moves explicitly
        available_moves = [str(i) for i, cell in enumerate(board) if not cell.strip()]
        
        # Calculate the mathematical perfect move using Minimax
        board_for_minimax = [None if not cell.strip() else cell.strip() for cell in board]
        # Only run minimax if there's an available move
        perfect_move = None
        if available_moves:
            perfect_move = minimax_move(board_for_minimax, "X")

        is_suggestion = request.data.get("is_suggestion", False)

        system_prompt = f"""[SYSTEM]
You are an expert Tic-Tac-Toe advisor helping a human player who is playing as X.
The opponent is an AI playing as O.

Current board:
{grid}

The human's objective is to achieve three X in a row (horizontally, vertically, or diagonally) before the opponent does.
You must analyze the board and suggest the best empty square numeric position for the human to choose this turn.
The following squares are currently EMPTY and are the ONLY VALID MOVES you can suggest: {', '.join(available_moves)}
"""
        if is_suggestion:
            system_prompt += f"\n[CRITICAL INSTRUCTION]: You MUST recommend that the human play in square {perfect_move}. This is mathematically the best move. You MUST include a short reasoning process outlining why square {perfect_move} is the best move (e.g. blocking the opponent, securing a win, or taking the center).\nYour final answer must clearly state the numeric position {perfect_move}."
        else:
            system_prompt += "\nYou MUST include a short reasoning process outlining your thoughts before answering.\nAnswer the human's question concisely in your final answer without using any XML tags."

        try:
            from openai import OpenAI
            client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
            
            # Dynamically grab the active model ID currently loaded in LM Studio
            # This prevents 400 errors when swapping models
            available_models = client.models.list()
            active_model = available_models.data[0].id if available_models.data else "local-model"
            
            messages = [{"role": "system", "content": system_prompt}]
            
            # ONLY include history if it's a manual chat to prevent suggestion loop hallucination
            if not is_suggestion:
                for msg in chat_history[-3:]:
                    messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
            
            final_user_content = f"Current Board:\n{grid}\n\n"
            if message:
                 final_user_content += f"Human Question: {message}"
            else:
                 final_user_content += "Analyze the board. Where should I play? Provide your reasoning, then state the chosen square number."
            
            messages.append({"role": "user", "content": final_user_content})
            
            response = client.chat.completions.create(
                model=active_model,
                messages=messages,
                temperature=0.5,
                max_tokens=150
            )
            
            msg = response.choices[0].message
            
            bot_message = msg.content

            return Response({"response": bot_message}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)