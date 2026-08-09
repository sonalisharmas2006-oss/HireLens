import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


# ============================================================
# FLASK / DATABASE CONFIGURATION
# ============================================================

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "hirelens-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "hirelens-jwt-secret")

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + os.path.join(BASE_DIR, "database", "database.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

    MAX_CONTENT_LENGTH = 500 * 1024 * 1024


# ============================================================
# AI / DETECTION CONFIGURATION
# ============================================================

# Hardware / capture
WEBCAM_INDEX = 0
AUDIO_SAMPLE_RATE = 16000


# ============================================================
# FILLER WORD DETECTION
# ============================================================

FILLER_WORDS = [
    "um",
    "uh",
    "like",
    "you know",
    "actually",
    "basically",
]


# ============================================================
# EMOTION DETECTION
# ============================================================

EMOTION_LABELS = [
    "happy",
    "neutral",
    "sad",
    "angry",
    "surprised",
    "fear",
]

DEFAULT_EMOTION = "neutral"


# ============================================================
# SPEAKING PACE
# ============================================================

WPM_TOO_SLOW = 100
WPM_IDEAL_MIN = 120
WPM_IDEAL_MAX = 160
WPM_TOO_FAST = 180


# ============================================================
# PAUSE ANALYSIS
# ============================================================

PAUSE_THRESHOLD_SECONDS = 0.6
LONG_PAUSE_THRESHOLD_SECONDS = 2.0


# ============================================================
# EYE CONTACT
# ============================================================

EYE_CONTACT_OFFSET_THRESHOLD = 0.15


# ============================================================
# CONFIDENCE SCORE
# ============================================================

CONFIDENCE_WEIGHTS = {
    "eye_contact": 0.3,
    "filler_words": 0.2,
    "emotion": 0.2,
    "pace": 0.2,
    "speech_clarity": 0.1,
}

MIN_CONFIDENCE_SCORE = 0
MAX_CONFIDENCE_SCORE = 100