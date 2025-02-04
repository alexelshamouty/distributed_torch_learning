import os
import subprocess

from database.database import init_db

ALEMBIC_DIR = "migrations"

def alembic_initialized():
    """Check if Alembic has already been initialized."""
    return os.path.exists(ALEMBIC_DIR)

def run_alembic_migrations():
    """Run Alembic migrations automatically."""
    if not alembic_initialized():
        print("Initializing Alembic...")
        subprocess.run(["alembic", "init", ALEMBIC_DIR], check=True)

    print("Running Alembic migrations...")

    # Ensure Alembic is configured with target_metadata
    alembic_env_path = os.path.join(ALEMBIC_DIR, "env.py")
    if os.path.exists(alembic_env_path):
        with open(alembic_env_path, "r") as file:
            content = file.read()
            if "target_metadata" not in content:
                print("❌ ERROR: Alembic env.py is missing target_metadata! Please check the file.")
                return

    # Generate migration only if none exist
    versions_dir = os.path.join(ALEMBIC_DIR, "versions")
    if not os.path.exists(versions_dir) or not os.listdir(versions_dir):
        print("Generating initial Alembic migration...")
        subprocess.run(["alembic", "revision", "--autogenerate", "-m", "Initial migration"], check=True)

    # Apply migrations
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    print("✅ Alembic migrations applied successfully!")

if __name__ == "__main__":
    print("Initializing the database...")
    init_db()  # Ensure tables are created
    print("✅ Database initialized successfully!")

    run_alembic_migrations()  # Run Alembic setup and migrations
    print("🚀 Setup completed successfully!")