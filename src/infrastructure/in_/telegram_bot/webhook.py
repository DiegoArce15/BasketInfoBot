import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from telegram import Update
from telegram.ext import Application

from src.shared.infrastructure.config.settings import Settings

logger = logging.getLogger(__name__)


def create_webhook_app(
    telegram_app: Application,
    settings: Settings,
) -> FastAPI:
    webhook_url = f"{settings.webhook_url}/telegram/webhook"

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("Initializing Telegram webhook")

        await telegram_app.initialize()

        await telegram_app.bot.set_webhook(
            url=webhook_url,
        )

        await telegram_app.start()

        logger.info("Telegram webhook configured successfully")

        try:
            yield
        finally:
            logger.info("Shutting down Telegram webhook")

            await telegram_app.bot.delete_webhook()
            await telegram_app.stop()
            await telegram_app.shutdown()

            logger.info("Telegram webhook shutdown completed")

    app = FastAPI(lifespan=lifespan)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/telegram/webhook")
    async def telegram_webhook(request: Request) -> Response:
        logger.debug("Received Telegram webhook request")

        data = await request.json()

        update = Update.de_json(
            data=data,
            bot=telegram_app.bot,
        )

        await telegram_app.update_queue.put(update)

        logger.debug("Telegram webhook request processed successfully")

        return Response(status_code=200)

    return app
