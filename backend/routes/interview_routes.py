from flask import Blueprint, request, jsonify

from services.interview_service import (
    create_interview,
    get_all_interviews,
    get_interview,
    complete_interview,
    delete_interview
)

interview_bp = Blueprint("interview", __name__)


# Create Interview
@interview_bp.route("/api/interview/create", methods=["POST"])
def create():

    data = request.get_json()

    interview = create_interview(data["user_id"])

    return jsonify({
        "message": "Interview Created",
        "interview": interview.to_dict()
    }), 201


# Get All Interviews
@interview_bp.route("/api/interview/all", methods=["GET"])
def get_all():

    interviews = get_all_interviews()

    return jsonify({
        "count": len(interviews),
        "interviews": [i.to_dict() for i in interviews]
    })


# Get One Interview
@interview_bp.route("/api/interview/<int:id>", methods=["GET"])
def get_one(id):

    interview = get_interview(id)

    if not interview:
        return jsonify({
            "message": "Interview Not Found"
        }), 404

    return jsonify(interview.to_dict())


# Complete Interview
@interview_bp.route("/api/interview/complete/<int:id>", methods=["PATCH"])
def complete(id):

    interview = complete_interview(id)

    if not interview:
        return jsonify({
            "message": "Interview Not Found"
        }), 404

    return jsonify({
        "message": "Interview Completed",
        "interview": interview.to_dict()
    })


# Delete Interview
@interview_bp.route("/api/interview/delete/<int:id>", methods=["DELETE"])
def delete(id):

    success = delete_interview(id)

    if not success:
        return jsonify({
            "message": "Interview Not Found"
        }), 404

    return jsonify({
        "message": "Interview Deleted"
    })