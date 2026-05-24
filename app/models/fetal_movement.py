from datetime import datetime

from app.extensions import db


class FetalMovementSession(db.Model):
    """
    Represents one fetal movement counting session.
    Activated automatically from 28 SA.
    The standard protocol: count until 10 movements are felt
    (or record total over a 2h period).
    """

    __tablename__ = "fetal_movement_sessions"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    user_id = db.Column(
        db.BigInteger().with_variant(db.Integer, "sqlite"),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    count = db.Column(db.Integer, nullable=False, default=0)
    session_start = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    session_end = db.Column(db.DateTime, nullable=True)
    gestational_week = db.Column(db.Integer, nullable=True)   # auto-calculated
    note = db.Column(db.Text, nullable=True)

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
            "fetal_movement_sessions", lazy=True, cascade="all, delete-orphan"
        ),
    )

    @property
    def duration_minutes(self) -> float | None:
        if self.session_start and self.session_end:
            delta = self.session_end - self.session_start
            return round(delta.total_seconds() / 60, 1)
        return None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "count": self.count,
            "session_start": (
                self.session_start.isoformat() if self.session_start else None
            ),
            "session_end": (
                self.session_end.isoformat() if self.session_end else None
            ),
            "duration_minutes": self.duration_minutes,
            "gestational_week": self.gestational_week,
            "note": self.note,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
