install:
	poetry lock
	poetry install

build:
	poetry build

publish:
	poetry build
	poetry publish

test:
	poetry run tox

readme:
	./_generate_readme.py

doc:
	poetry run tox -e docs
	xdg-open .tox/docs/tmp/html/index.html

.PHONY: install build publish test readme doc
