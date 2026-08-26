# 🏀 BasketInfoBot

Telegram bot for following ACB basketball matches.

BasketInfoBot allows users to:

* Register through Telegram.
* Browse available ACB teams.
* Add and remove favorite teams.
* View upcoming matches involving their favorite teams.
* Receive match information including date, time, TV channels and scores.

The application automatically synchronizes ACB matches from the official ACB website and persists them in PostgreSQL.

🇬🇧 **English** | 🇪🇸 [Español](README.es.md)

## 🏗️ Architecture

The project follows a **Hexagonal Architecture / Ports and Adapters** approach, separating domain logic from infrastructure concerns.

```text
                         ┌──────────────────────┐
                         │      Telegram        │
                         └──────────┬───────────┘
                                    │
                              HTTPS Webhook
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       FastAPI        │
                         │      Webhook API     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ python-telegram-bot  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      Use Cases       │
                         └──────────┬───────────┘
                                    │
                       ┌────────────┴────────────┐
                       ▼                         ▼
              ┌─────────────────┐       ┌─────────────────┐
              │    PostgreSQL   │       │      ACB        │
              │    Supabase     │       │     Scraper     │
              └─────────────────┘       └────────┬─────────┘
                                                  │
                                            Playwright
                                                  │
                                                  ▼
                                             ACB Website
```

### Main components

#### Domain

Contains the business model and repository/fetcher ports.

```text
src/domain/
├── id_generator.py
├── match_fetcher.py
├── match_repository.py
├── match.py
├── team_repository.py+
├── team.py
├── user_repository.py
└── user.py
```

The domain does not depend on PostgreSQL, Telegram, FastAPI or Playwright.

#### Application

Contains the use cases that orchestrate the business logic.

```text
src/application/
├── add_favorite_team_by_telegram_id_use_case.py
├── get_available_teams_use_case.py
├── get_favorite_teams_by_telegram_id_use_case.py
├── get_upcoming_matches_by_telegram_id_use_case.py
├── register_user_use_case.py
├── remove_favorite_team_by_telegram_id_use_case.py
└── sync_upcoming_matches_use_case.py
```

#### Infrastructure

Adapters for external systems.

```text
src/infrastructure/
├── in_/
│   ├── cli/
│   └── telegram_bot/
│       ├── bot.py
│       ├── handlers.py
│       └── webhook.py
│
└── out/
    ├── persistence/
    │   ├── postgres_match_persistence.py
    │   ├── postgres_team_persistence.py
    │   └── postgres_user_persistence.py
    │
    └── scrapers/
        └── acb_scraper.py
```

## 🤖 Telegram Bot

The bot uses `python-telegram-bot` with **webhooks** instead of polling.

Telegram sends updates to:

```text
POST /telegram/webhook
```

FastAPI receives the update and places it into the `python-telegram-bot` update queue.

The application supports commands such as:

```text
/start
/favorito
/quitarfavorito
/partidos
```

Interactive favorite-team selection and removal are handled through Telegram buttons and callback queries.

## 🕷️ ACB Scraper

The ACB scraper uses:

* Playwright for browser automation and JavaScript-rendered content.
* BeautifulSoup for HTML parsing.

The scraper:

1. Opens the ACB results page using Playwright.
2. Waits for match elements to be rendered.
3. Waits for dynamically loaded match times.
4. Retrieves the rendered HTML.
5. Parses match dates, teams, times, TV channels and scores.
6. Converts the information into `SyncMatchCommand` objects.

The scraper can currently retrieve the complete available ACB calendar and process hundreds of matches.

## 🔄 Match Synchronization

Match synchronization is handled by:

```text
SyncUpcomingMatchesUseCase
```

The process is:

```text
ACB Scraper
     │
     ▼
SyncMatchCommand[]
     │
     ▼
Load all teams once
     │
     ▼
Resolve team names → Team entities
     │
     ▼
Create Match entities
     │
     ▼
PostgresMatchPersistence.save_all()
```

The persistence layer uses a single PostgreSQL connection for the complete batch instead of opening a new connection for every match.

This significantly improves synchronization performance.

## 🗄️ Persistence

