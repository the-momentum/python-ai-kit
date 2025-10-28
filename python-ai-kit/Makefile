DOCKER_COMMAND = docker compose -f docker-compose.yml
UV = uv run
ALEMBIC_CMD = $(UV) alembic

help:	## Show this help.
	@echo "============================================================"
	@echo "This is a list of available commands for this project."
	@echo "============================================================"
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

build:	## Builds docker image
	$(DOCKER_COMMAND) build --no-cache

run:	## Runs the envionment in detached mode
	$(DOCKER_COMMAND) up -d --force-recreate

up:	## Runs the non-detached environment
	$(DOCKER_COMMAND) up --force-recreate

stop:	## Stops running instance
	$(DOCKER_COMMAND) stop

down:	## Kills running instance
	$(DOCKER_COMMAND) down

test:	## Run the tests.
	export ENV=config/.env.test
	uv run pytest -v --cov=app

migrate:  ## Apply all migrations
	$(ALEMBIC_CMD) upgrade head

create_migration:  ## Create a new migration. Use 'make create_migration m="Description of the change"'
	@if [ -z "$(m)" ]; then \
		echo "Error: You must provide a migration description using 'm=\"Description\"'"; \
		exit 1; \
	fi
	$(ALEMBIC_CMD) revision --autogenerate -m "$(m)"


downgrade:  ## Revert the last migration
	$(ALEMBIC_CMD) downgrade -1
