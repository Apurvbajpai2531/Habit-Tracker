from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from extensions import db
from models import User
from auth import register_schema, login_schema
from utils import success, error, handle_validation_errors

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
@handle_validation_errors
def register():
    payload = register_schema.load(request.get_json(force=True))

    if User.query.filter_by(email=payload["email"]).first():
        return error("Email already registered hai", 409)

    user = User(email=payload["email"])
    user.set_password(payload["password"])
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return success({"user": user.to_dict(), "access_token": token}, "Account ban gaya", 201)


@auth_bp.post("/login")
@handle_validation_errors
def login():
    payload = login_schema.load(request.get_json(force=True))
    user = User.query.filter_by(email=payload["email"]).first()

    if not user or not user.check_password(payload["password"]):
        return error("Email ya password galat hai", 401)

    token = create_access_token(identity=str(user.id))
    return success({"user": user.to_dict(), "access_token": token}, "Login successful")


@auth_bp.get("/me")
@jwt_required()
def me():
    user = User.query.get_or_404(int(get_jwt_identity()))
    return success(user.to_dict())