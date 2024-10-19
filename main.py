from aiohttp import web, ClientResponseError
from aiojobs.aiohttp import setup as setup_aiojobs
import jinja2
import aiohttp_jinja2
from aiohttp_session import session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import base64
from cryptography import fernet
from tortoise.contrib.aiohttp import register_tortoise

from app.db_func import prepare_db
from app.const import (
    log,
    TORTOISE_CONFIG,
)
from app.types import HYDRA

from app.func import (
    simple_json_encoder, simple_json_decoder,
    create_default_paths,)

from ehandlers import setup_error_handlers
from app_config import APP_PORT


async def on_startup(_: web.Application) -> None:
    """ Выполняется при запуске приложения.
    """
    await prepare_db()
    await create_default_paths()
    try:
        await HYDRA.make_auth()
    except ClientResponseError:
        log.error("Ошибка при инициализации Гидры")
        raise


async def on_shutdown(_: web.Application) -> None:
    """ Выполняется при выключении приложения.
    """
    await HYDRA.done()


def setup_routes(application: web.Application) -> None:
    """ Настраиваем пути для приложения. """
    from app.const import STATIC_DIR

    from app.views import setup_routes as setup

    setup(application)

    application.router.add_static(prefix="/", path=STATIC_DIR)


def setup_external_libraries(application: web.Application) -> None:
    """ Указываем шаблонизатору расположение шаблонов. """
    aiohttp_jinja2.setup(
        application,
        loader=jinja2.FileSystemLoader("templates"),
    )


def setup_app(application: web.Application) -> None:
    setup_external_libraries(application)
    setup_routes(application)
    setup_aiojobs(application)
    setup_error_handlers(application)

    application.on_startup.append(on_startup)
    application.on_shutdown.append(on_shutdown)


def create_app(testing: bool = False) -> web.Application:
    """ Создаем приложение.
    """

    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)

    session_mw = session_middleware(
        EncryptedCookieStorage(
            secret_key,
            cookie_name="FLAT_SESSION",
            encoder=simple_json_encoder,
            decoder=simple_json_decoder,
        )
    )

    application = web.Application(middlewares=[
        session_mw,
    ])

    # # ? Для тестирования используем тестовую базу на SQLite
    # if testing:
    #     TORTOISE_CONFIG["connections"]["default"] = SQLITE_DB_ENV

    # register_tortoise(application, config=TORTOISE_CONFIG, generate_schemas=True)

    setup_app(application)

    return application


if __name__ == "__main__":
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=APP_PORT)