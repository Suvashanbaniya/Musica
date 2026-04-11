from django.db import models
from django.contrib.auth.models import User
from urllib.parse import urlparse, parse_qs
import re


# =====================================
# Creator Profile Model
# =====================================
class Creator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='creator_profile')
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='creators/', blank=True, null=True)
    total_points = models.IntegerField(default=0)
    total_videos = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-total_points']

    def __str__(self):
        return f"{self.user.username} - {self.total_points} points"

    def add_points(self, points=10):
        """Add points when video is created"""
        self.total_points += points
        self.total_videos += 1
        self.save()

    def is_top_creator(self):
        """Check if creator is in top 3"""
        top_creators = Creator.objects.filter(total_points__gt=0).order_by('-total_points')[:3]
        return self in top_creators


# =====================================
# Artist Model
# =====================================
class Artist(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()
    genre = models.CharField(max_length=100)

    image = models.ImageField(
        upload_to='artists/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


# =====================================
# Song Model - UPDATED WITH CREATOR
# =====================================
class Song(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE, related_name='songs', blank=True, null=True)

    lyrics = models.TextField(blank=True, null=True)

    image = models.ImageField(upload_to='songs/', blank=True, null=True)

    youtube_link = models.URLField(blank=True)
    youtube_id = models.CharField(max_length=50, blank=True)

    views = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    likes = models.ManyToManyField(
        User,
        related_name='liked_songs',
        blank=True
    )

    class Meta:
        ordering = ['-created_at']
        unique_together = ('title', 'artist')  # Prevent duplicate songs by same artist

    # ⭐ Extract YouTube ID (FIXED VERSION)
    def extract_video_id(self, url):
        """
        Extract YouTube video ID from various URL formats:
        - https://www.youtube.com/watch?v=dQw4w9WgXcQ
        - https://youtu.be/dQw4w9WgXcQ
        - https://youtu.be/dQw4w9WgXcQ?si=V8wi0aTYokmMaWqf (with query params)
        - https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s
        - Just the ID: dQw4w9WgXcQ
        """
        
        if not url:
            return ""
        
        url = url.strip()
        
        # If it's already just an ID (11 characters)
        if len(url) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
        
        # YouTube short URL: youtu.be/ID (handles query parameters)
        if "youtu.be/" in url:
            try:
                # Extract everything after youtu.be/
                after_domain = url.split("youtu.be/")[1]
                # Remove query parameters (anything after ? or &)
                video_id = after_domain.split("?")[0]
                # Remove trailing slashes
                video_id = video_id.rstrip("/")
                
                if len(video_id) == 11:
                    return video_id
            except:
                pass
        
        # YouTube standard URL: youtube.com/watch?v=ID
        if "watch?v=" in url:
            try:
                video_id = url.split("v=")[1].split("&")[0]
                if len(video_id) == 11:
                    return video_id
            except:
                pass
        
        # Parse using URL parsing (handles edge cases)
        try:
            parsed_url = urlparse(url)
            
            # For youtube.com/watch?v=ID format
            if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
                query_params = parse_qs(parsed_url.query)
                if 'v' in query_params:
                    video_id = query_params['v'][0]
                    if len(video_id) == 11:
                        return video_id
            
            # For youtu.be/ID format
            if parsed_url.hostname in ['youtu.be', 'www.youtu.be']:
                video_id = parsed_url.path.lstrip('/')
                if len(video_id) == 11:
                    return video_id
        except:
            pass
        
        return ""

    # ⭐ Auto save video ID
    def save(self, *args, **kwargs):
        if self.youtube_link:
            self.youtube_id = self.extract_video_id(self.youtube_link)
        
        # Add points to creator when song is created
        if self.pk is None and self.creator:
            self.creator.add_points(10)
        
        super().save(*args, **kwargs)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title


# =====================================
# Comment Model
# =====================================
class Comment(models.Model):
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.song.title}"