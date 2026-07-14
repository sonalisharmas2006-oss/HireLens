from flask import Blueprint, jsonify

chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.route("/api/chatbot/test", methods=["GET"])
def chatbot_test():
    return jsonify({
        "message": "Chatbot Route Working"
    })