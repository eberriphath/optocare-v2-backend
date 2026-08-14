from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models import Partner, Service, Product
from app.utils.decorators import partner_required
from app.utils.security import hash_password, check_password



partner_bp = Blueprint(
    "partner",
    __name__,
    url_prefix="/api/partner"
)


@partner_bp.route("/profile", methods=["GET"])
@partner_required
def get_profile():

    user = request.current_user
    partner = user.partner

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
    partner = user.partner

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    allowed_fields = {
        "location",
        "specialty",
        "description"
    }

    for field in data:
        if field not in allowed_fields:
            return jsonify({
                "error": f"You cannot update '{field}'"
            }), 400

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


@partner_bp.route("/services", methods=["GET"])
@partner_required
def get_services():

    partner = request.current_user.partner

    services = Service.query.filter_by(
        partner_id=partner.id
    ).order_by(
        Service.created_at.desc()
    ).all()

    return jsonify({
        "services": [
            {
                "id": service.id,
                "name": service.name,
                "description": service.description,
                "category": service.category,
                "price": float(service.price)
                if service.price is not None
                else None,
                "is_active": service.is_active,
                "created_at": service.created_at.isoformat(),
                "updated_at": service.updated_at.isoformat()
            }
            for service in services
        ]
    }), 200


@partner_bp.route("/services", methods=["POST"])
@partner_required
def create_service():

    partner = request.current_user.partner

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    name = data.get("name")

    if not name:
        return jsonify({
            "error": "Service name is required"
        }), 400

    name = name.strip()

    if not name:
        return jsonify({
            "error": "Service name cannot be empty"
        }), 400

    service = Service(
        partner_id=partner.id,
        name=name,
        description=data.get("description"),
        category=data.get("category"),
        price=data.get("price"),
        is_active=data.get("is_active", True)
    )

    db.session.add(service)
    db.session.commit()

    return jsonify({
        "message": "Service created successfully",
        "service": {
            "id": service.id,
            "name": service.name,
            "description": service.description,
            "category": service.category,
            "price": float(service.price)
            if service.price is not None
            else None,
            "is_active": service.is_active,
            "created_at": service.created_at.isoformat(),
            "updated_at": service.updated_at.isoformat()
        }
    }), 201

@partner_bp.route("/services/<int:service_id>", methods=["PATCH"])
@partner_required
def update_service(service_id):

    partner = request.current_user.partner

    service = Service.query.filter_by(
        id=service_id,
        partner_id=partner.id
    ).first()

    if not service:
        return jsonify({
            "error": "Service not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    allowed_fields = {
        "name",
        "description",
        "category",
        "price",
        "is_active"
    }

    for field in data:
        if field not in allowed_fields:
            return jsonify({
                "error": f"You cannot update '{field}'"
            }), 400

    if "name" in data:
        name = data["name"]

        if not isinstance(name, str) or not name.strip():
            return jsonify({
                "error": "Service name cannot be empty"
            }), 400

        service.name = name.strip()

    if "description" in data:
        service.description = data["description"]

    if "category" in data:
        service.category = data["category"]

    if "price" in data:
        service.price = data["price"]

    if "is_active" in data:
        service.is_active = data["is_active"]

    db.session.commit()

    return jsonify({
        "message": "Service updated successfully",
        "service": {
            "id": service.id,
            "name": service.name,
            "description": service.description,
            "category": service.category,
            "price": float(service.price)
            if service.price is not None
            else None,
            "is_active": service.is_active,
            "created_at": service.created_at.isoformat(),
            "updated_at": service.updated_at.isoformat()
        }
    }), 200


@partner_bp.route("/services/<int:service_id>", methods=["DELETE"])
@partner_required
def delete_service(service_id):

    partner = request.current_user.partner

    service = Service.query.filter_by(
        id=service_id,
        partner_id=partner.id
    ).first()

    if not service:
        return jsonify({
            "error": "Service not found"
        }), 404

    db.session.delete(service)
    db.session.commit()

    return jsonify({
        "message": "Service deleted successfully"
    }), 200

@partner_bp.route("/products", methods=["GET"])
@partner_required
def get_products():

    partner = request.current_user.partner

    products = Product.query.filter_by(
        partner_id=partner.id
    ).order_by(
        Product.created_at.desc()
    ).all()

    return jsonify({
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
                "is_available": product.is_available,
                "image_url": product.image_url,
                "created_at": product.created_at.isoformat(),
                "updated_at": product.updated_at.isoformat()
            }
            for product in products
        ]
    }), 200


