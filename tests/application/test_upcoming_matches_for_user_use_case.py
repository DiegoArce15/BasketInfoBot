from datetime import datetime

from src.application.get_upcoming_matches_for_user_use_case import (
    GetUpcomingMatchesForUserUseCase,
)
from src.domain.entities import Match, MatchId, MatchStatus, Team, TeamId, User, UserId


def test_get_upcoming_matches_for_user_ordered_by_date(user_repo, match_repo):
    # Given
    user_id = UserId(1)
    real_madrid = Team(id=TeamId("real-madrid"), name="Real Madrid")
    ucam_murcia = Team(id=TeamId("ucam-murcia"), name="Ucam Murcia")
    valencia_basket = Team(id=TeamId("valencia-basket"), name="Valencia Basket")

    user_repo.save(User(id=user_id, favorite_team_ids=[TeamId("real-madrid")]))

    match_later = Match(
        id=MatchId("Madrid-vs-Valencia"),
        home_team=real_madrid,
        away_team=valencia_basket,
        start_time=datetime(2026, 10, 25, 20, 0),
        channel="Movistar",
        league="ACB",
        status=MatchStatus.SCHEDULED,
    )
    match_earlier = Match(
        id=MatchId("Madrid-vs-Murcia"),
        home_team=real_madrid,
        away_team=ucam_murcia,
        start_time=datetime(2026, 10, 20, 18, 0),
        channel="DAZN",
        league="ACB",
        status=MatchStatus.SCHEDULED,
    )

    match_repo.save(match_later)
    match_repo.save(match_earlier)

    use_case = GetUpcomingMatchesForUserUseCase(user_repo, match_repo)

    # When
    matches = use_case.execute(user_id=user_id)

    # Then
    assert len(matches) == 2
    assert matches[0].id == MatchId("Madrid-vs-Murcia")  # El partido anterior va primero
    assert matches[1].id == MatchId("Madrid-vs-Valencia")


def test_get_upcoming_matches_returns_empty_when_no_favorites(user_repo, match_repo):
    # Given
    user_id = UserId(1)
    user_repo.save(User(id=user_id, favorite_team_ids=[]))

    use_case = GetUpcomingMatchesForUserUseCase(user_repo, match_repo)

    # When
    matches = use_case.execute(user_id=user_id)

    # Then
    assert matches == []