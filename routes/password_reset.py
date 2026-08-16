from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import secrets

from models.user import User
from extensions import db
from flask_mail import Message
from extensions import mail

password_reset_bp = Blueprint("password_reset", __name__)


@password_reset_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """
    Request a password reset email.
    ---
    tags:
      - Password Reset
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
          properties:
            email:
              type: string
              format: email
    responses:
      200:
        description: Password reset email sent successfully.
      400:
        description: Email is required.
      404:
        description: User not found.
    """

    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"message": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    token = secrets.token_urlsafe(32)

    user.reset_token = token
    user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=30)

    db.session.commit()

    reset_link = f"http://localhost:5000/reset-password/{token}"

    message = Message(
        "Password Reset Request",
        recipients=[email]
    )
    message.body = f"Click this link to reset your password: {reset_link}"

    mail.send(message)

    return jsonify({
        "message": "Password reset email sent"
    }), 200


@password_reset_bp.route("/reset-password/<token>", methods=["POST"])
def reset_password(token):
    """
    Reset a user's password using a valid reset token.
    ---
    tags:
      - Password Reset
    consumes:
      - application/json
    parameters:
      - name: token
        in: path
        required: true
        type: string
        description: Password reset token received by email.
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - password
          properties:
            password:
              type: string
              format: password
    responses:
      200:
        description: Password reset successful.
      400:
        description: Missing password, invalid token, or expired token.
    """

    data = request.get_json()
    new_password = data.get("password")

    if not new_password:
        return jsonify({"message": "Password is required"}), 400

    user = User.query.filter_by(reset_token=token).first()

    if not user:
        return jsonify({"message": "Invalid token"}), 400

    if datetime.utcnow() > user.reset_token_expiry:
        return jsonify({"message": "Token expired"}), 400

    user.password = generate_password_hash(new_password)
    user.reset_token = None
    user.reset_token_expiry = None

    db.session.commit()

    return jsonify({
        "message": "Password reset successful"
    }), 200