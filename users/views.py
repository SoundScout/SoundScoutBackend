from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend

from django.contrib.auth import authenticate

from users.models import User, Follow, Artist
from subscriptions.models import Subscription, SubscriptionPlan
from users.utils import assign_group

from users.serializers import (
    UserSerializer,
    FollowSerializer,
    ArtistSerializer,
    ListenerRegisterSerializer,
    ArtistRegisterSerializer,
    LoginSerializer
)

import logging
logger = logging.getLogger('users')


# ----------------------------
# User CRUD (Used by admin / profile screen)
# ----------------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]


# ----------------------------
# Follow/Unfollow Users
# ----------------------------
class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]


# ----------------------------
# Listener Registration
# ----------------------------
class ListenerRegisterView(generics.CreateAPIView):
    serializer_class = ListenerRegisterSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]


# ----------------------------
# Artist Registration (listener role + artist profile = pending)
# ----------------------------
class ArtistRegisterView(generics.CreateAPIView):
    serializer_class = ArtistRegisterSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]


# ----------------------------
# Login View for All Users
# ----------------------------
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "role": user.role,
            "user_id": user.id,
            "email": user.email,
        })


# ----------------------------
# View All Artists (moderator/admin only)
# ----------------------------
class ArtistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]


# ----------------------------
# Approve or Reject Artist (moderator/admin only)
# ----------------------------
class ApproveOrRejectArtistView(APIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]

    def post(self, request, artist_id):
        user = request.user

        if user.role not in ['moderator', 'admin']:
            raise PermissionDenied("Only moderators or admins can perform this action.")

        artist = get_object_or_404(Artist, id=artist_id)
        action = request.data.get('action')  # "approve" or "reject"
        rejection_reason = request.data.get('rejection_reason', '')

        if action == 'approve':
            artist.status = 'approved'
            artist.user.role = 'artist'
            artist.user.save()
            assign_group(artist.user)               # ← ensure user is moved into the Artist group
            artist.save()

            logger.info(f"Artist '{artist.display_name}' (User: {artist.user.email}) approved by {user.email}")

            if not hasattr(artist, 'subscription'):
                free_plan = SubscriptionPlan.objects.filter(name='Free').first()
                if free_plan:
                    Subscription.objects.create(
                        artist=artist,
                        plan=free_plan,
                        status='active'
                    )
                    logger.info(f"🆕 Free subscription created for artist '{artist.display_name}'")
                else:
                    logger.warning(f"⚠️ Free subscription plan not found for '{artist.display_name}'")

            return Response({"message": "Artist approved and Free subscription created."})

        elif action == 'reject':
            if not rejection_reason:
                return Response({"error": "Rejection reason is required."}, status=400)

            artist.status = 'rejected'
            artist.rejection_reason = rejection_reason
            artist.save()

            logger.info(
                f"Artist '{artist.display_name}' (User: {artist.user.email}) rejected by {user.email}. "
                f"Reason: {rejection_reason}"
            )
            return Response({"message": "Artist rejected."})

        return Response({"error": "Invalid action. Use 'approve' or 'reject'."}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def LogoutView(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()  # ✅ Add token to blacklist table
        return Response({"message": "Logged out successfully."}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=400)