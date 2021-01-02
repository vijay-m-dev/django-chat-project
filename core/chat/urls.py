from django.urls import path, include
from . import views

urlpatterns = [
    path('<str:room_name>/',views.room, name='room'),
    path('single/<str:person_id>/',views.singleChatRoom, name='single_chat_room'),
    

]
