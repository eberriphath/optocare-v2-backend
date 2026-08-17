from app.extensions import db
from datetime import datetime


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    partner_id = db.Column(
        db.Integer,
        db.ForeignKey("partners.id"),
        nullable=False,
        index=True
    )

    # Optional because public visitors don't have to create accounts
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    reviewer_name = db.Column(
        db.String(120),
        nullable=False
    )

    reviewer_email = db.Column(
        db.String(150),
        nullable=True
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    comment = db.Column(
        db.Text,
        nullable=False
    )

    is_approved = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        index=True
    )

    admin_notes = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    partner = db.relationship(
        "Partner",
        backref=db.backref(
            "reviews",
            lazy=True
        )
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "reviews",
            lazy=True
        )
    )

    def __repr__(self):
        return f"<Review {self.id} - Partner {self.partner_id}>"
