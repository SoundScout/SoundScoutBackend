from rest_framework import serializers
from music.models import Artist, Track, TrackFeature, Interaction, ListeningHistory, TrackStatistics
from users.serializers import ArtistSerializer as BaseArtistSerializer

# now in this file you can refer to UserArtistSerializer

# ----------------------------
# Artist (Music App)
# ----------------------------

class ArtistSerializer(BaseArtistSerializer):
    class Meta(BaseArtistSerializer.Meta):
        ref_name = "MusicArtist"


# ----------------------------
# Track
# ----------------------------
class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = '__all__'
        read_only_fields = ['approval_status', 'rejection_reason']


# ----------------------------
# Track Features
# ----------------------------
class TrackFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackFeature
        fields = '__all__'


# ----------------------------
# Interaction
# ----------------------------
class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = '__all__'

    def validate(self, data):
        if data['interaction_type'] == 'comment' and not data.get('comment_text'):
            raise serializers.ValidationError("Comment text is required for comment interactions.")
        return data


# ----------------------------
# Listening History
# ----------------------------
class ListeningHistorySerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)

    class Meta:
        model = ListeningHistory
        fields = ['track', 'listened_at']


# ----------------------------
# Track Statistics
# ----------------------------
class TrackStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackStatistics
        fields = '__all__'
        read_only_fields = ['plays_count', 'likes_count', 'comments_count', 'updated_at']