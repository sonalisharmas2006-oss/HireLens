"""
services/ai_detection_service.py

Central service that orchestrates the AI/Detection utility modules
(speech-to-text, filler detection, pace/pause analysis, eye contact,
emotion) and produces a single structured result that the existing
report-generation code can consume.

This module contains NO Flask routes and NO database models. It's meant
to be called from interview_service.py / report_service.py or from a
route handler, e.g.:

    from services.ai_detection_service import AIDetectionService

    service = AIDetectionService()
    result = service.run_full_analysis(
        audio_file_path="uploads/interview_123.wav",
        duration_seconds=95,
        frames=captured_frames,          # list of OpenCV BGR frames
        word_timestamps=None,            # optional timing data
    )
"""

from utils.filler_detection import detect_fillers
from utils.speech_analysis import transcribe_audio, calculate_wpm, analyze_pauses
from utils.vision_analysis import estimate_eye_contact, analyze_emotion_sequence

try:
    from config import (
        CONFIDENCE_WEIGHTS,
        MIN_CONFIDENCE_SCORE,
        MAX_CONFIDENCE_SCORE,
        WPM_IDEAL_MIN,
        WPM_IDEAL_MAX,
        WPM_TOO_SLOW,
        WPM_TOO_FAST,
    )
except ImportError:
    CONFIDENCE_WEIGHTS = {
        "eye_contact": 0.3,
        "filler_words": 0.2,
        "emotion": 0.2,
        "pace": 0.2,
        "speech_clarity": 0.1,
    }
    MIN_CONFIDENCE_SCORE = 0
    MAX_CONFIDENCE_SCORE = 100
    WPM_TOO_SLOW = 100
    WPM_IDEAL_MIN = 120
    WPM_IDEAL_MAX = 160
    WPM_TOO_FAST = 180


