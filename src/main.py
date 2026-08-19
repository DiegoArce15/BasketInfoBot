from src.infrastructure.in_.telegram.bot import create_telegram_app

if __name__ == "__main__":
    app = create_telegram_app(...)
    app.run_polling()
