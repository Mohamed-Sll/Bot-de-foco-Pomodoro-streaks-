from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


class ConfigError(Exception):
    pass


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ConfigError(f"Variavel de ambiente obrigatoria em falta: {name}")
    return value


def _optional(name: str, default: str) -> str:
    return os.getenv(name, default)


def _optional_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigError(f'{name} deve ser um numero inteiro, recebi: {raw!r}') from exc


@dataclass(frozen=True)
class Settings:
    bot_token: str
    webhook_url: str
    webhook_secret: str
    webhook_port: int

    # base de dados:
    database_url: str

    # comportamento do bot:
    default_timezone: str
    min_focus_minutes: int
    max_focus_minutes: int
    default_break_minutes: int
    sweep_interval_seconds: int

    # ambiente:
    environment: str

    @property
    def is_production(self) -> bool:
        return self.environment == 'production'


def load_settings() -> Settings:
    settings = Settings(
        bot_token=_require('BOT_TOKEN'),
        webhook_url=_require('WEBHOOK_URL'),
        webhook_secret=_require('WEBHOOK_SECRET'),
        webhook_port=_optional_int('WEBHOOK_PORT', 8080),
        database_url=_require('DATABASE_URL'),
        default_timezone=_optional('DEFAULT_TIMEZONE', 'Europe/Lisbon'),
        min_focus_minutes=_optional_int('MIN_FOCUS_MINUTES', 15),
        max_focus_minutes=_optional_int('MAX_FOCUS_MINUTES', 120),
        default_break_minutes=_optional_int('DEFAULT_BREAK_MINUTES', 5),
        sweep_interval_seconds=_optional_int('SWEEP_INTERVAL_SECONDS', 60),
        environment=_optional('ENVIRONMENT', 'development'),
    )
    if settings.min_focus_minutes > settings.max_focus_minutes:
        raise ConfigError(
            "MIN_FOCUS_MINUTES deve ser menor que MAX_FOCUS_MINUTES "
            f"(recebi min={settings.min_focus_minutes}, max={settings.max_focus_minutes})"
        )
    return settings


settings = load_settings()