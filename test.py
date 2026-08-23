from tests.terminal_methods.models import TerminalMethods
from tests.partial_selects.models import SelectMethods
from tests.setup import db

from datetime import date


version = db.migrate()

if version != None:
    db.upgrade(version)


db(TerminalMethods).create()
db(SelectMethods).create(integer=1, string="test", date=date.today(), float=3.14)
