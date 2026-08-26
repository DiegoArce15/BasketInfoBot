from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from src.application.get_upcoming_matches_by_telegram_id_use_case import (
    MatchResponseDTO,
)
from src.domain.team import Team
from src.domain.user import TelegramId
from src.infrastructure.in_.telegram_bot.handlers import TelegramBotHandlers
from tests.test_utils.constants import TEAM_ID_1, TEAM_ID_2, TELEGRAM_ID_1


@pytest.fixture
def register_user_use_case():
    return MagicMock()


@pytest.fixture
def get_available_teams_use_case():
    return MagicMock()


@pytest.fixture
def add_favorite_team_by_telegram_id_use_case():
    return MagicMock()


@pytest.fixture
def get_favorite_teams_by_telegram_id_use_case():
    return MagicMock()


@pytest.fixture
def remove_favorite_team_by_telegram_id_use_case():
    return MagicMock()


@pytest.fixture
def get_upcoming_matches_by_telegram_id_use_case():
    return MagicMock()


@pytest.fixture
def handler(
    register_user_use_case,
    get_available_teams_use_case,
    get_favorite_teams_by_telegram_id_use_case,
    add_favorite_team_by_telegram_id_use_case,
    remove_favorite_team_by_telegram_id_use_case,
    get_upcoming_matches_by_telegram_id_use_case,
):
    return TelegramBotHandlers(
        register_user_use_case=register_user_use_case,
        get_available_teams_use_case=get_available_teams_use_case,
        get_favorite_teams_by_telegram_id_use_case=(
            get_favorite_teams_by_telegram_id_use_case
        ),
        add_favorite_team_by_telegram_id_use_case=(
            add_favorite_team_by_telegram_id_use_case
        ),
        remove_favorite_team_by_telegram_id_use_case=(
            remove_favorite_team_by_telegram_id_use_case
        ),
        get_upcoming_matches_by_telegram_id_use_case=(
            get_upcoming_matches_by_telegram_id_use_case
        ),
    )


async def test_start_handler_registers_user_and_sends_welcome_message(
    register_user_use_case,
    handler,
):
    # Given
    telegram_user = Mock()
    telegram_user.id = 123456789
    telegram_user.username = "john_doe"
    telegram_user.first_name = "John"

    update = MagicMock()
    update.effective_user = telegram_user
    update.message.reply_text = AsyncMock()

    # When
    await handler.start_handler(update, Mock())

    # Then
    register_user_use_case.execute.assert_called_once_with(
        telegram_id=TelegramId(123456789),
        username="john_doe",
    )

    update.message.reply_text.assert_awaited_once_with(
        "¡Hola John! 🏀\n"
        "Te has registrado correctamente en BasketInfoBot.\n\n"
        "Comandos disponibles:\n"
        "• `/favorito` - Añadir un equipo a favoritos\n"
        "• `/quitarfavorito` - Quitar un equipo de favoritos\n"
        "• `/partidos` - Ver tus próximos partidos",
        parse_mode="Markdown",
    )


async def test_start_handler_registers_user_without_username(
    register_user_use_case,
    handler,
):
    # Given
    telegram_user = Mock()
    telegram_user.id = 123456789
    telegram_user.username = None
    telegram_user.first_name = "John"

    update = MagicMock()
    update.effective_user = telegram_user
    update.message.reply_text = AsyncMock()

    # When
    await handler.start_handler(update, MagicMock())

    # Then
    register_user_use_case.execute.assert_called_once_with(
        telegram_id=TelegramId(123456789),
        username=None,
    )


async def test_select_favorite_team_handler_shows_available_teams(
    handler,
    get_available_teams_use_case,
):
    # Given
    real_madrid = Team(
        id=TEAM_ID_1,
        name="Real Madrid",
        short_name="RMB",
    )
    valencia = Team(
        id=TEAM_ID_2,
        name="Valencia Basket",
        short_name="VBC",
    )

    get_available_teams_use_case.execute.return_value = [
        real_madrid,
        valencia,
    ]

    update = MagicMock()
    update.message.reply_text = AsyncMock()

    # When
    await handler.select_favorite_team_handler(update, MagicMock())

    # Then
    get_available_teams_use_case.execute.assert_called_once_with()

    update.message.reply_text.assert_awaited_once()

    reply_markup = update.message.reply_text.call_args.kwargs["reply_markup"]
    buttons = reply_markup.inline_keyboard

    assert buttons[0][0].text == "Real Madrid"
    assert buttons[0][0].callback_data == "fav:00000000-0000-0000-0000-000000000001"

    assert buttons[1][0].text == "Valencia Basket"
    assert buttons[1][0].callback_data == "fav:00000000-0000-0000-0000-000000000002"


