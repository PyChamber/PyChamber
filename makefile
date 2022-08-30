sources = pychamber

.PHONY: test format lint unittest coverage pre-commit clean build
test: format lint unittest

format:
	isort $(sources) tests
	black $(sources) tests

lint:
	flake8 $(sources) tests
	mypy $(sources) tests

unittest:
	pytest

coverage:
	pytest --cov=$(sources) --cov-branch --cov-report=term-missing tests

pre-commit:
	pre-commit run --all-files

clean:
	rm -rf .mypy_cache .pytest_cache
	rm -rf *.egg-info
	rm -rf .tox dist site
	rm -rf coverage.xml .coverage

build:
	pyrcc5 resources/resources.qrc -o pychamber/ui/resources_rc.py
	poetry install

package:
	pyinstaller ./pychamber/launch.py --copy-metadata pychamber --onefile --collect-data skrf --paths=pychamber --hidden-import pyvisa_py -y --clean
