from giraffe_orm.fields import IntegerField, DateField
from giraffe_orm.model import Model

from datetime import date


class Migration(Model):
    __tablename__ = "__migrations__"

    id = IntegerField(primary_key=True)
    version = IntegerField(nullable=False)
    applied_at = DateField(nullable=False, default=date.today)
