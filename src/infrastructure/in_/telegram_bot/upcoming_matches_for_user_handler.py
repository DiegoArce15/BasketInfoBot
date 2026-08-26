from telegram import Update
from telegram.ext import ContextTypes

from src.application.get_upcoming_matches_by_telegram_id_use_case import (
    GetUpcomingMatchesByTelegramIdUseCase,
)
from src.domain.user import TelegramId


class UpcomingMatchesForUserHandler:
    def __init__(
        self,
        get_upcoming_matches_by_telegram_id_use_case: GetUpcomingMatchesByTelegramIdUseCase,
    ) -> None:
        self.get_upcoming_matches_by_telegram_id_use_case = (
            get_upcoming_matches_by_telegram_id_use_case
        )

    async def handle(
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
