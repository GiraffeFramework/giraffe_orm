from giraffe_orm.fields import Integer_, Date_
from giraffe_orm.models import Model

from datetime import date


class Migration(Model):
    __tablename__ = "__migrations__"

    id = Integer_(primary_key=True)
    version = Integer_(nullable=False)
    applied_at = Date_(nullable=False, default=date.today)
