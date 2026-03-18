import pytest
import pathlib
import time

import requests

from infra.database import Database

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent

CREATE_SQL = ROOT_DIR / "infra" / "sql" / "001_create_tables.sql"
DROP_SQL = ROOT_DIR / "infra" / "sql" / "002_drop_tables.sql"
WEB_SERVER_URL = "http://127.0.0.1:5000/openapi.json"


def _session_requires_web_server(request: pytest.FixtureRequest) -> bool:
    return any(
        "tests/test_post_atendimento.py" in item.nodeid
        for item in request.session.items
    )


def _wait_for_web_server(timeout_seconds: int = 30):
    deadline = time.monotonic() + timeout_seconds
    last_error = None

    while time.monotonic() < deadline:
        try:
            response = requests.get(WEB_SERVER_URL, timeout=1)
            if response.ok:
                return
        except requests.RequestException as err:
            last_error = err

        time.sleep(0.5)

    raise RuntimeError(
        f"Servidor web não ficou disponível em {WEB_SERVER_URL} dentro de {timeout_seconds}s."
    ) from last_error


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Database.run_sql_file(DROP_SQL)
    Database.run_sql_file(CREATE_SQL)
    yield  # retoma o controle para os testes.


@pytest.fixture(scope="session", autouse=True)
def wait_for_web_server(request: pytest.FixtureRequest):
    if not _session_requires_web_server(request):
        return

    _wait_for_web_server()
