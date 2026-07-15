from database.db import db
from models.ai_analysis import AIAnalysis


def create_ai_analysis(interview_id):

    analysis = AIAnalysis(
        interview_id=interview_id,

        confidence_score=87,

        eye_contact_score=90,

        emotion="Confident",

        smile_score=82,

        speaking_speed=135,

        filler_words=4,

        voice_confidence=88,

        posture_score=91,

        overall_score=89
    )

    db.session.add(analysis)
    db.session.commit()

    return analysis


def get_ai_analysis(interview_id):

    return AIAnalysis.query.filter_by(
        interview_id=interview_id
    ).first()