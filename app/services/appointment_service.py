from datetime import datetime, timedelta

from app.extensions import db
from app.models import Appointment, AppointmentFollowup


ALLOWED_TYPES = {"consultation", "analyse", "echographie"}
ALLOWED_STATUSES = {"planned", "done", "missed", "postponed", "cancelled"}
ALLOWED_OUTCOMES = {"normal", "anomaly", "unknown"}

PRENATAL_CONSULTATIONS = [
    {
        "target_week": 12,
        "title": "Consultation prénatale 1",
        "notes": (
            "Avant 12 SA : confirmation de la grossesse, datation, "
            "bilan sanguin complet (groupe sanguin + Rh, NFS, sérologies, glycémie à jeun), "
            "mesure TA, poids initial et première échographie."
        ),
    },
    {
        "target_week": 16,
        "title": "Consultation prénatale 2",
        "notes": (
            "4ème mois (vers 16 SA) : surveillance tensionnelle, "
            "suivi du poids et examen clinique général."
        ),
    },
    {
        "target_week": 20,
        "title": "Consultation prénatale 3",
        "notes": (
            "5ème mois (vers 20 SA) : deuxième échographie morphologique "
            "(morphologie fœtale, placenta, liquide amniotique)."
        ),
    },
    {
        "target_week": 24,
        "title": "Consultation prénatale 4",
        "notes": (
            "6ème mois (vers 24 SA) : surveillance mensuelle — "
            "TA, poids, hauteur utérine, mouvements fœtaux."
        ),
    },
    {
        "target_week": 28,
        "title": "Consultation prénatale 5",
        "notes": (
            "7ème mois (vers 28 SA) : vérification de la croissance fœtale, "
            "bilan biologique (NFS, HGPO , RAI) ,"
            "Vaccination DtCa (diphterie_ tétanos _coqueluche)"
        ),
    },
    {
        "target_week": 32,
        "title": "Consultation prénatale 6",
        "notes": (
            "8ème mois (vers 32 SA) : troisième échographie "
            "prélèvement vaginal et ECBU (examen d’urine)"
        ),
    },
    {
        "target_week": 36,
        "title": "Consultation prénatale 7",
        "notes": (
            "9ème mois (vers 36 SA) : préparation finale à l'accouchement, "
            "examen du bassin, présentation définitive, conseils sur les signes de travail."
        ),
    },
]

# Analyses sérologiques mensuelles
# Toxo  : tous les mois jusqu'à la fin de la grossesse (~40 SA)
# Rubéole: tous les mois jusqu'à 18 SA (si non immune)
MONTHLY_ANALYSES = [
    {
        "type": "toxo",
        "max_week": 40,
        "title_template": "Sérologie toxoplasmose — mois {month}",
        "notes": (
            "Rappel : contrôle de la sérologie toxoplasmose à répéter chaque mois "
            "en cas de séronégativité, jusqu'à l'accouchement."
        ),
    },
    {
        "type": "rubeole",
        "max_week": 18,
        "title_template": "Sérologie rubéole — mois {month}",
        "notes": (
            "Rappel : contrôle de la sérologie rubéole à répéter chaque mois "
            "jusqu'à 18 SA en cas de séronégativité."
        ),
    },
]


