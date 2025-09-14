import logging
from logging.handlers import RotatingFileHandler
from flask import request
from ..models import db, AuditLog
from flask_jwt_extended import get_jwt, verify_jwt_in_request

def init_audit(app):
    # File logger
    handler = RotatingFileHandler("securepy.log", maxBytes=1024*1024, backupCount=3)
    handler.setLevel(app.config.get("LOG_LEVEL", "INFO"))
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    app.logger.addHandler(handler)

    @app.after_request
    def after(resp):
        try:
            # If there is no valid JWT, we continue and log with user_id = None.
            user_id = None
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                # identity is normally in the "sub" claim
                user_id = claims.get("sub")
            except Exception:
                # no JWT or invalid token — that's ok for auditing
                user_id = None

            log = AuditLog(
                user_id=int(user_id) if user_id else None,
                event="http_request",
                route=request.path,
                method=request.method,
                ip=request.remote_addr,
                status_code=resp.status_code,
                message=(resp.get_data(as_text=True) or "")[:500]
            )
            db.session.add(log)
            db.session.commit()
        except Exception:
            db.session.rollback()
        return resp
