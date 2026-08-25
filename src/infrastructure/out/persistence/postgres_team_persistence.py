from uuid import UUID

import psycopg2
from psycopg2.extras import RealDictCursor

from src.domain.team import Team, TeamId
from src.domain.team_repository import TeamRepository


class PostgresTeamPersistence(TeamRepository):
    def __init__(self, db_url: str) -> None:
        self._db_url = db_url

    def _get_connection(self):
        return psycopg2.connect(self._db_url, cursor_factory=RealDictCursor)

    def save(self, team: Team) -> None:
        query = """
            INSERT INTO teams (id, name, short_name, country, logo_url)
            VALUES (%(id)s, %(name)s, %(short_name)s, %(country)s, %(logo_url)s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                short_name = EXCLUDED.short_name,
                country = EXCLUDED.country,
                logo_url = EXCLUDED.logo_url;
        """
        with self._get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(
                query,
                {
                    "id": str(team.id.value),
                    "name": team.name,
                    "short_name": team.short_name,
                    "country": team.country,
                    "logo_url": team.logo_url,
                },
            )

    def find_by_id(self, team_id: TeamId) -> Team | None:
        query = """
            SELECT id, name, short_name, country, logo_url
            FROM teams
            WHERE id = %(id)s;
        """
        with self._get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(query, {"id": str(team_id.value)})
            row = cursor.fetchone()

            if not row:
                return None

            return self._map_row_to_team(row)

    def find_by_ids(self, team_ids: list[TeamId]) -> list[Team]:
        if not team_ids:
            return []

        query = """
            SELECT id, name, short_name, country, logo_url
            FROM teams
            WHERE id = ANY(%(team_ids)s);
        """

        with self._get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(
                query,
                {"team_ids": [str(team_id.value) for team_id in team_ids]},
            )

            rows = cursor.fetchall()

        return [self._map_row_to_team(row) for row in rows]

    def find_by_name(self, name: str) -> Team | None:
        query = """
            SELECT id, name, short_name, country, logo_url
            FROM teams
            WHERE name = %(name)s;
        """
        with self._get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(query, {"name": name})
            row = cursor.fetchone()

            if not row:
                return None

            return self._map_row_to_team(row)

    def find_all(self) -> list[Team]:
        query = """
            SELECT id, name, short_name, country, logo_url
            FROM teams
            ORDER BY id ASC;
        """
        with self._get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

            return [self._map_row_to_team(row) for row in rows]

    def _map_row_to_team(self, row: dict) -> Team:
        return Team(
            id=TeamId(UUID(row["id"])),
            name=row["name"],
            short_name=row["short_name"],
            country=row["country"],
            logo_url=row["logo_url"],
        )
