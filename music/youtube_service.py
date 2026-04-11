from googleapiclient.discovery import build
from django.conf import settings

def get_video_details(video_id):

    youtube = build(
        "youtube",
        "v3",
        developerKey=settings.YOUTUBE_API_KEY
    )

    request = youtube.videos().list(
        part="snippet,contentDetails",
        id=video_id
    )

    response = request.execute()

    return response

#credentials of spotify = bfff5799a2d24c3aa572bb6580793b51
#client secret credentials of spotify = 35e546536e0f43a5b6073d93286f6ec8