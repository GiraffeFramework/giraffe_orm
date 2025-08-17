from pathlib import Path

from ..connections import execute_script
from ..defaults import Migration

import typing as t
import argparse
import json


MIGRATIONS_DIR = Path.cwd() / 'migrations'


def add_arguments(parser: argparse.ArgumentParser):
    parser.add_argument("migration", help="The migration name to apply.")

    return


def execute(args):
    migration = MIGRATIONS_DIR / f'{args.migration}.json'

    if not migration:
        print("Migration {args.migration} not found.")

        return

    with open(migration) as file:
        migration = json.load(file)

    migration_steps = _get_migration_steps(migration)

    if not migration_steps:
        print("No migrations available.")

        return

    execute_script(migration_steps)

    migration = Migration.query.create(
        name=args.migration
    )

    print(f"Migration {args.migration} applied successfully.")


def _get_migration_steps(migration: list[dict]) -> str:
    """Generate SQL migration steps for each table schema."""
    migration_steps: str = ''

    for schema in migration:
        if 'create' in schema and schema['create']:
            create_fields = ', '.join(_get_field(field) for field in schema['create'])
            migration_steps += f"CREATE TABLE IF NOT EXISTS {schema['tablename']} ({create_fields});"

        elif 'alter' in schema and schema['alter']:
            alter_statements = _get_alter_statements(schema['tablename'], schema['alter'])
            migration_steps += alter_statements

    return migration_steps


def _get_alter_statements(tablename: str, alterations: list[dict]) -> str:
    """Generate SQL ALTER TABLE statements."""
    alter_statements: str = ''

    for alter in alterations:
        if alter['mode'] == 'drop':
            alter_statements += f"ALTER TABLE {tablename} DROP COLUMN {alter['name']};"

        elif alter['mode'] == 'add':
            alter_statements += f"ALTER TABLE {tablename} ADD COLUMN {_get_field(alter)};"

        elif alter['mode'] == 'rename':
            alter_statements += f"ALTER TABLE {tablename} RENAME COLUMN {alter['old_name']} TO {alter['new_name']};"

    return alter_statements


def _get_field(field: dict):
    return f"{field['name']} {field['type']}{' NOT NULL' if field['notnull'] else ''}{' PRIMARY KEY' if field['pk'] else ''}{' AUTOINCREMENT' if field['pk'] and not field['dflt_value'] and field['type'] == 'INTEGER' else ''}{' DEFAULT ' + str(field['dflt_value']) if field['dflt_value'] else ''}"