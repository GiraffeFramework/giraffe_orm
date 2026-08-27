import pytest
from datetime import date

from tests.partial_selects.models import SelectMethods
from tests.setup import db


def test_select_single_column() -> None:
    result = db(SelectMethods).select(SelectMethods.integer).first()

    if result is None:
        pytest.fail("Expected a record, but received None.")

    if len(result) > 1:
        pytest.fail("Expected only one field.")

    assert isinstance(result, tuple), "Result must be a tuple."
    
    integer_val = result[0]
    assert isinstance(integer_val, int), "Expected the loaded field to be of type int."


def test_select_multiple_columns() -> None:
    result = db(SelectMethods).select(SelectMethods.integer, SelectMethods.string).first()

    if result is None:
        pytest.fail("Expected a record, but received None.")

    assert isinstance(result, tuple), "Result must be a tuple."
    assert len(result) == 2, f"Expected exactly 2 fields, got {len(result)}."

    integer_val, string_val = result
    
    assert isinstance(integer_val, int), "First field must be an int."
    assert isinstance(string_val, str), "Second field must be a str."


def test_select_all_multiple_columns() -> None:
    results = db(SelectMethods).select(SelectMethods.float, SelectMethods.date).all()

    assert isinstance(results, list), "Expected .all() to return a list."
    
    if len(results) == 0:
        pytest.fail("Expected at least one record in the database.")

    first_row = results[0]
    
    assert isinstance(first_row, tuple), "Each row must be a tuple."
    assert len(first_row) == 2, f"Expected exactly 2 fields per row, got {len(first_row)}."

    float_val, date_val = first_row
    
    assert isinstance(float_val, float), "First field must be a float."    
    assert isinstance(date_val, date), "Second field must be a date."
