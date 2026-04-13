from django.shortcuts import render, get_object_or_404, redirect
from .models import Song, Artist, Comment, Creator
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .spotify_service import SpotifyService
# YouTube API Library
from googleapiclient.discovery import build
import requests
import json







#spotify service instance
def search_spotify(request):
    """Search Last.fm for songs (FREE API - no premium needed)"""
    query = request.GET.get('q', '')
    results = []
    error_message = None
    
    print(f"\n{'='*70}")
    print(f"LAST.FM SEARCH REQUEST")
    print(f"Query: '{query}'")
    print(f"{'='*70}")
    
    if query and query.strip():
        try:
            from music.lastfm_service import LastFMService
            
            service = LastFMService()
            results = service.search_track(query.strip(), limit=10)
            
            if not results:
                error_message = f"❌ No songs found for '{query}'"
                print(f"Error: {error_message}")
            else:
                print(f"✅ Successfully found {len(results)} songs")
                
        except Exception as e:
            error_message = f"❌ Error searching: {str(e)}"
            print(f"Exception: {error_message}")
            import traceback
            traceback.print_exc()
    else:
        error_message = "Please enter a search query"
    
    context = {
        'query': query,
        'results': results,
        'error_message': error_message,
    }
    
    print(f"Returning {len(results)} results\n")
    return render(request, 'search_spotify.html', context)


# =====================================================
# YouTube API - Search for Videos
# =====================================================
# =====================================================
# YouTube API HELPER (RENAMED ✅)
# =====================================================
def search_youtube_api(query, max_results=10):
    try:
        youtube = build(
            "youtube",
            "v3",
            developerKey=settings.YOUTUBE_API_KEY
        )

        request = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=max_results,
            order="relevance"
        )

        response = request.execute()

        videos = []
        for item in response.get('items', []):
            video_id = item['id']['videoId']

            video = {
                'video_id': video_id,
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'image': item['snippet']['thumbnails'].get('medium', {}).get('url', ''),
                'channel': item['snippet']['channelTitle'],
                'url': f"https://www.youtube.com/watch?v={video_id}",  # ✅ ADD THIS LINE
            }
            videos.append(video)

        print(f"✅ Found {len(videos)} videos for: {query}")
        return videos

    except Exception as e:
        print(f"❌ YouTube API Error: {e}")
        return []

# =====================================================
# Authentication Views
# =====================================================
@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    User login view
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {
                'error': 'Invalid username or password'
            })
    
    return render(request, 'login.html')


