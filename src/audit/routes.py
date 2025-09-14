from flask import Blueprint, jsonify
from ..models import db, AuditLog
from ..rbac.decorators import role_required

audit_bp = Blueprint("audit", __name__, url_prefix="/audit")

@audit_bp.get("/logs")
@role_required("admin")
def logs():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(100).all()
    return jsonify([{
        "id": l.id,
        "user_id": l.user_id,
        "event": l.event,
        "route": l.route,
        "method": l.method,
        "ip": l.ip,
        "status_code": l.status_code,
        "message": l.message,
        "created_at": l.created_at.isoformat()
    } for l in logs])
