from .connections import query_all, query_one, change_db
from .fields import Field, Date, datetime

import typing as t


if t.TYPE_CHECKING:
    from .models import Model


T = t.TypeVar("T", bound='Model')
FD = t.TypeVar("FD", bound='Date')


class Query(t.Generic[T]):

    def __init__(self, model: t.Type[T]):
        self.model = model
        self.__date_field_cache: Date | None = None
    
    def create(self, *_, **kwargs) -> T:
        fields = ', '.join(kwargs.keys())
        placeholders = ', '.join('?' for _ in kwargs)
        values = tuple(kwargs.values())

        last_id = change_db(
            f"INSERT INTO {self.model().get_tablename()} ({fields}) VALUES ({placeholders})",
            values
        )

        if not last_id:
            raise ValueError("Failed to create new entry")

        row = query_one(f"SELECT * FROM {self.model().get_tablename()} WHERE id = ?", (last_id,))
        return self.model.from_db(row)

    @t.overload
    def latest(self) -> T | None: ...
    @t.overload
    def latest(self, date_field: str) -> T | None: ...
    @t.overload
    def latest(self, date_field: Date) -> T | None: ...
    @t.overload
    def latest(self, date_field: Field[datetime]) -> T | None: ...
    def latest(self, date_field = None) -> T | None:
        """
        Get last table row based on Date fields.
        """

        if isinstance(date_field, str):
            self.__date_field_cache = getattr(self, date_field, None)

        elif isinstance(date_field, Date):
            self.__date_field_cache = date_field

        elif not self.__date_field_cache:
            self.__date_field_cache = next(self.model.fields_of_type(Date))

        if not self.__date_field_cache:
            if not date_field:
                raise ValueError(f"{self.model().get_tablename()} does not have any date fields.")
            
            raise ValueError(f"Invalid Date Field '{date_field}' provided for latest() query.")
        
        field_name = self.__date_field_cache.get_name()

        if not self.model().field_exists(field_name):
            raise ValueError(f"Cannot return by date field {field_name}")

        query = f"SELECT * FROM {self.model().get_tablename()} ORDER BY {field_name} DESC LIMIT 1;"        
        result = query_one(query)

        if result:
            return self.model.from_db(result)
        
        return None
    
    def save(self) -> None:
        return