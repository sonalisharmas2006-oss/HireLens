from database.db import db
from sqlalchemy import func

from models.user import User
from models.interview import Interview
from models.report import Report
from models.ai_analysis import AIAnalysis


def get_dashboard_stats():

    total_users = User.query.count()

    total_interviews = Interview.query.count()

    completed_interviews = Interview.query.filter_by(
        status="Completed"
    ).count()

    pending_interviews = Interview.query.filter(
        Interview.status != "Completed"
    ).count()

    average_confidence = (
        db.session.query(
            func.avg(AIAnalysis.confidence_score)
        ).scalar() or 0
    )

    average_overall = (
        db.session.query(
            func.avg(AIAnalysis.overall_score)
        ).scalar() or 0
    )

    average_voice = (
        db.session.query(
            func.avg(AIAnalysis.voice_confidence)
        ).scalar() or 0
    )

    latest = Interview.query.order_by(
        Interview.created_at.desc()
    ).limit(5).all()

    recent = []

    for interview in latest:

        recent.append({

            "id": interview.id,

            "title": interview.title,

            "company": interview.company,

            "role": interview.role,

            "status": interview.status,

            "created_at": str(interview.created_at)

        })

    return {

        "total_users": total_users,

        "total_interviews": total_interviews,

        "completed_interviews": completed_interviews,

        "pending_interviews": pending_interviews,

        "average_confidence": round(average_confidence, 2),

        "average_voice_confidence": round(average_voice, 2),

        "average_overall_score": round(average_overall, 2),

        "recent_interviews": recent

    }