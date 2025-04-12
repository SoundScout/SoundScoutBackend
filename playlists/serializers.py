from rest_framework import serializers
from users.models import User, Follow
from music.models import Artist, Track, TrackFeature, Interaction, ListeningHistory, TrackStatistics
from playlists.models import Playlist, PlaylistTrack, Recommendation
from subscriptions.models import Subscription
from music.serializers import TrackSerializer

# Playlist Serializers
class PlaylistSerializer(serializers.ModelSerializer):
    track_count = serializers.SerializerMethodField()
    display_name = serializers.CharField(source='get_name_display', read_only=True)

    class Meta:
        model = Playlist
        fields = ['id', 'name', 'display_name', 'user', 'created_at', 'track_count']

    def get_track_count(self, obj):
        return obj.playlisttrack_set.count()

class PlaylistTrackSerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)  # from music.serializers

    class Meta:
        model = PlaylistTrack
        fields = ['id', 'playlist', 'track', 'added_at']

class RecommendationSerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)

    class Meta:
        model = Recommendation
        fields = ['id', 'user', 'track', 'added_at']
