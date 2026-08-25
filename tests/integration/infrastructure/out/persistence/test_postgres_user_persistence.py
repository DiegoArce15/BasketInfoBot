import psycopg2
import pytest

import src.infrastructure.out.persistence.postgres_user_persistence
from src.domain.user import User
from tests.test_utils.constants import (
    TEAM_ID_1,
    TEAM_ID_2,
    TELEGRAM_ID_1,
    TELEGRAM_ID_2,
    TELEGRAM_ID_404,
    USER_ID_1,
    USER_ID_2,
    USER_ID_404,
)


@pytest.fixture
def repository(db_url):
    return src.infrastructure.out.persistence.postgres_user_persistence.PostgresUserPersistence(
        db_url
    )


@pytest.fixture
def seed_user_with_favorite_team(db_url, seed_teams):
    with psycopg2.connect(db_url) as conn, conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO users (id, telegram_id, username)
            VALUES ('00000000-0000-0000-0000-000000000001', 1, 'John Doe');

            INSERT INTO user_favorite_teams (user_id, team_id)
            VALUES ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001');
            """
        )

    yield

    with psycopg2.connect(db_url) as conn, conn.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM user_favorite_teams WHERE user_id = '00000000-0000-0000-0000-000000000001';
            DELETE FROM users WHERE id = '00000000-0000-0000-0000-000000000001';
            """
        )


def test_save(repository):
    # Given
    user = User(
        id=USER_ID_2, telegram_id=TELEGRAM_ID_2, username="Jane Doe", favorite_teams=[]
    )

    # When
    repository.save(user)

    # Then
    saved_user = repository.find_by_id(user.id)

    assert saved_user == user


def test_update_user_info(repository, seed_user_with_favorite_team):
    # Given
    existing_user = repository.find_by_id(USER_ID_1)
    assert existing_user is not None

    updated_user_data = User(
        id=USER_ID_1,
        telegram_id=TELEGRAM_ID_1,
        username="John Updated",
        favorite_teams=[
            User.FavoriteTeam(team_id=TEAM_ID_1, notifications_enabled=True)
        ],
    )

    # When
    repository.save(updated_user_data)

    # Then
    saved_user = repository.find_by_id(USER_ID_1)
    assert saved_user == updated_user_data


def test_update_user_favorite_teams(repository, seed_user_with_favorite_team):
    # Given
    existing_user = repository.find_by_id(USER_ID_1)
    assert existing_user is not None

    user_with_new_favorites = User(
        id=USER_ID_1,
        telegram_id=TELEGRAM_ID_1,
        username="John Doe",
        favorite_teams=[
            User.FavoriteTeam(team_id=TEAM_ID_1, notifications_enabled=True),
            User.FavoriteTeam(team_id=TEAM_ID_2, notifications_enabled=False),
        ],
    )

    # When
    repository.save(user_with_new_favorites)

    # Then
    saved_user = repository.find_by_id(USER_ID_1)
    assert saved_user == user_with_new_favorites
    assert saved_user.favorite_teams == [
        User.FavoriteTeam(team_id=TEAM_ID_1, notifications_enabled=True),
        User.FavoriteTeam(team_id=TEAM_ID_2, notifications_enabled=False),
    ]


def test_find_by_id_should_return_user(repository, seed_user_with_favorite_team):
    # When
    result = repository.find_by_id(USER_ID_1)

    # Then
    assert result == User(
        id=USER_ID_1,
        telegram_id=TELEGRAM_ID_1,
        username="John Doe",
        favorite_teams=[
            User.FavoriteTeam(team_id=TEAM_ID_1, notifications_enabled=True)
        ],
    )


def test_find_by_id_should_return_none_when_user_does_not_exist(
    repository, seed_user_with_favorite_team
):
    # When
    result = repository.find_by_id(USER_ID_404)

    # Then
    assert result == None


def test_find_by_telegram_id_should_return_user(
    repository, seed_user_with_favorite_team
):
    # When
    result = repository.find_by_telegram_id(TELEGRAM_ID_1)

    # Then
    assert result == User(
        id=USER_ID_1,
        telegram_id=TELEGRAM_ID_1,
        username="John Doe",
        favorite_teams=[
            User.FavoriteTeam(team_id=TEAM_ID_1, notifications_enabled=True)
        ],
    )


def test_find_by_telegram_id_should_return_none_when_user_does_not_exist(
    repository, seed_user_with_favorite_team
):
    # When
    result = repository.find_by_telegram_id(TELEGRAM_ID_404)

    # Then
    assert result == None
