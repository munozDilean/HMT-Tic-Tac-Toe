from rest_framework import serializers


VALID_CELLS = {"X", "O", None}


class MoveRequestSerializer(serializers.Serializer):
    board = serializers.ListField(
        child=serializers.CharField(max_length=1, allow_null=True),
        min_length=9,
        max_length=9,
        help_text='9-element list: "X", "O", or null',
    )
    player = serializers.ChoiceField(
        choices=["X", "O"],
        help_text="Which player the AI is playing as",
    )
    mode = serializers.ChoiceField(
        choices=["auto", "minimax", "neural"],
        default="auto",
        required=False,
        help_text="AI mode: auto | minimax | neural",
    )

    def validate_board(self, board):
        cleaned = []
        for cell in board:
            if cell in (None, "null", ""):
                cleaned.append(None)
            elif cell in ("X", "O"):
                cleaned.append(cell)
            else:
                raise serializers.ValidationError(
                    f'Invalid cell value "{cell}". Must be "X", "O", or null.'
                )
        return cleaned


class MoveResponseSerializer(serializers.Serializer):
    move = serializers.IntegerField()
    board = serializers.ListField(child=serializers.CharField(allow_null=True))
    winner = serializers.CharField(allow_null=True)
    game_over = serializers.BooleanField()
    ai_type = serializers.CharField()
    encoded_state = serializers.ListField(child=serializers.FloatField())


class ValidateBoardSerializer(serializers.Serializer):
    board = serializers.ListField(
        child=serializers.CharField(max_length=1, allow_null=True),
        min_length=9,
        max_length=9,
    )

    # simplified this method
    def validate_board(self, board):
        return [None if c in (None, "null", "") else c for c in board]
