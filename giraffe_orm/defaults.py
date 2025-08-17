import db


class Migration(db.Model):
    __tablename__ = "migrations"

    id = db.Integer(primary_key=True)
    name = db.String(max_length=10, min_length=1)
    applied_at = db.Date()
