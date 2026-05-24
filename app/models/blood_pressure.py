from datetime import datetime

from app.extensions import db


class BloodPressureMeasurement(db.Model):
    __tablename__ = "blood_pressure_measurements"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    user_id = db.Column(
        db.BigInteger().with_variant(db.Integer, "sqlite"),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    systolic = db.Column(db.Integer, nullable=False)     # mmHg — chiffre du haut
    diastolic = db.Column(db.Integer, nullable=False)    # mmHg — chiffre du bas
    gestational_week = db.Column(db.Integer, nullable=True)   # auto-calculated on save
    note = db.Column(db.Text, nullable=True)
    measured_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "blood_pressure_measurements", lazy=True, cascade="all, delete-orphan"
        ),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "systolic": self.systolic,
            "diastolic": self.diastolic,
            "display": f"{self.systolic}/{self.diastolic} mmHg",
            "gestational_week": self.gestational_week,
            "note": self.note,
            "measured_at": self.measured_at.isoformat() if self.measured_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
