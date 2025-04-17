# playlists/urls.py

from rest_framework.routers import DefaultRouter
from .views import PlaylistViewSet, PlaylistTrackViewSet, RecommendationViewSet

router = DefaultRouter()
router.register(r'playlists',        PlaylistViewSet,      basename='playlist')
router.register(r'playlist-tracks',  PlaylistTrackViewSet, basename='playlisttrack')
router.register(r'recommendations',  RecommendationViewSet, basename='recommendation')

urlpatterns = router.urls