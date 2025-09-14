
from app import create_app
from extensions import db
from src.models import Role, Permission

def seed_roles_permissions():
    # Define permissions
    permissions = {
        "manage_users": "Can create, update, delete users",
        "view_audit": "Can view audit logs",
        "access_privacy": "Can run privacy queries",
        "basic_access": "Basic user access"
    }

    # Create permissions if not exist
    for code, desc in permissions.items():
        if not Permission.query.filter_by(code=code).first():
            db.session.add(Permission(code=code, description=desc))

    db.session.commit()

    # Define roles with permissions
    roles = {
        "admin": ["manage_users", "view_audit", "access_privacy", "basic_access"],
        "analyst": ["access_privacy", "view_audit"],
        "user": ["basic_access"]
    }

    # Create roles and assign permissions
    for role_name, perm_codes in roles.items():
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name, description=f"{role_name} role")
            db.session.add(role)
            db.session.commit()

        for code in perm_codes:
            perm = Permission.query.filter_by(code=code).first()
            if perm and perm not in role.permissions:
                role.permissions.append(perm)

    db.session.commit()
    print("Roles and permissions seeded successfully")
