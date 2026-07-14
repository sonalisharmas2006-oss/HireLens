from database.db import db
from models.interview import Interview


def create_interview(user_id):

    interview = Interview(
        user_id=user_id
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

    if not interview:
        return None

    interview.video_path = video_path

    db.session.commit()

    return interview