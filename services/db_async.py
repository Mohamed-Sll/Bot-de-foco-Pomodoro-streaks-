"""services/db_async.py — Offload de chamadas síncronas de BD para o event loop async."""

from __future__ import annotations

import asyncio
from functools import partial
from typing import Any, Callable, TypeVar

T = TypeVar("T")


async def run_in_thread(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """
    Executa uma função síncrona (ex: qualquer função de database/) numa
    thread separada, sem bloquear o event loop do bot.
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(func, *args, **kwargs))