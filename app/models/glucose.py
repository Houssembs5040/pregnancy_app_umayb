from datetime import datetime

from app.extensions import db


class GlucoseMeasurement(db.Model):
    __tablename__ = "glucose_measurements"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    user_id = db.Column(
        db.BigInteger().with_variant(db.Integer, "sqlite"),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Valeur à jeun obligatoire, post-prandiale optionnelle (g/L)
    fasting_value = db.Column(db.Numeric(4, 2), nullable=False)
    postprandial_value = db.Column(db.Numeric(4, 2), nullable=True)

    gestational_week = db.Column(db.Integer, nullable=True)   # auto-calculated
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
            "glucose_measurements", lazy=True, cascade="all, delete-orphan"
        ),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "fasting_value": (
                float(self.fasting_value) if self.fasting_value is not None else None
            ),
            "postprandial_value": (
                float(self.postprandial_value)
                if self.postprandial_value is not None
                else None
            ),
            "gestational_week": self.gestational_week,
            "note": self.note,
            "measured_at": self.measured_at.isoformat() if self.measured_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
