from src.application.remove_favorite_team_use_case import RemoveFavoriteTeamUseCase
from src.domain.entities import TeamId, User, UserId


def test_remove_favorite_team_success(user_repo):
    # Given
    user_id = UserId(1)
    team_id = TeamId("real-madrid")
    user = User(id=user_id, favorite_team_ids=[team_id])
    user_repo.save(user)

    use_case = RemoveFavoriteTeamUseCase(user_repo)

    # When
    use_case.execute(user_id=user_id, team_id=team_id)

    # Then
    updated_user = user_repo.find_by_id(user_id)
    assert team_id not in updated_user.favorite_team_ids