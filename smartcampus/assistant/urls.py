from django.urls import path
from . import views

urlpatterns = [

    path('', views.chatbot, name='chatbot'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('lostfound/', views.lostfound, name='lostfound'),

    path('events/', views.events, name='events'),

    path('signup/', views.signup_view, name='signup'),

    path('login/', views.login_view, name='login'),

    path('logout/', views.logout_view, name='logout'),

]