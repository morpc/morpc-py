# morpc-py/morpc/osm/osm.py

"""OpenStreetMap module for MORPC.

This module wraps osmnx/Overpass queries behind a scope (polygon, place name, or
bounding box) plus a tag filter, in the same spirit as morpc.rest_api wraps ArcGIS
REST queries. A single request to the public Overpass API can fail because the area
requested is too large for the server to answer, or because the mirror itself is
temporarily overloaded regardless of query size; fetch_osm_features() copes with both
by splitting an oversized request into smaller tiles and, failing that, falling back to
an alternate public Overpass mirror.

OsmResource/OsmControl/OsmPlugin register a "osm" Frictionless resource type, mirroring
morpc.rest_api.ArcGISResource: a resource documents a scope + tag query rather than a
literal file, and calling to_geodataframe() replays that query live against Overpass.
Overpass exposes no field metadata the way an ArcGIS REST service does, so OsmSchema
infers a schema from whichever tag columns are actually present in a fetched response,
rather than from a hand-written schema file.

Where fetch_osm_features() reports the current contents of the map, fetch_changesets()
reports recent editing activity: given the same kind of scope plus a date window, it
lists the OSM changesets touching that area through the OSMCha web API, and
summarize_changesets() rolls that list into a time series for monitoring a region.
"""

import json
import logging
import os
import re
import time

import attrs
import frictionless
import geopandas as gpd
import pandas as pd
import requests
import shapely
from frictionless.dialect import Control

logger = logging.getLogger(__name__)

# Public Overpass mirrors to try, in order, when a query keeps failing even at the
# smallest tile size. overpass-api.de is the busiest of the public mirrors and the one
# most likely to be temporarily overloaded (returning 504s or resetting connections);
# the others are independently-run public instances offering the same API.
DEFAULT_OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api",
    "https://overpass.kumi.systems/api",
    "https://overpass.private.coffee/api",
]

# How many times a request's area may be halved in each direction when it is too large
# for Overpass to answer. Each level of depth splits one request into four, so depth 4
# permits up to 256 tiles for a single query.
DEFAULT_MAX_SPLIT_DEPTH = 4

# Seconds to allow a single Overpass request before giving up on it.
DEFAULT_TIMEOUT = 900

# OSMCha web API, used by fetch_changesets() to list changesets by geometry and date.
# This is the API behind osmcha.org, not the osmcha PyPI package (which analyses one
# changeset at a time from replication files). A free token is required: log in at
# https://osmcha.org with an OSM account and copy the API token from the account page.
DEFAULT_OSMCHA_API = "https://osmcha.org/api/v1"

# Changesets whose bounding box is larger than this many square degrees are dropped by
# default. Continent-scale mechanical edits intersect any region of interest without
# saying anything about it; this is OSMCha's own knob for excluding them.
DEFAULT_OSMCHA_AREA_LT = 2.0


def _which_scope(polygon, place, bbox):
    """Return which of polygon/place/bbox was given. Raises if it is not exactly one."""
    given = [name for name, value in (("polygon", polygon), ("place", place), ("bbox", bbox)) if value is not None]
    if len(given) != 1:
        logger.error(f"Exactly one of polygon, place, or bbox must be given. Received: {given}")
        raise ValueError("Exactly one of polygon, place, or bbox must be given.")
    return given[0]


def _resolve_scope(polygon=None, place=None, bbox=None):
    """Return a single shapely (Multi)Polygon to query against, regardless of scope kind.

    Normalizing all three scope kinds to one geometry up front lets the split-retry
    engine below serve all of them through a single code path.
    """
    import osmnx as ox

    kind = _which_scope(polygon, place, bbox)
    if kind == "polygon":
        return polygon
    if kind == "bbox":
        return shapely.geometry.box(*bbox)

    boundary = ox.geocode_to_gdf(place)
    return boundary.union_all()


