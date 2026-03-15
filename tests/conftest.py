import pytest
import pathlib
from infra.database import Database

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent

CREATE_SQL = ROOT_DIR / "infra" / "sql" / "001_create_tables.sql"
DROP_SQL = ROOT_DIR / "infra" / "sql" / "002_drop_tables.sql"


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Database.run_sql_file(DROP_SQL)
    Database.run_sql_file(CREATE_SQL)
    yield  # retoma o controle para os testes.
