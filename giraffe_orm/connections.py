import typing as t
import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()


def change_db(query: str, parameters: tuple[t.Any, ...]) -> int:
    print('\tchange_query: ', query)

    cursor.execute(query, parameters)
    conn.commit()
    
    if query.lower().startswith("insert"):
        last_row_id = cursor.lastrowid

        return last_row_id if last_row_id else 0

    return 0


def query_all(query: str) -> list[tuple[t.Any, ...]]:
    print('\tall_query: ', query)

    cursor.execute(query)
    rows = cursor.fetchall()

    print('\tall_query_result: ', rows)

    return rows


def query_one(query: str, parameters: tuple[t.Any, ...] | None = None) -> tuple[t.Any, ...]:
    print('\tone_query: ', query)

    if parameters:
        cursor.execute(query, parameters)

    else:
        cursor.execute(query)
    
    row = cursor.fetchone()

    print('\tone_query_result: ', row)

    return row


def get_column_names(query: str) -> list[str]:
    cursor.execute(query)
    return [description[0] for description in cursor.description]


def execute_script(script: str) -> None:
    print('\tscript', script)

    cursor.executescript(script)
    conn.commit()

    return None
