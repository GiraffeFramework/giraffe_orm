from .connections import query_all
from .queries import Query
from .fields import Field

from typing_extensions import Self
import typing as t


T = t.TypeVar("T", bound='Model')
F = t.TypeVar("F", bound=Field)


class Model:
    query: Query[Self]
    _fields: list[Field] = []

    def __init__(self) -> None:
        self.__tablename__: str = ''

    def __init_subclass__(cls: t.Type[T], **kwargs):
        super().__init_subclass__(**kwargs)
        cls.query = Query(cls) # type: ignore
    
    def _valid_tablename(self, name: str) -> str:
        if len(name) > 128:
            raise ValueError("Table name cannot be longer than 128 characters")
        
        if not name.replace('_', '').isalnum():
            raise ValueError("Table name cannot contain non-alphanumeric characters")
        
        return name
    
    @classmethod
    def add_field(cls, field: Field) -> None:
        cls._fields.append(field)

    def field_exists(self, field: str) -> bool:
        return hasattr(self, field)
    
    def get_tablename(self) -> str:
        if self.field_exists('__tablename__') and self.__tablename__:
            return self._valid_tablename(self.__tablename__)
        
        return self._valid_tablename(self.__class__.__name__.lower())

    @classmethod
    def fields_of_type(cls, type: t.Type[F]) -> t.Generator[F, t.Any, t.Any]:
        for field in cls._fields:
            if isinstance(field, type):
                yield field

    @classmethod
    def _get_column_names(cls):
        names: list[str] = []

        for key, value in cls.__dict__.items():
            if not isinstance(value, Field):
                continue

            names.append(value.name)

        return names
    
    @classmethod
    def get_schema_changes(cls) -> dict | None:
        """Loop over existing schemas from the database and compare them to the current schema. Detects added, removed, modified, and renamed fields."""
        
        dropped_schemas: list[tuple] = []
        alter_schemas: list[dict] = []
        old_schemas: list[tuple] = query_all(f"PRAGMA table_info({cls().get_tablename()})")
        schema_keys: list[str] = []

        print('old_schemas: ', old_schemas)

        if not old_schemas:
            return cls.get_schema()
        
        for old_schema in old_schemas:
            field: Field | None = cls.__dict__.get(old_schema[1], None)

            schema_keys.append(old_schema[1])

            if field:
                schema = field.get_schema_changes(old_schema)

                if schema:
                    alter_schemas.append(schema)

            else:
                schema = {'name' : old_schema[1], 'mode' : 'drop'}
                alter_schemas.append(schema)
                dropped_schemas.append(old_schema)

        for key, value in cls.__dict__.items():
            if not isinstance(value, Field):
                continue

            if not key in schema_keys:
                schema = {}

                for old_schema in dropped_schemas:
                    if not value.get_schema_changes(old_schema):
                        schema = {
                            'old_name' : old_schema[1],
                            'new_name' : key,
                            'mode' : 'rename'
                        }

                        alter_schemas.remove({'name' : old_schema[1], 'mode' : 'drop'})

                if not schema:
                    schema = value.get_schema(key)
                    schema['mode'] = 'add'

                alter_schemas.append(schema)

        if not alter_schemas:
            return None

        print('schemas: ', alter_schemas)

        return {"tablename" : cls().get_tablename(), "create" : [], "alter" : alter_schemas}
    
    @classmethod
    def get_schema(cls) -> dict:
        primary_key: bool = False
        schemas: list = []

        for key, value in cls.__dict__.items():
            if not isinstance(value, Field):
                continue

            if value.primary_key:
                if primary_key:
                    raise ValueError("Model can only have one primary key")
                
                primary_key = True

            schemas.append(value.get_schema(key))

        if not primary_key:
            raise ValueError("Model must have a primary key")

        return {"tablename" : cls().get_tablename(), "create" : schemas, "alter" : [],}
    
    @classmethod
    def from_db(cls, row: tuple) -> Self:
        field_names = cls._get_column_names()
        field_values = dict(zip(field_names, row))
        return cls(**field_values)