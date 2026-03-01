# ========================
# Config
# ========================
PYTHON      := ./venv/bin/python
PIP         := ./venv/bin/pip
FLASK_APP   := main.py
ENV         ?= development

# ========================
# Init Commands
# ========================
init-project: create-venv install-deps create-db db-upgrade db-seed
	@echo "▶ Project initialized successfully!"

create-venv:
	@echo "▶ Creating virtual environment..."
	python3 -m venv venv

install-deps:
	@echo "▶ Installing dependencies..."
	$(PIP) install -r requirements.txt

create-db:
	@echo "▶ Creating database if not exists..."
	$(PYTHON) scripts/create_db.py

# ========================
# Basic Commands
# ========================
.PHONY: run shell test lint clean

run:
	@echo "▶ Running app..."
	FLASK_ENV=$(ENV) $(PYTHON) $(FLASK_APP)

shell:
	@echo "▶ Flask shell..."
	FLASK_APP=$(FLASK_APP) $(PYTHON) -m flask shell

clean:
	@echo "▶ Cleaning cache..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# ========================
# Database Migration (Flask-Alembic)
# ========================
.PHONY: db-init db-migrate db-upgrade db-downgrade db-history db-current

db-init:
	@echo "▶ Init alembic..."
	FLASK_APP=$(FLASK_APP) $(PYTHON) -m flask db init

db-migrate:
	@echo "▶ Create migration..."
	FLASK_APP=$(FLASK_APP) $(PYTHON) -m flask db migrate -m "$(MSG)"

db-upgrade:
	@echo "▶ Upgrade database..."
	FLASK_APP=$(FLASK_APP) $(PYTHON) -m flask db upgrade

db-downgrade:
	@echo "▶ Downgrade database..."
	FLASK_APP=$(FLASK_APP) $(PYTHON) -m flask db downgrade $(STEP)

db-history:
	@echo "▶ Migration history..."
	FLASK_APP=$(FLASK_APP) $(PYTHON) -m flask db history

db-current:
	@echo "▶ Current revision..."
	FLASK_APP=$(FLASK_APP) $(PYTHON) -m flask db current

db-seed:
	@echo "▶ Seeding data..."
	FLASK_APP=$(FLASK_APP) $(PYTHON) -m flask seed-users

db-revision:
	@echo "▶ Create revision..."
	FLASK_APP=$(FLASK_APP) $(PYTHON) -m flask db revision -m "$(MSG)"


# test
.PHONY: test

# running all tests
test:
	@echo "▶ Running tests..."
	$(PYTHON) -m pytest tests/ -v

# ========================
# Docker
# ========================
.PHONY: docker-up docker-down docker-logs docker-clean docker-ps

docker-up:
	@echo "▶ Starting containers..."
	docker compose up -d --build

docker-down:
	@echo "▶ Stopping containers..."
	docker compose down

docker-logs:
	@echo "▶ Tailing logs..."
	docker compose logs -f

docker-clean:
	@echo "▶ Removing containers and volumes..."
	docker compose down -v --remove-orphans

docker-ps:
	@echo "▶ Container status..."
	docker compose ps