from flask import Blueprint, jsonify
from datetime import datetime, timezone, timedelta

from app.models import Application, User, Partner
from app.utils.decorators import admin_required
from app.extensions import db
from flask import request



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

@admin_bp.route("/applications/<int:application_id>/approve", methods=["PATCH"])
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

    application.status = "approved"
    application.reviewed_by = admin.id
    application.reviewed_at = datetime.now(timezone.utc)
    application.review_notes = None

    db.session.commit()

    return jsonify({
        "message": "Application approved successfully",
        "application": {
            "id": application.id,
            "status": application.status,
            "reviewed_by": application.reviewed_by,
            "reviewed_at": application.reviewed_at.isoformat()
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