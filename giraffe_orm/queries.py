from .connections import query_all, query_one, change_db
from .fields import Field, Date, _Date

import typing as t


if t.TYPE_CHECKING:
    from .models import Model


T = t.TypeVar("T", bound='Model')
FD = t.TypeVar("FD", bound='Date')


class Query(t.Generic[T]):

    def __init__(self, model: t.Type[T]):
        self.model = model
        __date_field_cache: Date | None = None

    def create(self, body: dict, required_fields: list[Field]=[]) -> tuple[T | None, dict]:
        if not body:
            return None, {"status" : 400, "error" : "No body"}

        invalid_fields: list = []

        for field in required_fields:
            if not field.name in body:
                invalid_fields.append(field.name)

            value = body[field.name]
            valid, error = field.valid(value)

            if not valid:
                invalid_fields.append(f'{field.name} ({error})')

        if invalid_fields:
            return None, {"status" : 400, "error" : f"Invalid {', '.join(invalid_fields)}"}
        
        fields = ', '.join(body.keys())
        values = ', '.join(f"'{body[field]}'" for field in body.keys())

        last_id = change_db(f"INSERT INTO {self.model().get_tablename()} ({fields}) VALUES ({values})")

        if not last_id:
            return None, {"status": 500, "error": "Failed to create record"}
        
        new_record = query_one(f"SELECT * FROM {self.model().get_tablename()} WHERE id = {last_id}")

        return self.model.from_db(new_record), {}
    
    @t.overload
    def latest(self) -> T | None: ...
    @t.overload
    def latest(self, date_field: str) -> T | None: ...
    @t.overload
    def latest(self, date_field: Date) -> T | None: ...
    @t.overload
    def latest(self, date_field: Field[_Date]) -> T | None: ...
    def latest(self, date_field = None) -> T | None:

        if isinstance(date_field, str):
            self.__date_field_cache = getattr(self, date_field, None)

        elif isinstance(date_field, Date):
            self.__date_field_cache = date_field

        elif not self.__date_field_cache:
            self.__date_field_cache = next(self.model.fields_of_type(Date))

        if not self.__date_field_cache:
            if not date_field:
                raise ValueError(f"{self.model.get_tablename()}")
            raise ValueError(f"Invalid Date Field '{date_field}' provided for latest() query.")

        if not self.model().field_exists(field_name):
            raise ValueError(f"Cannot return by date field {field_name}")

        query = f"SELECT * FROM {self.model().get_tablename()} ORDER BY {field_name} DESC LIMIT 1;"        
        result = query_one(query)

        if result:
            return self.model.from_db(result)
        
        return None