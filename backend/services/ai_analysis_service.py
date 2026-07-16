import random

from database.db import db
from models.ai_analysis import AIAnalysis
from models.interview import Interview


def create_ai_analysis(interview_id):

    interview = Interview.query.get(interview_id)

    if interview is None:
        return None

    analysis = AIAnalysis.query.filter_by(
        interview_id=interview_id
    ).first()

    confidence = random.randint(72, 96)
    eye_contact = random.randint(70, 98)
    smile = random.randint(65, 95)
    voice = random.randint(70, 96)
    posture = random.randint(72, 97)
    speaking_speed = random.randint(115, 155)
    filler_words = random.randint(1, 8)

    emotions = [
        "Confident",
        "Focused",
        "Neutral",
        "Happy"
    ]

    emotion = random.choice(emotions)

    overall = round(
        (
            confidence +
            eye_contact +
            smile +
            voice +
            posture
        ) / 5,
        1
    )

    if analysis:

        analysis.confidence_score = confidence
        analysis.eye_contact_score = eye_contact
        analysis.emotion = emotion
        analysis.smile_score = smile
        analysis.speaking_speed = speaking_speed
        analysis.filler_words = filler_words
        analysis.voice_confidence = voice
        analysis.posture_score = posture
        analysis.overall_score = overall

    else:

        analysis = AIAnalysis(
            interview_id=interview_id,
            confidence_score=confidence,
            eye_contact_score=eye_contact,
            emotion=emotion,
            smile_score=smile,
            speaking_speed=speaking_speed,
            filler_words=filler_words,
            voice_confidence=voice,
            posture_score=posture,
            overall_score=overall
        )

        db.session.add(analysis)

    db.session.commit()

    return analysis


def get_ai_analysis(interview_id):

    return AIAnalysis.query.filter_by(
        interview_id=interview_id
    ).first()