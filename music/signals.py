from django.db.models.signals import post_save
from django.dispatch import receiver
from music.models import Track, TrackFeature
from music.utils.feature_extraction import extract_features
import os

@receiver(post_save, sender=Track)
def extract_features_on_approval(sender, instance, created, **kwargs):
    # Only extract if track is approved and features don't already exist
    if instance.approval_status == 'approved':
        if not hasattr(instance, 'trackfeature'):  # Prevent duplicate insert
            file_path = instance.audio_url  # Assuming it's a local path
            if os.path.exists(file_path):
                features = extract_features(file_path)
                TrackFeature.objects.create(track=instance, **features)