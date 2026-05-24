from datetime import datetime

from app.extensions import db


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    user_id = db.Column(
        db.BigInteger().with_variant(db.Integer, "sqlite"),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    type = db.Column(
        db.Enum("consultation", "analyse", "echographie", name="appointment_type_enum"),
        nullable=False,
    )
    title = db.Column(db.String(150), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False, index=True)
    appointment_time = db.Column(db.Time, nullable=True)
    location = db.Column(db.String(150), nullable=True)
    doctor_name = db.Column(db.String(120), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    source = db.Column(
        db.Enum("auto", "manual", name="appointment_source_enum"),
        nullable=False,
        default="manual",
    )
    status = db.Column(
        db.Enum(
            "planned",
            "done",
            "missed",
            "postponed",
            "cancelled",
            name="appointment_status_enum",
        ),
        nullable=False,
        default="planned",
        index=True,
    )
    gestational_week_target = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user = db.relationship(
        "User",
        backref=db.backref("appointments", lazy=True, cascade="all, delete-orphan"),
    )

    followup = db.relationship(
        "AppointmentFollowup",
        back_populates="appointment",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type,
            "title": self.title,
            "appointment_date": (
                self.appointment_date.isoformat() if self.appointment_date else None
            ),
            "appointment_time": (
                self.appointment_time.isoformat() if self.appointment_time else None
            ),
            "location": self.location,
            "doctor_name": self.doctor_name,
            "notes": self.notes,
            "source": self.source,
            "status": self.status,
            "gestational_week_target": self.gestational_week_target,
            "followup": self.followup.to_dict() if self.followup else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
