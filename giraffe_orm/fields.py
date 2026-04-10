from giraffe_orm.schemas import table_pragma, FieldSchema

from datetime import datetime

import typing as t


if t.TYPE_CHECKING:
    from .models import Model


def _is_valid(value: t.Any, expected_type: type, name: str) -> bool:
    if value is not None and not isinstance(value, expected_type):
        raise TypeError(f"Invalid value for {name}, expected {expected_type.__name__}")
    
    return True


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
        
        self.name = "UNSET"
        self.type = type
        self.nullable = nullable
        self.primary_key = primary_key
        self.unique = unique
        self.default = default

        self.max_length = None
        self.min_length = None

        self.__label: str | None = None
    
    def _get_schema(self) -> FieldSchema:
        return {
            "name" : self.name,
            "mode": "UNSET",
            "type": self.type,
            "notnull": not self.nullable,
            "dflt_value": self.default,
            "pk": self.primary_key,
        }
    
    def _get_schema_changes(self, old_schema: table_pragma) -> FieldSchema | None:
        print("\t[FIELD OLD SCHEMA]: ", old_schema)
        changes: dict[str, t.Any] = {}

        if self.type != old_schema[2]:
            changes["type"] = self.type

        if self.nullable == old_schema[3]:
            changes["notnull"] = not self.nullable

        if self.default != old_schema[4]:
            changes["dflt_value"] = self.default

        if self.primary_key != old_schema[5]:
            changes["pk"] = self.primary_key

        if not changes: return None
        
        changes["name"] = old_schema[1]
        changes["mode"] = "alter"

        return FieldSchema(**changes)
    
    def _select(self) -> str:
        if not self.__label: return self.name
        return self.name + " AS " + self.__label
    
    def get_name(self) -> str:
        return self.name
    
    def label(self, label: str) -> t.Self:
        self.__label = label
        return self

    def valid(self, value: str) -> tuple[bool, str]:
        if self.max_length and len(value) > self.max_length:
            return False, "Maximum length exceeded"
                
        if self.min_length and len(value) < self.min_length:
            return False, "Minimum length not reached"
        
        return True, ""

    @t.overload
    def __get__(self, instance: None, owner: t.Any) -> "Field[T]": ...
    @t.overload
    def __get__(self, instance: 'Model', owner: t.Any) -> T: ...
    def __get__(self, instance: 'Model | None', owner: t.Any) -> T | "Field[T]":
        if instance is None: return self
        
        return t.cast(T, instance._data.get(self.name, self.default))

    def __set__(self, instance: 'Model', value: str) -> None:
        instance._data[self.name] = value

    def __add__(self, value: T) -> str:
        return f"{self.get_name()} + {value}"


class String(Field[str]):
    def __init__(self, nullable: bool = True, primary_key: bool = False, unique: bool = False, default: str | None = None, max_length: int | None = 255, min_length: int | None = 0) -> None:
        super().__init__("VARCHAR", nullable, primary_key, unique)

        if max_length is not None and _is_valid(max_length, int, "max_length"):
            self.max_length = max_length
            self.type = f"VARCHAR({max_length})"

        if min_length is not None and _is_valid(min_length, int, "min_length"):
            self.min_length = min_length
        
        if default is not None and _is_valid(default, str, "default"):
            if not self.valid(default)[0]:
                raise ValueError(f"Invalid default '{default}' provided")
            
            self.default = default


class Integer(Field[int]):
    def __init__(self, nullable: bool = True, primary_key: bool = False, unique: bool = False, default: int | None = None) -> None:
        super().__init__('INTEGER', nullable, primary_key, unique)

        if default is not None and _is_valid(default, int, "default"):
            self.default = default


class Float(Field[float]):
    def __init__(self, nullable: bool = True, primary_key: bool = False, unique: bool = False, default: float | None = None) -> None:
        super().__init__('FLOAT', nullable, primary_key, unique)

        if default is not None and _is_valid(default, float, "default"):
            self.default = default


class Date(Field[datetime]):
    def __init__(self, nullable: bool = True, primary_key: bool = False, unique: bool = False, default: t.Any | None = None) -> None:
        if not default:
            default = "CURRENT_TIMESTAMP"
        
        super().__init__('DATE', nullable, primary_key, unique, default)
