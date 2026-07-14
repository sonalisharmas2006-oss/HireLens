from database.db import db
from models.user import User
from flask_bcrypt import generate_password_hash, check_password_hash


def register_user(name, email, password):

    # Check if email already exists
    if User.query.filter_by(email=email).first():
        return None

    # Hash the password
    hashed_password = generate_password_hash(password).decode("utf-8")

    # Create new user
    user = User(
        name=name,
        email=email,
        password=hashed_password
    )

    db.session.add(user)
    db.session.commit()

    return user


def login_user(email, password):

    # Find user by email
    user = User.query.filter_by(email=email).first()

    if not user:
        return None

    # Verify password
    if not check_password_hash(user.password, password):
        return None

    return user