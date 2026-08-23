from tests.setup import db


class TerminalMethods(db.Model):
    __tablename__ = "terminal_methods"

    primary_key = db.Integer(primary_key=True)
    date_1 = db.Date(nullable=False)
    date_2 = db.Date(nullable=False)