async def test_select_remove_favorite_team_handler_shows_user_favorite_teams(
    handler,
    get_favorite_teams_by_telegram_id_use_case,
):
    # Given
    get_favorite_teams_by_telegram_id_use_case.execute.return_value = [
        Team(
            id=TEAM_ID_1,
            name="Real Madrid",
            short_name="RMB",
            country="Spain",
        ),
        Team(
            id=TEAM_ID_2,
            name="Valencia Basket",
            short_name="VBC",
            country="Spain",
        ),
    ]

    update = MagicMock()
    update.effective_user.id = 1
    update.message.reply_text = AsyncMock()

    # When
    await handler.select_remove_favorite_team_handler(
        update,
        MagicMock(),
    )

    # Then
    get_favorite_teams_by_telegram_id_use_case.execute.assert_called_once_with(
        telegram_id=TELEGRAM_ID_1,
    )

    update.message.reply_text.assert_awaited_once()

    reply_markup = update.message.reply_text.call_args.kwargs["reply_markup"]
    buttons = reply_markup.inline_keyboard

    assert buttons[0][0].text == "Real Madrid"
    assert buttons[0][0].callback_data == "remove:00000000-0000-0000-0000-000000000001"

    assert buttons[1][0].text == "Valencia Basket"
    assert buttons[1][0].callback_data == "remove:00000000-0000-0000-0000-000000000002"


async def test_favorite_team_callback_handler_adds_selected_team_to_favorites(
    handler,
    add_favorite_team_by_telegram_id_use_case,
):
    # Given
    update = MagicMock()

    update.callback_query.from_user.id = 1
    update.callback_query.data = "fav:00000000-0000-0000-0000-000000000001"

    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()

    # When
    await handler.favorite_team_callback_handler(
        update,
        MagicMock(),
    )

    # Then
    add_favorite_team_by_telegram_id_use_case.execute.assert_called_once_with(
        telegram_id=TELEGRAM_ID_1,
        team_id=TEAM_ID_1,
    )

    update.callback_query.answer.assert_awaited_once()

    update.callback_query.edit_message_text.assert_awaited_once_with(
        "✅ ¡Equipo guardado en tus favoritos!"
    )


async def test_remove_favorite_team_callback_handler_removes_selected_team(
    handler,
    remove_favorite_team_by_telegram_id_use_case,
):
    # Given
    update = MagicMock()

    update.callback_query.from_user.id = 1
    update.callback_query.data = "remove:00000000-0000-0000-0000-000000000001"

    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()

    # When
    await handler.remove_favorite_team_callback_handler(
        update,
        MagicMock(),
    )

    # Then
    remove_favorite_team_by_telegram_id_use_case.execute.assert_called_once_with(
        telegram_id=TELEGRAM_ID_1,
        team_id=TEAM_ID_1,
    )

    update.callback_query.answer.assert_awaited_once()

    update.callback_query.edit_message_text.assert_awaited_once_with(
        "✅ ¡Equipo eliminado de tus favoritos!"
    )


async def test_upcoming_matches_handler_shows_message_when_there_are_no_matches(
    handler,
    get_upcoming_matches_by_telegram_id_use_case,
):
    # Given
    get_upcoming_matches_by_telegram_id_use_case.execute.return_value = []

    update = MagicMock()
    update.effective_user.id = 1
    update.message.reply_text = AsyncMock()

    # When
    await handler.upcoming_matches_handler(update, MagicMock())

    # Then
    get_upcoming_matches_by_telegram_id_use_case.execute.assert_called_once_with(
        telegram_id=TELEGRAM_ID_1,
    )

    update.message.reply_text.assert_awaited_once_with(
        "No hay partidos próximos para tus equipos favoritos."
    )


async def test_upcoming_matches_handler_shows_upcoming_matches(
    handler,
    get_upcoming_matches_by_telegram_id_use_case,
):
    # Given
    match = MatchResponseDTO(
        home_team_name="Real Madrid",
        away_team_name="Valencia Basket",
        start_time=datetime(
            2026,
            8,
            20,
            20,
            30,
            tzinfo=UTC,
        ),
        score=None,
        channels=["Movistar", "ESPN"],
        league="Liga ACB",
        status="SCHEDULED",
    )

    get_upcoming_matches_by_telegram_id_use_case.execute.return_value = [match]

    update = MagicMock()
    update.effective_user.id = 1
    update.message.reply_markdown = AsyncMock()

    # When
    await handler.upcoming_matches_handler(update, MagicMock())

    # Then
    get_upcoming_matches_by_telegram_id_use_case.execute.assert_called_once_with(
        telegram_id=TELEGRAM_ID_1,
    )

    update.message.reply_markdown.assert_awaited_once()

    message = update.message.reply_markdown.call_args.args[0]

    assert "Real Madrid" in message
    assert "Valencia Basket" in message
    assert "20/08/2026 a las 20:30" in message
    assert "Movistar, ESPN" in message
