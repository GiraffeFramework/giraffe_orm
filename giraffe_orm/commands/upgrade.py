
from giraffe_orm.connections import execute_script
from giraffe_orm.defaults import Migration
from giraffe_orm.schemas import Schema, FieldSchema, RawFieldSchema, RenameFieldSchema

from pathlib import Path

import typing_extensions as te
import argparse
import json


MIGRATIONS_DIR = Path.cwd() / "migrations"


def add_arguments(parser: argparse.ArgumentParser):
    parser.add_argument("migration_name", help="The migration name to apply.")

    return


def execute(args: argparse.Namespace):
    migration = MIGRATIONS_DIR / f"{args.migration_name}.json"

    if not migration:
        print(f"Migration {args.migration_name} not found.")
        return


    with open(migration) as file:
        migration_data: list[Schema] = json.load(file)

    migration_steps = _get_migration_steps(migration_data)


    if not migration_steps:
        print("No migrations available.")
        return
    

    execute_script(migration_steps)

    migration = Migration.query.create(name=args.migration_name)


    print(f"Migration {args.migration_name} applied successfully.")


def _get_migration_steps(migration: list[Schema]) -> str:
    """Generate SQL migration steps for each table schema."""
    migration_steps: str = ""

    for schema in migration:
        if "create" in schema and schema["create"]:
            create_fields = ", ".join(_get_field(field) for field in schema["create"])
            migration_steps += f"CREATE TABLE IF NOT EXISTS {schema["tablename"]} ({create_fields});"

        elif "alter" in schema and schema["alter"]:
            alter_statements = _get_alter_statements(schema["tablename"], schema["alter"])
            migration_steps += alter_statements

    return migration_steps


def _is_rename_field(alter: RawFieldSchema) -> te.TypeIs[RenameFieldSchema]:
    return alter["mode"] == "rename" and "old_name" in alter

def _is_field_schema(alter: RawFieldSchema) -> te.TypeIs[FieldSchema]:
    return alter["mode"] == "add" and "type" in alter


def _get_alter_statements(tablename: str, alterations: list[RawFieldSchema]) -> str:
    alter_statements: str = ""

    for alter in alterations:
        mode = alter["mode"]

        if mode == "drop":
            alter_statements += f"ALTER TABLE {tablename} DROP COLUMN {alter['name']};"

        elif _is_field_schema(alter):
            alter_statements += f"ALTER TABLE {tablename} ADD COLUMN {_get_field(alter)};"

        elif _is_rename_field(alter):
            alter_statements += f"ALTER TABLE {tablename} RENAME COLUMN {alter['old_name']} TO {alter['name']};"

    return alter_statements


def _get_field(field: FieldSchema):
    return f"{field["name"]} {field["type"]}{" NOT NULL" if field["notnull"] else ""}{" PRIMARY KEY" if field["pk"] else ""}{" AUTOINCREMENT" if field["pk"] and not field["dflt_value"] and field["type"] == "INTEGER" else ""}{" DEFAULT " + str(field["dflt_value"]) if field["dflt_value"] else ""}"
