from datetime import datetime

from aiojobs.aiohttp import spawn
import aiohttp_jinja2
from aiohttp.web import Request, Response, RouteTableDef, WebSocketResponse
# from aiohttp_session import get_session
from app.func import default_context, simple_json_encoder
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
    """ Возвращает основную страницу сайта.
    """

    ctx = await default_context(request)

    ctx.update(
        title=ctx["site_label"] + " — Официальный сайт.",
        is_index=True,
    )

    return ctx


async def call_hydra(call_session: CallSession) -> None:
    """ Выполняет запросы к Гидре.
    :param call_session: Событие сессии, которое будет
    обогащено данными из Гидры.
    """
    # ? Выполняем поиск пользователя по последним 10 символам
    # ? 921-123-45-67
    search_result = await HYDRA.search(call_session.phone[-10:])
    if search_entry := search_result.get_entry():

        customer_result = await HYDRA.get_customer(
            search_entry.user_second_id)

        customer = customer_result.get_entry()
        address_result = await HYDRA.get_addresses(
            customer.user_first_id)

        call_session.data = HydraData(
            login=search_entry.login,
            phone=search_entry.phone,
            profile_url=PROFILE_URL + str(search_entry.user_second_id),
            full_name=customer.full_name,
            short_name=customer.short_name,
            created_date=customer.created_date,
            firm_id=customer.firm_id,
            addresses=address_result.get_hydra_addresses()
        )

    await ACTIVE_SESSIONS.render()


@routes.post("/action")
async def action(request: Request) -> Response:
    """ Принимает json с описанием события и
    транслирует их в сокеты.
    """

    phone_message: PhoneMessage = await request.json(
        loads=action_decoder.decode
    )
    # pprint(phone_message)
    # print("=" * 10)

    match get_message_signature(phone_message):

        case "welcome":
            call_session = CallSession(
                phone=phone_message.caller_id_num,
                action="welcome",
                status="",
                time=datetime.fromtimestamp(
                    float(phone_message.event_time)),
                event_id=phone_message.linked_id,
                support_id=""
            )

            await ACTIVE_SESSIONS.add_session(call_session)

            await spawn(
                request=request,
                coro=call_hydra(call_session))

        case "calling":
            log.debug(f"Статус звонка: <green>{phone_message.caller_id_name}</>")
            await ACTIVE_SESSIONS.update_status_n_support_id(
                status=phone_message.caller_id_name,
                support_id=phone_message.caller_id_num,
                event_id=phone_message.linked_id)

        case "answered":
            await ACTIVE_SESSIONS.update_action(
                action="speak",
                event_id=phone_message.linked_id)

        case "done":
            await ACTIVE_SESSIONS.remove_session(
                event_id=phone_message.linked_id
            )

        # TODO:
        # case "missed":
        #     await ACTIVE_SESSIONS.remove_session(
        #         event_id=action.linked_id
        #     )

    return Response(text="ok", status=200)


def get_message_signature(phone_message: PhoneMessage) -> str | None:
    """ Вычисляет действие события.
    :param phone_message: Событие, пришедшее из телефонии.
    """
    # ? Пользователь дозвонился на ИВР.
    # ? В тональном режиме выбирает статус обращения.
    if phone_message.context == "ivr-welcome":
        return "welcome"

    if phone_message.context == "from-internal":
        # ? Пользователь определился со статусом обращения и
        # ? был переключен на дозвон в службу поддержки по
        # ? одному из соответствующих номеров.
        # ? Может быть получен ID телефонного аппарата, куда
        # ? был перенаправлен звонок, а так же статус обращения.
        if phone_message.event_type == "CHAN_START":
            return "calling"

        # ? Оператор взял трубку и отвечает на звонок.
        if phone_message.event_type == "ANSWER":
            return "answered"

        # ? Звонок завершен.
        if phone_message.event_type == "BRIDGE_EXIT":
            return "done"

        # TODO:
        # # ? Звонок пропущен.
        # if action.event_type == "BRIDGE_MISSED":
        #     return "missed"

    return None


@routes.get("/ws")
async def ws_loop(request: Request) -> WebSocketResponse:
    """ Создаёт и поддерживает потоковые соединения.
    """

    ws = WebSocketResponse()
    await ws.prepare(request)
    # log.debug(f"<red>{ws}-connected</>")

    # actions = [
    #     CallSession(
    #         phone="+79217809021",
    #         action="welcome",
    #         status="user",
    #         time=datetime.now(),
    #         event_id="1729243964.366",
    #         support_id="501",
    #     )
    # ]

    SOCKETS.append(ws)
    await ws.send_json(
        ACTIVE_SESSIONS.sessions,
        # actions,
        dumps=simple_json_encoder
    )

    async for msg in ws:
        # log.debug(f"<red>{ws}-message</>: {msg}")
        pass

    SOCKETS.remove(ws)
    # log.debug(f"<red>{ws}-disconnected</>")

    return ws
