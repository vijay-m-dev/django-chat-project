from django.urls import path, include
from . import views

urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),
    path('creategroup', views.createGroup, name='creategroup'),
    path('updateuser/<str:pk>', views.updateUser, name='updateuser'),
    path('confirm_adduser/<str:id1>/<str:id2>', views.confirmAddUser, name='confirm_adduser'),
    path('deleteuser/<str:id1>/<str:id2>', views.deleteUser, name='deleteuser'),
    path('viewgroup/<str:id1>', views.viewGroup, name='view_group'),
    path('deletegroupusers/<str:id1>', views.deleteGroupUsers, name='delete_groupusers'),
    path('deletegroup/<str:id1>', views.deleteGroup, name='delete_group'),
]
