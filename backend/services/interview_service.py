from database.db import db
from models.interview import Interview


def create_interview(
    user_id,
    title="Mock Interview",
    company="General",
    role="Software Engineer",
    interview_type="Technical"
):

    interview = Interview(
        user_id=user_id,
        title=title,
        company=company,
        role=role,
        interview_type=interview_type,
        status="Created"
    )

    db.session.add(interview)
    db.session.commit()

    return interview


def get_all_interviews():
    return Interview.query.all()


def get_interview(interview_id):
    return Interview.query.get(interview_id)


def update_video(interview_id, video_path):

    interview = Interview.query.get(interview_id)

    if interview is None:
        return None

    interview.video_path = video_path
    interview.status = "Video Uploaded"

    db.session.commit()

    return interview


def update_status(interview_id, status):

    interview = Interview.query.get(interview_id)

    if interview is None:
        return None

    interview.status = status

    db.session.commit()

    return interview