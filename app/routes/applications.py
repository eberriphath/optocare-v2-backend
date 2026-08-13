from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models import Application


applications_bp = Blueprint(
    "applications",
    __name__,
    url_prefix="/api/applications"
)


@applications_bp.route("", methods=["POST"])
def create_application():
    data = request.get_json()

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
        field for field in required_fields
        if not data.get(field)
    ]

    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing_fields
        }), 400

    application = Application(
        full_name=data["full_name"].strip(),
        position=data["position"].strip(),
        email=data["email"].strip().lower(),
        phone=data["phone"].strip(),
        company_name=data["company_name"].strip(),
        services_offered=data["services_offered"].strip(),
        partner_type=data["partner_type"].strip()
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