def _describe_scope(polygon=None, place=None, bbox=None):
    """Return (scope_type, scope) in a form that round-trips through a Resource descriptor."""
    kind = _which_scope(polygon, place, bbox)
    if kind == "polygon":
        return "polygon", shapely.geometry.mapping(polygon)
    if kind == "bbox":
        return "bbox", list(bbox)
    return "place", place


def _reconstruct_scope(scope_type, scope):
    """Return (polygon, place, bbox) kwargs for fetch_osm_features from a stored scope descriptor."""
    if scope_type == "polygon":
        return shapely.geometry.shape(scope), None, None
    if scope_type == "bbox":
        return None, None, tuple(scope)
    if scope_type == "place":
        return None, scope, None

    logger.error(f"Unknown scope_type '{scope_type}'.")
    raise ValueError(f"Unknown scope_type '{scope_type}'.")


def _quarter_polygon(polygon):
    """Split `polygon` into its four bounding-box quadrants, dropping any that it does not reach."""
    minx, miny, maxx, maxy = polygon.bounds
    midx, midy = (minx + maxx) / 2, (miny + maxy) / 2
    quadrants = [
        shapely.geometry.box(minx, miny, midx, midy),
        shapely.geometry.box(midx, miny, maxx, midy),
        shapely.geometry.box(minx, midy, midx, maxy),
        shapely.geometry.box(midx, midy, maxx, maxy),
    ]
    parts = [polygon.intersection(q) for q in quadrants]
    return [p for p in parts if not p.is_empty]


def _fetch_with_splitting(polygon, tags, label, max_split_depth, depth=0):
    """Fetch every feature within `polygon`, splitting the request when it is too large.

    A single query covering a large area can exceed what the public Overpass API will
    return; Overpass signals this by timing out or returning an error status rather
    than by returning partial data. This treats a failed request as a signal to ask for
    less: it splits the area into quadrants and retries each one, recursing until the
    request succeeds or max_split_depth is reached. Splitting is done only when needed,
    so a scope small enough to answer in one request still costs exactly one request.

    A feature straddling a tile boundary is returned by every tile it touches; the
    caller is responsible for de-duplicating on OSM element identity if that matters.
    """
    import pandas as pd
    import osmnx as ox
    from osmnx._errors import InsufficientResponseError, ResponseStatusCodeError

    indent = "  " * depth
    try:
        logger.info(f"{indent}Requesting features for {label}")
        gdf = ox.features_from_polygon(polygon, tags=tags)
        logger.info(f"{indent}{label}: {len(gdf):,} features returned")
        return gdf

    except InsufficientResponseError:
        # Overpass answered, and the answer is that there is nothing here. This is a
        # legitimate result, not a failure, so it must not trigger a split.
        logger.info(f"{indent}{label}: no features found")
        return gpd.GeoDataFrame(geometry=[], crs="epsg:4326")

    except (ResponseStatusCodeError, TimeoutError, OSError) as error:
        # The request was too big, or the server declined it. Ask for less.
        if depth >= max_split_depth:
            logger.error(
                f"{indent}{label}: still failing at maximum split depth {max_split_depth}. "
                f"Increase max_split_depth or retry later. Underlying error: {error}"
            )
            raise

        parts = _quarter_polygon(polygon)
        logger.warning(
            f"{indent}{label}: request failed ({type(error).__name__}), splitting into "
            f"{len(parts)} tiles and retrying. Underlying error: {error}"
        )
        results = [
            _fetch_with_splitting(part, tags, f"{label}.{i + 1}", max_split_depth, depth=depth + 1)
            for i, part in enumerate(parts)
        ]
        results = [r for r in results if len(r) > 0]
        if not results:
            return gpd.GeoDataFrame(geometry=[], crs="epsg:4326")
        return pd.concat(results)


