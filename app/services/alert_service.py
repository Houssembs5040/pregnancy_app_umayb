from datetime import datetime, UTC

from app.extensions import db
from app.models import Alert


ALLOWED_CATEGORIES = {
    "blood_pressure",
    "glucose",
    "weight",
    "fetal_movement",
    "followup",
    "system",
}

ALLOWED_SEVERITIES = {"info", "warning", "urgent"}


def create_alert(user, data: dict) -> dict:
    category = data.get("category")
    severity = data.get("severity")
    title = data.get("title")
    message = data.get("message")
    source_table = data.get("source_table")
    source_id = data.get("source_id")

    if category not in ALLOWED_CATEGORIES:
        raise ValueError(
            "category must be one of: blood_pressure, glucose, weight, fetal_movement, followup, system"
        )

    if severity not in ALLOWED_SEVERITIES:
        raise ValueError("severity must be one of: info, warning, urgent")

    if not title:
        raise ValueError("title is required")

    if not message:
        raise ValueError("message is required")

    if source_id is not None:
        try:
            source_id = int(source_id)
        except (TypeError, ValueError):
            raise ValueError("source_id must be an integer")

    alert = Alert(
        user_id=user.id,
        category=category,
        severity=severity,
        title=title,
        message=message,
        source_table=source_table,
        source_id=source_id,
        is_active=True,
    )

    db.session.add(alert)
    db.session.commit()

    return {
        "message": "alert created successfully",
        "alert": alert.to_dict(),
    }


def list_alerts(user, active_only: bool | None = None) -> dict:
    query = Alert.query.filter_by(user_id=user.id)

    if active_only is True:
        query = query.filter_by(is_active=True)
    elif active_only is False:
        query = query.filter_by(is_active=False)

    alerts = query.order_by(Alert.created_at.desc()).all()

    return {
        "count": len(alerts),
        "alerts": [alert.to_dict() for alert in alerts],
    }


def resolve_alert(user, alert_id: int) -> dict:
    alert = Alert.query.filter_by(id=alert_id, user_id=user.id).first()

    if not alert:
        raise ValueError("alert not found")

    if not alert.is_active:
        return {
            "message": "alert already resolved",
            "alert": alert.to_dict(),
        }

    alert.is_active = False
    alert.resolved_at = datetime.now(UTC).replace(tzinfo=None)

    db.session.commit()

    return {
        "message": "alert resolved successfully",
        "alert": alert.to_dict(),
    }
