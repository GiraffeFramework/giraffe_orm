from tests.terminal_methods.models import TerminalMethods
from tests.setup import db


latest_1 = db(TerminalMethods).latest()
latest_2 = db(TerminalMethods).latest(TerminalMethods.date_1)
latest_3 = db(TerminalMethods).latest("date_1")

assert latest_1 is not None
assert latest_1 == latest_2
assert latest_1 == latest_3
