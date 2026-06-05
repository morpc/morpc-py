# morpc-py/morpc/rest_api/rest_api.py

"""REST API module for MORPC.
This module provides tools to interact with ArcGIS REST API services,
including fetching data, schema introspection, and creating frictionless resources.
"""

import logging
import re
import urllib.parse
from json import JSONDecodeError

import attrs
import frictionless
from frictionless.dialect import Control
from requests import HTTPError

from morpc.req import get_json_safely

logger = logging.getLogger(__name__)

ESRI_TYPE_MAP = {
    'oid':          'string',
    'globalid':     'string',
    'guid':         'string',
    'string':       'string',
    'xml':          'string',
    'blob':         'string',
    'raster':       'string',
    'integer':      'integer',
    'smallinteger': 'integer',
    'double':       'number',
    'single':       'number',
    'date':         'datetime',
}


class ArcGISSchema(frictionless.Schema):
    """A frictionless Schema built from an ArcGIS REST service field list."""

    @classmethod
    def from_url(cls, url, outfields=None):
        """Fetch field definitions from an ArcGIS REST service and return an ArcGISSchema.

        Parameters
        ----------
        url : str
            Base URL of the ArcGIS REST service.
        outfields : str, optional
            Comma-separated field names to include, or '*' / None for all fields.
        """
        logger.info(f"Fetching schema metadata from {url}?f=pjson")
        pjson = get_json_safely(f"{url}?f=pjson")

        requested = None if outfields in (None, '*') else set(outfields.split(','))

        fields = []
        for field in pjson['fields']:
            if requested is not None and field['name'] not in requested:
                continue
            esri_type = field['type'].replace('esriFieldType', '').lower()
            if esri_type == 'geometry':
                continue
            frictionless_type = ESRI_TYPE_MAP.get(esri_type)
            if frictionless_type is None:
                logger.warning(f"Unknown ESRI type '{esri_type}' for field '{field['name']}', defaulting to 'string'")
                frictionless_type = 'string'
            fields.append({'name': field['name'], 'title': field['alias'], 'type': frictionless_type})

        return cls({'fields': fields})


@attrs.define(kw_only=True, repr=False)
class ArcGISControl(Control):
    """Control for ArcGIS REST API query parameters and service pagination metadata."""

    type = "arcgis"

    total_records: int = 0
    max_record_count: int = 500
    query: dict = attrs.Factory(dict)

    metadata_profile_patch = {
        "properties": {
            "totalRecords": {"type": "integer"},
            "maxRecordCount": {"type": "integer"},
            "query": {"type": "object"},
        }
    }


class ArcGISPlugin(frictionless.Plugin):
    """Frictionless plugin that registers ArcGIS classes for type='arcgis'."""

    def select_resource_class(self, type=None, *, datatype=None):
        if type == "arcgis":
            return ArcGISResource

    def select_control_class(self, type=None):
        if type == "arcgis":
            return ArcGISControl


frictionless.system.register("arcgis", ArcGISPlugin())


