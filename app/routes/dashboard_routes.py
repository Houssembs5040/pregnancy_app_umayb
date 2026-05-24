from flask import Blueprint, jsonify

from app.services.dashboard_service import get_dashboard_data
from app.utils.decorators import current_user_required

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("", methods=["GET"])
@current_user_required
def get_dashboard(current_user):
    try:
        result = get_dashboard_data(current_user)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
