from django.urls import path
from .views import MoveView, ValidateBoardView, HealthView, start, game, ChatbotView

urlpatterns = [
    path("move/",     MoveView.as_view(),         name="ai-move"),
    path("validate/", ValidateBoardView.as_view(), name="validate-board"),
    path("health/",   HealthView.as_view(),        name="health"),
    path("chat/",     ChatbotView.as_view(),       name="chat"),
    path("", start, name='start' ),
    path("game/", game, name='game' )
]
