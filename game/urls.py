from django.urls import path
from .views import MoveView, ValidateBoardView, HealthView, home

urlpatterns = [
    path("move/",     MoveView.as_view(),         name="ai-move"),
    path("validate/", ValidateBoardView.as_view(), name="validate-board"),
    path("health/",   HealthView.as_view(),        name="health"),
    path("", home, name='home' )
]
