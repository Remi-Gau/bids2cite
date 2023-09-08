.. _Usage :

Usage Notes
===========

*bids2cite* takes as principal input
the path of the `BIDS <https://bids-specification.readthedocs.io/en/latest/>`_ dataset
where the dataset description file is located.
The dataset description file is a JSON file named ``dataset_description.json``
that is located in the root of the BIDS dataset.

More information about the command line arguments can be found by typing::

    bids2cite --help

Command-Line Arguments
----------------------
.. argparse::
   :prog: bids2cite
   :module: bids2cite.bids2cite
   :func: _common_parser
