from abc import ABC, abstractmethod

from src.domain.entities import TelegramId, User, UserId


class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> None:
        """Save or update an User"""

    @abstractmethod
    def find_by_id(self, user_id: UserId) -> User | None: ...

    @abstractmethod
    def find_by_telegram_id(self, telegram_id: TelegramId) -> User | None: ...
