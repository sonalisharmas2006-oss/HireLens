from flask import Blueprint, request, jsonify

from services.chatbot_service import get_chatbot_response

chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.route("/api/chatbot", methods=["POST"])
def chatbot():

    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({
            "message": "Message is required"
        }), 400

    reply = get_chatbot_response(data["message"])

    return jsonify({
        "user_message": data["message"],
        "bot_reply": reply
    }), 200


@chatbot_bp.route("/api/chatbot/test", methods=["GET"])
def chatbot_test():

    return jsonify({
        "message": "Chatbot Route Working"
    })