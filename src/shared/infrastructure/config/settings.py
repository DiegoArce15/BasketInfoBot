import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Configuración de la aplicación obtenida de variables de entorno."""

    @property
    def acb_target_url(self) -> str:
        return self._get_required("ACB_TARGET_URL")

    @property
    def database_url(self) -> str:
        return self._get_required("DATABASE_URL")

    @property
    def telegram_bot_token(self) -> str:
        return self._get_required("TELEGRAM_BOT_TOKEN")

    @staticmethod
    def _get_required(name: str) -> str:
        value = os.getenv(name)

        if not value:
            raise ValueError(f"La variable de entorno '{name}' no está definida.")

        return value
