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
	tox

doc:
	tox -e docs
	xdg-open .tox/docs/tmp/html/index.html

.PHONY: build upload test readme doc
