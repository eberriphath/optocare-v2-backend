from flask import Blueprint, request, jsonify
from email_validator import validate_email, EmailNotValidError

from app.extensions import db
from app.models import Application, User


applications_bp = Blueprint(
    "applications",
    __name__,
    url_prefix="/api/applications"
)


ALLOWED_PARTNER_TYPES = {
    "clinic",
    "optical_shop",
    "distributor",
    "manufacturer",
    "laboratory",
    "other"
}


@applications_bp.route("", methods=["POST"])
def create_application():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    required_fields = [
        "full_name",
        "position",
        "email",
        "phone",
        "company_name",
        "services_offered",
        "partner_type"
    ]

    missing_fields = [
        field
        for field in required_fields
        if not isinstance(data.get(field), str)
        or not data.get(field).strip()
    ]

    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing_fields
        }), 400

    full_name = data["full_name"].strip()
    position = data["position"].strip()
    email = data["email"].strip().lower()
    phone = data["phone"].strip()
    company_name = data["company_name"].strip()
    services_offered = data["services_offered"].strip()
    partner_type = data["partner_type"].strip().lower()

    # ---------------------------------------------------------
    # Length validation
    # ---------------------------------------------------------

    field_limits = {
        "full_name": (2, 120),
        "position": (2, 100),
        "email": (5, 150),
        "phone": (7, 30),
        "company_name": (2, 150),
        "services_offered": (10, 10000),
        "partner_type": (2, 30)
    }

    values = {
        "full_name": full_name,
        "position": position,
        "email": email,
        "phone": phone,
        "company_name": company_name,
        "services_offered": services_offered,
        "partner_type": partner_type
    }

    for field, (minimum, maximum) in field_limits.items():

        length = len(values[field])

        if length < minimum or length > maximum:
            return jsonify({
                "error": f"{field} must be between "
                         f"{minimum} and {maximum} characters"
            }), 400

    # ---------------------------------------------------------
    # Email validation
    # ---------------------------------------------------------

    try:
        validated_email = validate_email(
            email,
            check_deliverability=False
        )

        email = validated_email.normalized.lower()

    except EmailNotValidError:
        return jsonify({
            "error": "Invalid email address"
        }), 400

    # ---------------------------------------------------------
    # Partner type validation
    # ---------------------------------------------------------

    if partner_type not in ALLOWED_PARTNER_TYPES:
        return jsonify({
            "error": "Invalid partner_type",
            "allowed_types": sorted(ALLOWED_PARTNER_TYPES)
        }), 400

    # ---------------------------------------------------------
    # Basic phone validation
    # ---------------------------------------------------------

    allowed_phone_characters = set(
        "0123456789+()- "
    )

    if not all(
        character in allowed_phone_characters
        for character in phone
    ):
        return jsonify({
            "error": "Invalid phone number"
        }), 400

    # ---------------------------------------------------------
    # Existing account check
    # ---------------------------------------------------------

    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:
        return jsonify({
            "error": "An account already exists for this email"
        }), 409

    # ---------------------------------------------------------
    # Existing application check
    # ---------------------------------------------------------

    existing_application = Application.query.filter_by(
        email=email
    ).order_by(
        Application.created_at.desc()
    ).first()

    if existing_application:

        if existing_application.status in {
            "pending",
            "approved"
        }:
            return jsonify({
                "error": "An application already exists for this email",
                "status": existing_application.status
            }), 409

        # Rejected applications are allowed to reapply.

    # ---------------------------------------------------------
    # Create application
    # ---------------------------------------------------------

    application = Application(
        full_name=full_name,
        position=position,
        email=email,
        phone=phone,
        company_name=company_name,
        services_offered=services_offered,
        partner_type=partner_type,
        status="pending"
    )

    db.session.add(application)
    db.session.commit()

    return jsonify({
        "message": "Partner application submitted successfully",
        "application": {
            "id": application.id,
            "status": application.status,
            "created_at": application.created_at.isoformat()
        }
    }), 201