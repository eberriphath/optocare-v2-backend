from flask import Blueprint, request, jsonify
from datetime import datetime, timezone

from app.extensions import db
from app.models import Application, User
from app.utils.security import hash_password


activation_bp = Blueprint(
    "activation",
    __name__,
    url_prefix="/api/activation"
)


@activation_bp.route("/<token>", methods=["POST"])
def activate_account(token):

    application = Application.query.filter_by(
        activation_token=token
    ).first()

    if not application:
        return jsonify({
            "error": "Invalid activation token"
        }), 400

    if application.status != "approved":
        return jsonify({
            "error": "This application is not approved"
        }), 400

    if not application.activation_expires_at:
        return jsonify({
            "error": "Activation token is invalid"
        }), 400

    now = datetime.now(timezone.utc)

    expires_at = application.activation_expires_at

    # Handle database timestamps without timezone
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if now > expires_at:
        return jsonify({
            "error": "Activation token has expired"
        }), 400

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    password = data.get("password")

    if not password:
        return jsonify({
            "error": "Password is required"
        }), 400

    if len(password) < 8:
        return jsonify({
            "error": "Password must be at least 8 characters"
        }), 400

    user = User.query.filter_by(
        email=application.email.lower()
    ).first()

    if not user:
        return jsonify({
            "error": "Partner account not found"
        }), 404

    user.password_hash = hash_password(password)
    user.is_active = True
    user.must_set_password = False

    # Token can only be used once
    application.activation_token = None
    application.activation_expires_at = None

    db.session.commit()

    return jsonify({
        "message": "Account activated successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 200