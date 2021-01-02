from django.urls import path, include
from . import views

urlpatterns = [
	path('', views.loginPage, name='login'),
    path('register', views.registerPage, name='register'),
    path('logout', views.logoutUser, name="logout"),
]
