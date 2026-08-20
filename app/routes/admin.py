from flask import Blueprint, jsonify, request, current_app
from datetime import datetime, timezone, timedelta

from app.models import (
    Application, User, Partner, Review, Service, Product
)
from app.utils.tokens import generate_activation_token
from app.utils.decorators import admin_required
from app.utils.security import hash_password
from app.extensions import db

from app.services.email_service import (
    send_application_approved_email,
    send_application_rejected_email,
)
import secrets



admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/api/admin"
)


@admin_bp.route("/applications", methods=["GET"])
@admin_required
def get_applications():
    applications = Application.query.order_by(
        Application.created_at.desc()
    ).all()

    return jsonify({
        "applications": [
            {
                "id": application.id,
                "full_name": application.full_name,
                "position": application.position,
                "email": application.email,
                "phone": application.phone,
                "company_name": application.company_name,
                "services_offered": application.services_offered,
                "partner_type": application.partner_type,
                "document_path": application.document_path,
                "status": application.status,
                "reviewed_by": application.reviewed_by,
                "review_notes": application.review_notes,
                "reviewed_at": (
                    application.reviewed_at.isoformat()
                    if application.reviewed_at
                    else None
                ),
                "created_at": application.created_at.isoformat()
            }
            for application in applications
        ]
    }), 200


@admin_bp.route("/applications/<int:application_id>", methods=["GET"])
@admin_required
def get_application(application_id):
    application = Application.query.get(application_id)

    if not application:
        return jsonify({
            "error": "Application not found"
        }), 404

    return jsonify({
        "application": {
            "id": application.id,
            "full_name": application.full_name,
            "position": application.position,
            "email": application.email,
            "phone": application.phone,
            "company_name": application.company_name,
            "services_offered": application.services_offered,
            "partner_type": application.partner_type,
            "document_path": application.document_path,
            "status": application.status,
            "reviewed_by": application.reviewed_by,
            "review_notes": application.review_notes,
            "reviewed_at": (
                application.reviewed_at.isoformat()
                if application.reviewed_at
                else None
            ),
            "created_at": application.created_at.isoformat()
        }
    }), 200

@admin_bp.route(
    "/applications/<int:application_id>/approve",
    methods=["PATCH"]
)
@admin_required
def approve_application(application_id):

    application = Application.query.get(application_id)

    if not application:
        return jsonify({
            "error": "Application not found"
        }), 404

    if application.status != "pending":
        return jsonify({
            "error": "Only pending applications can be approved"
        }), 400

    admin = request.current_user

    # Check whether an account already exists
    existing_user = User.query.filter_by(
        email=application.email.lower()
    ).first()

    if existing_user:
        return jsonify({
            "error": "A user account already exists for this email"
        }), 409

    # Generate a temporary random password.
    # The partner will replace it through activation.
    temporary_password = secrets.token_urlsafe(32)

    user = User(
        name=application.full_name,
        email=application.email.lower(),
        password_hash=hash_password(temporary_password),
        role="partner",
        is_active=False,
        must_set_password=True
    )

    db.session.add(user)
    db.session.flush()

    partner = Partner(
        user_id=user.id,
        company_name=application.company_name,
        location=None,
        specialty=None,
        partner_type=application.partner_type,
        description=application.services_offered,
        is_verified=True
    )

    db.session.add(partner)

    # Generate activation token
    activation_token = secrets.token_urlsafe(48)

    application.status = "approved"
    application.reviewed_by = admin.id
    application.reviewed_at = datetime.now(timezone.utc)
    application.review_notes = None
    application.user_id = user.id
    application.activation_token = activation_token
    application.activation_expires_at = (
        datetime.now(timezone.utc) + timedelta(hours=48)
    )

    db.session.commit()

    # ---------------------------------------------------------
    # Approval email notification
    # ---------------------------------------------------------

    try:
        activation_base_url = current_app.config.get(
            "ACTIVATION_URL"
        )

        if activation_base_url:
            activation_url = (
                f"{activation_base_url}"
                f"?token={activation_token}"
            )

            send_application_approved_email(
                recipient=application.email,
                name=application.full_name,
                activation_url=activation_url
            )

    except Exception:
        current_app.logger.exception(
            "Failed to send application approval email "
            "for application %s",
            application.id
        )

    return jsonify({
        "message": "Application approved successfully",

        "application": {
            "id": application.id,
            "status": application.status
        },

        "activation": {
            "token": activation_token,
            "expires_at": application.activation_expires_at.isoformat()
        },

        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "must_set_password": user.must_set_password
        },

        "partner": {
            "id": partner.id,
            "company_name": partner.company_name,
            "partner_type": partner.partner_type
        }
    }), 200

