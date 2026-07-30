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


def prepare_release(resources, owner, repo, tag, version=None, packageName=None, dir=None):
    """Rewrite a set of resource descriptors to point at a release's asset URLs, and rewrite them to disk.

    This is the multi-resource counterpart to publish_paths(): it loads each descriptor, publishes its
    path and _cache for the given tag, and writes the result back over the original file. Optionally it
    also bundles the resources into a data package, which is how a workflow that produces several
    related outputs (e.g. a database, a resource, a schema) hands them off together.

    Parameters
    ----------
    resources : str or list of str
        Path(s) to resource descriptor files. A single path may be passed as a bare string.
    owner : str
        The GitHub organization or user that owns the repository.
    repo : str
        The repository name.
    tag : str
        The release tag the assets will be published under, e.g. "v2026.7.22".
    version : str
        Optional. The version to record in the data package, used only when packageName is given.
        Defaults to tag with a single leading "v" stripped.
    packageName : str
        Optional. If given, bundle the published resources into a data package named packageName,
        written as "{packageName}.package.yaml" in dir. If omitted, no package is created.
    dir : str
        Optional. The directory the resource descriptors live in, used only when packageName is given,
        since create_package() requires resource paths relative to a single directory. Defaults to the
        common directory of the descriptor paths in resources.

    Returns
    -------
    list of frictionless.Resource
        The published resources, in the same order as resources.
    """
    import os
    import frictionless
    from .frictionless import create_package, write_resource

    if isinstance(resources, str):
        resources = [resources]

    published = []
    for resourcePath in resources:
        resource = frictionless.Resource(resourcePath)
        publishedResource = publish_paths(resource, owner, repo, tag)
        write_resource(publishedResource, resourcePath)
        published.append(publishedResource)

    if packageName is not None:
        if dir is None:
            # Compared as absolute paths so that equivalent spellings of one directory ("output_data"
            # and "./output_data") are not mistaken for two.
            dirs = {os.path.abspath(os.path.dirname(resourcePath)) for resourcePath in resources}
            if len(dirs) > 1:
                logger.error("Resource descriptors are not all in the same directory. create_package() requires resource paths relative to a single directory; pass dir explicitly.")
                raise RuntimeError

            # A bare filename has no dirname, but create_package() needs a real directory to resolve
            # the resource paths against.
            dir = os.path.dirname(resources[0]) or "."

        if version is None:
            version = tag[1:] if tag.startswith("v") else tag

        resourceNames = [os.path.basename(resourcePath) for resourcePath in resources]
        create_package(dir, resourceNames, packageName, version)

    return published


def _format_bytes(size):
    """Return a human-readable byte count using binary units, e.g. "175.1 MB"."""
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            if unit == "B":
                return "{:.0f} B".format(value)
            return "{:.1f} {}".format(value, unit)
        value /= 1024


