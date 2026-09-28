from datetime import datetime

from app.extensions import db


class Prescription(db.Model):
    __tablename__ = "prescriptions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    client_id = db.Column(
        db.Integer,
        db.ForeignKey("clients.id"),
        nullable=False,
        index=True
    )

    right_sph = db.Column(
        db.String(20),
        nullable=True
    )

    right_cyl = db.Column(
        db.String(20),
        nullable=True
    )

    right_axis = db.Column(
        db.String(20),
        nullable=True
    )

    right_add = db.Column(
        db.String(20),
        nullable=True
    )

    right_pd = db.Column(
        db.String(20),
        nullable=True
    )

    left_sph = db.Column(
        db.String(20),
        nullable=True
    )

    left_cyl = db.Column(
        db.String(20),
        nullable=True
    )

    left_axis = db.Column(
        db.String(20),
        nullable=True
    )

    left_add = db.Column(
        db.String(20),
        nullable=True
    )

    left_pd = db.Column(
        db.String(20),
        nullable=True
    )

    prescription_date = db.Column(
        db.Date,
        nullable=True
    )

    source = db.Column(
        db.String(150),
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

    client = db.relationship(
        "Client",
        back_populates="prescriptions"
    )

    orders = db.relationship(
        "Order",
        back_populates="prescription"
    )

    def __repr__(self):
        return f"<Prescription {self.id} - Client {self.client_id}>"