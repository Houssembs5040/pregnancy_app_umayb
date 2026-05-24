from datetime import datetime

from app.extensions import db
from app.models.glucose import GlucoseMeasurement


# ─── Seuils médicaux (spec-defined, g/L) ────────────────────────────────────
_FASTING_THRESHOLD_WARNING = 0.92   # ≥ 0.92 g/L à jeun → contrôle recommandé
_FASTING_THRESHOLD_URGENT = 1.26    # ≥ 1.26 g/L à jeun → diabète gestationnel suspecté
_POSTPRANDIAL_THRESHOLD = 1.20      # ≥ 1.20 g/L post-prandial → alerte


def _get_gestational_week(user) -> int | None:
    pregnancy = user.pregnancy_profile
    if not pregnancy:
        return None
    return pregnancy.gestational_weeks()


def _trigger_glucose_alerts(user, measurement: GlucoseMeasurement) -> list[dict]:
    """
    Alert logic per spec:
      - à jeun ≥ 0.92 g/L                     → warning
      - à jeun ≥ 1.26 g/L OR post-prandial ≥ 1.20 g/L → urgent
    """
    from app.services.alert_service import create_alert

    alerts_created = []
    fasting = float(measurement.fasting_value)
    postprandial = (
        float(measurement.postprandial_value)
        if measurement.postprandial_value is not None
        else None
    )

    # Urgent: fasting too high or postprandial too high
    if fasting >= _FASTING_THRESHOLD_URGENT or (
        postprandial is not None and postprandial >= _POSTPRANDIAL_THRESHOLD
    ):
        msg_parts = []
        if fasting >= _FASTING_THRESHOLD_URGENT:
            msg_parts.append(f"glycémie à jeun de {fasting:.2f} g/L")
        if postprandial is not None and postprandial >= _POSTPRANDIAL_THRESHOLD:
            msg_parts.append(f"glycémie post-prandiale de {postprandial:.2f} g/L")

        alert = create_alert(user, {
            "category": "glucose",
            "severity": "urgent",
            "title": "Diabète gestationnel suspecté",
            "message": (
                f"Valeur anormale détectée : {', '.join(msg_parts)}. "
                "Consultez pour dépistage du diabète gestationnel."
            ),
            "source_table": "glucose_measurements",
            "source_id": measurement.id,
        })
        alerts_created.append(alert)

    elif fasting >= _FASTING_THRESHOLD_WARNING:
        alert = create_alert(user, {
            "category": "glucose",
            "severity": "warning",
            "title": "Glycémie à jeun limite",
            "message": (
                f"Votre glycémie à jeun est de {fasting:.2f} g/L "
                f"(seuil : {_FASTING_THRESHOLD_WARNING} g/L). "
                "Un contrôle est recommandé."
            ),
            "source_table": "glucose_measurements",
            "source_id": measurement.id,
        })
        alerts_created.append(alert)

    return alerts_created


def add_glucose(user, data: dict) -> dict:
    fasting_value = data.get("fasting_value")
    postprandial_value = data.get("postprandial_value")
    note = data.get("note")
    measured_at_str = data.get("measured_at")

    if fasting_value is None:
        raise ValueError("fasting_value is required (g/L)")

    try:
        fasting_value = float(fasting_value)
    except (TypeError, ValueError):
        raise ValueError("fasting_value must be a valid number (g/L)")

    if fasting_value <= 0 or fasting_value > 10:
        raise ValueError("fasting_value must be between 0 and 10 g/L")

    if postprandial_value is not None:
        try:
            postprandial_value = float(postprandial_value)
        except (TypeError, ValueError):
            raise ValueError("postprandial_value must be a valid number (g/L)")

        if postprandial_value <= 0 or postprandial_value > 10:
            raise ValueError("postprandial_value must be between 0 and 10 g/L")

    measured_at = datetime.utcnow()
    if measured_at_str:
        try:
            measured_at = datetime.fromisoformat(measured_at_str)
        except ValueError:
            raise ValueError("measured_at must be a valid ISO datetime")

    gestational_week = _get_gestational_week(user)

    measurement = GlucoseMeasurement(
        user_id=user.id,
        fasting_value=fasting_value,
        postprandial_value=postprandial_value,
        gestational_week=gestational_week,
        note=note,
        measured_at=measured_at,
    )

    db.session.add(measurement)
    db.session.flush()

    alerts = _trigger_glucose_alerts(user, measurement)

    db.session.commit()

    return {
        "message": "glucose measurement recorded",
        "measurement": measurement.to_dict(),
        "alerts_triggered": len(alerts),
    }


def list_glucose(user) -> dict:
    measurements = (
        GlucoseMeasurement.query
        .filter_by(user_id=user.id)
        .order_by(GlucoseMeasurement.measured_at.asc())
        .all()
    )

    return {
        "count": len(measurements),
        "measurements": [m.to_dict() for m in measurements],
    }


def get_latest_glucose(user) -> dict | None:
    measurement = (
        GlucoseMeasurement.query
        .filter_by(user_id=user.id)
        .order_by(GlucoseMeasurement.measured_at.desc())
        .first()
    )

    return measurement.to_dict() if measurement else None
