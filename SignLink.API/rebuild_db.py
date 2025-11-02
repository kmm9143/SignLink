# DESCRIPTION:
#   This script rebuilds the database schema for the SignLink application
#   using the SQLAlchemy Base metadata defined in your models.
#   It imports the shared engine from `database.py` to ensure environment
#   consistency with the rest of the app.
#
#   ⚠️ WARNING: This script DROPS all existing tables in the connected
#   database before recreating them. Use only when you intend to reset
#   your Supabase or local schema.
#
# LANGUAGE: PYTHON
# SOURCE(S):
#   [1] SQLAlchemy Docs – ORM Metadata Management
#   [2] Supabase Docs – Connecting External Clients to PostgreSQL
# -------------------------------------------------------------------

from database import engine
from models.base import Base
from models.user_information import UserInformation
from models.user_settings import UserSettings
from models.user_translation_history import UserTranslationHistory
import os

# -------------------------------------------------------------------
# Step 1: Confirm database environment
# -------------------------------------------------------------------
env = os.getenv("ENVIRONMENT", "development").lower()

print(f"⚙️ Environment detected: {env}")
print(f"Connected to: {engine.url}")

# -------------------------------------------------------------------
# Step 2: Safety check – prevent accidental production wipe
# -------------------------------------------------------------------
if "supabase" in str(engine.url) and env != "development":
    confirm = input(
        "\n⚠️ WARNING: You are connected to a Supabase (production-like) database.\n"
        "This will DROP and RECREATE all tables.\n"
        "Type 'YES' to continue: "
    )
    if confirm != "YES":
        print("❌ Aborted to prevent data loss.")
        exit(1)

# -------------------------------------------------------------------
# Step 3: Drop and recreate all tables
# -------------------------------------------------------------------
print("🧱 Dropping existing tables (if any)...")
Base.metadata.drop_all(bind=engine)

print("🚀 Rebuilding database schema...")
Base.metadata.create_all(bind=engine)

print("✅ Schema rebuilt successfully!")

# -------------------------------------------------------------------
# Step 4: (Optional) Seed test user
# -------------------------------------------------------------------
seed = input("\nWould you like to seed a test user? (y/N): ").strip().lower()
if seed == "y":
    from sqlalchemy.orm import Session
    session = Session(bind=engine)

    test_user = UserInformation(
        USERNAME="testuser",
        FIRST_NAME="Test",
        LAST_NAME="User",
        EMAIL="testuser@example.com",
        PASSWORD="fakehashed",
    )
    session.add(test_user)
    session.commit()

    test_settings = UserSettings(
        USER_ID=test_user.USER_ID,
        SPEECH_ENABLED=False,
        WEBCAM_ENABLED=True
    )
    session.add(test_settings)
    session.commit()
    session.close()

    print("👤 Test user created successfully!")
else:
    print("ℹ️ Skipped user seeding.")

print("\n🏁 Done! Database is ready for use.")