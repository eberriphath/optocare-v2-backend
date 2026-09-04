from flask import Blueprint, jsonify, request

from app.models import Product, Partner


public_products_bp = Blueprint(
    "public_products",
    __name__,
    url_prefix="/api/products"
)


def public_product_query():
    return (
        Product.query
        .join(Product.partner)
        .join(Partner.user)
        .filter(
            Product.is_available.is_(True),
            Partner.is_verified.is_(True),
            Partner.user.has(is_active=True)
        )
    )


@public_products_bp.route("", methods=["GET"])
def get_public_products():
    """
    Return available products belonging to verified and active partners.
    """

    query = public_product_query()

    category = request.args.get("category", type=str)
    brand = request.args.get("brand", type=str)
    search = request.args.get("search", type=str)

    if category:
        category = category.strip()
        if category:
            query = query.filter(Product.category.ilike(category))

    if brand:
        brand = brand.strip()
        if brand:
            query = query.filter(Product.brand.ilike(brand))

    if search:
        search = search.strip()
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                Product.name.ilike(search_pattern)
                | Product.description.ilike(search_pattern)
                | Product.brand.ilike(search_pattern)
            )

    products = query.order_by(Product.name.asc()).all()

    return jsonify({
        "products": [
            {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "category": product.category,
                "brand": product.brand,
                "price": float(product.price) if product.price is not None else None,
                "stock_quantity": product.stock_quantity,
                "image_url": product.image_url,
                "partner": {
                    "id": product.partner.id,
                    "company_name": product.partner.company_name,
                    "location": product.partner.location,
                    "specialty": product.partner.specialty,
                }
            }
            for product in products
        ]
    }), 200


@public_products_bp.route("/<int:product_id>", methods=["GET"])
def get_public_product(product_id):
    """
    Return one available product belonging to a verified and active partner.
    """

    product = (
        public_product_query()
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        return jsonify({
            "error": "Product not found"
        }), 404

    return jsonify({
        "product": {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "category": product.category,
            "brand": product.brand,
            "price": float(product.price) if product.price is not None else None,
            "stock_quantity": product.stock_quantity,
            "image_url": product.image_url,
            "partner": {
                "id": product.partner.id,
                "company_name": product.partner.company_name,
                "partner_type": product.partner.partner_type,
                "location": product.partner.location,
                "specialty": product.partner.specialty,
                "description": product.partner.description,
                "is_verified": product.partner.is_verified,
            }
        }
    }), 200
