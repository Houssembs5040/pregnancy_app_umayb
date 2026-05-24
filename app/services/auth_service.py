from datetime import datetime

from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models import User, UserProfile, PregnancyProfile
from app.services.appointment_service import generate_prenatal_consultations


def register_user(data: dict) -> dict:
    phone = data.get("phone")
    password = data.get("password")
    lmp_date_str = data.get("lmp_date")

    name = data.get("name")
    email = data.get("email")
    age = data.get("age")
    city = data.get("city")
    height_cm = data.get("height_cm")

    if not phone:
        raise ValueError("phone is required")
    if not password:
        raise ValueError("password is required")
    if not lmp_date_str:
        raise ValueError("lmp_date is required")

    existing_user = User.query.filter_by(phone=phone).first()
    if existing_user:
        raise ValueError("phone already exists")

    if email:
        existing_email = UserProfile.query.filter_by(email=email).first()
        if existing_email:
            raise ValueError("email already exists")

    try:
        lmp_date = datetime.strptime(lmp_date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("lmp_date must be in YYYY-MM-DD format")

    due_date = PregnancyProfile.calculate_due_date(lmp_date)

    user = User(phone=phone)
    user.set_password(password)

    profile = UserProfile(
        user=user,
        name=name,
        email=email,
        age=age,
        city=city,
        height_cm=height_cm,
    )

    pregnancy_profile = PregnancyProfile(
        user=user,
        lmp_date=lmp_date,
        due_date=due_date,
    )

    db.session.add(user)
    db.session.add(profile)
    db.session.add(pregnancy_profile)
    db.session.flush()

    prenatal_plan = generate_prenatal_consultations(user, commit=False)

    db.session.commit()

    access_token = create_access_token(identity=str(user.id))

    return {
        "message": "user registered successfully",
        "access_token": access_token,
        "generated_prenatal_appointments_count": prenatal_plan["count"],
        "user": user.to_dict(),
        "profile": profile.to_dict(),
        "pregnancy_profile": pregnancy_profile.to_dict(),
    }


def login_user(data: dict) -> dict:
    phone = data.get("phone")
    password = data.get("password")

    if not phone:
        raise ValueError("phone is required")
    if not password:
        raise ValueError("password is required")

    user = User.query.filter_by(phone=phone).first()

    if not user or not user.check_password(password):
        raise ValueError("invalid phone or password")

    access_token = create_access_token(identity=str(user.id))

    return {
        "message": "login successful",
        "access_token": access_token,
        "user": user.to_dict(),
        "profile": user.profile.to_dict() if user.profile else None,
        "pregnancy_profile": (
            user.pregnancy_profile.to_dict() if user.pregnancy_profile else None
        ),
    }


def get_current_user_data(user: User) -> dict:
    return {
        "user": user.to_dict(),
        "profile": user.profile.to_dict() if user.profile else None,
        "pregnancy_profile": (
            user.pregnancy_profile.to_dict() if user.pregnancy_profile else None
        ),
    }


def change_password(user: User, data: dict) -> dict:
    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not current_password:
        raise ValueError("current_password is required")
    if not new_password:
        raise ValueError("new_password is required")
    if len(new_password) < 6:
        raise ValueError("new_password must be at least 6 characters")
    if not user.check_password(current_password):
        raise ValueError("current_password is incorrect")
    if current_password == new_password:
        raise ValueError("new_password must be different from current_password")

    user.set_password(new_password)
    db.session.commit()

    return {"message": "password changed successfully"}
