# morpc-py/morpc/rest_api/rest_api.py

"""REST API module for MORPC.
This module provides functions to interact with ArcGIS REST API services,
including fetching data, converting ESRI WKID to WKT2, and creating frictionless resources
from ArcGIS services.
"""

import itertools
from json import JSONDecodeError
import logging
from types import NoneType
from typing import List
import urllib.parse

from pandas import concat
from requests import HTTPError
import urllib
from morpc.req import get_json_safely

logger = logging.getLogger(__name__)

def resource(name, url, where='1=1', outfields='*', max_record_count=None):
    """Creates a frictionless Resource object from an ArcGIS REST API service URL.

    Parameters:
    ----------- 
    name : str
        The name of the resource, which will be used to create a valid resource name.
    
    url : str
        The URL of the ArcGIS REST API service. 

    where : str, optional
        A SQL-like query string to filter the results. Default is '1=1', which returns all records. 
    
    outfields : str, optional
        A comma-separated list of field names to include in the results. Default is '*', which
        includes all fields.
    
    max_record_count : int, optional
        The maximum number of records to fetch in a single request. If not provided, it defaults
        to 500 if the total record count exceeds 500, otherwise it uses the total record count.

    Returns:
    --------    
    resource : frictionless.Resource
        A frictionless Resource object containing the schema and metadata of the service.

    """
    import frictionless
    import re
    from morpc.rest_api import totalRecordCount, schema
    import urllib.parse
            
    # Construct the query parameters
    query = {
        'where': where, 
        'outFields': outfields, 
        'returnGeometry': 'true', 
        'f': 'geojson'
    }

    logger.info(f"Query Params: where = {where}, outFields = {outfields}")

    # Get the total record count
    try:
        total_record_count = totalRecordCount(url, where=where, outfields=outfields)
    except HTTPError as e:
        logger.error(f"Failed to get total record count, HTTPError: {e}")

    logger.info(f"Total number of geographies: {total_record_count}")
    
    # Determine the max record count
    if max_record_count is None:
        try:
            max_record_count = maxRecordCount(url)
        except ValueError as e:
            logger.warning(f"Unable to find maxRecordCount. Using default.")
            if total_record_count > 500:
                max_record_count = 500
            else:
                max_record_count = total_record_count
        logger.info(f"Fetching {max_record_count} at a time.")

    # Construct the frictionless Resource object
    resource = {
        "name": re.sub('[:/_ ]', '-', name).lower(),
        "format": "json",
        "path": url,
        "schema": schema(url, outfields=outfields),
        "mediatype": "application/geo+json",
        "_metadata": {
            "type": "arcgis_service",
            "params": query,
            "total_records": total_record_count,
            "max_record_count": max_record_count
        }
    }

    return frictionless.Resource(resource)

def gdf_from_resource(resource, out_fields: List[str] | None = None, CRS = 'epsg:4326'):
    """Creates a GeoDataFrame from resource file for an ArcGIS Services. Automatically queries for maxRecordCount and
    iterates over the whole feature layer to return all features. Optional: Filter the results by including a list of field
    IDs.

    Example Usage:

    Parameters:
    ------------
    resource : str
        A frictionless.Resource or path to the resource file, which can be a local file or a URL to an ArcGIS REST API service.

    out_fields : list[str]
        A list of strings representing the fields to include in the query.
    Returns:
    ----------
    gdf : pandas.core.frame.DataFrame
        A GeoPandas GeoDataframe constructed from the GeoJSON requested from the url.

    """

    from requests import Session
    import frictionless
    import enlighten
    import geopandas as gpd
    import pandas as pd
    from time import sleep


    headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}
    # Check if the resource is a string or a frictionless Resource object
    if isinstance(resource, str):
        # If it's a string, create a frictionless Resource object from the URL or file path
        resource = frictionless.Resource(path=resource)
    elif isinstance(resource, frictionless.Resource):
        # If it's already a Resource object, use it directly
        pass

    if not isinstance(out_fields, NoneType):
        for field in out_fields:
            if field not in resource.schema.field_names:
                logger.error(f"field {field} not in resource fields: {resource.schema.field_names}")
                raise ValueError

    metadata = resource.to_dict()['_metadata']

    offsets = [x for x in range(0, metadata['total_records'], metadata['max_record_count'])]

    # Construct URLS for each request based on offests
    urls = []
    for offset in offsets:
        url = resource.path
        params = metadata['params']
        if not isinstance(out_fields, NoneType):
            params.update({'outFields': ",".join(out_fields)})
        params.update({'resultRecordCount': metadata['max_record_count']})
        params.update({'resultOffset': offset})
        url = f"{resource.path}/query?" + urllib.parse.urlencode(params, safe=",()")
        urls.append(url)

    # Fetch the GeoJSON data in chunks via source urls constructed above
    gdfs = []
    with Session() as session:
        with enlighten.Manager() as manager: # Load progress bar
            with manager.counter(total=len(urls), desc='Downloading:', unit='requests') as pb:
                for url in urls:
                    logger.debug(f"Fetching {url}")
                    r = session.get(url)
                    while r.status_code != 200:
                        logger.warning(f"Status Code {r.status_code}, trying again. URL: {r.url}")
                        if r.status_code == 400:
                            if "Output format not supported" in r.text:
                                url = url.replace('geojson', 'json').replace('&returnGeometry=true','')
                                logger.warning(f"Output format not supported, trying json. {url}")
                        sleep(1)
                        r = session.get(url, headers=headers)

                    try:
                        json = r.json()
                    except JSONDecodeError as e:
                        logger.error(f"Failed to decode json. {r.content}")
                        raise JSONDecodeError(e)

                    try:
                        gdf = gpd.GeoDataFrame.from_features(json)
                    except Exception as e:
                        logger.error(f"Failed to create gdf. {e}")
                        logger.error(f"{r.url}")
                        logger.error(f"{json}")
                        raise RuntimeError

                    gdfs.append(gdf)
                    pb.update()

    gdf = pd.concat(gdfs)
    if len(gdf) != metadata['total_records']:
        logger.error(f"Number of records do not match. Expected {metadata['total_records']}, downloaded: {len(gdf)}")
    
    gdf = gdf.set_crs(CRS)

    return gdf

