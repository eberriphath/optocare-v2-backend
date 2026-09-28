from datetime import datetime

from app.extensions import db


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    client_number = db.Column(
        db.String(30),
        unique=True,
        nullable=False,
        index=True
    )

    full_name = db.Column(
        db.String(150),
        nullable=False
    )

    phone = db.Column(
        db.String(30),
        nullable=False,
        index=True
    )

    email = db.Column(
        db.String(150),
        nullable=True,
        index=True
    )

    date_of_birth = db.Column(
        db.Date,
        nullable=True
    )

    notes = db.Column(
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

    prescriptions = db.relationship(
        "Prescription",
        back_populates="client",
        cascade="all, delete-orphan"
    )

    orders = db.relationship(
        "Order",
        back_populates="client",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Client {self.client_number} - {self.full_name}>"