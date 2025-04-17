from django.contrib import admin
from .models import Track, TrackFeature, Interaction, ListeningHistory, TrackStatistics

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display  = ['title', 'artist', 'approval_status', 'created_at']
    list_filter   = ['approval_status', 'genre', 'created_at']
    search_fields = ['title', 'artist__display_name']
    ordering      = ['-created_at']

@admin.register(TrackFeature)
class TrackFeatureAdmin(admin.ModelAdmin):
    list_display  = ['track', 'danceability', 'energy', 'valence', 'mood']
    list_filter   = ['mood']
    search_fields = ['track__title']
    ordering      = ['track']

@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display  = ['user', 'track', 'interaction_type', 'created_at']
    list_filter   = ['interaction_type', 'created_at']
    search_fields = ['user__username', 'track__title']
    ordering      = ['-created_at']

@admin.register(ListeningHistory)
class ListeningHistoryAdmin(admin.ModelAdmin):
    list_display  = ['user', 'track', 'listened_at']
    list_filter   = ['listened_at']
    search_fields = ['user__username', 'track__title']
    ordering      = ['-listened_at']

@admin.register(TrackStatistics)
class TrackStatisticsAdmin(admin.ModelAdmin):
    list_display  = ['track', 'plays_count', 'likes_count', 'comments_count', 'updated_at']
    list_filter   = ['updated_at']
    search_fields = ['track__title']
    ordering      = ['-updated_at']