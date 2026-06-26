from functools import wraps
from flask import jsonify
from marshmallow import ValidationError


def success(data=None, message="ok", status=200):
    return jsonify({"success": True, "message": message, "data": data}), status


def error(message="Something went wrong", status=400, details=None):
    payload = {"success": False, "message": message}
    if details:
        payload["details"] = details
    return jsonify(payload), status


def handle_validation_errors(fn):
    """Decorator: marshmallow validation errors ko clean JSON response me convert karta hai."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ValidationError as e:
            return error("Validation failed", 422, e.messages)
    return wrapper