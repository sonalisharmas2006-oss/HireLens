from database.db import db


class AIAnalysis(db.Model):
    __tablename__ = "ai_analysis"

    id = db.Column(db.Integer, primary_key=True)

    interview_id = db.Column(
        db.Integer,
        db.ForeignKey("interviews.id"),
        nullable=False,
        unique=True
    )

    confidence_score = db.Column(db.Float, default=0)

    eye_contact_score = db.Column(db.Float, default=0)

    emotion = db.Column(db.String(50), default="Unknown")

    smile_score = db.Column(db.Float, default=0)

    speaking_speed = db.Column(db.Float, default=0)

    filler_words = db.Column(db.Integer, default=0)

    voice_confidence = db.Column(db.Float, default=0)

    posture_score = db.Column(db.Float, default=0)

    overall_score = db.Column(db.Float, default=0)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def to_dict(self):
        return {
            "id": self.id,
            "interview_id": self.interview_id,
            "confidence_score": self.confidence_score,
            "eye_contact_score": self.eye_contact_score,
            "emotion": self.emotion,
            "smile_score": self.smile_score,
            "speaking_speed": self.speaking_speed,
            "filler_words": self.filler_words,
            "voice_confidence": self.voice_confidence,
            "posture_score": self.posture_score,
            "overall_score": self.overall_score,
            "created_at": str(self.created_at)
        }