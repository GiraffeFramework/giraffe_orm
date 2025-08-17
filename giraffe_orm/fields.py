from datetime import _Date
from typing import Any, Optional, Tuple, Type, Generic, TypeVar, Union, overload, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Model


def _is_valid(value: Any, expected_type: Type, name: str) -> bool:
    if value is not None and not isinstance(value, expected_type):
        raise TypeError(f"Invalid value for {name}, expected {expected_type.__name__}")
    
    return True


T = TypeVar('T')


class Field(Generic[T]):
    def __init__(
            self, 
            type: str, 
            nullable: bool = True, 
            primary_key: bool = False, 
            unique: bool = False, 
            default: Optional[Any]=None,
            name: Optional[str]=None
        ) -> None:
        
        self.value: Any = None
        self.name: str = name if name else "unset"
        self.type = type
        self.nullable = nullable
        self.primary_key = primary_key
        self.unique = unique
        self.default = default

        self.max_length = None
        self.min_length = None

    def get_name(self) -> str:
        return self.name

    def valid(self, value: str) -> Tuple[bool, str]:
        if self.max_length and len(value) > self.max_length:
            return False, "Maximum length exceeded"
                
        if self.min_length and len(value) < self.min_length:
            return False, "Minimum length not reached"
        
        return True, ""
    
    def get_schema(self, name: str) -> dict:
        return {
            "name" : name,
            "type": self.type,
            "notnull": not self.nullable,
            "dflt_value": self.default,
            "pk": self.primary_key,
        }
    
    def get_schema_changes(self, old_schema: tuple) -> Optional[dict]:
        schema = {}

        if self.type != old_schema[2]:
            schema["type"] = self.type

        if self.nullable == old_schema[3]:
            schema["notnull"] = not self.nullable

        if self.default != old_schema[4]:
            schema["dflt_value"] = self.default

        if self.primary_key != old_schema[5]:
            schema["pk"] = self.primary_key

        if not schema:
            return None
        
        schema["name"] = old_schema[1]
        schema["mode"] = "alter"

        return schema
    
    def __set_name__(self, owner: Model, name: str):
        if not name.isidentifier():
            raise ValueError(f"Invalid field name: {name}")

        self.name = name
        owner.fields.append(self)

    @overload
    def __get__(self, instance: None, owner: Any) -> "Field[T]": ...
    @overload
    def __get__(self, instance: Any, owner: Any) -> T: ...
    def __get__(self, instance: Any, owner: Any) -> Union[T, "Field[T]"]:
        if instance is None:
            return self
        return self.value

    def __set__(self, instance: Any, value: str) -> None:
        self.value = value


class String(Field[str]):
    def __init__(self, nullable: bool = True, primary_key: bool = False, unique: bool = False, default: Optional[str] = None, name: Optional[str] = None, max_length: Optional[int] = 255, min_length: Optional[int] = 0) -> None:
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
    def __init__(self, nullable: bool = True, primary_key: bool = False, unique: bool = False, default: Optional[int] = None, name: Optional[str] = None) -> None:
        super().__init__('INTEGER', nullable, primary_key, unique)

        if default is not None and _is_valid(default, int, "default"):
            self.default = default


class Float(Field[float]):
    def __init__(self, nullable: bool = True, primary_key: bool = False, unique: bool = False, default: Optional[float] = None, name: Optional[str] = None) -> None:
        super().__init__('FLOAT', nullable, primary_key, unique)

        if default is not None and _is_valid(default, float, "default"):
            self.default = default


class Date(Field[_Date]):
    def __init__(self, nullable: bool = True, primary_key: bool = False, unique: bool = False, default: Optional[Any]=None, name: Optional[str] = None) -> None:
        if not default:
            default = "CURRENT_TIMESTAMP"
        
        super().__init__('DATE', nullable, primary_key, unique, default)
