import typing as t
import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()


def change_db(query: str, parameters: tuple) -> int:
    print('change_query: ', query)

    cursor.execute(query, parameters)
    conn.commit()
    
    if query.lower().startswith("insert"):
        last_row_id = cursor.lastrowid

        return last_row_id if last_row_id else 0

    return 0


def query_all(query: str) -> list[tuple]:
    print('all_query: ', query)

    cursor.execute(query)
    rows = cursor.fetchall()

    print('all_query_result: ', rows)

    return rows


def query_one(query: str, parameters: tuple | None = None) -> tuple:
    print('one_query: ', query)

    if parameters:
        cursor.execute(query, parameters)

    else:
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