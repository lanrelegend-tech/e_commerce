from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.user import User


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):

        current_user = db.session.get(
            User,
            int(get_jwt_identity())
        )

        if not current_user:
            return jsonify({"error": "User not found"}), 404

        if not current_user.is_admin:
            return jsonify({"error": "Admin access required"}), 403

        return fn(*args, **kwargs)

    return wrapper