# Documentation for how to release an updated package to Pypi

## Introduction

This document is meant to instruct someone on how to release a new version of the morpc package to the [morpc pip site](https://pypi.org/project/morpc/).

The process involves the following steps:

1. After completing any updates to the .py files change increment the version in the parent __init__.py file. See below for instructions.
2. Commit and push and local changes to the [moprc-py](https://github.com/morpc/morpc-py) GitHub repository.
3. Create a new release in the GitHub via https://github.com/morpc/morpc-py/releases
    - Under "Choose a tag" create a new tag formated as a "v" followed by the version number. 
    - Click generate release notes,
    - Update Release tite to align with "morpc-v1.2.3"
    - Click publish release
4. Click on "Actions" in the top github menu. Make sure the automated workflow publishes the package to pip.
5. Go to [morpc pip site](https://pypi.org/project/morpc/) to check it is updated. 

## Version numbering

The version numbering is based on [semantic versioning](https://semver.org/) rules. See the website for more details. 

The basic format is major.minor.patch

Major numbers are for major breaking changes to the package. 0 is always for development, pre-release versions. 

Minor changes are changes that add functionality but are backward compatible.

Patch is for minor fixes and updates. 

Always increment the appropriate number by only one. Do not use leading zeros. 