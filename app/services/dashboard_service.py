from datetime import date

from sqlalchemy import select

from app.extensions import db
from app.models import Appointment, Alert
from app.data.baby_development import get_baby_data
from app.data.symptoms import get_maternal_state


def _get_latest_vitals(user) -> dict:
    """Fetch the most recent measurement from each tracking model."""
    from app.models.weight import WeightMeasurement
    from app.models.blood_pressure import BloodPressureMeasurement
    from app.models.glucose import GlucoseMeasurement

    latest_weight = (
        WeightMeasurement.query.filter_by(user_id=user.id)
        .order_by(WeightMeasurement.measured_at.desc())
        .first()
    )
    latest_bp = (
        BloodPressureMeasurement.query.filter_by(user_id=user.id)
        .order_by(BloodPressureMeasurement.measured_at.desc())
        .first()
    )
    latest_glucose = (
        GlucoseMeasurement.query.filter_by(user_id=user.id)
        .order_by(GlucoseMeasurement.measured_at.desc())
        .first()
    )

    return {
        "weight": latest_weight.to_dict() if latest_weight else None,
        "blood_pressure": latest_bp.to_dict() if latest_bp else None,
        "glucose": latest_glucose.to_dict() if latest_glucose else None,
    }


def get_dashboard_data(user) -> dict:
    pregnancy_profile = user.pregnancy_profile

    if not pregnancy_profile:
        raise ValueError("pregnancy profile not found")

    week_info = pregnancy_profile.gestational_week_and_days()
    total_days = max(pregnancy_profile.gestational_days(), 0)
    current_week = week_info["weeks"]
    trimester = pregnancy_profile.trimester()

    next_appointment = db.session.execute(
        select(Appointment)
        .where(
            Appointment.user_id == user.id,
            Appointment.status == "planned",
            Appointment.appointment_date >= date.today(),
        )
        .order_by(Appointment.appointment_date.asc(), Appointment.appointment_time.asc())
        .limit(1)
    ).scalar_one_or_none()

    active_alerts = db.session.execute(
        select(Alert)
        .where(
            Alert.user_id == user.id,
            Alert.is_active.is_(True),
        )
        .order_by(Alert.created_at.desc())
    ).scalars().all()

    # ── Baby development block ──────────────────────────────────────────────
    baby_data = get_baby_data(current_week)

    # ── Maternal state block ────────────────────────────────────────────────
    maternal_state = get_maternal_state(trimester)

    # ── Latest vitals summary ───────────────────────────────────────────────
    latest_vitals = _get_latest_vitals(user)

    return {
        "gestational_age": {
            "weeks": current_week,
            "days": week_info["days"],
            "display": f"{current_week} SA + {week_info['days']} jours",
            "total_days": total_days,
        },
        "pregnancy": {
            "lmp_date": pregnancy_profile.lmp_date.isoformat(),
            "due_date": pregnancy_profile.due_date.isoformat(),
            "trimester": trimester,
            "progress_percentage": pregnancy_profile.progress_percentage(),
        },
        "baby_development": baby_data,
        "maternal_state": maternal_state,
        "latest_vitals": latest_vitals,
        "next_appointment": (
            next_appointment.to_dict() if next_appointment else None
        ),
        "active_alerts": [alert.to_dict() for alert in active_alerts],
        "summary": {
            "active_alerts_count": len(active_alerts),
            "has_next_appointment": next_appointment is not None,
        },
    }
