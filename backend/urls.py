from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import AllowAny

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# ViewSets and Custom Views
from users.views import (
    UserViewSet,
    FollowViewSet,
    ArtistSignupView,
    ApproveOrRejectArtistView
)

from music.views import (
    ArtistViewSet,
    TrackViewSet,
    TrackFeatureViewSet,
    InteractionViewSet,
    ListeningHistoryViewSet,
    TrackStatisticsViewSet,
    MyTracksView,
    TracksByArtistView
)

from playlists.views import (
    PlaylistViewSet,
    PlaylistTrackViewSet,
    RecommendationViewSet
)

from subscriptions.views import (
    SubscriptionViewSet,
    SubscriptionPlanViewSet
)

# -----------------------
# DRF Router Registration
# -----------------------
router = DefaultRouter()

# Users
router.register(r'users', UserViewSet)
router.register(r'follows', FollowViewSet)

# Music
router.register(r'artists', ArtistViewSet)
router.register(r'tracks', TrackViewSet)
router.register(r'track-features', TrackFeatureViewSet)
router.register(r'interactions', InteractionViewSet)
router.register(r'listening-history', ListeningHistoryViewSet)
router.register(r'track-statistics', TrackStatisticsViewSet)

# Playlists
router.register(r'playlists', PlaylistViewSet)
router.register(r'playlist-tracks', PlaylistTrackViewSet)
router.register(r'recommendations', RecommendationViewSet)

# Subscriptions
router.register(r'subscriptions', SubscriptionViewSet)
router.register(r'subscription-plans', SubscriptionPlanViewSet)

# -----------------------
# Swagger Documentation
# -----------------------
schema_view = get_schema_view(
    openapi.Info(
        title="SoundScout API",
        default_version='v1',
        description="API documentation for SoundScout",
        terms_of_service="https://www.soundscout.com/terms/",
        contact=openapi.Contact(email="support@soundscout.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(AllowAny,),
)

# -----------------------
# URL Patterns
# -----------------------
urlpatterns = [
    path('admin/', admin.site.urls),

    # API Router
    path('api/v1/', include(router.urls)),

    # Custom User/Artist Endpoints
    path('api/v1/signup/artist/', ArtistSignupView.as_view(), name='artist-signup'),
    path('api/v1/my-tracks/', MyTracksView.as_view(), name='my-tracks'),
    path('api/v1/moderate/artist/<int:artist_id>/tracks/', TracksByArtistView.as_view(), name='artist-tracks-moderator'),
    path('api/v1/moderate/artist/<int:artist_id>/', ApproveOrRejectArtistView.as_view(), name='moderate-artist'),

    # API Docs
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^swagger\.json$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]