class AIDetectionService:
    """
    Central coordinator for the AI/Detection features. Keeps orchestration
    logic separate from raw signal-processing logic (which lives in utils/).
    """

    # ----------------------------------------------------------------
    # Individual analysis steps
    # ----------------------------------------------------------------

    def transcribe(self, audio_file_path):
        """Speech-to-text. Returns the transcribe_audio() result dict."""
        return transcribe_audio(audio_file_path)

    def analyze_fillers(self, transcript):
        """Filler-word analysis. Returns the detect_fillers() result dict."""
        return detect_fillers(transcript)

    def analyze_pace(self, transcript, duration_seconds):
        """Speaking pace analysis (words per minute)."""
        return calculate_wpm(transcript, duration_seconds)

    def analyze_pauses(self, word_timestamps=None):
        """Pause analysis, if timing data is available."""
        return analyze_pauses(word_timestamps)

    def analyze_eye_contact(self, frames):
        """Eye-contact estimation across a sequence of frames."""
        return estimate_eye_contact(frames)

    def analyze_emotion(self, frames, model=None):
        """Emotion analysis across a sequence of frames."""
        return analyze_emotion_sequence(frames, model=model)

    # ----------------------------------------------------------------
    # Confidence scoring
    # ----------------------------------------------------------------

    def _score_eye_contact(self, eye_contact_result):
        # eye_contact percentage is already 0-100
        return max(MIN_CONFIDENCE_SCORE, min(MAX_CONFIDENCE_SCORE, eye_contact_result.get("percentage", 0)))

    def _score_filler_words(self, filler_result, word_count):
        """Fewer fillers relative to total words -> higher score."""
        if not word_count:
            return 50  # neutral default when we can't compute a rate

        rate = filler_result.get("rate")
        if rate is None:
            return 50

        # 0% filler rate -> 100 score; 20%+ filler rate -> 0 score
        score = 100 - (rate * 5)
        return max(MIN_CONFIDENCE_SCORE, min(MAX_CONFIDENCE_SCORE, round(score, 2)))

    def _score_emotion(self, emotion_result):
        """
        Simple heuristic: positive/neutral-leaning emotions score higher.
        This is intentionally transparent and easy to adjust.
        """
        positive_weight = {
            "happy": 100,
            "neutral": 80,
            "surprised": 65,
            "sad": 40,
            "fear": 35,
            "angry": 30,
        }
        distribution = emotion_result.get("distribution", {})
        if not distribution:
            return 50

        weighted_score = sum(
            distribution.get(label, 0) * positive_weight.get(label, 50)
            for label in distribution
        )
        return max(MIN_CONFIDENCE_SCORE, min(MAX_CONFIDENCE_SCORE, round(weighted_score, 2)))

    def _score_pace(self, pace_result):
        """Score is highest inside the ideal WPM band, tapering outside it."""
        wpm = pace_result.get("words_per_minute", 0)
        if not wpm:
            return 50  # neutral default when pace can't be computed

        if WPM_IDEAL_MIN <= wpm <= WPM_IDEAL_MAX:
            return 100
        if wpm <= WPM_TOO_SLOW or wpm >= WPM_TOO_FAST:
            return 30
        # Linear taper between "too slow/fast" bounds and the ideal band
        if wpm < WPM_IDEAL_MIN:
            span = WPM_IDEAL_MIN - WPM_TOO_SLOW or 1
            return round(30 + ((wpm - WPM_TOO_SLOW) / span) * 70, 2)
        span = WPM_TOO_FAST - WPM_IDEAL_MAX or 1
        return round(100 - ((wpm - WPM_IDEAL_MAX) / span) * 70, 2)

    def _score_speech_clarity(self, transcription_result):
        """
        Basic proxy for clarity: did speech-to-text succeed at all?
        Real clarity scoring could be extended later (e.g. confidence
        scores from a richer STT engine).
        """
        return 85 if transcription_result.get("success") else 40

    def calculate_confidence(self, eye_contact_result, filler_result, emotion_result,
                              pace_result, transcription_result, word_count=0):
        """
        Combine component scores using CONFIDENCE_WEIGHTS into a single
        0-100 confidence score.

        Returns:
            dict: {
                "score": float,
                "breakdown": {component: score, ...}
            }
        """
        breakdown = {
            "eye_contact": self._score_eye_contact(eye_contact_result),
            "filler_words": self._score_filler_words(filler_result, word_count),
            "emotion": self._score_emotion(emotion_result),
            "pace": self._score_pace(pace_result),
            "speech_clarity": self._score_speech_clarity(transcription_result),
        }

        total = sum(breakdown[key] * CONFIDENCE_WEIGHTS.get(key, 0) for key in breakdown)
        total = max(MIN_CONFIDENCE_SCORE, min(MAX_CONFIDENCE_SCORE, round(total, 2)))

        return {"score": total, "breakdown": breakdown}

    # ----------------------------------------------------------------
    # Full pipeline
    # ----------------------------------------------------------------

    def run_full_analysis(self, audio_file_path=None, transcript=None,
                           duration_seconds=0, frames=None, word_timestamps=None,
                           emotion_model=None):
        """
        Run the complete AI/Detection pipeline and return a structured
        result dictionary ready to be handed to report_service.py.

        Either `audio_file_path` (to transcribe) or a pre-computed
        `transcript` can be supplied. If both are missing, transcript-based
        analyses safely fall back to empty defaults instead of failing.

        Args:
            audio_file_path (str|None): path to interview audio.
            transcript (str|None): pre-transcribed text, if already available.
            duration_seconds (float): total speaking duration.
            frames (list|None): list of OpenCV BGR frames captured during interview.
            word_timestamps (list|None): optional per-word/segment timing data.
            emotion_model (object|None): optional real emotion-classification model.

        Returns:
            dict: structured result, see module docstring / spec for shape.
        """
        frames = frames or []

        # 1. Speech-to-text (only if transcript wasn't already provided)
        transcription_result = {"transcript": transcript or "", "success": bool(transcript), "error": None}
        if not transcript and audio_file_path:
            transcription_result = self.transcribe(audio_file_path)

        final_transcript = transcription_result.get("transcript", "") or ""

        # 2. Filler word analysis
        filler_result = self.analyze_fillers(final_transcript)

        # 3. Speaking pace
        pace_result = self.analyze_pace(final_transcript, duration_seconds)

        # 4. Pause analysis
        pause_result = self.analyze_pauses(word_timestamps)

        # 5. Eye contact
        eye_contact_result = self.analyze_eye_contact(frames)

        # 6. Emotion
        emotion_result = self.analyze_emotion(frames, model=emotion_model)

        # 7. Confidence score
        confidence_result = self.calculate_confidence(
            eye_contact_result=eye_contact_result,
            filler_result=filler_result,
            emotion_result=emotion_result,
            pace_result=pace_result,
            transcription_result=transcription_result,
            word_count=pace_result.get("word_count", 0),
        )

        return {
            "transcript": final_transcript,
            "filler_words": {
                "count": filler_result.get("count", 0),
                "words": filler_result.get("words", []),
                "frequency": filler_result.get("frequency", {}),
            },
            "speech": {
                "words_per_minute": pace_result.get("words_per_minute", 0),
                "pause_count": pause_result.get("pause_count", 0),
                "average_pause_duration": pause_result.get("average_pause_duration", 0),
            },
            "eye_contact": {
                "score": eye_contact_result.get("score", 0),
                "percentage": eye_contact_result.get("percentage", 0),
            },
            "emotion": {
                "dominant": emotion_result.get("dominant", "neutral"),
                "distribution": emotion_result.get("distribution", {}),
            },
            "confidence": {
                "score": confidence_result.get("score", 0),
                "breakdown": confidence_result.get("breakdown", {}),
            },
        }