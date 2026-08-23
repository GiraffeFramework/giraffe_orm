from giraffe_orm.connections import query_one, change_db, query_all
from giraffe_orm.fields import Field, Date_, datetime, Clause

from enum import Enum

import typing as t


if t.TYPE_CHECKING:
    from giraffe_orm.models import Model


MT = t.TypeVar("MT", bound='Model')
RT = t.TypeVar("RT")

T1 = t.TypeVar("T1")
T2 = t.TypeVar("T2")
T3 = t.TypeVar("T3")
T4 = t.TypeVar("T4")
T5 = t.TypeVar("T5")
T6 = t.TypeVar("T6")
T7 = t.TypeVar("T7")
T8 = t.TypeVar("T8")
T9 = t.TypeVar("T9")
T10 = t.TypeVar("T10")


class QueryMode(Enum):
    MODEL = 0
    ROWS = 1


class Query(t.Generic[MT, RT]):

    def __init__(self, model: t.Type[MT]):
        self.model = model

        self._mode = QueryMode.MODEL

        self.__offset = -1
        self.__limit = -1
        self.__selected_fields: tuple[Field[t.Any], ...] | None = None
        self.__date_field_cache: Date_ | None = None


    def _build_select(self) -> str:
        """
        Generates a stringified format of what should be in the SELECT 
        statement of the database query.
        """
        if not self.__selected_fields: 
            return ", ".join(self.model._get_column_names())
        
        select = ""
        for field in self.__selected_fields:
            select += field._select() + ", "
        
        # Remove the trailing ", " which is unused at the end
        return select[:-2]
    

    def _build_where(self) -> str:
        """
        Generates a stringified format of what should be in the WHERE part of
        the database query.
        """

        return ""
    

    def _query_one(self, query: str) -> RT | None:
        result = query_one(query)

        if not result: return None
        
        # Check whether the query is returning a model or plain row data
        if self._mode == QueryMode.MODEL:
            instance = self.model._from_db(result)
            return t.cast(RT, instance)

        return t.cast(RT, result) 
    

    def _query_all(self, query: str) -> list[RT]:
        results = query_all(query)

        if not results: return []
        
        # Check whether the query is returning a model or plain row data
        if self._mode == QueryMode.MODEL:
            instances = [self.model._from_db(result) for result in results]
            return t.cast(list[RT], instances)

        return t.cast(list[RT], results) 
    
    
    # TODO: TEMPORARY FIELD:
    def create(self, **kwargs: t.Any) -> MT:
        fields = ', '.join(kwargs.keys())
        placeholders = ', '.join('?' for _ in kwargs)
        values = tuple(kwargs.values())

        last_id = change_db(
            f"INSERT INTO {self.model._cls_tablename()} ({fields}) VALUES ({placeholders})",
            values
        )

        if not last_id:
            raise ValueError("Failed to create new entry")

        print("\tTODO: fix", last_id)
        row = query_one(f"SELECT * FROM {self.model._cls_tablename()} WHERE rowid = ?", (last_id,))
        return self.model._from_db(row)
    

    # --- Output modifiers ---


    def where(self) -> t.Self:
        """
        Applies the provided conditions to the WHERE clause of the query.
        """
        return self


    def limit(self, limit: int = 0) -> t.Self:
        """
        Applies a limit to this query.
        """
        if limit < 0: raise ValueError(f"Invalid offset {limit}, must be greater than 0")

        self.__limit = limit
        return self


    def load(self, *fields: Field[t.Any]) -> t.Self:
        """
        This query will return (an) instance(s) of this Model with only the 
        provided fields loaded from the database.
        """
        self._mode = QueryMode.MODEL
        self.__selected_fields = fields

        return self
    

    def offset(self, offset: int = 0) -> t.Self:
        """
        Applies an offset to this query.
        """
        if offset < 0: raise ValueError(f"Invalid offset {offset}, must be greater than 0")

        self.__offset = offset
        return self


    # fmt: off
    @t.overload
    def select(self, __f1: Field[T1]) -> "Query[MT, tuple[T1]]": ...
    @t.overload
    def select(self, __f1: Field[T1], __f2: Field[T2]) -> "Query[MT, tuple[T1, T2]]": ...
    @t.overload
    def select(self, __f1: Field[T1], __f2: Field[T2], __f3: Field[T3]) -> "Query[MT, tuple[T1, T2, T3]]": ...
    @t.overload
    def select(self, __f1: Field[T1], __f2: Field[T2], __f3: Field[T3], __f4: Field[T4]) -> "Query[MT, tuple[T1, T2, T3, T4]]": ...
    @t.overload
    def select(self, __f1: Field[T1], __f2: Field[T2], __f3: Field[T3], __f4: Field[T4], __f5: Field[T5]) -> "Query[MT, tuple[T1, T2, T3, T4, T5]]": ...
    @t.overload
    def select(self, __f1: Field[T1], __f2: Field[T2], __f3: Field[T3], __f4: Field[T4], __f5: Field[T5], __f6: Field[T6]) -> "Query[MT, tuple[T1, T2, T3, T4, T5, T6]]": ...
    @t.overload
    def select(self, __f1: Field[T1], __f2: Field[T2], __f3: Field[T3], __f4: Field[T4], __f5: Field[T5], __f6: Field[T6], __f7: Field[T7]) -> "Query[MT, tuple[T1, T2, T3, T4, T5, T6, T7]]": ...
    @t.overload
    def select(self, __f1: Field[T1], __f2: Field[T2], __f3: Field[T3], __f4: Field[T4], __f5: Field[T5], __f6: Field[T6], __f7: Field[T7], __f8: Field[T8]) -> "Query[MT, tuple[T1, T2, T3, T4, T5, T6, T7, T8]]": ...
    @t.overload
    def select(self, __f1: Field[T1], __f2: Field[T2], __f3: Field[T3], __f4: Field[T4], __f5: Field[T5], __f6: Field[T6], __f7: Field[T7], __f8: Field[T8], __f9: Field[T9]) -> "Query[MT, tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9]]": ...
    @t.overload
    def select(self, __f1: Field[T1], __f2: Field[T2], __f3: Field[T3], __f4: Field[T4], __f5: Field[T5], __f6: Field[T6], __f7: Field[T7], __f8: Field[T8], __f9: Field[T9], __f10: Field[T10]) -> "Query[MT, tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10]]": ...
    @t.overload
    def select(self, *fields: Field[t.Any]) -> "Query[MT, tuple[t.Any, ...]]": ...
    # fmt: on
    def select(self, *fields: Field[t.Any]) -> "Query[MT, t.Any]":
        """
        This query will return (a) tuple(s) with only the provided fields 
        loaded from the database.
        """
        self._mode = QueryMode.ROWS
        self.__selected_fields = fields

        new_query = t.cast(t.Any, self)
        return new_query
    

    # --- Terminal methods ---

    def all(self) -> list[RT]:
        """
        Get all elements satisfying the query.
        """

        where = self._build_where()

        query = \
        f"""
        SELECT {self._build_select()}
        FROM {self.model._cls_tablename()}
        {"WHERE " + where if where else ""}
        """

        if self.__limit > -1:
            query += f"LIMIT {self.__limit}"

        if self.__offset > -1:
            query += f" OFFSET {self.__offset}"
        
        return self._query_all(query)


    def assure(self) -> RT | None:
        """
        Retunrs the first element that satisfies the query. Will raise an error
        if this is None.
        """

        where = self._build_where()

        query = \
        f"""
        SELECT {self._build_select()}
        FROM {self.model._cls_tablename()}
        {"WHERE " + where if where else ""}
        LIMIT 1;
        """

        if result := self._query_one(query):
            return result

        # TODO: custom errors?
        raise ValueError("Expected not None value, got None")


    def first(self) -> RT | None:
        """
        Get the first element (or None) satisfying the query.
        """

        where = self._build_where()

        query = \
        f"""
        SELECT {self._build_select()}
        FROM {self.model._cls_tablename()}
        {"WHERE " + where if where else ""}
        LIMIT 1;
        """

        return self._query_one(query)

    @t.overload
    def latest(self) -> RT | None: ...
    @t.overload
    def latest(self, date_field: str) -> RT | None: ...
    @t.overload
    def latest(self, date_field: Field[datetime]) -> RT | None: ...
    def latest(self, date_field: str | Field[datetime] | None = None) -> RT | None:
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
        elif isinstance(date_field, Date_):
            self.__date_field_cache = date_field

        elif not self.__date_field_cache:
            try:
                self.__date_field_cache = next(self.model._fields_of_type(Date_))
            
            except StopIteration:
                raise ValueError("Could not find any date fields.")

        # If still no correct field is known, return an error.
        if not self.__date_field_cache:
            if not date_field:
                raise ValueError(f"Could not find any date fields.")
            
            raise ValueError(f"Date Field '{date_field}' not found on model.")
        
        field_name = self.__date_field_cache.get_name()
        where = self._build_where()

        query = \
        f"""
        SELECT {self._build_select()}
        FROM {self.model._cls_tablename()}
        {"WHERE " + where if where else ""}
        ORDER BY {field_name} DESC
        LIMIT 1;
        """

        return self._query_one(query)


    def update(self, changes: dict[Field[t.Any], t.Any]) -> None:
        """
        Will update the provided fields with the provided values for all 
        selected fields.
        """

        fields: str = ""
        values: list[t.Any] = []

        for field, value in changes.items():
            if not isinstance(value, dict):
                fields += field.get_name() + " = ?, "
                values.append(value)
                continue

            value = t.cast(Clause, value)

            fields += f"{field.get_name()} = {value['lhs']} ?, "
            values.append(value["rhs"])

        where = self._build_where()
        query = \
        f"""
        UPDATE {self.model._cls_tablename()}
        SET {fields[:-2]}
        {"WHERE " + where if where else ""};
        """

        change_db(query, tuple(values))
