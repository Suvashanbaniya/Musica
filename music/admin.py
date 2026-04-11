from django.contrib import admin
from .models import Creator, Song, Artist, Comment

# =====================================================
# Creator Admin
# =====================================================
@admin.register(Creator)
class CreatorAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_points', 'total_videos', 'is_featured', 'created_at')
    list_filter = ('created_at', 'is_featured')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'total_points', 'total_videos')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Profile', {
            'fields': ('bio', 'profile_image')
        }),
        ('Statistics', {
            'fields': ('total_points', 'total_videos', 'is_featured'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# =====================================================
# Artist Admin
# =====================================================
@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'genre', 'song_count')
    list_filter = ('genre',)
    search_fields = ('name',)
    
    fieldsets = (
        ('Artist Information', {
            'fields': ('name', 'genre')
        }),
        ('Details', {
            'fields': ('bio', 'image')
        }),
    )
    
    def song_count(self, obj):
        """Display number of songs by this artist"""
        return obj.song_set.count()
    song_count.short_description = 'Total Songs'


# =====================================================
# Song Admin - WITH DUPLICATE PREVENTION
# =====================================================
@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'creator', 'views', 'likes_count', 'created_at')
    list_filter = ('created_at', 'artist', 'creator')
    search_fields = ('title', 'artist__name', 'creator__user__username')
    readonly_fields = ('views', 'created_at', 'youtube_id_display')
    
    fieldsets = (
        ('Song Information', {
            'fields': ('title', 'artist', 'creator'),
            'description': '⚠️ Title + Artist combination must be unique'
        }),
        ('Media & Links', {
            'fields': ('image', 'youtube_link', 'youtube_id_display')
        }),
        ('Content', {
            'fields': ('lyrics', 'chords'),
            'description': 'Add lyrics and guitar chords here'
        }),
        ('Statistics', {
            'fields': ('views', 'created_at', 'likes'),
            'classes': ('collapse',)
        }),
    )
    
    def youtube_id_display(self, obj):
        """Display the extracted YouTube ID"""
        if obj.youtube_id:
            return f"✅ {obj.youtube_id}"
        return "❌ No YouTube ID"
    youtube_id_display.short_description = 'YouTube Video ID'
    
    def likes_count(self, obj):
        """Display number of likes"""
        return obj.total_likes()
    likes_count.short_description = 'Likes'
    
    def save_model(self, request, obj, form, change):
        """
        Override save to:
        1. Extract YouTube ID from link
        2. Check for duplicates
        """
        # Extract YouTube ID if not already set
        if obj.youtube_link and not obj.youtube_id:
            from django.core.exceptions import ValidationError
            
            # Try to extract ID
            youtube_link = obj.youtube_link
            youtube_id = None
            
            # Handle different YouTube URL formats
            if 'youtu.be/' in youtube_link:
                youtube_id = youtube_link.split('youtu.be/')[1].split('?')[0].split('&')[0]
            elif 'youtube.com/watch?v=' in youtube_link:
                youtube_id = youtube_link.split('v=')[1].split('&')[0]
            
            if youtube_id and len(youtube_id) == 11:
                obj.youtube_id = youtube_id
                print(f"✅ Extracted YouTube ID: {youtube_id}")
            else:
                raise ValidationError(
                    "Invalid YouTube URL. Use: https://youtu.be/VIDEO_ID or https://youtube.com/watch?v=VIDEO_ID"
                )
        
        # Check for duplicate songs (same title + artist)
        duplicate = Song.objects.filter(
            title=obj.title,
            artist=obj.artist
        ).exclude(id=obj.id).first()
        
        if duplicate:
            from django.core.exceptions import ValidationError
            raise ValidationError(
                f"❌ Duplicate Song: '{obj.title}' by '{obj.artist.name}' already exists!\n\n"
                f"Please use a different title or artist."
            )
        
        super().save_model(request, obj, form, change)
        print(f"✅ Song saved: {obj.title} by {obj.artist.name}")


# =====================================================
# Comment Admin
# =====================================================
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'song', 'created_at', 'content_preview')
    list_filter = ('created_at', 'song')
    search_fields = ('user__username', 'song__title', 'content')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('song', 'user')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        """Display first 50 characters of comment"""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Comment Preview'


# =====================================================
# Admin Site Customization
# =====================================================
admin.site.site_header = "🎵 Sangeet Music Admin"
admin.site.site_title = "Sangeet Music"
admin.site.index_title = "Welcome to Sangeet Music Admin Panel"