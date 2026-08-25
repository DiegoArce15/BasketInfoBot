import uuid

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.application.add_favorite_team_by_telegram_id_use_case import (
    AddFavoriteTeamByTelegramIdUseCase,
)
from src.application.get_available_teams_use_case import GetAvailableTeamsUseCase
from src.application.get_favorite_teams_by_telegram_id_use_case import (
    GetFavoriteTeamsByTelegramIdUseCase,
)
from src.application.get_upcoming_matches_by_telegram_id_use_case import (
    GetUpcomingMatchesByTelegramIdUseCase,
)
from src.application.register_user_use_case import RegisterUserUseCase
from src.application.remove_favorite_team_by_telegram_id_use_case import (
    RemoveFavoriteTeamByTelegramIdUseCase,
)
from src.domain.entities import TeamId, TelegramId


class TelegramBotHandlers:
    def __init__(
        self,
        register_user_use_case: RegisterUserUseCase,
        add_favorite_team_by_telegram_id_use_case: AddFavoriteTeamByTelegramIdUseCase,
        remove_favorite_team_by_telegram_id_use_case: RemoveFavoriteTeamByTelegramIdUseCase,
        get_favorite_teams_by_telegram_id_use_case: GetFavoriteTeamsByTelegramIdUseCase,
        get_available_teams_use_case: GetAvailableTeamsUseCase,
        get_upcoming_matches_by_telegram_id_use_case: GetUpcomingMatchesByTelegramIdUseCase,
    ) -> None:
        self.register_user_use_case = register_user_use_case
        self.add_favorite_team_by_telegram_id_use_case = (
            add_favorite_team_by_telegram_id_use_case
        )
        self.remove_favorite_team_by_telegram_id_use_case = (
            remove_favorite_team_by_telegram_id_use_case
        )
        self.get_favorite_teams_by_telegram_id_use_case = (
            get_favorite_teams_by_telegram_id_use_case
        )
        self.get_available_teams_use_case = get_available_teams_use_case
        self.get_upcoming_matches_by_telegram_id_use_case = (
            get_upcoming_matches_by_telegram_id_use_case
        )

    async def start_handler(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Comando /start."""
        user = update.effective_user

        if not user or not update.message:
            return

        self.register_user_use_case.execute(
            telegram_id=TelegramId(user.id),
            username=user.username,
        )

        await update.message.reply_text(
            f"¡Hola {user.first_name}! 🏀\n"
            "Te has registrado correctamente en BasketInfoBot.\n\n"
            "Comandos disponibles:\n"
            "• `/favorito` - Añadir un equipo a favoritos\n"
            "• `/quitarfavorito` - Quitar un equipo de favoritos\n"
            "• `/partidos` - Ver tus próximos partidos",
            parse_mode="Markdown",
        )

    async def select_favorite_team_handler(
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
            [
                InlineKeyboardButton(
                    team.name,
                    callback_data=f"fav:{team.id.value}",
                )
            ]
            for team in teams
        ]

        await update.message.reply_text(
            "🏀 *Selecciona tu equipo favorito:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    async def select_remove_favorite_team_handler(
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

    async def favorite_team_callback_handler(
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

    async def remove_favorite_team_callback_handler(
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

    async def upcoming_matches_handler(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Comando /partidos."""
        user = update.effective_user

        if not user or not update.message:
            return

        matches = self.get_upcoming_matches_by_telegram_id_use_case.execute(
            telegram_id=TelegramId(user.id)
        )

        if not matches:
            await update.message.reply_text(
                "No hay partidos próximos para tus equipos favoritos."
            )
            return

        lines = ["🏀 *Próximos Partidos:*\n"]

        for match in matches:
            date_str = match.start_time.strftime("%d/%m/%Y a las %H:%M")

            if match.channels:
                channels_str = ", ".join(match.channels)
            else:
                channels_str = "Sin confirmar"

            lines.append(
                f"• *{match.home_team_name}* vs "
                f"*{match.away_team_name}*\n"
                f"  🗓️ {date_str} UTC\n"
                f"  📺 TVs: {channels_str}\n"
            )

        await update.message.reply_markdown("\n".join(lines))
