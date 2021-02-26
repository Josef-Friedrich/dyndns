build:
	rm -rf dist
  # No bdist_wheel: problems with versioneer. Version nummer is not
	# replaced in the dyndns-1.1.0+4.gbe56337-py3-none-any.whl file
	python3 setup.py sdist

upload:
	pip3 install twine
	twine upload --skip-existing dist/*

readme:
	./_generate_readme.py

test:
	pyenv update
	pyenv install --skip-existing 3.6.13
	pyenv install --skip-existing 3.7.10
	pyenv install --skip-existing 3.9.2
	pyenv local 3.6.13 3.7.10 3.9.2
	pip3 install tox
	tox

doc:
	tox -e docs
	xdg-open .tox/docs/tmp/html/index.html

.PHONY: build upload test readme doc
