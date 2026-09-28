from datetime import datetime

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Client, Prescription, Order
from app.utils.decorators import admin_required
from app.utils.number_generator import generate_client_number


clients_bp = Blueprint(
    "clients",
    __name__,
    url_prefix="/api/clients"
)


@clients_bp.route("", methods=["GET"])
@admin_required
def get_clients():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    page = max(page, 1)
    per_page = min(max(per_page, 1), 100)

    search = request.args.get("search", "").strip()

    query = Client.query

    if search:
        search_pattern = f"%{search}%"

        query = query.filter(
            db.or_(
                Client.client_number.ilike(search_pattern),
                Client.full_name.ilike(search_pattern),
                Client.phone.ilike(search_pattern),
                Client.email.ilike(search_pattern)
            )
        )

    pagination = (
        query
        .order_by(Client.created_at.desc())
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    )

    return jsonify({
        "clients": [
            {
                "id": client.id,
                "client_number": client.client_number,
                "full_name": client.full_name,
                "phone": client.phone,
                "email": client.email,
                "date_of_birth": (
                    client.date_of_birth.isoformat()
                    if client.date_of_birth
                    else None
                ),
                "notes": client.notes,
                "created_at": client.created_at.isoformat(),
                "updated_at": client.updated_at.isoformat()
            }
            for client in pagination.items
        ],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }
    })


@clients_bp.route("/<int:client_id>", methods=["GET"])
@admin_required
def get_client(client_id):
    client = db.session.get(Client, client_id)

    if not client:
        return jsonify({
            "message": "Client not found."
        }), 404

    return jsonify({
        "id": client.id,
        "client_number": client.client_number,
        "full_name": client.full_name,
        "phone": client.phone,
        "email": client.email,
        "date_of_birth": (
            client.date_of_birth.isoformat()
            if client.date_of_birth
            else None
        ),
        "notes": client.notes,
        "created_at": client.created_at.isoformat(),
        "updated_at": client.updated_at.isoformat()
    })


@clients_bp.route("/<int:client_id>/history", methods=["GET"])
@admin_required
def get_client_history(client_id):
    client = db.session.get(Client, client_id)

    if not client:
        return jsonify({
            "message": "Client not found."
        }), 404

    prescriptions = (
        Prescription.query
        .filter_by(client_id=client.id)
        .order_by(Prescription.created_at.desc())
        .all()
    )

    orders = (
        Order.query
        .filter_by(client_id=client.id)
        .order_by(Order.created_at.desc())
        .all()
    )

    return jsonify({
        "client": {
            "id": client.id,
            "client_number": client.client_number,
            "full_name": client.full_name,
            "phone": client.phone,
            "email": client.email,
            "date_of_birth": (
                client.date_of_birth.isoformat()
                if client.date_of_birth
                else None
            ),
            "notes": client.notes,
            "created_at": client.created_at.isoformat(),
            "updated_at": client.updated_at.isoformat()
        },

        "prescriptions": [
            {
                "id": prescription.id,

                "right_eye": {
                    "sph": prescription.right_sph,
                    "cyl": prescription.right_cyl,
                    "axis": prescription.right_axis,
                    "add": prescription.right_add,
                    "pd": prescription.right_pd,
                },

                "left_eye": {
                    "sph": prescription.left_sph,
                    "cyl": prescription.left_cyl,
                    "axis": prescription.left_axis,
                    "add": prescription.left_add,
                    "pd": prescription.left_pd,
                },

                "prescription_date": (
                    prescription.prescription_date.isoformat()
                    if prescription.prescription_date
                    else None
                ),

                "source": prescription.source,
                "notes": prescription.notes,
                "created_at": prescription.created_at.isoformat(),
            }
            for prescription in prescriptions
        ],

        "orders": [
            {
                "id": order.id,
                "order_number": order.order_number,
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
            for order in orders
        ]
    })


@clients_bp.route("/<int:client_id>", methods=["PUT"])
@admin_required
def update_client(client_id):
    client = db.session.get(Client, client_id)

    if not client:
        return jsonify({
            "message": "Client not found."
        }), 404

    data = request.get_json(silent=True) or {}

    if "full_name" in data:
        full_name = data.get("full_name")

        if not isinstance(full_name, str):
            return jsonify({
                "message": "Full name must be a string."
            }), 400

        full_name = full_name.strip()

        if not full_name:
            return jsonify({
                "message": "Full name cannot be empty."
            }), 400

        if len(full_name) > 150:
            return jsonify({
                "message": (
                    "Full name must not exceed 150 characters."
                )
            }), 400

        client.full_name = full_name

    if "phone" in data:
        phone = data.get("phone")

        if not isinstance(phone, str):
            return jsonify({
                "message": "Phone number must be a string."
            }), 400

        phone = phone.strip()

        if not phone:
            return jsonify({
                "message": "Phone number cannot be empty."
            }), 400

        if len(phone) > 30:
            return jsonify({
                "message": (
                    "Phone number must not exceed 30 characters."
                )
            }), 400

        client.phone = phone

    if "email" in data:
        email = data.get("email")

        if email is not None:
            if not isinstance(email, str):
                return jsonify({
                    "message": "Email must be a string."
                }), 400

            email = email.strip().lower()

            if len(email) > 150:
                return jsonify({
                    "message": (
                        "Email must not exceed 150 characters."
                    )
                }), 400

            client.email = email or None

        else:
            client.email = None

    if "date_of_birth" in data:
        date_of_birth = data.get("date_of_birth")

        if date_of_birth:
            try:
                date_of_birth = datetime.strptime(
                    date_of_birth,
                    "%Y-%m-%d"
                ).date()
            except (ValueError, TypeError):
                return jsonify({
                    "message": (
                        "Date of birth must use YYYY-MM-DD format."
                    )
                }), 400

            client.date_of_birth = date_of_birth

        else:
            client.date_of_birth = None

    if "notes" in data:
        notes = data.get("notes")

        if notes is not None and not isinstance(notes, str):
            return jsonify({
                "message": "Notes must be a string."
            }), 400

        client.notes = notes.strip() if notes else None

    db.session.commit()

    return jsonify({
        "message": "Client updated successfully.",
        "client": {
            "id": client.id,
            "client_number": client.client_number,
            "full_name": client.full_name,
            "phone": client.phone,
            "email": client.email,
            "date_of_birth": (
                client.date_of_birth.isoformat()
                if client.date_of_birth
                else None
            ),
            "notes": client.notes,
            "created_at": client.created_at.isoformat(),
            "updated_at": client.updated_at.isoformat()
        }
    })



@clients_bp.route("", methods=["POST"])
@admin_required
def create_client():
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
            date_of_birth = datetime.strptime(
                data["date_of_birth"],
                "%Y-%m-%d"
            ).date()
        except (ValueError, TypeError):
            return jsonify({
                "message": "Date of birth must use YYYY-MM-DD format."
            }), 400

    client = Client(
        client_number=generate_client_number(),
        full_name=full_name,
        phone=phone,
        email=email,
        date_of_birth=date_of_birth,
        notes=data.get("notes")
    )

    db.session.add(client)
    db.session.commit()

    return jsonify({
        "message": "Client created successfully.",
        "client": {
            "id": client.id,
            "client_number": client.client_number,
            "full_name": client.full_name,
            "phone": client.phone,
            "email": client.email,
            "date_of_birth": (
                client.date_of_birth.isoformat()
                if client.date_of_birth
                else None
            ),
            "notes": client.notes,
            "created_at": client.created_at.isoformat()
        }
    }), 201