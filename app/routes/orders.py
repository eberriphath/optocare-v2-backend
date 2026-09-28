from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Client, Order, Prescription, Partner
from app.utils.decorators import admin_required
from app.utils.number_generator import ( 
    generate_order_number,
    generate_client_number
)


orders_bp = Blueprint(
    "orders",
    __name__,
    url_prefix="/api/orders"
)


ORDER_STATUSES = {
    "submitted",
    "under_review",
    "confirmed",
    "processing",
    "ready",
    "completed",
}


def serialize_order(order):
    return {
        "id": order.id,
        "order_number": order.order_number,

        "client": {
            "id": order.client.id,
            "client_number": order.client.client_number,
            "full_name": order.client.full_name,
            "phone": order.client.phone,
            "email": order.client.email,
        } if order.client else None,

        "prescription_id": order.prescription_id,
        "partner_id": order.partner_id,

        "status": order.status,

        "frame": {
            "make": order.frame_make,
            "model": order.frame_model,
            "size": order.frame_size,
            "tint_color": order.tint_color,
        },

        "lens": {
            "type": order.lens_type,
            "coating": order.coating,
            "base_curve": order.base_curve,
        },

        "remarks": order.remarks,

        "created_at": order.created_at.isoformat(),
        "updated_at": order.updated_at.isoformat(),
    }


@orders_bp.route("", methods=["GET"])
@admin_required
def get_orders():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    page = max(page, 1)
    per_page = min(max(per_page, 1), 100)

    status = request.args.get("status", "").strip()
    search = request.args.get("search", "").strip()

    query = Order.query.join(Client)

    if status:
        if status not in ORDER_STATUSES:
            return jsonify({
                "message": "Invalid order status."
            }), 400

        query = query.filter(
            Order.status == status
        )

    if search:
        search_pattern = f"%{search}%"

        query = query.filter(
            db.or_(
                Order.order_number.ilike(search_pattern),
                Client.client_number.ilike(search_pattern),
                Client.full_name.ilike(search_pattern),
                Client.phone.ilike(search_pattern)
            )
        )

    pagination = (
        query
        .order_by(Order.created_at.desc())
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    )

    return jsonify({
        "orders": [
            serialize_order(order)
            for order in pagination.items
        ],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }
    })


@orders_bp.route("/<int:order_id>", methods=["GET"])
@admin_required
def get_order(order_id):
    order = db.session.get(Order, order_id)

    if not order:
        return jsonify({
            "message": "Order not found."
        }), 404

    return jsonify(
        serialize_order(order)
    )


@orders_bp.route("", methods=["POST"])
@admin_required
def create_order():
    data = request.get_json(silent=True) or {}

    client_id = data.get("client_id")

    if not client_id:
        return jsonify({
            "message": "Client ID is required."
        }), 400

    client = db.session.get(Client, client_id)

    if not client:
        return jsonify({
            "message": "Client not found."
        }), 404

    prescription_id = data.get("prescription_id")

    prescription = None

    if prescription_id:
        prescription = db.session.get(
            Prescription,
            prescription_id
        )

        if not prescription:
            return jsonify({
                "message": "Prescription not found."
            }), 404

        if prescription.client_id != client.id:
            return jsonify({
                "message": (
                    "Prescription does not belong to this client."
                )
            }), 400

    partner_id = data.get("partner_id")

    if partner_id:
        partner = db.session.get(
            Partner,
            partner_id
        )

        if not partner:
            return jsonify({
                "message": "Partner not found."
            }), 404

    order = Order(
        order_number=generate_order_number(),

        client_id=client.id,
        prescription_id=(
            prescription.id
            if prescription
            else None
        ),
        partner_id=partner_id,

        status="submitted",

        frame_make=data.get("frame_make"),
        frame_model=data.get("frame_model"),
        frame_size=data.get("frame_size"),
        tint_color=data.get("tint_color"),

        lens_type=data.get("lens_type"),
        coating=data.get("coating"),
        base_curve=data.get("base_curve"),

        remarks=data.get("remarks")
    )

    db.session.add(order)
    db.session.commit()

    return jsonify({
        "message": "Order created successfully.",
        "order": serialize_order(order)
    }), 201



