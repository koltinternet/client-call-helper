
from aiohttp import MultipartReader
from aiohttp.web import Response, Request
from datetime import datetime

from aiopath import AsyncPath
from msgspec import json


from app.const import (
    SITE_LABEL,
    TOKEN_FILE,

    SRC_DIR,
    LOGS_DIR,
)


async def load_token() -> str:
    try:
        async with TOKEN_FILE.open("r", encoding="utf-8") as file:
            return await file.read()
    except FileNotFoundError:
        return ""


async def save_token(token: str) -> None:
    async with AsyncPath(TOKEN_FILE).open("w", encoding="utf-8") as file:
        await file.write(token)


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


def ok(**kwargs) -> Response:
    """ Собирает JSON сообщение об успешном выполнении запроса.
    """
    return Response(body=json.encode(dict(
        error=False,
        data=kwargs
    )), content_type="application/json")


def err(message: str, code: int = -1, **kwargs) -> Response:
    """ Собирает JSON сообщение об ошибке.
    """
    return Response(body=json.encode(dict(
        error=True,
        error_message=message,
        error_code=code,
        **kwargs
    )), content_type="application/json")
