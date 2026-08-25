import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def get_db_url() -> str:
    database_url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")

    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not defined.")

    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    return database_url


def run_migrations_offline() -> None:
    url = get_db_url()

    context.configure(url=url, literal_binds=True, dialect_name="postgresql")

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    db_url = get_db_url()
    connectable = create_engine(db_url)

    with connectable.connect() as connection:
        context.configure(connection=connection)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
