# MORPC Python package

## Introduction

The MORPC data team maintains a package with contains commonly-used constants, mappings, and functions to allow for code-reuse in multiple scripts.  The package documentation and code is available at the [morpc-py](https://github.com/morpc/morpc-py) repository in GitHub.  

This package is still in development but currently contains the following modules:

  - morpc - Main library.  Includes contents which are broadly applicable for MORPC's work, including MORPC branding, region definitions and utilities, and general purpose data manipulation functions.
  - morpc.frictionless -  Functions and classes for working with metadata, including schemas, resources, and data packages. These are for internal processes that use the [frictionless-py](https://github.com/frictionlessdata/frictionless-py/tree/main) package. Frictionless was implemented by MORPRC roughly around 2025 to manage all metadata and to develop workflow documentation. 
  - morpc.census - Constants and functions that are relevant when working with Census data, including decennial census, ACS, and PEP.

## Installation

Install via pip.


```python
# !pip install morpc --upgrade
```

## Import morpc package 


```python
import morpc
```

## Demos

See [demo] notebook for more information on features and functionality.