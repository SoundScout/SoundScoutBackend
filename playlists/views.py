from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q

from playlists.models import Playlist, PlaylistTrack, Recommendation
from playlists.serializers import PlaylistSerializer, PlaylistTrackSerializer, RecommendationSerializer


class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()  
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        public_playlists = Q(name__in=['most_liked', 'admin_picks'])

        if not user.is_authenticated:
            return Playlist.objects.filter(public_playlists)

        return Playlist.objects.filter(public_playlists | Q(user=user))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PlaylistTrackViewSet(viewsets.ModelViewSet):
    queryset = PlaylistTrack.objects.all()  
    serializer_class = PlaylistTrackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PlaylistTrack.objects.filter(playlist__user=self.request.user)

    def perform_create(self, serializer):
        playlist = serializer.validated_data['playlist']
        if playlist.user != self.request.user:
            raise PermissionDenied("You can only modify your own playlists.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.playlist.user != self.request.user:
            raise PermissionDenied("You can only remove tracks from your own playlists.")
        instance.delete()


class RecommendationViewSet(viewsets.ModelViewSet):
    queryset = Recommendation.objects.all()  
    serializer_class = RecommendationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Recommendation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)