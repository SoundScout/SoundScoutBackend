from django.db import models
from users.models import User
from music.models import Track

# Playlist Model
class Playlist(models.Model):
    PLAYLIST_TYPES = [('most_liked', 'Most Liked'), ('admin_picks', 'Admin Picks'), ('for_you', 'For You'), ('liked_songs', 'Liked Songs')]
    
    name = models.CharField(max_length=20, choices=PLAYLIST_TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('name', 'user')

# Playlist Tracks Model
class PlaylistTrack(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('playlist', 'track')

# Recommendation Model
class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

