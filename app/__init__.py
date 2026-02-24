from flask import Flask

from config import Config
from app.extensions import db
from app.helper.logger import init_logger


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Initialize logger with app config
    init_logger(app)

    return app