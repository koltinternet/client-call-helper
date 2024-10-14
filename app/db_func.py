from asyncio import sleep
from datetime import timedelta, date

from tortoise.functions import Min, Max, Count
from tortoise.queryset import QuerySet
from tortoise.timezone import localtime
from tortoise import connections, Model
# from tortoise.expressions import Q

# from .models import
from .const import log




async def prepare_db() -> None:
    """ Обеспечивает начальное состояние базы данных.
    """
    pass
