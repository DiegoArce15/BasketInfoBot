import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

# Configuración del logger de Alembic
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def get_db_url() -> str:
    """Obtiene y limpia la URL de conexión desde la variable de entorno o alembic.ini."""
    database_url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    if not database_url:
        raise ValueError("La variable de entorno DATABASE_URL no está definida.")

    # Normalizamos el prefijo para psycopg2/SQLAlchemy si viene como postgres://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    return database_url


def run_migrations_offline() -> None:
    """Modo offline: Genera las sentencias SQL en consola sin conectarse a la BD."""
    url = get_db_url()
    context.configure(url=url, literal_binds=True, dialect_name="postgresql")

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Modo online: Se conecta a PostgreSQL y ejecuta las migraciones DDL."""
    db_url = get_db_url()

    # Alembic utiliza create_engine internamente para gestionar la conexión y el dialecto
    connectable = create_engine(db_url)

    with connectable.connect() as connection:
        context.configure(connection=connection)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
