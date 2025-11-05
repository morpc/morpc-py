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

SCOPES = {
    "us": {
        'for': 'us:1'
        },
    "region15": {
        "in": "state:39", 
        "for": f"county:{','.join([morpc.CONST_COUNTY_NAME_TO_ID[x][2:6] for x in morpc.CONST_REGIONS['15-County Region']])}"
        },
    "region10": {
        "in": "state:39", 
        "for": f"county:{','.join([morpc.CONST_COUNTY_NAME_TO_ID[x][2:6] for x in morpc.CONST_REGIONS['10-County Region']])}"
        },
    "region7": {
        "in": "state:39", 
        "for": f"county:{','.join([morpc.CONST_COUNTY_NAME_TO_ID[x][2:6] for x in morpc.CONST_REGIONS['7-County Region']])}"
        },
    "region-corpo": {
        "in": "state:39", 
        "for": f"county:{','.join([morpc.CONST_COUNTY_NAME_TO_ID[x][2:6] for x in morpc.CONST_REGIONS['CORPO Region']])}"
        }
}

for x in STATE_SCOPES:
    SCOPES.update(x)

for x in COUNTY_SCOPES:
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
 '970': ['1000000']}


def geoids_from_params(for_params, in_params = None, year = 2023):
    """
    returns a list of GEOIDFQs from for and in parameters. 

    Parameters
    ----------
    for_param :  string
        A string formatted according the Census API.
    
    in_params : string
    
    """
    url = f"https://api.census.gov/data/{year}/geoinfo"
    params = {
        'get': 'GEO_ID',
        'for': for_params
    }

    if in_params != None:
        params.update({
            'in': in_params
        })
    
    logger.info(f"Getting GEOIDS from {for_params} and {in_params}.")
    json = morpc.req.get_json_safely(url, params = params)

    # Extract UCGIDs from the response
    ucgids = [x[0] for x in json[1:]]
    return ucgids

def geoids_from_pseudo(pseudos, year=2023):
    """
    returns a list of GEOIDFQs from list of ucgid psuedos. 

    Parameters
    ----------
    psuedos : list
        a list of ucgid pseudo predicate. See https://www.census.gov/data/developers/guidance/api-user-guide/ucgid-predicate.html
    
    """
    baseurl = f"https://api.census.gov/data/{year}/geoinfo"
    params = {
        'get': 'GEO_ID',
        'ucgid': f"pseudo({",".join(pseudos)})"
    }
    
    logger.info("Getting GEOIDS from pseudo groups {pseudos}")
    json = morpc.req.get_json_safely(baseurl,params = params)

    # Extract UCGIDs from the response
    ucgids = [x[0] for x in json[1:]]
    return ucgids