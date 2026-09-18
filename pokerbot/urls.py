from django.urls import path

from . import views

urlpatterns = [
    path("start/", views.start_game, name="start_game"),
    path("", views.game, name="game"),
    path("act/", views.act, name="act"),
]