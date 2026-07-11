from flask import Flask
from flask_cors import CORS

from config import Config
from database.db import db
from services.auth_service import bcrypt

from routes.home_routes import home_bp
from routes.auth_routes import auth_bp   # <-- Add it here

from models.user import User

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)

db.init_app(app)
bcrypt.init_app(app)

app.register_blueprint(home_bp)
app.register_blueprint(auth_bp)   # <-- Register it here

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)