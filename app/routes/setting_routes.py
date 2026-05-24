from flask import Blueprint, jsonify, request

from app.services.setting_service import get_settings, update_settings
from app.utils.decorators import current_user_required

setting_bp = Blueprint("settings", __name__, url_prefix="/settings")


@setting_bp.route("", methods=["GET"])
@current_user_required
def get_user_settings(current_user):
    """Return the current user's notification settings."""
    try:
        result = get_settings(current_user)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@setting_bp.route("", methods=["PUT"])
@current_user_required
def update_user_settings(current_user):
    """Update notification preferences."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    try:
        result = update_settings(current_user, data)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
