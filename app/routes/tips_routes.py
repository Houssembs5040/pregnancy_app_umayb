from flask import Blueprint, jsonify, request

from app.data.tips import get_tips_by_trimester, get_tips_by_category, AVAILABLE_CATEGORIES
from app.utils.decorators import current_user_required

tips_bp = Blueprint("tips", __name__, url_prefix="/tips")


def _get_trimester(user) -> int:
    pregnancy = user.pregnancy_profile
    if not pregnancy:
        return 1  # fallback
    return pregnancy.trimester()


@tips_bp.route("", methods=["GET"])
@current_user_required
def get_all_tips(current_user):
    """Return all tip categories with content for the user's current trimester."""
    try:
        trimester = _get_trimester(current_user)
        result = get_tips_by_trimester(trimester)
        return jsonify({
            "trimester": trimester,
            "categories": result,
        }), 200
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@tips_bp.route("/categories", methods=["GET"])
@current_user_required
def list_categories(current_user):
    """Return a list of available tip categories."""
    return jsonify({"categories": AVAILABLE_CATEGORIES}), 200


@tips_bp.route("/<string:category>", methods=["GET"])
@current_user_required
def get_category_tips(current_user, category):
    """Return tips for a specific category, for the user's current trimester."""
    try:
        trimester_override = request.args.get("trimester")
        trimester = int(trimester_override) if trimester_override else _get_trimester(current_user)

        if trimester not in (1, 2, 3):
            return jsonify({"error": "trimester must be 1, 2, or 3"}), 400

        result = get_tips_by_category(category, trimester)
        if result is None:
            return jsonify({
                "error": f"Unknown category '{category}'. Available: {AVAILABLE_CATEGORIES}"
            }), 404

        return jsonify(result), 200
    except ValueError:
        return jsonify({"error": "trimester must be an integer (1, 2 or 3)"}), 400
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500
