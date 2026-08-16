# 🏀 BasketInfoBot

**BasketInfoBot** es un bot de Telegram diseñado para ofrecer información actualizada sobre partidos de baloncesto: horarios, canales de emisión de televisión y resultados de partidos finalizados.

El proyecto está desarrollado en **Python** aplicando **Domain-Driven Design (DDD)** y **Arquitectura Hexagonal (Puertos y Adaptadores)**, desacoplando completamente la lógica de negocio de la infraestructura de entrega y almacenamiento.

---

## 🏗️ Arquitectura del Proyecto

```text
src/
├── domain/            # Reglas de negocio (Entidades e Interfaces de Repositorios)
├── application/       # Casos de uso (Orquestación de lógica)
└── infrastructure/
    ├── in/            # Adaptadores de entrada (Telegram Bot)
    └── out/           # Adaptadores de salida (Web Scrapers, APIs, BD)