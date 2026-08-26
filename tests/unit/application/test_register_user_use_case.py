from unittest.mock import Mock
from uuid import UUID

from src.application.register_user_use_case import RegisterUserUseCase
from src.domain.user import User
from tests.test_utils.constants import TELEGRAM_ID_1, USER_ID_1, UUID_1
from tests.test_utils.user_mother import an_user


def test_register_new_user(
    mock_user_repo: Mock,
    mock_id_generator: Mock,
) -> None:
    # Given
    fixture = RegisterUserTestFixture(
        mock_user_repo,
        mock_id_generator,
    )

    fixture.given_user_repository_returns(None)
    fixture.given_id_generator_returns(UUID_1)

    # When
    result = fixture.use_case.execute(
        telegram_id=TELEGRAM_ID_1,
        username="John",
    )

    # Then
    assert result == an_user(
        id=USER_ID_1,
        telegram_id=TELEGRAM_ID_1,
        username="John",
    )

    mock_user_repo.find_by_telegram_id.assert_called_once_with(TELEGRAM_ID_1)
    mock_id_generator.generate.assert_called_once()
    mock_user_repo.save.assert_called_once_with(result)


def test_register_existing_user_returns_same_user(
    mock_user_repo: Mock,
    mock_id_generator: Mock,
) -> None:
    # Given
    fixture = RegisterUserTestFixture(
        mock_user_repo,
        mock_id_generator,
    )

    existing_user = an_user(
        id=USER_ID_1,
        telegram_id=TELEGRAM_ID_1,
        username="John",
    )

    fixture.given_user_repository_returns(existing_user)

    # When
    result = fixture.use_case.execute(
        telegram_id=TELEGRAM_ID_1,
        username="John_doe",
    )

    # Then
    assert result is existing_user

    mock_user_repo.find_by_telegram_id.assert_called_once_with(TELEGRAM_ID_1)
    mock_id_generator.generate.assert_not_called()
    mock_user_repo.save.assert_not_called()


class RegisterUserTestFixture:
    def __init__(
        self,
        user_repository: Mock,
        id_generator: Mock,
    ) -> None:
        self.user_repository = user_repository
        self.id_generator = id_generator

        self.use_case = RegisterUserUseCase(
            user_repository=self.user_repository,
            id_generator=self.id_generator,
        )

    def given_user_repository_returns(self, user: User | None) -> None:
        self.user_repository.find_by_telegram_id.return_value = user

    def given_id_generator_returns(self, user_id: UUID) -> None:
        self.id_generator.generate.return_value = user_id
