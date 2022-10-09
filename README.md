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
