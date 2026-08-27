from tests.setup import db 
from typing import Generator

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> Generator[None, None, None]:
    version = db.migrate()
    
    if version is not None:
        db.upgrade(version)
            
    yield
    
    # Add any teardown/cleanup logic here
