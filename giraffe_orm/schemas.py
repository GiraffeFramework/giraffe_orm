import typing as t


#                    cid,  name,  type,  notnull,  dflt_value,  pk
table_pragma = tuple[int,  str,   str,   int,      t.Any,       int]



class RawFieldSchema(t.TypedDict):
    mode: t.Literal["UNSET", "alter", "drop", "rename", "add"]
    name: str


class RenameFieldSchema(RawFieldSchema):
    old_name: str


class FieldSchema(RawFieldSchema):
    type: str
    notnull: bool
    dflt_value: t.Any
    pk: bool


class Schema(t.TypedDict):
    tablename: str
    create: list[FieldSchema]
    alter: list[RawFieldSchema]
