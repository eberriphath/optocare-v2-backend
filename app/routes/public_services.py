from flask import Blueprint, jsonify, request

from app.models import Service, Partner


public_services_bp = Blueprint(
    "public_services",
    __name__,
    url_prefix="/api/services"
)


def public_service_query():
    return (
        Service.query
        .join(Service.partner)
        .join(Partner.user)
        .filter(
            Service.is_active.is_(True),
            Partner.is_verified.is_(True),
            Partner.user.has(is_active=True)
        )
    )


@public_services_bp.route("", methods=["GET"])
def get_public_services():
    """
    Return active services belonging to verified and active partners.
    """

    query = public_service_query()

    category = request.args.get("category", type=str)
    search = request.args.get("search", type=str)

    if category:
        category = category.strip()
        if category:
            query = query.filter(Service.category.ilike(category))

    if search:
        search = search.strip()
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                Service.name.ilike(search_pattern)
                | Service.description.ilike(search_pattern)
            )

    services = query.order_by(Service.name.asc()).all()

    return jsonify({
        "services": [
            {
                "id": service.id,
                "name": service.name,
                "description": service.description,
                "category": service.category,
                "price": float(service.price) if service.price is not None else None,
                "partner": {
                    "id": service.partner.id,
                    "company_name": service.partner.company_name,
                    "location": service.partner.location,
                    "specialty": service.partner.specialty,
                }
            }
            for service in services
        ]
    }), 200


@public_services_bp.route("/<int:service_id>", methods=["GET"])
def get_public_service(service_id):
    """
    Return one active service belonging to a verified and active partner.
    """

    service = (
        public_service_query()
        .filter(Service.id == service_id)
        .first()
    )

    if not service:
        return jsonify({
            "error": "Service not found"
        }), 404

    return jsonify({
        "service": {
            "id": service.id,
            "name": service.name,
            "description": service.description,
            "category": service.category,
            "price": float(service.price) if service.price is not None else None,
            "partner": {
                "id": service.partner.id,
                "company_name": service.partner.company_name,
                "partner_type": service.partner.partner_type,
                "location": service.partner.location,
                "specialty": service.partner.specialty,
                "description": service.partner.description,
                "is_verified": service.partner.is_verified,
            }
        }
    }), 200
