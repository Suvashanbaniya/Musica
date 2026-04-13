from django.urls import path
from . import views

urlpatterns = [
    # =====================================================
    # Main Pages
    # =====================================================
    path('', views.home, name='home'),
    path('song/<int:id>/', views.song_detail, name='song_detail'),
    path('artist/<int:id>/', views.artist_detail, name='artist_detail'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    
    
    # =====================================================
    # Authentication
    # =====================================================
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    
    # =====================================================
    # Creator System
    # =====================================================
    path('become-creator/', views.become_creator, name='become_creator'),
    path('creator-dashboard/', views.creator_dashboard, name='creator_dashboard'),
    path('upload-video/', views.upload_video, name='upload_video'),
    
    
    # =====================================================
    # Like System
    # =====================================================
    path('song/<int:id>/like/', views.like_song, name='like_song'),
    
    
    # =====================================================
    # YouTube Features
    # =====================================================
    path('youtube-search/', views.search_youtube, name='search_youtube'),
    path('search/', views.search_video, name='search_video'),
    
    
    # =====================================================
    # API Endpoints
    # =====================================================
    path('api/search-youtube/', views.api_search_youtube, name='api_search_youtube'),
    path('api/video-details/', views.api_get_video_details, name='api_video_details'),
    path('search-spotify/', views.search_spotify, name='search_spotify'),
]