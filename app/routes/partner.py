from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Partner
from app.utils.decorators import partner_required


partner_bp = Blueprint(
    "partner",
    __name__,
    url_prefix="/api/partner"
)


@partner_bp.route("/profile", methods=["GET"])
@partner_required
def get_profile():

    user = request.current_user

    partner = Partner.query.filter_by(
        user_id=user.id
    ).first()

    if not partner:
        return jsonify({
            "error": "Partner profile not found"
        }), 404

    return jsonify({
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        },
        "partner": {
            "id": partner.id,
            "company_name": partner.company_name,
            "partner_type": partner.partner_type,
            "location": partner.location,
            "specialty": partner.specialty,
            "description": partner.description,
            "is_verified": partner.is_verified,
            "created_at": partner.created_at.isoformat()
        }
    }), 200


@partner_bp.route("/profile", methods=["PATCH"])
@partner_required
def update_profile():

    user = request.current_user

    partner = Partner.query.filter_by(
        user_id=user.id
    ).first()

    if not partner:
        return jsonify({
            "error": "Partner profile not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    allowed_fields = {
        "company_name",
        "location",
        "specialty",
        "description"
    }

    for field in data:
        if field not in allowed_fields:
            return jsonify({
                "error": f"You cannot update '{field}'"
            }), 400

    if "company_name" in data:
        company_name = data["company_name"]

        if not isinstance(company_name, str) or not company_name.strip():
            return jsonify({
                "error": "company_name must be a non-empty string"
            }), 400

        partner.company_name = company_name.strip()

    if "location" in data:
        partner.location = data["location"]

    if "specialty" in data:
        partner.specialty = data["specialty"]

    if "description" in data:
        partner.description = data["description"]

    db.session.commit()

    return jsonify({
        "message": "Partner profile updated successfully",
        "partner": {
            "id": partner.id,
            "company_name": partner.company_name,
            "partner_type": partner.partner_type,
            "location": partner.location,
            "specialty": partner.specialty,
            "description": partner.description,
            "is_verified": partner.is_verified,
            "created_at": partner.created_at.isoformat()
        }
    }), 200