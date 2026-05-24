from datetime import datetime

from app.extensions import db


class UserProfile(db.Model):
    __tablename__ = "user_profiles"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    user_id = db.Column(
        db.BigInteger().with_variant(db.Integer, "sqlite"),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    age = db.Column(db.Integer, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    height_cm = db.Column(db.Numeric(5, 2), nullable=True)
    preferred_language = db.Column(db.String(10), nullable=False, default="fr")
    theme = db.Column(db.String(20), nullable=False, default="light")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user = db.relationship("User", back_populates="profile")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "age": self.age,
            "city": self.city,
            "height_cm": float(self.height_cm) if self.height_cm is not None else None,
            "preferred_language": self.preferred_language,
            "theme": self.theme,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
