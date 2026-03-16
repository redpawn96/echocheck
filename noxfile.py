import os

import nox

nox.options.sessions = ["unit", "api"]


def _install(session: nox.Session) -> None:
    session.install("-r", "apps/api/requirements.txt")
    session.install("-r", "requirements-dev.txt")


@nox.session(python="3.12")
def unit(session: nox.Session) -> None:
    """Run unit tests."""
    _install(session)
    env = {"PYTHONPATH": "apps/api"}
    session.run("pytest", "-m", "unit", "tests/unit", env=env)


@nox.session(python="3.12")
def api(session: nox.Session) -> None:
    """Run API tests with FastAPI TestClient."""
    _install(session)
    env = {
        "PYTHONPATH": "apps/api",
        "DATABASE_URL": "sqlite+pysqlite:///./tests/test_api.db",
        "JWT_SECRET_KEY": "test-secret",
    }
    session.run("pytest", "-m", "api", "tests/api", env=env)


@nox.session(python="3.12")
def smoke(session: nox.Session) -> None:
    """Run smoke tests against a running API instance."""
    _install(session)
    env = {
        "PYTHONPATH": "apps/api",
        "SMOKE_BASE_URL": os.getenv("SMOKE_BASE_URL", "http://localhost:8000"),
    }
    session.run("pytest", "-m", "smoke", "tests/smoke", env=env)


@nox.session(python="3.12")
def all_tests(session: nox.Session) -> None:
    """Run all test markers."""
    _install(session)
    env = {
        "PYTHONPATH": "apps/api",
        "DATABASE_URL": "sqlite+pysqlite:///./tests/test_api.db",
        "JWT_SECRET_KEY": "test-secret",
        "SMOKE_BASE_URL": os.getenv("SMOKE_BASE_URL", "http://localhost:8000"),
    }
    session.run("pytest", "tests", env=env)
