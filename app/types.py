from msgspec import Struct
from aiohttp import ClientSession, ClientResponseError, request, ClientTimeout

from app_config import HYDRA_USER, HYDRA_PASSWORD
from app.const import log, RE_AUTH_HYDRA_DELAY, SOCKETS
from msgspec import json, field
from datetime import datetime


TIMEOUT = ClientTimeout(60)
API_URL = "https://h.kolt-internet.ru/rest/v2/"

class PhoneMessage(Struct):
    """ Описание события, полученного из телефонии.
    """

    bridge_peer: str = field(name="BRIDGEPEER")
    caller_id_name: str = field(name="CALLERID(name)")
    caller_id_num: str = field(name="CALLERID(num)")
    account_code: str = field(name="CHANNEL(accountcode)")
    ama_flags: str = field(name="CHANNEL(amaflags)")
    appdata: str = field(name="CHANNEL(appdata)")
    appname: str = field(name="CHANNEL(appname)")
    channel_name: str = field(name="CHANNEL(channame)")
    context: str = field(name="CHANNEL(context)")
    exten: str = field(name="CHANNEL(exten)")
    linked_id: str = field(name="CHANNEL(linkedid)")
    unique_id: str = field(name="CHANNEL(uniqueid)")
    user_field: str = field(name="CHANNEL(userfield)")
    event_extra: str = field(name="eventextra")
    event_time: str = field(name="eventtime")
    event_type: str = field(name="eventtype")
    user_def_type: str = field(name="userdeftype")


class HydraAddress(Struct):
    data: str
    """ Данные адреса/контакта """
    title: str
    """ Наименование """


class HydraData(Struct):
    login: str
    """ Логин """
    phone: str
    """ Номер телефона """
    profile_url: str
    """ URL профиля в Гидре """
    full_name: str
    """ Полное имя """
    short_name: str
    """ Фамилия И.О. """
    created_date: str
    """ Дата регистрации """
    firm_id: int = 0
    """ ?!? """
    addresses: list[HydraAddress] = []
    """ Список адресов/контактов """


class CallSession(Struct):
    phone: str
    """ Номер телефона """
    action: str
    """ Действие welcome|calling|answered|done|missed """
    status: str
    """ Статус user|forced|kvartira|chasny|... """
    time: datetime
    """ Время события """
    event_id: str
    """ ID события """
    support_id: str
    """ ID телефонного аппарата поддержки """
    data: HydraData | dict | None = None
    """ Данные об учётке из Гидры """


class ActiveCallSessions:
    sessions: list[CallSession] = []

    async def add_session(self, session: CallSession) -> None:
        """ Добавляет сессию в список сессий.
        :param session: Сессия.
        """
        self.sessions.insert(0, session)
        await self.render()

    async def remove_session(self, event_id: str) -> None:
        """ Удаляет сессию из списка сессий.
        :param event_id: ID удаляемого события.
        """
        for i, session in enumerate(self.sessions):
            if session.event_id == event_id:
                del self.sessions[i]
                await self.render()

    async def update_action(self, action: str, event_id: str) -> None:
        """ Обновляет действие в сессии.
        :param action: Действие new|speak|done.
        :param event_id: ID события.
        """
        for session in self.sessions:
            if session.event_id == event_id:
                session.action = action
                await self.render()

    async def update_status_n_support_id(
            self, status: str,
            support_id: str,
            event_id: str) -> None:
        """ Обновляет статус обращения и ID телефонного аппарата,
        на который был перенаправлен звонок.
        :param status: Статус user|forced|kvartira|chasny|...
        :param support_id: ID телефонного аппарата поддержки.
        :param event_id: ID события.
        """
        for session in self.sessions:
            if session.event_id == event_id:
                session.action = "calling"
                session.status = status
                session.support_id = support_id
                await self.render()

    async def render(self) -> None:
        """ Отправляет состояния сессий в сокеты. """
        data = (json.encode(self.sessions)
                .decode("utf-8"))

        for ws in SOCKETS:
            await ws.send_str(data)


class HydraSearchEntry(Struct):
    # n_entity_id: int
    # vc_entity_role: str
    user_second_id: int = field(name="n_result_id")
    """ ID второй вкладки в Гидре """
    login: str = field(name="vc_result_name")
    """ Логин """
    phone: str = field(name="cl_highlighted_query_result")
    """ Номер телефона """
    # vc_entity_type: str
    # vc_result_type: str
    # vc_result_subtype: str
    # vc_section: str


class HydraSearch(Struct):
    result: list[HydraSearchEntry] = field(name="search_results")

    def get_entry(self) -> HydraSearchEntry | None:
        return self.result[0] if self.result else None


class HydraCustomerEntry(Struct):
    # n_subject_id: int
    # n_customer_id: int
    user_first_id: int = field(name="n_base_subject_id")
    """ ID первой вкладки в Гидре """
    full_name: str = field(name="vc_base_subject_name")
    """ ФИО полностью """
    # n_base_subj_type_id: int
    # n_subj_state_id: int
    short_name: str = field(name="vc_name")
    """ Фамилия И.О. """
    login: str = field(name="vc_code")
    """ Логин """
    created_date: str = field(name="d_created")
    """ Дата создания учётки """
    # t_tags: list
    # vc_rem: str
    firm_id: int = field(name="n_firm_id")  # !
    """ ?!? """
    # n_subj_group_id: int
    # n_reseller_id: int
    # group_ids: list
    # vc_base_subject_code: str
    # additional_values: list


