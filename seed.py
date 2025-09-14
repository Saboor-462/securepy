from getpass import getpass
from app import app, db
from src.models import Role, Permission, User
from src.utils.security import hash_password

def ensure_roles():
    admin = Role.query.filter_by(name="admin").first()
    user = Role.query.filter_by(name="user").first()
    if not admin:
        admin = Role(name="admin", description="Administrator")
        db.session.add(admin)
    if not user:
        user = Role(name="user", description="Basic user")
        db.session.add(user)
    db.session.commit()
    return admin, user

def ensure_permissions():
    perm_codes = [
        ("view_audit", "Can view audit logs"),
        ("manage_users", "Can manage users"),
    ]
    perms = []
    for code, desc in perm_codes:
        p = Permission.query.filter_by(code=code).first()
        if not p:
            p = Permission(code=code, description=desc)
            db.session.add(p)
        perms.append(p)
    db.session.commit()
    return perms

def link_admin_perms(admin, perms):
    for p in perms:
        if p not in admin.permissions:
            admin.permissions.append(p)
    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        admin_role, user_role = ensure_roles()
        perms = ensure_permissions()
        link_admin_perms(admin_role, perms)

        email = input("Admin email [admin@example.com]: ") or "admin@example.com"
        password = getpass("Admin password [Admin@123]: ") or "Admin@123"

        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, password_hash=hash_password(password), role=admin_role)
            db.session.add(user)
            db.session.commit()
            print(f"Created admin user: {email}")
        else:
            # Update password if user exists
            user.password_hash = hash_password(password)
            user.role = admin_role  # make sure the role is still admin
            db.session.commit()
            print(f"Updated admin user password: {email}")
