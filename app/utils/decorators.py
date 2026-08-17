from functools import wraps
from app.extensions import db

import jwt
from flask import request, jsonify

from app.config import Config
from app.models import User


def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        # Get Authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({
                "error": "Authorization header is required"
            }), 401

        # Expected format:
        # Authorization: Bearer <token>
        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({
                "error": "Invalid authorization header format"
            }), 401

        token = parts[1]

        try:
            payload = jwt.decode(
                token,
                Config.SECRET_KEY,
                algorithms=["HS256"]
            )

        except jwt.ExpiredSignatureError:
            return jsonify({
                "error": "Token has expired"
            }), 401

        except jwt.InvalidTokenError:
            return jsonify({
                "error": "Invalid token"
            }), 401

        # Get user ID from token
        user_id = payload.get("sub")

        if not user_id:
            return jsonify({
                "error": "Invalid token payload"
            }), 401

        # Find user
        user = db.session.get(User, user_id)

        if not user:
            return jsonify({
                "error": "User no longer exists"
            }), 401

        if not user.is_active:
            return jsonify({
                "error": "Account is not active"
            }), 401

        # Attach authenticated user to request
        request.current_user = user

        return f(*args, **kwargs)

    return decorated_function


def role_required(*allowed_roles):
    def decorator(f):

        @wraps(f)
        @jwt_required
        def decorated_function(*args, **kwargs):

            user = request.current_user

            if user.role not in allowed_roles:
                return jsonify({
                    "error": "You do not have permission to access this resource"
                }), 403

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f):
    return role_required("admin")(f)


def partner_required(f):
    return role_required("partner")(f)