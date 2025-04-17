from django.db import models
from users.models import Artist
from django.conf import settings

# Track Model
class Track(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="tracks")
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=50, blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    demo_start_time = models.IntegerField(default=0)
    audio_url = models.URLField(max_length=500)
    artwork_url = models.URLField(max_length=500, blank=True, null=True)
    lyrics = models.TextField(blank=True, null=True)
    approval_status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# Track Features Model
class TrackFeature(models.Model):
    MOOD_CHOICES = [
        ('happy',    'Happy'),
        ('sad',      'Sad'),
        ('energetic','Energetic'),
        ('calm',     'Calm'),
        ('romantic', 'Romantic'),
        ('angry',    'Angry'),
        ('chill',    'Chill'),
    ]

    track = models.OneToOneField(Track, on_delete=models.CASCADE)
    danceability     = models.FloatField()
    energy           = models.FloatField()
    valence          = models.FloatField()
    tempo            = models.FloatField()
    speechiness      = models.FloatField()
    instrumentalness = models.FloatField()
    acousticness     = models.FloatField()
    liveness         = models.FloatField()
    mood             = models.CharField(max_length=20, choices=MOOD_CHOICES, db_index=True)

    class Meta:
        ordering = ['track']


# Interaction Model (like, stream, comment)
class Interaction(models.Model):
    INTERACTION_TYPES = [
        ('like',   'Like'),
        ('stream', 'Stream'),
        ('comment','Comment'),
    ]

    user             = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interactions')
    track            = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(
        max_length=10,
        choices=INTERACTION_TYPES,
        default='stream',
        db_index=True
    )
    comment_text     = models.TextField(null=True, blank=True)
    created_at       = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.interaction_type == 'comment' and not self.comment_text:
            raise ValueError("Comment text is required when interaction_type is 'comment'.")
        if self.interaction_type != 'comment':
            self.comment_text = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.interaction_type} - {self.track}"


# Listening History Model
class ListeningHistory(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    track       = models.ForeignKey(Track, on_delete=models.CASCADE)
    listened_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-listened_at']


# Track Statistics Model
class TrackStatistics(models.Model):
    track          = models.OneToOneField(Track, on_delete=models.CASCADE)
    plays_count    = models.IntegerField(default=0)
    likes_count    = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    updated_at     = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ['-updated_at']