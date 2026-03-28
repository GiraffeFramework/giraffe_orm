from pathlib import Path

from giraffe_orm.defaults import Migration
from giraffe_orm.schemas import Schema
from giraffe_orm.models import Model

import typing as t
import importlib.util
import argparse
import json
import sys
import os


MIGRATIONS_DIR = Path.cwd() / 'migrations'


def add_arguments(parser: argparse.ArgumentParser):
    return


def execute(_: None):
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


def _import_python_files(root_dir: str = os.getcwd()):
    """
    Dynamically imports modules named 'models.py' within the specified directory 
    and adds them to sys.modules.
    """
    
    # We'll use this list to track files we successfully load
    loaded_modules = []

    # os.walk traverses the directory tree
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Prevent searching common virtual environment or temporary folders
        dirnames[:] = [d for d in dirnames if not d.startswith(('.', '__')) and d not in ('venv', 'env', 'site-packages')]

        if 'models.py' in filenames:
            file_path = os.path.join(dirpath, 'models.py')
            module_name = f'app_models.{os.path.basename(dirpath)}' 
            # Create a unique module name for dynamic loading

            try:
                # Use importlib to load the module specification
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                
                # If spec is None, the file likely isn't a valid Python module
                if spec is None:
                    continue

                # Create the module object
                module = importlib.util.module_from_spec(spec)
                
                # Add it to sys.modules so imports work correctly later
                sys.modules[module_name] = module
                
                # EXECUTE the module code
                spec.loader.exec_module(module) 
                
                loaded_modules.append(module)
            
            except Exception as e:
                # Handle import errors gracefully, e.g., print a warning
                print(f"Warning: Could not import model file at {file_path}. Error: {e}")

    return loaded_modules


def _get_models() -> list[t.Type[Model]]:
    """
    Get all model class objects defined in models.py files at the custom framework app level.
    """

    try:
        _import_python_files()
    
    except:
        raise FileNotFoundError("Your models must be declared separate from your main content.")

    models = Model._get_registry()
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