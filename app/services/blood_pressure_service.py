from datetime import datetime

from app.extensions import db
from app.models.blood_pressure import BloodPressureMeasurement


# ─── Threshold constants (spec-defined) ────────────────────────────────────
_THRESHOLD_WARNING_SYSTOLIC = 140
_THRESHOLD_WARNING_DIASTOLIC = 90
_THRESHOLD_URGENT_SYSTOLIC = 160
_THRESHOLD_URGENT_DIASTOLIC = 110
_PREECLAMPSIA_MIN_WEEK = 20


def _get_gestational_week(user) -> int | None:
    pregnancy = user.pregnancy_profile
    if not pregnancy:
        return None
    return pregnancy.gestational_weeks()


def _trigger_bp_alerts(user, measurement: BloodPressureMeasurement) -> list[dict]:
    """
    Apply hypertension and pre-eclampsia alert logic per spec:
      - TA ≥ 140/90       → warning  "Tension élevée"
      - TA ≥ 160/110      → urgent   "Urgence hypertensive"
      - elevated + SA > 20 → urgent  "Risque prééclampsie"
    """
    from app.services.alert_service import create_alert

    alerts_created = []
    s = measurement.systolic
    d = measurement.diastolic
    sa = measurement.gestational_week or 0

    is_high = s >= _THRESHOLD_WARNING_SYSTOLIC or d >= _THRESHOLD_WARNING_DIASTOLIC
    is_urgent = s >= _THRESHOLD_URGENT_SYSTOLIC or d >= _THRESHOLD_URGENT_DIASTOLIC

    if is_urgent:
        alert = create_alert(user, {
            "category": "blood_pressure",
            "severity": "urgent",
            "title": "Urgence hypertensive",
            "message": (
                f"Votre tension ({s}/{d} mmHg) est très élevée. "
                "Rendez-vous aux urgences immédiatement."
            ),
            "source_table": "blood_pressure_measurements",
            "source_id": measurement.id,
        })
        alerts_created.append(alert)

    elif is_high:
        alert = create_alert(user, {
            "category": "blood_pressure",
            "severity": "warning",
            "title": "Tension artérielle élevée",
            "message": (
                f"Votre tension ({s}/{d} mmHg) est élevée. "
                "Surveillez votre tension et consultez si la persistance."
            ),
            "source_table": "blood_pressure_measurements",
            "source_id": measurement.id,
        })
        alerts_created.append(alert)

    # Pre-eclampsia risk: elevated BP after 20 SA
    if is_high and sa > _PREECLAMPSIA_MIN_WEEK:
        alert = create_alert(user, {
            "category": "blood_pressure",
            "severity": "urgent",
            "title": "Risque de prééclampsie",
            "message": (
                f"Tension élevée ({s}/{d} mmHg) à {sa} SA. "
                "Ce signe peut indiquer une prééclampsie. "
                "Consultez votre médecin rapidement."
            ),
            "source_table": "blood_pressure_measurements",
            "source_id": measurement.id,
        })
        alerts_created.append(alert)

    return alerts_created


def add_blood_pressure(user, data: dict) -> dict:
    systolic = data.get("systolic")
    diastolic = data.get("diastolic")
    note = data.get("note")
    measured_at_str = data.get("measured_at")

    if systolic is None:
        raise ValueError("systolic is required")
    if diastolic is None:
        raise ValueError("diastolic is required")

    try:
        systolic = int(systolic)
        diastolic = int(diastolic)
    except (TypeError, ValueError):
        raise ValueError("systolic and diastolic must be integers")

    if not (40 <= systolic <= 300):
        raise ValueError("systolic must be between 40 and 300 mmHg")
    if not (20 <= diastolic <= 200):
        raise ValueError("diastolic must be between 20 and 200 mmHg")

    measured_at = datetime.utcnow()
    if measured_at_str:
        try:
            measured_at = datetime.fromisoformat(measured_at_str)
        except ValueError:
            raise ValueError("measured_at must be a valid ISO datetime")

    gestational_week = _get_gestational_week(user)

    measurement = BloodPressureMeasurement(
        user_id=user.id,
        systolic=systolic,
        diastolic=diastolic,
        gestational_week=gestational_week,
        note=note,
        measured_at=measured_at,
    )

    db.session.add(measurement)
    db.session.flush()

    alerts = _trigger_bp_alerts(user, measurement)

    db.session.commit()

    return {
        "message": "blood pressure recorded",
        "measurement": measurement.to_dict(),
        "alerts_triggered": len(alerts),
    }


def list_blood_pressure(user) -> dict:
    measurements = (
        BloodPressureMeasurement.query
        .filter_by(user_id=user.id)
        .order_by(BloodPressureMeasurement.measured_at.asc())
        .all()
    )

    return {
        "count": len(measurements),
        "measurements": [m.to_dict() for m in measurements],
    }


def get_latest_blood_pressure(user) -> dict | None:
    measurement = (
        BloodPressureMeasurement.query
        .filter_by(user_id=user.id)
        .order_by(BloodPressureMeasurement.measured_at.desc())
        .first()
    )

    return measurement.to_dict() if measurement else None
