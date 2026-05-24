from functools import wraps

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from app.extensions import db
from app.models import User


def current_user_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = db.session.get(User, int(user_id))

            if not user:
                return jsonify({"error": "user not found"}), 404

            return fn(current_user=user, *args, **kwargs)
        except Exception:
            return jsonify({"error": "invalid or missing token"}), 401

    return wrapper
