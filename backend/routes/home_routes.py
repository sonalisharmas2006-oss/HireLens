from flask import Blueprint

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
def home():
    return {
        "project": "HireLens AI",
        "version": "1.0",
        "status": "Backend Running Successfully 🚀",
        "developer": "Sonali Sharma"
    }