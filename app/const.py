from aiopath import AsyncPath
from aiohttp.web import WebSocketResponse
from loguru import logger
from datetime import timedelta
import copy

log = logger.opt(colors=True)

ROOT_DIR = AsyncPath(__file__).parent.parent

STATIC_DIR = ROOT_DIR / "static"

LOGS_DIR = ROOT_DIR / "logs"

SRC_DIR = ROOT_DIR / "src"

DB_PATH = SRC_DIR / "Baza.db"

# ===========================================

PROFILE_URL = "https://h.kolt-internet.ru/subjects/persons/edit/"
""" Первая часть URL для перехода в профиль. """

RE_AUTH_HYDRA_DELAY = timedelta(hours=1)
""" Промежутки времени, по истечении которых необходимо
переподключиться к Hydra.
"""

SITE_LABEL = "Client Call Helper"

# ===========================================
SOCKETS: list[WebSocketResponse] = []
""" Список клиентских WS-соединений. """
# ===========================================
USE_POSTGRES = False                     # ! Использовать PostgreSQL
# ===========================================

TORTOISE_CONFIG = {
    "connections": {
        "default": {},
    },
    "apps": {
        "models": {
            "models": ["app.models"],
            "default_connection": "default",
        },
    },
    "use_tz": False,
    "timezone": "Europe/Moscow"
}

SQLITE_DB_ENV = {
    "engine": "tortoise.backends.sqlite",
    "credentials": {
        "file_path": DB_PATH
    }
}

PG_DB_ENV = {
    "engine": "tortoise.backends.asyncpg",
    "credentials": {
        "host": "127.0.0.1",
        "port": 5432,
        "user": "project_user",
        "password": "project_password",
        "database": "project_database",
    }
}

AERICH_CONFIG = copy.deepcopy(TORTOISE_CONFIG)

if USE_POSTGRES:
    TORTOISE_CONFIG["connections"]["default"].update(PG_DB_ENV)
    AERICH_CONFIG["connections"]["default"].update(PG_DB_ENV)
else:
    TORTOISE_CONFIG["connections"]["default"].update(SQLITE_DB_ENV)
    AERICH_CONFIG["connections"]["default"].update(SQLITE_DB_ENV)

AERICH_CONFIG["apps"]["models"]["models"] += ["aerich.models"]

# ==============================================================
