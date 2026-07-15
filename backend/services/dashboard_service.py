from models.user import User
from models.interview import Interview
from models.report import Report


def get_dashboard_stats():

    total_users = User.query.count()

    total_interviews = Interview.query.count()

    completed_interviews = Interview.query.filter_by(
        status="Completed"
    ).count()

    reports = Report.query.all()

    if reports:

        scores = [
            report.confidence_score
            for report in reports
        ]

        average_score = round(
            sum(scores) / len(scores),
            2
        )

        best_score = max(scores)

    else:

        average_score = 0
        best_score = 0

    latest = Interview.query.order_by(
        Interview.created_at.desc()
    ).limit(5).all()

    return {

        "total_users": total_users,

        "total_interviews": total_interviews,

        "completed_interviews": completed_interviews,

        "average_confidence_score": average_score,

        "best_confidence_score": best_score,

        "latest_interviews": [

            interview.to_dict()

            for interview in latest

        ]
    }