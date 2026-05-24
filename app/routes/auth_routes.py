from flask import Blueprint, request, jsonify

from app.services.auth_service import register_user, login_user, get_current_user_data, change_password
from app.utils.decorators import current_user_required

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST", "OPTIONS"])
def register():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    try:
        result = register_user(data)
        response = {"data": result, "success": True}
        return jsonify(response), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@auth_bp.route("/login", methods=["POST", "OPTIONS"])
def login():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    try:
        result = login_user(data)
        response = {"data": result, "success": True}
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@auth_bp.route("/me", methods=["GET"])
@current_user_required
def me(current_user):
    try:
        result = get_current_user_data(current_user)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@auth_bp.route("/change-password", methods=["POST"])
@current_user_required
def change_user_password(current_user):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    try:
        result = change_password(current_user, data)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500