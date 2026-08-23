from tests.partial_selects.models import SelectMethods
from tests.setup import db


integer = db(SelectMethods).select(SelectMethods.integer).first()
integers = db(SelectMethods).select(SelectMethods.integer).all()

integer_string = db(SelectMethods).select(SelectMethods.integer, SelectMethods.string).first()
floats_dates = db(SelectMethods).select(SelectMethods.float, SelectMethods.date).all()
