import typing as t
import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()


def change_db(action: str) -> int:
    print('change_query: ', action)

    cursor.execute(action)
    conn.commit()
    
    if action.lower().startswith("insert"):
        last_row_id = cursor.lastrowid

        return last_row_id if last_row_id else 0

    return 0


def query_all(query: str) -> list[tuple]:
    print('all_query: ', query)

    cursor.execute(query)
    rows = cursor.fetchall()

    print('all_query_result: ', rows)

    return rows


def query_one(query: str) -> tuple:
    print('one_query: ', query)

    cursor.execute(query)
    row = cursor.fetchone()

    print('one_query_result: ', row)

    return row


def get_column_names(query: str) -> list[str]:
    cursor.execute(query)
    return [description[0] for description in cursor.description]


def execute_script(script: str) -> None:
    print('script', script)

    cursor.executescript(script)
    conn.commit()

    return None