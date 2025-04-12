from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import User
from music.models import Artist, Track, TrackFeature, Interaction, ListeningHistory, TrackStatistics
from playlists.models import Playlist, PlaylistTrack, Recommendation
from subscriptions.models import Subscription
from users.serializers import UserSerializer
from music.serializers import (
    ArtistSerializer,
    TrackSerializer,
    TrackFeatureSerializer,
    InteractionSerializer,
    ListeningHistorySerializer,
    TrackStatisticsSerializer
)
from playlists.serializers import PlaylistSerializer, PlaylistTrackSerializer, RecommendationSerializer
from subscriptions.serializers import SubscriptionSerializer


class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class TrackViewSet(viewsets.ModelViewSet):
    serializer_class = TrackSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Track.objects.all()
    
    def get_queryset(self):
        user = self.request.user

        # Public, listener, or artist: only approved tracks
        if not user.is_authenticated or user.role in ['listener', 'artist']:
            return Track.objects.filter(approval_status='approved')

        # Moderator/admin: see all
        return Track.objects.all()


class TrackFeatureViewSet(viewsets.ModelViewSet):
    queryset = TrackFeature.objects.all()
    serializer_class = TrackFeatureSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class InteractionViewSet(viewsets.ModelViewSet):
    queryset = Interaction.objects.all()
    serializer_class = InteractionSerializer
    permission_classes = [IsAuthenticated]


# class CommentViewSet(viewsets.ModelViewSet):
#     queryset = Comment.objects.all()
#     serializer_class = CommentSerializer
#     permission_classes = [IsAuthenticated]


class ListeningHistoryViewSet(viewsets.ModelViewSet):
    queryset = ListeningHistory.objects.all()
    serializer_class = ListeningHistorySerializer
    permission_classes = [IsAuthenticated]


class TrackStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TrackStatistics.objects.all()
    serializer_class = TrackStatisticsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


#Artist's own uploaded tracks (any status)
class MyTracksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Only artists can access their uploads
        if user.role != 'artist':
            return Response({"error": "Only artists can access their uploaded tracks."}, status=403)

        # Get tracks uploaded by this artist (via FK)
        tracks = Track.objects.filter(artist__user=user).order_by('-created_at')
        serializer = TrackSerializer(tracks, many=True)
        return Response(serializer.data)
    
class TracksByArtistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, artist_id):
        user = request.user

        # Only allow moderators/admins to access this view
        if not user.is_authenticated:
            return Response({"error": "Authentication required."}, status=401)
        if user.role not in ['moderator', 'admin']:
            return Response({"error": "Access denied. Moderators only."}, status=403)
        tracks = Track.objects.filter(artist__id=artist_id).order_by('-created_at')
        serializer = TrackSerializer(tracks, many=True)
        return Response(serializer.data)