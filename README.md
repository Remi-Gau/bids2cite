[![codecov](https://codecov.io/gh/Remi-Gau/bids2cite/branch/main/graph/badge.svg?token=UBE490738A)](https://codecov.io/gh/Remi-Gau/bids2cite)
[![License](https://img.shields.io/badge/license-GPL3-blue.svg)](./LICENSE)
![https://github.com/psf/black](https://img.shields.io/badge/code%20style-black-000000.svg)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Remi-Gau/bids2cite/main.svg)](https://results.pre-commit.ci/latest/github/Remi-Gau/bids2cite/main)

# bids2cite

Create a citation file for a BIDS dataset.

## Installation

```bash
git clone https://github.com/Remi-Gau/bids2cite.git
cd bids2cite
pip install .
```

### For developpers

```bash
pip install .[dev]
```

Basic tests can be run with:

```bash
make test
make test-cli
```

## Usage

```bash
bids2cite tests/bids \
    --skip-prompt false \
    --verbosity INFO \
    --keywords "foo, bar, me" \
    --description "this is the description of my dataset"
```
