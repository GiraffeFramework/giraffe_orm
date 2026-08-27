from tests.setup import db
from tests.partial_selects.models import SelectMethods
from tests.terminal_methods.models import TerminalMethods


db(SelectMethods).create()
db(TerminalMethods).create()
