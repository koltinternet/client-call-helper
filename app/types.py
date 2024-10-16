from msgspec import Struct


class ActionMessage(Struct):
    id: int
    phone: str
    action: str
    status: str
    data: dict = {}
