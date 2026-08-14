from app.extensions import db
from datetime import datetime


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    partner_id = db.Column(
        db.Integer,
        db.ForeignKey("partners.id"),
        nullable=False
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    category = db.Column(
        db.String(100),
        nullable=True
    )

    brand = db.Column(
        db.String(100),
        nullable=True
    )

    price = db.Column(
        db.Numeric(10, 2),
        nullable=True
    )

    stock_quantity = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    is_available = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    image_url = db.Column(
        db.String(500),
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
            "products",
            lazy=True
        )
    )

    def __repr__(self):
        return f"<Product {self.name}>"