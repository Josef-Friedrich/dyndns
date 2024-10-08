all: test

serve:
	poetry run dyndns-debug serve

check:
	poetry run dyndns-debug check

test_quick:
	poetry run tox -e py312

test:
	poetry run tox

install: update

clear_poetry_cache:
	poetry cache clear PyPI --all --no-interaction
	poetry cache clear _default_cache --all --no-interaction

# https://github.com/python-poetry/poetry/issues/34#issuecomment-1054626460
# pip install --editable . # error: externally-managed-environment -> pipx
install_editable:
	pipx install --force --editable .

update: clear_poetry_cache
	poetry lock
	poetry install

build:
	poetry build

publish:
	poetry build
	poetry publish

format:
	poetry run tox -e format

docs:
	poetry run tox -e docs
	xdg-open docs/_build/index.html > /dev/null 2>&1

lint:
	poetry run tox -e lint

type_check:
	poetry run tox -e type-check

pin_docs_requirements:
	pip-compile --output-file=docs/requirements.txt docs/requirements.in pyproject.toml

dev_up_no_log:
	sudo docker compose --file ./dev-dns-server/compose.yaml up --detach

dev_up: dev_up_no_log dev_logs

dev_down:
	sudo docker compose --file ./dev-dns-server/compose.yaml down

dev_logs:
	sudo docker compose --file ./dev-dns-server/compose.yaml logs --follow

.PHONY: test install install_editable update build publish format docs lint pin_docs_requirements dev_server
