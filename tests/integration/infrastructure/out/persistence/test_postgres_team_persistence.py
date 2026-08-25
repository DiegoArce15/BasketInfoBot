import uuid

import pytest

import src.infrastructure.out.persistence.postgres_team_persistence
from src.domain.team import Team, TeamId
from tests.test_utils.constants import (
    TEAM_ID_1,
    TEAM_ID_2,
    TEAM_ID_3,
    TEAM_ID_4,
    TEAM_ID_5,
    TEAM_ID_6,
    TEAM_ID_7,
    TEAM_ID_8,
    TEAM_ID_9,
    TEAM_ID_10,
    TEAM_ID_11,
    TEAM_ID_12,
    TEAM_ID_13,
    TEAM_ID_14,
    TEAM_ID_15,
    TEAM_ID_16,
    TEAM_ID_17,
    TEAM_ID_18,
    TEAM_ID_404,
)


@pytest.fixture
def repository(db_url):
    return src.infrastructure.out.persistence.postgres_team_persistence.PostgresTeamPersistence(
        db_url
    )


def test_save(repository):
    # Given
    team = Team(
        id=TeamId(uuid.uuid4()),
        name="My Team",
        short_name="MTT",
        country="Spain",
        logo_url="test.png",
    )

    # When
    repository.save(team)

    # Then
    saved_team = repository.find_by_id(team.id)

    assert saved_team == team


def test_save_updates_existing_team(repository):
    # Given
    team = Team(
        id=TEAM_ID_1,
        name="Real Madrid UPDATED",
        short_name="AND",
        country="Other-country",
        logo_url="madrid.png",
    )

    # When
    repository.save(team)

    # Then
    updated_team = repository.find_by_id(team.id)

    assert updated_team == team


def test_find_by_id_should_return_team(repository):
    # When
    result = repository.find_by_id(TEAM_ID_12)

    # Then
    assert result == Team(
        id=TEAM_ID_12,
        name="Real Madrid",
        short_name="RMB",
        country="Spain",
        logo_url=None,
    )


def test_find_by_id_should_return_none_when_team_does_not_exist(repository):
    # When
    result = repository.find_by_id(TEAM_ID_404)

    # Then
    assert result == None


def test_find_by_name_should_return_team(repository):
    # When
    result = repository.find_by_name("UCAM Murcia")

    # Then
    assert result == Team(
        id=TEAM_ID_16,
        name="UCAM Murcia",
        short_name="UCM",
        country="Spain",
        logo_url=None,
    )


def test_find_by_name_should_return_none_when_team_does_not_exist(repository):
    # When
    result = repository.find_by_name("404-Not-found")

    # Then
    assert result == None


def test_find_all(repository):
    # When
    result = repository.find_all()

    # Then
    # fmt: off
    assert result == [
        Team(id=TEAM_ID_1, name="Asisa Joventut", short_name="JOV", country="Spain", logo_url=None),
        Team(id=TEAM_ID_2, name="Barça", short_name="BAR", country="Spain", logo_url=None),
        Team(id=TEAM_ID_3, name="Casademont Zaragoza", short_name="CAZ", country="Spain", logo_url=None),
        Team(id=TEAM_ID_4, name="FIATC Girona", short_name="GIR", country="Spain", logo_url=None),
        Team(id=TEAM_ID_5, name="iLERNA Lleida", short_name="ILE", country="Spain", logo_url=None),
        Team(id=TEAM_ID_6, name="Kids&Us Manresa", short_name="K&U", country="Spain", logo_url=None),
        Team(id=TEAM_ID_7, name="Kosner Baskonia", short_name="BKN", country="Spain", logo_url=None ),
        Team(id=TEAM_ID_8, name="La Laguna Tenerife", short_name="LLT", country="Spain", logo_url=None),
        Team(id=TEAM_ID_9, name="Leyma Coruña", short_name="COR", country="Spain", logo_url=None),
        Team(id=TEAM_ID_10, name="Monbus Obradoiro", short_name="MOB", country="Spain", logo_url=None),
        Team(id=TEAM_ID_11, name="MoraBanc Andorra", short_name="MBA", country="Spain", logo_url=None),
        Team(id=TEAM_ID_12, name="Real Madrid", short_name="RMB", country="Spain", logo_url=None),
        Team(id=TEAM_ID_13, name="Recoletas Salud San Pablo Burgos", short_name="BUR", country="Spain", logo_url=None),
        Team(id=TEAM_ID_14, name="Río Breogán", short_name="BRE", country="Spain", logo_url=None),
        Team(id=TEAM_ID_15, name="Surne Bilbao", short_name="SBB", country="Spain", logo_url=None),
        Team(id=TEAM_ID_16, name="UCAM Murcia", short_name="UCM", country="Spain", logo_url=None),
        Team(id=TEAM_ID_17, name="Unicaja", short_name="UNI", country="Spain", logo_url=None),
        Team(id=TEAM_ID_18, name="Valencia Basket", short_name="VBC", country="Spain", logo_url=None),
    ]
