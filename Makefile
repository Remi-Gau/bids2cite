.PHONY: clean clean-build clean-pyc clean-test coverage dist  help install
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

# Put it first so that "make" without argument is like "make help".
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -f tests/bids/.bidsignore
	rm -f tests/bids/datacite.yml
	rm -f tests/bids/LICENSE
	rm -f tests/bids/CITATION.cff
	rm -rf tests/bids/derivatives

## INSTALL

install: clean  ## install the package to the active Python's site-packages
	pip install .

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

## STYLE

lint/flake8: ## check style with flake8
	flake8 bids2cite tests
lint/black: ## check style with black
	black bids2cite tests
lint/mypy: ## check style with mypy
	mypy bids2cite

lint: lint/black lint/mypy lint/flake8  ## check style

validate_cff: ## Validate the citation file
	cffconvert --validate


## DOC
.PHONY: docs

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/source/bids2cite.rst
	rm -f docs/source/modules.rst
	sphinx-apidoc -o docs/source bids2cite
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .


## TESTS

coverage: ## use coverage
	coverage erase
	coverage run --source bids2cite -m pytest

test: ## run tests with pytest
	pytest

test-cli:
	bids2cite tests/bids \
		--skip-prompt \
		-vv \
		--keywords "foo, bar, me" \
		--license "PDDL-1.0" \
		--description "this is the description of my dataset"
	make clean-test
