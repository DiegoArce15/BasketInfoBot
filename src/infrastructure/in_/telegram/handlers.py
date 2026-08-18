from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.application.add_favorite_team_use_case import AddFavoriteTeamUseCase
from src.application.get_available_teams_use_case import GetAvailableTeamsUseCase
from src.application.get_upcoming_matches_by_user_use_case import (
    GetUpcomingMatchesByUserUseCase,
)
from src.application.register_user_use_case import RegisterUserUseCase
from src.domain.entities import TeamId, UserId


class TelegramBotHandlers:
    """Clase contenedora de los handlers de Telegram para BasketInfoBot."""

    def __init__(
        self,
        register_user_use_case: RegisterUserUseCase,
        add_favorite_team_use_case: AddFavoriteTeamUseCase,
        get_available_teams_use_case: GetAvailableTeamsUseCase,
        get_upcoming_matches_by_user_use_case: GetUpcomingMatchesByUserUseCase,
    ):
        self.register_user_use_case = register_user_use_case
        self.add_favorite_team_use_case = add_favorite_team_use_case
        self.get_available_teams_use_case = get_available_teams_use_case
        self.get_upcoming_matches_by_user_use_case = get_upcoming_matches_by_user_use_case

    async def start_handler(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Comando /start"""
        user = update.effective_user
        if not user or not update.message:
            return

        self.register_user_use_case.execute(
            user_id=UserId(user.id), username=user.username
        )

        await update.message.reply_text(
            f"¡Hola {user.first_name}! 🏀\n"
            "Te has registrado correctamente en BasketInfoBot.\n\n"
            "Comandos disponibles:\n"
            "• `/favorito <id_equipo>` - Añadir un equipo a favoritos\n"
            "• `/partidos` - Ver tus próximos partidos"
        )

    async def select_favorite_team_handler(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Muestra los equipos guardados en la BD como botones interactivos."""
        if not update.message:
            return

        # Consultamos los equipos que existen en la base de datos
        teams = self.get_available_teams_use_case.execute()

        if not teams:
            await update.message.reply_text(
                "Aún no hay equipos registrados en el sistema. Inténtalo más tarde."
            )
            return

        # Creamos un botón por cada equipo recuperado de la BD
        keyboard = [
            [InlineKeyboardButton(team.name, callback_data=f"fav_{team.id.value}")]
            for team in teams
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "🏀 *Selecciona tu equipo favorito:*",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
    async def favorite_callback_handler(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Maneja el clic en uno de los botones de equipo."""
        query = update.callback_query
        if not query or not query.data:
            return

        await query.answer()

        # Extraemos el ID del callback_data (ej. "fav_real-madrid")
        raw_team_id = query.data.replace("fav_", "")

        try:
            self.add_favorite_team_use_case.execute(
                user_id=UserId(query.from_user.id),
                team_id=TeamId(raw_team_id)
            )
            await query.edit_message_text(
                "✅ ¡Equipo guardado en tus favoritos!"
            )
        except ValueError as exc:
            await query.edit_message_text(f"❌ Error: {exc!s}")

    async def upcoming_matches_handler(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Comando /partidos"""
        user = update.effective_user
        if not user or not update.message:
            return

        matches = self.get_upcoming_matches_by_user_use_case.execute(
            user_id=UserId(user.id)
        )

        if not matches:
            await update.message.reply_text(
                "No hay partidos próximos para tus equipos favoritos"
            )
            return

        lines = ["🏀 *Próximos Partidos:*\n"]
        for match in matches:
            date_str = match.start_time.strftime("%d/%m/%Y a las %H:%M")
            channels = match.channels if match.channels else "Sin confirmar"
            lines.append(
                f"• *{match.home_team_name}* vs *{match.away_team_name}*\n"
                f"  🗓️ {date_str} UTC\n"
                f"  📺 TVs: {channels}\n"
            )

        await update.message.reply_markdown("\n".join(lines))