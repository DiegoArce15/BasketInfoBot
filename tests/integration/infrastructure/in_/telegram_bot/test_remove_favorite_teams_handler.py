from unittest.mock import AsyncMock, MagicMock

import pytest

from src.domain.team import Team, TeamId
from src.infrastructure.in_.telegram_bot.remove_favorite_teams_handler import (
    RemoveFavoriteTeamHandler,
)
from tests.test_utils.constants import TEAM_ID_1, TEAM_ID_2, TELEGRAM_ID_1


@pytest.fixture
def get_favorite_teams_by_telegram_id_use_case() -> MagicMock:
    return MagicMock()


@pytest.fixture
def remove_favorite_team_by_telegram_id_use_case() -> MagicMock:
    return MagicMock()


@pytest.fixture
def handler(
    get_favorite_teams_by_telegram_id_use_case: MagicMock,
    remove_favorite_team_by_telegram_id_use_case: MagicMock,
) -> RemoveFavoriteTeamHandler:
    return RemoveFavoriteTeamHandler(
        get_favorite_teams_by_telegram_id_use_case=(
            get_favorite_teams_by_telegram_id_use_case
        ),
        remove_favorite_team_by_telegram_id_use_case=(
            remove_favorite_team_by_telegram_id_use_case
        ),
    )


async def test_select_remove_favorite_team_handler_shows_user_favorite_teams(
    handler: RemoveFavoriteTeamHandler,
    get_favorite_teams_by_telegram_id_use_case: MagicMock,
    remove_favorite_team_by_telegram_id_use_case: MagicMock,
) -> None:
    # Given
    fixture = RemoveFavoriteTeamHandlerTestFixture(
        handler,
        get_favorite_teams_by_telegram_id_use_case,
        remove_favorite_team_by_telegram_id_use_case,
    )

    fixture.given_favorite_teams(
        [
            Team(id=TEAM_ID_1, name="Real Madrid", short_name="RMB"),
            Team(id=TEAM_ID_2, name="Valencia Basket", short_name="VBC"),
        ]
    )

    # When
    await fixture.handler.handle(fixture.update, MagicMock())

    # Then
    get_favorite_teams_by_telegram_id_use_case.execute.assert_called_once_with(
        telegram_id=TELEGRAM_ID_1,
    )

    fixture.update.message.reply_text.assert_awaited_once()

    reply_markup = fixture.update.message.reply_text.call_args.kwargs["reply_markup"]
    buttons = reply_markup.inline_keyboard

    assert buttons[0][0].text == "Real Madrid"
    assert buttons[0][0].callback_data == f"remove:{TEAM_ID_1.value}"

    assert buttons[1][0].text == "Valencia Basket"
    assert buttons[1][0].callback_data == f"remove:{TEAM_ID_2.value}"


async def test_remove_favorite_team_callback_handler_removes_selected_team(
    handler: RemoveFavoriteTeamHandler,
    get_favorite_teams_by_telegram_id_use_case: MagicMock,
    remove_favorite_team_by_telegram_id_use_case: MagicMock,
) -> None:
    # Given
    fixture = RemoveFavoriteTeamHandlerTestFixture(
        handler,
        get_favorite_teams_by_telegram_id_use_case,
        remove_favorite_team_by_telegram_id_use_case,
    )

    fixture.given_remove_team_callback(team_id=TEAM_ID_1)

    # When
    await fixture.handler.callback_handle(fixture.update, MagicMock())

    # Then
    remove_favorite_team_by_telegram_id_use_case.execute.assert_called_once_with(
        telegram_id=TELEGRAM_ID_1,
        team_id=TEAM_ID_1,
    )

    fixture.update.callback_query.answer.assert_awaited_once()

    fixture.update.callback_query.edit_message_text.assert_awaited_once_with(
        "✅ ¡Equipo eliminado de tus favoritos!"
    )


class RemoveFavoriteTeamHandlerTestFixture:
    def __init__(
        self,
        handler: RemoveFavoriteTeamHandler,
        get_favorite_teams_by_telegram_id_use_case: MagicMock,
        remove_favorite_team_by_telegram_id_use_case: MagicMock,
    ) -> None:
        self.handler = handler
        self.get_favorite_teams_by_telegram_id_use_case = (
            get_favorite_teams_by_telegram_id_use_case
        )
        self.remove_favorite_team_by_telegram_id_use_case = (
            remove_favorite_team_by_telegram_id_use_case
        )

        self.update = MagicMock()
        self.update.effective_user.id = TELEGRAM_ID_1.value
        self.update.message.reply_text = AsyncMock()

        self.update.callback_query.from_user.id = TELEGRAM_ID_1.value
        self.update.callback_query.answer = AsyncMock()
        self.update.callback_query.edit_message_text = AsyncMock()

    def given_favorite_teams(self, teams: list[Team]) -> None:
        self.get_favorite_teams_by_telegram_id_use_case.execute.return_value = teams

    def given_remove_team_callback(self, team_id: TeamId) -> None:
        self.update.callback_query.data = f"remove:{team_id.value}"
