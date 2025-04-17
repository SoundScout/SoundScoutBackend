from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from playlists.models import Playlist, PlaylistTrack, Recommendation
from playlists.serializers import (
    PlaylistSerializer,
    PlaylistTrackSerializer,
    RecommendationSerializer
)


# Custom permission to ensure the track belongs to the requesting user’s playlist
class IsPlaylistOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # obj here is a PlaylistTrack instance
        return obj.playlist.user == request.user


class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]

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
    permission_classes = [permissions.IsAuthenticated, IsPlaylistOwner]
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        # Only allow the user to see tracks in their own playlists
        return PlaylistTrack.objects.filter(playlist__user=self.request.user)

    def perform_create(self, serializer):
        playlist = serializer.validated_data['playlist']
        if playlist.user != self.request.user:
            raise PermissionDenied("You can only add to your own playlists.")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        # DRF will call get_object(), then check_object_permissions()
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        return super().destroy(request, *args, **kwargs)


class RecommendationViewSet(viewsets.ModelViewSet):
    """
    Global, admin‐curated recommendations visible to all users.
    List/read is open to anyone; create/update/delete restricted to admins/moderators.
    """
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['track__title']

    def perform_create(self, serializer):
        if self.request.user.role not in ['admin', 'moderator']:
            raise PermissionDenied("Only admins or moderators can add recommendations.")
        serializer.save()

    def perform_update(self, serializer):
        if self.request.user.role not in ['admin', 'moderator']:
            raise PermissionDenied("Only admins or moderators can modify recommendations.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.role not in ['admin', 'moderator']:
            raise PermissionDenied("Only admins or moderators can remove recommendations.")
        instance.delete()