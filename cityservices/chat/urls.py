from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_room, name='chat_room'),
    path('<int:user_id>/', views.chat_room, name='chat_with_user'),
]