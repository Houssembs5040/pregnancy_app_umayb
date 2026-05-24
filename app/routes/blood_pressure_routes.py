from flask import Blueprint, jsonify, request

from app.services.blood_pressure_service import (
    add_blood_pressure,
    list_blood_pressure,
    get_latest_blood_pressure,
)
from app.utils.decorators import current_user_required

blood_pressure_bp = Blueprint(
    "blood_pressure", __name__, url_prefix="/followup/blood-pressure"
)


@blood_pressure_bp.route("", methods=["POST"])
@current_user_required
def create_blood_pressure(current_user):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    try:
        result = add_blood_pressure(current_user, data)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@blood_pressure_bp.route("", methods=["GET"])
@current_user_required
def get_blood_pressure(current_user):
    try:
        result = list_blood_pressure(current_user)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@blood_pressure_bp.route("/latest", methods=["GET"])
@current_user_required
def latest_blood_pressure(current_user):
    try:
        result = get_latest_blood_pressure(current_user)
        if result is None:
            return jsonify({"message": "no blood pressure measurements found"}), 404
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
