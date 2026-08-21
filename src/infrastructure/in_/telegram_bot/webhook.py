from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from telegram import Update
from telegram.ext import Application

from src.shared.infrastructure.config.settings import Settings


def create_webhook_app(
    telegram_app: Application,
    settings: Settings,
) -> FastAPI:
    webhook_url = f"{settings.webhook_url}/telegram/webhook"

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await telegram_app.initialize()

        await telegram_app.bot.set_webhook(
            url=webhook_url,
        )

        await telegram_app.start()

        print(f"Webhook de Telegram configurado: {webhook_url}")

        try:
            yield
        finally:
            await telegram_app.bot.delete_webhook()
            await telegram_app.stop()
            await telegram_app.shutdown()

    app = FastAPI(lifespan=lifespan)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/telegram/webhook")
    async def telegram_webhook(request: Request) -> Response:
        data = await request.json()

        update = Update.de_json(
            data=data,
            bot=telegram_app.bot,
        )

        await telegram_app.update_queue.put(update)

        return Response(status_code=200)

    return app
