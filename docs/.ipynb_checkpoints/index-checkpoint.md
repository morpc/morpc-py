# morpc-py

## Introducion

The MORPC data team maintains a package with contains commonly-used constants, mappings, and functions to allow for code-reuse in multiple scripts.  The package documentation and code is available at the [morpc-py](https://github.com/morpc/morpc-py) repository in GitHub.

This package is still in development but will contain the following modules:

  - morpc - Main library.  Includes contents which are broadly applicable for MORPC's work, including MORPC branding, region definitions and utilities, and general purpose data manipulation functions.
  - morpc.frictionless -  Functions and classes for working with metadata, including schemas, resources, and data packages. These are for internal processes that us the [frictionless-py](https://github.com/frictionlessdata/frictionless-py/tree/main) package. Frictionless was implemented roughly 2025 to manage all metadata and to develop workflow documentation.
  - morpc.census - Constants and functions that are relevant when working with Census data, including decennial census, ACS, and PEP.
  - morpc.rest_apt - Tools for working with ArcGIS Online REST API, including scripts for creating local copies as frictionless resources.
  - morpc.plot - Tools for standard plots which leverage MORPC branding and data visualization best practices.
  - morpc.color - Various tools for working with colors, largely implemented through morpc.plot.

## Installation

A version of the package is available via pip and can be installed by a standard pip install. 

```bash
$ pip install morpc
```

### Dev Install

As the package is still in development, the best way to install it is via the pip [-editable option](https://setuptools.pypa.io/en/latest/userguide/development_mode.html). To do so:
1. Pull the most recent verision of the jordan_dev (branch name may change later) to a local repo.
2. Using the following command to install an editable version, replacing the path to the correct location.

```bash
$ pip install -e "C:/path/to/folder/morpc-py/"
```

Import the package as normal
```bash
$ import morpc
```

To contribute to the development branch make changes in the local repo and push them to git. When making changes to the package, you will have to re-import the package. If you are working in a Jupyter environment you will have to do this after restarting the kernel.

## Documentation

See [docs](https://morpc.github.com/morpc-py) for documentation.