def _fetch_with_fallback(polygon, tags, label, overpass_endpoints, max_split_depth, timeout):
    """Fetch `label`'s features, falling back to the next Overpass mirror if the current
    mirror keeps failing.

    _fetch_with_splitting already copes with a request that is too large by splitting
    it into smaller tiles. That does not help when the mirror itself is the problem --
    overloaded or otherwise returning errors regardless of query size -- so this only
    moves to the next mirror once a mirror has failed even at max_split_depth. A working
    first mirror never triggers this at all.
    """
    import osmnx as ox
    from osmnx._errors import ResponseStatusCodeError

    ox.settings.requests_timeout = timeout
    ox.settings.overpass_rate_limit = True

    lastError = None
    for i, endpoint in enumerate(overpass_endpoints):
        if i > 0:
            logger.warning(f"{label}: switching to Overpass mirror {endpoint} after the previous mirror failed")
        ox.settings.overpass_url = endpoint
        try:
            return _fetch_with_splitting(polygon, tags, label, max_split_depth)
        except (ResponseStatusCodeError, TimeoutError, OSError) as error:
            lastError = error

    logger.error(f"{label}: every configured Overpass mirror failed. Underlying error: {lastError}")
    raise lastError


def fetch_osm_features(
    tags,
    polygon=None,
    place=None,
    bbox=None,
    label=None,
    overpass_endpoints=None,
    max_split_depth=DEFAULT_MAX_SPLIT_DEPTH,
    timeout=DEFAULT_TIMEOUT,
    archive_dir=None,
    name=None,
    version=None,
):
    """Fetch OSM features matching `tags` within a scope, optionally archiving the result.

    Exactly one of polygon, place, or bbox must be given to define the query's scope.
    The request is retried against progressively smaller tiles if the scope is too
    large for Overpass to answer in one response, and falls back to an alternate public
    Overpass mirror if a mirror keeps failing even at the smallest tile size.

    Parameters
    ----------
    tags : dict
        OSM tag filter passed to osmnx, e.g. {"building": True}. See
        osmnx.features_from_polygon for the accepted forms.
    polygon : shapely Polygon or MultiPolygon, optional
        Area to query, in EPSG:4326.
    place : str or dict, optional
        Place name or structured Nominatim query to geocode and query, e.g.
        "Franklin County, Ohio".
    bbox : tuple of float, optional
        Bounding box as (left, bottom, right, top) in EPSG:4326.
    label : str, optional
        Human-readable name for the query, used in log messages to make split/fallback
        retries legible. Defaults to `name`, or "query" if neither is given.
    overpass_endpoints : list of str, optional
        Overpass mirrors to try, in order. Defaults to DEFAULT_OVERPASS_ENDPOINTS.
    max_split_depth : int, optional
        How many times the scope may be halved in each direction before giving up.
        Defaults to DEFAULT_MAX_SPLIT_DEPTH.
    timeout : int, optional
        Seconds to allow a single Overpass request before giving up on it. Defaults to
        DEFAULT_TIMEOUT.
    archive_dir : str, optional
        If given, write the fetched features to `{archive_dir}/{name}.gpkg`, along with
        a schema inferred from the response, an OsmResource documenting the live query
        that produced it, a GpkgResource documenting the archived copy, and a single
        `{name}.package.yaml` bundling both inline. Requires `name`.
    name : str, optional
        Base name for the archived files. Required if archive_dir is given.
    version : str, optional
        Version for the archived package. Defaults to morpc.frictionless.calver() if
        omitted.

    Returns
    -------
    geopandas.GeoDataFrame
        The fetched features.
    """
    overpass_endpoints = overpass_endpoints or DEFAULT_OVERPASS_ENDPOINTS
    label = label or name or "query"

    scope_geometry = _resolve_scope(polygon=polygon, place=place, bbox=bbox)
    gdf = _fetch_with_fallback(scope_geometry, tags, label, overpass_endpoints, max_split_depth, timeout)

    if archive_dir is not None:
        if name is None:
            logger.error("name is required when archive_dir is given.")
            raise ValueError("name is required when archive_dir is given.")
        _archive_features(
            gdf,
            tags,
            polygon=polygon,
            place=place,
            bbox=bbox,
            overpass_endpoints=overpass_endpoints,
            max_split_depth=max_split_depth,
            archive_dir=archive_dir,
            name=name,
            version=version,
        )

    return gdf


