from unittest.mock import Mock

from src.application.register_user_use_case import RegisterUserUseCase
from src.domain.entities import User, UserId


def test_register_new_user(
    mock_user_repo: Mock,
):
    # Given
    mock_user_repo.find_by_id.return_value = None

    use_case = RegisterUserUseCase(
        mock_user_repo,
    )

    # When
    result = use_case.execute(
        user_id=UserId(1),
        username="John",
    )

    # Then
    assert result.id == UserId(1)
    assert result.username == "John"

    mock_user_repo.find_by_id.assert_called_once_with(UserId(1))
    mock_user_repo.save.assert_called_once_with(result)


def test_register_existing_user_returns_same_user(
    mock_user_repo: Mock,
):
    # Given
    existing_user = User(
        id=UserId(1),
        username="John",
    )

    mock_user_repo.find_by_id.return_value = existing_user

    use_case = RegisterUserUseCase(
        mock_user_repo,
    )

    # When
    result = use_case.execute(
        user_id=UserId(1),
        username="John_doe",
    )

    # Then
    assert result is existing_user

    mock_user_repo.find_by_id.assert_called_once_with(UserId(1))
    mock_user_repo.save.assert_not_called()
