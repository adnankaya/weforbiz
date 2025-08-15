# chat/urls.py
from django.urls import path

from . import views

app_name = "chats"

urlpatterns = [
    path("", views.index, name="chat-index"),
    path("start-chat/", views.start_chat, name="start-chat"),
    path("rooms/<str:room_name>/", views.room, name="room"),
]