@require_http_methods(["GET", "POST"])
def register_view(request):
    """
    User registration view
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validate passwords match
        if password1 != password2:
            return render(request, 'register.html', {
                'error': 'Passwords do not match'
            })
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {
                'error': 'Username already exists'
            })
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        
        # Log user in
        login(request, user)
        return redirect('home')
    
    return render(request, 'register.html')


@login_required(login_url='login')
def logout_view(request):
    """
    User logout view
    """
    logout(request)
    return redirect('home')


# =====================================================
# Creator Profile Views
# =====================================================
@login_required(login_url='login')
def become_creator(request):
    """
    Create a creator profile
    """
    # Check if user already has a creator profile
    if hasattr(request.user, 'creator_profile'):
        return redirect('creator_dashboard')
    
    if request.method == 'POST':
        bio = request.POST.get('bio', '')
        profile_image = request.FILES.get('profile_image', None)
        
        # Create creator profile
        creator = Creator.objects.create(
            user=request.user,
            bio=bio,
            profile_image=profile_image
        )
        
        print(f"✅ Creator profile created for {request.user.username}")
        return redirect('creator_dashboard')
    
    return render(request, 'creator/become_creator.html')


@login_required(login_url='login')
def creator_dashboard(request):
    """
    Creator dashboard - view profile and upload videos
    """
    # Check if user has creator profile
    if not hasattr(request.user, 'creator_profile'):
        return redirect('become_creator')
    
    creator = request.user.creator_profile
    songs = creator.songs.all().order_by('-created_at')
    
    # Get rank
    all_creators = Creator.objects.filter(total_points__gt=0).order_by('-total_points')
    rank = list(all_creators).index(creator) + 1 if creator in all_creators else None
    
    context = {
        'creator': creator,
        'songs': songs,
        'rank': rank,
    }
    
    return render(request, 'creator/dashboard.html', context)


@login_required(login_url='login')
def upload_video(request):
    """
    Upload a video as creator
    """
    # Check if user has creator profile
    if not hasattr(request.user, 'creator_profile'):
        return redirect('become_creator')
    
    if request.method == 'POST':
        title = request.POST.get('title', '')
        youtube_link = request.POST.get('youtube_link', '')
        lyrics = request.POST.get('lyrics', '')
        artist_name = request.POST.get('artist', '')
        image = request.FILES.get('image', None)
        
        if not title or not youtube_link:
            return render(request, 'creator/upload_video.html', {
                'error': 'Title and YouTube link are required'
            })
        
        try:
            # Get or create artist
            if artist_name:
                artist, created = Artist.objects.get_or_create(
                    name=artist_name
                )
            else:
                artist = None
            
            # Create song with creator
            song = Song.objects.create(
                title=title,
                youtube_link=youtube_link,
                lyrics=lyrics,
                artist=artist,
                image=image,
                creator=request.user.creator_profile
            )
            
            print(f"✅ Video '{title}' uploaded by {request.user.username}")
            return redirect('song_detail', id=song.id)
        
        except Exception as e:
            print(f"❌ Error uploading video: {e}")
            return render(request, 'creator/upload_video.html', {
                'error': f'Error uploading video: {str(e)}'
            })
    
    return render(request, 'creator/upload_video.html')


# =====================================================
# Leaderboard - Top Creators
# =====================================================
def leaderboard(request):
    """
    Display top creators leaderboard
    """
    top_creators = Creator.objects.filter(total_points__gt=0).order_by('-total_points')[:10]
    
    context = {
        'top_creators': top_creators,
    }
    
    return render(request, 'leaderboard.html', context)


# =====================================================
# Home Page
# =====================================================
def home(request):
    """
    Display all songs or search results
    Show top 3 creators featured
    """
    query = request.GET.get('q')

    if query:
        songs = Song.objects.filter(title__icontains=query)
        print(f"DEBUG: Searched for '{query}' - Found {songs.count()} songs")
    else:
        songs = Song.objects.all().order_by('-created_at')
        print(f"DEBUG: Home page - Found {songs.count()} total songs")

    # Get top 3 creators
    top_creators = Creator.objects.filter(total_points__gt=0).order_by('-total_points')[:3]

    context = {
        'songs': songs,
        'top_creators': top_creators,
    }
    
    return render(request, 'home.html', context)


# =====================================================
# Song Detail Page - WITH YOUTUBE API ✅
# =====================================================
def song_detail(request, id):
    """
    Display song details, lyrics, comments, and YouTube video
    WITH YouTube API to fetch video metadata
    """
    song = get_object_or_404(Song, id=id)

    # Increase view count
    song.views += 1
    song.save()

    # YouTube Data
    video_data = None
    youtube_id = None
    error_message = None

    # ✅ VALIDATE AND PROCESS YOUTUBE ID
    if song.youtube_id:
        # Clean up the YouTube ID (remove any extra characters)
        youtube_id = song.youtube_id.strip()
        
        print(f"DEBUG: Song '{song.title}'")
        print(f"  youtube_id from DB: '{song.youtube_id}'")
        print(f"  youtube_id stripped: '{youtube_id}'")
        print(f"  Length: {len(youtube_id)}")
        
        # Validate format (11 characters)
        if len(youtube_id) == 11:
            # ✅ FETCH VIDEO DETAILS FROM YOUTUBE API
            try:
                youtube = build(
                    "youtube",
                    "v3",
                    developerKey=settings.YOUTUBE_API_KEY
                )

                request_obj = youtube.videos().list(
                    part="snippet,statistics",
                    id=youtube_id
                )

                response = request_obj.execute()
                
                if response.get('items'):
                    item = response['items'][0]
                    video_data = item
                    print(f"  ✅ API call successful - fetched video data")
                else:
                    print(f"  ⚠️ Video not found in API")
                    # Video will still play, just no metadata
                    video_data = None
            
            except Exception as e:
                print(f"  ⚠️ API Error: {e}")
                # Video will still play even if API fails
                video_data = None
                
        else:
            error_message = f"Invalid YouTube ID format: {youtube_id} (must be 11 characters)"
            print(f"  ❌ Invalid video ID - wrong length")
    else:
        error_message = "No YouTube video ID found for this song"
        print(f"DEBUG: No youtube_id for song: {song.title}")

    # ✅ COMMENT SUBMISSION - NO LOGIN REQUIRED
    if request.method == 'POST':
        content = request.POST.get("text")

        if content:
            # Get or create anonymous user
            username = request.POST.get("username", "Anonymous")
            if not username or username.strip() == "":
                username = "Anonymous"
            
            # Try to use logged-in user, otherwise create/use anonymous
            if request.user.is_authenticated:
                user = request.user
            else:
                # Create an anonymous user or use existing one
                user, created = User.objects.get_or_create(
                    username="anonymous_user",
                    defaults={
                        'first_name': 'Anonymous',
                        'email': 'anonymous@example.com'
                    }
                )
            
            Comment.objects.create(
                song=song,
                user=user,
                content=content
            )
            
            print(f"DEBUG: Comment added by {user.username}")
            return redirect('song_detail', id=id)

    comments = song.comments.order_by('-created_at')
    
    # Check if user liked the song
    is_liked = request.user.is_authenticated and request.user in song.likes.all()

    context = {
        'song': song,
        'comments': comments,
        'video_data': video_data,
        'youtube_id': youtube_id,
        'error_message': error_message,
        'is_liked': is_liked,
    }

    return render(request, 'song_detail.html', context)


# =====================================================
# Artist Detail Page
# =====================================================
def artist_detail(request, id):
    """
    Display artist info and all their songs
    """
    artist = get_object_or_404(Artist, id=id)
    songs = artist.song_set.all().order_by('-created_at')

    print(f"DEBUG: Artist detail - {artist.name} has {songs.count()} songs")

    context = {
        'artist': artist,
        'songs': songs,
    }

    return render(request, 'artist_detail.html', context)


# =====================================================
# Like System
# =====================================================
@login_required
def like_song(request, id):
    """
    Toggle like/unlike for a song
    """
    song = get_object_or_404(Song, id=id)

    if request.user in song.likes.all():
        song.likes.remove(request.user)
        print(f"DEBUG: {request.user.username} unliked {song.title}")
    else:
        song.likes.add(request.user)
        print(f"DEBUG: {request.user.username} liked {song.title}")

    return redirect('song_detail', id=id)


# =====================================================
# YouTube Search Page (View)
# =====================================================
# =====================================================
# YouTube Search Page (VIEW)
# =====================================================
def search_youtube(request):
    """
    Display YouTube search page and handle searches
    """
    query = request.GET.get('q', '').strip()
    results = []
    error_message = None

    print(f"🔎 YOUTUBE QUERY: {query}")

    if query:
        results = search_youtube_api(query, max_results=10)

        if not results:
            error_message = f"No videos found for '{query}'"
    else:
        error_message = "Please enter a search query"

    context = {
        'query': query,
        'results': results,
        'error_message': error_message,
    }

    return render(request, 'search_youtube.html', context)

# =====================================================
# API Endpoints
# =====================================================
@require_http_methods(["GET"])
def api_search_youtube(request):
    """
    API endpoint to search YouTube
    """
    query = request.GET.get('q', '')
    
    if not query or len(query) < 2:
        return JsonResponse({
            'success': False,
            'error': 'Search query too short'
        })
    
    videos = search_youtube_api(query, max_results=10)
    
    return JsonResponse({
        'success': True,
        'query': query,
        'count': len(videos),
        'videos': videos
    })


@require_http_methods(["GET"])
def api_get_video_details(request):
    """
    Get video details from YouTube
    """
    video_id = request.GET.get('video_id', '')
    
    if not video_id:
        return JsonResponse({
            'success': False,
            'error': 'No video ID provided'
        })
    
    try:
        youtube = build(
            "youtube",
            "v3",
            developerKey=settings.YOUTUBE_API_KEY
        )

        request_obj = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        )

        response = request_obj.execute()
        
        if response.get('items'):
            item = response['items'][0]
            video = {
                'video_id': video_id,
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'thumbnail': item['snippet']['thumbnails'].get('high', {}).get('url', ''),
                'channel': item['snippet']['channelTitle'],
                'views': item['statistics'].get('viewCount', 0),
                'likes': item['statistics'].get('likeCount', 0),
            }
            
            return JsonResponse({
                'success': True,
                'video': video
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Video not found'
            })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


# =====================================================
# Search Videos
# =====================================================
def search_video(request):
    """
    Search for songs in database and YouTube
    """
    query = request.GET.get('q', '')
    songs = Song.objects.all()
    youtube_results = []
    
    if query:
        # Search in database
        songs = songs.filter(title__icontains=query)
        print(f"DEBUG: Database search for '{query}' - Found {songs.count()} results")
        
        # Also search YouTube
        youtube_results = search_youtube_api(query, max_results=5)
    
    context = {
        'query': query,
        'songs': songs,
        'youtube_results': youtube_results,
    }
    return render(request, 'music/search_results.html', context)