@orders_bp.route("/public", methods=["POST"])
def create_public_order():
    data = request.get_json(silent=True) or {}


    full_name = data.get("full_name", "").strip()
    phone = data.get("phone", "").strip()
    email = data.get("email")

    if email:
        email = email.strip().lower()

    if not full_name:
        return jsonify({
            "message": "Full name is required."
        }), 400

    if not phone:
        return jsonify({
            "message": "Phone number is required."
        }), 400

    if len(full_name) > 150:
        return jsonify({
            "message": "Full name must not exceed 150 characters."
        }), 400

    if len(phone) > 30:
        return jsonify({
            "message": "Phone number must not exceed 30 characters."
        }), 400

    if email and len(email) > 150:
        return jsonify({
            "message": "Email must not exceed 150 characters."
        }), 400


    date_of_birth = None

    if data.get("date_of_birth"):
        try:
            from datetime import datetime

            date_of_birth = datetime.strptime(
                data["date_of_birth"],
                "%Y-%m-%d"
            ).date()

        except (ValueError, TypeError):
            return jsonify({
                "message": (
                    "Date of birth must use YYYY-MM-DD format."
                )
            }), 400


    client = (
        Client.query
        .filter_by(phone=phone)
        .first()
    )

    if client:
        same_name = (
            client.full_name.strip().lower()
            == full_name.strip().lower()
        )

        same_email = (
            email
            and client.email
            and client.email.strip().lower()
            == email.strip().lower()
        )

        same_dob = (
            date_of_birth
            and client.date_of_birth
            and client.date_of_birth == date_of_birth
        )

        identity_matches = (
            same_name
            and (same_email or same_dob)
        )

        if identity_matches:
            if email and not client.email:
                client.email = email

            if date_of_birth and not client.date_of_birth:
                client.date_of_birth = date_of_birth

        else:
            client = Client(
                client_number=generate_client_number(),
                full_name=full_name,
                phone=phone,
                email=email,
                date_of_birth=date_of_birth,
            )

            db.session.add(client)
            db.session.flush()

    else:
        client = Client(
            client_number=generate_client_number(),
            full_name=full_name,
            phone=phone,
            email=email,
            date_of_birth=date_of_birth,
        )

        db.session.add(client)
        db.session.flush()

    prescription_data = data.get("prescription")

    prescription = None

    if prescription_data:
        prescription = Prescription(
            client_id=client.id,

            right_sph=prescription_data.get("right_sph"),
            right_cyl=prescription_data.get("right_cyl"),
            right_axis=prescription_data.get("right_axis"),
            right_add=prescription_data.get("right_add"),
            right_pd=prescription_data.get("right_pd"),

            left_sph=prescription_data.get("left_sph"),
            left_cyl=prescription_data.get("left_cyl"),
            left_axis=prescription_data.get("left_axis"),
            left_add=prescription_data.get("left_add"),
            left_pd=prescription_data.get("left_pd"),

            source="Public website",
        )

        db.session.add(prescription)
        db.session.flush()

    order = Order(
        order_number=generate_order_number(),

        client_id=client.id,

        prescription_id=(
            prescription.id
            if prescription
            else None
        ),

        status="submitted",

        frame_make=data.get("frame_make"),
        frame_model=data.get("frame_model"),
        frame_size=data.get("frame_size"),
        tint_color=data.get("tint_color"),

        lens_type=data.get("lens_type"),
        coating=data.get("coating"),
        base_curve=data.get("base_curve"),

        remarks=data.get("remarks"),
    )

    db.session.add(order)
    db.session.commit()

    return jsonify({
        "message": (
            "Your glasses order request "
            "has been submitted successfully."
        ),
        "order": {
            "order_number": order.order_number,
            "status": order.status,
        }
    }), 201


@orders_bp.route("/<int:order_id>", methods=["PUT"])
@admin_required
def update_order(order_id):
    order = db.session.get(Order, order_id)

    if not order:
        return jsonify({
            "message": "Order not found."
        }), 404

    data = request.get_json(silent=True) or {}

    if "client_id" in data:
        client_id = data.get("client_id")

        if not client_id:
            return jsonify({
                "message": "Client ID cannot be empty."
            }), 400

        client = db.session.get(Client, client_id)

        if not client:
            return jsonify({
                "message": "Client not found."
            }), 404

        order.client_id = client.id

        if order.prescription_id:
            prescription = db.session.get(
                Prescription,
                order.prescription_id
            )

            if prescription and prescription.client_id != client.id:
                return jsonify({
                    "message": (
                        "The selected prescription does not "
                        "belong to the selected client."
                    )
                }), 400

    if "prescription_id" in data:
        prescription_id = data.get(
            "prescription_id"
        )

        if prescription_id is None:
            order.prescription_id = None

        else:
            prescription = db.session.get(
                Prescription,
                prescription_id
            )

            if not prescription:
                return jsonify({
                    "message": "Prescription not found."
                }), 404

            if prescription.client_id != order.client_id:
                return jsonify({
                    "message": (
                        "The prescription does not belong "
                        "to this client."
                    )
                }), 400

            order.prescription_id = prescription.id

    if "frame_make" in data:
        order.frame_make = data.get("frame_make")

    if "frame_model" in data:
        order.frame_model = data.get("frame_model")

    if "frame_size" in data:
        order.frame_size = data.get("frame_size")

    if "tint_color" in data:
        order.tint_color = data.get("tint_color")

    if "lens_type" in data:
        order.lens_type = data.get("lens_type")

    if "coating" in data:
        order.coating = data.get("coating")

    if "base_curve" in data:
        order.base_curve = data.get("base_curve")

    if "remarks" in data:
        order.remarks = data.get("remarks")

    db.session.commit()

    return jsonify({
        "message": "Order updated successfully.",
        "order": serialize_order(order)
    })


@orders_bp.route(
    "/<int:order_id>/partner",
    methods=["PUT"]
)
@admin_required
def assign_order_partner(order_id):
    order = db.session.get(Order, order_id)

    if not order:
        return jsonify({
            "message": "Order not found."
        }), 404

    data = request.get_json(silent=True) or {}

    if "partner_id" not in data:
        return jsonify({
            "message": "Partner ID is required."
        }), 400

    partner_id = data.get("partner_id")

    if partner_id is None:
        order.partner_id = None

        db.session.commit()

        return jsonify({
            "message": "Partner assignment removed.",
            "order": serialize_order(order)
        })

    partner = db.session.get(
        Partner,
        partner_id
    )

    if not partner:
        return jsonify({
            "message": "Partner not found."
        }), 404

    order.partner_id = partner.id

    db.session.commit()

    return jsonify({
        "message": "Order assigned to partner successfully.",
        "order": serialize_order(order)
    })