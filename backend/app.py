from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from database.db import db
from services.auth_service import bcrypt

# Blueprints
from routes.home_routes import home_bp
from routes.auth_routes import auth_bp
from routes.interview_routes import interview_bp

# Models
from models.user import User
from models.interview import Interview

app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Enable CORS
CORS(app)

# Initialize Extensions
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

# Register Blueprints
app.register_blueprint(home_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(interview_bp)

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)