import os
from flask import Flask, request
from flask_cors import CORS
from app.config import Config
import re
from app.extensions import db, migrate, jwt, cors   # keep if you need them

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Parse comma-separated frontend URLs from env (supports multiple origins)
    _frontend_urls = [
        u.strip() for u in os.getenv("FRONTEND_URL", "").split(",") if u.strip()
    ]

    CORS(
        app,
        origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://umay-tau.vercel.app",      # production Vercel frontend
            r"https://.*\.vercel\.app",          # all Vercel preview deployments (regex)
            *_frontend_urls,
        ],
        allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        supports_credentials=True,
        max_age=3600
    )

    # Remove your custom after_request handler - it's causing conflicts
    # We'll rely on flask-cors instead

    from app.models import (
        User, UserProfile, PregnancyProfile, Appointment,
        AppointmentFollowup, Alert,
        WeightMeasurement, BloodPressureMeasurement,
        GlucoseMeasurement, FetalMovementSession,
        UserSetting, Conversation, ChatMessage,
    )

    from app.routes import (
        auth_bp, pregnancy_bp, profile_bp, dashboard_bp,
        appointment_bp, alert_bp, chat_bp,
        weight_bp, blood_pressure_bp, glucose_bp, fetal_movement_bp,
        tips_bp, setting_bp,
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(pregnancy_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(alert_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(weight_bp)
    app.register_blueprint(blood_pressure_bp)
    app.register_blueprint(glucose_bp)
    app.register_blueprint(fetal_movement_bp)
    app.register_blueprint(tips_bp)
    app.register_blueprint(setting_bp)

    @app.route("/")
    def home():
        return {"message": "Pregnancy Tracker API is running"}

    return app