def _archive_features(gdf, tags, polygon, place, bbox, overpass_endpoints, max_split_depth, archive_dir, name, version):
    """Write `gdf` to a GeoPackage and a dense Frictionless package documenting it.

    The package bundles two inline resources: an OsmResource documenting the live
    Overpass query that produced the data, and a GpkgResource documenting the archived
    local copy -- so the package is self-describing about both provenance and storage.
    """
    from morpc.frictionless.frictionless import create_package, tempWorkingDirectory
    from morpc.frictionless.gpkg import create_gpkgresource
    from morpc.frictionless.release import calver

    os.makedirs(archive_dir, exist_ok=True)

    dataFileName = f"{name}.gpkg"
    schemaFileName = f"{name}.schema.yaml"

    schema = OsmSchema.from_geodataframe(gdf)

    with tempWorkingDirectory(archive_dir):
        gdf.to_file(dataFileName, driver="GPKG", layer=name)
        schema.to_yaml(schemaFileName)

        gpkgResource = create_gpkgresource(
            dataFileName,
            name,
            schemaPaths=schemaFileName,
            computeHash=True,
            computeBytes=True,
        )[0]

    osmResource = OsmResource.from_query(
        name,
        tags,
        polygon=polygon,
        place=place,
        bbox=bbox,
        overpass_endpoints=overpass_endpoints,
        max_split_depth=max_split_depth,
    )

    packageVersion = version if version is not None else calver()
    create_package(
        dir=archive_dir,
        resources=[osmResource, gpkgResource],
        name=name,
        version=packageVersion,
    )


# --- changeset monitoring -------------------------------------------------------------
#
# fetch_osm_features() answers "what is in the map here now". fetch_changesets() answers
# "what has been edited here lately": it lists the OSM changesets that touch a scope over
# a time window, with OSMCha's review metadata attached, and summarize_changesets() rolls
# that list into a time series suitable for monitoring a region.

# Changeset properties kept from each OSMCha feature. OSMCha returns many more fields;
# these are the ones that carry over to regional monitoring.
_CHANGESET_PROPERTIES = [
    "user", "uid", "date", "editor", "comment", "source",
    "create", "modify", "delete", "comments_count",
    "is_suspect", "harmful", "checked", "check_user", "check_date", "reasons",
]


def _osmcha_get(url, params, headers, max_retries=5, timeout=180):
    """GET `url`, retrying with exponential backoff on HTTP 429 and transient failures.

    OSMCha rate-limits fairly aggressively (a few hundred results per minute), so a
    backfill of any length will be throttled at least once. It also serves a large
    geometry-and-date query slowly enough to time out or drop the connection now and
    then. Both are transient, so both are retried rather than raised.
    """
    delay = 10
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=timeout)
        except requests.exceptions.RequestException as exc:
            if attempt == max_retries:
                raise
            logger.warning(
                f"OSMCha request failed ({type(exc).__name__}); "
                f"retrying in {delay}s (attempt {attempt + 1}/{max_retries})."
            )
            time.sleep(delay)
            delay *= 2
            continue
        if response.status_code != 429 or attempt == max_retries:
            return response
        wait = int(response.headers.get("Retry-After", delay))
        logger.warning(f"OSMCha rate limited (429); waiting {wait}s (attempt {attempt + 1}/{max_retries}).")
        time.sleep(wait)
        delay *= 2
    return response


def _changesets_to_gdf(features):
    """Turn a list of OSMCha GeoJSON changeset features into a typed GeoDataFrame."""
    rows = []
    geometries = []
    for feature in features:
        properties = feature.get("properties", {})
        row = {key: properties.get(key) for key in _CHANGESET_PROPERTIES}
        # OSMCha reports the changeset id at the GeoJSON feature level, not in properties.
        row["id"] = feature.get("id", properties.get("id"))
        rows.append(row)
        geometries.append(shapely.geometry.shape(feature["geometry"]) if feature.get("geometry") else None)

    gdf = gpd.GeoDataFrame(rows, geometry=geometries, crs="EPSG:4326")
    if gdf.empty:
        return gdf

    gdf["date"] = pd.to_datetime(gdf["date"], utc=True, errors="coerce")
    gdf["check_date"] = pd.to_datetime(gdf["check_date"], utc=True, errors="coerce")
    for column in ("id", "uid", "create", "modify", "delete", "comments_count"):
        gdf[column] = pd.to_numeric(gdf[column], errors="coerce")
    gdf["edits"] = gdf[["create", "modify", "delete"]].sum(axis=1)
    return gdf


