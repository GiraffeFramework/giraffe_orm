from giraffe_orm.connections import query_all
from giraffe_orm.queries import Query
from giraffe_orm.schemas import table_pragma, Schema, RawFieldSchema, RenameFieldSchema
from giraffe_orm.fields import Field

from typing_extensions import Self
import typing as t


T = t.TypeVar("T", bound='Model')
F = t.TypeVar("F", bound=Field[t.Any])


def _get_rename_field_schema(name: str, old_name: str) -> RenameFieldSchema:
    return {
        "mode": "rename",
        "name": name,
        "old_name": old_name
    }


class Model:
    query: Query[Self]
    __fields: list[Field[t.Any]] = []
    __registry: list[t.Type["Model"]] = []


    def __init__(self) -> None:
        self._tablename: str | None = None


    def __init_subclass__(cls: t.Type[T], **kwargs: dict[str, t.Any]):
        super().__init_subclass__(**kwargs)
        cls.query = Query(cls)

        # There is no need to discover the internal table as it is 
        # automatically added during migrations anyway.
        if cls()._get_tablename() == "__migrations__": return
        cls.__registry.append(cls)


    def _valid_tablename(self, name: str) -> str:
        if len(name) > 128:
            raise ValueError("Table name cannot be longer than 128 characters")

        if not name.replace("_", "").isalnum():
            raise ValueError("Table name cannot contain non-alphanumeric characters")
        
        return name
    

    @classmethod
    def _add_field(cls, field: Field[t.Any]) -> None:
        cls.__fields.append(field)


    def _field_exists(self, field: str) -> bool:
        return hasattr(self, field)
    

    def _get_tablename(self) -> str:
        if self._tablename:
            return self._tablename

        if hasattr(self, "__tablename__"):
            self._tablename = self._valid_tablename(getattr(self, "__tablename__"))

        else:
            self._tablename = self.__class__.__name__.lower() + "s"
        
        return self._tablename

    @classmethod
    def _fields_of_type(cls, type: t.Type[F]) -> t.Generator[F, t.Any, t.Any]:
        for field in cls.__fields:
            if isinstance(field, type):
                yield field

    @classmethod
    def _get_column_names(cls):
        names: list[str] = []

        for _, value in cls.__dict__.items():
            if not isinstance(value, Field): continue

            names.append(value.name)

        return names
    
    @classmethod
    def _get_schema_changes(cls) -> Schema | None:
        """
        Loop over the potentially existing schema in the database and compare 
        them to the current schema. Detects added, removed, modified, and 
        renamed fields.
        """
        
        __dropped_fields: dict[RawFieldSchema, table_pragma] = {}
        altered_fields: list[RawFieldSchema] = []
        created_fields: list[RawFieldSchema] = []
        old_schemas: list[table_pragma] = query_all(f"PRAGMA table_info({cls()._get_tablename()})")
        schema_keys: list[str] = []

        print('old_schemas: ', old_schemas)
        
        # If not previous schema exists, we may just return the current schema
        if not old_schemas: return cls._get_schema()
        

        # Loop over all existing schemas for this table. Check whether a field 
        # with the current column exists. If a field exists, check whether it 
        # has changed and alter it.
        # If an old field no longer exists, assume it is deleted. We will alter
        # the current table (drop old field) and keep track of dropped fields 
        # for internal use (name change detection)
        for old_schema in old_schemas:
            field: Field[t.Any] | None = cls.__dict__.get(old_schema[1], None)

            schema_keys.append(old_schema[1])

            if field:
                changes = field._get_schema_changes(old_schema)
                if not changes: continue

                altered_fields.append(changes)

            else:
                schema = {"mode": "drop", "name": old_schema[1]}

                __dropped_fields[schema] = old_schema
                altered_fields.append(schema)


        # Loop over all current fields of the Model. If the field is part of 
        # the current schema it is ignored (schema_keys). Any new field is 
        # compared against all dropped fields. If the schema of a new field is
        # exactly the same as an old field, it is assumed as being renamed. 
        # Otherwise it is added as a completely new schema
        schema: RawFieldSchema | None = None

        for key, value in cls.__dict__.items():
            if not isinstance(value, Field): continue
            if key in schema_keys: continue

            for raw_field, old_schema in __dropped_fields.items():
                if value._get_schema_changes(old_schema): continue
                schema = _get_rename_field_schema(key, old_schema[1])

                altered_fields.remove(raw_field)

            if not schema:
                schema = value._get_schema(key)
                schema["mode"] = 'add'

            created_fields.append(schema)


        if not altered_fields: return None
        print('schemas: ', altered_fields)


        return {
            "tablename": cls()._get_tablename(),
            "create": created_fields,
            "alter": altered_fields
        }
    

    @classmethod
    def _get_schema(cls) -> Schema:
        """
        Generates the schema for the current Model. Will look for a primary key,
        and all its fields.
        """
        primary_key: bool = False
        fields: list[RawFieldSchema] = []

        for key, value in cls.__dict__.items():
            if not isinstance(value, Field): continue

            if value.primary_key:
                if primary_key: raise ValueError("Model can only have one primary key")

                primary_key = True

            fields.append(value._get_schema(key))

        if not primary_key: raise ValueError("Model must have a primary key")

        return {
            "tablename": cls()._get_tablename(),
            "create": fields,
            "alter": []
        }
    

    @classmethod
    def _from_db(cls, row: tuple[t.Any, ...]) -> Self:
        field_names = cls._get_column_names()
        field_values = dict(zip(field_names, row))
        return cls(**field_values)
    

    @classmethod
    def _get_registry(cls) -> list[t.Type["Model"]]:
        return cls.__registry
