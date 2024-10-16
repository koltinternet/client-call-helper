from aiojobs.aiohttp import spawn
import aiohttp_jinja2
from aiohttp.web import Request, Response, RouteTableDef, WebSocketResponse
# from aiohttp_session import get_session
from app.func import default_context
from app.const import log, SOCKETS
from app.types import ActionMessage
from msgspec.json import Decoder

routes = RouteTableDef()
action_decoder = Decoder(ActionMessage)

__all__ = (
    "routes",
)


@routes.get("/")
@aiohttp_jinja2.template("index.html")
async def index(request: Request) -> dict:

    ctx = await default_context(request)

    ctx.update(
        title=ctx["site_label"] + " — Официальный сайт.",
        is_index=True,
    )

    return ctx


async def call_hydra(action: dict) -> None:
    """ Выполняет запросы к Гидре.
    """
    # TODO: Запрос к Гидре
    # TODO: Обновить событие данными ответа
    # TODO: Отправить событие в сокеты

    # action["action"] = "update"
    # for ws in SOCKETS:
    #     await ws.send_json(action)


@routes.post("/action")
async def action(request: Request) -> Response:
    """ Принимает json с описанием события и
    транслирует их в сокеты.
    """

    action: dict = await request.json(
        # loads=action_decoder.decode
    )
    log.info(f"Входящее событие: {action}")

    for ws in SOCKETS:
        await ws.send_json(action)

    if action.get("action") == "new":
        await spawn(request=request, coro=call_hydra(action))

    return Response(text="ok", status=200)


@routes.get("/ws")
async def ws_loop(request: Request) -> WebSocketResponse:
    """ Создаёт и поддерживает потоковые соединения.
    """

    ws = WebSocketResponse()
    await ws.prepare(request)
    # log.debug(f"<red>{ws}-connected</>")

    SOCKETS.append(ws)

    async for msg in ws:
        # log.debug(f"<red>{ws}-message</>: {msg}")
        pass

    SOCKETS.remove(ws)
    # log.debug(f"<red>{ws}-disconnected</>")

    return ws
