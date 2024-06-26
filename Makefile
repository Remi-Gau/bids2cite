.PHONY: clean clean-build clean-pyc clean-test coverage help
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
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -f tests/bids/.bidsignore
	rm -f tests/bids/datacite.yml
	rm -f tests/bids/LICENSE
	rm -f tests/bids/CITATION.cff
	rm -rf tests/bids/derivatives

## DOC
.PHONY: docs

docs: ## generate Sphinx HTML documentation, including API docs
	$(BROWSER) docs/_build/html/index.html

## TESTS

coverage: ## use coverage
	coverage erase
	coverage run --source bids2cite -m pytest

test-cli:
	bids2cite tests/bids \
		--skip-prompt \
		-vv \
		--keywords "foo, bar, me" \
		--license "PDDL-1.0" \
		--description "this is the description of my dataset"
	make clean-test
