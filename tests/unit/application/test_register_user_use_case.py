from src.application.register_user_use_case import RegisterUserUseCase
from src.domain.entities import User, UserId


def test_register_new_user(user_repo):
    # Given
    use_case = RegisterUserUseCase(user_repo)
    user_id = 123456

    # When
    user = use_case.execute(user_id=user_id, username="basket_fan")

    # Then
    assert user.id.value == user_id
    assert user.username == "basket_fan"
    assert user_repo.find_by_id(UserId(user_id)) is not None


def test_register_existing_user_returns_same_user(user_repo):
    # Given
    user_id = UserId(123456)
    existing_user = User(id=user_id, username="old_name")
    user_repo.save(existing_user)

    use_case = RegisterUserUseCase(user_repo)

    # When
    user = use_case.execute(user_id=123456, username="new_name")

    # Then
    assert user.username == "old_name"  # Mantiene los datos existentes