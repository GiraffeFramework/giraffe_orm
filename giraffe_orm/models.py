from giraffe_orm.connections import query_all, change_db
from giraffe_orm.queries import Query
from giraffe_orm.schemas import table_pragma, Schema, RawFieldSchema, RenameFieldSchema, FieldSchema
from giraffe_orm.fields import Field

from typing_extensions import Self
import typing as t


T = t.TypeVar("T", bound='Model')
F = t.TypeVar("F", bound=Field[t.Any])


def _get_rename_field_schema(name: str, old_name: str) -> RenameFieldSchema:
    """Helper function to return a type corrected RenameFieldSchema"""

    return {
        "mode": "rename",
        "name": name,
        "old_name": old_name
    }


class Model:
    query: Query[Self, Self]


    _data: dict[str, t.Any] = {}
    _original_data: dict[str, t.Any] = {}
    
    _fields: list[Field[t.Any]] = []
    _primary_key: Field[t.Any]

    _tablename: str | None = None
    _registry: list[t.Type['Model']] = []


    def __init__(self, **kwargs: dict[str, t.Any]) -> None:
        self._original_data = kwargs
        
        for key, value in kwargs.items():
            setattr(self, key, value)


    def __init_subclass__(cls: t.Type[T], is_abstract: bool = False, **kwargs: dict[str, t.Any]):
        super().__init_subclass__(**kwargs)
        cls.query = Query(cls)

        # Initialize class specific storage
        cls._fields = []
        found_pk: Field[t.Any] | None = None

        # Any non-abstract class should be taken up into the registry.
        if not is_abstract:
            Model._registry.append(cls)

        # Loop over all key, values of this Model instance (ignore all that 
        # arent Fields). Store all Fields and the primary_key
        for name, value in cls.__dict__.items():
            if not isinstance(value, Field): continue
            if not name.isidentifier(): raise ValueError(f"Invalid field name {name}")
            
            value.name = name
            cls._fields.append(value)   # type: ignore

            if not value.primary_key: continue
            if found_pk != None:
                raise TypeError(f"You cannot have multiple primary keys")
            
            found_pk = value     # type: ignore

        if not found_pk: raise ValueError("No primary key defined for Model")
        cls._primary_key = found_pk     # type: ignore


    @classmethod
    def _valid_tablename(cls, name: str) -> str:
        if len(name) > 128:
            raise ValueError("Table name cannot be longer than 128 characters")

        if not name.replace("_", "").isalnum():
            raise ValueError("Table name cannot contain non-alphanumeric characters")
        
        return name
    
    @classmethod
    def _cls_tablename(cls) -> str:
        if cls._tablename:
            return cls._tablename
        
        if hasattr(cls, "__tablename__"):
            cls._tablename = cls._valid_tablename(getattr(cls, "__tablename__"))
        
        else:
            cls._tablename = cls.__name__.lower() + "s"
        
        return cls._tablename

    @classmethod
    def _fields_of_type(cls, type: t.Type[F]) -> t.Generator[F, t.Any, t.Any]:
        for field in cls._fields:
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
        old_schemas: list[table_pragma] = query_all(f"PRAGMA table_info({cls._cls_tablename()})")
        schema_keys: list[str] = []

        print('\told_schemas: ', old_schemas)
        
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
                altered_fields.append(schema)
                continue

            schema = value._get_schema()
            schema["mode"] = 'add'

            altered_fields.append(schema)


        if not altered_fields: return None
        print('\tschemas: ', altered_fields)


        return {
            "tablename": cls._cls_tablename(),
            "create": [],
            "alter": altered_fields
        }
    

    @classmethod
    def _get_schema(cls) -> Schema:
        """
        Generates the schema for the current Model. Will look for a primary key,
        and all its fields.
        """
        primary_key: bool = False
        fields: list[FieldSchema] = []

        for field in cls._fields:
            if field.primary_key:
                if primary_key: raise ValueError("Model can only have one primary key")

                primary_key = True

            fields.append(field._get_schema())

        if not primary_key: raise ValueError("Model must have a primary key")

        return {
            "tablename": cls()._cls_tablename(),
            "create": fields,
            "alter": []
        }
    

    @classmethod
    def _from_db(cls, row: tuple[t.Any, ...]) -> Self:
        field_names = cls._get_column_names()
        field_values = dict(zip(field_names, row))

        return cls(**field_values)


    def save(self) -> None:
        changed_fields: list[str] = []
        changed_values: list[t.Any] = []

        # Loop over all the fields of this Model and check whether their values
        # changed. If so store the field names and the new values
        for field in self._fields:
            value = self._data[field.get_name()]
            if self._original_data[field.get_name()] == value: continue

            changed_fields.append(field.get_name())
            changed_values.append(value)

        if not changed_fields: return

        pk_name = type(self)._primary_key.get_name()
        query = \
        f"""
        UPDATE {self._cls_tablename()} 
        SET {" = ?, ".join(changed_fields)} = ? 
        WHERE {pk_name} = ?
        """

        # As final parameter, we add the identifier for this modal (whatever 
        # its value is for the primary key field)
        changed_values.append(self._original_data[pk_name])
        change_db(query, tuple(changed_values))

        return
