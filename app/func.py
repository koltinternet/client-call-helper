
# from aiohttp import MultipartReader
from aiohttp.web import Response, Request
from datetime import datetime

from aiopath import AsyncPath
from msgspec import json


from app.const import (
    SITE_LABEL,

    SRC_DIR,
    LOGS_DIR,
)


async def event_log_write(data: str, event_time: str) -> None:
    """ Записывает данные в лог, для каждого события.
    :param data: Данные для записи.
    :param event_time: Время события. Временная метка из "CHANNEL(linkedid)".
    """
    # ? "1729243964.366" -> "2024-10-18 12_32_44"
    name = (str(datetime.fromtimestamp(float(event_time))
             .replace(microsecond=0)).replace(":", "_"))

    file: AsyncPath = LOGS_DIR / name
    async with file.open("a", encoding="utf-8") as f:
        await f.write(data + "\n\n")


async def create_default_paths() -> None:
    """ Создает необходимые директории.
    """
    for p in (SRC_DIR, LOGS_DIR, ):
        await p.mkdir(parents=True, exist_ok=True)


async def default_context(request: Request) -> dict:
    now = datetime.now().replace(microsecond=0)
    return dict(
        date_now=now,
        site_label=SITE_LABEL,
    )


def simple_json_encoder(obj: any) -> str:
    """ Преобразует объекты Python в JSON-строку.
    """
    return json.encode(obj).decode("utf-8")


def simple_json_decoder(obj: str) -> any:
    """ Преобразует JSON-строку в объект Python.
    """
    return json.decode(obj)
