from tests.partial_selects.models import SelectMethods
from tests.setup import db


integer = db(SelectMethods).load(SelectMethods.integer).first()
integers = db(SelectMethods).load(SelectMethods.integer).all()

integer_string = db(SelectMethods).load(SelectMethods.integer, SelectMethods.string).first()
floats_dates = db(SelectMethods).load(SelectMethods.float, SelectMethods.date).all()