class HydraCustomers(Struct):
    result: list[HydraCustomerEntry] = field(name="customers")

    def get_entry(self) -> HydraCustomerEntry | None:
        return self.result[0] if self.result else None


class HydraAddressEntry(Struct):
    # n_address_id: int
    addr_type_id: int = field(name="n_addr_type_id")
    """ ID типа адреса:
        1006 - адрес проживания
        13006 - телефон
    """
    data: str = field(name="vc_visual_code")
    """ Данные адреса """
    # n_par_addr_id: int
    # vc_code: str
    # vc_address: str
    # vc_flat: str
    # n_region_id: int
    # vc_entrance_no: str
    # n_floor_no: int
    # n_firm_id: int
    # n_subj_address_id: int
    # n_subject_id: int
    # n_subj_addr_type_id: int
    # n_addr_state_id: int
    # vc_rem: str
    # n_bind_addr_id: int
    title: str = field(name="vc_subj_addr_type_name")
    """ Наименование типа адреса """
    # d_begin: str
    # d_end: str
    # c_fl_main: str


class HydraAddresses(Struct):
    result: list[HydraAddressEntry] = field(name="subject_addresses")

    def get_address(self) -> HydraAddressEntry | None:
        """ Возвращает строку с записью адреса проживания.
        """
        for addr in self.result:
            if addr.addr_type_id == 1006:
                return addr
        return None

    def get_addresses_as_src(self) -> list[dict]:
        """ Возвращает список словарей с адресами. """
        result = []
        for addr in self.result:
            result.append({
                "data": addr.data,
                "title": addr.title,
            })
        return result

    def get_hydra_addresses(self) -> list[HydraAddress]:
        """ Возвращает список упакованных данных. """
        return [
            HydraAddress(
                data=addr.data,
                title=addr.title,
            )
            for addr in self.result
        ]


class Hydra:
    session: ClientSession | None = None
    """ Сессия Гидры. """
    auth_time: datetime | None = None
    """ Время авторизации. """

    def __init__(self) -> None:
        self.executors: dict = {}

    async def make_auth(self) -> None:
        """ Выполняет авторизацию в Гидре,
        запоминая время.
        """
        await self.done()
        token = await self.get_auth_token()

        self.session = ClientSession(
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Token token={token}",
            }
        )

        self.executors = {
            "GET": self.session.get,    #type: ignore
            "POST": self.session.post,  #type: ignore
        }
        log.debug("Выполнена авторизация в Гидре")

    async def done(self) -> None:
        """ Необходимо выполнить при завершении работы!
        Закрывает сессию.
        """
        if self.session and not self.session.closed:
            await self.session.close()

    @classmethod
    async def get_auth_token(cls) -> str:
        auth_url = API_URL + "login"
        options = dict(
            json=dict(
            session=dict(
                login=HYDRA_USER,
                password=HYDRA_PASSWORD
                )
            ),
            timeout=TIMEOUT
        )
        try:
            async with request("POST", auth_url, **options) as response:
                response.raise_for_status()
                session = (await response.json())["session"]
                cls.auth_time = datetime.now()
                return session["token"]
        except ClientResponseError as e:
            log.error(f"Ошибка авторизации при получении токена у Гидры: {e}")
            raise

    async def hydra_request(
            self, url_path: str,
            params: dict,
            method: str = "GET") -> bytes:
        """ Выполняет запрос к Гидре, проверяя время
        авторизации и авторизует, если время сессии истекло."""

        if not self.auth_time or (
                datetime.now() - self.auth_time > RE_AUTH_HYDRA_DELAY):
            await self.make_auth()

        if not (executor := self.executors.get(method)):
            raise ValueError(f"Метод {method} не поддерживается")

        url_path = API_URL + url_path
        options: dict = {"params": params} if method == "GET" else {"json": params}
        options["timeout"] = TIMEOUT

        try:
            async with executor(url_path, **options) as response:    #type: ignore
                response.raise_for_status()
                return await response.read()
        except ClientResponseError as e:
            log.error(
                f"{url_path=} {params=} {method=}"
                f"Ошибка при запросе к Гидре: {e}"
            )
            raise

    async def search(self, phone: str) -> HydraSearch:
        result = await self.hydra_request(
            "search",
            {"result_subtype_id": "2001", "query": phone}
        )
        return json.decode(result, type=HydraSearch)

    async def get_customer(self, user_id: int) -> HydraCustomers:
        result = await self.hydra_request(
            "subjects/customers/batch",
            {"ids": [user_id]},
            "POST"
        )
        return json.decode(result, type=HydraCustomers)

    async def get_addresses(self, subject_id: int) -> HydraAddresses:
        result = await self.hydra_request(
            "subject_addresses",
            {"subject_id": [subject_id]}
        )
        return json.decode(result, type=HydraAddresses)


HYDRA = Hydra()
""" Глобальный объект Гидры. """

ACTIVE_SESSIONS = ActiveCallSessions()
""" Глобальный объект сессий. """
