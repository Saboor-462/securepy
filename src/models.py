from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from extensions import db  

class DPResult(db.Model):
    __tablename__ = "dp_results"

    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.String(128), nullable=False) 
    columns = db.Column(db.Text)  
    mechanism = db.Column(db.String(64))
    epsilon = db.Column(db.Float)
    delta = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "file_id": self.file_id,
            "columns": self.columns,
            "mechanism": self.mechanism,
            "epsilon": self.epsilon,
            "delta": self.delta,
            "created_at": self.created_at.isoformat(),
        }
    
# Association table for Role-Permission
class RolePermission(db.Model):
    __tablename__ = "role_permissions"
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey("permissions.id"), primary_key=True)

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256))
    permissions = db.relationship("Permission",
                                  secondary="role_permissions",
                                  backref=db.backref("roles", lazy="dynamic"))

class Permission(db.Model):
    __tablename__ = "permissions"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True, nullable=False)  
    description = db.Column(db.String(256))

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    role = db.relationship("Role", backref=db.backref("users", lazy=True))

class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    event = db.Column(db.String(128), nullable=False)  
    route = db.Column(db.String(255))
    method = db.Column(db.String(10))
    ip = db.Column(db.String(64))
    status_code = db.Column(db.Integer, default=200)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("audit_logs", lazy=True))    

def __repr__(self):
    return f"<User {self.email}>"