def _fetch_changeset_features(url, params, headers, max_pages):
    """Page through one OSMCha changeset query and return the raw feature list."""
    features = []
    for page in range(1, max_pages + 1):
        response = _osmcha_get(url, {**params, "page": page}, headers)
        if response.status_code == 404:
            break  # paged past the last result
        response.raise_for_status()
        payload = response.json()
        page_features = payload.get("features", [])
        features.extend(page_features)
        logger.info(f"OSMCha page {page}: {len(page_features)} changesets (total {len(features)}).")
        if not payload.get("next"):
            break
        time.sleep(2)  # be gentle with a shared service
    else:
        logger.warning(f"fetch_changesets hit max_pages={max_pages}; results may be truncated.")
    return features


def _date_chunks(start, end, chunk_days):
    """Yield (gte, lte) date-string pairs covering [start, end] in <= chunk_days steps.

    Chunk boundaries overlap by a day because OSMCha's date filter is inclusive on both
    ends; the caller deduplicates by changeset id.
    """
    start = pd.Timestamp(start).normalize()
    end = pd.Timestamp(end).normalize()
    step = pd.Timedelta(days=chunk_days)
    left = start
    while left <= end:
        right = min(left + step, end)
        yield left.strftime("%Y-%m-%d"), right.strftime("%Y-%m-%d")
        left = right + pd.Timedelta(days=1)


def fetch_changesets(
    polygon=None,
    place=None,
    bbox=None,
    start=None,
    end=None,
    token=None,
    area_lt=DEFAULT_OSMCHA_AREA_LT,
    only_suspect=False,
    endpoint=DEFAULT_OSMCHA_API,
    page_size=100,
    max_pages=200,
    chunk_days=30,
):
    """List the OSM changesets intersecting a scope within a date window, via OSMCha.

    Exactly one of polygon, place, or bbox must be given to define the scope, the same
    way as fetch_osm_features(). Every changeset OSMCha reports for that scope and date
    range is returned as one row, with its bounding box as the geometry.

    Parameters
    ----------
    polygon : shapely Polygon or MultiPolygon, optional
        Area to query, in EPSG:4326.
    place : str or dict, optional
        Place name or structured Nominatim query to geocode and query, e.g.
        "Franklin County, Ohio".
    bbox : tuple of float, optional
        Bounding box as (left, bottom, right, top) in EPSG:4326.
    start, end : str or datetime, optional
        Inclusive bounds on changeset creation date, anything pandas can parse to a
        timestamp. OSMCha compares against the date only. An open end is allowed.
    token : str, optional
        OSMCha API token. Defaults to the OSMCHA_TOKEN environment variable.
    area_lt : float or None, optional
        Drop changesets whose bounding box is larger than this many square degrees.
        Defaults to DEFAULT_OSMCHA_AREA_LT. Pass None to keep every changeset.
    only_suspect : bool, optional
        Ask OSMCha for flagged changesets only. Defaults to False.
    endpoint : str, optional
        OSMCha API base URL. Defaults to DEFAULT_OSMCHA_API.
    page_size : int, optional
        Changesets per request, capped at 100 by OSMCha. Defaults to 100.
    max_pages : int, optional
        Stop after this many pages as a runaway guard, per date chunk. Defaults to 200.
    chunk_days : int, optional
        Split the date range into windows of at most this many days and query each
        separately. OSMCha answers a narrow date range quickly but can time out on a
        wide one, so a long history is fetched as a series of short queries and
        concatenated. Defaults to 30. Only applies when both start and end are given.

    Returns
    -------
    geopandas.GeoDataFrame
        One row per changeset: id, user, uid, date, editor, comment, source,
        create/modify/delete, edits, comments_count, is_suspect, harmful, checked,
        check_user, check_date, reasons, plus the changeset bounding box as geometry.
        Empty if nothing matched.
    """
    token = token or os.environ.get("OSMCHA_TOKEN")
    if not token:
        logger.error("An OSMCha API token is required. Pass token= or set OSMCHA_TOKEN.")
        raise ValueError("An OSMCha API token is required. Pass token= or set OSMCHA_TOKEN.")

    scope_geometry = _resolve_scope(polygon=polygon, place=place, bbox=bbox)

    params = {
        "geometry": json.dumps(shapely.geometry.mapping(scope_geometry)),
        "page_size": min(page_size, 100),
    }
    if area_lt is not None:
        params["area_lt"] = area_lt
    if only_suspect:
        params["is_suspect"] = "True"

    headers = {"Authorization": f"Token {token}"}
    url = f"{endpoint}/changesets/"

    if start is not None and end is not None:
        windows = list(_date_chunks(start, end, chunk_days))
    else:
        window = {}
        if start is not None:
            window["date__gte"] = pd.Timestamp(start).strftime("%Y-%m-%d")
        if end is not None:
            window["date__lte"] = pd.Timestamp(end).strftime("%Y-%m-%d")
        windows = [(window.get("date__gte"), window.get("date__lte"))]

    features = []
    for i, (gte, lte) in enumerate(windows, start=1):
        window_params = dict(params)
        if gte is not None:
            window_params["date__gte"] = gte
        if lte is not None:
            window_params["date__lte"] = lte
        if len(windows) > 1:
            logger.info(f"OSMCha window {i}/{len(windows)}: {gte} to {lte}.")
        features.extend(_fetch_changeset_features(url, window_params, headers, max_pages))

    gdf = _changesets_to_gdf(features)
    if not gdf.empty:
        gdf = gdf.drop_duplicates(subset="id").reset_index(drop=True)
    return gdf


