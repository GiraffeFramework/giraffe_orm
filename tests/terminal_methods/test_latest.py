from tests.terminal_methods.models import TerminalMethods
from tests.setup import db

import pytest


def test_latest_returns_matching_records() -> None:
    latest_1 = db(TerminalMethods).latest()
    
    if latest_1 is None:
        pytest.fail("Expected latest_1 to return a record, got None.")

    latest_2 = db(TerminalMethods).latest(TerminalMethods.date_1)
    latest_3 = db(TerminalMethods).latest("date_1")

    assert latest_1 == latest_2, "Direct column reference did not match default latest"
    assert latest_1 == latest_3, "String column reference did not match default latest"
