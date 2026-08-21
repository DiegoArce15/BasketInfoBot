from datetime import UTC, datetime

import psycopg2
import pytest

import src.infrastructure.out.persistence.postgres_match_persistence
from src.domain.entities import Channel, Match, MatchId, MatchStatus, Score
from tests.test_utils.constants import (
    TEAM_ID_2,
    TEAM_ID_3,
    TEAM_ID_12,
    TEAM_ID_16,
    USER_ID_11,
    USER_ID_404,
)


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
            INSERT INTO matches (id, home_team_id, away_team_id, start_time, home_score, away_score, league, status)
            VALUES 
                ('real-madrid-vs-ucam-murcia-2026-08-20', '00000000-0000-0000-0000-000000000012', '00000000-0000-0000-0000-000000000016', '2026-08-20 18:00:00+00', 80, 75, 'ACB', 'FINISHED'),
                ('barca-vs-casademont-zaragoza-2026-08-21', '00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000003', '2026-08-21 20:00:00+00', null, null, 'ACB', 'SCHEDULED'),
                ('real-madrid-vs-barca-2026-10-19', '00000000-0000-0000-0000-000000000012', '00000000-0000-0000-0000-000000000002', '2026-10-19 20:00:00+00', null, null, 'ACB', 'SCHEDULED');
            
            INSERT INTO match_channels (match_id, channel_name)
            VALUES 
                ('real-madrid-vs-ucam-murcia-2026-08-20', 'ESPN' ),
                ('barca-vs-casademont-zaragoza-2026-08-21', 'ESPN'),
                ('real-madrid-vs-barca-2026-10-19', 'Movistar+');
            """
        )

    yield

    # 2. TEARDOWN: Dejar la BD limpia para el siguiente test
    with psycopg2.connect(db_url) as conn, conn.cursor() as cursor:
        cursor.execute(
            """
                DELETE FROM match_channels;
                DELETE FROM matches;
            """
        )


@pytest.fixture
def seed_user_with_favorite_team(db_url, seed_teams):
    with psycopg2.connect(db_url) as conn, conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO users (id, telegram_id, username)
            VALUES ('00000000-0000-0000-0000-000000000011', 1, 'John-Doe');

            INSERT INTO user_favorite_teams (user_id, team_id)
            VALUES ('00000000-0000-0000-0000-000000000011', '00000000-0000-0000-0000-000000000012');
            """
        )

    yield

    with psycopg2.connect(db_url) as conn, conn.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM user_favorite_teams WHERE user_id = '00000000-0000-0000-0000-000000000011';
            DELETE FROM users WHERE id = '00000000-0000-0000-0000-000000000011';
            """
        )


def test_save(repository, seed_matches):
    # Given
    match = Match(
        id=MatchId("real-madrid-vs-barca-2026-08-25"),
        home_team_id=TEAM_ID_12,
        away_team_id=TEAM_ID_2,
        start_time=datetime(2026, 8, 25, 20, 30, tzinfo=UTC),
        score=Score(home=85, away=80),
        league="ACB",
        channels=[Channel("ESPN"), Channel("La1")],
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
        id=MatchId("barca-vs-casademont-zaragoza-2026-08-21"),
        home_team_id=TEAM_ID_2,
        away_team_id=TEAM_ID_3,
        start_time=datetime(2026, 8, 21, 20, 0, tzinfo=UTC),
        score=Score(home=90, away=85),
        league="ACB",
        channels=[Channel("Movistar+")],
        status=MatchStatus.FINISHED,
    )

    # When
    repository.save(match)

    # Then
    updated_match = repository.find_by_id(match.id)

    assert updated_match == match


def test_save_all(repository, seed_matches):
    # Given
    matches = [
        Match(
            id=MatchId("real-madrid-vs-barca-2026-08-25"),
            home_team_id=TEAM_ID_12,
            away_team_id=TEAM_ID_2,
            start_time=datetime(2026, 8, 25, 20, 30, tzinfo=UTC),
            score=Score(home=85, away=80),
            league="ACB",
            channels=[Channel("ESPN"), Channel("La1")],
            status=MatchStatus.FINISHED,
        ),
        Match(
            id=MatchId("barca-vs-real-madrid-2026-08-26"),
            home_team_id=TEAM_ID_2,
            away_team_id=TEAM_ID_12,
            start_time=datetime(2026, 8, 26, 21, 0, tzinfo=UTC),
            channels=[Channel("Movistar+")],
            league="ACB",
            status=MatchStatus.SCHEDULED,
        ),
    ]

    # When
    repository.save_all(matches)

    # Then
    assert repository.find_by_id(matches[0].id) == matches[0]
    assert repository.find_by_id(matches[1].id) == matches[1]


def test_save_all_updates_existing_matches(repository, seed_matches):
    # Given
    matches = [
        Match(
            id=MatchId("barca-vs-casademont-zaragoza-2026-08-21"),
            home_team_id=TEAM_ID_2,
            away_team_id=TEAM_ID_3,
            start_time=datetime(2026, 8, 21, 20, 0, tzinfo=UTC),
            score=Score(home=90, away=85),
            league="ACB",
            channels=[Channel("Movistar+")],
            status=MatchStatus.FINISHED,
        ),
        Match(
            id=MatchId("real-madrid-vs-barca-2026-08-27"),
            home_team_id=TEAM_ID_12,
            away_team_id=TEAM_ID_2,
            start_time=datetime(2026, 8, 27, 20, 30, tzinfo=UTC),
            channels=[Channel("ESPN"), Channel("La1")],
            league="ACB",
            status=MatchStatus.SCHEDULED,
        ),
    ]

    # When
    repository.save_all(matches)

    # Then
    assert repository.find_by_id(matches[0].id) == matches[0]
    assert repository.find_by_id(matches[1].id) == matches[1]


def test_find_by_id(repository, seed_matches):
    # When
    match = repository.find_by_id(MatchId("real-madrid-vs-ucam-murcia-2026-08-20"))

    # Then
    assert match == Match(
        id=MatchId("real-madrid-vs-ucam-murcia-2026-08-20"),
        home_team_id=TEAM_ID_12,
        away_team_id=TEAM_ID_16,
        start_time=datetime(2026, 8, 20, 18, 0, tzinfo=UTC),
        score=Score(home=80, away=75),
        channels=[Channel("ESPN")],
        league="ACB",
        status="FINISHED",
    )


def test_find_by_id_not_found(repository, seed_matches):
    # When
    match = repository.find_by_id(MatchId("404-non-found"))

    # Then
    assert match is None


def test_find_upcoming_by_user_returns_upcoming_matches(
    repository, seed_user_with_favorite_team, seed_matches, db_url
):
    # When
    matches = repository.find_upcoming_by_user(USER_ID_11)

    # Then
    assert matches == [
        Match(
            id=MatchId("real-madrid-vs-barca-2026-10-19"),
            home_team_id=TEAM_ID_12,
            away_team_id=TEAM_ID_2,
            start_time=datetime(2026, 10, 19, 20, 0, tzinfo=UTC),
            channels=[Channel("Movistar+")],
            league="ACB",
            status=MatchStatus.SCHEDULED,
        )
    ]


def test_find_upcoming_by_user_returns_empty_when_user_does_not_exist(
    repository, seed_matches
):
    # Given
    user_id = USER_ID_404

    # When
    matches = repository.find_upcoming_by_user(user_id)

    # Then
    assert matches == []
