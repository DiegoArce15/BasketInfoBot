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
                INSERT INTO teams ( id, name, short_name, country)
                VALUES 
                    ('00000000-0000-0000-0000-000000000001','Asisa Joventut', 'JOV', 'Spain'),
                    ('00000000-0000-0000-0000-000000000002','Barça', 'BAR', 'Spain'),
                    ('00000000-0000-0000-0000-000000000003','Casademont Zaragoza', 'CAZ', 'Spain'),
                    ('00000000-0000-0000-0000-000000000004','FIATC Girona', 'GIR', 'Spain'),
                    ('00000000-0000-0000-0000-000000000005','iLERNA Lleida', 'ILE', 'Spain'),
                    ('00000000-0000-0000-0000-000000000006','Kids&Us Manresa', 'K&U', 'Spain'),
                    ('00000000-0000-0000-0000-000000000007','Kosner Baskonia', 'BKN', 'Spain'),
                    ('00000000-0000-0000-0000-000000000008','La Laguna Tenerife', 'LLT', 'Spain'),
                    ('00000000-0000-0000-0000-000000000009','Leyma Coruña', 'COR', 'Spain'),
                    ('00000000-0000-0000-0000-000000000010','Monbus Obradoiro', 'MOB', 'Spain'),
                    ('00000000-0000-0000-0000-000000000011','MoraBanc Andorra', 'MBA', 'Spain'),
                    ('00000000-0000-0000-0000-000000000012','Real Madrid', 'RMB', 'Spain'),
                    ('00000000-0000-0000-0000-000000000013','Recoletas Salud San Pablo Burgos', 'BUR', 'Spain'),
                    ('00000000-0000-0000-0000-000000000014','Río Breogán', 'BRE', 'Spain'),
                    ('00000000-0000-0000-0000-000000000015','Surne Bilbao', 'SBB', 'Spain'),
                    ('00000000-0000-0000-0000-000000000016','UCAM Murcia', 'UCM', 'Spain'),
                    ('00000000-0000-0000-0000-000000000017','Unicaja', 'UNI', 'Spain'),
                    ('00000000-0000-0000-0000-000000000018','Valencia Basket', 'VBC', 'Spain');
            """
        )
        conn.commit()
