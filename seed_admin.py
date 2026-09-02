"""
Bootstraps the very first Admin (Center head) account.

This is intentionally a STANDALONE SCRIPT, not an API endpoint. Exposing
"create an Admin" over HTTP — even gated by "only works if zero users
exist" — is a live attack surface sitting in a deployed system forever.
An Admin account has full access to every beneficiary's health data, so
its creation should happen once, by someone with direct database/server
access, not through a URL anyone could hit.

Usage:
    python seed_admin.py

Run this once, right after the tables are created (i.e. after the app
has started at least once, or after main.py's create_tables() has run).
Safe to run again later — it will refuse to create a duplicate email.
"""

import sys
import getpass

from database import SessionLocal, Base, engine
import screening.models  # noqa: F401 - registers all models before create_all
from screening.models.user import User
from screening.models.center import CenterProfile
from core.security import PasswordService


def main():
    print("=== Health Screening Platform: First Admin Setup ===\n")

    Base.metadata.create_all(bind=engine)  # safe no-op if tables already exist

    db = SessionLocal()
    try:
        name = input("Admin full name: ").strip()
        email = input("Admin email: ").strip()

        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"\nAn account with email '{email}' already exists (role: {existing.role}). Aborting.")
            sys.exit(1)

        password = getpass.getpass("Admin password (min 8 characters, input hidden): ")
        confirm = getpass.getpass("Confirm password: ")

        if password != confirm:
            print("\nPasswords do not match. Aborting.")
            sys.exit(1)

        if len(password) < 8:
            print("\nPassword must be at least 8 characters. Aborting.")
            sys.exit(1)

        admin = User(
            name=name,
            email=email,
            password_hash=PasswordService.hash_password(password),
            role="Admin",
            status="Active",          # no activation-code step needed — created directly, already trusted
            is_email_verified=True,
            facility_id=None,          # Admins aren't tied to a facility
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(f"\n✅ Admin account created: {admin.name} <{admin.email}> (user_id={admin.user_id})")

        # --- Optionally seed the Center profile in the same step ---
        existing_center = db.query(CenterProfile).first()
        if not existing_center:
            print("\nNo center profile found yet — let's set one up now (used as the header on reports).")
            center_name = input("Center name: ").strip()
            region = input("Region: ").strip()
            contact_info = input("Contact info (optional): ").strip() or None

            center = CenterProfile(
                name=center_name,
                region=region,
                contact_info=contact_info,
                head_admin_id=admin.user_id,
            )
            db.add(center)
            db.commit()
            print(f"✅ Center profile created: {center_name} ({region})")

        print("\nSetup complete. You can now log in via POST /api/v1/auth/login-request "
              "with this admin's email and password.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
