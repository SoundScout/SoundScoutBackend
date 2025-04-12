from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from subscriptions.models import Subscription, SubscriptionPlan
from subscriptions.serializers import SubscriptionSerializer, SubscriptionPlanSerializer

class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [AllowAny]

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'artist'):
            return Subscription.objects.filter(artist=user.artist)
        return Subscription.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if not hasattr(user, 'artist'):
            raise PermissionDenied("Only approved artists can create subscriptions.")

        if Subscription.objects.filter(artist=user.artist).exists():
            raise PermissionDenied("You already have a subscription.")

        serializer.save(artist=user.artist)