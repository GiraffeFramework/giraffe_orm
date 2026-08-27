from tests.setup import db

from datetime import date


class SelectMethods(db.Model):
    __tablename__ = "select_methods"

    primary_key = db.Integer(primary_key=True)
    integer = db.Integer(nullable=False, default=0)
    string = db.String(nullable=False, default="test")
    date = db.Date(nullable=False, default=date.today)
    float = db.Float(nullable=False, default=0)
