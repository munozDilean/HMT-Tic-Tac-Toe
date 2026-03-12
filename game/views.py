from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .ai import get_ai_move, check_winner, get_available_moves, encode_board
from .serializers import MoveRequestSerializer, ValidateBoardSerializer


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

