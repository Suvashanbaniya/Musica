import requests
from django.conf import settings

class LastFMService:
    BASE_URL = "http://ws.audioscrobbler.com/2.0/"
    
    def __init__(self):
        self.api_key = settings.LASTFM_API_KEY
        if not self.api_key:
            raise ValueError("LASTFM_API_KEY not set in settings")
        print("✅ Last.fm Service initialized")
    
    def search_track(self, query, limit=10):
        """Search for songs on Last.fm"""
        try:
            if not query or query.strip() == "":
                print("❌ Empty query")
                return []
            
            print(f"\n🔍 Searching Last.fm for: '{query}'")
            
            params = {
                'method': 'track.search',
                'track': query.strip(),
                'api_key': self.api_key,
                'format': 'json',
                'limit': limit
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'results' not in data:
                print("❌ No results key in response")
                return []
            
            if 'trackmatches' not in data['results']:
                print("❌ No trackmatches in results")
                return []
            
            matches = data['results']['trackmatches']
            
            if isinstance(matches, dict) and 'track' not in matches:
                print("❌ No tracks in matches")
                return []
            
            track_list = matches.get('track', [])
            
            # Handle single track response (returns dict instead of list)
            if isinstance(track_list, dict):
                track_list = [track_list]
            
            tracks = []
            for item in track_list:
                try:
                    track = {
                        'id': item.get('mbid', ''),
                        'title': item.get('name', 'Unknown'),
                        'artist': item.get('artist', 'Unknown'),
                        'url': item.get('url', ''),
                        'listeners': item.get('listeners', '0'),
                        'image': None,
                    }
                    
                    # Get image if available
                    if item.get('image'):
                        images = item.get('image', [])
                        if isinstance(images, list) and len(images) > 0:
                            track['image'] = images[-1].get('#text', '')
                    
                    tracks.append(track)
                except Exception as e:
                    print(f"⚠️  Error parsing track: {e}")
                    continue
            
            print(f"✅ Found {len(tracks)} tracks")
            for i, track in enumerate(tracks[:3], 1):
                print(f"   {i}. {track['title']} by {track['artist']}")
            
            return tracks
            
        except requests.exceptions.Timeout:
            print("❌ Last.fm API timeout")
            return []
        except requests.exceptions.ConnectionError:
            print("❌ Connection error to Last.fm")
            return []
        except Exception as e:
            print(f"❌ Last.fm Error: {e}")
            import traceback
            traceback.print_exc()
            return []