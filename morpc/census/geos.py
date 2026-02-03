import logging

logger  = logging.getLogger(__name__)

import morpc

# TODO (jinskeep_morpc): Develop function for fetching census geographies leveraging scopes
# Issue URL: https://github.com/morpc/morpc-py/issues/102
#   The current geos-lookup workflow is limited by size and scope. This function will be used
#   to fetch geographies at any scale and scope without the need to store it locally. It is 
#   limited to census geographies. 
#   [ ]: Consider storing the data as a remote frictionless resource similar to the acs data class.
#   [ ]: Define scale and scopes that are used. Possibly lists for benchmarking (i.e. Most populous cities)

import morpc.req

STATE_SCOPES = [
    {
        key: {"for": f"state:{int(value):02d}"}
    } 
    for key, value in morpc.CONST_STATE_NAME_TO_ID.items()
    ]

COUNTY_SCOPES = [
    {
    key.lower(): {
        "in": "state:39", 
        "for": f"county:{int(value[2:6]):03d}"
        }
    }
    for key, value in morpc.CONST_COUNTY_NAME_TO_ID.items()
    ]

MORPC_REGION_SCOPES = [
    {"region15": {
        "in": "state:39", 
        "for": f"county:{','.join([morpc.CONST_COUNTY_NAME_TO_ID[x][2:6] for x in morpc.CONST_REGIONS['15-County Region']])}"
        }
        },
    {"region10": {
        "in": "state:39", 
        "for": f"county:{','.join([morpc.CONST_COUNTY_NAME_TO_ID[x][2:6] for x in morpc.CONST_REGIONS['10-County Region']])}"
        }
        },
    {"region7": {
        "in": "state:39", 
        "for": f"county:{','.join([morpc.CONST_COUNTY_NAME_TO_ID[x][2:6] for x in morpc.CONST_REGIONS['7-County Region']])}"
        }
        },
    {"regioncorpo": {
        "in": "state:39", 
        "for": f"county:{','.join([morpc.CONST_COUNTY_NAME_TO_ID[x][2:6] for x in morpc.CONST_REGIONS['CORPO Region']])}"
        }
        },
    {"regionceds": {
        "in": "state:39", 
        "for": f"county:{','.join([morpc.CONST_COUNTY_NAME_TO_ID[x][2:6] for x in morpc.CONST_REGIONS['CEDS Region']])}"
        }
        },
    {"regioncbsa": {
        "in": "state:39", 
        "for": f"county:{','.join([morpc.CONST_COUNTY_NAME_TO_ID[x][2:6] for x in morpc.CONST_REGIONS['CBSA']])}"
        }
        }
]

SCOPES = {
    "us": {
        'for': 'us:1'
        },
    "columbuscbsa": {
        "for": f"metropolitan statistical area/micropolitan statistical area:{morpc.CONST_COLUMBUS_CBSA_ID}"
    }
}

for x in STATE_SCOPES:
    SCOPES.update(x)

for x in COUNTY_SCOPES:
    SCOPES.update(x)

for x in MORPC_REGION_SCOPES:
    SCOPES.update(x)

## These are the available children sumelevels for the various parent level sumlevels when using the ucgid=psuedo() predicate.
## https://www.census.gov/data/developers/guidance/api-user-guide/ucgid-predicate.html
## See https://www2.census.gov/data/api-documentation/list-of-available-collections-of-geographies.xlsx for list of geographies.
PSEUDOS = {'010': [
    '0300000',
    '0400000',
    '04000S0',
    '0500000',
    '0600000',
    '1400000',
    '1500000',
    '1600000',
    '2500000',
    '2510000',
    '3100000',
    '31000M1',
    '31000M2',
    '3140000',
    '3300000',
    '3500000',
    '4000000',
    '5000000',
    '7950000',
    '8600000',
    '8610000',
    '9500000',
    '9600000',
    '9700000',
    '9800000',
    'E330000',
    'E600000',
    'E800000',
    'E810000'],
 '040': [
    '0500000',
    '0600000',
    '06V0000',
    '1000000',
    '1400000',
    '1500000',
    '1600000',
    '1700000',
    '2300000',
    '2500000',
    '3100000',
    '3500000',
    '4000000',
    '4200000',
    '5000000',
    '6100000',
    '6200000',
    '7000000',
    '7950000',
    '8600000',
    '8610000',
    '8710000',
    '9040000',
    '9500000',
    '9600000',
    '9700000',
    '9800000',
    'E600000'],
 '050': [
    '0600000',
    '06V0000',
    '1000000',
    '1400000',
    '1500000',
    '1600000',
    '7000000',
    '8600000',
    '8710000'],
 '060': ['1000000'],
 '140': ['1000000', '1500000'],
 '160': ['1000000', '1400000', '8600000', '8710000'],
 '250': ['1000000', '2510000', '5000000'],
 '310': [
    '0500000',
    '0600000',
    '1400000',
    '1500000',
    '1600000',
    '5000000',
    '8600000',
    'E600000'],
 '314': ['0500000',
    '0600000',
    '1400000',
    '1500000',
    '1600000',
    '5000000',
    '8600000'],
 '330': ['0500000',
    '0600000',
    '1400000',
    '1500000',
    '1600000',
    '3100000',
    '5000000'],
 '335': ['0600000'],
 '350': ['0500000', '0600000', '3520000'],
 '355': ['0600000'],
 '500': ['0500000', '0600000', '1400000', '1500000', '4000000'],
 '610': ['0600000', '1600000'],
 '620': ['0600000', '1600000'],
 '950': ['1000000'],
 '960': ['1000000'],
 '970': ['1000000']
 }


