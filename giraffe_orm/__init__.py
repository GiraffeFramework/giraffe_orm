from .versioning import migrate, upgrade

from .query import Query
from .model import Model as Model_
from .fields import StringField, IntegerField, FloatField, DateField

from typing import TypeVar


M = TypeVar("M", bound=Model_)


class GiraffeORM:
    Model = Model_
    String = StringField
    Integer = IntegerField
    Float = FloatField
    Date = DateField
    DateTime = DateField

    def __call__(self, model: type[M]) -> Query[M, M]:
        return Query[M, M](model)


    def migrate(self) -> int | None:
        return migrate(self)

    def upgrade(self, version: int) -> None:
        return upgrade(self, version)
