import uuid

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.application.add_favorite_team_by_telegram_id_use_case import (
    AddFavoriteTeamByTelegramIdUseCase,
)
from src.application.get_available_teams_use_case import GetAvailableTeamsUseCase
from src.domain.team import TeamId
from src.domain.user import TelegramId


class SelectFavoriteTeamHandler:
    def __init__(
        self,
        get_available_teams_use_case: GetAvailableTeamsUseCase,
        add_favorite_team_by_telegram_id_use_case: AddFavoriteTeamByTelegramIdUseCase,
    ) -> None:
        self.get_available_teams_use_case = get_available_teams_use_case
        self.add_favorite_team_by_telegram_id_use_case = (
            add_favorite_team_by_telegram_id_use_case
        )

    async def handle(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Muestra los equipos disponibles para añadir a favoritos."""
        if not update.message:
            return

        teams = self.get_available_teams_use_case.execute()

        if not teams:
            await update.message.reply_text(
                "Aún no hay equipos registrados en el sistema. Inténtalo más tarde."
            )
            return

        keyboard = [
            [InlineKeyboardButton(team.name, callback_data=f"fav:{team.id.value}")]
            for team in teams
        ]

        await update.message.reply_text(
            "🏀 *Selecciona tu equipo favorito:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    async def callback_handle(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Añade el equipo seleccionado a los favoritos."""
        query = update.callback_query

        if not query or not query.data:
            return

        await query.answer()

        try:
            raw_team_id = query.data.removeprefix("fav:")
            team_id = TeamId(uuid.UUID(raw_team_id))

            self.add_favorite_team_by_telegram_id_use_case.execute(
                telegram_id=TelegramId(query.from_user.id),
                team_id=team_id,
            )

            await query.edit_message_text("✅ ¡Equipo guardado en tus favoritos!")

        except ValueError as exc:
            await query.edit_message_text(f"❌ Error: {exc!s}")
