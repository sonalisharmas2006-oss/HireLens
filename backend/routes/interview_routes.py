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

    interview = create_interview(data["user_id"])

    return jsonify({
        "message": "Interview Created Successfully",
        "interview": interview.to_dict()
    }), 201


@interview_bp.route("/api/interview/all", methods=["GET"])
def all_interviews():

    interviews = get_all_interviews()

    return jsonify({
        "count": len(interviews),
        "interviews": [i.to_dict() for i in interviews]
    })


@interview_bp.route("/api/interview/<int:id>", methods=["GET"])
def one_interview(id):

    interview = get_interview(id)

    if not interview:
        return jsonify({
            "message": "Interview Not Found"
        }), 404

    return jsonify(interview.to_dict())