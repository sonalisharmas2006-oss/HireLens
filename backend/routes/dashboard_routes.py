from flask import Blueprint, jsonify

from services.dashboard_service import get_dashboard_stats

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/api/dashboard", methods=["GET"])
def dashboard():

    return jsonify(
        get_dashboard_stats()
    )