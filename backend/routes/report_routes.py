from flask import Blueprint, request, jsonify

from services.report_service import (
    generate_report,
    get_report
)

report_bp = Blueprint("report", __name__)


@report_bp.route("/api/report/generate", methods=["POST"])
def create_report():

    data = request.get_json()

    report = generate_report(
        data["interview_id"]
    )

    return jsonify({
        "message": "Report Generated Successfully",
        "report": report.to_dict()
    }), 201


@report_bp.route("/api/report/<int:interview_id>", methods=["GET"])
def fetch_report(interview_id):

    report = get_report(interview_id)

    if not report:
        return jsonify({
            "message": "Report Not Found"
        }), 404

    return jsonify(report.to_dict())