def summarize_changesets(changesets, freq="W"):
    """Roll a fetch_changesets() result into a time series for monitoring.

    Parameters
    ----------
    changesets : geopandas.GeoDataFrame
        A fetch_changesets() result.
    freq : str, optional
        pandas offset alias for the bucket size, e.g. "D", "W", "MS". Defaults to "W".

    Returns
    -------
    pandas.DataFrame
        Indexed by period start, with columns changeset_count, distinct_users,
        total_edits, suspect_count, harmful_count, reviewed_count. Empty if the input
        is empty.
    """
    if changesets.empty:
        return pd.DataFrame()

    grouped = changesets.set_index("date").groupby(pd.Grouper(freq=freq))
    return grouped.agg(
        changeset_count=("id", "count"),
        distinct_users=("uid", "nunique"),
        total_edits=("edits", "sum"),
        suspect_count=("is_suspect", "sum"),
        harmful_count=("harmful", lambda s: s.fillna(False).astype(bool).sum()),
        reviewed_count=("checked", "sum"),
    )


class OsmSchema(frictionless.Schema):
    """A frictionless Schema built from the tag columns present in a fetched GeoDataFrame.

    Overpass exposes no field metadata to build a schema from ahead of a fetch, unlike
    an ArcGIS REST service (see morpc.rest_api.ArcGISSchema.from_url()), so this infers
    the schema after the fact from whatever tag columns actually came back. Every field
    is typed "string": OSM tags are free text, and this module does not interpret them
    the way a downstream standardization workflow would.
    """

    @classmethod
    def from_geodataframe(cls, gdf):
        geometryColumn = gdf.geometry.name
        fields = [{"name": column, "type": "string"} for column in gdf.columns if column != geometryColumn]
        return cls({"fields": fields})


