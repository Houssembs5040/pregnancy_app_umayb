from datetime import datetime

from app.extensions import db


class UserSetting(db.Model):
    __tablename__ = "user_settings"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    user_id = db.Column(
        db.BigInteger().with_variant(db.Integer, "sqlite"),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Notification toggles
    notifications_enabled = db.Column(db.Boolean, nullable=False, default=True)
    reminder_7_days = db.Column(db.Boolean, nullable=False, default=True)
    reminder_3_days = db.Column(db.Boolean, nullable=False, default=True)
    reminder_same_day = db.Column(db.Boolean, nullable=False, default=True)
    reminder_2_hours = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    user = db.relationship(
        "User",
        backref=db.backref("settings", uselist=False, cascade="all, delete-orphan"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "notifications_enabled": self.notifications_enabled,
            "reminder_7_days": self.reminder_7_days,
            "reminder_3_days": self.reminder_3_days,
            "reminder_same_day": self.reminder_same_day,
            "reminder_2_hours": self.reminder_2_hours,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
