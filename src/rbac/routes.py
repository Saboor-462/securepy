from flask import Blueprint, jsonify
from .decorators import role_required

rbac_bp = Blueprint("rbac", __name__, url_prefix="/rbac")

@rbac_bp.get("/admin-only")
@role_required("admin")
def admin_only():
    return jsonify(message="Welcome, admin!")
