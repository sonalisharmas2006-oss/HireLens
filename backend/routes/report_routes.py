from flask import Blueprint, jsonify

report_bp = Blueprint("report", __name__)


@report_bp.route("/api/report/test", methods=["GET"])
def report_test():
    return jsonify({
        "message": "Report Route Working"
    })