class ArcGISResource(frictionless.Resource):
    """A frictionless Resource representing an ArcGIS REST API service.

    Construct from an existing descriptor or resource file using the inherited
    frictionless.Resource interface, or use from_url() to fetch metadata from
    a live ArcGIS REST service.
    """

    type = "arcgis"

    @classmethod
    def from_url(cls, name, url, where='1=1', outfields='*', max_record_count=None, **kwargs):
        """Create an ArcGISResource by fetching metadata from an ArcGIS REST service URL.

        Parameters
        ----------
        name : str
            Human-readable name; converted to a valid resource slug.
        url : str
            Base URL of the ArcGIS REST service (without /query).
        where : str, optional
            SQL WHERE clause to filter records. Default '1=1' returns all.
        outfields : str, optional
            Comma-separated field names, or '*' for all fields.
        max_record_count : int, optional
            Records per paginated request. Fetched from the service if omitted;
            falls back to 500 if the service does not advertise a limit.
        **kwargs
            Additional ArcGIS query parameters (e.g. orderByFields).
        """
        query = {
            'where': where,
            'outFields': outfields,
            'returnGeometry': 'true',
            'f': 'geojson',
            **kwargs,
        }

        logger.info(f"Query Params: {[f'{k}={v}' for k, v in query.items()]}")

        try:
            total_record_count = _total_record_count(url, **query)
        except HTTPError as e:
            logger.error(f"Failed to get total record count, HTTPError: {e}")
            raise

        logger.info(f"Total number of geographies: {total_record_count}")

        if max_record_count is None:
            try:
                max_record_count = _max_record_count(url)
            except (ValueError, KeyError):
                logger.warning("Unable to find maxRecordCount. Using default.")
                max_record_count = min(total_record_count, 500)
            logger.info(f"Fetching {max_record_count} at a time.")

        control = ArcGISControl(
            total_records=total_record_count,
            max_record_count=max_record_count,
            query={
                'where': where,
                'outFields': outfields,
                **kwargs,
            },
        )
        dialect = frictionless.Dialect(controls=[control])

        descriptor = {
            "name": re.sub(r'[:/_ ]', '-', name).lower(),
            "type": "arcgis",
            "format": "json",
            "path": url,
            "schema": ArcGISSchema.from_url(url, outfields=outfields).to_descriptor(),
            "mediatype": "application/geo+json",
            "dialect": dialect.to_descriptor(),
        }

        return cls(descriptor)

    def to_geodataframe(self, out_fields: list[str] | None = None, CRS='epsg:4326', show_progress: bool = True):
        """Fetch all features from the ArcGIS service as a GeoDataFrame.

        Parameters
        ----------
        out_fields : list[str], optional
            Subset of fields to include. Must be present in the resource schema.
        CRS : str, optional
            Coordinate reference system for the output GeoDataFrame.
        """
        import enlighten
        import geopandas as gpd
        import pandas as pd
        from requests import Session
        from time import sleep

        headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}

        if out_fields is not None:
            for field in out_fields:
                if field not in self.schema.field_names:
                    logger.error(f"field {field} not in resource fields: {self.schema.field_names}")
                    raise ValueError(f"field {field} not in resource fields")

        control = ArcGISControl.from_dialect(self.dialect)

        urls = []
        for offset in range(0, control.total_records, control.max_record_count):
            params = {
                **control.query,
                'returnGeometry': 'true',
                'f': 'geojson',
                'resultRecordCount': control.max_record_count,
                'resultOffset': offset,
            }
            if out_fields is not None:
                params['outFields'] = ",".join(out_fields)
            urls.append(f"{self.path}/query?" + urllib.parse.urlencode(params, safe="=(),"))

        gdfs = []
        with Session() as session:
            with enlighten.Manager() as manager:
                pb = manager.counter(total=len(urls), desc='Downloading:', unit='requests') if show_progress else None
                for url in urls:
                    logger.debug(f"Fetching {url}")
                    r = session.get(url)
                    while r.status_code != 200:
                        logger.warning(f"Status Code {r.status_code}, trying again. URL: {r.url}")
                        if r.status_code == 400 and "Output format not supported" in r.text:
                            url = url.replace('geojson', 'json').replace('&returnGeometry=true', '')
                            logger.warning(f"Output format not supported, trying json. {url}")
                        sleep(1)
                        r = session.get(url, headers=headers)

                    try:
                        json_data = r.json()
                    except JSONDecodeError:
                        logger.error(f"Failed to decode json. {r.content}")
                        raise

                    try:
                        gdf = gpd.GeoDataFrame.from_features(json_data)
                    except Exception as e:
                        logger.error(f"Failed to create GeoDataFrame. {e}")
                        logger.error(f"{r.url}")
                        logger.error(f"{json_data}")
                        raise RuntimeError(f"Failed to create GeoDataFrame: {e}")

                    gdfs.append(gdf)
                    if pb is not None:
                        pb.update()

        gdf = pd.concat(gdfs)
        if len(gdf) != control.total_records:
            logger.error(f"Record count mismatch. Expected {control.total_records}, got {len(gdf)}")

        return gdf.set_crs(CRS)


def _schema(url, outfields=None):
    """Fetch field definitions from an ArcGIS REST service and return a descriptor dict."""
    return ArcGISSchema.from_url(url, outfields=outfields).to_descriptor()


def _total_record_count(url, **kwargs):
    """Fetch the total record count from an ArcGIS REST service."""
    logger.info("Requesting total record count")

    params = {**kwargs, 'returnCountOnly': 'true'}

    try:
        json_data = get_json_safely(f"{url}/query/", params=params)
    except HTTPError:
        try:
            logger.warning("geoJSON not supported, trying JSON...")
            params['f'] = 'json'
            json_data = get_json_safely(f"{url}/query/", params=params)
        except HTTPError as e:
            logger.error(f"HTTPError: {e}")
            raise

    import re
    total_count = int(re.findall(r'[0-9]+', str(json_data))[0])
    logger.info(f"Total records: {total_count}")
    return total_count


def _max_record_count(url):
    """Fetch the maxRecordCount from an ArcGIS REST service."""
    logger.info("Requesting max record count")

    try:
        json_data, fetched_url = get_json_safely(f"{url}?f=pjson", returnurl=True)
        max_record_count = json_data['maxRecordCount']
    except ValueError:
        logger.error("Could not find maxRecordCount in response.")
        raise
    except KeyError:
        logger.error(f"maxRecordCount not in response: {fetched_url}")
        raise

    logger.info(f"Max record count: {max_record_count}")
    return max_record_count


# Backward-compatible module-level functions

def resource(name, url, where='1=1', outfields='*', max_record_count=None, **kwargs):
    """Deprecated: use ArcGISResource.from_url() instead."""
    return ArcGISResource.from_url(name, url, where=where, outfields=outfields, max_record_count=max_record_count, **kwargs)

def gdf_from_resource(resource, out_fields: list[str] | None = None, CRS='epsg:4326'):
    """Deprecated: use ArcGISResource.to_geodataframe() instead."""
    if isinstance(resource, str):
        resource = ArcGISResource(resource)
    return resource.to_geodataframe(out_fields=out_fields, CRS=CRS)

def schema(url, outfields=None):
    """Deprecated: use morpc.rest_api._schema() instead."""
    return _schema(url, outfields=outfields)

def totalRecordCount(url, **kwargs):
    """Deprecated: use morpc.rest_api._total_record_count() instead."""
    return _total_record_count(url, **kwargs)

def maxRecordCount(url):
    """Deprecated: use morpc.rest_api._max_record_count() instead."""
    return _max_record_count(url)
