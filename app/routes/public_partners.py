from flask import Blueprint, jsonify, request

from app.models import Partner, Service, Product


public_partners_bp = Blueprint(
    "public_partners",
    __name__,
    url_prefix="/api/partners"
)


@public_partners_bp.route("", methods=["GET"])
def get_partners():

    location = request.args.get("location")
    specialty = request.args.get("specialty")
    partner_type = request.args.get("partner_type")

    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
    except ValueError:
        return jsonify({
            "error": "page and per_page must be integers"
        }), 400

    if page < 1:
        return jsonify({
            "error": "page must be at least 1"
        }), 400

    if per_page < 1 or per_page > 100:
        return jsonify({
            "error": "per_page must be between 1 and 100"
        }), 400

    query = Partner.query.filter_by(
        is_verified=True
    )

    if location:
        query = query.filter(
            Partner.location.ilike(f"%{location}%")
        )

    if specialty:
        query = query.filter(
            Partner.specialty.ilike(f"%{specialty}%")
        )

    if partner_type:
        query = query.filter(
            Partner.partner_type.ilike(f"%{partner_type}%")
        )

    pagination = query.order_by(
        Partner.company_name.asc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        "filters": {
            "location": location,
            "specialty": specialty,
            "partner_type": partner_type
        },
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_previous": pagination.has_prev
        },
        "partners": [
            {
                "id": partner.id,
                "company_name": partner.company_name,
                "partner_type": partner.partner_type,
                "location": partner.location,
                "specialty": partner.specialty,
                "description": partner.description,
                "is_verified": partner.is_verified
            }
            for partner in pagination.items
        ]
    }), 200


@public_partners_bp.route("/<int:partner_id>", methods=["GET"])
def get_partner(partner_id):

    partner = Partner.query.filter_by(
        id=partner_id,
        is_verified=True
    ).first()

    if not partner:
        return jsonify({
            "error": "Partner not found"
        }), 404

    return jsonify({
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

@public_partners_bp.route("/<int:partner_id>/services", methods=["GET"])
def get_partner_services(partner_id):

    partner = Partner.query.filter_by(
        id=partner_id,
        is_verified=True
    ).first()

    if not partner:
        return jsonify({
            "error": "Partner not found"
        }), 404

    services = Service.query.filter_by(
        partner_id=partner.id,
        is_active=True
    ).order_by(
        Service.created_at.desc()
    ).all()

    return jsonify({
        "partner": {
            "id": partner.id,
            "company_name": partner.company_name
        },
        "services": [
            {
                "id": service.id,
                "name": service.name,
                "description": service.description,
                "category": service.category,
                "price": float(service.price)
                if service.price is not None
                else None
            }
            for service in services
        ]
    }), 200

@public_partners_bp.route("/<int:partner_id>/products", methods=["GET"])
def get_partner_products(partner_id):

    partner = Partner.query.filter_by(
        id=partner_id,
        is_verified=True
    ).first()

    if not partner:
        return jsonify({
            "error": "Partner not found"
        }), 404

    products = Product.query.filter_by(
        partner_id=partner.id,
        is_available=True
    ).order_by(
        Product.created_at.desc()
    ).all()

    return jsonify({
        "partner": {
            "id": partner.id,
            "company_name": partner.company_name
        },
        "products": [
            {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "category": product.category,
                "brand": product.brand,
                "price": float(product.price)
                if product.price is not None
                else None,
                "stock_quantity": product.stock_quantity,
                "image_url": product.image_url
            }
            for product in products
        ]
    }), 200