@admin_bp.route("/applications/<int:application_id>/reject", methods=["PATCH"])
@admin_required
def reject_application(application_id):
    application = Application.query.get(application_id)

    if not application:
        return jsonify({
            "error": "Application not found"
        }), 404

    if application.status != "pending":
        return jsonify({
            "error": "Only pending applications can be rejected"
        }), 400

    data = request.get_json() or {}

    review_notes = data.get("review_notes")

    if not review_notes or not review_notes.strip():
        return jsonify({
            "error": "Review notes are required when rejecting an application"
        }), 400

    admin = request.current_user

    application.status = "rejected"
    application.reviewed_by = admin.id
    application.reviewed_at = datetime.now(timezone.utc)
    application.review_notes = review_notes.strip()

    db.session.commit()

    return jsonify({
        "message": "Application rejected successfully",
        "application": {
            "id": application.id,
            "status": application.status,
            "reviewed_by": application.reviewed_by,
            "reviewed_at": application.reviewed_at.isoformat(),
            "review_notes": application.review_notes
        }
    }), 200

@admin_bp.route("/partners", methods=["GET"])
@admin_required
def get_partners():

    partners = Partner.query.order_by(
        Partner.company_name.asc()
    ).all()

    return jsonify({
        "partners": [
            {
                "id": partner.id,
                "company_name": partner.company_name,
                "partner_type": partner.partner_type,
                "location": partner.location,
                "specialty": partner.specialty,
                "description": partner.description,
                "is_verified": partner.is_verified,
                "created_at": partner.created_at.isoformat(),

                "user": {
                    "id": partner.user.id,
                    "name": partner.user.name,
                    "email": partner.user.email,
                    "role": partner.user.role,
                    "is_active": partner.user.is_active,
                    "must_set_password": partner.user.must_set_password
                }
            }
            for partner in partners
        ]
    }), 200


@admin_bp.route("/partners/<int:partner_id>", methods=["GET"])
@admin_required
def get_partner(partner_id):

    partner = Partner.query.get(partner_id)

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
            "created_at": partner.created_at.isoformat(),

            "user": {
                "id": partner.user.id,
                "name": partner.user.name,
                "email": partner.user.email,
                "role": partner.user.role,
                "is_active": partner.user.is_active,
                "must_set_password": partner.user.must_set_password,
                "created_at": partner.user.created_at.isoformat()
            }
        }
    }), 200


@admin_bp.route(
    "/partners/<int:partner_id>/status",
    methods=["PATCH"]
)
@admin_required
def update_partner_status(partner_id):

    partner = Partner.query.get(partner_id)

    if not partner:
        return jsonify({
            "error": "Partner not found"
        }), 404

    user = partner.user

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    if "is_active" not in data:
        return jsonify({
            "error": "'is_active' is required"
        }), 400

    if not isinstance(data["is_active"], bool):
        return jsonify({
            "error": "'is_active' must be true or false"
        }), 400

    user.is_active = data["is_active"]

    db.session.commit()

    return jsonify({
        "message": (
            "Partner activated successfully"
            if user.is_active
            else "Partner deactivated successfully"
        ),
        "partner": {
            "id": partner.id,
            "company_name": partner.company_name,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "is_active": user.is_active,
                "must_set_password": user.must_set_password
            }
        }
    }), 200


