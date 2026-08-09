"""
utils/filler_detection.py

Detects filler words/phrases in a transcript.

Handles:
- case-insensitive matching
- multi-word fillers (e.g. "you know")
- avoiding partial-word false positives (e.g. "like" inside "likely")
"""

import re

try:
    from config import FILLER_WORDS
except ImportError:
    # Safe fallback if config isn't importable in isolation
    FILLER_WORDS = ["um", "uh", "like", "you know", "actually", "basically"]


def _build_pattern(filler_words):
    """
    Builds a single regex that matches any configured filler word/phrase
    as a whole word/phrase (word-boundary safe), case-insensitive.

    Multi-word fillers (e.g. "you know") are treated as literal phrases.
    Longer phrases are sorted first so they take priority over shorter
    fillers that might be a substring (not strictly needed here, but safe).
    """
    escaped = [re.escape(word) for word in sorted(filler_words, key=len, reverse=True)]
    pattern = r"\b(" + "|".join(escaped) + r")\b"
    return re.compile(pattern, re.IGNORECASE)


_FILLER_PATTERN = _build_pattern(FILLER_WORDS)


def detect_fillers(transcript, filler_words=None):
    """
    Detect filler words in the given transcript text.

    Args:
        transcript (str): The transcribed speech text.
        filler_words (list[str], optional): Override the configured filler
            word list. Defaults to config.FILLER_WORDS.

    Returns:
        dict: {
            "count": int,
            "words": [str, ...],        # every filler occurrence, in order
            "frequency": {word: count}, # per-filler occurrence counts
            "rate": float | None        # fillers per 100 words, if computable
        }
    """
    safe_result = {
        "count": 0,
        "words": [],
        "frequency": {},
        "rate": None
    }

    if not transcript or not isinstance(transcript, str) or not transcript.strip():
        return safe_result

    pattern = _build_pattern(filler_words) if filler_words else _FILLER_PATTERN

    matches = pattern.findall(transcript)
    normalized_matches = [m.lower() for m in matches]

    frequency = {}
    for word in normalized_matches:
        frequency[word] = frequency.get(word, 0) + 1

    total_words = len(transcript.split())
    rate = None
    if total_words > 0:
        rate = round((len(normalized_matches) / total_words) * 100, 2)

    return {
        "count": len(normalized_matches),
        "words": normalized_matches,
        "frequency": frequency,
        "rate": rate
    }