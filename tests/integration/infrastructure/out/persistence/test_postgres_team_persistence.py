import pytest

import src.infrastructure.out.persistence.postgres_team_persistence
from src.domain.entities import Team
from tests.test_utils.constants import (
    TEAM_ID_1,
    TEAM_ID_2,
    TEAM_ID_3,
    TEAM_ID_4,
    TEAM_ID_5,
    TEAM_ID_6,
    TEAM_ID_404,
)


@pytest.fixture
def repository(db_url):
    return src.infrastructure.out.persistence.postgres_team_persistence.PostgresTeamPersistence(
        db_url
    )

def test_save(repository):
    # Given
    team = Team( id=TEAM_ID_6, name="UNICAJA", country="Spain", logo_url="fake-s3-unicaja.png", )

    # When
    repository.save(team)

    # Then
    saved_team = repository.find_by_id(team.id)

    assert saved_team == team

def test_save_updates_existing_team(repository):
    # Given
    team = Team( id=TEAM_ID_1, name="Real Madrid UPDATED", country="Other-country", logo_url="fake-s3-madid.png", )

    # When
    repository.save(team)

    # Then
    updated_team = repository.find_by_id(team.id)

    assert updated_team == team

def test_find_by_id_should_return_team(repository):
    # When
    result = repository.find_by_id(TEAM_ID_1)

    # Then
    assert result == Team( id=TEAM_ID_1, name="Real Madrid", country=None, logo_url=None, )

def test_find_by_id_should_return_none_when_team_does_not_exist(repository):
    # When
    result = repository.find_by_id(TEAM_ID_404)

    # Then
    assert result == None

def test_find_all(repository):
    # When
    result = repository.find_all()

    # Then
    assert result == [
        Team( id=TEAM_ID_1, name="Real Madrid", country=None, logo_url=None, ),
        Team( id=TEAM_ID_2, name="Barcelona", country=None, logo_url=None, ),
        Team( id=TEAM_ID_3, name="Saski Baskonia", country=None, logo_url=None, ),
        Team( id=TEAM_ID_4, name="Valencia Basket", country=None, logo_url=None, ),
        Team( id=TEAM_ID_5, name="UCAM Murcia", country=None, logo_url=None, ),
    ]