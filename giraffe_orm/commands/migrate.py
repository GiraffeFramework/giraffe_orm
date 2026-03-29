from pathlib import Path

from giraffe_orm.defaults import Migration
from giraffe_orm.schemas import Schema
from giraffe_orm.models import Model

import typing as t
import importlib
import argparse
import json


MIGRATIONS_DIR = Path.cwd() / 'migrations'


def add_arguments(parser: argparse.ArgumentParser):
    return


def execute(_: None):
    version: Migration | None = _get_version()
    models: list[t.Type[Model]] = _get_models()

    # Add migration table for initial migrations
    if not version:
        migration_name = "0.json"

    else:
        migration_name = f"{int(version.name.split('.')[0]) + 1}.json"

    if not models:
        print("No migrations available.")

        return
    
    if (MIGRATIONS_DIR / migration_name).exists():
        print(f"Run `giraffe upgrade {migration_name.split('.')[0]}` first before you can initiate a new migration.")

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


def _get_models() -> list[t.Type[Model]]:
    """
    Get all model class objects defined in models.py files at the custom framework app level.
    """

    # TODO: more permanent solution
    with open("temp.config.json", "r") as json_config:
        config = json.load(json_config)

    for module_path in config["models"]:
        importlib.import_module(module_path)

    models = Model._registry
    print(models)
    return models


def _get_version() -> Migration | None:
    """
    Get the latest migration version.
    """

    try:
        return Migration.query.latest('applied_at')
    
    except:
        return None