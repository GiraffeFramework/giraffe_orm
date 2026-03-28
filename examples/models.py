from giraffe_orm import db


class Giraffe(db.Model):
    primary_key = db.String(primary_key=True, min_length=0, max_length=10)
    date = db.Date()
