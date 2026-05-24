from flask import Blueprint, jsonify, request

from app.services.fetal_movement_service import (
    start_session,
    increment_count,
    end_session,
    list_sessions,
    get_open_session,
    check_absence_alert,
)
from app.utils.decorators import current_user_required

fetal_movement_bp = Blueprint(
    "fetal_movement", __name__, url_prefix="/followup/fetal-movements"
)


@fetal_movement_bp.route("/start", methods=["POST"])
@current_user_required
def start_counting(current_user):
    """Start a new fetal movement counting session (requires 28 SA)."""
    try:
        result = start_session(current_user)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@fetal_movement_bp.route("/<int:session_id>/increment", methods=["POST"])
@current_user_required
def add_movement(current_user, session_id):
    """Increment movement count for an open session (tap once per movement felt)."""
    try:
        result = increment_count(current_user, session_id)
        return jsonify(result), 200
    except ValueError as e:
        status = 404 if "not found" in str(e) else 400
        return jsonify({"error": str(e)}), status
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@fetal_movement_bp.route("/<int:session_id>/end", methods=["POST"])
@current_user_required
def end_counting(current_user, session_id):
    """End a session, record final count and trigger alerts if needed."""
    data = request.get_json(silent=True) or {}
    try:
        result = end_session(current_user, session_id, data)
        return jsonify(result), 200
    except ValueError as e:
        status = 404 if "not found" in str(e) else 400
        return jsonify({"error": str(e)}), status
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@fetal_movement_bp.route("", methods=["GET"])
@current_user_required
def get_sessions(current_user):
    """List all past fetal movement sessions."""
    try:
        result = list_sessions(current_user)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@fetal_movement_bp.route("/open", methods=["GET"])
@current_user_required
def get_current_session(current_user):
    """Get the currently open (in-progress) session, if any."""
    try:
        result = get_open_session(current_user)
        if result is None:
            return jsonify({"message": "no active session"}), 404
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@fetal_movement_bp.route("/check-absence", methods=["POST"])
@current_user_required
def check_absence(current_user):
    """
    Manually trigger absence check (> 12h without session at 28+ SA).
    In production this would be called by a scheduler; exposed here for testing.
    """
    try:
        result = check_absence_alert(current_user)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
