from flask import Flask
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

from config import Config
from database.db import db

# Blueprints
from routes.home_routes import home_bp
from routes.auth_routes import auth_bp
from routes.interview_routes import interview_bp
from routes.upload_routes import upload_bp
from routes.report_routes import report_bp
from routes.chatbot_routes import chatbot_bp

app = Flask(__name__)
app.config.from_object(Config)

print("Current Working Directory:", __import__("os").getcwd())
print("Database URI:", app.config["SQLALCHEMY_DATABASE_URI"])

CORS(app)

db.init_app(app)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

app.register_blueprint(home_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(interview_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(report_bp)
app.register_blueprint(chatbot_bp)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)