def schema(url, outfields=None):
    """Extracts the schema from a JSON object returned by an ArcGIS REST API service.

    Parameters:
    -----------
    url : str
        The URL of the ArcGIS REST API service.
    Returns:
    --------
    schema : dict
        A dictionary containing the schema of the fields in the service.
    """
    import frictionless
    import requests


        # Fetch the service metadata
    logger.info(f"Fetching metadata for schema from {url}?f=pjson")
    r = requests.get(f"{url}?f=pjson")
    pjson = r.json()
    r.close()

    schema = {}
    schema['fields'] = []
    if outfields == '*':
        for field in pjson['fields']:
            properties = {}
            properties['name'] = field['name']
            properties['title'] = field['alias']
            ftype = field['type'].replace('esriFieldType', '').lower()
            if ftype == 'oid':
                properties['type'] ='string'
            if ftype == 'double':
                properties['type'] ='number'
            if ftype == 'single':
                ftype ='number'
            if ftype == 'smallinteger':
                properties['type'] ='number'
            if ftype == 'geometry':
                continue # skip extra geometry columns
            schema['fields'].append(properties)
    else:
        for field in pjson['fields']:
            if field['name'] in outfields.split(','):
                properties = {}
                properties['name'] = field['name']
                properties['title'] = field['alias']
                ftype = field['type'].replace('esriFieldType', '').lower()
                if ftype == 'oid':
                    properties['type'] ='string'
                if ftype == 'double':
                    properties['type'] ='number'
                if ftype == 'single':
                    ftype ='number'
                if ftype == 'smallinteger':
                    properties['type'] ='number'
                if ftype == 'geometry':
                    continue # skip extra geometry columns
                schema['fields'].append(properties)

    return schema

def totalRecordCount(url, where, outfields='*'):
    """Fetches the total number of records from an ArcGIS REST API service.
    Parameters:
    -----------
    url : str
        The URL of the ArcGIS REST API service.
    Returns:
    --------    
    total_count : int
        The total number of records in the service.
    """
    import requests
    import re
    from morpc.req import get_json_safely

    # Find the total number of records
    logger.info(f"Requesting metadata for total record")

    # Create query for total record count
    url= f"{url}/query/"
    params = {
        "outfields": "*",
        "where": where,
        "f": "geojson",
        "returnCountOnly": "true"} ## Inlcude in paramters to return only the total records
    
    # Try to fetch it as a geojson
    try:
        json = get_json_safely(url, params = params)

    # If it errors, check if geojson is not supported and try json
    except HTTPError as e:
        try:
            logger.warning(f"geoJSON not supported, trying Json...")
            params['f'] = 'json'
            json = get_json_safely(url, params = params)
        except:
            logger.error(f"HTTPError: {e}")
            raise HTTPError

    total_count = int(re.findall('[0-9]+',str(json))[0])
    logger.info(f"Total records: {total_count}")

    return total_count

def maxRecordCount(url):
    """Fetches the total number of records from an ArcGIS REST API service.
    Parameters:
    -----------
    url : str
        The URL of the ArcGIS REST API service.
    Returns:
    --------    
    total_count : int
        The total number of records in the service.
    """

    from morpc.req import get_json_safely
    # Find the total number of records
    logger.info(f"Requesting metadata for max records in query")

    # Get properties json
    url= f"{url}?f=pjson"

    try:
        json, url = get_json_safely(url, returnurl=True)
        max_record_count = json['maxRecordCount']
    except ValueError as e:
        logger.error('Could not find maxRecordCount in json. revert to default value.')
        raise ValueError
    except KeyError as e:
        logger.error(f"maxRecordCount not in json: {url}")
    logger.info(f"Total records: {max_record_count}")


    return max_record_count

