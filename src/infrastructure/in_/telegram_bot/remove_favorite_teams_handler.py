import uuid

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.application.get_favorite_teams_by_telegram_id_use_case import (
    GetFavoriteTeamsByTelegramIdUseCase,
)
from src.application.remove_favorite_team_by_telegram_id_use_case import (
    RemoveFavoriteTeamByTelegramIdUseCase,
)
from src.domain.team import TeamId
from src.domain.user import TelegramId


class RemoveFavoriteTeamHandler:
    def __init__(
        self,
        get_favorite_teams_by_telegram_id_use_case: GetFavoriteTeamsByTelegramIdUseCase,
        remove_favorite_team_by_telegram_id_use_case: RemoveFavoriteTeamByTelegramIdUseCase,
    ) -> None:
        self.get_favorite_teams_by_telegram_id_use_case = (
            get_favorite_teams_by_telegram_id_use_case
        )
        self.remove_favorite_team_by_telegram_id_use_case = (
            remove_favorite_team_by_telegram_id_use_case
        )

    async def handle(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Muestra los equipos favoritos del usuario para eliminarlos."""
        user = update.effective_user

        if not user or not update.message:
            return

        teams = self.get_favorite_teams_by_telegram_id_use_case.execute(
            telegram_id=TelegramId(user.id)
        )

        if not teams:
            await update.message.reply_text("No tienes equipos favoritos.")
            return

        keyboard = [
            [
                InlineKeyboardButton(
                    team.name,
                    callback_data=f"remove:{team.id.value}",
                )
            ]
            for team in teams
        ]

        await update.message.reply_text(
            "❌ *Selecciona el equipo que quieres quitar:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    async def callback_handle(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Elimina el equipo seleccionado de los favoritos."""
        query = update.callback_query

        if not query or not query.data:
            return

        await query.answer()

        try:
            raw_team_id = query.data.removeprefix("remove:")
            team_id = TeamId(uuid.UUID(raw_team_id))

            self.remove_favorite_team_by_telegram_id_use_case.execute(
                telegram_id=TelegramId(query.from_user.id),
                team_id=team_id,
            )

            await query.edit_message_text("✅ ¡Equipo eliminado de tus favoritos!")

        except ValueError as exc:
            await query.edit_message_text(f"❌ Error: {exc!s}")
