from flask import Blueprint, jsonify, request

from app.services.appointment_service import (
    list_appointments,
    get_appointment_by_id,
    create_appointment,
    update_appointment,
    delete_appointment,
    generate_prenatal_consultations,
    generate_monthly_analyses,
    complete_appointment,
    get_appointment_history,
)
from app.utils.decorators import current_user_required

appointment_bp = Blueprint("appointments", __name__, url_prefix="/appointments")


@appointment_bp.route("", methods=["GET"])
@current_user_required
def get_appointments(current_user):
    try:
        status = request.args.get("status")
        result = list_appointments(current_user, status=status)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@appointment_bp.route("/history", methods=["GET"])
@current_user_required
def get_history(current_user):
    try:
        result = get_appointment_history(current_user)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@appointment_bp.route("/<int:appointment_id>", methods=["GET"])
@current_user_required
def get_appointment(current_user, appointment_id):
    try:
        result = get_appointment_by_id(current_user, appointment_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@appointment_bp.route("", methods=["POST"])
@current_user_required
def create_new_appointment(current_user):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    try:
        result = create_appointment(current_user, data)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@appointment_bp.route("/generate-prenatal-plan", methods=["POST"])
@current_user_required
def generate_prenatal_plan(current_user):
    try:
        result = generate_prenatal_consultations(current_user)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@appointment_bp.route("/generate-monthly-analyses", methods=["POST"])
@current_user_required
def generate_monthly_analyses_route(current_user):
    try:
        result = generate_monthly_analyses(current_user)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@appointment_bp.route("/<int:appointment_id>/complete", methods=["POST"])
@current_user_required
def complete_existing_appointment(current_user, appointment_id):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    try:
        result = complete_appointment(current_user, appointment_id, data)
        return jsonify(result), 200
    except ValueError as e:
        message = str(e)
        status_code = 404 if message == "appointment not found" else 400
        return jsonify({"error": message}), status_code
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@appointment_bp.route("/<int:appointment_id>", methods=["PUT"])
@current_user_required
def update_existing_appointment(current_user, appointment_id):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    try:
        result = update_appointment(current_user, appointment_id, data)
        return jsonify(result), 200
    except ValueError as e:
        message = str(e)
        status_code = 404 if message == "appointment not found" else 400
        return jsonify({"error": message}), status_code
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@appointment_bp.route("/<int:appointment_id>", methods=["DELETE"])
@current_user_required
def delete_existing_appointment(current_user, appointment_id):
    try:
        result = delete_appointment(current_user, appointment_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
