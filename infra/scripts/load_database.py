import pathlib
from infra.database import Database

ROOT_DIR = pathlib.Path(__file__).resolve().parents[2]
CREATE_SQL = ROOT_DIR / "infra" / "sql" / "001_create_tables.sql"
DROP_SQL = ROOT_DIR / "infra" / "sql" / "002_drop_tables.sql"


print("🔄 Resetando banco de dados...")
Database.run_sql_file(DROP_SQL)

print("🔄 Criando tabelas...")
Database.run_sql_file(CREATE_SQL)

print("✅ Banco de dados carregado com sucesso.")
