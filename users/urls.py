from django.urls import path
from users.views import (
    ListenerRegisterView,
    ArtistRegisterView,
    LoginView,
    ApproveOrRejectArtistView,
    ArtistViewSet,
)
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet, FollowViewSet
from django.urls import path
from users.views import LogoutView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'follows', FollowViewSet)
router.register(r'artists', ArtistViewSet, basename='artist-profiles')  # ArtistViewSet from users

urlpatterns = [
    path('register/listener/', ListenerRegisterView.as_view(), name='register-listener'),
    path('register/artist/', ArtistRegisterView.as_view(), name='register-artist'),
    path('login/', LoginView.as_view(), name='login'),
    path('moderate/artist/<int:artist_id>/', ApproveOrRejectArtistView.as_view(), name='moderate-artist'),
    path('logout/', LogoutView, name='logout'),
]

urlpatterns += router.urls