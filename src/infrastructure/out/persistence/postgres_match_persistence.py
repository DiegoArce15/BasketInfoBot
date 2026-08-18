from uuid import UUID

import psycopg2
from psycopg2.extras import RealDictCursor

from src.domain.entities import (
    Channel,
    Match,
    MatchId,
    MatchStatus,
    Score,
    TeamId,
    UserId,
)
from src.domain.match_repository import MatchRepository


class PostgresMatchPersistence(MatchRepository):

    def __init__(self, db_url: str) -> None:
        self._db_url = db_url

    def _get_connection(self):
        return psycopg2.connect(self._db_url, cursor_factory=RealDictCursor)

    def save(self, match: Match) -> None:
        # Extraer valores de Score si existe
        home_score = match.score.home if match.score else None
        away_score = match.score.away if match.score else None

        with self._get_connection() as conn, conn.cursor() as cursor:
            # 1. Guardar/actualizar datos del partido
            cursor.execute(
                query="""
                    INSERT INTO matches (
                        id, home_team_id, away_team_id, start_time, 
                        league, status, home_score, away_score
                    )
                    VALUES (
                        %(id)s, %(home_team_id)s, %(away_team_id)s, %(start_time)s,
                        %(league)s, %(status)s, %(home_score)s, %(away_score)s
                    )
                    ON CONFLICT (id) DO UPDATE SET
                        home_team_id = EXCLUDED.home_team_id,
                        away_team_id = EXCLUDED.away_team_id,
                        start_time = EXCLUDED.start_time,
                        league = EXCLUDED.league,
                        status = EXCLUDED.status,
                        home_score = EXCLUDED.home_score,
                        away_score = EXCLUDED.away_score;
                """,
                vars={
                    "id": str(match.id.value),
                    "home_team_id": str(match.home_team_id.value),
                    "away_team_id": str(match.away_team_id.value),
                    "start_time": match.start_time,
                    "league": match.league,
                    "status": match.status.value,
                    "home_score": home_score,
                    "away_score": away_score,
                },
            )

            # 2. Sincronizar canales asociados
            cursor.execute(
                query="""
                    DELETE FROM match_channels WHERE match_id = %(match_id)s;
                """,
                vars={"match_id": str(match.id.value)})

            for channel in match.channels:
                cursor.execute(
                    query="""
                        INSERT INTO match_channels (match_id, channel_name)
                        VALUES (%(match_id)s, %(channel_name)s);
                    """,
                    vars={
                        "match_id": str(match.id.value),
                        "channel_name": channel.name,
                    },
                )

    def find_by_id(self, match_id: MatchId) -> Match | None:
        query = """
            SELECT id, home_team_id, away_team_id, start_time, 
                league, status, home_score, away_score
            FROM matches
            WHERE id = %(id)s;
        """

        with self._get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(query, {"id": str(match_id.value)})
            match_row = cursor.fetchone()

            if not match_row:
                return None

            return self._fetch_match_with_channels(cursor, match_row)

    
    def find_upcoming_by_user(self, user_id: UserId, limit: int = 10) -> list[Match]:
        query = """
            SELECT m.id, m.home_team_id, m.away_team_id, m.start_time, m.home_score, m.away_score, m.league, m.status
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
            match_rows = cursor.fetchall()

            # Unificamos el mapeo usando el helper
            return [self._fetch_match_with_channels(cursor, row) for row in match_rows]

    def _fetch_match_with_channels(self, cursor, match_row: dict) -> Match:
        # 1. Obtener canales para el partido actual
        channels_query = """
            SELECT channel_name 
            FROM match_channels 
            WHERE match_id = %(match_id)s;
        """
        cursor.execute(channels_query, {"match_id": str(match_row["id"])})
        channel_rows = cursor.fetchall()

        channels = [Channel(name=row["channel_name"]) for row in channel_rows]

        # 2. Reconstruir Score
        score = None
        if match_row["home_score"] is not None and match_row["away_score"] is not None:
            score = Score(home=match_row["home_score"], away=match_row["away_score"])

        # 3. Construir entidad de dominio
        return Match(
            id=MatchId(str(match_row["id"])),
            home_team_id=TeamId(value=UUID(str(match_row["home_team_id"]))),
            away_team_id=TeamId(value=UUID(str(match_row["away_team_id"]))),
            start_time=match_row["start_time"],
            league=match_row["league"],
            status=MatchStatus(match_row["status"]),
            score=score,
            channels=channels,
        )
