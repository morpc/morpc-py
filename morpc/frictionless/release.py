"""Helpers for describing MORPC data outputs that are published as GitHub release assets.

Large build outputs are too big for Git LFS to hold economically, but they fit comfortably in a
GitHub release asset, which counts against neither the LFS quota nor the repository size. A release
asset URL is fully determined by (owner, repo, tag, filename), so a resource descriptor can be
written before the release exists, provided the tag is chosen first.
"""

import logging
logger = logging.getLogger(__name__)

RELEASE_ASSET_URL_TEMPLATE = "https://github.com/{owner}/{repo}/releases/download/{tag}/{filename}"


def release_asset_url(owner, repo, tag, filename):
    """Return the download URL for a GitHub release asset.

    This is the single place the release asset URL shape is encoded. Callers should use it rather
    than composing the URL themselves, so that a change to the shape is made in one place.

    Parameters
    ----------
    owner : str
        The GitHub organization or user that owns the repository, e.g. "morpc".
    repo : str
        The repository name, e.g. "morpc-parcels-standardize".
    tag : str
        The release tag, e.g. "v2026.7.22". Note the leading "v", which is part of the tag but not
        part of the package version.
    filename : str
        The name of the asset as published in the release.

    Returns
    -------
    str
        The asset download URL.
    """
    return RELEASE_ASSET_URL_TEMPLATE.format(owner=owner, repo=repo, tag=tag, filename=filename)


def calver(date=None, sequence=None):
    """Return an unpadded CalVer version string, e.g. "2026.7.22".

    The version is unpadded deliberately. create_package() coerces the version through
    packaging.Version, which silently normalizes a zero-padded "2026.07.22" to "2026.7.22". That
    would break the correspondence between the package version and the release tag that the asset
    URL depends on. Unpadded values round-trip unchanged, and this function asserts that they do.

    Parameters
    ----------
    date : datetime.date
        Optional. The date to derive the version from. Defaults to today.
    sequence : int
        Optional. A same-day rebuild counter, appended as a fourth component, e.g. "2026.7.22.1".
        If unspecified, the version has three components.

    Returns
    -------
    str
        The version string, which is guaranteed to round-trip through packaging.Version.
    """
    import datetime
    from packaging.version import Version

    if date is None:
        date = datetime.date.today()

    version = "{}.{}.{}".format(date.year, date.month, date.day)
    if sequence is not None:
        version = "{}.{}".format(version, sequence)

    if str(Version(version)) != version:
        logger.error("Version {} does not round-trip through packaging.Version.".format(version))
        raise RuntimeError

    return version


def publish_paths(resource, owner, repo, tag):
    """Return a copy of a resource whose path points at a release asset and whose _cache points at the local file.

    This is what a CI workflow runs at release time. The resource as built locally has a local file
    name in its path. Publishing rewrites that path to the immutable release asset URL and records
    the local file name in _cache, so that the same descriptor serves both consumers who must
    download the data and local development where the file is already on disk.

    The hash and bytes of the original resource are preserved, so a consumer that downloads the
    asset can verify it against the descriptor.

    Parameters
    ----------
    resource : frictionless.Resource
        The resource as built locally, whose path is a local file name.
    owner : str
        The GitHub organization or user that owns the repository.
    repo : str
        The repository name.
    tag : str
        The release tag the asset is published under, e.g. "v2026.7.22".

    Returns
    -------
    frictionless.Resource
        A new resource. The original is not modified.
    """
    import os
    import frictionless
    from .frictionless import _is_url

    descriptor = resource.to_dict()
    localPath = descriptor.get("path")

    if localPath is None:
        logger.error("Resource has no path. Unable to determine the asset filename.")
        raise RuntimeError

    if _is_url(localPath):
        logger.warning("Resource path is already a URL. It will be replaced with the release asset URL for tag {}.".format(tag))
        localPath = descriptor.get("_cache", os.path.basename(localPath))

    filename = os.path.basename(localPath)

    descriptor["path"] = release_asset_url(owner, repo, tag, filename)
    descriptor["_cache"] = localPath

    # The scheme describes the path, which has just changed from a local file to a URL. Frictionless
    # preserves an explicit scheme rather than re-deriving it, so a stale "file" would survive onto a
    # descriptor whose path is https. Drop it and let frictionless infer the scheme from the new path.
    descriptor.pop("scheme", None)

    return frictionless.Resource.from_descriptor(descriptor)
