from datetime import datetime

from app.extensions import db


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    order_number = db.Column(
        db.String(30),
        unique=True,
        nullable=False,
        index=True
    )

    client_id = db.Column(
        db.Integer,
        db.ForeignKey("clients.id"),
        nullable=False,
        index=True
    )

    prescription_id = db.Column(
        db.Integer,
        db.ForeignKey("prescriptions.id"),
        nullable=True,
        index=True
    )

    partner_id = db.Column(
        db.Integer,
        db.ForeignKey("partners.id"),
        nullable=True,
        index=True
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="submitted",
        index=True
    )

    frame_make = db.Column(
        db.String(150),
        nullable=True
    )

    frame_model = db.Column(
        db.String(150),
        nullable=True
    )

    frame_size = db.Column(
        db.String(100),
        nullable=True
    )

    tint_color = db.Column(
        db.String(150),
        nullable=True
    )

    lens_type = db.Column(
        db.String(150),
        nullable=True
    )

    coating = db.Column(
        db.String(150),
        nullable=True
    )

    base_curve = db.Column(
        db.String(50),
        nullable=True
    )

    remarks = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    client = db.relationship(
        "Client",
        back_populates="orders"
    )

    prescription = db.relationship(
        "Prescription",
        back_populates="orders"
    )

    partner = db.relationship(
        "Partner"
    )

    def __repr__(self):
        return f"<Order {self.order_number}>"