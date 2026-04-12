import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from django.conf import settings

class SpotifyService:
    _instance = None  # Singleton pattern to reuse connection
    
    def __new__(cls):
        """Create singleton instance - reuse same connection"""
        if cls._instance is None:
            cls._instance = super(SpotifyService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize only once"""
        if self._initialized:
            return
        
        try:
            print("🔌 Initializing Spotify API (Singleton)...")
            
            # Validate credentials exist
            if not settings.SPOTIFY_CLIENT_ID:
                raise ValueError("SPOTIFY_CLIENT_ID is not set")
            if not settings.SPOTIFY_CLIENT_SECRET:
                raise ValueError("SPOTIFY_CLIENT_SECRET is not set")
            
            print(f"   Client ID: {settings.SPOTIFY_CLIENT_ID[:10]}...")
            print(f"   Client Secret: {settings.SPOTIFY_CLIENT_SECRET[:10]}...")
            
            # Create credentials manager
            self.client_credentials_manager = SpotifyClientCredentials(
                client_id=settings.SPOTIFY_CLIENT_ID,
                client_secret=settings.SPOTIFY_CLIENT_SECRET
            )
            
            # Create Spotify client
            self.sp = spotipy.Spotify(
                client_credentials_manager=self.client_credentials_manager
            )
            
            print("✅ Spotify API initialized successfully!")
            self._initialized = True
            
        except Exception as e:
            print(f"❌ Spotify initialization error: {e}")
            self._initialized = False
            raise

    def search_track(self, query, limit=10):
        """Search for songs on Spotify"""
        try:
            if not query or query.strip() == "":
                print("❌ Empty query")
                return []
            
            if not self._initialized or not self.sp:
                print("❌ Spotify client not initialized")
                return []
            
            print(f"\n🔍 Searching Spotify for: '{query}'")
            
            # Perform search
            results = self.sp.search(
                q=query.strip(),
                type='track',
                limit=limit
            )
            
            if not results:
                print("❌ No results object")
                return []
            
            if 'tracks' not in results:
                print("❌ No 'tracks' in results")
                return []
            
            if not results['tracks']['items']:
                print("❌ No tracks in items")
                return []
            
            tracks = []
            
            for item in results['tracks']['items']:
                try:
                    # Extract track info safely
                    track_id = item.get('id', '')
                    title = item.get('name', 'Unknown')
                    
                    # Get artist safely
                    artists = item.get('artists', [])
                    artist = artists[0].get('name', 'Unknown') if artists else 'Unknown'
                    
                    # Get album safely
                    album = item.get('album', {}).get('name', 'Unknown')
                    
                    # Get image safely
                    album_images = item.get('album', {}).get('images', [])
                    image = album_images[0].get('url') if album_images else None
                    
                    # Get preview and other info
                    preview_url = item.get('preview_url')
                    duration = item.get('duration_ms', 0)
                    external_url = item.get('external_urls', {}).get('spotify', '')
                    
                    track = {
                        'id': track_id,
                        'title': title,
                        'artist': artist,
                        'album': album,
                        'image': image,
                        'preview_url': preview_url,
                        'duration': duration,
                        'external_url': external_url,
                    }
                    tracks.append(track)
                    
                except Exception as e:
                    print(f"⚠️  Error parsing track: {e}")
                    continue
            
            print(f"✅ Found {len(tracks)} tracks")
            for i, track in enumerate(tracks[:3], 1):
                print(f"   {i}. {track['title']} by {track['artist']}")
            
            return tracks
            
        except spotipy.exceptions.SpotifyException as e:
            print(f"❌ Spotify API Error: {e}")
            print(f"   Status: {e.http_status}")
            print(f"   Message: {e.msg}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_track_info(self, track_id):
        """Get detailed info about a track"""
        try:
            if not self.sp or not self._initialized:
                print("❌ Spotify client not initialized")
                return None
            
            track = self.sp.track(track_id)
            
            return {
                'id': track['id'],
                'title': track['name'],
                'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown',
                'album': track['album']['name'],
                'image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'preview_url': track.get('preview_url'),
                'duration': track['duration_ms'],
                'popularity': track['popularity'],
                'external_url': track['external_urls']['spotify'],
            }
        except Exception as e:
            print(f"❌ Error getting track info: {e}")
            return None