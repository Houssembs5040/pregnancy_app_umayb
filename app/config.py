import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-key")

    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "defaultdb")
    DB_SSL = os.getenv("DB_SSL", "false").lower() == "true"

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Enable SSL when connecting to cloud databases (e.g. Aiven) — SSL mode REQUIRED
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"ssl": {}} if DB_SSL else {}
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False
