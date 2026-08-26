from unittest.mock import AsyncMock, MagicMock

import pytest

from src.domain.team import Team
from src.infrastructure.in_.telegram_bot.select_favorite_teams_handler import (
    SelectFavoriteTeamHandler,
)
from tests.test_utils.constants import TEAM_ID_1, TEAM_ID_2, TELEGRAM_ID_1


@pytest.fixture
def get_available_teams_use_case() -> MagicMock:
    return MagicMock()


@pytest.fixture
def add_favorite_team_by_telegram_id_use_case() -> MagicMock:
    return MagicMock()


@pytest.fixture
def handler(
    get_available_teams_use_case: MagicMock,
    add_favorite_team_by_telegram_id_use_case: MagicMock,
) -> SelectFavoriteTeamHandler:
    return SelectFavoriteTeamHandler(
        get_available_teams_use_case=get_available_teams_use_case,
        add_favorite_team_by_telegram_id_use_case=(
            add_favorite_team_by_telegram_id_use_case
        ),
    )


async def test_select_favorite_team_handler_shows_available_teams(
    handler: SelectFavoriteTeamHandler,
    get_available_teams_use_case: MagicMock,
    add_favorite_team_by_telegram_id_use_case: MagicMock,
) -> None:
    # Given
    fixture = SelectFavoriteTeamHandlerTestFixture(
        handler,
        get_available_teams_use_case,
        add_favorite_team_by_telegram_id_use_case,
    )

    fixture.given_available_teams(
        [
            Team(id=TEAM_ID_1, name="Real Madrid", short_name="RMB"),
            Team(id=TEAM_ID_2, name="Valencia Basket", short_name="VBC"),
        ]
    )

    # When
    await fixture.handler.handle(fixture.update, MagicMock())

    # Then
    get_available_teams_use_case.execute.assert_called_once_with()

    fixture.update.message.reply_text.assert_awaited_once()

    reply_markup = fixture.update.message.reply_text.call_args.kwargs["reply_markup"]
    buttons = reply_markup.inline_keyboard

    assert buttons[0][0].text == "Real Madrid"
    assert buttons[0][0].callback_data == f"fav:{TEAM_ID_1.value}"

    assert buttons[1][0].text == "Valencia Basket"
    assert buttons[1][0].callback_data == f"fav:{TEAM_ID_2.value}"


async def test_favorite_team_callback_handler_adds_selected_team_to_favorites(
    handler: SelectFavoriteTeamHandler,
    get_available_teams_use_case: MagicMock,
    add_favorite_team_by_telegram_id_use_case: MagicMock,
) -> None:
    # Given
    fixture = SelectFavoriteTeamHandlerTestFixture(
        handler,
        get_available_teams_use_case,
        add_favorite_team_by_telegram_id_use_case,
    )

    fixture.given_favorite_team_callback(team_id=TEAM_ID_1)

    # When
    await fixture.handler.callback_handle(fixture.update, MagicMock())

    # Then
    add_favorite_team_by_telegram_id_use_case.execute.assert_called_once_with(
        telegram_id=TELEGRAM_ID_1,
        team_id=TEAM_ID_1,
    )

    fixture.update.callback_query.answer.assert_awaited_once()

    fixture.update.callback_query.edit_message_text.assert_awaited_once_with(
        "✅ ¡Equipo guardado en tus favoritos!"
    )


class SelectFavoriteTeamHandlerTestFixture:
    def __init__(
        self,
        handler: SelectFavoriteTeamHandler,
        get_available_teams_use_case: MagicMock,
        add_favorite_team_by_telegram_id_use_case: MagicMock,
    ) -> None:
        self.handler = handler
        self.get_available_teams_use_case = get_available_teams_use_case
        self.add_favorite_team_by_telegram_id_use_case = (
            add_favorite_team_by_telegram_id_use_case
        )

        self.update = MagicMock()
        self.update.message.reply_text = AsyncMock()

        self.update.callback_query.from_user.id = TELEGRAM_ID_1.value
        self.update.callback_query.answer = AsyncMock()
        self.update.callback_query.edit_message_text = AsyncMock()

    def given_available_teams(self, teams: list[Team]) -> None:
        self.get_available_teams_use_case.execute.return_value = teams

    def given_favorite_team_callback(self, team_id) -> None:
        self.update.callback_query.data = f"fav:{team_id.value}"
