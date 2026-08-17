from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from src.application.process_scraped_matches_use_case import (
    ProcessScrapedMatchesUseCase,
    ScrapedMatchDTO,
)
from src.domain.entities import MatchStatus, TeamId


@pytest.fixture
def mock_match_repository() -> Mock:
    return Mock()


@pytest.fixture
def use_case(mock_match_repository: Mock) -> ProcessScrapedMatchesUseCase:
    return ProcessScrapedMatchesUseCase(match_repository=mock_match_repository)


def test_process_scraped_match_creates_and_saves_match(
    use_case: ProcessScrapedMatchesUseCase,
    mock_match_repository: Mock,
) -> None:
    # Given
    match_date = datetime(2026, 10, 25, 20, 0, tzinfo=UTC)
    scraped_dto = ScrapedMatchDTO(
        home_team_id=TeamId(value="real-madrid"),
        away_team_id=TeamId(value="barcelona"),
        status="FINISHED",
        start_time=match_date,
        home_score=88,
        away_score=85,
        channel="ESPN",
        league="ACB",
    )

    # When
    processed_match = use_case.execute(scraped_dto)

    # Then
    assert processed_match.id.value == "real-madrid-vs-barcelona-2026-10-25"
    assert processed_match.home_team_id == TeamId(value="real-madrid")
    assert processed_match.away_team_id == TeamId(value="barcelona")
    assert processed_match.start_time == match_date
    assert processed_match.status == MatchStatus.FINISHED

    assert processed_match.score is not None
    assert processed_match.score.home == 88
    assert processed_match.score.away == 85
    assert processed_match.channel == "ESPN"
    assert processed_match.league == "ACB"

    mock_match_repository.save.assert_called_once_with(processed_match)


def test_process_scraped_match_without_score(
    use_case: ProcessScrapedMatchesUseCase,
    mock_match_repository: Mock,
) -> None:
    # Given
    match_date = datetime(2026, 11, 15, 18, 0, tzinfo=UTC)
    scraped_dto = ScrapedMatchDTO(
        home_team_id=TeamId(value="baskonia"),
        away_team_id=TeamId(value="valencia-basket"),
        start_time=match_date,
        status="SCHEDULED",
        home_score=None,
        away_score=None,
        channel=None,
        league=None,
    )

    # When
    processed_match = use_case.execute(scraped_dto)

    # Then
    assert processed_match.id.value == "baskonia-vs-valencia-basket-2026-11-15"
    assert processed_match.home_team_id == TeamId(value="baskonia")
    assert processed_match.away_team_id == TeamId(value="valencia-basket")
    assert processed_match.start_time == match_date
    assert processed_match.status == MatchStatus.SCHEDULED
    assert processed_match.score is None
    assert processed_match.channel is None
    assert processed_match.league is None

    mock_match_repository.save.assert_called_once_with(processed_match)


def test_process_scraped_match_updates_existing_match_with_score_and_no_channel(
    use_case: ProcessScrapedMatchesUseCase,
    mock_match_repository: Mock,
) -> None:
    # Given
    match_date = datetime(2026, 10, 25, 20, 0, tzinfo=UTC)
    scraped_updated_dto = ScrapedMatchDTO(
        home_team_id=TeamId(value="real-madrid"),
        away_team_id=TeamId(value="barcelona"),
        start_time=match_date,
        status="FINISHED",
        home_score=92,
        away_score=88,
        channel=None,
        league="ACB",
    )

    # When
    updated_match = use_case.execute(scraped_updated_dto)

    # Then
    assert updated_match.id.value == "real-madrid-vs-barcelona-2026-10-25"
    assert updated_match.home_team_id == TeamId(value="real-madrid")
    assert updated_match.away_team_id == TeamId(value="barcelona")
    assert updated_match.start_time == match_date
    assert updated_match.status == MatchStatus.FINISHED
    assert updated_match.score is not None
    assert updated_match.score.home == 92
    assert updated_match.score.away == 88
    assert updated_match.channel is None
    assert updated_match.league == "ACB"

    mock_match_repository.save.assert_called_once_with(updated_match)