-include .env
export

.PHONY: install lint fmt test build check all

install:
	uv sync --all-extras

lint:
	uv run ruff check .
	uv run ruff format --check .

fmt:
	uv run ruff format .
	uv run ruff check --fix .

test:
	uv run pytest

build:
	uv run traininglog build

check:
	uv run traininglog check

all: lint test build
