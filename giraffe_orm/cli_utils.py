from giraffe_orm import GiraffeORM
from pathlib import Path

import importlib
import sys
import os


AUTODISCOVERY_FILES = ["app.py", "main.py", "wsgi.py"]
DEFAULT_INSTANCE_NAMES = ["db", "orm"]


def _find_default_app() -> str | None:
    for filename in AUTODISCOVERY_FILES:
        if not Path(filename).exists():
            continue

        module_name = filename.removesuffix(".py")
        return f"{module_name}:db"

    return None


def resolve_db_instance(cli_app: str | None = None) -> GiraffeORM:
    # Highest priority: CLI argument
    target = cli_app

    # Medium priority: Environment variable
    if not target:
        target = os.environ.get("GIRAFFE_APP")

    # Lowest priority: Auto-discovery in current directory
    if not target:
        target = _find_default_app()

    if not target:
        print("Could not locate GiraffeORM instance.")
        print("Set GIRAFFE_APP environment variable or pass --app.")
        sys.exit(1)

    if ":" not in target:
        target = f"{target}:db"

    module_name, instance_name = target.split(":", 1)

    # Ensure current directory is in Python path
    sys.path.insert(0, str(Path.cwd()))

    try:
        module = importlib.import_module(module_name)

    except ImportError as exc:
        
        print(f"Could not import module '{module_name}': {exc}")
        sys.exit(1)

    instance = getattr(module, instance_name, None)

    if instance is None:
        print(f"Module '{module_name}' has no attribute '{instance_name}'.")
        sys.exit(1)

    return instance
