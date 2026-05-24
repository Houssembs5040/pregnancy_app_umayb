from datetime import datetime, timedelta

from app.extensions import db
from app.models.fetal_movement import FetalMovementSession


# ─── Constants ───────────────────────────────────────────────────────────────
_MIN_ACTIVATION_WEEK = 28          # Module activated at 28 SA
_LOW_MOVEMENT_THRESHOLD = 10       # < 10 movements in 2h → alert
_SESSION_DURATION_HOURS = 2        # Standard counting window
_ABSENCE_ALERT_HOURS = 12          # No session for > 12h → urgent alert


def _get_gestational_week(user) -> int | None:
    pregnancy = user.pregnancy_profile
    if not pregnancy:
        return None
    return pregnancy.gestational_weeks()


def _check_activation(user):
    """Raise ValueError if user is not yet at 28 SA."""
    sa = _get_gestational_week(user)
    if sa is None:
        raise ValueError("pregnancy profile not found")
    if sa < _MIN_ACTIVATION_WEEK:
        raise ValueError(
            f"Le suivi des mouvements fœtaux est activé à partir de 28 SA "
            f"(vous êtes à {sa} SA)."
        )


def start_session(user) -> dict:
    """Start a new fetal movement counting session."""
    _check_activation(user)

    # Check if there is already an open session
    open_session = (
        FetalMovementSession.query
        .filter(
            FetalMovementSession.user_id == user.id,
            FetalMovementSession.session_end.is_(None),
        )
        .first()
    )

    if open_session:
        raise ValueError(
            "Une session est déjà en cours. "
            "Terminez-la avant d'en démarrer une nouvelle."
        )

    sa = _get_gestational_week(user)

    session = FetalMovementSession(
        user_id=user.id,
        count=0,
        session_start=datetime.utcnow(),
        gestational_week=sa,
    )

    db.session.add(session)
    db.session.commit()

    return {
        "message": "session de comptage démarrée",
        "session": session.to_dict(),
    }


def increment_count(user, session_id: int) -> dict:
    """Increment movement count for an open session."""
    _check_activation(user)

    session = FetalMovementSession.query.filter_by(
        id=session_id, user_id=user.id
    ).first()

    if not session:
        raise ValueError("session not found")

    if session.session_end is not None:
        raise ValueError("Cette session est déjà terminée.")

    session.count += 1
    db.session.commit()

    return {
        "message": "mouvement enregistré",
        "session": session.to_dict(),
    }


def end_session(user, session_id: int, data: dict) -> dict:
    """End a counting session and trigger alerts if needed."""
    _check_activation(user)

    session = FetalMovementSession.query.filter_by(
        id=session_id, user_id=user.id
    ).first()

    if not session:
        raise ValueError("session not found")

    if session.session_end is not None:
        raise ValueError("Cette session est déjà terminée.")

    # Allow override of count and note
    final_count = data.get("count")
    note = data.get("note")

    if final_count is not None:
        try:
            final_count = int(final_count)
        except (TypeError, ValueError):
            raise ValueError("count must be an integer")
        if final_count < 0:
            raise ValueError("count must be >= 0")
        session.count = final_count

    if note is not None:
        session.note = note

    session.session_end = datetime.utcnow()

    db.session.flush()

    alerts = _trigger_movement_alerts(user, session)

    db.session.commit()

    return {
        "message": "session terminée",
        "session": session.to_dict(),
        "alerts_triggered": len(alerts),
    }


def check_absence_alert(user) -> dict:
    """
    Check if there has been no session in > 12h at SA ≥ 28.
    This can be called periodically by a scheduler or on demand.
    """
    sa = _get_gestational_week(user)
    if sa is None or sa < _MIN_ACTIVATION_WEEK:
        return {"alert_needed": False}

    last_session = (
        FetalMovementSession.query
        .filter_by(user_id=user.id)
        .order_by(FetalMovementSession.session_start.desc())
        .first()
    )

    threshold = datetime.utcnow() - timedelta(hours=_ABSENCE_ALERT_HOURS)

    if last_session is None or last_session.session_start < threshold:
        from app.services.alert_service import create_alert
        alert = create_alert(user, {
            "category": "fetal_movement",
            "severity": "urgent",
            "title": "Absence de mouvements fœtaux",
            "message": (
                "Aucun mouvement fœtal enregistré depuis plus de 12h. "
                "Si vous ne sentez pas bouger votre bébé, "
                "consultez immédiatement."
            ),
        })
        db.session.commit()
        return {"alert_needed": True, "alert": alert}

    return {"alert_needed": False}


def _trigger_movement_alerts(user, session: FetalMovementSession) -> list[dict]:
    """Alert if count < 10 in a 2h session."""
    from app.services.alert_service import create_alert

    alerts_created = []
    duration = session.duration_minutes

    # Only evaluate sessions that ran for at least 60 minutes
    if duration and duration >= 60 and session.count < _LOW_MOVEMENT_THRESHOLD:
        alert = create_alert(user, {
            "category": "fetal_movement",
            "severity": "urgent",
            "title": "Diminution des mouvements fœtaux",
            "message": (
                f"Seulement {session.count} mouvements perçus en "
                f"{int(duration)} minutes. "
                "Consultez immédiatement si votre bébé bouge peu."
            ),
            "source_table": "fetal_movement_sessions",
            "source_id": session.id,
        })
        alerts_created.append(alert)

    return alerts_created


def list_sessions(user) -> dict:
    sessions = (
        FetalMovementSession.query
        .filter_by(user_id=user.id)
        .order_by(FetalMovementSession.session_start.desc())
        .all()
    )

    return {
        "count": len(sessions),
        "sessions": [s.to_dict() for s in sessions],
    }


def get_open_session(user) -> dict | None:
    session = (
        FetalMovementSession.query
        .filter(
            FetalMovementSession.user_id == user.id,
            FetalMovementSession.session_end.is_(None),
        )
        .first()
    )

    return session.to_dict() if session else None
