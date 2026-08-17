import os

import psycopg2
import pytest
from alembic import command
from alembic.config import Config
from testcontainers.community.postgres import PostgresContainer

os.environ["TESTCONTAINERS_RYUK_DISABLED"] = "true"


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def db_url(postgres_container):
    """Fixture que entrega la URL de la base de datos limpia a los tests."""
    raw_url = postgres_container.get_connection_url()
    clean_url = raw_url.replace("postgresql+psycopg2://", "postgresql://")
    os.environ["DATABASE_URL"] = clean_url
    return clean_url


@pytest.fixture(scope="session", autouse=True)
def run_migrations(db_url, pytestconfig):
    project_root = pytestconfig.rootpath
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "migrations"))
    config.set_main_option("sqlalchemy.url", db_url)

    command.upgrade(config, "head")


@pytest.fixture(scope="session", autouse=True)
def seed_teams(db_url, run_migrations):
    """
    Inserta los equipos fijos de prueba UNA SOLA VEZ por sesión,
    inmediatamente después de ejecutar las migraciones.
    """
    teams_data = [
        ("real-madrid", "Real Madrid"),
        ("barcelona", "Barcelona"),
        ("saski-baskonia", "Saski Baskonia"),
        ("valencia-basket", "Valencia Basket"),
        ("ucam-murcia", "UCAM Murcia"),
    ]

    with psycopg2.connect(db_url) as conn, conn.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO teams (id, name)
            VALUES (%s, %s)
            ON CONFLICT (id) DO NOTHING;
            """,
            teams_data,
        )

    yield teams_data
