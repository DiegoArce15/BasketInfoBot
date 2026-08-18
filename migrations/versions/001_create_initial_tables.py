"""create_initial_tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-08-17
"""
from alembic import op

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tabla de Equipos
    op.execute("""
        CREATE TABLE teams (
            id UUID PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            country VARCHAR(50) DEFAULT 'Spain',
            logo_url TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Tabla de Usuarios
    op.execute("""
        CREATE TABLE users (
            id UUID PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            username VARCHAR(100),
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Tabla intermedia de Favoritos (Relación N:M)
    op.execute("""
        CREATE TABLE user_favorite_teams (
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            team_id UUID NOT NULL,
            notifications_enabled BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, team_id)
        );
    """)

    # Tabla de Partidos
    op.execute("""
        CREATE TABLE matches (
            id VARCHAR(100) PRIMARY KEY,
            home_team_id UUID NOT NULL REFERENCES teams(id),
            away_team_id UUID NOT NULL REFERENCES teams(id),
            home_score INTEGER,
            away_score INTEGER,
            start_time TIMESTAMPTZ NOT NULL,
            channel VARCHAR(100) DEFAULT NULL,
            league VARCHAR(100) DEFAULT NULL,
            status VARCHAR(30) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS matches;")
    op.execute("DROP TABLE IF EXISTS user_favorite_teams;")
    op.execute("DROP TABLE IF EXISTS users;")
    op.execute("DROP TABLE IF EXISTS teams;")