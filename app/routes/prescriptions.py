from datetime import datetime

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Client, Prescription
from app.utils.decorators import admin_required


prescriptions_bp = Blueprint(
    "prescriptions",
    __name__,
    url_prefix="/api/prescriptions"
)


def serialize_prescription(prescription):
    return {
        "id": prescription.id,

        "client": {
            "id": prescription.client.id,
            "client_number": prescription.client.client_number,
            "full_name": prescription.client.full_name,
            "phone": prescription.client.phone,
        },

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


@prescriptions_bp.route("", methods=["GET"])
@admin_required
def get_prescriptions():
    page = request.args.get(
        "page",
        1,
        type=int
    )

    per_page = request.args.get(
        "per_page",
        20,
        type=int
    )

    search = request.args.get(
        "search",
        "",
        type=str
    ).strip()

    query = Prescription.query.join(Client)

    if search:
        search_term = f"%{search}%"

        query = query.filter(
            db.or_(
                Client.client_number.ilike(search_term),
                Client.full_name.ilike(search_term),
                Client.phone.ilike(search_term),
                Client.email.ilike(search_term),
            )
        )

    pagination = (
        query
        .order_by(Prescription.created_at.desc())
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    )

    return jsonify({
        "prescriptions": [
            serialize_prescription(prescription)
            for prescription in pagination.items
        ],

        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }
    })


@prescriptions_bp.route("/<int:prescription_id>", methods=["GET"])
@admin_required
def get_prescription(prescription_id):
    prescription = db.session.get(
        Prescription,
        prescription_id
    )

    if not prescription:
        return jsonify({
            "message": "Prescription not found."
        }), 404

    return jsonify({
        "prescription": serialize_prescription(
            prescription
        )
    })

@prescriptions_bp.route("", methods=["POST"])
@admin_required
def create_prescription():
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

    prescription_date = None

    if data.get("prescription_date"):
        try:
            prescription_date = datetime.strptime(
                data["prescription_date"],
                "%Y-%m-%d"
            ).date()
        except (ValueError, TypeError):
            return jsonify({
                "message": (
                    "Prescription date must use "
                    "YYYY-MM-DD format."
                )
            }), 400

    prescription = Prescription(
        client_id=client.id,

        right_sph=data.get("right_sph"),
        right_cyl=data.get("right_cyl"),
        right_axis=data.get("right_axis"),
        right_add=data.get("right_add"),
        right_pd=data.get("right_pd"),

        left_sph=data.get("left_sph"),
        left_cyl=data.get("left_cyl"),
        left_axis=data.get("left_axis"),
        left_add=data.get("left_add"),
        left_pd=data.get("left_pd"),

        prescription_date=prescription_date,

        source=data.get("source"),
        notes=data.get("notes"),
    )

    db.session.add(prescription)
    db.session.commit()

    return jsonify({
        "message": "Prescription created successfully.",
        "prescription": serialize_prescription(
            prescription
        )
    }), 201


@prescriptions_bp.route("/<int:prescription_id>", methods=["PUT"])
@admin_required
def update_prescription(prescription_id):
    prescription = db.session.get(
        Prescription,
        prescription_id
    )

    if not prescription:
        return jsonify({
            "message": "Prescription not found."
        }), 404

    data = request.get_json(silent=True) or {}

    eye_fields = [
        "right_sph",
        "right_cyl",
        "right_axis",
        "right_add",
        "right_pd",
        "left_sph",
        "left_cyl",
        "left_axis",
        "left_add",
        "left_pd",
    ]

    for field in eye_fields:
        if field in data:
            value = data.get(field)

            if value is not None and not isinstance(value, str):
                return jsonify({
                    "message": f"{field} must be a string."
                }), 400

            setattr(
                prescription,
                field,
                value.strip() if isinstance(value, str) else None
            )

    if "prescription_date" in data:
        prescription_date = data.get(
            "prescription_date"
        )

        if prescription_date:
            try:
                prescription.prescription_date = (
                    datetime.strptime(
                        prescription_date,
                        "%Y-%m-%d"
                    ).date()
                )
            except (ValueError, TypeError):
                return jsonify({
                    "message": (
                        "Prescription date must use "
                        "YYYY-MM-DD format."
                    )
                }), 400
        else:
            prescription.prescription_date = None

    if "source" in data:
        source = data.get("source")

        if source is not None and not isinstance(source, str):
            return jsonify({
                "message": "Source must be a string."
            }), 400

        prescription.source = (
            source.strip()
            if isinstance(source, str)
            else None
        )

    if "notes" in data:
        notes = data.get("notes")

        if notes is not None and not isinstance(notes, str):
            return jsonify({
                "message": "Notes must be a string."
            }), 400

        prescription.notes = (
            notes.strip()
            if isinstance(notes, str)
            else None
        )

    db.session.commit()

    return jsonify({
        "message": "Prescription updated successfully.",
        "prescription": serialize_prescription(
            prescription
        )
    })