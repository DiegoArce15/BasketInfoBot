from uuid import UUID

import psycopg2
from psycopg2.extras import RealDictCursor

from src.domain.team import TeamId
from src.domain.user import TelegramId, User, UserId
from src.domain.user_repository import UserRepository


class PostgresUserPersistence(UserRepository):
    def __init__(self, db_url: str) -> None:
        self._db_url = db_url

    def _get_connection(self):
        return psycopg2.connect(self._db_url, cursor_factory=RealDictCursor)

    def save(self, user: User) -> None:
        with self._get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(
                query="""
                    INSERT INTO users (id, telegram_id, username)
                    VALUES (%(id)s, %(telegram_id)s, %(username)s)
                    ON CONFLICT (id) DO UPDATE SET
                        username = EXCLUDED.username;
                """,
                vars={
                    "id": str(user.id.value),
                    "telegram_id": user.telegram_id.value,
                    "username": user.username,
                },
            )

            cursor.execute(
                query="""
                    DELETE FROM user_favorite_teams
                    WHERE user_id = %(user_id)s;
                """,
                vars={"user_id": str(user.id.value)},
            )

            for favorite in user.favorite_teams:
                cursor.execute(
                    query="""
                        INSERT INTO user_favorite_teams (user_id, team_id, notifications_enabled)
                        VALUES (%(user_id)s, %(team_id)s, %(notifications_enabled)s);
                    """,
                    vars={
                        "user_id": str(user.id.value),
                        "team_id": str(favorite.team_id.value),
                        "notifications_enabled": favorite.notifications_enabled,
                    },
                )

    def find_by_id(self, user_id: UserId) -> User | None:
        user_query = """
            SELECT id, telegram_id, username
            FROM users
            WHERE id = %(id)s;
        """
        return self._fetch_user(user_query, {"id": str(user_id.value)})

    def find_by_telegram_id(self, telegram_id: TelegramId) -> User | None:
        return self._fetch_user(
            user_query="""
                SELECT id, telegram_id, username
                FROM users
                WHERE telegram_id = %(telegram_id)s;
            """,
            params={"telegram_id": str(telegram_id.value)},
        )

    def _fetch_user(self, user_query: str, params: dict) -> User | None:
        with self._get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(user_query, params)
            user_row = cursor.fetchone()

            if not user_row:
                return None

            cursor.execute(
                query="""
                    SELECT team_id, notifications_enabled
                    FROM user_favorite_teams
                    WHERE user_id = %(user_id)s;
                """,
                vars={"user_id": str(user_row["id"])},
            )
            fav_rows = cursor.fetchall()

            favorite_teams = [
                User.FavoriteTeam(
                    team_id=TeamId(value=UUID(str(row["team_id"]))),
                    notifications_enabled=row["notifications_enabled"],
                )
                for row in fav_rows
            ]

            return User(
                id=UserId(UUID(user_row["id"])),
                telegram_id=TelegramId(user_row["telegram_id"]),
                username=user_row["username"],
                favorite_teams=favorite_teams,
            )
