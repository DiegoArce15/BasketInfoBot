from src.domain.entities import TelegramId, User, UserId
from src.domain.id_generator import IdGenerator
from src.domain.user_repository import UserRepository


class RegisterUserUseCase:
    """Registra un nuevo usuario cuando inicia interacción con el bot."""

    def __init__(
        self, user_repository: UserRepository, id_generator: IdGenerator
    ) -> None:
        self._user_repository = user_repository
        self._id_generator = id_generator

    def execute(self, telegram_id: TelegramId, username: str | None = None) -> User:
        existing_user = self._user_repository.find_by_telegram_id(telegram_id)

        if existing_user:
            return existing_user

        new_user = User(
            id=UserId(self._id_generator.generate()),
            telegram_id=telegram_id,
            username=username,
        )
        self._user_repository.save(new_user)
        return new_user
