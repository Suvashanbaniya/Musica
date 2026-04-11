import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from django.conf import settings

class SpotifyService:
    def __init__(self):
        try:
            if not settings.SPOTIFY_CLIENT_ID or not settings.SPOTIFY_CLIENT_SECRET:
                raise ValueError("Spotify credentials not set in environment")
            
            print("🔌 Initializing Spotify API...")
            self.client_credentials_manager = SpotifyClientCredentials(
                client_id=settings.SPOTIFY_CLIENT_ID,
                client_secret=settings.SPOTIFY_CLIENT_SECRET
            )
            self.sp = spotipy.Spotify(
                client_credentials_manager=self.client_credentials_manager
            )
            print("✅ Spotify API initialized successfully!")
        except Exception as e:
            print(f"❌ Spotify initialization error: {e}")
            raise

    def search_track(self, query, limit=10):
        """Search for songs on Spotify"""
        try:
            if not query or query.strip() == "":
                return []
            
            print(f"🔍 Searching Spotify for: '{query}'")
            results = self.sp.search(q=query, type='track', limit=limit)
            
            if not results or 'tracks' not in results:
                print("❌ No tracks found in results")
                return []
            
            tracks = []
            for item in results['tracks']['items']:
                try:
                    track = {
                        'id': item['id'],
                        'title': item['name'],
                        'artist': item['artists'][0]['name'] if item['artists'] else 'Unknown',
                        'album': item['album']['name'] if item['album'] else 'Unknown',
                        'image': item['album']['images'][0]['url'] if item['album'] and item['album']['images'] else None,
                        'preview_url': item.get('preview_url'),
                        'duration': item['duration_ms'],
                        'external_url': item['external_urls']['spotify'] if item['external_urls'] else None,
                    }
                    tracks.append(track)
                except Exception as e:
                    print(f"⚠️  Error parsing track: {e}")
                    continue
            
            print(f"✅ Found {len(tracks)} tracks")
            return tracks
        except Exception as e:
            print(f"❌ Search Error: {e}")
            return []

    def get_track_info(self, track_id):
        """Get detailed info about a track"""
        try:
            track = self.sp.track(track_id)
            return {
                'id': track['id'],
                'title': track['name'],
                'artist': track['artists'][0]['name'],
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