@attrs.define(kw_only=True, repr=False)
class OsmControl(Control):
    """Control identifying the scope and tag query an OsmResource describes."""

    type = "osm"

    tags: dict = attrs.Factory(dict)
    scope_type: str = "polygon"
    scope: object = attrs.Factory(dict)
    overpass_endpoints: list = attrs.Factory(list)
    max_split_depth: int = DEFAULT_MAX_SPLIT_DEPTH

    metadata_profile_patch = {
        "properties": {
            "tags": {"type": "object"},
            "scopeType": {"type": "string"},
            "scope": {},
            "overpassEndpoints": {"type": "array"},
            "maxSplitDepth": {"type": "integer"},
        }
    }


class OsmPlugin(frictionless.Plugin):
    """Frictionless plugin that registers OsmResource/OsmControl for type='osm', and
    OsmQueryPackage for package type='osm-query'."""

    def select_resource_class(self, type=None, *, datatype=None):
        if type == "osm":
            return OsmResource

    def select_control_class(self, type=None):
        if type == "osm":
            return OsmControl

    def select_package_class(self, type=None):
        if type == "osm-query":
            return OsmQueryPackage


frictionless.system.register("osm", OsmPlugin())


class OsmResource(frictionless.Resource):
    """A frictionless Resource describing an OpenStreetMap Overpass query.

    Construct from an existing descriptor using the inherited frictionless.Resource
    interface, or use from_query() to describe a fresh scope + tag query. to_geodataframe()
    replays the stored query live against Overpass, the way morpc.rest_api.ArcGISResource
    replays its stored query against a live ArcGIS REST service.
    """

    type = "osm"

    @classmethod
    def from_query(
        cls,
        name,
        tags,
        polygon=None,
        place=None,
        bbox=None,
        overpass_endpoints=None,
        max_split_depth=DEFAULT_MAX_SPLIT_DEPTH,
    ):
        """Create an OsmResource describing a scope + tag query, without fetching it.

        Parameters
        ----------
        name : str
            Human-readable name; converted to a valid resource slug.
        tags : dict
            OSM tag filter, e.g. {"building": True}.
        polygon, place, bbox
            Exactly one must be given. See fetch_osm_features().
        overpass_endpoints : list of str, optional
            Overpass mirrors to try, in order. Defaults to DEFAULT_OVERPASS_ENDPOINTS.
        max_split_depth : int, optional
            Defaults to DEFAULT_MAX_SPLIT_DEPTH.
        """
        overpass_endpoints = overpass_endpoints or DEFAULT_OVERPASS_ENDPOINTS
        scope_type, scope = _describe_scope(polygon=polygon, place=place, bbox=bbox)

        control = OsmControl(
            tags=tags,
            scope_type=scope_type,
            scope=scope,
            overpass_endpoints=overpass_endpoints,
            max_split_depth=max_split_depth,
        )
        dialect = frictionless.Dialect(controls=[control])

        descriptor = {
            "name": re.sub(r"[:/_ ]", "-", name).lower(),
            "type": "osm",
            "format": "json",
            "path": f"{overpass_endpoints[0]}/interpreter",
            "mediatype": "application/json",
            "dialect": dialect.to_descriptor(),
        }

        return cls(descriptor)

    def to_geodataframe(self, timeout=DEFAULT_TIMEOUT):
        """Fetch this resource's query live from Overpass and return a GeoDataFrame.

        The schema is inferred from whichever tag columns are present in the response
        and attached to this resource, since Overpass exposes no field metadata to
        build one from ahead of time.
        """
        control = OsmControl.from_dialect(self.dialect)
        polygon, place, bbox = _reconstruct_scope(control.scope_type, control.scope)

        gdf = fetch_osm_features(
            control.tags,
            polygon=polygon,
            place=place,
            bbox=bbox,
            label=self.name,
            overpass_endpoints=control.overpass_endpoints,
            max_split_depth=control.max_split_depth,
            timeout=timeout,
        )
        self.schema = OsmSchema.from_geodataframe(gdf)
        return gdf


