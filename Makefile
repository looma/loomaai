# Makefile for managing Looma-II and loomaai

# Variables
LOOMA_AI_DIR := .
COMPOSE_FILE := docker-compose.yml

# Targets
.PHONY: build update run halt status

define setup_env
    export MONGO_URI=mongodb://localhost:47017; \
    export MONGO_DB=looma; \
    export QDRANT_URL=http://localhost:46333; \
    export DATADIR=data; \
    . .env; \
    source env/bin/activate;
endef

build:
	@echo "Building loomaai..."
	@docker build -t loomaai -f Dockerfile .
	@echo "Build complete."

update:
	@echo "Updating loomaai..."
	@git -C $(LOOMA_AI_DIR) pull
	@echo "Update complete."

run:
	@echo "Make sure Looma-II docker compose is running first!"
	@echo "Make sure your .env file is populated with the OpenAI api key"
	. .env
	@echo "Starting loomaai services..."
	@docker-compose -f $(LOOMA_AI_DIR)/$(COMPOSE_FILE) up -d
	@echo "loomaai is running."

halt:
	@echo "Stopping loomaai services..."
	@docker-compose -f $(LOOMA_AI_DIR)/$(COMPOSE_FILE) down
	@echo "loomai services stopped."

status:
	@echo "Checking status of loomaai services..."
	@docker-compose -f $(LOOMA_AI_DIR)/$(COMPOSE_FILE) ps

logs:
	@echo "Showing logs for loomaai services..."
	@docker-compose -f $(LOOMA_AI_DIR)/$(COMPOSE_FILE) logs -f

shell:
	@echo "Opening a shell in the loomaai container..."
	@docker exec -it looma-streamlit /bin/bash

embed-all:
	@$(setup_env) python3 -m appai.cli.embed

translate-lessons:
	@$(setup_env) python3 -m appai.cli.translate_lessons

embed-missing:
	@$(setup_env) python3 -m appai.cli.embed --missing-only

populate-mongo:
	@$(setup_env) python3 -m appai.cli.populate_mongo