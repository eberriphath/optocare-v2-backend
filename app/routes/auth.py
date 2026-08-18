from flask import Blueprint, request, jsonify
import jwt
from datetime import datetime, timedelta, timezone
import secrets
import hashlib

from app.config import Config
from app.models import User, Application
from app.utils.security import check_password, hash_password
from app.utils.decorators import jwt_required
from app.extensions import db


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    user = User.query.filter_by(email=email.lower()).first()

    if not user:
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    if not user.is_active:
        return jsonify({
            "error": "Account is not active"
        }), 403

    if not check_password(password, user.password_hash):
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user.id),
        "role": user.role,
        "iat": now,
        "exp": now + timedelta(hours=2)
    }

    token = jwt.encode(
        payload,
        Config.SECRET_KEY,
        algorithm="HS256"
    )

    return jsonify({
        "message": "Login successful",
        "access_token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 200

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    email = data.get("email")

    if not email:
        return jsonify({
            "error": "Email is required"
        }), 400

    email = email.strip().lower()

    user = User.query.filter_by(
        email=email
    ).first()

    # Always return the same response so attackers
    # cannot discover which emails have accounts.
    if not user:
        return jsonify({
            "message": "If an account exists for this email, password reset instructions will be provided."
        }), 200

    # Generate secure random token
    raw_token = secrets.token_urlsafe(48)

    # Hash token before storing it
    token_hash = hashlib.sha256(
        raw_token.encode("utf-8")
    ).hexdigest()

    user.password_reset_token = token_hash

    user.password_reset_expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=30)
    )

    db.session.commit()

    # DEVELOPMENT ONLY
    # Later this token will be sent through email.
    return jsonify({
        "message": "If an account exists for this email, password reset instructions will be provided.",
        "development_token": raw_token,
        "expires_in_minutes": 30
    }), 200


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    token = data.get("token")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if not token:
        return jsonify({
            "error": "Reset token is required"
        }), 400

    if not new_password:
        return jsonify({
            "error": "New password is required"
        }), 400

    if not confirm_password:
        return jsonify({
            "error": "Password confirmation is required"
        }), 400

    if len(new_password) < 8:
        return jsonify({
            "error": "Password must be at least 8 characters"
        }), 400

    if new_password != confirm_password:
        return jsonify({
            "error": "Passwords do not match"
        }), 400

    # Hash the supplied token so we can compare it
    # against the hashed token stored in the database.
    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    user = User.query.filter_by(
        password_reset_token=token_hash
    ).first()

    if not user:
        return jsonify({
            "error": "Invalid or expired reset token"
        }), 400

    # Check expiration
    if not user.password_reset_expires_at:
        return jsonify({
            "error": "Invalid or expired reset token"
        }), 400

    expires_at = user.password_reset_expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    if expires_at < datetime.now(timezone.utc):
        return jsonify({
            "error": "Reset token has expired"
        }), 400

    # Prevent reusing the current password
    if check_password(
        new_password,
        user.password_hash
    ):
        return jsonify({
            "error": "New password must be different from current password"
        }), 400

    # Set new password
    user.password_hash = hash_password(
        new_password
    )

    # Invalidate reset token immediately
    user.password_reset_token = None
    user.password_reset_expires_at = None

    # A successful password reset should also satisfy
    # any previous "must set password" requirement.
    user.must_set_password = False

    db.session.commit()

    return jsonify({
        "message": "Password reset successfully"
    }), 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required
def me():
    user = request.current_user

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }), 200


@auth_bp.route("/activate", methods=["POST"])
def activate_account():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    token = data.get("token")
    password = data.get("password")

    if not token or not password:
        return jsonify({
            "error": "Activation token and password are required"
        }), 400

    if len(password) < 8:
        return jsonify({
            "error": "Password must be at least 8 characters"
        }), 400

    application = Application.query.filter_by(
        activation_token=token
    ).first()

    if not application:
        return jsonify({
            "error": "Invalid activation token"
        }), 400

    if application.status != "approved":
        return jsonify({
            "error": "This application has not been approved"
        }), 400

    if not application.activation_expires_at:
        return jsonify({
            "error": "Activation token is invalid"
        }), 400

    now = datetime.now(timezone.utc)

    # PostgreSQL may return a naive datetime depending on the column type
    expires_at = application.activation_expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < now:
        return jsonify({
            "error": "Activation token has expired"
        }), 400

    user = User.query.get(application.user_id)

    if not user:
        return jsonify({
            "error": "Associated user account not found"
        }), 400

    if user.is_active:
        return jsonify({
            "error": "Account is already active"
        }), 400

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
            "role": user.role,
            "is_active": user.is_active
        }
    }), 200