from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from services.auth_service import register_user, login_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/register", methods=["POST"])
def register():

    data = request.get_json()

    user = register_user(
        data["name"],
        data["email"],
        data["password"]
    )

    if user is None:
        return jsonify({
            "message": "Email already exists"
        }), 400

    return jsonify({
        "message": "User registered successfully",
        "user": user.to_dict()
    }), 201


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():

    data = request.get_json()

    user = login_user(
        data["email"],
        data["password"]
    )

    if user is None:
        return jsonify({
            "message": "Invalid Email or Password"
        }), 401

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Login Successful",
        "token": token,
        "user": user.to_dict()
    }), 200