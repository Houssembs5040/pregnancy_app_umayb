from flask import Blueprint, jsonify, request

from app.services.glucose_service import add_glucose, list_glucose, get_latest_glucose
from app.utils.decorators import current_user_required

glucose_bp = Blueprint("glucose", __name__, url_prefix="/followup/glucose")


@glucose_bp.route("", methods=["POST"])
@current_user_required
def create_glucose(current_user):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    try:
        result = add_glucose(current_user, data)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@glucose_bp.route("", methods=["GET"])
@current_user_required
def get_glucose(current_user):
    try:
        result = list_glucose(current_user)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@glucose_bp.route("/latest", methods=["GET"])
@current_user_required
def latest_glucose(current_user):
    try:
        result = get_latest_glucose(current_user)
        if result is None:
            return jsonify({"message": "no glucose measurements found"}), 404
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
