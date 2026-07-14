from database.db import db
from models.interview import Interview


def create_interview(user_id):

    interview = Interview(user_id=user_id)

    db.session.add(interview)
    db.session.commit()

    return interview


def get_all_interviews():

    return Interview.query.all()


def get_interview(interview_id):

    return Interview.query.get(interview_id)


def complete_interview(interview_id):

    interview = Interview.query.get(interview_id)

    if not interview:
        return None

    interview.status = "Completed"

    db.session.commit()

    return interview


def delete_interview(interview_id):

    interview = Interview.query.get(interview_id)

    if not interview:
        return False

    db.session.delete(interview)
    db.session.commit()

    return True