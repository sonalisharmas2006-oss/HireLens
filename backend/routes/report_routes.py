from flask import Blueprint, jsonify

from services.report_service import (
    generate_report,
    get_report
)

report_bp = Blueprint("report", __name__)


@report_bp.route("/api/report/generate/<int:interview_id>", methods=["POST"])
def create_report(interview_id):

    try:
        report = generate_report(interview_id)

        if report is None:
            return jsonify({
                "message": "Report could not be generated"
            }), 404

        return jsonify({
            "message": "Report Generated Successfully",
            "report": report.to_dict()
        }), 201

    except Exception as e:
        print("REPORT ERROR:", e)
        return jsonify({
            "message": str(e)
        }), 500


@report_bp.route("/api/report/<int:interview_id>", methods=["GET"])
def fetch_report(interview_id):

    report = get_report(interview_id)

    if report is None:
        return jsonify({
            "message": "Report Not Found"
        }), 404

    return jsonify(report.to_dict())