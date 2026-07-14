from database.db import db
from models.report import Report


def generate_report(interview_id):

    report = Report(
        interview_id=interview_id,
        confidence_score=87,
        eye_contact="Good",
        emotion="Confident",
        filler_words=5,
        communication_score=90,
        suggestions="""
• Maintain eye contact throughout the interview.
• Reduce filler words like 'um' and 'uh'.
• Speak slightly slower for better clarity.
• Keep a confident posture.
"""
    )

    db.session.add(report)
    db.session.commit()

    return report


def get_report(interview_id):

    return Report.query.filter_by(
        interview_id=interview_id
    ).first()