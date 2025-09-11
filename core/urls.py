from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),        
    path('', views.dashboard_view, name='dashboard'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('search/', views.search_users, name='search_users'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path("duel/start/", views.start_duel, name="start_duel"),
    path("duel/start/<int:user_id>/", views.start_duel, name="start_duel_with_user"),
    path("duel/<int:duel_id>/", views.duel_view, name="duel_view"),
    path("duel/<int:duel_id>/wait/", views.wait_for_opponent, name="wait_for_opponent"),
    path("duel/<int:duel_id>/attack/", views.attack, name="attack"),
    path("duel/<int:duel_id>/status/", views.duel_status, name="duel_status"),
    path("duel/<int:duel_id>/accept/", views.accept_duel, name="accept_duel"),
    path("duel/<int:duel_id>/decline/", views.decline_duel, name="decline_duel"),
    path("duels/", views.my_duels, name="my_duels"),
    path('duels/invitations/', views.get_duel_invitations, name='get_duel_invitations'),
    path('duel/<int:duel_id>/end/', views.end_duel, name='end_duel'),
    path('duel/<int:duel_id>/cancelled/', views.duel_cancelled, name='duel_cancelled'),
    path('duel/<int:duel_id>/declined_info/', views.duel_declined_info, name='duel_declined_info'),
]

