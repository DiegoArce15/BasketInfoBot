from uuid import UUID

import psycopg2
from psycopg2.extras import RealDictCursor

from src.domain.entities import Match, MatchId, Score, TeamId, UserId
from src.domain.match_repository import MatchRepository


class PostgresMatchPersistence(MatchRepository):
    """Implementación de la persistencia de partidos utilizando PostgreSQL y psycopg2."""

    def __init__(self, db_url: str) -> None:
        self._db_url = db_url

    def _get_connection(self):
        return psycopg2.connect(self._db_url, cursor_factory=RealDictCursor)

    def save(self, match: Match) -> None:
        """Inserta o actualiza un partido usando UPSERT de PostgreSQL."""
        query = """
            INSERT INTO matches (id, home_team_id, away_team_id, start_time, home_score, away_score, channel, league, status)
            VALUES (%(id)s, %(home_team_id)s, %(away_team_id)s, %(start_time)s, %(home_score)s, %(away_score)s, %(channel)s, %(league)s, %(status)s)
            ON CONFLICT (id) DO UPDATE SET
                home_team_id = EXCLUDED.home_team_id,
                away_team_id = EXCLUDED.away_team_id,
                start_time = EXCLUDED.start_time,
                home_score = EXCLUDED.home_score,
                away_score = EXCLUDED.away_score,
                channel = EXCLUDED.channel,
                league = EXCLUDED.league,
                status = EXCLUDED.status;
        """
        with self._get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(
                query,
                {
                    "id": match.id.value,
                    "home_team_id": match.home_team_id.value,
                    "away_team_id": match.away_team_id.value,
                    "start_time": match.start_time,
                    "home_score": match.score.home if match.score else None,
                    "away_score": match.score.away if match.score else None,
                    "channel": match.channel,
                    "league": match.league,
                    "status": match.status.value
                    if hasattr(match.status, "value")
                    else str(match.status),
                },
            )

    def find_by_id(self, match_id: MatchId) -> Match | None:
        """Obtiene un partido por su ID."""
        query = """
            SELECT id, home_team_id, away_team_id, start_time, home_score, away_score, channel, league, status
            FROM matches
            WHERE id = %(id)s;
        """
        with self._get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(query, {"id": str(match_id)})
            row = cursor.fetchone()

            if not row:
                return None

            return self._map_row_to_match(row)
    
    def find_upcoming_by_user(self, user_id: UserId, limit: int = 10) -> list[Match]:
        """Busca los próximos partidos de interés para un usuario especifico."""
        query = """
            SELECT m.id, m.home_team_id, m.away_team_id, m.start_time, m.home_score, m.away_score, m.channel, m.league, m.status
            FROM matches m
            WHERE m.status = 'SCHEDULED'
            AND EXISTS (
                SELECT 1 
                FROM user_favorite_teams uft 
                WHERE uft.user_id = %(user_id)s
                    AND (uft.team_id = m.home_team_id OR uft.team_id = m.away_team_id)
            )
            ORDER BY m.start_time ASC
            LIMIT %(limit)s;
        """
        with self._get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(query, {"user_id": str(user_id.value), "limit": limit})
            rows = cursor.fetchall()

            return [self._map_row_to_match(row) for row in rows]

    def _map_row_to_match(self, row: dict) -> Match:
        """Mapea una fila de PostgreSQL a la Entidad de Dominio Match."""
        score = None
        if row["home_score"] is not None and row["away_score"] is not None:
            score = Score(home=row["home_score"], away=row["away_score"])
            
        return Match(
            id=MatchId(row["id"]),
            home_team_id=TeamId(UUID(row["home_team_id"])),
            away_team_id=TeamId(UUID(row["away_team_id"])),
            start_time=row["start_time"],
            score=score,
            channel=row["channel"],
            league=row["league"],
            status=row["status"],
        )
