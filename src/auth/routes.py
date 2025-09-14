from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, User
from .service import register_user, authenticate

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.post("/register")
def register():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")
    if not email or not password:
        return jsonify({"error": "email and password required"}), 400
    
    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "Email already registered.You can’t register multiple accounts with the same email."}), 400
    
    try:
        user = register_user(email, password, role)
        return jsonify({"message": "registered", "user": {"id": user.id, "email": user.email, "role": user.role.name}}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    res = authenticate(email, password)
    if not res:
        return jsonify({"error": "Invalid credentials"}), 401
    return jsonify(res), 200

@auth_bp.get("/me")
@jwt_required()
def me():
    uid = get_jwt_identity()
    user = User.query.get(int(uid))
    return jsonify({"id": user.id, "email": user.email, "role": user.role.name if user.role else None})
