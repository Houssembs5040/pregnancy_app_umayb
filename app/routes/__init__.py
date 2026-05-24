from app.routes.auth_routes import auth_bp
from app.routes.pregnancy_routes import pregnancy_bp
from app.routes.profile_routes import profile_bp
from app.routes.dashboard_routes import dashboard_bp
from app.routes.appointment_routes import appointment_bp
from app.routes.alert_routes import alert_bp
from app.routes.chat_routes import chat_bp
from app.routes.weight_routes import weight_bp
from app.routes.blood_pressure_routes import blood_pressure_bp
from app.routes.glucose_routes import glucose_bp
from app.routes.fetal_movement_routes import fetal_movement_bp
from app.routes.tips_routes import tips_bp
from app.routes.setting_routes import setting_bp

__all__ = [
    "auth_bp",
    "pregnancy_bp",
    "profile_bp",
    "dashboard_bp",
    "appointment_bp",
    "alert_bp",
    "chat_bp",
    "weight_bp",
    "blood_pressure_bp",
    "glucose_bp",
    "fetal_movement_bp",
    "tips_bp",
    "setting_bp",
]
