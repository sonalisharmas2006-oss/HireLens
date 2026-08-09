"""
utils/vision_analysis.py

Computer-vision side of the AI detection pipeline:
    A. Face detection
    B. Eye/iris position analysis
    C. Eye-contact estimation
    D. Emotion analysis interface (safe baseline / fallback)

Notes:
- OpenCV + MediaPipe give us reliable face/landmark geometry, but they do
  NOT by themselves provide accurate 6-class emotion recognition. The
  emotion function below defines a clean interface plus a neutral-leaning
  heuristic fallback, so it can later be swapped for a real trained model
  (e.g. an ONNX/Keras classifier) without changing the calling code.
- Nothing here downloads models or hardcodes external URLs.
- Every function degrades gracefully (missing camera, no face found,
  mediapipe/opencv not installed, etc).
"""

try:
    import cv2
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False

try:
    import mediapipe as mp
    _MEDIAPIPE_AVAILABLE = True
except ImportError:
    _MEDIAPIPE_AVAILABLE = False

try:
    from config import EYE_CONTACT_OFFSET_THRESHOLD, EMOTION_LABELS, DEFAULT_EMOTION
except ImportError:
    EYE_CONTACT_OFFSET_THRESHOLD = 0.15
    EMOTION_LABELS = ["happy", "neutral", "sad", "angry", "surprised", "fear"]
    DEFAULT_EMOTION = "neutral"


# ------------------------------------------------------------------
# Shared MediaPipe setup (lazy-initialized, safe if unavailable)
# ------------------------------------------------------------------

_face_mesh = None


def _get_face_mesh():
    global _face_mesh
    if not _MEDIAPIPE_AVAILABLE:
        return None
    if _face_mesh is None:
        try:
            _face_mesh = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
        except Exception:
            _face_mesh = None
    return _face_mesh


# ------------------------------------------------------------------
# A. Face detection
# ------------------------------------------------------------------

def detect_face(frame):
    """
    Detect whether a face is present in the given frame and return its
    landmark set (if MediaPipe is available).

    Args:
        frame: a BGR image (numpy array) as returned by OpenCV, or None.

    Returns:
        dict: {
            "face_found": bool,
            "landmarks": mediapipe landmark list | None,
            "error": str | None
        }
    """
    result = {"face_found": False, "landmarks": None, "error": None}

    if frame is None:
        result["error"] = "No frame provided."
        return result

    if not _CV2_AVAILABLE or not _MEDIAPIPE_AVAILABLE:
        result["error"] = "OpenCV/MediaPipe not available in this environment."
        return result

    face_mesh = _get_face_mesh()
    if face_mesh is None:
        result["error"] = "Face mesh model could not be initialized."
        return result

    try:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        processed = face_mesh.process(rgb_frame)
    except Exception as e:
        result["error"] = f"Frame processing failed: {e}"
        return result

    if not processed.multi_face_landmarks:
        result["error"] = "No face detected in frame."
        return result

    result["face_found"] = True
    result["landmarks"] = processed.multi_face_landmarks[0]
    return result


# ------------------------------------------------------------------
# B & C. Eye position + eye-contact estimation
# ------------------------------------------------------------------

# Approximate MediaPipe FaceMesh iris/eye landmark indices
_LEFT_IRIS = [468, 469, 470, 471]
_RIGHT_IRIS = [473, 474, 475, 476]
_LEFT_EYE_CORNERS = (33, 133)
_RIGHT_EYE_CORNERS = (362, 263)


def _landmark_xy(landmarks, index):
    point = landmarks.landmark[index]
    return point.x, point.y


def estimate_eye_position(landmarks):
    """
    Estimate normalized iris offset from eye center for both eyes.

    Args:
        landmarks: MediaPipe face landmark object (from detect_face).

    Returns:
        dict: {
            "available": bool,
            "left_offset": float | None,
            "right_offset": float | None,
            "error": str | None
        }
    """
    result = {"available": False, "left_offset": None, "right_offset": None, "error": None}

    if landmarks is None:
        result["error"] = "No landmarks provided."
        return result

    try:
        left_iris_pts = [_landmark_xy(landmarks, i) for i in _LEFT_IRIS]
        right_iris_pts = [_landmark_xy(landmarks, i) for i in _RIGHT_IRIS]

        left_corner_a = _landmark_xy(landmarks, _LEFT_EYE_CORNERS[0])
        left_corner_b = _landmark_xy(landmarks, _LEFT_EYE_CORNERS[1])
        right_corner_a = _landmark_xy(landmarks, _RIGHT_EYE_CORNERS[0])
        right_corner_b = _landmark_xy(landmarks, _RIGHT_EYE_CORNERS[1])

        left_iris_center_x = sum(p[0] for p in left_iris_pts) / len(left_iris_pts)
        right_iris_center_x = sum(p[0] for p in right_iris_pts) / len(right_iris_pts)

        left_eye_center_x = (left_corner_a[0] + left_corner_b[0]) / 2
        right_eye_center_x = (right_corner_a[0] + right_corner_b[0]) / 2

        left_eye_width = abs(left_corner_b[0] - left_corner_a[0]) or 1e-6
        right_eye_width = abs(right_corner_b[0] - right_corner_a[0]) or 1e-6

        left_offset = abs(left_iris_center_x - left_eye_center_x) / left_eye_width
        right_offset = abs(right_iris_center_x - right_eye_center_x) / right_eye_width

    except (IndexError, AttributeError, ZeroDivisionError) as e:
        result["error"] = f"Could not compute eye offsets: {e}"
        return result

    result["available"] = True
    result["left_offset"] = round(left_offset, 4)
    result["right_offset"] = round(right_offset, 4)
    return result


