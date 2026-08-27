from unittest.mock import AsyncMock, MagicMock

import pytest

from src.infrastructure.in_.telegram_bot.help_handler import HelpHandler


@pytest.fixture
def handler():
    return HelpHandler()


async def test_help_handler_shows_available_commands(
    handler,
) -> None:
    # Given
    update = MagicMock()
    update.message.reply_text = AsyncMock()

    # When
    await handler.handle(update, MagicMock())

    # Then
    update.message.reply_text.assert_awaited_once_with(
        "🏀 Comandos disponibles:\n\n"
        "• /start - Registrarte en BasketInfoBot\n"
        "• /favorito - Añadir un equipo a favoritos\n"
        "• /quitarfavorito - Quitar un equipo de favoritos\n"
        "• /partidos - Ver tus próximos partidos\n"
        "• /ayuda - Mostrar esta ayuda"
    )
