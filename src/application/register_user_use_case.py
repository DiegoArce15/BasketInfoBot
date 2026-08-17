from src.domain.entities import User, UserId
from src.domain.user_repository import UserRepository


class RegisterUserUseCase:
    """Registra un nuevo usuario cuando inicia interacción con el bot."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(self, user_id: UserId, username: str | None = None) -> User:
        existing_user = self.user_repo.find_by_id(user_id)

        if existing_user:
            return existing_user

        new_user = User(id=user_id, username=username)
        self.user_repo.save(new_user)
        return new_user