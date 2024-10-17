from aiopath import AsyncPath
from aiohttp.web import WebSocketResponse
from hashlib import md5
from loguru import logger
import copy

log = logger.opt(colors=True)

ROOT_DIR = AsyncPath(__file__).parent.parent

STATIC_DIR = ROOT_DIR / "static"

LOGS_DIR = ROOT_DIR / "logs"

SRC_DIR = ROOT_DIR / "src"

DB_PATH = SRC_DIR / "Baza.db"

TOKEN_FILE = SRC_DIR / "token_file"

# ===========================================

SECRET_PHRASE = md5("случайная строка для шифрования".encode("utf-8")).hexdigest()

SITE_LABEL = "Client Call Helper"

# ===========================================
SOCKETS: list[WebSocketResponse] = []
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
