from functools import wraps
from flask import jsonify
from marshmallow import ValidationError


# ---------------- Response Helpers ----------------
def success(data=None, message="ok", status=200):
    return jsonify({
        "success": True,
        "message": message,
        "data": data
    }), status


def error(message="Something went wrong", status=400, details=None):
    payload = {
        "success": False,
        "message": message
    }
    if details:
        payload["details"] = details
    return jsonify(payload), status


# ---------------- Validation Decorator ----------------
def handle_validation_errors(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ValidationError as e:
            return error("Validation failed", 422, e.messages)
    return wrapper


# ---------------- STREAK LOGIC (MISSING FIX) ----------------
def calculate_streaks(dates):
    """
    Returns:
        current_streak, longest_streak
    """

    if not dates:
        return 0, 0

    # remove duplicates + sort
    dates = sorted(set(dates))

    longest = 1
    current = 1
    temp = 1

    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            temp += 1
        else:
            longest = max(longest, temp)
            temp = 1

    longest = max(longest, temp)
    current = temp

    return current, longest