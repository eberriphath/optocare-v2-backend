from app.extensions import db
from datetime import datetime

class Partner(db.Model):
    __tablename__ = "partners"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    clinic_name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)

    description = db.Column(db.Text)

    is_verified = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Partner {self.clinic_name}>"