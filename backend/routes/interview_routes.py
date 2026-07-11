from flask import Blueprint, request, jsonify

from database.db import db
from models.interview import Interview

interview_bp = Blueprint("interview", __name__)


# Create Interview
@interview_bp.route("/api/interview/create", methods=["POST"])
def create_interview():

    data = request.get_json()

    interview = Interview(
        user_id=data["user_id"]
    )

    db.session.add(interview)
    db.session.commit()

    return jsonify({
        "message": "Interview Created",
        "interview": interview.to_dict()
    }), 201


# Get All Interviews
@interview_bp.route("/api/interview/all", methods=["GET"])
def get_all_interviews():

    interviews = Interview.query.all()

    return jsonify({
        "count": len(interviews),
        "interviews": [i.to_dict() for i in interviews]
    }), 200