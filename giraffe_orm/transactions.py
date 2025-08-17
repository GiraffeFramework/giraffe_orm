class Transaction:
    def __init__(self, connection):
        self.conn = connection

    def __enter__(self):
        self.conn.execute("BEGIN;")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type: 
            self.conn.execute("ROLLBACK;")

        else:
            self.conn.execute("COMMIT;")


"""
class Database:
    def __init__(self, conn):
        self.conn = conn

    def transaction(self):
        return Transaction(self.conn)

with db.transaction():
    giraffe = Giraffe(date=...)
    giraffe.save()
    other = OtherModel(...)
    other.save()

"""
