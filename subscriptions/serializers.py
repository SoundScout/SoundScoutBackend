from rest_framework import serializers
from subscriptions.models import Subscription, SubscriptionPlan


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'max_upload_rate', 'price']


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)  # Nested plan info (read-only)
    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=SubscriptionPlan.objects.all(), write_only=True, source='plan'
    )

    class Meta:
        model = Subscription
        fields = [
            'id', 'artist', 'plan', 'plan_id',
            'max_upload_rate', 'price',
            'status', 'is_active',
            'end_subscription', 'created_at'
        ]
        read_only_fields = ['max_upload_rate', 'price', 'is_active', 'created_at']