@partner_bp.route("/products", methods=["POST"])
@partner_required
def create_product():

    partner = request.current_user.partner

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    name = data.get("name")

    if not name:
        return jsonify({
            "error": "Product name is required"
        }), 400

    if not isinstance(name, str) or not name.strip():
        return jsonify({
            "error": "Product name cannot be empty"
        }), 400

    stock_quantity = data.get("stock_quantity", 0)

    if not isinstance(stock_quantity, int) or stock_quantity < 0:
        return jsonify({
            "error": "Stock quantity must be a non-negative integer"
        }), 400

    price = data.get("price")

    if price is not None:
        try:
            price = float(price)
        except (TypeError, ValueError):
            return jsonify({
                "error": "Price must be a valid number"
            }), 400

        if price < 0:
            return jsonify({
                "error": "Price cannot be negative"
            }), 400

    product = Product(
        partner_id=partner.id,
        name=name.strip(),
        description=data.get("description"),
        category=data.get("category"),
        brand=data.get("brand"),
        price=price,
        stock_quantity=stock_quantity,
        is_available=data.get("is_available", True),
        image_url=data.get("image_url")
    )

    db.session.add(product)
    db.session.commit()

    return jsonify({
        "message": "Product created successfully",
        "product": {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "category": product.category,
            "brand": product.brand,
            "price": float(product.price)
            if product.price is not None
            else None,
            "stock_quantity": product.stock_quantity,
            "is_available": product.is_available,
            "image_url": product.image_url,
            "created_at": product.created_at.isoformat(),
            "updated_at": product.updated_at.isoformat()
        }
    }), 201


@partner_bp.route("/products/<int:product_id>", methods=["PATCH"])
@partner_required
def update_product(product_id):

    partner = request.current_user.partner

    product = Product.query.filter_by(
        id=product_id,
        partner_id=partner.id
    ).first()

    if not product:
        return jsonify({
            "error": "Product not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    allowed_fields = {
        "name",
        "description",
        "category",
        "brand",
        "price",
        "stock_quantity",
        "is_available",
        "image_url"
    }

    for field in data:
        if field not in allowed_fields:
            return jsonify({
                "error": f"You cannot update '{field}'"
            }), 400

    if "name" in data:
        name = data["name"]

        if not isinstance(name, str) or not name.strip():
            return jsonify({
                "error": "Product name cannot be empty"
            }), 400

        product.name = name.strip()

    if "description" in data:
        product.description = data["description"]

    if "category" in data:
        product.category = data["category"]

    if "brand" in data:
        product.brand = data["brand"]

    if "price" in data:
        price = data["price"]

        if price is not None:
            try:
                price = float(price)
            except (TypeError, ValueError):
                return jsonify({
                    "error": "Price must be a valid number"
                }), 400

            if price < 0:
                return jsonify({
                    "error": "Price cannot be negative"
                }), 400

        product.price = price

    if "stock_quantity" in data:
        stock_quantity = data["stock_quantity"]

        if (
            not isinstance(stock_quantity, int)
            or stock_quantity < 0
        ):
            return jsonify({
                "error": "Stock quantity must be a non-negative integer"
            }), 400

        product.stock_quantity = stock_quantity

    if "is_available" in data:
        if not isinstance(data["is_available"], bool):
            return jsonify({
                "error": "is_available must be true or false"
            }), 400

        product.is_available = data["is_available"]

    if "image_url" in data:
        product.image_url = data["image_url"]

    db.session.commit()

    return jsonify({
        "message": "Product updated successfully",
        "product": {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "category": product.category,
            "brand": product.brand,
            "price": float(product.price)
            if product.price is not None
            else None,
            "stock_quantity": product.stock_quantity,
            "is_available": product.is_available,
            "image_url": product.image_url,
            "created_at": product.created_at.isoformat(),
            "updated_at": product.updated_at.isoformat()
        }
    }), 200


@partner_bp.route("/products/<int:product_id>", methods=["DELETE"])
@partner_required
def delete_product(product_id):

    partner = request.current_user.partner

    product = Product.query.filter_by(
        id=product_id,
        partner_id=partner.id
    ).first()

    if not product:
        return jsonify({
            "error": "Product not found"
        }), 404

    db.session.delete(product)
    db.session.commit()

    return jsonify({
        "message": "Product deleted successfully"
    }), 200


@partner_bp.route("/password", methods=["PATCH"])
@partner_required
def change_password():

    user = request.current_user

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    current_password = data.get("current_password")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if not current_password:
        return jsonify({
            "error": "Current password is required"
        }), 400

    if not new_password:
        return jsonify({
            "error": "New password is required"
        }), 400

    if not confirm_password:
        return jsonify({
            "error": "Password confirmation is required"
        }), 400

    if not check_password(
        current_password,
        user.password_hash
    ):
        return jsonify({
            "error": "Current password is incorrect"
        }), 401

    if len(new_password) < 8:
        return jsonify({
            "error": "New password must be at least 8 characters"
        }), 400

    if new_password != confirm_password:
        return jsonify({
            "error": "New passwords do not match"
        }), 400

    if check_password(
        new_password,
        user.password_hash
    ):
        return jsonify({
            "error": "New password must be different from current password"
        }), 400

    user.password_hash = hash_password(new_password)

    db.session.commit()

    return jsonify({
        "message": "Password changed successfully"
    }), 200


@partner_bp.route("/dashboard", methods=["GET"])
@partner_required
def get_dashboard():

    user = request.current_user
    partner = user.partner

    total_services = Service.query.filter_by(
        partner_id=partner.id
    ).count()

    active_services = Service.query.filter_by(
        partner_id=partner.id,
        is_active=True
    ).count()

    total_products = Product.query.filter_by(
        partner_id=partner.id
    ).count()

    available_products = Product.query.filter_by(
        partner_id=partner.id,
        is_available=True
    ).count()

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
            "is_verified": partner.is_verified
        },
        "statistics": {
            "total_services": total_services,
            "active_services": active_services,
            "total_products": total_products,
            "available_products": available_products
        }
    }), 200