# Makefile for Event Propagator and Consumer Services

.PHONY: install run test

# Install dependencies using Poetry
install:
	poetry install

# Run the Event Propagator and Consumer services
run:
	poetry run python main.py

# Run tests using pytest
test:
	poetry run pytest
