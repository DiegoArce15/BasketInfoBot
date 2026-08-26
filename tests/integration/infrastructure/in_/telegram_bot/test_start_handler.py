from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from src.domain.user import TelegramId
from src.infrastructure.in_.telegram_bot.start_handler import StartHandler


@pytest.fixture
def register_user_use_case():
    return MagicMock()


@pytest.fixture
def handler(register_user_use_case):
    return StartHandler(register_user_use_case)


async def test_start_handler_registers_user_and_sends_welcome_message(
    register_user_use_case: MagicMock,
    handler: StartHandler,
) -> None:
    # Given
    fixture = StartHandlerTestFixture(register_user_use_case, handler)

    fixture.given_telegram_user(
        telegram_id=123456789,
        username="john_doe",
        first_name="John",
    )

    # When
    await fixture.handler.handle(fixture.update, Mock())

    # Then
    register_user_use_case.execute.assert_called_once_with(
        telegram_id=TelegramId(123456789),
        username="john_doe",
    )

    fixture.update.message.reply_text.assert_awaited_once_with(
        "¡Hola John! 🏀\n"
        "Te has registrado correctamente en BasketInfoBot.\n\n"
        "Comandos disponibles:\n"
        "• `/favorito` - Añadir un equipo a favoritos\n"
        "• `/quitarfavorito` - Quitar un equipo de favoritos\n"
        "• `/partidos` - Ver tus próximos partidos",
        parse_mode="Markdown",
    )


async def test_start_handler_registers_user_without_username(
    register_user_use_case: MagicMock,
    handler: StartHandler,
) -> None:
    # Given
    fixture = StartHandlerTestFixture(register_user_use_case, handler)

    fixture.given_telegram_user(
        telegram_id=123456789,
        username=None,
        first_name="John",
    )

    # When
    await fixture.handler.handle(fixture.update, Mock())

    # Then
    register_user_use_case.execute.assert_called_once_with(
        telegram_id=TelegramId(123456789),
        username=None,
    )


class StartHandlerTestFixture:
    def __init__(
        self,
        register_user_use_case: MagicMock,
        handler: StartHandler,
    ) -> None:
        self.register_user_use_case = register_user_use_case
        self.handler = handler

        self.update = MagicMock()
        self.update.message.reply_text = AsyncMock()

    def given_telegram_user(
        self,
        telegram_id: int,
        username: str,
        first_name: str,
    ) -> None:
        self.update.effective_user.id = telegram_id
        self.update.effective_user.username = username
        self.update.effective_user.first_name = first_name
