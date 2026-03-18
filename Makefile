servicesUp:
	docker compose -f infra/compose.yaml up -d

servicesStop:
	docker compose -f infra/compose.yaml stop

servicesDown:
	docker compose -f infra/compose.yaml down

servicesWaitDatabase:
	PYTHONPATH=. uv run python infra/scripts/wait_for_db.py

servicesLoadDatabase:
	PYTHONPATH=. uv run python infra/scripts/load_database.py

commit:
	uv run cz commit

run:
	make --quiet build

build:
	make servicesUp && make servicesWaitDatabase && make servicesLoadDatabase && uv run python run.py

test:
	make servicesUp && make servicesWaitDatabase && make servicesLoadDatabase && uv run honcho start -f Procfile.test -q flask

testWatch:
	uv run pytest-watcher . -vv

lint:
	uv run ruff check . --fix
	uv run ruff format

setup:
	uv sync
	uv run pre-commit install
	uv run pre-commit install --hook-type commit-msg
	@echo "✅ Ambiente configurado! Pre-commit hooks instalados."
