from pathlib import Path

from ..defaults import Migration
from ..models import Model

import typing as t
import importlib.util
import argparse
import inspect
import json
import sys


MIGRATIONS_DIR = Path.cwd() / 'migrations'


def add_arguments(parser: argparse.ArgumentParser):
    return


def execute(args):
    version: Migration | None = _get_version()
    models: list[t.Type[Model]] = _get_models()

    # Add migration table for initial migrations
    if not version:
        migration_name = "0.json"
        
        models.append(Migration)

    else:
        migration_name = f"{int(version.name.split('.')[0]) + 1}.json"

    if not models:
        print("No migrations available.")

        return
    
    if (MIGRATIONS_DIR / migration_name).exists():
        print(f"Run `giraffe migrate {migration_name.split('.')[0]}` first before you can initiate a new migration.")

        return
    
    MIGRATIONS_DIR.mkdir(exist_ok=True)

    schemas: list = []


    for model in models:
        changes = model.get_schema_changes()

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

    root = Path.cwd()
    models = []

    # loop over all models.py files that are in a Giraffe app.
    for models_file in root.glob("*/models.py"):
        # Load file to get access to the classes
        module_name = f"models_{models_file.stem}"
        spec = importlib.util.spec_from_file_location(module_name, models_file)

        if not spec:
            raise ValueError(f"Failed to load module {module_name}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module) # type: ignore

        # Extract all model classes from the module
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ != module.__name__:
                continue

            if not issubclass(obj, Model):
                continue
            
            models.append(obj)

    return models


def _get_version() -> Migration | None:
    """
    Get the latest migration version.
    """

    try:
        return Migration.query.latest('applied_at')
    
    except:
        return None