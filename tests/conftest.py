import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
API_PATH = ROOT / "apps" / "api"

if str(API_PATH) not in sys.path:
    sys.path.insert(0, str(API_PATH))

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///./tests/test_api.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")

from app.db import Base, models  # noqa: E402,F401
from app.db.session import engine  # noqa: E402


@pytest.fixture
def reset_db() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
