from flask import Blueprint, jsonify, request

from app.services.weight_service import add_weight, list_weights, get_latest_weight
from app.utils.decorators import current_user_required

weight_bp = Blueprint("weight", __name__, url_prefix="/followup/weight")


@weight_bp.route("", methods=["POST"])
@current_user_required
def create_weight(current_user):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    try:
        result = add_weight(current_user, data)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@weight_bp.route("", methods=["GET"])
@current_user_required
def get_weights(current_user):
    try:
        result = list_weights(current_user)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@weight_bp.route("/latest", methods=["GET"])
@current_user_required
def latest_weight(current_user):
    try:
        result = get_latest_weight(current_user)
        if result is None:
            return jsonify({"message": "no weight measurements found"}), 404
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