PostgreSQL is used as the persistence layer through Supabase.

The main repositories are:

```text
PostgresUserPersistence
PostgresTeamPersistence
PostgresMatchPersistence
```

`PostgresMatchPersistence.save_all()` performs batch synchronization using a single database connection.

Match TV channels are stored separately in:

```text
match_channels
```

and users' favorite teams are associated through:

```text
user_favorite_teams
```

with the relationship:

```text
users
  │
  └── user_favorite_teams
           │
           └── teams
```

Database schema changes are managed using **Alembic**.

## ☁️ Deployment

The application is deployed as a Render Web Service.

The production architecture is:

```text
Telegram
   │
   ▼
Render
   │
   ├── FastAPI
   └── python-telegram-bot
          │
          ▼
       Supabase
```

Render runs the application using:

```bash
uv run python -m src.main
```

The application listens on the port provided by Render through the `PORT` environment variable.

A health endpoint is available at:

```text
GET /health
```

which returns:

```json
{
  "status": "ok"
}
```

## ⚙️ Configuration

Configuration is provided through environment variables.

Required variables:

```env
DATABASE_URL=
TELEGRAM_BOT_TOKEN=
ACB_TARGET_URL=
WEBHOOK_URL=
```

`WEBHOOK_URL` contains the public URL of the deployed application:

```env
WEBHOOK_URL=https://your-app.onrender.com
```

The Telegram webhook endpoint is automatically generated:

```text
https://your-app.onrender.com/telegram/webhook
```

The webhook is automatically registered when the application starts.

## ⏰ Match Synchronization

The match synchronization process runs independently from the Telegram web application.

GitHub Actions is used to periodically synchronize upcoming ACB matches.

The workflow can also be triggered manually.

The process is:

```text
GitHub Actions
      │
      ▼
ACB Scraper
      │
      ▼
SyncUpcomingMatchesUseCase
      │
      ▼
PostgresMatchPersistence.save_all()
      │
      ▼
Supabase PostgreSQL
```

The workflow uses `uv` to install dependencies and execute the synchronization command.

## 🧪 Testing

The project contains unit and integration tests.

Main testing tools include:

* `pytest`
* `pytest-asyncio`
* `pytest-mock`
* `testcontainers`
* PostgreSQL

Persistence integration tests run against PostgreSQL and verify operations such as:

* Saving matches.
* Updating existing matches.
* Finding matches by ID.
* Finding upcoming matches for a user.
* Handling missing matches.

The scraper also has tests using representative ACB HTML fixtures to verify:

* Match dates.
* Teams.
* Start times.
* TV channels.
* Scores.
* Match status.

## 🛠️ Development

The project uses [`uv`](https://docs.astral.sh/uv/) for Python dependency and environment management.

Install dependencies:

```bash
uv sync
```

Run tests:

```bash
uv run pytest
```

Run the Telegram bot locally:

```bash
uv run python -m src.main
```

Run match synchronization manually:

```bash
uv run python -m src.infrastructure.in.cli.sync_matches
```

Run Alembic migrations:

```bash
uv run alembic upgrade head
```

## 📦 Dependencies

Main dependencies:

* Python 3.11+
* FastAPI
* Uvicorn
* python-telegram-bot
* Playwright
* BeautifulSoup
* psycopg2
* Alembic
* PostgreSQL / Supabase

Development dependencies include:

* pytest
* pytest-asyncio
* pytest-mock
* testcontainers
* mypy
* ruff

## 💡 About the project

This project was created **for fun and as a personal learning project**.

If you find it useful, feel free to use it, modify it, reuse it, or take any part of the code for your own projects.

Make whatever you want with it! 🚀


## 🚀 MVP Status

The MVP is currently operational.

The complete production flow has been validated:

```text
ACB
 │
 │ Playwright
 ▼
Scraper
 │
 ▼
SyncMatchesUseCase
 │
 ▼
Supabase PostgreSQL
 │
 │
 ▼
Telegram Bot
 │
 │ Webhook
 ▼
FastAPI / Render
 │
 ▼
Users
```

The bot can currently retrieve real ACB match data, persist it efficiently, and serve it to Telegram users through a production webhook.
