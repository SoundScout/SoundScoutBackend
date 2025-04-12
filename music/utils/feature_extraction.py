import librosa
import numpy as np
from music.models import Track, TrackFeature

def extract_features(file_path):
    y, sr = librosa.load(file_path, sr=None)

    # Tempo (BPM)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    # Energy (RMS)
    energy = np.mean(librosa.feature.rms(y=y))

    # Zero-crossing rate
    zcr = np.mean(librosa.feature.zero_crossing_rate(y))

    # Spectral centroid (brightness)
    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))

    # Spectral rolloff (acousticness)
    spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))

    # Chroma STFT
    chroma_stft = np.mean(librosa.feature.chroma_stft(y=y, sr=sr))

    # MFCCs (summary)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_mean = np.mean(mfcc)

    # Heuristic logic
    danceability = min(1.0, tempo / 250.0)
    speechiness = zcr
    instrumentalness = max(0.0, 1.0 - chroma_stft)
    acousticness = max(0.0, 1.0 - spectral_rolloff / sr)
    liveness = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)) / sr
    valence = spectral_centroid / sr

    # Mood classification
    if valence > 0.6 and tempo > 110:
        mood = "happy"
    elif valence < 0.4 and tempo < 90 and energy < 0.2:
        mood = "sad"
    elif energy > 0.25 and tempo > 120:
        mood = "energetic"
    elif acousticness > 0.5 and tempo < 100:
        mood = "calm"
    elif 0.4 < valence < 0.65 and acousticness > 0.3 and tempo < 100:
        mood = "romantic"
    elif energy > 0.4 and speechiness > 0.15:
        mood = "angry"
    else:
        mood = "chill"

    return {
        "tempo": float(tempo),
        "energy": float(energy),
        "danceability": float(danceability),
        "valence": float(valence),
        "speechiness": float(speechiness),
        "instrumentalness": float(instrumentalness),
        "acousticness": float(acousticness),
        "liveness": float(liveness),
        "mood": mood,
    }

# === MANUAL TESTING BLOCK ===

# Change this to your track ID