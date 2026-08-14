from app.extensions import db
from datetime import datetime


class Partner(db.Model):
    __tablename__ = "partners"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "partner",
            uselist=False
        )
    )

    company_name = db.Column(
        db.String(150),
        nullable=False
    )

    partner_type = db.Column(
        db.String(30),
        nullable=False
    )

    location = db.Column(
        db.String(150),
        nullable=True
    )

    specialty = db.Column(
        db.String(100),
        nullable=True
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    is_verified = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f"<Partner {self.company_name}>"