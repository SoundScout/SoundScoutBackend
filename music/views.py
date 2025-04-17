# music/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging
music_logger = logging.getLogger('music')
from users.models import Artist
from music.models import Track, TrackFeature, Interaction, ListeningHistory, TrackStatistics
from users.serializers import ArtistSerializer as MusicArtistSerializer
from music.serializers import (
    TrackSerializer,
    TrackFeatureSerializer,
    InteractionSerializer,
    ListeningHistorySerializer,
    TrackStatisticsSerializer,
)


# ----------------------------
# Artist Endpoints
# ----------------------------
class ArtistViewSet(viewsets.ModelViewSet):
    """
    CRUD for Artist profiles.
    """
    queryset = Artist.objects.all()
    serializer_class = MusicArtistSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]

    @swagger_auto_schema(
        tags=['Artists'],
        operation_summary="List all artists",
        operation_description="Returns a paginated list of all artist profiles (approved, pending, and rejected).",
        responses={200: MusicArtistSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Artists'],
        operation_summary="Retrieve an artist",
        operation_description="Get the details of a single artist profile by its ID.",
        responses={200: MusicArtistSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Artists'],
        operation_summary="Create a new artist profile",
        operation_description="Create a new artist profile. Requires authenticated user and valid payload.",
        request_body=MusicArtistSerializer,
        responses={201: MusicArtistSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Artists'],
        operation_summary="Update an artist profile",
        operation_description="Modify an existing artist profile by its ID.",
        request_body=MusicArtistSerializer,
        responses={200: MusicArtistSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Artists'],
        operation_summary="Delete an artist profile",
        operation_description="Remove an artist profile by its ID.",
        responses={204: openapi.Response(description="No Content")}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

# ----------------------------
# Track Endpoints
# ----------------------------
class TrackViewSet(viewsets.ModelViewSet):
    """
    Only artists may create tracks; listeners & anonymous can only read approved tracks.
    """
    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]

    @swagger_auto_schema(
        tags=['Music Tracks'],
        operation_summary="List approved tracks",
        operation_description=(
            "For anonymous or listener/artist roles, returns only approved tracks; "
            "for moderators and admins, returns all tracks."
        ),
        responses={200: TrackSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Music Tracks'],
        operation_summary="Retrieve a track",
        operation_description="Get the details of a single track by its ID.",
        responses={200: TrackSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Music Tracks'],
        operation_summary="Upload a new track",
        operation_description=(
            "Only authenticated users with the 'artist' role may upload a new track. "
            "Provide at least `title` and `audio_file` (multipart/form-data)."
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['title', 'audio_file'],
            properties={
                'title':      openapi.Schema(type=openapi.TYPE_STRING, description='Track title'),
                'audio_file': openapi.Schema(type=openapi.TYPE_FILE, description='Audio file (mp3/wav)'),
                'genre':      openapi.Schema(type=openapi.TYPE_STRING, description='Genre (optional)'),
                'lyrics':     openapi.Schema(type=openapi.TYPE_STRING, description='Lyrics text (optional)'),
            }
        ),
        responses={
            201: TrackSerializer,
            403: openapi.Response(description="Forbidden – only artists can upload"),
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Music Tracks'],
        operation_summary="Update a track",
        operation_description="Modify an existing track’s metadata (artists only).",
        request_body=TrackSerializer,
        responses={200: TrackSerializer}
    )
    def update(self, request, *args, **kwargs):
        # Capture old status to compare after save
        instance = self.get_object()
        old_status = instance.approval_status
        updated = super().update(request, *args, **kwargs)
        new_status = self.get_object().approval_status
        # Log if approval_status changed
        if old_status != new_status:
            music_logger.info(
                f"Track {instance.id} ('{instance.title}') status changed "
                f"from {old_status} to {new_status} by user {request.user.id}"
            )
        return updated

    @swagger_auto_schema(
        tags=['Music Tracks'],
        operation_summary="Delete a track",
        operation_description="Remove a track by its ID (artists and above).",
        responses={204: openapi.Response(description="No Content")}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated or user.role in ['listener', 'artist']:
            return Track.objects.filter(approval_status='approved')
        return Track.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated or user.role != 'artist':
            raise PermissionDenied("Only users with the 'artist' role can upload tracks.")
        artist = Artist.objects.get(user=user)
        serializer.save(artist=artist)
    
    def update(self, request, *args, **kwargs):
        # 1) grab the existing instance and its old status
        instance = self.get_object()
        old_status = instance.approval_status

        # 2) perform the normal update
        response = super().update(request, *args, **kwargs)

        # 3) re-fetch the instance and compare statuses
        new_instance = self.get_object()
        new_status = new_instance.approval_status

        if old_status != new_status:
            music_logger.info(
                f"Track {new_instance.id} ('{new_instance.title}') status changed "
                f"from {old_status} to {new_status} by user {request.user.id}"
            )

        return response


# ----------------------------
# TrackFeature Endpoints
# ----------------------------
class TrackFeatureViewSet(viewsets.ModelViewSet):
    """
    CRUD for TrackFeature.
    """
    queryset = TrackFeature.objects.all()
    serializer_class = TrackFeatureSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]

    @swagger_auto_schema(
        tags=['Track Features'],
        operation_summary="List all track features",
        operation_description="Returns all extracted audio feature records.",
        responses={200: TrackFeatureSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Track Features'],
        operation_summary="Retrieve track features",
        operation_description="Get the features for a specific track by Feature ID.",
        responses={200: TrackFeatureSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Track Features'],
        operation_summary="Create track features",
        operation_description="Manually create feature data for a track (rarely used).",
        request_body=TrackFeatureSerializer,
        responses={201: TrackFeatureSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Track Features'],
        operation_summary="Update track features",
        operation_description="Modify existing feature data for a track.",
        request_body=TrackFeatureSerializer,
        responses={200: TrackFeatureSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Track Features'],
        operation_summary="Delete track features",
        operation_description="Remove feature data by its ID.",
        responses={204: openapi.Response(description="No Content")}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


# ----------------------------
# Interaction Endpoints
# ----------------------------
class InteractionViewSet(viewsets.ModelViewSet):
    """
    CRUD for Interaction (likes, streams, comments).
    """
    queryset = Interaction.objects.all()
    serializer_class = InteractionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]

    @swagger_auto_schema(
        tags=['Interactions'],
        operation_summary="List interactions",
        operation_description="Returns all user interactions (likes, streams, comments).",
        responses={200: InteractionSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Interactions'],
        operation_summary="Create interaction",
        operation_description="Record a like, stream, or comment on a track.",
        request_body=InteractionSerializer,
        responses={201: InteractionSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


# ----------------------------
# Listening History Endpoints
# ----------------------------
class ListeningHistoryViewSet(viewsets.ModelViewSet):
    """
    CRUD for ListeningHistory.
    """
    queryset = ListeningHistory.objects.all()
    serializer_class = ListeningHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]

    @swagger_auto_schema(
        tags=['Listening History'],
        operation_summary="List listening history",
        operation_description="Get the listening history for all users (admins) or self (user).",
        responses={200: ListeningHistorySerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Listening History'],
        operation_summary="Create listening history entry",
        operation_description="Log a user’s listening event for a track.",
        request_body=ListeningHistorySerializer,
        responses={201: ListeningHistorySerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


# ----------------------------
# Track Statistics Endpoints
# ----------------------------
class TrackStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only access for TrackStatistics.
    """
    queryset = TrackStatistics.objects.all()
    serializer_class = TrackStatisticsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]

    @swagger_auto_schema(
        tags=['Track Statistics'],
        operation_summary="List track statistics",
        operation_description="Returns play, like, and comment counts for all tracks.",
        responses={200: TrackStatisticsSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Track Statistics'],
        operation_summary="Retrieve track statistics",
        operation_description="Get statistics for a specific track by its statistic ID.",
        responses={200: TrackStatisticsSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


# ----------------------------
# Custom APIViews
# ----------------------------
class MyTracksView(APIView):
    """
    Artists can view all their own uploaded tracks (any status).
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Music Tracks'],
        operation_summary="List your uploaded tracks",
        operation_description="Returns all tracks uploaded by the authenticated artist, regardless of approval status.",
        responses={200: TrackSerializer(many=True)}
    )
    def get(self, request):
        user = request.user
        if user.role != 'artist':
            return Response({"error": "Only artists can access their uploaded tracks."}, status=403)
        tracks = Track.objects.filter(artist__user=user).order_by('-created_at')
        serializer = TrackSerializer(tracks, many=True)
        return Response(serializer.data)


class TracksByArtistView(APIView):
    """
    Moderators/Admins can view any artist’s tracks (all statuses).
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Music Tracks'],
        operation_summary="List tracks by artist",
        operation_description="Allows moderators or admins to retrieve all tracks for a given artist ID.",
        manual_parameters=[
            openapi.Parameter(
                'artist_id',
                openapi.IN_PATH,
                description="ID of the artist",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: TrackSerializer(many=True)}
    )
    def get(self, request, artist_id):
        user = request.user
        if user.role not in ['moderator', 'admin']:
            return Response({"error": "Access denied. Moderators only."}, status=403)

        tracks = Track.objects.filter(artist__id=artist_id).order_by('-created_at')
        serializer = TrackSerializer(tracks, many=True)
        return Response(serializer.data)