@admin_bp.route(
    "/partners/<int:partner_id>/verification",
    methods=["PATCH"]
)
@admin_required
def update_partner_verification(partner_id):

    partner = Partner.query.get(partner_id)

    if not partner:
        return jsonify({
            "error": "Partner not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    if "is_verified" not in data:
        return jsonify({
            "error": "'is_verified' is required"
        }), 400

    if not isinstance(data["is_verified"], bool):
        return jsonify({
            "error": "'is_verified' must be true or false"
        }), 400

    partner.is_verified = data["is_verified"]

    db.session.commit()

    return jsonify({
        "message": (
            "Partner verified successfully"
            if partner.is_verified
            else "Partner verification removed successfully"
        ),
        "partner": {
            "id": partner.id,
            "company_name": partner.company_name,
            "is_verified": partner.is_verified
        }
    }), 200


# =========================================================
# SERVICES
# =========================================================

@admin_bp.route("/services", methods=["GET"])
@admin_required
def get_services():

    services = Service.query.order_by(
        Service.created_at.desc()
    ).all()

    return jsonify({
        "services": [
            {
                "id": service.id,
                "name": service.name,
                "description": service.description,
                "category": service.category,
                "price": (
                    float(service.price)
                    if service.price is not None
                    else None
                ),
                "is_active": service.is_active,
                "created_at": service.created_at.isoformat(),
                "updated_at": service.updated_at.isoformat(),

                "partner": {
                    "id": service.partner.id,
                    "company_name": service.partner.company_name,

                    "user": {
                        "id": service.partner.user.id,
                        "name": service.partner.user.name,
                        "email": service.partner.user.email
                    }
                }
            }
            for service in services
        ]
    }), 200


@admin_bp.route("/services/<int:service_id>", methods=["GET"])
@admin_required
def get_service(service_id):

    service = Service.query.get(service_id)

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
            "price": (
                float(service.price)
                if service.price is not None
                else None
            ),
            "is_active": service.is_active,
            "created_at": service.created_at.isoformat(),
            "updated_at": service.updated_at.isoformat(),

            "partner": {
                "id": service.partner.id,
                "company_name": service.partner.company_name,
                "partner_type": service.partner.partner_type,

                "user": {
                    "id": service.partner.user.id,
                    "name": service.partner.user.name,
                    "email": service.partner.user.email
                }
            }
        }
    }), 200


@admin_bp.route(
    "/services/<int:service_id>/status",
    methods=["PATCH"]
)
@admin_required
def update_service_status(service_id):

    service = Service.query.get(service_id)

    if not service:
        return jsonify({
            "error": "Service not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    if "is_active" not in data:
        return jsonify({
            "error": "'is_active' is required"
        }), 400

    if not isinstance(data["is_active"], bool):
        return jsonify({
            "error": "'is_active' must be true or false"
        }), 400

    service.is_active = data["is_active"]

    db.session.commit()

    return jsonify({
        "message": (
            "Service activated successfully"
            if service.is_active
            else "Service deactivated successfully"
        ),
        "service": {
            "id": service.id,
            "name": service.name,
            "is_active": service.is_active
        }
    }), 200


# =========================================================
# PRODUCTS
# =========================================================

@admin_bp.route("/products", methods=["GET"])
@admin_required
def get_products():

    products = Product.query.order_by(
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
                "price": (
                    float(product.price)
                    if product.price is not None
                    else None
                ),
                "stock_quantity": product.stock_quantity,
                "is_available": product.is_available,
                "image_url": product.image_url,
                "created_at": product.created_at.isoformat(),
                "updated_at": product.updated_at.isoformat(),

                "partner": {
                    "id": product.partner.id,
                    "company_name": product.partner.company_name,

                    "user": {
                        "id": product.partner.user.id,
                        "name": product.partner.user.name,
                        "email": product.partner.user.email
                    }
                }
            }
            for product in products
        ]
    }), 200


@admin_bp.route("/products/<int:product_id>", methods=["GET"])
@admin_required
def get_product(product_id):

    product = Product.query.get(product_id)

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
            "price": (
                float(product.price)
                if product.price is not None
                else None
            ),
            "stock_quantity": product.stock_quantity,
            "is_available": product.is_available,
            "image_url": product.image_url,
            "created_at": product.created_at.isoformat(),
            "updated_at": product.updated_at.isoformat(),

            "partner": {
                "id": product.partner.id,
                "company_name": product.partner.company_name,
                "partner_type": product.partner.partner_type,

                "user": {
                    "id": product.partner.user.id,
                    "name": product.partner.user.name,
                    "email": product.partner.user.email
                }
            }
        }
    }), 200


