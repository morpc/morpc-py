# morpc-py/morpc/rest_api/rest_api.py
"""REST API module for MORPC.
This module provides functions to interact with ArcGIS REST API services,
including fetching data, converting ESRI WKID to WKT2, and creating frictionless resources
from ArcGIS services.
"""


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

    Example:
    --------
    >>> resource = resource(
    ...     name = 'morpc-franklin-tracts',
    ...     url = 'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_ACS2024/MapServer/8',
    ...     where = "STATE = '39' and COUNTY = '049'",
    ...     outfields = '*',
    ...     max_record_count = 500
    ... )
    >>> print(resource.to_dict())

    """
    import frictionless
    import re
    from morpc.rest_api import totalRecordCount, schema
    import urllib.parse
    import requests
    

            
    # Construct the query parameters
    query = {
        'where': where, 
        'outFields': outfields, 
        'returnGeometry': 'true', 
        'f': 'geojson'
    }

    # Get the total record count
    total_record_count = totalRecordCount(url, where=where, outfields=outfields)
    
    # Determine the max record count
    if max_record_count is None:
        if total_record_count > 500:
            max_record_count = 500
        else:
            max_record_count = total_record_count

    # Get WKID from the properties of the service
    r = requests.get(f"{url}?f=pjson")
    pjson = r.json()
    r.close()

    if 'spatialReference' in pjson:
        wkid = pjson['spatialReference']['wkid']
    elif 'sourceSpatialReference' in pjson:
        wkid = pjson['sourceSpatialReference']['wkid']
    else:
        print("No spatial reference found in the service metadata. Using default WKID 4326.")
        wkid = 4326

    # Construct list of source urls to account for max record counts
    sources = []
    offsets = [x for x in range(0, total_record_count, max_record_count)]
    for i in range(len(offsets)):
        start = offsets[i]
        source = {
            "url": f"{url}/query?",
            "params": query
                }
        source['params']['resultOffset'] = start
        path = source['url'] + urllib.parse.urlencode(query)
        sources.append(path)

    # Construct the frictionless Resource object
    resource = {
        "name": re.sub('[:/_ ]', '-', name).lower(),
        "format": "json",
        "path": sources,
        "schema": schema(url),
        "mediatype": "application/geo+json",
        "_metadata": {
            "type": "arcgis_service",
            "params": query,
            "total_records": total_record_count,
            "wkid": wkid
        }
    }

    return frictionless.Resource(resource)

def query(resource, api_key=None, recordcount_override=None):
    """Creates a GeoDataFrame from resource file for an ArcGIS Services. Automatically queries for maxRecordCount and
    iterates over the whole feature layer to return all features. Optional: Filter the results by including a list of field
    IDs.

    Example Usage:

    Parameters:
    ------------
    resource : str
        The path to the resource file, which can be a local file or a URL to an ArcGIS REST API service.

    field_ids : list of str
        A list of strings that match field ids in the feature layer.

    api_key : str, optional
        An API key for accessing the ArcGIS REST API service. If not provided, the function will attempt to access the service without an API key.

    Returns:
    ----------
    gdf : pandas.core.frame.DataFrame
        A GeoPandas GeoDataframe constructed from the GeoJSON requested from the url.

    Raises:
    ---------
    RuntimeError: If the provided field_ids are not available in the resource.  

    Example:
    ---------
    >>> gdf = get("path/to/resource.json", 
                  field_ids=['OBJECTID', 'NAME'], 
                  api_key=get_api_key('path/to/api_key.txt'))
    """

    import requests
    import frictionless


    headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}
    # Check if the resource is a string or a frictionless Resource object
    if isinstance(resource, str):
        # If it's a string, create a frictionless Resource object from the URL or file path
        resource = frictionless.Resource(path=resource)
    elif isinstance(resource, frictionless.Resource):
        # If it's already a Resource object, use it directly
        pass    

    sources = resource.paths

    # Fetch the GeoJSON data in chunks via source urls constructed above
    features = []
    with requests.Session() as s:
        # Check if sources is None or empty
        if sources is None or len(sources) == 0:
            print("No sources found in the resource. Check the resource file or URL.")
            raise RuntimeError("No sources found in the resource. Check the resource file or URL.")\
        # If there is only one source, fetch it directly
        if len(sources) == 1:
            r = s.get(sources[0], headers=headers)
            # Check if the request was successful
            if r.status_code != 200:
                print(f"Error fetching data from {sources[0]}: {r.status_code}")
                raise RuntimeError(f"Failed to fetch data from {sources[0]}")
            # Parse the JSON response
            try:
                features = [r.json()]
            except:
                print(f"CONTENTS OF REQUESTS {r.content}")
        # If there are multiple sources, iterate over them
        if len(sources) > 1:
            for i in range(len(sources)):
                print_bar(i, len(sources))
                r = s.get(sources[i], headers=headers)
                try:
                    result = r.json()
                except:
                    print(f"CONTENTS OF REQUESTS {r.content}")

                # Check if the request was successful
                if 'error' in result:
                    print(f"Error fetching data: {result['error']['message']}")
                    raise RuntimeError
                
                # Check if the result contains features
                if 'features' not in result:
                    print(f"No features found in the response. Check the URL or parameters.")
                    raise RuntimeError
            
                features.append(result)
    try:
    # Combine list of feature collections into a single feature collection
        if len(features) == 0:
            print("No features found in the response. Check the URL or parameters.")
            raise RuntimeError
        elif len(features) == 1:
            feature_collection = features[0]
        if len(features) > 1:
            features = [item for sublist in features for item in sublist['features']]
            feature_collection = {
                "type": "FeatureCollection",
                "features": features
            }
    except Exception as e:
        print(f"Error combining features: {e}", len(features))
        raise RuntimeError("Failed to combine features from the response.")

    return feature_collection

def gdf_from_resource(resource):
    """
    Converts a resource file from an ArcGIS REST API service into a GeoDataFrame.
    Parameters:
    -----------
    resource : str or frictionless.Resource
        The path to the resource file, which can be a local file or a URL to an ArcGIS REST API service.

    Returns:
    --------
    gdf : geopandas.GeoDataFrame
        A GeoPandas GeoDataFrame constructed from the GeoJSON requested from the URL.

    Raises:
    --------
    RuntimeError: If the provided resource is not a valid ArcGIS REST API service or if there are issues with the request.  

    Example:
    --------
    >>> gdf = gdf_from_resource("path/to/example.resource.yaml")
    >>> print(gdf.head())
    
    """
    import frictionless
    import pandas as pd
    import geopandas as gpd
    import geojson
    from pyproj import CRS

    # Check if the resource is a string or a frictionless Resource object
    if isinstance(resource, str):
        # If it's a string, create a frictionless Resource object from the URL or file path
        resource = frictionless.Resource(path=resource)
    elif isinstance(resource, frictionless.Resource):
        # If it's already a Resource object, use it directly
        pass    

    # Fetch the GeoJSON data from the resource
    features = query(resource)

    # Get the spatial reference system (WKID) from the resource metadata
    wkid = resource.to_dict()['_metadata']['wkid']
    wkt = esri_wkid_to_wkt2(wkid) ## Convert ESRI WKID to wkt2  
      
    # Convert GeoJSON features to GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(features)
    
    # Set the coordinate reference system of the GeoDataFrame
    gdf = gpd.GeoDataFrame(gdf, geometry='geometry', crs=CRS.from_wkt(wkt))

    return(gdf)

def schema(url):
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
    r = requests.get(f"{url}?f=pjson")
    pjson = r.json()
    r.close()

    schema = {}
    schema['fields'] = []
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

    return schema

def get_tigerweb_layers_map(year, survey='ACS'):
    """
    Parameters: 
    -----------
    year : int
        The year of the TIGERweb layer (e.g., 2024).
    survey : str, optional
        The survey type, either 'ACS' (American Community Survey) or 'DEC' for Decennial Census
        or 'Current' for the most current geometries.
        Default is 'ACS'.

    Returns:
    --------
    dict : dict
        A dictionary mapping layer names to their corresponding IDs.

    Example:
    --------
    >>>   layers = get_tigerweb_layers_map(2024, survey='ACS')
    >>>   print(layers)
    """
    import pandas as pd
    import requests
    import re


    if survey not in ['ACS', 'DEC']:
        raise ValueError("Invalid survey type. Must be 'ACS' or 'DEC'.")
    if survey == 'DEC' and year not in ['2010', '2020']:
        raise ValueError("Invalid year for Decennial Census. Must be 2010 or 2020.")
    if survey == 'ACS' and pd.to_numeric(year) < 2012:
        raise ValueError("Invalid year for ACS. Must be 2012 or later.")
    if survey == 'DEC':
        survey = 'Census'
    if survey == 'Current':
        year == ""

    baseurl = f"https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/"
    mapserver_path = f"tigerWMS_{survey}{year}/MapServer/"
    mapserver_url = baseurl + mapserver_path

    # Retrieve the layers from the map service
    r = requests.get(f"{mapserver_url}?f=pjson")
    
    #   Check if the request was successful
    if r.status_code != 200:
        print(f"Error fetching data from {mapserver_url}: {r.status_code}")
        raise RuntimeError(f"Failed to fetch data from {mapserver_url}")
    
    # Parse the JSON response
    try:
        layers_json = r.json()
    except:
        print(f"CONTENTS OF REQUESTS {r.content}")
        r.close()
        raise RuntimeError(f"Failed to parse JSON from {mapserver_url}")
    r.close()    

    # Convert the layers to a DataFrame for easier manipulation
    layers = pd.DataFrame(layers_json['layers'])
    layers = layers[['id', 'name']]
    layers = layers.loc[layers['name'].str.contains('Labels') == False]  # Exclude label layers
    
    # Convert the DataFrame to a dictionary mapping layer names to IDs
    layers = layers.set_index('name')['id'].to_dict()
    
    layers = {k.lower(): v for k, v in layers.items()}  # Normalize layer names to lowercase
    # remove census from keys in layers
    layers = {k.replace('census ', ''): v for k, v in layers.items()}
    # remove years from keys in layers
    layers = {re.sub(r"^(19|20)\d{2}$ ", '', k): v for k, v in layers.items()}
    # remove the 11Xth from congressional districts
    layers = {re.sub(r"^(11)\d{1}$th ", '', k): v for k, v in layers.items()}


    return layers
    
def get_layer_url(year, layer_name, survey='ACS'):
    """Constructs the URL for a specific TIGERweb layer based on the year, layer name, and survey type.
    Parameters:
    -----------
    year : int
        The year of the TIGERweb layer (e.g., 2024).
    layer_name : str
        The name of the layer to retrieve (e.g., 'tracts', 'counties').
    survey : str, optional
        The survey type, either 'ACS' (American Community Survey) or 'DEC' for Decennial Census.
        Default is 'ACS'.
        
    Returns:
    --------
    str : str
        The URL of the specified TIGERweb layer.

    Example:
    --------
    >>> url = get_layer_url(2024, 'tracts', survey='ACS')
    >>> print(url)
    https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_ACS2024/MapServer/8

    Raises:
    -------
    ValueError: If the survey type or year is invalid, or if the layer name does not exist for the specified year and survey.
    RuntimeError: If there is an error fetching data from the constructed URL.

    
    """
    
    import requests
    from morpc.rest_api import get_tigerweb_layers_map
    import pandas as pd
    
    # Validate inputs
    if survey not in ['ACS', 'DEC']:
        raise ValueError("Invalid survey type. Must be 'ACS' or 'DEC'.")
    if survey == 'DEC' and year not in ['2010', '2020']:
        raise ValueError("Invalid year for Decennial Census. Must be 2010 or 2020.")
    if survey == 'ACS' and pd.to_numeric(year) < 2012:
        raise ValueError("Invalid year for ACS. Must be 2012 or later.")    
    if survey == 'DEC':
        survey = 'Census'
    
    layers = get_tigerweb_layers_map(year, survey)

    # Normalize the layer name to lowercase
    layer_name = layer_name.lower()
    
    # Check if the layer name exists in the layers dictionary
    if layer_name not in layers:
        raise ValueError(f"Layer '{layer_name}' not found for year {year} and survey '{survey}'. Available layers: {list(layers.keys())}")

    baseurl = f"https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/"
    mapserver_path = f"tigerWMS_{survey}{year}/MapServer/{layers[layer_name]}"
    mapserver_url = baseurl + mapserver_path

    # Verify the constructed URL
    r = requests.get(f"{mapserver_url}?f=pjson")
    if r.status_code != 200:
        print(f"Error fetching data from {mapserver_url}: {r.status_code}")
        raise RuntimeError(f"Failed to fetch data from {mapserver_url}")
    r.close()
    
    # Return the constructed URL
    return mapserver_url





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

    # Find the total number of records
    r = requests.get(f"{url}/query/", params = {
        "outfields": "*",
        "where": where,
        "f": "geojson",
        "returnCountOnly": "true"})
    total_count = int(re.findall('[0-9]+',str(r.json()))[0])
    r.close()

    return total_count


def esri_wkid_to_wkt2(esri_wkid):
    """Converts an ESRI WKID to an EPSG code.

    Parameters:
    -----------
    esri_wkid : int
        The ESRI WKID to be converted.  
    Returns:
    --------
    wkt : int
        The corresponding Well-Known Text string.
    Example:
    --------
    >>> wkt = esri_wkid_to_wkt2(4326)
    >>> print(wkt)
    

    """
    import json
    import requests

    r = requests.get(f"https://spatialreference.org/ref/esri/{esri_wkid}/prettywkt2.txt")
    wkt = r.text
    r.close()
    return wkt

# Depreciated for wkt2
# def esri_wkid_to_epsg(esri_wkid):
#     """Converts an ESRI WKID to an EPSG code.

