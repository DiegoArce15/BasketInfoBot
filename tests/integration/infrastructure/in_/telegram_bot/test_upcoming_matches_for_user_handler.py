from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from src.application.get_upcoming_matches_by_telegram_id_use_case import (
    MatchResponseDTO,
)
from src.infrastructure.in_.telegram_bot.upcoming_matches_for_user_handler import (
    UpcomingMatchesForUserHandler,
)
from tests.test_utils.constants import TELEGRAM_ID_1


@pytest.fixture
def get_upcoming_matches_by_telegram_id_use_case() -> Mock:
    return MagicMock()


async def test_upcoming_matches_handler_shows_message_when_there_are_no_matches(
    get_upcoming_matches_by_telegram_id_use_case: Mock,
):
    # Given
    fixture = UpcomingMatchesForUserHandlerTestFixture(
        get_upcoming_matches_by_telegram_id_use_case,
    )

    fixture.given_upcoming_matches([])
    fixture.given_telegram_update()

    # When
    await fixture.handler.handle(fixture.update, MagicMock())

    # Then
    fixture.get_upcoming_matches_by_telegram_id_use_case.execute.assert_called_once_with(
        telegram_id=TELEGRAM_ID_1,
    )

    fixture.update.message.reply_text.assert_awaited_once_with(
        "No hay partidos próximos para tus equipos favoritos."
    )


async def test_upcoming_matches_handler_shows_upcoming_matches(
    get_upcoming_matches_by_telegram_id_use_case: Mock,
):
    # Given
    fixture = UpcomingMatchesForUserHandlerTestFixture(
        get_upcoming_matches_by_telegram_id_use_case,
    )

    fixture.given_upcoming_matches(
        [
            MatchResponseDTO(
                home_team_name="Real Madrid",
                away_team_name="Valencia Basket",
                start_time=datetime(2026, 8, 20, 20, 30, tzinfo=UTC),
                score=None,
                channels=["Movistar", "ESPN"],
                league="Liga ACB",
                status="SCHEDULED",
            )
        ]
    )
    fixture.given_telegram_update()

    # When
    await fixture.handler.handle(fixture.update, MagicMock())

    # Then
    fixture.get_upcoming_matches_by_telegram_id_use_case.execute.assert_called_once_with(
        telegram_id=TELEGRAM_ID_1,
    )

    fixture.update.message.reply_markdown.assert_awaited_once()

    message = fixture.update.message.reply_markdown.call_args.args[0]

    assert "Real Madrid" in message
    assert "Valencia Basket" in message
    assert "20/08/2026 a las 20:30" in message
    assert "Movistar, ESPN" in message


class UpcomingMatchesForUserHandlerTestFixture:
    def __init__(
        self,
        get_upcoming_matches_by_telegram_id_use_case: Mock,
    ) -> None:
        self.get_upcoming_matches_by_telegram_id_use_case = (
            get_upcoming_matches_by_telegram_id_use_case
        )
        self.handler = UpcomingMatchesForUserHandler(
            get_upcoming_matches_by_telegram_id_use_case=(
                get_upcoming_matches_by_telegram_id_use_case
            )
        )
        self.update = MagicMock()

    def given_upcoming_matches(
        self,
        matches: list[MatchResponseDTO],
    ) -> None:
        self.get_upcoming_matches_by_telegram_id_use_case.execute.return_value = matches

    def given_telegram_update(self) -> None:
        self.update.effective_user.id = TELEGRAM_ID_1.value
        self.update.message.reply_text = AsyncMock()
        self.update.message.reply_markdown = AsyncMock()
