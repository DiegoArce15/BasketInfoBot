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


@pytest.fixture(scope="function", autouse=True)
def seed_teams(db_url, run_migrations):
    """
    Limpia y reinicia los equipos de prueba antes de CADA test.
    """
    with psycopg2.connect(db_url) as conn, conn.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE teams RESTART IDENTITY CASCADE;")
        
        cursor.execute(
            """
            INSERT INTO teams (id, name)
            VALUES 
                ('00000000-0000-0000-0000-000000000001', 'Real Madrid'),
                ('00000000-0000-0000-0000-000000000002', 'Barcelona'),
                ('00000000-0000-0000-0000-000000000003', 'Saski Baskonia'),
                ('00000000-0000-0000-0000-000000000004', 'Valencia Basket'),
                ('00000000-0000-0000-0000-000000000005', 'UCAM Murcia');
            """
        )
        conn.commit()