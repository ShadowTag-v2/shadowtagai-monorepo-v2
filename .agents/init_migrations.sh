#!/bin/bash
# ==============================================================================
# Antigravity Alembic Setup Script
# Initializes agent-friendly, auto-generating database migrations.
# ==============================================================================

APP_DIR="apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services"

echo "🚀 Initializing Agent-Proof Alembic Migrations..."

cd "$APP_DIR" || exit 1

# 1. Install Alembic and standard PostgreSQL drivers via uv
echo "📦 Installing alembic and postgres drivers..."
uv add alembic sqlalchemy psycopg2-binary

# 2. Scaffold the base Alembic directory
echo "🏗️ Scaffolding Alembic..."
uv run alembic init alembic

# 3. Overwrite env.py with an agent-friendly, dynamic version
echo "⚙️ Injecting dynamic env.py..."
cat << 'EOF' > alembic/env.py
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# IMPORT YOUR DATABASE MODELS HERE
# Note for Agent: Ensure this path correctly points to the declarative base!
try:
    from database import Base
    import models
    target_metadata = Base.metadata
except ImportError:
    print("⚠️ WARNING: Could not import Base metadata. Autogeneration will be blank.")
    target_metadata = None

config = context.config

# ---------------------------------------------------------
# MAGIC TRICK: Force Alembic to use the Docker Environment Variable
# ---------------------------------------------------------
database_url = os.getenv("DATABASE_URL", "postgresql://shadowtag-omega-v4_user:secure_password_here@localhost:5432/shadowtag-omega-v4_db")
config.set_main_option("sqlalchemy.url", database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
EOF

echo "✅ Alembic successfully configured for autonomous agents!"
