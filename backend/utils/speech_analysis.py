"""
utils/speech_analysis.py

Speech-related analysis:
    A. Speech-to-text (via SpeechRecognition, with graceful failure handling)
    B. Speaking pace (words per minute)
    C. Pause analysis (when timing data is available)

This module never raises for expected failure modes (missing mic, unclear
audio, missing timing data, zero duration, etc). It always returns a
structured, safe-default dictionary instead.
"""

try:
    import speech_recognition as sr
    _SR_AVAILABLE = True
except ImportError:
    _SR_AVAILABLE = False

try:
    from config import (
        PAUSE_THRESHOLD_SECONDS,
        LONG_PAUSE_THRESHOLD_SECONDS,
    )
except ImportError:
    PAUSE_THRESHOLD_SECONDS = 0.6
    LONG_PAUSE_THRESHOLD_SECONDS = 2.0


# ------------------------------------------------------------------
# A. Speech-to-text
# ------------------------------------------------------------------

def transcribe_audio(audio_file_path, recognizer=None):
    """
    Convert an audio file to text using SpeechRecognition (Google Web Speech
    API backend by default). Designed to fail gracefully.

    Args:
        audio_file_path (str): Path to a .wav (or compatible) audio file.
        recognizer (sr.Recognizer, optional): Reuse an existing recognizer.

    Returns:
        dict: {
            "transcript": str,
            "success": bool,
            "error": str | None
        }
    """
    result = {"transcript": "", "success": False, "error": None}

    if not _SR_AVAILABLE:
        result["error"] = "SpeechRecognition library is not installed."
        return result

    if not audio_file_path:
        result["error"] = "No audio file path provided."
        return result

    recognizer = recognizer or sr.Recognizer()

    try:
        with sr.AudioFile(audio_file_path) as source:
            audio_data = recognizer.record(source)
    except FileNotFoundError:
        result["error"] = f"Audio file not found: {audio_file_path}"
        return result
    except Exception as e:
        result["error"] = f"Could not read audio file: {e}"
        return result

    try:
        transcript = recognizer.recognize_google(audio_data)
        result["transcript"] = transcript
        result["success"] = True
    except sr.UnknownValueError:
        result["error"] = "Speech was unintelligible; could not transcribe."
    except sr.RequestError as e:
        result["error"] = f"Speech recognition service error: {e}"
    except Exception as e:
        result["error"] = f"Unexpected transcription error: {e}"

    return result


# ------------------------------------------------------------------
# B. Speaking pace
# ------------------------------------------------------------------

def calculate_wpm(transcript, duration_seconds):
    """
    Calculate words per minute.

    Args:
        transcript (str): The spoken text.
        duration_seconds (float): Total speaking duration in seconds.

    Returns:
        dict: {
            "words_per_minute": float,
            "word_count": int
        }
    """
    if not transcript or not isinstance(transcript, str):
        return {"words_per_minute": 0, "word_count": 0}

    word_count = len(transcript.split())

    if not duration_seconds or duration_seconds <= 0:
        # Can't safely compute a rate without a valid duration
        return {"words_per_minute": 0, "word_count": word_count}

    minutes = duration_seconds / 60
    wpm = round(word_count / minutes, 2) if minutes > 0 else 0

    return {"words_per_minute": wpm, "word_count": word_count}


# ------------------------------------------------------------------
# C. Pause analysis
# ------------------------------------------------------------------

def analyze_pauses(word_timestamps=None):
    """
    Analyze pauses between spoken segments, if timing data is available.

    Args:
        word_timestamps (list[dict] | None): A list of segments like
            {"start": float, "end": float} representing spoken word/phrase
            timing in seconds, in chronological order. If None or too short
            to compute gaps, safe defaults are returned.

    Returns:
        dict: {
            "pause_count": int,
            "average_pause_duration": float,
            "long_pauses": int,
            "has_timing_data": bool
        }
    """
    safe_result = {
        "pause_count": 0,
        "average_pause_duration": 0,
        "long_pauses": 0,
        "has_timing_data": False
    }

    if not word_timestamps or len(word_timestamps) < 2:
        return safe_result

    pause_durations = []
    for prev_seg, next_seg in zip(word_timestamps, word_timestamps[1:]):
        try:
            gap = next_seg["start"] - prev_seg["end"]
        except (KeyError, TypeError):
            # Malformed timing entry; skip this pair rather than crash
            continue

        if gap >= PAUSE_THRESHOLD_SECONDS:
            pause_durations.append(gap)

    if not pause_durations:
        return {
            "pause_count": 0,
            "average_pause_duration": 0,
            "long_pauses": 0,
            "has_timing_data": True
        }

    long_pauses = sum(1 for g in pause_durations if g >= LONG_PAUSE_THRESHOLD_SECONDS)
    average_pause = round(sum(pause_durations) / len(pause_durations), 2)

    return {
        "pause_count": len(pause_durations),
        "average_pause_duration": average_pause,
        "long_pauses": long_pauses,
        "has_timing_data": True
    }