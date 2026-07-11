from flask import Flask
from flask_cors import CORS

from config import Config
from database.db import db
from routes.home_routes import home_bp

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)

db.init_app(app)

app.register_blueprint(home_bp)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)