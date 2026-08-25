import logging

from src.domain.id_generator import IdGenerator
from src.domain.user import TelegramId, User, UserId
from src.domain.user_repository import UserRepository

logger = logging.getLogger(__name__)


class RegisterUserUseCase:
    def __init__(
        self, user_repository: UserRepository, id_generator: IdGenerator
    ) -> None:
        self._user_repository = user_repository
        self._id_generator = id_generator

    def execute(self, telegram_id: TelegramId, username: str | None = None) -> User:
        logger.info("Registering new user with telegram_id=%s", telegram_id.value)
        existing_user = self._user_repository.find_by_telegram_id(telegram_id)

        if existing_user:
            logger.warning("User with telegram id %s already exist", telegram_id.value)
            return existing_user

        new_user = User(
            id=UserId(self._id_generator.generate()),
            telegram_id=telegram_id,
            username=username,
        )
        self._user_repository.save(new_user)
        return new_user
