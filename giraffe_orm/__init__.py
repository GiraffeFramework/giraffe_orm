from .versioning import migrate, upgrade

from .queries import Query
from .models import Model as Model_
from .fields import String_, Integer_, Float_, Date_

from typing import TypeVar


M = TypeVar("M", bound=Model_)


class GiraffeORM:
    Model = Model_
    String = String_
    Integer = Integer_
    Float = Float_
    Date = Date_
    DateTime = Date_

    def __call__(self, model: type[M]) -> Query[M, M]:
        return Query[M, M](model)


    def migrate(self) -> int | None:
        return migrate(self)

    def upgrade(self, version: int) -> None:
        return upgrade(self, version)
