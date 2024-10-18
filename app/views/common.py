from datetime import datetime

from aiojobs.aiohttp import spawn
import aiohttp_jinja2
from aiohttp.web import Request, Response, RouteTableDef, WebSocketResponse
# from aiohttp_session import get_session
from app.func import default_context
from app.const import log, SOCKETS, PROFILE_URL
from app.types import (
    PhoneMessage,
    HYDRA,
    ACTIVE_SESSIONS,
    CallSession,
    HydraData,
)
from msgspec.json import Decoder
from pprint import pprint


routes = RouteTableDef()
action_decoder = Decoder(PhoneMessage)

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


async def call_hydra(session: CallSession) -> None:
    """ Выполняет запросы к Гидре.
    """
    # ? Помечаем событие как обновлённое из Гидры
    data = dict()

    search_result = await HYDRA.search(session.phone[-10:])
    if search_entry := search_result.get_entry():
        customer_result = await HYDRA.get_customer(
            search_entry.user_second_id)

        customer = customer_result.get_entry()
        address_result = await HYDRA.get_addresses(
            customer.user_first_id)

        data.update(
            login=search_entry.login,
            phone=search_entry.phone,
            profile_url=PROFILE_URL + str(search_entry.user_second_id),
            full_name=customer.full_name,
            short_name=customer.short_name,
            created_date=customer.created_date,
            firm_id=customer.firm_id,
            addresses=address_result.get_hydra_addresses()
        )

    session.action = "hydra"
    session.data = HydraData(**data)

    await ACTIVE_SESSIONS.render()


@routes.post("/action")
async def action(request: Request) -> Response:
    """ Принимает json с описанием события и
    транслирует их в сокеты.
    """

    action: PhoneMessage = await request.json(
        loads=action_decoder.decode
    )
    # log.info(f"Входящее событие: {action}")
    pprint(action)
    print("=" * 10)

    # for ws in SOCKETS:
    #     await ws.send_json(action)
    #

    if action.context == "ivr-welcome":
        # ? Получаем номер телефона начиная с девятки,
        # ? на случай конфликта между восьмёркой и семёркой

        call_session = CallSession(
            phone=action.caller_id_num,
            action="new",
            status="",
            time=datetime.fromtimestamp(float(action.event_time)),
            event_id=action.linked_id,
            support_id=""
        )

        await ACTIVE_SESSIONS.add_session(call_session)

        await spawn(
            request=request,
            coro=call_hydra(call_session)
        )

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
