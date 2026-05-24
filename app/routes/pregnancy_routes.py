from flask import Blueprint, jsonify

from app.services.pregnancy_service import get_current_pregnancy_data
from app.utils.decorators import current_user_required

pregnancy_bp = Blueprint("pregnancy", __name__, url_prefix="/pregnancy")


@pregnancy_bp.route("/current", methods=["GET"])
@current_user_required
def current_pregnancy(current_user):
    try:
        result = get_current_pregnancy_data(current_user)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
