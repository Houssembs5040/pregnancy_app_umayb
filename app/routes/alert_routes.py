from flask import Blueprint, jsonify, request

from app.services.alert_service import create_alert, list_alerts, resolve_alert
from app.utils.decorators import current_user_required

alert_bp = Blueprint("alerts", __name__, url_prefix="/alerts")


def _parse_active_only(value):
    if value is None:
        return None

    value = value.strip().lower()

    if value in {"true", "1", "yes"}:
        return True
    if value in {"false", "0", "no"}:
        return False

    raise ValueError("active_only must be true or false")


@alert_bp.route("", methods=["POST"])
@current_user_required
def create_new_alert(current_user):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    try:
        result = create_alert(current_user, data)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@alert_bp.route("", methods=["GET"])
@current_user_required
def get_alerts(current_user):
    try:
        active_only_raw = request.args.get("active_only")
        active_only = _parse_active_only(active_only_raw)
        result = list_alerts(current_user, active_only=active_only)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@alert_bp.route("/<int:alert_id>/resolve", methods=["PATCH"])
@current_user_required
def resolve_existing_alert(current_user, alert_id):
    try:
        result = resolve_alert(current_user, alert_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
