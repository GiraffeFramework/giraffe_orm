from tests.partial_selects.models import SelectMethods
from tests.setup import db


def test_load_single_column() -> None:
    integer = db(SelectMethods).load(SelectMethods.integer).first()

    assert isinstance(integer, SelectMethods), "Failed to load single integer column"
    assert integer.date is None, "Failed to load only integer column"
    
    integers = db(SelectMethods).load(SelectMethods.integer).all()

    assert isinstance(integers, list), "Expected .all() to return a list"
    assert len(integers) > 0, "Expected at least one record in the database"
    assert isinstance(integers[0], SelectMethods), "Expected .all() to return a list of instances"


def test_load_multiple_columns() -> None:
    integer_string = db(SelectMethods).load(SelectMethods.integer, SelectMethods.string).first()

    assert integer_string is not None, "Failed to load integer and string columns"
    assert integer_string.date is None, "Failed to load only the selected columns"
    
    floats_dates = db(SelectMethods).load(SelectMethods.float, SelectMethods.date).all()

    assert isinstance(floats_dates, list)
    assert len(floats_dates) > 0, "Expected at least on record in the database"
    assert isinstance(floats_dates[0], SelectMethods), "Expected .all() to return a list of instances"
