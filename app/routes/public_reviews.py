from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Review, Partner


public_reviews_bp = Blueprint(
    "public_reviews",
    __name__,
    url_prefix="/api/reviews"
)


@public_reviews_bp.route("/partner/<int:partner_id>", methods=["GET"])
def get_partner_reviews(partner_id):

    partner = Partner.query.filter_by(
        id=partner_id,
        is_verified=True
    ).first()

    if not partner:
        return jsonify({
            "error": "Partner not found"
        }), 404

    reviews = Review.query.filter_by(
        partner_id=partner.id,
        is_approved=True
    ).order_by(
        Review.created_at.desc()
    ).all()

    return jsonify({
        "partner": {
            "id": partner.id,
            "company_name": partner.company_name
        },
        "reviews": [
            {
                "id": review.id,
                "reviewer_name": review.reviewer_name,
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at.isoformat()
            }
            for review in reviews
        ]
    }), 200


@public_reviews_bp.route("", methods=["POST"])
def create_review():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    partner_id = data.get("partner_id")
    reviewer_name = data.get("reviewer_name")
    reviewer_email = data.get("reviewer_email")
    rating = data.get("rating")
    comment = data.get("comment")

    if partner_id is None:
        return jsonify({
            "error": "partner_id is required"
        }), 400

    if not isinstance(partner_id, int):
        return jsonify({
            "error": "partner_id must be an integer"
        }), 400

    partner = Partner.query.filter_by(
        id=partner_id,
        is_verified=True
    ).first()

    if not partner:
        return jsonify({
            "error": "Partner not found"
        }), 404

    if not isinstance(reviewer_name, str) or not reviewer_name.strip():
        return jsonify({
            "error": "Reviewer name is required"
        }), 400

    reviewer_name = reviewer_name.strip()

    if len(reviewer_name) > 120:
        return jsonify({
            "error": "Reviewer name must not exceed 120 characters"
        }), 400

    if reviewer_email is not None:
        if not isinstance(reviewer_email, str):
            return jsonify({
                "error": "Reviewer email must be a string"
            }), 400

        reviewer_email = reviewer_email.strip().lower()

        if len(reviewer_email) > 150:
            return jsonify({
                "error": "Reviewer email must not exceed 150 characters"
            }), 400

    if not isinstance(rating, int) or isinstance(rating, bool):
        return jsonify({
            "error": "Rating must be an integer"
        }), 400

    if rating < 1 or rating > 5:
        return jsonify({
            "error": "Rating must be between 1 and 5"
        }), 400

    if not isinstance(comment, str) or not comment.strip():
        return jsonify({
            "error": "Comment is required"
        }), 400

    comment = comment.strip()

    if len(comment) > 2000:
        return jsonify({
            "error": "Comment must not exceed 2000 characters"
        }), 400

    review = Review(
        partner_id=partner.id,
        user_id=None,
        reviewer_name=reviewer_name,
        reviewer_email=reviewer_email,
        rating=rating,
        comment=comment,
        is_approved=False,
        admin_notes=None
    )

    db.session.add(review)
    db.session.commit()

    return jsonify({
        "message": "Review submitted successfully and is awaiting approval",
        "review": {
            "id": review.id,
            "partner_id": review.partner_id,
            "reviewer_name": review.reviewer_name,
            "rating": review.rating,
            "is_approved": review.is_approved,
            "created_at": review.created_at.isoformat()
        }
    }), 201