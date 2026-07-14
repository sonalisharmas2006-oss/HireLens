from database.db import db


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)

    interview_id = db.Column(
        db.Integer,
        db.ForeignKey("interviews.id"),
        nullable=False
    )

    confidence_score = db.Column(db.Integer)

    eye_contact = db.Column(db.String(50))

    emotion = db.Column(db.String(50))

    filler_words = db.Column(db.Integer)

    communication_score = db.Column(db.Integer)

    suggestions = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def to_dict(self):
        return {
            "id": self.id,
            "interview_id": self.interview_id,
            "confidence_score": self.confidence_score,
            "eye_contact": self.eye_contact,
            "emotion": self.emotion,
            "filler_words": self.filler_words,
            "communication_score": self.communication_score,
            "suggestions": self.suggestions,
            "created_at": str(self.created_at)
        }