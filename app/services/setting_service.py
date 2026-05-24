from app.extensions import db
from app.models.setting import UserSetting

_BOOL_FIELDS = {
    "notifications_enabled",
    "reminder_7_days",
    "reminder_3_days",
    "reminder_same_day",
    "reminder_2_hours",
}


def _get_or_create_settings(user) -> UserSetting:
    setting = UserSetting.query.filter_by(user_id=user.id).first()
    if not setting:
        setting = UserSetting(user_id=user.id)
        db.session.add(setting)
    return setting


def get_settings(user) -> dict:
    setting = _get_or_create_settings(user)
    db.session.commit()
    return {"settings": setting.to_dict()}


def update_settings(user, data: dict) -> dict:
    setting = _get_or_create_settings(user)

    for field in _BOOL_FIELDS:
        if field in data:
            value = data[field]
            if not isinstance(value, bool):
                raise ValueError(f"'{field}' must be a boolean (true/false)")
            setattr(setting, field, value)

    db.session.commit()
    return {
        "message": "settings updated successfully",
        "settings": setting.to_dict(),
    }
