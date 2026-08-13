from app.extensions import db
from datetime import datetime


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)

    # Applicant information
    full_name = db.Column(db.String(120), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(30), nullable=False)

    # Company information
    company_name = db.Column(db.String(150), nullable=False)

    # Services offered
    services_offered = db.Column(db.Text, nullable=False)

    # Partnership type
    partner_type = db.Column(
        db.String(30),
        nullable=False
    )

    # Supporting document
    document_path = db.Column(db.String(255), nullable=True)

    # Application status
    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending"
    )

    # Admin review
    reviewed_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    review_notes = db.Column(db.Text, nullable=True)

    reviewed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f"<Application {self.company_name} - {self.status}>"