def _parse_date(date_str: str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("appointment_date must be in YYYY-MM-DD format")


def _parse_time(time_str: str | None):
    if time_str in (None, ""):
        return None

    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue

    raise ValueError("appointment_time must be in HH:MM or HH:MM:SS format")


def _serialize_appointment(appointment: Appointment) -> dict:
    return appointment.to_dict()


def _prenatal_date_from_lmp(lmp_date, target_week: int):
    return lmp_date + timedelta(weeks=target_week)


def generate_prenatal_consultations(user, commit: bool = True) -> dict:
    pregnancy_profile = user.pregnancy_profile
    if not pregnancy_profile:
        raise ValueError("pregnancy profile not found")

    target_weeks = [item["target_week"] for item in PRENATAL_CONSULTATIONS]

    existing_auto_appointments = Appointment.query.filter(
        Appointment.user_id == user.id,
        Appointment.source == "auto",
        Appointment.type == "consultation",
        Appointment.gestational_week_target.in_(target_weeks),
    ).all()

    existing_by_week = {
        appointment.gestational_week_target: appointment
        for appointment in existing_auto_appointments
    }

    generated = []

    for item in PRENATAL_CONSULTATIONS:
        target_week = item["target_week"]
        scheduled_date = _prenatal_date_from_lmp(
            pregnancy_profile.lmp_date,
            target_week,
        )

        appointment = existing_by_week.get(target_week)

        if appointment is None:
            appointment = Appointment(
                user_id=user.id,
                type="consultation",
                source="auto",
                status="planned",
                gestational_week_target=target_week,
            )
            db.session.add(appointment)

        if appointment.status not in {"done", "cancelled"}:
            appointment.title = item["title"]
            appointment.appointment_date = scheduled_date
            appointment.appointment_time = None
            appointment.location = None
            appointment.doctor_name = None
            appointment.notes = item["notes"]
            appointment.source = "auto"
            appointment.type = "consultation"
            appointment.gestational_week_target = target_week

        generated.append(appointment)

    if commit:
        db.session.commit()
    else:
        db.session.flush()

    return {
        "message": "prenatal consultations generated successfully",
        "count": len(generated),
        "appointments": [_serialize_appointment(a) for a in generated],
    }


def generate_monthly_analyses(user, commit: bool = True) -> dict:
    """Generate monthly toxo & rubéole serology reminders as 'analyse' appointments.

    - Toxoplasmosis: every 4 weeks from week 4 up to week 40 (full pregnancy).
    - Rubéole      : every 4 weeks from week 4 up to week 18 SA.
    Appointments are idempotent: existing auto records are updated, not duplicated.
    """
    pregnancy_profile = user.pregnancy_profile
    if not pregnancy_profile:
        raise ValueError("pregnancy profile not found")

    generated = []

    for analysis in MONTHLY_ANALYSES:
        analysis_type = analysis["type"]
        max_week = analysis["max_week"]
        title_template = analysis["title_template"]
        notes = analysis["notes"]

        # Build target weeks: 4, 8, 12, … up to max_week
        target_weeks = list(range(4, max_week + 1, 4))

        # Fetch all existing auto analyse records for this analysis type
        existing = Appointment.query.filter(
            Appointment.user_id == user.id,
            Appointment.source == "auto",
            Appointment.type == "analyse",
            Appointment.notes.like(f"%{analysis_type}%"),
            Appointment.gestational_week_target.in_(target_weeks),
        ).all()

        existing_by_week = {
            a.gestational_week_target: a for a in existing
        }

        for month_index, target_week in enumerate(target_weeks, start=1):
            scheduled_date = _prenatal_date_from_lmp(
                pregnancy_profile.lmp_date, target_week
            )

            appointment = existing_by_week.get(target_week)

            if appointment is None:
                appointment = Appointment(
                    user_id=user.id,
                    type="analyse",
                    source="auto",
                    status="planned",
                    gestational_week_target=target_week,
                )
                db.session.add(appointment)

            if appointment.status not in {"done", "cancelled"}:
                appointment.title = title_template.format(month=month_index)
                appointment.appointment_date = scheduled_date
                appointment.appointment_time = None
                appointment.location = None
                appointment.doctor_name = None
                appointment.notes = notes
                appointment.source = "auto"
                appointment.type = "analyse"
                appointment.gestational_week_target = target_week

            generated.append(appointment)

    if commit:
        db.session.commit()
    else:
        db.session.flush()

    return {
        "message": "monthly analyses generated successfully",
        "count": len(generated),
        "appointments": [_serialize_appointment(a) for a in generated],
    }


def list_appointments(user, status=None) -> dict:
    query = Appointment.query.filter_by(user_id=user.id)

    if status:
        if status not in ALLOWED_STATUSES:
            raise ValueError("invalid status")
        query = query.filter_by(status=status)

    appointments = query.order_by(
        Appointment.appointment_date.asc(),
        Appointment.appointment_time.asc()
    ).all()

    return {
        "count": len(appointments),
        "appointments": [_serialize_appointment(a) for a in appointments],
    }


def get_appointment_by_id(user, appointment_id: int) -> dict:
    appointment = Appointment.query.filter_by(
        id=appointment_id,
        user_id=user.id
    ).first()

    if not appointment:
        raise ValueError("appointment not found")

    return _serialize_appointment(appointment)


def create_appointment(user, data: dict) -> dict:
    appointment_type = data.get("type")
    title = data.get("title")
    appointment_date_str = data.get("appointment_date")
    appointment_time_str = data.get("appointment_time")
    location = data.get("location")
    doctor_name = data.get("doctor_name")
    notes = data.get("notes")
    source = data.get("source", "manual")
    status = data.get("status", "planned")
    gestational_week_target = data.get("gestational_week_target")

    if appointment_type not in ALLOWED_TYPES:
        raise ValueError("type must be one of: consultation, analyse, echographie")

    if not title:
        raise ValueError("title is required")

    if not appointment_date_str:
        raise ValueError("appointment_date is required")

    if source not in {"auto", "manual"}:
        raise ValueError("source must be 'auto' or 'manual'")

    if status not in ALLOWED_STATUSES:
        raise ValueError("invalid status")

    appointment_date = _parse_date(appointment_date_str)
    appointment_time = _parse_time(appointment_time_str)

    if gestational_week_target is not None:
        if not isinstance(gestational_week_target, int) or gestational_week_target < 0:
            raise ValueError("gestational_week_target must be a non-negative integer")

    appointment = Appointment(
        user_id=user.id,
        type=appointment_type,
        title=title,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        location=location,
        doctor_name=doctor_name,
        notes=notes,
        source=source,
        status=status,
        gestational_week_target=gestational_week_target,
    )

    db.session.add(appointment)
    db.session.commit()

    return {
        "message": "appointment created successfully",
        "appointment": _serialize_appointment(appointment),
    }


def update_appointment(user, appointment_id: int, data: dict) -> dict:
    appointment = Appointment.query.filter_by(
        id=appointment_id,
        user_id=user.id
    ).first()

    if not appointment:
        raise ValueError("appointment not found")

    if "type" in data:
        if data["type"] not in ALLOWED_TYPES:
            raise ValueError("type must be one of: consultation, analyse, echographie")
        appointment.type = data["type"]

    if "title" in data:
        if not data["title"]:
            raise ValueError("title cannot be empty")
        appointment.title = data["title"]

    if "appointment_date" in data:
        appointment.appointment_date = _parse_date(data["appointment_date"])

    if "appointment_time" in data:
        appointment.appointment_time = _parse_time(data["appointment_time"])

    if "location" in data:
        appointment.location = data["location"]

    if "doctor_name" in data:
        appointment.doctor_name = data["doctor_name"]

    if "notes" in data:
        appointment.notes = data["notes"]

    if "source" in data:
        if data["source"] not in {"auto", "manual"}:
            raise ValueError("source must be 'auto' or 'manual'")
        appointment.source = data["source"]

    if "status" in data:
        if data["status"] not in ALLOWED_STATUSES:
            raise ValueError("invalid status")
        appointment.status = data["status"]

    if "gestational_week_target" in data:
        value = data["gestational_week_target"]
        if value is not None and (not isinstance(value, int) or value < 0):
            raise ValueError("gestational_week_target must be a non-negative integer")
        appointment.gestational_week_target = value

    db.session.commit()

    return {
        "message": "appointment updated successfully",
        "appointment": _serialize_appointment(appointment),
    }


def complete_appointment(user, appointment_id: int, data: dict) -> dict:
    appointment = Appointment.query.filter_by(
        id=appointment_id,
        user_id=user.id
    ).first()

    if not appointment:
        raise ValueError("appointment not found")

    outcome_type = data.get("outcome_type")
    comment = data.get("comment")

    if outcome_type not in {"normal", "anomaly"}:
        raise ValueError("outcome_type must be 'normal' or 'anomaly'")

    followup = AppointmentFollowup.query.filter_by(
        appointment_id=appointment.id,
        user_id=user.id
    ).first()

    if followup is None:
        followup = AppointmentFollowup(
            appointment_id=appointment.id,
            user_id=user.id,
            was_completed=True,
        )
        db.session.add(followup)

    followup.was_completed = True
    followup.outcome_type = outcome_type
    followup.comment = comment
    followup.completed_at = datetime.utcnow()

    appointment.status = "done"

    db.session.commit()

    return {
        "message": "appointment completed successfully",
        "appointment": _serialize_appointment(appointment),
        "followup": followup.to_dict(),
    }


def get_appointment_history(user) -> dict:
    history = AppointmentFollowup.query.filter_by(user_id=user.id).order_by(
        AppointmentFollowup.completed_at.desc()
    ).all()

    return {
        "count": len(history),
        "history": [
            {
                "followup": item.to_dict(),
                "appointment": item.appointment.to_dict() if item.appointment else None,
            }
            for item in history
        ],
    }


def delete_appointment(user, appointment_id: int) -> dict:
    appointment = Appointment.query.filter_by(
        id=appointment_id,
        user_id=user.id
    ).first()

    if not appointment:
        raise ValueError("appointment not found")

    db.session.delete(appointment)
    db.session.commit()

    return {
        "message": "appointment deleted successfully"
    }
