from unittest.mock import Mock

from src.application.register_user_use_case import RegisterUserUseCase
from src.domain.entities import User
from tests.test_utils.constants import TELEGRAM_ID_1, USER_ID_1, UUID_1


def test_register_new_user(mock_user_repo: Mock, mock_id_generator: Mock):
    # Given
    mock_user_repo.find_by_telegram_id.return_value = None
    mock_id_generator.generate.return_value = UUID_1

    use_case = RegisterUserUseCase(
        user_repository=mock_user_repo, id_generator=mock_id_generator
    )

    # When
    result = use_case.execute(telegram_id=TELEGRAM_ID_1, username="John")

    # Then
    assert result.id == USER_ID_1
    assert result.telegram_id == TELEGRAM_ID_1
    assert result.username == "John"

    mock_user_repo.find_by_telegram_id.assert_called_once_with(TELEGRAM_ID_1)
    mock_user_repo.save.assert_called_once_with(
        User(id=USER_ID_1, telegram_id=TELEGRAM_ID_1, username="John")
    )


def test_register_existing_user_returns_same_user(
    mock_user_repo: Mock, mock_id_generator: Mock
):
    # Given
    existing_user = User(id=USER_ID_1, telegram_id=TELEGRAM_ID_1, username="John")

    mock_user_repo.find_by_telegram_id.return_value = existing_user

    use_case = RegisterUserUseCase(mock_user_repo, mock_id_generator)

    # When
    result = use_case.execute(telegram_id=TELEGRAM_ID_1, username="John_doe")

    # Then
    assert result is existing_user

    mock_user_repo.find_by_telegram_id.assert_called_once_with(TELEGRAM_ID_1)
    mock_user_repo.save.assert_not_called()
