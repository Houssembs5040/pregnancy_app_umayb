from datetime import datetime, timedelta

from app.extensions import db
from app.models.weight import WeightMeasurement


# ─── OMS weight gain recommendations by pre-pregnancy BMI ───────────────────
# (total recommended gain over 40 weeks)
_BMI_GAIN_RANGES = {
    "underweight": (12.5, 18.0),   # IMC < 18.5
    "normal":      (11.5, 16.0),   # IMC 18.5–24.9
    "overweight":  (7.0, 11.5),    # IMC 25–29.9
    "obese":       (5.0, 9.0),     # IMC ≥ 30
}


def _get_gestational_week(user) -> int | None:
    pregnancy = user.pregnancy_profile
    if not pregnancy:
        return None
    return pregnancy.gestational_weeks()


def _bmi_category(height_cm: float | None, weight_kg: float) -> str | None:
    """Return OMS BMI category based on pre-pregnancy weight (first recorded)."""
    if not height_cm or height_cm <= 0:
        return None
    height_m = float(height_cm) / 100
    bmi = weight_kg / (height_m ** 2)
    if bmi < 18.5:
        return "underweight"
    if bmi < 25:
        return "normal"
    if bmi < 30:
        return "overweight"
    return "obese"


def _trigger_weight_alerts(user, new_measurement: WeightMeasurement) -> list[dict]:
    """
    Evaluate weight gain rules and create Alert records if thresholds are crossed.
    Returns list of created alert dicts.
    """
    from app.services.alert_service import create_alert

    alerts_created = []
    pregnancy = user.pregnancy_profile

    if not pregnancy:
        return alerts_created

    # ── Rule 1: gain > 2 kg in the past 7 days ──────────────────────────────
    one_week_ago = new_measurement.measured_at - timedelta(days=7)
    week_ago_measure = (
        WeightMeasurement.query
        .filter(
            WeightMeasurement.user_id == user.id,
            WeightMeasurement.measured_at <= one_week_ago,
        )
        .order_by(WeightMeasurement.measured_at.desc())
        .first()
    )

    if week_ago_measure:
        weekly_gain = float(new_measurement.weight_kg) - float(week_ago_measure.weight_kg)
        if weekly_gain > 2.0:
            alert = create_alert(user, {
                "category": "weight",
                "severity": "warning",
                "title": "Prise de poids rapide",
                "message": (
                    f"Vous avez pris {weekly_gain:.1f} kg en 7 jours. "
                    "Une prise de poids rapide peut nécessiter une consultation."
                ),
                "source_table": "weight_measurements",
                "source_id": new_measurement.id,
            })
            alerts_created.append(alert)

    # ── Rule 2: T3 excessive cumulative gain ────────────────────────────────
    trimester = pregnancy.trimester()
    if trimester == 3:
        first_measure = (
            WeightMeasurement.query
            .filter_by(user_id=user.id)
            .order_by(WeightMeasurement.measured_at.asc())
            .first()
        )
        if first_measure and first_measure.id != new_measurement.id:
            total_gain = float(new_measurement.weight_kg) - float(first_measure.weight_kg)
            # Get OMS limit for this user
            height_cm = user.profile.height_cm if user.profile else None
            category = _bmi_category(height_cm, float(first_measure.weight_kg))
            if category:
                _, max_gain = _BMI_GAIN_RANGES[category]
                if total_gain > max_gain:
                    alert = create_alert(user, {
                        "category": "weight",
                        "severity": "warning",
                        "title": "Prise de poids excessive",
                        "message": (
                            f"Prise de poids totale de {total_gain:.1f} kg, "
                            f"au-dessus de la limite OMS ({max_gain} kg). "
                            "Consultez votre médecin."
                        ),
                        "source_table": "weight_measurements",
                        "source_id": new_measurement.id,
                    })
                    alerts_created.append(alert)

    return alerts_created


def add_weight(user, data: dict) -> dict:
    weight_kg = data.get("weight_kg")
    note = data.get("note")
    measured_at_str = data.get("measured_at")

    if weight_kg is None:
        raise ValueError("weight_kg is required")

    try:
        weight_kg = float(weight_kg)
    except (TypeError, ValueError):
        raise ValueError("weight_kg must be a valid number")

    if weight_kg <= 0 or weight_kg > 300:
        raise ValueError("weight_kg must be between 0 and 300")

    measured_at = datetime.utcnow()
    if measured_at_str:
        try:
            measured_at = datetime.fromisoformat(measured_at_str)
        except ValueError:
            raise ValueError("measured_at must be a valid ISO datetime")

    gestational_week = _get_gestational_week(user)

    measurement = WeightMeasurement(
        user_id=user.id,
        weight_kg=weight_kg,
        gestational_week=gestational_week,
        note=note,
        measured_at=measured_at,
    )

    db.session.add(measurement)
    db.session.flush()   # get ID before alert creation

    alerts = _trigger_weight_alerts(user, measurement)

    db.session.commit()

    return {
        "message": "weight measurement recorded",
        "measurement": measurement.to_dict(),
        "alerts_triggered": len(alerts),
    }


def list_weights(user) -> dict:
    measurements = (
        WeightMeasurement.query
        .filter_by(user_id=user.id)
        .order_by(WeightMeasurement.measured_at.asc())
        .all()
    )

    # Compute gain vs first measurement
    gain = None
    if len(measurements) >= 2:
        gain = round(
            float(measurements[-1].weight_kg) - float(measurements[0].weight_kg), 2
        )

    return {
        "count": len(measurements),
        "total_gain_kg": gain,
        "measurements": [m.to_dict() for m in measurements],
    }


def get_latest_weight(user) -> dict | None:
    measurement = (
        WeightMeasurement.query
        .filter_by(user_id=user.id)
        .order_by(WeightMeasurement.measured_at.desc())
        .first()
    )

    if not measurement:
        return None

    # Compute gain vs first
    first = (
        WeightMeasurement.query
        .filter_by(user_id=user.id)
        .order_by(WeightMeasurement.measured_at.asc())
        .first()
    )

    gain = None
    if first and first.id != measurement.id:
        gain = round(float(measurement.weight_kg) - float(first.weight_kg), 2)

    result = measurement.to_dict()
    result["total_gain_kg"] = gain
    return result