class OsmQueryPackage(frictionless.Package):
    """A Frictionless Package that documents an OSM/Overpass query without fetching or
    embedding any data -- a metadata snapshot of "what query would produce this input".

    Registers as a "osm-query" package type (see OsmPlugin.select_package_class), so
    loading a saved snapshot back with frictionless.Package(path) or OsmQueryPackage(path)
    returns an OsmQueryPackage, the same way a "gpkg"/"arcgis" resource round-trips to its
    own class -- provided morpc.osm has been imported to register the plugin. Without it,
    loading raises rather than silently degrading, the same tradeoff every other custom
    morpc Frictionless type (GpkgResource, ArcGISResource) already makes.

    The package holds exactly one resource: the OsmResource describing the query. Saving
    never fetches anything -- see save(). Actually running the query, optionally archiving
    the result, is the separate, explicit fetch().
    """

    type = "osm-query"

    @classmethod
    def from_query(
        cls,
        name,
        tags,
        polygon=None,
        place=None,
        bbox=None,
        overpass_endpoints=None,
        max_split_depth=DEFAULT_MAX_SPLIT_DEPTH,
        version=None,
        keywords=None,
    ):
        """Describe a scope + tag query as a package, without fetching it.

        Parameters
        ----------
        name : str
            Human-readable name; converted to a valid resource slug for the wrapped
            OsmResource, and used as-is for the package's own name.
        tags : dict
            OSM tag filter, e.g. {"building": True}.
        polygon, place, bbox
            Exactly one must be given. See fetch_osm_features().
        overpass_endpoints : list of str, optional
            Overpass mirrors to try, in order. Defaults to DEFAULT_OVERPASS_ENDPOINTS.
        max_split_depth : int, optional
            Defaults to DEFAULT_MAX_SPLIT_DEPTH.
        version : str, optional
            Package version. Defaults to morpc.frictionless.calver() if omitted.
        keywords : list of str, optional
            Package keywords.
        """
        import datetime

        from morpc.frictionless.release import calver

        resource = OsmResource.from_query(
            name,
            tags,
            polygon=polygon,
            place=place,
            bbox=bbox,
            overpass_endpoints=overpass_endpoints,
            max_split_depth=max_split_depth,
        )

        descriptor = {
            "name": resource.name,
            "type": "osm-query",
            "version": str(version) if version is not None else str(calver()),
            "created": datetime.datetime.now().isoformat(),
            "resources": [resource.to_dict()],
        }
        if keywords is not None:
            descriptor["keywords"] = keywords

        return cls(descriptor)

    def save(self, dir):
        """Write this package to `{dir}/{name}.package.yaml`. Never fetches or writes data.

        Returns
        -------
        str
            The path written.
        """
        path = os.path.join(dir, f"{self.name}.package.yaml")
        self.to_yaml(path)
        return path

    def fetch(self, archive_dir=None, timeout=DEFAULT_TIMEOUT, version=None):
        """Run the documented query live, optionally archiving the result.

        Delegates entirely to fetch_osm_features() using the scope, tags, and mirrors
        recorded in this package's OsmResource -- this is the one place that actually
        talks to Overpass. See fetch_osm_features() for the archiving behavior.

        Parameters
        ----------
        archive_dir : str, optional
            If given, archive the result there (gpkg + schema + a separate dense
            package documenting the fetched copy). See fetch_osm_features().
        timeout : int, optional
            Defaults to DEFAULT_TIMEOUT.
        version : str, optional
            Version for the archived package, if archive_dir is given. Defaults to
            morpc.frictionless.calver() if omitted.

        Returns
        -------
        geopandas.GeoDataFrame
        """
        control = OsmControl.from_dialect(self.resources[0].dialect)
        polygon, place, bbox = _reconstruct_scope(control.scope_type, control.scope)

        return fetch_osm_features(
            control.tags,
            polygon=polygon,
            place=place,
            bbox=bbox,
            label=self.name,
            overpass_endpoints=control.overpass_endpoints,
            max_split_depth=control.max_split_depth,
            timeout=timeout,
            archive_dir=archive_dir,
            name=self.name,
            version=version,
        )
