import os
from celery import shared_task
from music.models import Track, TrackFeature
from music.utils.feature_extraction import extract_features

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def extract_features_task(self, track_id):
    """
    Celery task to extract and save TrackFeature for the given track.
    Retries on failure up to 3 times.
    """
    try:
        track = Track.objects.get(id=track_id)
        file_path = track.audio_file.path

        if not os.path.exists(file_path):
            # Nothing to do if file missing
            return

        features = extract_features(file_path)
        TrackFeature.objects.create(track=track, **features)
    except Exception as exc:
        # Retry on unexpected errors
        raise self.retry(exc=exc)