def valid_scale(scale):
    from morpc import SUMLEVEL_DESCRIPTIONS

    logger.debug(f"Validating scale {scale} against implemented morpc.SUMLEVEL_DESCRIPTIONS.")
    # Get available scales from morpc SUMLEVEL_DESCRIPTIONS
    available_scales = [SUMLEVEL_DESCRIPTIONS[x]['censusQueryName'] for x in SUMLEVEL_DESCRIPTIONS if SUMLEVEL_DESCRIPTIONS[x]['censusQueryName'] != None]

    # Validate inputs
    if scale not in available_scales:
        logger.error(f"Scale '{scale}' is not recognized. Available scales: {available_scales}")
        raise ValueError(f"Scale '{scale}' is not recognized. Available scales: {available_scales}")
    else:
        return True
        
def valid_scope(scope):

    logger.debug(f"Validating scope {scope} against implemented morpc.census.geos.SCOPES")
    if scope != None:
        if scope not in SCOPES:
            logger.error(f"Scope '{scope}' is not recognized. Available scopes: {list(SCOPES.keys())}")
            raise ValueError(f"Scope '{scope}' is not recognized. Available scopes: {list(SCOPES.keys())}")
        else:
            return True

def get_query_req(scale, year='2023'):
    from morpc import SUMLEVEL_FROM_CENSUSQUERY
    from morpc.req import get_json_safely

    logger.debug(f"Getting required 'in' parameters for {scale}")

    sumlevel = SUMLEVEL_FROM_CENSUSQUERY[scale]

    url = f"https://api.census.gov/data/{year}/geoinfo/geography.json"
    json = get_json_safely(url)

    query_requirements = {}
    for item in json['fips']:
        if item['geoLevelDisplay'] in sumlevel:
            if 'requires' in item.keys():
                query_requirements['requires'] = item['requires']
            else:
                query_requirements['requires'] = None
            if 'wildcard' in item.keys():
                query_requirements['wildcard'] = item['wildcard']
            else:
                query_requirements['wildcard'] = None
    
    logger.info(f"{scale} requires {query_requirements}")
    return query_requirements

def geo_params_from_scope_scale(scope, scale=None):

    logger.debug(f"Building parameters to pass for geographies Scope: {scope} and Scale: {scale}")
    params = {}
    if scale == None:
        logger.info(f"No scale specified. Using {scope} parameters. {SCOPES[scope]}")
        params.update(SCOPES[scope])
    else:
        logger.info(f"Scale {scale} specified for scope {scope}.")
        if "in" in SCOPES[scope]:
            logger.info(f"Scope {scope} already has 'in' parameter. Converting to ucgid=pseudo() type predicate.")
            pseudos = pseudos_from_scale_scope(scale, scope)
            params.update({'ucgid': f"pseudo({','.join(pseudos)})"})
        else:
            logger.info(f"Scope {scope} has no 'in' parameter. Applying scale.")
            params.update({"in": SCOPES[scope]['for']})
            params.update({"for": f"{scale}:*"})

            logger.info(f"Checking for valid 'for' and 'in' parameters. ")
            query_req = get_query_req(scale)

            in_list = [x.split(':')[0] for x in params['in']]

            for req in query_req['requires']:
                if req not in in_list:
                    if req not in query_req['wildcard']:
                        logger.error(f"{scale} requires designating a scope with {req} variable.")
                    else:
                        logger.info(f"Adding wildcard to fulfill hierarchical geographic requirement {req}")
                        if not isinstance(params, list):
                            params['in'] = [params['in'], f"{req}:*"]
                        else:
                            params['in'].append(f"{req}:*")
        
    logger.debug(f"params from scope and scale: {params}")
    return params


def geoids_from_scope(scope):
    from morpc.req import get_json_safely

    logger.debug(f"Fetching geoids from scope parameters {SCOPES[scope]}.")
    if valid_scope(scope):
        baseurl = "https://api.census.gov/data/2023/geoinfo?get=GEO_ID"
        json = get_json_safely(baseurl, params = SCOPES[scope])
        geoids = [row[0] for row in json[1:]]

        return geoids
    
def pseudos_from_scale_scope(scale, scope):
    from morpc import SUMLEVEL_FROM_CENSUSQUERY

    logger.debug(f"Getting psuedo combinations for parents in {scope} at scale {scale}")
    parents = geoids_from_scope(scope)

    sumlevel = parents[0][0:3]

    child = f"{SUMLEVEL_FROM_CENSUSQUERY[scale]}0000"

    if child in PSEUDOS[sumlevel]:
        logger.info(f"Returning pseudos for {child} in {parents}")
        pseudos = [f"{parent}${child}" for parent in parents]
    else:
        logger.error(f"{child} is not allowed child for parent sumlevel {sumlevel}")

    return pseudos

def geoids_from_params(param_dict, year = 2023):
    """
    returns a list of GEOIDFQs from psuedo ucgids, or for and in parameters. 

    Parameters
    ----------
    param_dict : dict
        A dictionary of the parameters for the query, including for and in, or ucgid.
    
    """
    url = f"https://api.census.gov/data/{year}/geoinfo"
    params = {
        'get': 'GEO_ID',
    }
    logger.debug(f"Updating params from {param_dict}")

    if 'ucgid' in param_dict:
        params.update({
            'ucgid': param_dict['ucgid']
        })
    elif 'for' in param_dict:
        params.update({
            'for': param_dict['for']
        })
        if 'in' in param_dict:
            params.update({
                'in': param_dict['in']
            })
    
    logger.info(f"Getting GEOIDS from {url} and params: {params}.")
    json = morpc.req.get_json_safely(url, params = params)

    # Extract UCGIDs from the response
    ucgids = [x[0] for x in json[1:]]
    return ucgids

## depreciated and combined with geoids_from_params()
# def geoids_from_pseudo(pseudos, year=2023):
#     """
#     returns a list of GEOIDFQs from list of ucgid psuedos. 

#     Parameters
#     ----------
#     psuedos : list
#         a list of ucgid pseudo predicate. See https://www.census.gov/data/developers/guidance/api-user-guide/ucgid-predicate.html
    
#     """
#     baseurl = f"https://api.census.gov/data/{year}/geoinfo"
#     params = {
#         'get': 'GEO_ID',
#         'ucgid': f"pseudo({",".join(pseudos)})"
#     }
    
#     logger.info("Getting GEOIDS from pseudo groups {pseudos}")
#     json = morpc.req.get_json_safely(baseurl,params = params)

#     # Extract UCGIDs from the response
#     ucgids = [x[0] for x in json[1:]]
#     return ucgids

def fetch_geos_from_geoids(geoidfqs, year, survey):
    """
    Fetches a table of geometries from a list of Census GEOIDFQs using the Rest API.

    Parameters:
    geoidfqs : list
        A list of fully qualified Census GEOIDs, i.e. ['0550000US39049', '0550000US39045']

    year : str
        The year of the data to ret
    """

    from morpc.census.tigerweb import get_layer_url
    import pandas as pd
    import geopandas as gpd

    # Get sum levels in the data
    sumlevels = set([x[0:3] for x in geoidfqs])

    logger.info(f"Sum levels {', '.join(sumlevels)} are in data.")

    geometries = []
    for sumlevel in sumlevels: # Get geometries for each sumlevel iteratively
        # Get rest api layer name and get url
        layerName = morpc.SUMLEVEL_DESCRIPTIONS[sumlevel]['censusRestAPI_layername']

        url = get_layer_url(year, layer_name=layerName, survey=survey)
        logger.info(f"Fetching geometries for {layerName} ({sumlevel}) from {url}")

        # Construct a list of geoids from data to us to query API
        geoids = ",".join([f"'{x.split('US')[-1]}'" for x in geoidfqs if x.startswith(sumlevel)])

        logger.info(f"There are {len(geoids)} geographies in {layerName}")
        logger.debug(f"{', '.join(geoidfqs)}")

        # Build resource file and query API
        logger.info(f"Building resource file to fetch from RestAPI.")
        resource = morpc.rest_api.resource(name='temp', url=url, where= f"GEOID in ({geoids})", outfields='GEOID')

        logger.info(f"Fetching geographies from RestAPI.")
        geos = morpc.rest_api.gdf_from_resource(resource)
        geos['GEOIDFQ'] = [f"{sumlevel}0000US{x}" for x in geos['GEOID']]

        geometries.append(geos[['GEOIDFQ', 'geometry']])
    logger.info("Combining geometries...")
    geometries = pd.concat(geometries)
    geometries = geometries.rename(columns={'GEOIDFQ': 'GEO_ID'})
    geometries = geometries.set_index('GEO_ID')

    return gpd.GeoDataFrame(geometries, geometry='geometry')

def fetch_geos_from_scale_scope(scope, scale=None, year='2023', survey='ACS'):
    """
    Returns a geodataframe of with geoids and and geometries from scales and scope.

    Parameters
    ----------
    scope : 
        se morpc.census.geos.SCOPES
    scale : str, optional
        see morpc.SUMLEVEL_DESCRIPTIONS.CensusQueryName
    year : str, optional
        The year of the geometries to return, by default '2023'
        Available options are determined by census API, currently 2020 and 2023
    survey : str, optional
        The survey to retrive the data for, ACS or DEC
    """

    return fetch_geos_from_geoids(geoids_from_params(geo_params_from_scope_scale(scope, scale)), year, survey)
