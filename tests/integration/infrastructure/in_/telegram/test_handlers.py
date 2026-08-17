from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.domain.entities import Match, MatchId, Team, TeamId, UserId
from src.infrastructure.in_.telegram.handlers import TelegramBotHandlers


@pytest.fixture
def register_user_use_case():
    return MagicMock()


@pytest.fixture
def get_available_teams_use_case():
    return MagicMock()


@pytest.fixture
def add_favorite_team_use_case():
    return MagicMock()


@pytest.fixture
def get_upcoming_matches_use_case():
    return MagicMock()


@pytest.fixture
def handler(
    register_user_use_case,
    get_available_teams_use_case,
    add_favorite_team_use_case,
    get_upcoming_matches_use_case,
):
    return TelegramBotHandlers(
        register_user_use_case=register_user_use_case,
        get_available_teams_use_case=get_available_teams_use_case,
        add_favorite_team_use_case=add_favorite_team_use_case,
        get_upcoming_matches_use_case=get_upcoming_matches_use_case,
    )

async def test_select_favorite_team_handler_shows_available_teams(
        handler,
        get_available_teams_use_case
):
    # Given
    real_madrid = Team(
        id=TeamId("real-madrid"),
        name="Real Madrid",
    )

    valencia = Team(
        id=TeamId("valencia-basket"),
        name="Valencia Basket",
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
    assert buttons[0][0].callback_data == "fav_real-madrid"

    assert buttons[1][0].text == "Valencia Basket"
    assert buttons[1][0].callback_data == "fav_valencia-basket"

async def test_favorite_team_callback_adds_selected_team_to_favorites(
    handler,
    add_favorite_team_use_case
):
    # Given
    update = MagicMock()

    update.callback_query.from_user.id = 1
    update.callback_query.data = "fav_valencia-basket"

    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()

    # When
    await handler.favorite_callback_handler(update, MagicMock())

    # Then
    add_favorite_team_use_case.execute.assert_called_once_with(
        user_id=UserId(1),
        team_id=TeamId("valencia-basket"),
    )

    update.callback_query.answer.assert_awaited_once()

    update.callback_query.edit_message_text.assert_awaited_once_with(
        '✅ ¡Equipo guardado en tus favoritos!'    )

async def test_upcoming_matches_handler_shows_message_when_there_are_no_matches(
    handler,
    get_upcoming_matches_use_case
):
    # Given
    get_upcoming_matches_use_case.execute.return_value = []

    update = MagicMock()
    update.effective_user.id = 1
    update.message.reply_text = AsyncMock()

    # When
    await handler.upcoming_matches_handler(update, MagicMock())

    # Then
    get_upcoming_matches_use_case.execute.assert_called_once_with(
        user_id=UserId(1),
    )

    update.message.reply_text.assert_awaited_once_with(
        "No hay partidos próximos para tus equipos favoritos"
    )

async def test_upcoming_matches_handler_shows_upcoming_matches(
    handler,
    get_upcoming_matches_use_case,
):
    # Given
    home_team = Team(
        id=TeamId("real-madrid"),
        name="Real Madrid",
    )

    away_team = Team(
        id=TeamId("valencia-basket"),
        name="Valencia Basket",
    )

    match = Match(
        id=MatchId("2026-08-20-rm-valencia"),
        home_team=home_team,
        away_team=away_team,
        start_time=datetime(
            2026, 8, 20, 20, 30, tzinfo=UTC
        ),
        channel="Movistar",
        league="Liga ACB",
    )

    get_upcoming_matches_use_case.execute.return_value = [match]

    update = MagicMock()
    update.effective_user.id = 1
    update.message.reply_markdown = AsyncMock()

    # When
    await handler.upcoming_matches_handler(update, MagicMock())

    # Then
    get_upcoming_matches_use_case.execute.assert_called_once_with(
        user_id=UserId(1),
    )

    update.message.reply_markdown.assert_awaited_once()

    message = update.message.reply_markdown.call_args.args[0]

    assert "Real Madrid" in message
    assert "Valencia Basket" in message
    assert "20/08/2026 a las 20:30" in message
    assert "Movistar" in message