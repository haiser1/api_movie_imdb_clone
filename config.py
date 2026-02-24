import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = 300
    JWT_REFRESH_TOKEN_EXPIRES = 604800

    # Port untuk menjalankan aplikasi
    PORT = os.getenv("GLOBAL_PORT")  # Default port
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30,
        "connect_args": {
            "options": (
                "-c statement_timeout=5000 "  # 5 second for timeout query
                "-c lock_timeout=3000 "  # 3 second for timeout lock
                "-c idle_in_transaction_session_timeout=60000"  # 60 second for timeout idle in transaction
            )
        },
    }

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
