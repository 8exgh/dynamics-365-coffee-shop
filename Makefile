.PHONY: configure up down test build logs backup
configure:
	python3 scripts/configure.py
up: configure
	docker compose up -d --build --wait
down:
	docker compose down
logs:
	docker compose logs -f --tail=100
test:
	.venv/bin/python -m pytest -q
build:
	npm --prefix web run build
backup:
	python3 scripts/backup.py
