from rest_framework import serializers
from users.models import User, Follow
from music.models import Artist, Track, TrackFeature, Interaction, ListeningHistory, TrackStatistics
from playlists.models import Playlist, PlaylistTrack, Recommendation
from subscriptions.models import Subscription

# Music Serializers
class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'

class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = '__all__'

class TrackFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackFeature
        fields = '__all__'

class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = '__all__'

    def validate(self, data):
        if data['interaction_type'] == 'comment' and not data.get('comment_text'):
            raise serializers.ValidationError("Comment text is required for comment interactions.")
        return data

#class CommentSerializer(serializers.ModelSerializer):
#    class Meta:
#       model = Comment
#        fields = '__all__'

class ListeningHistorySerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)

    class Meta:
        model = ListeningHistory
        fields = ['track', 'listened_at']

class TrackStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackStatistics
        fields = '__all__'
        read_only_fields = ['plays_count', 'likes_count', 'comments_count', 'updated_at']
