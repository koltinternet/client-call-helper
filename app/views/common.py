from datetime import datetime

from aiojobs.aiohttp import spawn
import aiohttp_jinja2
from aiohttp.web import Request, Response, RouteTableDef, WebSocketResponse
# from aiohttp_session import get_session
from app.func import default_context, simple_json_encoder, event_log_write
from app.const import log, SOCKETS, PROFILE_URL
from app.types import (
    PhoneMessage,
    HYDRA,
    ACTIVE_SESSIONS,
    CallSession,
    HydraData,
)
from msgspec import json
from pprint import pprint


routes = RouteTableDef()
action_decoder = json.Decoder(PhoneMessage)

__all__ = (
    "routes",
)
CONTEXT_NAMES = (
    "dial-to-accounting-department",
    "dial-to-specialist",
    "dial-to-artem",
    "nwh-artem",
    "fast-support",
    "from-internal"
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
            profile_url=PROFILE_URL + str(customer.user_first_id),
            full_name=customer.full_name,
            short_name=customer.short_name,
            created_date=customer.created_date,
            firm_id=customer.firm_id,
            addresses=address_result.get_hydra_addresses()
        )
    else:
        call_session.data = {}

    await ACTIVE_SESSIONS.render()


@routes.post("/action")
async def action(request: Request) -> Response:
    """ Принимает json с описанием события и
    транслирует их в сокеты.
    """
    raw_message = await request.text()
    phone_message = action_decoder.decode(raw_message)

    await event_log_write(raw_message, phone_message.linked_id)

    # phone_message: PhoneMessage = await request.json(
    #     loads=action_decoder.decode
    # )

    # await ACTIVE_SESSIONS.set_out_context(phone_message)

    pprint(phone_message)
    print("=" * 10)

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

            await event_log_write(
                "\n========== welcome ==========\n",
                phone_message.linked_id)

            await spawn(
                request=request,
                coro=call_hydra(call_session))

        case "calling":
            log.debug(f"Статус звонка: <green>{phone_message.caller_id_name}</>")
            await ACTIVE_SESSIONS.update_support_id(
                support_id=phone_message.caller_id_num,
                event_id=phone_message.linked_id)
            await event_log_write(
                "\n========== calling ==========\n",
                phone_message.linked_id)

        case "answered":
            await ACTIVE_SESSIONS.update_action(
                action="answered",
                event_id=phone_message.linked_id)

            await event_log_write(
                "\n========== answered ==========\n",
                phone_message.linked_id)

        case "statuses":
            await  ACTIVE_SESSIONS.update_status(
                status=phone_message.caller_id_name,
                event_id=phone_message.linked_id
            )
            log.debug(f"[- <red>{phone_message.linked_id}</> -] "
                      f"Статус для answered: <green>{phone_message.caller_id_name}</>")

        case "done":
            await ACTIVE_SESSIONS.remove_session(
                event_id=phone_message.linked_id
            )
            await event_log_write(
                "\n========== done ==========\n",
                phone_message.linked_id)

        case "missed":
            await ACTIVE_SESSIONS.remove_session(
                event_id=phone_message.linked_id
            )
            await event_log_write(
                "\n========== missed ==========\n",
                phone_message.linked_id)

    return Response(text="ok", status=200)


def get_message_signature(phone_message: PhoneMessage) -> str | None:
    """ Вычисляет действие события.
    :param phone_message: Событие, пришедшее из телефонии.
    """

    # ? Пользователь дозвонился на ИВР.
    # ? ivr-welcome|ivr-main
    # ? В тональном режиме выбирает статус обращения.
    ivr = phone_message.context.startswith("ivr-")
    # ? notice-and-dial-to-specialist
    notice = phone_message.context.startswith("notice-")
    if ivr or notice or phone_message.context == "incoming":
        match phone_message.event_type:
            case "ANSWER":
                return "welcome"

            case "HANGUP":
                log.debug(f"Звонок прерван с:\n\tcontext=<red>{phone_message.context}</>\n\t"
                          f"event_type=<red>{phone_message.event_type}</>")
                return "done"

    extra = {}
    if phone_message.event_extra:
        extra: dict[str, str | int] = json.decode(
            phone_message.event_extra)

    if phone_message.context in CONTEXT_NAMES:
        match phone_message.event_type:

            # ? Пользователь определился со статусом обращения и
            # ? был переключен на дозвон в службу поддержки по
            # ? одному из соответствующих номеров.
            # ? Может быть получен ID телефонного аппарата, куда
            # ? был перенаправлен звонок.
            case "CHAN_START":
                return "calling"

            # ? Oператор взял трубку и отвечает на звонок.
            case "ANSWER":
                return "answered"

            # ? Можно получить статус звонка.
            case "BRIDGE_ENTER":
                if phone_message.appname == "Queue":
                    return "statuses"

            # ? Звонок завершен.
            case "HANGUP":

                # ? Звонок переадресован на другой телефон.
                if extra.get("hangupcause", "-EMPTY-") in (17, ):
                    return None

                log.debug("Звонок завершен с:"
                          f"\n\tcontext=<red>{phone_message.context}</>\n\t"
                          f"event_type=<red>{phone_message.event_type}</>")
                return "done"

            case _:

                # ? Звонок пропущен. CANCEL|NOANSWER|BUSY
                if extra.get("dialstatus", "-EMPTY-") in (
                        "CANCEL", "NOANSWER", "BUSY"):
                    log.debug("Звонок пропущен с:"
                              f"\n\textra=<red>{extra}</>\n\t"
                              f"context=<red>{phone_message.context}</>\n\t"
                              f"event_type=<red>{phone_message.event_type}</>")
                    return "missed"

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
        message: dict = json.decode(msg)

    SOCKETS.remove(ws)
    # log.debug(f"<red>{ws}-disconnected</>")

    return ws
