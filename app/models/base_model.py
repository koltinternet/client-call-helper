from tortoise import fields
from tortoise.models import Model

__all__ = (
    "BaseModel",
)


class BaseModel(Model):
    class Meta:
        abstract = True

    id = fields.IntField(primary_key=True, db_index=True)

    async def as_dict(self) -> dict:
        """ Возвращает словарь с данными предметной области. """
        return dict(filter(
            lambda k: not k[0].startswith("_"),
            self.__dict__.items()))

    @classmethod
    def field_names(cls) -> list[str]:
        """ Возвращает список имен собственных полей
        без отношений.
        """
        return list(cls._meta.fields_db_projection.keys())

    @classmethod
    def field_names_all(cls) -> list[str]:
        """ Возвращает все имена полей, включая отношения. """
        return list(cls._meta.fields_map.keys())
