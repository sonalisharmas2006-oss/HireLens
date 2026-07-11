from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from database.db import db
from models.user import User
from services.auth_service import hash_password, check_password

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/register", methods=["POST"])
def register():

    data = request.get_json()

    if not data:
        return jsonify({"message": "No data received"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already exists"}), 400

    new_user = User(
        name=data["name"],
        email=data["email"],
        password=hash_password(data["password"])
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "user": new_user.to_dict()
    }), 201


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({"message": "No data received"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user:
        return jsonify({"message": "Invalid Email"}), 401

    if not check_password(user.password, data["password"]):
        return jsonify({"message": "Invalid Password"}), 401

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Login Successful",
        "token": token,
        "user": user.to_dict()
    }), 200