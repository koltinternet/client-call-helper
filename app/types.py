from msgspec import Struct
from aiohttp import ClientSession, ClientResponseError, request, ClientTimeout
from app_config import HYDRA_USER, HYDRA_PASSWORD
from app.const import log, RE_AUTH_HYDRA_DELAY
from msgspec import json, field
from datetime import datetime


TIMEOUT = ClientTimeout(60)
API_URL = "https://h.kolt-internet.ru/rest/v2/"

class ActionMessage(Struct):
    id: int
    phone: str
    action: str
    status: str
    data: dict = {}


class HydraSearchEntry(Struct):
    # n_entity_id: int
    # vc_entity_role: str
    user_second_id: int = field(name="n_result_id")                # ? ID второй вкладки в Гидре
    login: str = field(name="vc_result_name")               # ? Логин
    phone: str = field(name="cl_highlighted_query_result")  # ? Номер телефона
    # vc_entity_type: str
    # vc_result_type: str
    # vc_result_subtype: str
    # vc_section: str


class HydraSearch(Struct):
    result: list[HydraSearchEntry] = field(name="search_results")

    def get_entry(self):
        return self.result[0]


class HydraCustomerEntry(Struct):
    # n_subject_id: int
    # n_customer_id: int
    user_first_id: int = field(name="n_base_subject_id")    # ? ID первой вкладки в Гидре
    full_name: str = field(name="vc_base_subject_name")     # ? ФИО полностью
    # n_base_subj_type_id: int
    # n_subj_state_id: int
    short_name: str = field(name="vc_name")                 # ? Фамилия И.О.
    login: str = field(name="vc_code")                      # ? Логин
    created_date: str = field(name="d_created")             # ? Дата создания
    # t_tags: list
    # vc_rem: str
    n_firm_id: int  # !
    # n_subj_group_id: int
    # n_reseller_id: int
    # group_ids: list
    # vc_base_subject_code: str
    # additional_values: list


class HydraCustomers(Struct):
    result: list[HydraCustomerEntry] = field(name="customers")

    def get_entry(self):
        return self.result[0]


class HydraAddressEntry(Struct):
    # n_address_id: int
    addr_type_id: int = field(name="n_addr_type_id")    # ? ID типа:
                                                        # ?     13006 - телефон
                                                        # ?     1006 - адрес проживания
    data: str = field(name="vc_visual_code")    # ? Данные
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
    title: str = field(name="vc_subj_addr_type_name")   # ? Наименование поля
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

    async def done(self) -> None:
        if not self.session.closed:
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

        if not self.auth_time or datetime.now() - self.auth_time > RE_AUTH_HYDRA_DELAY:
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
