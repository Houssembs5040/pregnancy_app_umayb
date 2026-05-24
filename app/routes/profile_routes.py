from flask import Blueprint, jsonify, request

from app.services.profile_service import get_profile_data, update_profile_data
from app.utils.decorators import current_user_required

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.route("", methods=["GET"])
@current_user_required
def get_profile(current_user):
    try:
        result = get_profile_data(current_user)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@profile_bp.route("", methods=["PUT"])
@current_user_required
def update_profile(current_user):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    try:
        result = update_profile_data(current_user, data)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
