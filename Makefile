build:
	python3 setup.py sdist bdist_wheel


upload:
	pip3 install twine
	twine upload --skip-existing dist/*


.PHONY: build upload
	
