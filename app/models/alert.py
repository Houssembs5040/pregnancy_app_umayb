from datetime import datetime

from app.extensions import db


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    user_id = db.Column(
        db.BigInteger().with_variant(db.Integer, "sqlite"),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    category = db.Column(
        db.Enum(
            "blood_pressure",
            "glucose",
            "weight",
            "fetal_movement",
            "followup",
            "system",
            name="alert_category_enum",
        ),
        nullable=False,
    )
    severity = db.Column(
        db.Enum("info", "warning", "urgent", name="alert_severity_enum"),
        nullable=False,
    )
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)

    source_table = db.Column(db.String(100), nullable=True)
    source_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), nullable=True)

    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship(
        "User",
        backref=db.backref("alerts", lazy=True, cascade="all, delete-orphan"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category": self.category,
            "severity": self.severity,
            "title": self.title,
            "message": self.message,
            "source_table": self.source_table,
            "source_id": self.source_id,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }
