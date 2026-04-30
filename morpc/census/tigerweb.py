import logging
from os import PathLike
from typing import Literal

logger = logging.getLogger(__name__)

current_endpoints = {
    'public use microdata areas': 0,
    'zip code tabulation areas': 2,
    'tribal tracts': 4,
    'tribal block groups': 6,
    'tracts': 8,
    'block groups': 10,
    'unified school districts': 14,
    'secondary school districts': 16,
    'elementary school districts': 18,
    'school district administrative areas': 84,
    'estates': 20,
    'county subdivisions': 22,
    'subbarrios': 24,
    'consolidated cities': 26,
    'incorporated places': 28,
    'designated places': 30,
    'alaska native regional corporations': 32,
    'tribal subdivisions': 34,
    'federal american indian reservations': 36,
    'off-reservation trust lands': 38,
    'state american indian reservations': 40,
    'hawaiian home lands': 42,
    'alaska native village statistical areas': 44,
    'oklahoma tribal statistical areas': 46,
    'state designated tribal statistical areas': 48,
    'tribal designated statistical areas': 50,
    'american indian joint-use areas': 52,
    'congressional districts': 54,
    'state legislative districts - upper': 56,
    'state legislative districts - lower': 58,
    'divisions': 60,
    'regions': 62,
    'states': 80,
    'counties': 82,
    'urban areas': 88,
    'combined statistical areas': 97,
    'metropolitan divisions': 95,
    'metropolitan statistical areas': 93,
    'micropolitan statistical areas': 91
    }

def get_tigerweb_layers_map(year: int = 2023, survey:Literal['ACS','DEC']='ACS'):
    """
    Parameters: s
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
        logger.error(f"Invalid survey type {survey}. Must be 'ACS' or 'DEC'.")
        raise ValueError("Invalid survey type. Must be 'ACS' or 'DEC'.")
    if survey == 'DEC' and year not in ['2010', '2020']:
        logger.error(f"Invalid year {year} for Decennial Census. Must be 2010 or 2020.")
        raise ValueError("Invalid year for Decennial Census. Must be 2010 or 2020.")
    if survey == 'ACS' and pd.to_numeric(year) < 2012:
        logger.error(f"Invalid year {year} for ACS. Must be 2012 or later.")
        raise ValueError("Invalid year for ACS. Must be 2012 or later.")
    if survey == 'DEC':
        survey = 'Census'
    if survey == 'Current':
        year == ""

    baseurl = f"https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/"
    mapserver_path = f"tigerWMS_{survey}{year}/MapServer/"
    mapserver_url = baseurl + mapserver_path

    # Retrieve the layers from the map service
    logger.info(f"Fetching metadata from {mapserver_url}?f=pjson")
    r = requests.get(f"{mapserver_url}?f=pjson")
    
    #   Check if the request was successful
    if r.status_code != 200:
        logger.error(f"Error fetching data from {mapserver_url}: {r.status_code}")
        raise RuntimeError(f"Failed to fetch data from {mapserver_url}")
    else:
        logger.info(f"successful fetch using {r.url}")
    
    # Parse the JSON response
    try:
        layers_json = r.json()
    except:
        logger.error(f"Failed to decode json: CONTENTS OF REQUESTS {r.content}")
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
    layers = {re.sub(r"^(19|20)[0-9]{2} ", '', k): v for k, v in layers.items()}
    # remove the 11Xth from congressional districts
    layers = {re.sub(r"^(11)[0-9]{1}th ", '', k): v for k, v in layers.items()}

    return layers
    
def get_layer_url(layer_name, year:int|None=None, survey:Literal['current', 'ACS', 'DEC']='current'):
    """Constructs the URL for a specific TIGERweb layer based on the year, layer name, and survey type.
    Parameters:
    -----------
    year : int
        The year of the TIGERweb layer (e.g., 2024).
    layer_name : str
        The name of the layer to retrieve (e.g., 'tracts', 'counties').
    survey : str, optional
        The survey type, either 'current', 'ACS' (American Community Survey) or 'DEC' for Decennial Census.
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
    import pandas as pd
    
    logger.info(f"Validating Survey {survey} and Year {year}")
    # Validate inputs
    if survey not in ['ACS', 'DEC', 'current']:
        raise ValueError("Invalid survey type. Must be 'current','ACS' or 'DEC'.")
    if survey == 'DEC' and year not in ['2010', '2020']:
        raise ValueError("Invalid year for Decennial Census. Must be 2010 or 2020.")
    if survey == 'ACS' and pd.to_numeric(year) < 2012:
        raise ValueError("Invalid year for ACS. Must be 2012 or later.")    
    if survey == 'DEC':
        survey = 'Census'
    
    if survey != 'current':
        layers = get_tigerweb_layers_map(year, survey)
        # Check if the layer name exists in the layers dictionary
        if layer_name not in layers:
            logger.error(f"Layer '{layer_name}' not found for year {year} and survey '{survey}'. Available layers: {list(layers.keys())}")
            raise ValueError(f"Layer '{layer_name}' not found for year {year} and survey '{survey}'. Available layers: {list(layers.keys())}")
        
    # Normalize the layer name to lowercase
    layer_name = layer_name.lower()

    baseurl = f"https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/"
    if survey != 'current':
        mapserver_path = f"tigerWMS_{survey}{year}/MapServer/{layers[layer_name]}"
    else:
        mapserver_path = f"tigerWMS_Current/MapServer/{current_endpoints[layer_name]}"

    mapserver_url = baseurl + mapserver_path

    logger.info(f"url: {mapserver_url}")

    # Verify the constructed URL
    r = requests.get(f"{mapserver_url}?f=pjson")
    if r.status_code != 200:
        print(f"Error fetching data from {mapserver_url}: {r.status_code}")
        raise RuntimeError(f"Failed to fetch data from {mapserver_url}")
    r.close()
    
    # Return the constructed URL
    return mapserver_url

def outfields_from_scale(scale):
    import re
    from morpc import SUMLEVEL_DESCRIPTIONS, SUMLEVEL_FROM_CENSUSQUERY

    sumlevel = SUMLEVEL_FROM_CENSUSQUERY[scale]
    template = SUMLEVEL_DESCRIPTIONS[sumlevel]['geoidfq_format']

    fields = [[y[0].lower(), y[1]] for y in [x.split(':') for x in re.findall(r'\{(.+?)\}', template)] if y[0] not in ['SUMLEVEL', 'VARIANT', 'GEOCOMP']]

    return ",".join(['GEOID','NAME'] + [x[0].upper() for x in fields])

def where_from_scope(scope):
    from morpc.census.geos import SCOPES
    if scope == 'us':
        where = '1=1'
    else:
        scope_params = SCOPES[scope] 
        wheres = []
        for param in scope_params:
            geo, ids = scope_params[param].split(':')
            wheres.append(f"{geo.upper()} in ({",".join([f"'{str(x)}'" for x in ids.split(',')])})")
        where = " and ".join(wheres)
    return where


def resource_from_scope_scale(scope, scale, archive:PathLike|None=None, max_record_count=20):
    from morpc.rest_api import resource
    from morpc import SUMLEVEL_DESCRIPTIONS, SUMLEVEL_FROM_CENSUSQUERY, HIERARCHY_STRING_FROM_CENSUSNAME

    sumlevel = SUMLEVEL_FROM_CENSUSQUERY[scale]
    url = get_layer_url(SUMLEVEL_DESCRIPTIONS[sumlevel]['censusRestAPI_layername'])

    where = where_from_scope(scope)
    outfields = outfields_from_scale(scale)

    tigerweb_resource = resource(name=f"censustigerweb-{scope}-{HIERARCHY_STRING_FROM_CENSUSNAME[scale].lower()}", url=url, where=where, outfields=outfields, max_record_count=max_record_count)

    if archive != None:
        tigerweb_resource.to_yaml(archive)

    return tigerweb_resource

def resource_from_geometry_scale(geo, scopename, scale, archive:PathLike|None=None, max_record_count=20):
    from morpc.rest_api import resource
    from morpc import SUMLEVEL_DESCRIPTIONS, SUMLEVEL_FROM_CENSUSQUERY, HIERARCHY_STRING_FROM_CENSUSNAME

    sumlevel = SUMLEVEL_FROM_CENSUSQUERY[scale]
    url = get_layer_url(SUMLEVEL_DESCRIPTIONS[sumlevel]['censusRestAPI_layername'])

    outfields = outfields_from_scale(scale)

    params = {
        'geometry': ",".join([str(x) for x in geo.total_bounds]),
        'geometryType': 'esriGeometryEnvelope',
        'inSR': geo.crs.to_epsg(),
        'spatialRel': 'esriSpatialRelContains',
        'returnGeometry': 'true',
        'f': 'geojson'
    }
    tigerweb_resource = resource(name=f"censustigerweb-{scopename}-{HIERARCHY_STRING_FROM_CENSUSNAME[scale].lower()}", url=url, outfields=outfields, max_record_count=max_record_count, **params)

    if archive != None:
        tigerweb_resource.to_yaml(archive)

    return tigerweb_resource