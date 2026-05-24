from datetime import datetime

from app.extensions import db
from app.models import UserProfile, PregnancyProfile
from app.services.appointment_service import generate_prenatal_consultations


def get_profile_data(user) -> dict:
    return {
        "user": user.to_dict(),
        "profile": user.profile.to_dict() if user.profile else None,
        "pregnancy_profile": (
            user.pregnancy_profile.to_dict() if user.pregnancy_profile else None
        ),
    }


def update_profile_data(user, data: dict) -> dict:
    profile = user.profile
    pregnancy_profile = user.pregnancy_profile
    prenatal_plan = None

    if profile is None:
        profile = UserProfile(user=user)

    name = data.get("name")
    email = data.get("email")
    age = data.get("age")
    city = data.get("city")
    height_cm = data.get("height_cm")
    preferred_language = data.get("preferred_language")
    theme = data.get("theme")
    lmp_date_str = data.get("lmp_date")

    if email is not None:
        existing_email = UserProfile.query.filter(
            UserProfile.email == email,
            UserProfile.user_id != user.id
        ).first()
        if existing_email:
            raise ValueError("email already exists")
        profile.email = email

    if name is not None:
        profile.name = name

    if age is not None:
        if not isinstance(age, int) or age <= 0:
            raise ValueError("age must be a positive integer")
        profile.age = age

    if city is not None:
        profile.city = city

    if height_cm is not None:
        try:
            height_cm = float(height_cm)
        except (TypeError, ValueError):
            raise ValueError("height_cm must be a valid number")

        if height_cm <= 0:
            raise ValueError("height_cm must be greater than 0")

        profile.height_cm = height_cm

    if preferred_language is not None:
        profile.preferred_language = preferred_language

    if theme is not None:
        profile.theme = theme

    if lmp_date_str is not None:
        try:
            lmp_date = datetime.strptime(lmp_date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("lmp_date must be in YYYY-MM-DD format")

        if pregnancy_profile is None:
            pregnancy_profile = PregnancyProfile(user=user)

        pregnancy_profile.lmp_date = lmp_date
        pregnancy_profile.due_date = PregnancyProfile.calculate_due_date(lmp_date)

        db.session.add(pregnancy_profile)
        db.session.flush()

        prenatal_plan = generate_prenatal_consultations(user, commit=False)

    db.session.add(profile)
    db.session.commit()

    response = {
        "message": "profile updated successfully",
        "user": user.to_dict(),
        "profile": profile.to_dict(),
        "pregnancy_profile": (
            pregnancy_profile.to_dict() if pregnancy_profile else None
        ),
    }

    if prenatal_plan is not None:
        response["generated_prenatal_appointments_count"] = prenatal_plan["count"]

    return response
