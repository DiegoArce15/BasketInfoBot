from datetime import UTC, datetime

import psycopg2
import pytest

import src.infrastructure.out.persistence.postgres_match_persistence
from src.domain.entities import Match, MatchId, MatchStatus, Score, TeamId, UserId


@pytest.fixture
def repository(db_url):
    return src.infrastructure.out.persistence.postgres_match_persistence.PostgresMatchPersistence(
        db_url
    )


@pytest.fixture
def seed_matches(db_url):
    """Inserta datos de prueba antes del test y limpia las tablas al terminar."""
    # 1. SETUP: Datos iniciales
    with psycopg2.connect(db_url) as conn, conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO matches (id, home_team_id, away_team_id, start_time, home_score, away_score, league, channel, status)
            VALUES 
                ('real-madrid-vs-ucam-murcia-2026-08-20', 'real-madrid', 'ucam-murcia', '2026-08-20 18:00:00+00', 80, 75, 'ACB', 'ESPN', 'FINISHED'),
                ('barcelona-vs-saski-baskonia-2026-08-21', 'barcelona', 'saski-baskonia', '2026-08-21 20:00:00+00', null, null, 'ACB', 'TNT Sports', 'SCHEDULED');
            """
        )

    yield

    # 2. TEARDOWN: Dejar la BD limpia para el siguiente test
    with psycopg2.connect(db_url) as conn, conn.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE matches;")


@pytest.fixture
def seed_user_with_favorite_team(db_url, seed_teams):
    with psycopg2.connect(db_url) as conn, conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO users (id, username)
            VALUES (1, 'John-Doe');

            INSERT INTO user_favorite_teams (user_id, team_id)
            VALUES (1, 'real-madrid');
            """
        )

    yield UserId(1)

    with psycopg2.connect(db_url) as conn, conn.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM user_favorite_teams WHERE user_id = '1';
            DELETE FROM users WHERE id = '1';
            """
        )


def test_save(repository, seed_matches):
    # Given
    match = Match(
        id=MatchId("real-madrid-vs-barcelona-2026-08-25"),
        home_team_id=TeamId("real-madrid"),
        away_team_id=TeamId("barcelona"),
        start_time=datetime(
            2026,
            8,
            25,
            20,
            30,
            tzinfo=UTC,
        ),
        score=Score(home=85, away=80),
        league="ACB",
        channel="ESPN",
        status=MatchStatus.FINISHED,
    )

    # When
    repository.save(match)

    # Then
    saved_match = repository.find_by_id(match.id)

    assert saved_match == match


def test_save_updates_existing_match(repository, seed_matches):
    # Given
    match = Match(
        id=MatchId("barcelona-vs-saski-baskonia-2026-08-21"),
        home_team_id=TeamId("barcelona"),
        away_team_id=TeamId("saski-baskonia"),
        start_time=datetime(
            2026,
            8,
            21,
            20,
            0,
            tzinfo=UTC,
        ),
        score=Score(home=90, away=85),
        league="ACB",
        channel="Movistar",
        status=MatchStatus.FINISHED,
    )

    # When
    repository.save(match)

    # Then
    updated_match = repository.find_by_id(match.id)

    assert updated_match == match


def test_find_by_id(repository, seed_matches):
    match = repository.find_by_id(MatchId("real-madrid-vs-ucam-murcia-2026-08-20"))

    assert match is not None
    assert match.id == MatchId("real-madrid-vs-ucam-murcia-2026-08-20")
    assert match.home_team_id == TeamId("real-madrid")
    assert match.away_team_id == TeamId("ucam-murcia")
    assert match.start_time.isoformat() == "2026-08-20T18:00:00+00:00"
    assert match.score == Score(home=80, away=75)
    assert match.channel == "ESPN"
    assert match.league == "ACB"
    assert match.status == "FINISHED"


def test_find_by_id_not_found(repository, seed_matches):
    match = repository.find_by_id(MatchId("404-non-found"))

    assert match is None


def test_find_upcoming_by_user_returns_upcoming_matches( repository, seed_user_with_favorite_team, db_url, ):
    # Given

    # When
    matches = repository.find_upcoming_by_user(UserId(1))

    # Then
    assert len(matches) == 1

    match = matches[0]

    assert match.id == MatchId("real-madrid-vs-barcelona-2026-08-25")
    assert match.home_team_id == TeamId("real-madrid")
    assert match.away_team_id == TeamId("barcelona")
    assert match.status == MatchStatus.SCHEDULED

def test_find_upcoming_by_user_returns_empty_when_user_does_not_exist( repository, seed_matches, ):
    # Given
    user_id = UserId(404)

    # When
    matches = repository.find_upcoming_by_user(user_id)

    # Then
    assert matches == []