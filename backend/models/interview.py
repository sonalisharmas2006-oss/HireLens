from database.db import db


class Interview(db.Model):
    __tablename__ = "interviews"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    title = db.Column(
        db.String(100),
        default="Mock Interview"
    )

    company = db.Column(
        db.String(100),
        default="General"
    )

    role = db.Column(
        db.String(100),
        default="Software Engineer"
    )

    duration = db.Column(
        db.Integer,
        default=0
    )

    interview_type = db.Column(
        db.String(50),
        default="Technical"
    )

    status = db.Column(
        db.String(30),
        default="Started"
    )

    video_path = db.Column(db.String(255))

    audio_path = db.Column(db.String(255))

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "company": self.company,
            "role": self.role,
            "duration": self.duration,
            "interview_type": self.interview_type,
            "status": self.status,
            "video_path": self.video_path,
            "audio_path": self.audio_path,
            "created_at": str(self.created_at)
        }