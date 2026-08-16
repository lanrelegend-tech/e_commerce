from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models.user import User

profile_bp = Blueprint("profile", __name__)


# Get current user profile
@profile_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """
    Get the authenticated user's profile.
    ---
    tags:
      - Profile
    security:
      - Bearer: []
    responses:
      200:
        description: User profile returned successfully.
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
            email:
              type: string
              format: email
      401:
        description: Authentication required.
      404:
        description: User not found.
    """

    user_id = int(get_jwt_identity())

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email
    }), 200


# Update profile details
@profile_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """
    Update the authenticated user's profile details.
    ---
    tags:
      - Profile
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            email:
              type: string
              format: email
    responses:
      200:
        description: Profile updated successfully.
      400:
        description: Invalid profile data.
      401:
        description: Authentication required.
      404:
        description: User not found.
    """

    user_id = int(get_jwt_identity())

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()

    if "name" in data:
        user.name = data["name"]

    if "email" in data:
        user.email = data["email"]

    db.session.commit()

    return jsonify({
        "message": "Profile updated successfully"
    }), 200


# Change password while logged in
@profile_bp.route("/profile/password", methods=["PUT"])
@jwt_required()
def change_password():
    """
    Change the authenticated user's password.
    ---
    tags:
      - Profile
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - old_password
            - new_password
          properties:
            old_password:
              type: string
              format: password
            new_password:
              type: string
              format: password
    responses:
      200:
        description: Password changed successfully.
      400:
        description: Old password is incorrect.
      401:
        description: Authentication required.
    """

    user_id = int(get_jwt_identity())

    user = db.session.get(User, user_id)

    data = request.get_json()

    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not check_password_hash(user.password, old_password):
        return jsonify({
            "error": "Old password is incorrect"
        }), 400

    user.password = generate_password_hash(new_password)

    db.session.commit()

    return jsonify({
        "message": "Password changed successfully"
    }), 200