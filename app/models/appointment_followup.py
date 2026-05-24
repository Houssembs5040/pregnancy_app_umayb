from datetime import datetime

from app.extensions import db


class AppointmentFollowup(db.Model):
    __tablename__ = "appointment_followups"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)

    appointment_id = db.Column(
        db.BigInteger().with_variant(db.Integer, "sqlite"),
        db.ForeignKey("appointments.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    user_id = db.Column(
        db.BigInteger().with_variant(db.Integer, "sqlite"),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    was_completed = db.Column(db.Boolean, nullable=False, default=True)

    outcome_type = db.Column(
        db.Enum("normal", "anomaly", "unknown", name="appointment_outcome_enum"),
        nullable=False,
        default="unknown",
    )

    comment = db.Column(db.Text, nullable=True)

    completed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    appointment = db.relationship("Appointment", back_populates="followup")
    user = db.relationship(
        "User",
        backref=db.backref("appointment_followups", lazy=True, cascade="all, delete-orphan"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "appointment_id": self.appointment_id,
            "user_id": self.user_id,
            "was_completed": self.was_completed,
            "outcome_type": self.outcome_type,
            "comment": self.comment,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
