from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity

from extensions import db
from models.user import User
from utils.admin import admin_required

admin_bp = Blueprint("admin", __name__)




@admin_bp.route("/admin/promote/<int:user_id>", methods=["PUT"])
@admin_required
def promote_user(user_id):

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({
            "error": "User not found."
        }), 404

    if user.is_admin:
        return jsonify({
            "message": "User is already an admin."
        }), 200

    user.is_admin = True

    db.session.commit()

    return jsonify({
        "message": f"{user.username} is now an admin."
    }), 200