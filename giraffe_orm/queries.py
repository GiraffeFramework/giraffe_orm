from .connections import query_one, change_db
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
    
    # TODO: FIX
    def create(self, **kwargs: dict[str, t.Any]) -> T:
        fields = ', '.join(kwargs.keys())
        placeholders = ', '.join('?' for _ in kwargs)
        values = tuple(kwargs.values())

        last_id = change_db(
            f"INSERT INTO {self.model()._get_tablename()} ({fields}) VALUES ({placeholders})",
            values
        )

        if not last_id:
            raise ValueError("Failed to create new entry")

        print("TODO: fix", last_id)
        row = query_one(f"SELECT * FROM {self.model()._get_tablename()} WHERE rowid = ?", (last_id,))
        return self.model._from_db(row)

    @t.overload
    def latest(self) -> T | None: ...
    @t.overload
    def latest(self, date_field: str) -> T | None: ...
    @t.overload
    def latest(self, date_field: Field[datetime]) -> T | None: ...
    def latest(self, date_field: str | Field[datetime] | None = None) -> T | None:
        """
        Get last table row based on Date fields. If no explicit field provided
        the first field of type Date will be used. Takes in a Field[datetime] 
        (or) string.
        """

        # Overwrite cache with explicit lookups for override 1 (field by str),
        # override 2 (field by Field[datetime]) and lastly (if no cache value 
        # is known) by finding the first field of type Date of the model.

        if isinstance(date_field, str):
            self.__date_field_cache = getattr(self.model, date_field, None)

        # Internally Field[datetime] does not exist and will always be a Date field
        elif isinstance(date_field, Date):
            self.__date_field_cache = date_field

        elif not self.__date_field_cache:
            print(self.model._fields)
            try:
                self.__date_field_cache = next(self.model._fields_of_type(Date))
            
            except StopIteration:
                raise ValueError("Could not find any date fields.")

        # If still no correct field is known, return an error.
        if not self.__date_field_cache:
            if not date_field:
                raise ValueError(f"Could not find any date fields.")
            
            raise ValueError(f"Date Field '{date_field}' not found on model.")
        
        field_name = self.__date_field_cache.get_name()
        query = f"SELECT * FROM {self.model()._get_tablename()} ORDER BY {field_name} DESC LIMIT 1;"        
        result = query_one(query)

        if result: return self.model._from_db(result)
        return None
