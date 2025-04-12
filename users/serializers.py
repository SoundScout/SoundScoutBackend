from rest_framework import serializers
from users.models import User, Follow, Artist
from music.models import Track, TrackFeature, Interaction, ListeningHistory, TrackStatistics
from playlists.models import Playlist, PlaylistTrack, Recommendation
from subscriptions.models import Subscription


#Basic User Serializer
class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = '__all__'

    def get_profile_picture(self, obj):
        return obj.get_profile_picture()

#Follower System
class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'


#Artist Profile Serializer (used by admin/moderators/frontend)
class ArtistSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Artist
        fields = [
            'id',
            'user',
            'username',
            'user_email',
            'display_name',
            'bio',
            'profile_picture',
            'status',
            'created_at',
        ]
        read_only_fields = ['status', 'created_at', 'user_email', 'username']


#Artist Signup Serializer (used by POST /signup/artist/)
class ArtistSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'profile_picture']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role='artist',
            profile_picture=validated_data.get('profile_picture', '')
        )

        Artist.objects.create(
            user=user,
            display_name=user.username,
            profile_picture=user.profile_picture,
            status='pending'
        )

        return user