def estimate_eye_contact(frames):
    """
    Estimate an overall eye-contact score across a sequence of frames.

    Args:
        frames (list): list of BGR numpy-array frames. May be empty.

    Returns:
        dict: {
            "score": float,        # 0-100 usable score
            "percentage": float,   # % of analyzed frames counted as eye contact
            "frames_analyzed": int,
            "frames_with_face": int
        }
    """
    safe_result = {
        "score": 0,
        "percentage": 0,
        "frames_analyzed": 0,
        "frames_with_face": 0
    }

    if not frames:
        return safe_result

    frames_with_face = 0
    frames_with_contact = 0

    for frame in frames:
        face_result = detect_face(frame)
        if not face_result["face_found"]:
            continue

        frames_with_face += 1
        eye_result = estimate_eye_position(face_result["landmarks"])
        if not eye_result["available"]:
            continue

        avg_offset = (eye_result["left_offset"] + eye_result["right_offset"]) / 2
        if avg_offset <= EYE_CONTACT_OFFSET_THRESHOLD:
            frames_with_contact += 1

    total_frames = len(frames)
    percentage = round((frames_with_contact / frames_with_face) * 100, 2) if frames_with_face else 0

    return {
        "score": percentage,  # score and percentage are equivalent here, 0-100
        "percentage": percentage,
        "frames_analyzed": total_frames,
        "frames_with_face": frames_with_face
    }


# ------------------------------------------------------------------
# D. Emotion analysis (interface + safe fallback)
# ------------------------------------------------------------------

def analyze_emotion(frame, model=None):
    """
    Analyze emotion for a single frame.

    This function defines the stable interface the rest of the app should
    call. If a real trained emotion-classification model is later added to
    the project, pass it in via `model` (any object exposing a
    `.predict(frame_or_face_crop)` method returning a label from
    EMOTION_LABELS). Until then, this returns a safe neutral-leaning
    baseline rather than fabricating an unreliable classification purely
    from OpenCV/MediaPipe geometry.

    Args:
        frame: BGR numpy-array frame.
        model: optional external emotion-classification model.

    Returns:
        dict: {
            "dominant": str,             # one of EMOTION_LABELS
            "distribution": dict,        # label -> probability (sums to 1)
            "model_used": bool,          # True if a real model produced this
            "error": str | None
        }
    """
    baseline_distribution = {label: 0.0 for label in EMOTION_LABELS}
    baseline_distribution[DEFAULT_EMOTION] = 1.0

    result = {
        "dominant": DEFAULT_EMOTION,
        "distribution": baseline_distribution,
        "model_used": False,
        "error": None
    }

    if frame is None:
        result["error"] = "No frame provided."
        return result

    face_result = detect_face(frame)
    if not face_result["face_found"]:
        result["error"] = face_result["error"] or "No face detected."
        return result

    if model is None:
        # No real emotion model plugged in yet -- return the safe baseline.
        return result

    try:
        prediction = model.predict(frame)
        if isinstance(prediction, dict):
            # Assume prediction is already a {label: probability} distribution
            distribution = {label: float(prediction.get(label, 0.0)) for label in EMOTION_LABELS}
            dominant = max(distribution, key=distribution.get)
            return {
                "dominant": dominant,
                "distribution": distribution,
                "model_used": True,
                "error": None
            }
        elif isinstance(prediction, str) and prediction in EMOTION_LABELS:
            distribution = {label: (1.0 if label == prediction else 0.0) for label in EMOTION_LABELS}
            return {
                "dominant": prediction,
                "distribution": distribution,
                "model_used": True,
                "error": None
            }
        else:
            result["error"] = "Model returned an unrecognized prediction format."
            return result
    except Exception as e:
        result["error"] = f"Emotion model inference failed: {e}"
        return result


def analyze_emotion_sequence(frames, model=None):
    """
    Run analyze_emotion across multiple frames and summarize the dominant
    emotion distribution over the whole sequence.

    Args:
        frames (list): list of BGR frames.
        model: optional external emotion-classification model.

    Returns:
        dict: {
            "dominant": str,
            "distribution": dict,   # normalized average distribution
            "frames_analyzed": int
        }
    """
    if not frames:
        baseline = {label: 0.0 for label in EMOTION_LABELS}
        baseline[DEFAULT_EMOTION] = 1.0
        return {"dominant": DEFAULT_EMOTION, "distribution": baseline, "frames_analyzed": 0}

    totals = {label: 0.0 for label in EMOTION_LABELS}
    analyzed = 0

    for frame in frames:
        single = analyze_emotion(frame, model=model)
        analyzed += 1
        for label in EMOTION_LABELS:
            totals[label] += single["distribution"].get(label, 0.0)

    distribution = {label: round(total / analyzed, 4) for label, total in totals.items()}
    dominant = max(distribution, key=distribution.get)

    return {"dominant": dominant, "distribution": distribution, "frames_analyzed": analyzed}