#     Parameters:
#     -----------
#     esri_wkid : int
#         The ESRI WKID to be converted.  
#     Returns:
#     --------
#     epsg : int
#         The corresponding EPSG code.
#     Example:
#     --------
#     >>> epsg = esri_wkid_to_epsg(4326)
#     >>> print(epsg)
#     4326    

#     """
#     import json
#     import requests

#     r = requests.get(f"https://spatialreference.org/ref/esri/{esri_wkid}/projjson.json")
#     json = r.json()
#     epsg = json['base_crs']['id']['code']
#     return epsg

def print_bar(i, total):
    """Prints a progress bar to the console.

    Parameters:     
    -----------
    i : int
        The current iteration number.
    total : int
        The total number of iterations.
    """
    from IPython.display import clear_output

    percent = round((i + 1)/total * 100, 3)
    completed = round(percent)
    not_completed = 100-completed
    bar = f"{i+1}/{total} |{'|'*completed}{'.'*not_completed}| {percent}%"
    print(bar)
    clear_output(wait=True)

def get_api_key(path):
    """Reads an API key from a file.
    Parameters: 
    -----------
    path : str
        The path to the file containing the API key.
    Returns:
    --------
    key : str
        The API key read from the file.
    Example:
    --------
    >>> key = get_api_key('path/to/api_key.txt')
    """
    import os

    # Verify file exists
    if not os.path.exists(path):
        print(f"File does not exist: {path}")

    with open(path, 'r') as file:
        key = file.readlines()
    return key[0]

