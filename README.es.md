# 🏀 BasketInfoBot

Bot de Telegram para seguir los partidos de baloncesto de la ACB.

BasketInfoBot permite a los usuarios:

* Registrarse a través de Telegram.
* Consultar los equipos ACB disponibles.
* Añadir y eliminar equipos favoritos.
* Consultar los próximos partidos de sus equipos favoritos.
* Recibir información de los partidos, incluyendo fecha, hora, canales de televisión y resultados.

La aplicación sincroniza automáticamente los partidos de la ACB desde la web oficial de la ACB y los persiste en PostgreSQL.

🇪🇸 **Español** | 🇬🇧 [English](README.md)

## 🏗️ Arquitectura

El proyecto sigue un enfoque de **Arquitectura Hexagonal / Ports and Adapters**, separando la lógica de dominio de las dependencias de infraestructura.

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

### Componentes principales

#### Domain

Contiene el modelo de negocio y los puertos de repositorios y obtención de partidos.

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

El dominio no depende de PostgreSQL, Telegram, FastAPI ni Playwright.

#### Application

Contiene los casos de uso que orquestan la lógica de negocio.

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

Adaptadores para sistemas externos.

```text
src/infrastructure/
├── in_/
│   ├── cli/
│   └── telegram_bot/
│       ├── bot.py
│       ├── remove_favorite_teams_handler.py
│       ├── select_favorite_teams_handler.py
│       ├── start_handler.py
│       ├── upcoming_matches_for_user_handler.py
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

El bot utiliza `python-telegram-bot` con **webhooks** en lugar de polling.

Telegram envía las actualizaciones a:

```text
POST /telegram/webhook
```

FastAPI recibe la actualización y la introduce en la cola de actualizaciones de `python-telegram-bot`.

La aplicación soporta comandos como:

```text
/start
/favorito
/quitarfavorito
/partidos
```

La selección y eliminación de equipos favoritos se realiza mediante botones interactivos de Telegram y callback queries.

## 🕷️ ACB Scraper

El scraper de la ACB utiliza:

* Playwright para automatización del navegador y contenido renderizado mediante JavaScript.
* BeautifulSoup para analizar el HTML.

El scraper:

1. Abre la página de resultados de la ACB mediante Playwright.
2. Espera a que se rendericen los elementos de los partidos.
3. Espera a que se carguen dinámicamente los horarios.
4. Obtiene el HTML renderizado.
5. Analiza fechas, equipos, horarios, canales de televisión y resultados.
6. Convierte la información en objetos `SyncMatchCommand`.

Actualmente el scraper puede recuperar todo el calendario ACB disponible y procesar cientos de partidos.

## 🔄 Sincronización de partidos

La sincronización de partidos se realiza mediante:

```text
SyncUpcomingMatchesUseCase
```

El proceso es:

```text
ACB Scraper
     │
     ▼
SyncMatchCommand[]
     │
     ▼
Cargar todos los equipos una vez
     │
     ▼
Resolver nombres de equipo → Team entities
     │
     ▼
Crear Match entities
     │
     ▼
PostgresMatchPersistence.save_all()
```

La capa de persistencia utiliza una única conexión PostgreSQL para todo el lote en lugar de abrir una conexión por cada partido.

Esto mejora considerablemente el rendimiento de la sincronización.

## 🗄️ Persistencia

PostgreSQL se utiliza como capa de persistencia mediante Supabase.

Los principales repositorios son:

```text
PostgresUserPersistence
PostgresTeamPersistence
PostgresMatchPersistence
```

`PostgresMatchPersistence.save_all()` realiza la sincronización por lotes utilizando una única conexión a la base de datos.

Los canales de televisión de los partidos se almacenan separadamente en:

```text
match_channels
```

y los equipos favoritos de los usuarios se relacionan mediante:

```text
user_favorite_teams
```

con la relación:

```text
users
  │
  └── user_favorite_teams
           │
           └── teams
```

Los cambios en el esquema de la base de datos se gestionan mediante **Alembic**.

## ☁️ Despliegue

La aplicación está desplegada como un Web Service en Render.

La arquitectura de producción es:

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

Render ejecuta la aplicación mediante:

```bash
uv run python -m src.main
```

La aplicación escucha en el puerto proporcionado por Render mediante la variable de entorno `PORT`.

Existe un endpoint de health check:

```text
GET /health
```

que devuelve:

```json
{
  "status": "ok"
}
```

## ⚙️ Configuración

La configuración se proporciona mediante variables de entorno.

Variables requeridas:

```env
DATABASE_URL=
TELEGRAM_BOT_TOKEN=
ACB_TARGET_URL=
WEBHOOK_URL=
```

`WEBHOOK_URL` contiene la URL pública de la aplicación desplegada:

```env
WEBHOOK_URL=https://your-app.onrender.com
```

El endpoint del webhook de Telegram se genera automáticamente:

```text
https://your-app.onrender.com/telegram/webhook
```

El webhook se registra automáticamente cuando se inicia la aplicación.

## ⏰ Sincronización de partidos

El proceso de sincronización de partidos se ejecuta independientemente de la aplicación web de Telegram.

GitHub Actions se utiliza para sincronizar periódicamente los próximos partidos de la ACB.

El workflow también puede ejecutarse manualmente.

El proceso es:

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

El workflow utiliza `uv` para instalar las dependencias y ejecutar el comando de sincronización.

## 🧪 Tests

El proyecto contiene tests unitarios y de integración.

Las principales herramientas utilizadas son:

* `pytest`
* `pytest-asyncio`
* `pytest-mock`
* `testcontainers`
* PostgreSQL

Los tests de integración de persistencia utilizan PostgreSQL y verifican operaciones como:

* Guardar partidos.
* Actualizar partidos existentes.
* Buscar partidos por ID.
* Buscar próximos partidos para un usuario.
* Gestionar partidos inexistentes.

El scraper también dispone de tests utilizando fixtures HTML representativos de la ACB para verificar:

* Fechas.
* Equipos.
* Horarios.
* Canales de televisión.
* Resultados.
* Estado de los partidos.

## 🛠️ Desarrollo

El proyecto utiliza [`uv`](https://docs.astral.sh/uv/) para la gestión de dependencias y entornos Python.

Instalar dependencias:

```bash
uv sync
```

Ejecutar tests:

```bash
uv run pytest
```

Ejecutar el bot de Telegram localmente:

```bash
uv run python -m src.main
```

Ejecutar manualmente la sincronización de partidos:

```bash
uv run python -m src.infrastructure.in.cli.sync_matches
```

Ejecutar migraciones de Alembic:

```bash
uv run alembic upgrade head
```

## 📦 Dependencias

Dependencias principales:

* Python 3.11+
* FastAPI
* Uvicorn
* python-telegram-bot
* Playwright
* BeautifulSoup
* psycopg2
* Alembic
* PostgreSQL / Supabase

Dependencias de desarrollo:

* pytest
* pytest-asyncio
* pytest-mock
* testcontainers
* mypy
* ruff

## 💡 Sobre el proyecto

Este proyecto ha sido creado **por diversión y como proyecto personal de aprendizaje**.

Si te resulta útil, siéntete libre de usarlo, modificarlo, reutilizarlo o tomar cualquier parte del código para tus propios proyectos.

¡Haz con él lo que quieras! 🚀


## 🚀 Estado del MVP

El MVP está actualmente operativo.

El flujo completo de producción ha sido validado:

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
Usuarios
```

El bot actualmente puede obtener datos reales de partidos de la ACB, almacenarlos eficientemente y servirlos a usuarios de Telegram mediante un webhook de producción.