def create_release(resources, owner, repo, tag, title=None, notes=None, assets=None, dryRun=False):
    """Create a GitHub release from a set of published resource descriptors.

    This is the multi-resource counterpart to the hand-rolled `gh release create` step a workflow
    would otherwise run itself. It derives the asset list from the resources rather than requiring the
    caller to re-enumerate files, and it writes release notes summarizing each resource.

    Only descriptor paths are accepted, not in-memory frictionless.Resource objects: a Resource built
    in memory may have no known descriptor path, and the descriptor file is itself an asset that must
    be uploaded. Use prepare_release() to publish descriptors first; pass the same paths here.

    Parameters
    ----------
    resources : str or list of str
        Path(s) to resource descriptor files. A single path may be passed as a bare string.
    owner : str
        The GitHub organization or user that owns the repository.
    repo : str
        The repository name.
    tag : str
        The release tag, e.g. "v2026.7.22". Raises if a release with this tag already exists, since a
        tag may only be cut once: moving one would leave published descriptors pointing at bytes that
        changed underneath them.
    title : str
        Optional. The release title. Defaults to tag.
    notes : str
        Optional. Introductory text placed above the generated "## Resources" section of the release
        notes.
    assets : list of str
        Optional. Extra asset paths to upload alongside the ones derived from resources, e.g. a data
        package descriptor.
    dryRun : bool
        Optional. If True, run every preflight check except the tag-existence check, log the resolved
        asset list and notes, and return without creating a release or calling `gh` to check the tag.
        Defaults to False.

    Returns
    -------
    (list of str, str)
        The de-duplicated list of asset paths, and the rendered release notes. Returned in both the
        real and dry-run cases so callers and tests can inspect what was or would be sent.
    """
    import os
    import shutil
    import subprocess
    import frictionless
    from .frictionless import _is_url

    if isinstance(resources, str):
        resources = [resources]

    descriptors = []
    assetPaths = []
    for resourcePath in resources:
        resourceDir = os.path.dirname(resourcePath)
        descriptor = frictionless.Resource(resourcePath).to_dict()
        descriptors.append(descriptor)

        cache = descriptor.get("_cache")
        path = descriptor.get("path")
        if cache is not None:
            dataPath = os.path.join(resourceDir, cache)
        elif path is not None and not _is_url(path):
            dataPath = os.path.join(resourceDir, path)
        else:
            logger.error("Resource {} has no local data to upload: path is a URL and no _cache is recorded.".format(resourcePath))
            raise RuntimeError
        assetPaths.append(dataPath)
        assetPaths.append(resourcePath)

        schema = descriptor.get("schema")
        if isinstance(schema, str) and not _is_url(schema):
            assetPaths.append(os.path.join(resourceDir, schema))

    if assets:
        assetPaths.extend(assets)

    seen = set()
    dedupedAssets = []
    for assetPath in assetPaths:
        key = os.path.abspath(assetPath)
        if key not in seen:
            seen.add(key)
            dedupedAssets.append(assetPath)

    lines = []
    if notes is not None:
        lines.append(notes)
        lines.append("")
    lines.append("## Resources")
    lines.append("")
    for descriptor in descriptors:
        name = descriptor.get("name")
        resourceTitle = descriptor.get("title", name)
        lines.append("- **{}** (`{}`)".format(resourceTitle, name))
        description = descriptor.get("description")
        if description:
            lines.append("  {}".format(description))
        sizeBytes = descriptor.get("bytes")
        hashValue = descriptor.get("hash")
        detailParts = []
        if sizeBytes is not None:
            detailParts.append("{} ({:,} bytes)".format(_format_bytes(sizeBytes), sizeBytes))
        if hashValue is not None:
            detailParts.append("`{}`".format(hashValue))
        if detailParts:
            lines.append("  {}".format(" — ".join(detailParts)))
    lines.append("")
    lines.append("Load with `morpc.frictionless.load_data()` against the resource descriptor attached to this release.")
    releaseNotes = "\n".join(lines)

    releaseTitle = title if title is not None else tag

    if shutil.which("gh") is None:
        logger.error("The gh CLI is required to create a GitHub release but was not found on PATH.")
        raise RuntimeError

    for assetPath in dedupedAssets:
        if not os.path.exists(assetPath):
            logger.error("Asset {} does not exist.".format(assetPath))
            raise RuntimeError

    if not dryRun:
        result = subprocess.run(["gh", "release", "view", tag, "--repo", "{}/{}".format(owner, repo)], capture_output=True)
        if result.returncode == 0:
            logger.error("Release {} already exists in {}/{}. A tag may only be cut once.".format(tag, owner, repo))
            raise RuntimeError

    if dryRun:
        logger.info("Dry run. Assets: {}".format(dedupedAssets))
        logger.info("Dry run. Notes:\n{}".format(releaseNotes))
        return dedupedAssets, releaseNotes

    subprocess.run(["gh", "release", "create", tag, "--repo", "{}/{}".format(owner, repo),
                     "--title", releaseTitle, "--notes", releaseNotes, *dedupedAssets], check=True)

    return dedupedAssets, releaseNotes
