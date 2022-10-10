[![codecov](https://codecov.io/gh/Remi-Gau/bids2cite/branch/main/graph/badge.svg?token=UBE490738A)](https://codecov.io/gh/Remi-Gau/bids2cite)
[![License](https://img.shields.io/badge/license-GPL3-blue.svg)](./LICENSE)
![https://github.com/psf/black](https://img.shields.io/badge/code%20style-black-000000.svg)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Remi-Gau/bids2cite/main.svg)](https://results.pre-commit.ci/latest/github/Remi-Gau/bids2cite/main)
[![Documentation Status](https://readthedocs.org/projects/bids2cite/badge/?version=latest)](https://bids2cite.readthedocs.io/en/latest/?badge=latest)

# bids2cite

Create a citation file for a BIDS dataset.

Can also be used to update references, authors and add license to a dataset.

## Visual demo

[![demo](https://user-images.githubusercontent.com/6961185/194825672-d7af29d1-62db-49bf-8d74-9d4fa8d32b32.png)](https://www.youtube.com/embed/BXSW5KGoQRY)

## Installation

```bash
pip install bids2cite
```

### For developers

Fork the repo and clone your fork.

```bash
pip install .[dev]
```

Basic tests can be run with:

```bash
make test
make test-cli
```

## Usage

The most basic usage is:

```bash
bids2cite path_to_bids_dataset
```

An example of call with all the options:

```bash
bids2cite "tests/bids" \
    --keywords "foo, bar, me" \
    --description "this is the description of my dataset" \
    --authors_file "inputs/authors.tsv" \
    --skip-prompt false \
    --verbosity INFO
```

`--keywords` and `--description` allow you to pass keywords and description to
add to the citation file.

`--skip-prompt` is set to `false` (default) to prompt you for information to add
to the citation file.

`--authors_file` points to a TSV file containing potential authors to add
citation file. This can be useful if you need to have a single file to keep
track of several lab members and only pick the relevant ones to add to a given
dataset.

This TSV file must at least have `first_name` and `last_name` columns, but can
also include `ORCID` and `affiliation` columns.

**Example**

| first_name | last_name | ORCID               | affiliation |
| ---------- | --------- | ------------------- | ----------- |
| Rémi       | Gau       | 0000-0002-1535-9767 | UCLouvain   |
| Mohamed    | Rezk      | 0000-0002-1866-8645 | UCLouvain   |

There is a sample TSV in the [inputs folder](https://github.com/Remi-Gau/bids2cite/tree/main/inputs).

Type the following for more info on how to run it:

```bash
bids2cite --help
```