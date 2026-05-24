def get_current_pregnancy_data(user) -> dict:
    pregnancy_profile = user.pregnancy_profile

    if not pregnancy_profile:
        raise ValueError("pregnancy profile not found")

    week_info = pregnancy_profile.gestational_week_and_days()
    total_days = max(pregnancy_profile.gestational_days(), 0)

    return {
        "user_id": user.id,
        "lmp_date": pregnancy_profile.lmp_date.isoformat(),
        "due_date": pregnancy_profile.due_date.isoformat(),
        "gestational_age": {
            "weeks": week_info["weeks"],
            "days": week_info["days"],
            "display": f"{week_info['weeks']} SA + {week_info['days']} jours",
        },
        "trimester": pregnancy_profile.trimester(),
        "progress_percentage": pregnancy_profile.progress_percentage(),
        "gestational_days_total": total_days,
    }
