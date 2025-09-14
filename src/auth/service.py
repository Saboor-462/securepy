from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token
from ..utils.security import hash_password, verify_password
from ..models import db, User, Role

def register_user(email: str, password: str, role_name: str = "user"):
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        role = Role(name=role_name, description="Default user role")
        db.session.add(role)
        db.session.commit()

    user = User(email=email, password_hash=hash_password(password), role=role)
    db.session.add(user)
    db.session.commit()
    return user

def authenticate(email: str, password: str):
    user = User.query.filter_by(email=email).first()
    if user and verify_password(password, user.password_hash) and user.is_active:
        claims = {"role": user.role.name if user.role else "user"}
        return {
            "access_token": create_access_token(identity=str(user.id), additional_claims=claims),
            "refresh_token": create_refresh_token(identity=str(user.id), additional_claims=claims),
            "user": {"id": user.id, "email": user.email, "role": claims["role"]},
        }
    return None
