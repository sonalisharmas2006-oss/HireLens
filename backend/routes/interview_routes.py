from flask import Blueprint, request, jsonify

from services.interview_service import (
    create_interview,
    get_all_interviews,
    get_interview
)

interview_bp = Blueprint("interview", __name__)


@interview_bp.route("/api/interview/create", methods=["POST"])
def create():

    data = request.get_json()

    interview = create_interview(
        user_id=data["user_id"],
        title=data.get("title", "Mock Interview"),
        company=data.get("company", "General"),
        role=data.get("role", "Software Engineer"),
        interview_type=data.get("interview_type", "Technical")
    )

    return jsonify({
        "message": "Interview Created Successfully",
        "interview": interview.to_dict()
    }), 201


@interview_bp.route("/api/interview/all", methods=["GET"])
def get_all():

    interviews = get_all_interviews()

    return jsonify([
        interview.to_dict()
        for interview in interviews
    ])


@interview_bp.route("/api/interview/<int:interview_id>", methods=["GET"])
def get_one(interview_id):

    interview = get_interview(interview_id)

    if interview is None:
        return jsonify({
            "message": "Interview Not Found"
        }), 404

    return jsonify(interview.to_dict())