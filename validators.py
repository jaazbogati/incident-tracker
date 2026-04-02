#--------input normalizing--------------------

def normalize_status(value):
    if not isinstance(value, str):
        return None
    return value.strip().title()

def normalize_severity(value):
    if not isinstance(value, str):
        return None
    return value.strip().title()

#------------Input Validation--------------------------------

def validate_required_fields(data, required_fields):
    for field in required_fields:
        if not str(data.get(field, "")).strip():
            return f"{field} is required and cannot be empty"
    return None

def validate_enum_field(value, allowed_values, field_name):
    if value not in allowed_values:
        return f"Invalid {field_name}"
    return None

#-----------Allowed Statuses and severities-------------

ALLOWED_STATUSES = {"Open", "In Progress", "Closed"}
ALLOWED_SEVERITIES = {"Low", "Medium", "High", "Critical"}

