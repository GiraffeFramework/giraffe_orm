from pathlib import Path

from giraffe_orm.versioning.migration import Migration
from giraffe_orm.connections import execute_script
from giraffe_orm.schemas import Schema
from giraffe_orm.models import Model

import typing as t
import json


if t.TYPE_CHECKING:
    from giraffe_orm import GiraffeORM


MIGRATIONS_DIR = Path.cwd() / 'migrations'


def migrate(db: "GiraffeORM") -> int | None:
    models = _get_models(db)

    if not models:
        print("No migrations available.")
        return

    # Determine version & file name
    version = _get_version(db)
    version = 0 if version == None else version + 1

    migration_name = f"{version}.json"
    
    if (MIGRATIONS_DIR / migration_name).exists():
        print(f"Run `giraffe upgrade {version}` first before you can initiate a new migration.")
        return
    
    MIGRATIONS_DIR.mkdir(exist_ok=True)

    schemas: list[Schema] = []

    for model in models:
        changes = model._get_schema_changes()

        if changes:
            schemas.append(changes)

    if not schemas:
        print("No migrations available.")

        return

    with open(MIGRATIONS_DIR / migration_name, 'w') as file:
        json.dump(schemas, file, indent=4)

    print(f"Migration {migration_name} generated successfully.")

    return version


def _get_models(db: "GiraffeORM") -> list[t.Type[Model]]:
    """
    Get all model class objects defined in models.py files at the custom framework app level.
    """

    return db.Model._registry


def _get_version(db: "GiraffeORM") -> int | None:
    """
    Get the latest migration version. Created Migration table if it does not 
    yet exist.
    """

    execute_script(
        '''
        CREATE TABLE IF NOT EXISTS __migrations__ (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version INTEGER NOT NULL,
            applied_at DATE NOT NULL
        );
        '''
    )

    if migration := db(Migration).select(Migration.version).latest('applied_at'):
        return migration[0]

    return None
