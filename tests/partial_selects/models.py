from tests.setup import db


class SelectMethods(db.Model):
    __tablename__ = "select_methods"

    primary_key = db.Integer(primary_key=True)
    integer = db.Integer(nullable=False)
    string = db.String(nullable=False)
    date = db.Date(nullable=False)
    float = db.Float(nullable=False)
