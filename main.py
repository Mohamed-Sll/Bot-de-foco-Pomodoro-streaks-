"""main.py — Entry point: FastAPI app, webhook, health check, startup/shutdown."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from telegram import Update

from bot import build_application
from config import settings
from database.connection import close_all_connections
from database.migrations import run_migrations
from services.sweep_service import start_sweep_loop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

telegram_app = build_application()
sweep_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global sweep_task

    run_migrations()

    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(
        url=f"{settings.webhook_url}/webhook/telegram/{settings.webhook_secret}"
    )
    await telegram_app.start()

    sweep_task = asyncio.create_task(start_sweep_loop(telegram_app.bot))
    logger.info("Bot arrancado, sweep loop a correr")

    yield

    if sweep_task:
        sweep_task.cancel()

    await telegram_app.bot.delete_webhook()
    await telegram_app.stop()
    await telegram_app.shutdown()
    close_all_connections()
    logger.info("Bot desligado")


app = FastAPI(lifespan=lifespan)


@app.post("/webhook/telegram/{secret}")
async def telegram_webhook(secret: str, request: Request):
    if secret != settings.webhook_secret:
        raise HTTPException(status_code=403, detail="Forbidden")

    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}


@app.get("/health")
async def health():
    return {"status": "ok"}