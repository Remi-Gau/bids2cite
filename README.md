[![Python tests](https://github.com/Remi-Gau/bids2cite/actions/workflows/test.yml/badge.svg)](https://github.com/Remi-Gau/bids2cite/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/Remi-Gau/bids2cite/branch/main/graph/badge.svg?token=UBE490738A)](https://codecov.io/gh/Remi-Gau/bids2cite)
![License](https://img.shields.io/badge/license-GPL3-blue.svg)
![https://github.com/psf/black](https://img.shields.io/badge/code%20style-black-000000.svg)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Remi-Gau/bids2cite/main.svg)](https://results.pre-commit.ci/latest/github/Remi-Gau/bids2cite/main)
[![Documentation Status](https://readthedocs.org/projects/bids2cite/badge/?version=latest)](https://bids2cite.readthedocs.io/en/latest/?badge=latest)
![https://github.com/psf/black](https://img.shields.io/badge/code%20style-black-000000.svg)
[![PyPI version](https://badge.fury.io/py/bids2cite.svg)](https://badge.fury.io/py/bids2cite)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bids2cite)

# bids2cite

Create a citation file for a BIDS dataset based on its
`dataset_description.json` file.

Can also be used to interactively update references, authors and add a license
to a dataset.

You can add references using their DOI or PMID, and add authors by using their
ORCID.

This will also update the `dataset_description.json` by creating in a new file
in a `derivatives/bids2cite` folder.

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

Do not forget to check the [online doc](https://bids2cite.readthedocs.io) for
more details.

### Command line

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
    --license "CC0-1.0" \
    --verbose
```

`--keywords`, `--license` and `--description` allow you to pass
keywords, license and description to add to the citation file.

With `--skip-prompt` you will skip the prompt to add information manually
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

There is a sample TSV in the
[inputs folder](https://github.com/Remi-Gau/bids2cite/tree/main/inputs).

Type the following for more info on how to run it:

```bash
bids2cite --help
```

### Python

If you need to incorporate this into a python script you can do like this:

```python
from bids2cite.bids2cite import bids2cite
from pathlib import Path

path_to_bids_dataset = Path("path/to/bids/dataset")

bids2cite(
    bids_dir=path_to_bids_dataset,
    description="add something",
    keywords=["foo", "bar"],
    skip_prompt=True,
)
```

More info in the
[doc](https://bids2cite.readthedocs.io/en/latest/bids2cite.html#bids2cite.bids2cite.main)

## See also...

- [a BIDS dataset_description.json generator with a GUI](https://github.com/tolik-g/BIDS_GUI_dataset_description)
- datalad-neuroimaging
  [Pull Request](https://github.com/bids-standard/bids-specification/issues/901)
  to implement something similar to bids2cite in the datalad ecosysten
