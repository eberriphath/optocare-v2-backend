from app.extensions import db
from datetime import datetime

class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    clinic_name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)

    status = db.Column(db.String(20), default="pending")

    reviewed_by = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Application {self.clinic_name} - {self.status}>"