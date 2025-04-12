from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from users.models import User, Follow, Artist
from subscriptions.models import Subscription, SubscriptionPlan

from users.serializers import (
    UserSerializer,
    FollowSerializer,
    ArtistSerializer,
    ArtistSignupSerializer
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


# ----------------------------
# Follow/Unfollow Users
# ----------------------------
class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]


# ----------------------------
# Artist Signup (creates User + Artist profile with status = pending)
# ----------------------------
class ArtistSignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = ArtistSignupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Artist signup successful. Awaiting approval.",
                "user_id": user.id,
                "role": user.role,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------------------
# View All Artists (for moderators/admins only)
# ----------------------------
class ArtistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [IsAuthenticated]


# ----------------------------
# Approve or Reject Artist (by moderators/admins)
# ----------------------------
class ApproveOrRejectArtistView(APIView):
    permission_classes = [IsAuthenticated]

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
            artist.save()

            # Log approval
            logger.info(f" Artist '{artist.display_name}' (User: {artist.user.email}) approved by {user.email}")

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
                    logger.warning(f"⚠️ Free subscription plan not found during approval of artist '{artist.display_name}'")

            return Response({"message": "Artist approved and Free subscription created."})

        elif action == 'reject':
            if not rejection_reason:
                return Response({"error": "Rejection reason is required."}, status=400)

            artist.status = 'rejected'
            artist.rejection_reason = rejection_reason
            artist.save()

            # Log rejection
            logger.info(f" Artist '{artist.display_name}' (User: {artist.user.email}) rejected by {user.email}. Reason: {rejection_reason}")

            return Response({"message": "Artist rejected."})

        return Response({"error": "Invalid action. Use 'approve' or 'reject'."}, status=400)