@admin_bp.route(
    "/products/<int:product_id>/availability",
    methods=["PATCH"]
)
@admin_required
def update_product_availability(product_id):

    product = Product.query.get(product_id)

    if not product:
        return jsonify({
            "error": "Product not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    if "is_available" not in data:
        return jsonify({
            "error": "'is_available' is required"
        }), 400

    if not isinstance(data["is_available"], bool):
        return jsonify({
            "error": "'is_available' must be true or false"
        }), 400

    product.is_available = data["is_available"]

    db.session.commit()

    return jsonify({
        "message": (
            "Product marked as available"
            if product.is_available
            else "Product marked as unavailable"
        ),
        "product": {
            "id": product.id,
            "name": product.name,
            "is_available": product.is_available
        }
    }), 200


@admin_bp.route("/reviews", methods=["GET"])
@admin_required
def get_reviews():

    reviews = Review.query.order_by(
        Review.created_at.desc()
    ).all()

    return jsonify({
        "reviews": [
            {
                "id": review.id,
                "partner_id": review.partner_id,
                "user_id": review.user_id,
                "reviewer_name": review.reviewer_name,
                "reviewer_email": review.reviewer_email,
                "rating": review.rating,
                "comment": review.comment,
                "is_approved": review.is_approved,
                "admin_notes": review.admin_notes,
                "created_at": review.created_at.isoformat(),
                "updated_at": review.updated_at.isoformat()
            }
            for review in reviews
        ]
    }), 200


@admin_bp.route("/reviews/<int:review_id>", methods=["GET"])
@admin_required
def get_review(review_id):

    review = Review.query.get(review_id)

    if not review:
        return jsonify({
            "error": "Review not found"
        }), 404

    return jsonify({
        "review": {
            "id": review.id,
            "partner_id": review.partner_id,
            "user_id": review.user_id,
            "reviewer_name": review.reviewer_name,
            "reviewer_email": review.reviewer_email,
            "rating": review.rating,
            "comment": review.comment,
            "is_approved": review.is_approved,
            "admin_notes": review.admin_notes,
            "created_at": review.created_at.isoformat(),
            "updated_at": review.updated_at.isoformat()
        }
    }), 200


@admin_bp.route(
    "/reviews/<int:review_id>",
    methods=["PATCH"]
)
@admin_required
def moderate_review(review_id):

    review = Review.query.get(review_id)

    if not review:
        return jsonify({
            "error": "Review not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    allowed_fields = {
        "is_approved",
        "admin_notes"
    }

    for field in data:
        if field not in allowed_fields:
            return jsonify({
                "error": f"You cannot update '{field}'"
            }), 400

    if "is_approved" in data:

        if not isinstance(data["is_approved"], bool):
            return jsonify({
                "error": "'is_approved' must be true or false"
            }), 400

        review.is_approved = data["is_approved"]

    if "admin_notes" in data:

        admin_notes = data["admin_notes"]

        if admin_notes is not None and not isinstance(
            admin_notes,
            str
        ):
            return jsonify({
                "error": "'admin_notes' must be a string or null"
            }), 400

        if isinstance(admin_notes, str):
            admin_notes = admin_notes.strip()

            if len(admin_notes) > 2000:
                return jsonify({
                    "error": "Admin notes must not exceed 2000 characters"
                }), 400

        review.admin_notes = admin_notes

    db.session.commit()

    return jsonify({
        "message": "Review updated successfully",
        "review": {
            "id": review.id,
            "partner_id": review.partner_id,
            "reviewer_name": review.reviewer_name,
            "rating": review.rating,
            "comment": review.comment,
            "is_approved": review.is_approved,
            "admin_notes": review.admin_notes,
            "updated_at": review.updated_at.isoformat()
        }
    }), 200

@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def get_dashboard():

    total_users = User.query.count()

    total_partners = Partner.query.count()

    active_partners = Partner.query.join(
        User,
        Partner.user_id == User.id
    ).filter(
        User.is_active.is_(True)
    ).count()

    verified_partners = Partner.query.filter_by(
        is_verified=True
    ).count()

    pending_applications = Application.query.filter_by(
        status="pending"
    ).count()

    approved_applications = Application.query.filter_by(
        status="approved"
    ).count()

    rejected_applications = Application.query.filter_by(
        status="rejected"
    ).count()

    total_products = Product.query.count()

    total_services = Service.query.count()

    pending_reviews = Review.query.filter_by(
        is_approved=False
    ).count()

    approved_reviews = Review.query.filter_by(
        is_approved=True
    ).count()

    return jsonify({
        "statistics": {
            "total_users": total_users,
            "total_partners": total_partners,
            "active_partners": active_partners,
            "verified_partners": verified_partners,
            "pending_applications": pending_applications,
            "approved_applications": approved_applications,
            "rejected_applications": rejected_applications,
            "total_products": total_products,
            "total_services": total_services,
            "pending_reviews": pending_reviews,
            "approved_reviews": approved_reviews
        }
    }), 200