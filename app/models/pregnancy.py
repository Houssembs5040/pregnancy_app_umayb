from datetime import date, datetime, timedelta

from app.extensions import db


class PregnancyProfile(db.Model):
    __tablename__ = "pregnancy_profiles"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    user_id = db.Column(
        db.BigInteger().with_variant(db.Integer, "sqlite"),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    lmp_date = db.Column(db.Date, nullable=False)   # Date des dernières règles
    due_date = db.Column(db.Date, nullable=False)   # DDR + 280 jours
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user = db.relationship("User", back_populates="pregnancy_profile")

    @staticmethod
    def calculate_due_date(lmp_date: date) -> date:
        return lmp_date + timedelta(days=280)

    def gestational_days(self, today: date | None = None) -> int:
        today = today or date.today()
        return (today - self.lmp_date).days

    def gestational_weeks(self, today: date | None = None) -> int:
        days = self.gestational_days(today)
        return max(days // 7, 0)

    def gestational_week_and_days(self, today: date | None = None) -> dict:
        days = max(self.gestational_days(today), 0)
        weeks = days // 7
        extra_days = days % 7
        return {
            "weeks": weeks,
            "days": extra_days,
        }

    def trimester(self, today: date | None = None) -> int:
        weeks = self.gestational_weeks(today)
        if weeks < 14:
            return 1
        if weeks < 28:
            return 2
        return 3

    def progress_percentage(self, today: date | None = None) -> float:
        days = max(min(self.gestational_days(today), 280), 0)
        return round((days / 280) * 100, 2)

    def to_dict(self) -> dict:
        week_info = self.gestational_week_and_days()
        return {
            "id": self.id,
            "user_id": self.user_id,
            "lmp_date": self.lmp_date.isoformat() if self.lmp_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "gestational_weeks": week_info["weeks"],
            "gestational_days": week_info["days"],
            "trimester": self.trimester(),
            "progress_percentage": self.progress_percentage(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
