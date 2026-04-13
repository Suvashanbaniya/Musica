from googleapiclient.discovery import build
from django.conf import settings

class YouTubeService:
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY not set in settings")
        print("✅ YouTube Service initialized")
    
    def search_music(self, query, limit=10):
        """Search for music videos on YouTube"""
        try:
            if not query or query.strip() == "":
                print("❌ Empty query")
                return []
            
            print(f"\n🔍 Searching YouTube for: '{query}'")
            
            youtube = build('youtube', 'v3', developerKey=self.api_key)
            
            request = youtube.search().list(
                part='snippet',
                q=query.strip(),
                type='video',
                maxResults=limit,
                order='relevance',
                videoCategoryId='10'  # Music category
            )
            
            response = request.execute()
            
            if 'items' not in response or not response['items']:
                print("❌ No videos found")
                return []
            
            videos = []
            for item in response.get('items', []):
                try:
                    video = {
                        'id': item['id']['videoId'],
                        'title': item['snippet']['title'],
                        'artist': item['snippet']['channelTitle'],
                        'description': item['snippet']['description'],
                        'image': item['snippet']['thumbnails'].get('medium', {}).get('url', ''),
                        'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                        'channel': item['snippet']['channelTitle'],
                    }
                    videos.append(video)
                except Exception as e:
                    print(f"⚠️  Error parsing video: {e}")
                    continue
            
            print(f"✅ Found {len(videos)} videos")
            for i, video in enumerate(videos[:3], 1):
                print(f"   {i}. {video['title']} by {video['artist']}")
            
            return videos
            
        except Exception as e:
            print(f"❌ YouTube Error: {e}")
            import traceback
            traceback.print_exc()
            return []