from giraffe_orm.schemas import table_pragma, FieldSchema

from datetime import datetime, date

import typing as t


if t.TYPE_CHECKING:
    from .model import Model


def _is_valid(value: t.Any, expected_type: type, name: str) -> bool:
    if value is not None and not isinstance(value, expected_type):
        raise TypeError(f"Invalid value for {name}, expected {expected_type.__name__}")
    
    return True


def _serialize(value: t.Any) -> t.Any | None:
    """
    Make values SQL compatible.
    """

    if callable(value): return None

    return value


class Clause(t.TypedDict):
    lhs: str
    rhs: t.Any


T = t.TypeVar('T')


class Field(t.Generic[T]):
    def __init__(
            self, 
            type: str, 
            nullable: bool = True, 
            primary_key: bool = False, 
            unique: bool = False, 
            default: t.Any | None = None,
        ) -> None:

        # Field names are set by the model when the class is initialized. They
        # take on the name of their respective attribute
        self.name = "UNKNOWN"

        self.type = type
        self.nullable = nullable
        self.primary_key = primary_key
        self.unique = unique
        self.default = default

        # Internally used for SELECT ... AS label <--
        self.__label: str | None = None

    
    def _get_schema(self) -> FieldSchema:
        return {
            "name" : self.name,
            "mode": "UNSET",
            "type": self.type,
            "notnull": not self.nullable,
            "dflt_value": _serialize(self.default),
            "pk": self.primary_key,
        }
    
    def _get_schema_changes(self, old_schema: table_pragma) -> FieldSchema | None:
        changes: dict[str, t.Any] = {}

        if self.type != old_schema[2]:
            changes["type"] = self.type

        if self.nullable == old_schema[3]:
            changes["notnull"] = not self.nullable

        dflt = _serialize(self.default)
        if dflt != old_schema[4]:
            changes["dflt_value"] = dflt

        if self.primary_key != old_schema[5]:
            changes["pk"] = self.primary_key

        if not changes: return None
        
        changes["name"] = old_schema[1]
        changes["mode"] = "alter"

        return FieldSchema(**changes)

    
    def _select(self) -> str:
        if not self.__label: return self.name
        return self.name + " AS " + self.__label


    def get_default(self) -> t.Any | None:
        """
        Properly handles callable default values
        """

        if self.default is None: return None

        if not callable(self.default): 
            return self.default

        return self.default()
    
    def get_name(self) -> str:
        return self.name

    def label(self, label: str) -> t.Self:
        self.__label = label
        return self


    @t.overload
    def __get__(self, instance: None, owner: t.Any) -> "Field[T]": ...
    @t.overload
    def __get__(self, instance: 'Model', owner: t.Any) -> T: ...
    def __get__(self, instance: 'Model | None', owner: t.Any) -> T | "Field[T]":
        if instance is None: return self

        # TODO: figure out None
        return instance.get(self.name) # type: ignore

    def __set__(self, instance: 'Model', value: str) -> None:
        instance.set(self.name, value)

    def __add__(self, value: T) -> Clause:
        return {
            "lhs": self.get_name() + " +",
            "rhs": value
        }


class StringField(Field[str]):
    def __init__(self, nullable: bool = True, primary_key: bool = False, unique: bool = False, default: str | None = None, max_length: int | None = 255, min_length: int | None = 0) -> None:
        super().__init__("VARCHAR", nullable, primary_key, unique, default)

        if max_length is not None and _is_valid(max_length, int, "max_length"):
            self.max_length = max_length
            self.type = f"VARCHAR({max_length})"

        if min_length is not None and _is_valid(min_length, int, "min_length"):
            self.min_length = min_length

    def valid(self, value: str) -> tuple[bool, str]:
        if self.max_length and len(value) > self.max_length:
            return False, "Maximum length exceeded"
                
        if self.min_length and len(value) < self.min_length:
            return False, "Minimum length not reached"
        
        return True, ""


class IntegerField(Field[int]):
    def __init__(self, nullable: bool = True, primary_key: bool = False, unique: bool = False, default: int | None = None) -> None:
        super().__init__('INTEGER', nullable, primary_key, unique, default)


class FloatField(Field[float]):
    def __init__(self, nullable: bool = True, primary_key: bool = False, unique: bool = False, default: float | None = None) -> None:
        super().__init__('FLOAT', nullable, primary_key, unique, default)


class DateTimeField(Field[datetime]):
    def __init__(self, nullable: bool = True, primary_key: bool = False, unique: bool = False, default: datetime | None = None) -> None:        
        super().__init__('DATETIME', nullable, primary_key, unique, default)


class DateField(Field[date]):
    def __init__(self, nullable: bool = True, primary_key: bool = False, unique: bool = False, default: t.Any | None = None) -> None:        
        super().__init__('DATE', nullable, primary_key, unique, default)
