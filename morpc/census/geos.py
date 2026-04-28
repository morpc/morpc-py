
import logging
logger  = logging.getLogger(__name__)

from pandas import DataFrame, Series
from typing import Literal

import morpc
import morpc.req

# TODO (jinskeep_morpc): Develop function for fetching census geographies leveraging scopes
# Issue URL: https://github.com/morpc/morpc-py/issues/102
#   The current geos-lookup workflow is limited by size and scope. This function will be used
#   to fetch geographies at any scale and scope without the need to store it locally. It is 
#   limited to census geographies. 
#   [ ]: Consider storing the data as a remote frictionless resource similar to the acs data class.
#   [ ]: Define scale and scopes that are used. Possibly lists for benchmarking (i.e. Most populous cities)

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
        },
    {"regionmobility": {
        "in": "state:39", 
        "for": f"county:{','.join([morpc.CONST_COUNTY_NAME_TO_ID[x][2:6] for x in morpc.CONST_REGIONS['Mobility Region']])}"
        }
        },
    {"regionmpo":{
        "in": "state:39",
        "for": f"county:{','.join([morpc.CONST_COUNTY_NAME_TO_ID[x][2:6] for x in morpc.CONST_REGIONS['MPO Region']])}"
    }}
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

def geoinfo_for_hierarchical_geos(scope, scale):
    """
    For geographic calls that are more complex than can be handled with psuedo(). 
    
    Creates a list of geoids from iterating through hierarchy and constructing manually. 

    Parameters:

    """
    from morpc.census.geos import geoinfo_from_params, geoids_from_scope, get_query_req, SCOPES
    import pandas as pd

    # Get the query requirements
    query_req = get_query_req(scale)

    # Get all the geos in the scope
    scope_params = [x for x in SCOPES[scope].values()]
    in_scope = [x.split(":")[0] for x in scope_params if x.split(":")[0] in query_req['requires']]

    # Get the difference
    not_in_scope = [x for x in query_req['requires'] if x not in in_scope]

    # Create a table of the geoids for what is already in the scope
    parent_table = geoids_from_scope(scope, output='table').drop(columns='GEO_ID')

    # To fill in required geographic levels build a table representing a query for each 
    # query we need to construct the whole table. 

    # For each geography that is not in the scope but is in the requirements...
    for geo in not_in_scope:
        logger.info(f"Getting {geo} from {in_scope}")

        # Add a column to the table for the geography
        parent_table[geo] = None
        parent_table[geo] = parent_table[geo].astype('object')

        # For each row in the table
        for i, row in parent_table.iterrows():      

            # Create query parameters from columns in row
            in_param_str = []      
            for x in in_scope:
                in_param_str.append(f"{x}:{",".join(row[x]) if isinstance(row[x],list) else row[x]}")

            # Get a list of all geoids (*) for the geography we are adding to the table
            geoids = geoinfo_from_params({"in": in_param_str, "for": f"{geo}:*"}, output='table')[geo].to_list()
            logger.debug(f"at row:{i}, column:{geo} adding geoids {geoids}")

            # Add it to the table
            parent_table.at[i, geo] = geoids

        # Add the geography to the list of geographies in the scope
        in_scope += [geo]

        # If the list of geographies in the scope is less than the last column. Explode the list
        if len(in_scope) < len(query_req['requires']):
            parent_table = parent_table.explode(geo).reset_index().drop(columns='index')

    # With table each row representing a required query...
    geoinfos = []
    # Itereate through each row
    for i, row in parent_table.iterrows():

        # Construct the in parameter for the query
        in_param_str = []      
        for x in in_scope:
            in_param_str.append(f"{x}:{",".join(row[x]) if isinstance(row[x],list) else row[x]}")

        # Call this list of GEOIDFQs this time
        geoinfo = geoinfo_from_params({"in": in_param_str, "for": f"{scale}:*"}, output='table')

        # Add to list
        geoinfos.append(geoinfo)

    # combine and return
    return pd.concat(geoinfos)

def geoinfo_from_scope_scale(scope: str, scale: str | None = None, output: Literal['list','table','json','params']='list'):
    """
    Creates a dictionary with 'for' and 'in' or 'ucgid' parameters that conforms to Census API query requirements.

    Parameters
    ----------
    scope : str
        see morpc.census.geos.SCOPES
    scale : str, optional
        see morpc.SUMLEVEL_DESCRIPTION['censusQueryName'], by default None
    output : {'list', 'table', 'json', 'params'}
        The type of geoinfo to return

    Raises
    ------
    ValueError
        When the defined scale and scope are invalid combinations. 
    """
    logger.debug(f"Building parameters to pass for geographies Scope: {scope} and Scale: {scale}")
    params = {}
    scope_sumlevel = list(set([x[0:3] for x in geoids_from_scope(scope)]))[0]

    # If there is no scale, just use scope.
    if scale == None:
        if scope.startswith('region'):
            scale = 'county'
        logger.info(f"No scale specified. Using {scope} parameters. {SCOPES[scope]}")
        params.update(SCOPES[scope])
        if output == 'params':
            return params
        geoinfo = geoinfo_from_params(params, output='table')

    # If there is a scale...
    else:
        logger.info(f"Scale {scale} specified for scope {scope}.")
        scale_sumlevel = morpc.SUMLEVEL_FROM_CENSUSQUERY[scale]

        # Check to make sure scope and scale are different sumlevels...
        # If it is, just use scope.
        if scope_sumlevel == scale_sumlevel:
            logger.warning(f"Scope and Scale have same sumlevel, using Scope {scope}.")
            params.update(SCOPES[scope])
            if output == 'params':
                return params
            geoinfo = geoinfo_from_params(params, output='table')

        # If we need to use scale
        else:
            # First try to use psuedos
            try:
                pseudos = pseudos_from_scale_scope(scale, scope)
                params.update({'ucgid': f"pseudo({','.join(pseudos)})"})
                if output == 'params':
                    return params
                geoinfo = geoinfo_from_params(params, output='table')

            except ValueError as e:
                logger.info(f"Manually building list of all geoids.")
            
            # If geography combination is not valid combination for psuedos...

                            # (see list of available combinations 
                            # at https://www.census.gov/data/developers/guidance/api-user-guide/ucgid-predicate.html
                            # in the "List of Available Collections of Geographies.")

            # try to build "in" and "for" parameters to meet requirements. (see https://api.census.gov/data/2023/acs/acs5/geography.json)
                if output == 'params':
                    return {'ucgid': ",".join(geoinfo_for_hierarchical_geos(scope, scale)['GEO_ID'])}
                geoinfo = geoinfo_for_hierarchical_geos(scope, scale)

    if output == 'table':
        return geoinfo
    if output == 'json':
        return geoinfo.set_index('GEO_ID').to_dict()['NAME']
    if output == 'list':
        return geoinfo['GEO_ID'].to_list()


def geoids_from_scope(scope, output: Literal['list','table','json']='list'):
    from morpc.req import get_json_safely
    import pandas as pd

    logger.debug(f"Fetching geoids from scope parameters {SCOPES[scope]}.")
    if valid_scope(scope):
        baseurl = "https://api.census.gov/data/2023/geoinfo?get=GEO_ID"
        json = get_json_safely(baseurl, params = SCOPES[scope])
        if output == 'list':
            return [row[0] for row in json[1:]]
        if output == 'table':
            return pd.DataFrame.from_records(json[1:], columns=json[0]).reset_index().drop(columns='index')
        if output == 'json':
            return json
    
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
        raise ValueError

    return pseudos

def geoinfo_from_params(param_dict: dict, year: int = 2024, output: Literal['list','table','json']='table') -> list:
    """
    returns a list of GEOIDFQs from psuedo ucgids, or for and in parameters. 

    Parameters
    ----------
    param_dict : dict
        A dictionary of the parameters for the query, including for and in, or ucgid.
    
    """
    import pandas as pd
    url = f"https://api.census.gov/data/{year}/geoinfo"
    params = {
        'get': 'GEO_ID,NAME',
    }
    logger.debug(f"Updating params from {param_dict}")

    if 'ucgid' in param_dict:
        if 'pseudo' in param_dict['ucgid']:
            params.update({
                'ucgid': param_dict['ucgid']
            })
        else:
            logger.error(f"ucgid without pseudo. {params}")
            raise NotImplementedError
        
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

    if output == 'list':
        return [row[0] for row in json[1:]]
    if output == 'table':
        return pd.DataFrame.from_records(json[1:], columns=json[0]).reset_index().drop(columns='index')
    if output == 'json':
        return json

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

def fetch_geos_from_geoids(geoidfqs, year:int|None=None, survey:Literal['current', 'ACS', 'DEC']='current', chunk_size=500):
    """
    Fetches a table of geometries from a list of Census GEOIDFQs using the Rest API.

    Parameters:
    geoidfqs : list
        A list of fully qualified Census GEOIDs, i.e. ['0550000US39049', '0550000US39045']

    year : str
        The year of the data to return

    survey : str
        The survey to return the geos for, "ACS" or "DEC"
    """

    from morpc.census.tigerweb import get_layer_url
    import pandas as pd
    import geopandas as gpd
    
    all_geoidfqs = geoidfqs
    all_geometries = []

    if len(geoidfqs) > chunk_size:
        start = 0
        offset = chunk_size-1
        while start < len(all_geoidfqs):
            if start+offset > len(all_geoidfqs):
                offset = len(all_geoidfqs)-start
            logger.info(f"Fetching geoids {start} - {start+offset}")
            geoidfqs = all_geoidfqs[start:start+offset+1]
        
        # Get sum levels in the data
            sumlevels = set([x[0:3] for x in geoidfqs])

            logger.info(f"Sum levels {', '.join(sumlevels)} are in data.")

            for sumlevel in sumlevels: # Get geometries for each sumlevel iteratively
                # Get rest api layer name and get url
                layerName = morpc.SUMLEVEL_DESCRIPTIONS[sumlevel]['censusRestAPI_layername']
                if layerName == None:
                    logger.error(f"Sumlevel {sumlevel} does not have a layer in TigerWeb REST API.")
                    raise NotImplementedError

                url = get_layer_url(layer_name=layerName, year=year, survey=survey)
                logger.info(f"Fetching geometries for {layerName} ({sumlevel}) from {url}")

                # Construct a list of geoids from data to us to query API
                geoids = ",".join([f"'{x.split('US')[-1]}'" for x in geoidfqs if x.startswith(sumlevel)])

                logger.info(f"There are {len(geoids)} geographies in {layerName}")
                logger.debug(f"{geoids}")

                # Build resource file and query API
                logger.info(f"Building resource file to fetch from RestAPI.")
                resource = morpc.rest_api.resource(name='temp', url=url, where=f"GEOID in ({geoids})", outfields='GEOID', max_record_count=chunk_size)

                logger.info(f"Fetching geographies from RestAPI.")
                geos = morpc.rest_api.gdf_from_resource(resource)

            all_geometries.append(geos)
            start += offset+1
    else:
        sumlevels = set([x[0:3] for x in geoidfqs])

        logger.info(f"Sum levels {', '.join(sumlevels)} are in data.")

        for sumlevel in sumlevels: # Get geometries for each sumlevel iteratively
            # Get rest api layer name and get url
            layerName = morpc.SUMLEVEL_DESCRIPTIONS[sumlevel]['censusRestAPI_layername']
            if layerName == None:
                logger.error(f"Sumlevel {sumlevel} does not have a layer in TigerWeb REST API.")
                raise NotImplementedError

            url = get_layer_url(year, layer_name=layerName, survey=survey)
            logger.info(f"Fetching geometries for {layerName} ({sumlevel}) from {url}")

            # Construct a list of geoids from data to us to query API
            geoids = ",".join([f"'{x.split('US')[-1]}" for x in geoidfqs if x.startswith(sumlevel)])

            logger.info(f"There are {len(geoids)} geographies in {layerName}")
            logger.debug(f"{', '.join(geoidfqs)}")

            # Build resource file and query API
            logger.info(f"Building resource file to fetch from RestAPI.")
            resource = morpc.rest_api.resource(name='temp', url=url, where= f"GEOID in ({geoids})", outfields='GEOID', max_record_count=chunk_size)
            logger.debug(f"{resource}")
            logger.info(f"Fetching geographies from RestAPI.")
            geos = morpc.rest_api.gdf_from_resource(resource)

            all_geometries.append(geos)

    logger.info("Combining geometries...")
    geometries = pd.concat(all_geometries)
    geometries = geometries.rename(columns={'GEOID': 'GEO_ID'})

    return gpd.GeoDataFrame(geometries, geometry='geometry')

def fetch_geos_from_scale_scope(scope, scale=None, year=None, survey='current', chunk_size=500):
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

    geoinfo = geoinfo_from_scope_scale(scope, scale, output='table')
    geoinfo['GEOIDFQ'] = geoinfo['GEO_ID']
    geoinfo['GEO_ID'] = [x.split('US')[-1] for x in geoinfo['GEO_ID']]
    geos = fetch_geos_from_geoids(geoinfo['GEOIDFQ'].to_list(), year, survey, chunk_size=chunk_size)

    try:
        geos = geos.set_index('GEO_ID').join(geoinfo.set_index('GEO_ID')).reset_index()
        geos = geos.loc[~geos['geometry'].isna()]
    except Exception as e:
        logger.error(f"Unable to join geoinfo to geos, returning only geos.")

    return geos

def morpc_juris_part_to_full(geoidSeries, validateTranslation=True, gitRootPath="../"):
    """Given a series of fully-qualified MORPC GEOIDs representing county parts of MORPC jurisdictions (i.e. SUMLEVEL
    M11 or M25), this function provides a dataframe which maps each part to its parent jurisdiction (M10 or M24, respectively).

    Parameters
    ----------
    geoidSeries : pandas.core.series.Series
        A Pandas Series object which contains a list of MORPC GEOIDs. GEOIDs must belong to a single SUMLEVEL. The following 
        SUMLEVELs are supported:
            M11 - County parts for active and prospective MORPC member jurisdictions, including non-incorporated townships and
                  parts of cities and villages.  These geographies are defined using Census-maintained (i.e. TIGER) boundaries.
                  Also known as "JURIS-COUNTY" geos.
            M25 - Like M11, these are county parts of cities, villages, and non-incorporated townships, however these are defined 
                  using MORPC-maintained boundaries rather than Census boundaries.  Also known as "JURIS-COUNTY-MORPC" geos.
    validateTranslation : bool
        When validateTranslation is True (default), the function will attempt to validate the provided list of GEOIDs using the 
        lookup table output from the morpc-geos-collect workflow prior to attempting to map them to their parents.  If validateTranslation 
        is False or if the lookup table is not available, the function will attempt a naive mapping of the GEOID, however the 
        resulting parent GEOID may not be valid.  The lookup table is located via gitRootPath (see below).
    gitRootPath : str
        The path to a folder containing the Git repository for the morpc-geos-collect workflow. Defaults to the parent 
        directory ("../").  .

    Returns
    -------
    mappingDataFrame : pandas.core.frame.DataFrame
        A Pandas DataFrame object which maps each of the input MORPC GEOIDs to its parent MORPC GEOID.

    """
    import pandas as pd
    import logging
    import os
    import morpc

    logger  = logging.getLogger(__name__)    

    supportedSumlevels = ["M11","M25"]

    # Create a copy of the user-provided series that we can manipulate. Preserve the name of the series so we can name
    # the returned series accordingly
    myGeoidSeries = geoidSeries.copy()
    myGeoidSeries.name = "GEOIDFQ"

    # Convert the series to a dataframe and extract the original sumlevels. Create a field to capture the
    # translated GEOID
    df = pd.DataFrame(myGeoidSeries)
    df["SUMLEVEL_ORIG"] = df["GEOIDFQ"].apply(lambda x:x[0:3])
    df["GEOIDFQ_PARENT"] = None
    df["GEOIDFQ_PARENT"] = df["GEOIDFQ_PARENT"].astype("string")
    df = df.set_index("GEOIDFQ")

    # Verify that only a single SUMLEVEL is represented among the provided GEOIDs
    includedSumlevels = df["SUMLEVEL_ORIG"].unique()
    if(len(includedSumlevels) > 1):
        logger.error(f"Detected multiple SUMLEVELs among input GEOIDs. GEOIDs must belong to a single SUMLEVEL (i.e. one of the following: {','.join(supportedSumlevels)})")
        raise RuntimeError

    # Assuming we made it this far, we can extract the single input SUMLEVEL
    includedSumlevel = includedSumlevels[0]
    
    # Verify that the SUMLEVELs for the user-provided GEOIDs are all supported
    if(not includedSumlevel in supportedSumlevels):
        logger.error(f"SUMLEVEL {includedSumlevel} is not supported. Supported sumlevels are {','.join(supportedSumlevels)}")
        raise RuntimeError

    # Try to load the geography lookup table output from the morpc-geos-collect workflow from a local copy of the repository
    # to be found in a subdirectory of gitRootPath. This is the authoritative list of geographies known to MORPC. If a GEOID
    # is not listed here it may be invalid. If the attempt to load the lookup table fails, flag the translation as naive
    # and warn the user.
    naiveTranslation = True
    if(validateTranslation == True):
        try:
            morpcGeosLookupPath = os.path.join(os.path.normpath(gitRootPath), "morpc-geos-collect", "output_data", "morpc-geos-lookup.resource.yaml")
            logger.info(f"Attempting to load MORPC geography lookup table from path: {morpcGeosLookupPath}")
            (morpcGeosLookup, morpcGeosLookupResource, morpcGeosLookupSchema) = morpc.frictionless.load_data(morpcGeosLookupPath)
            morpcGeosLookup = morpcGeosLookup.set_index("GEOIDFQ")
            # Add a "VALID" flag to the records in the table. When joined to the user-provided GEOIDs, a missing flag will
            # indicate that the GEOID was not found in the lookup table.
            morpcGeosLookup["VALID"] = True
            morpcGeosLookup["VALID"] = morpcGeosLookup["VALID"].astype("bool")
            naiveTranslation = False
        except Exception as e:
            logger.warning("Failed to MORPC geography lookup table. GEOID mappings will be naive (not validated). {e}")
    else:
        logger.warning("Not attempting to validate translations per user instruction. GEOID mappings will be naive.")

    # If the user requested to validate the GEOIDs and we were able to load the lookup table, join the VALID
    # flag from the lookup table for each user-provided GEOID that appears in the lookup table. If some GEOIDs
    # did not appear in the lookup table, warn the user and continue.
    if(not naiveTranslation):            
        df = df.join(morpcGeosLookup["VALID"])
        missingIndex = df.loc[df["VALID"] != True].index
        if(not len(missingIndex) == 0):
            logger.warn("The following GEOIDs were not found in the MORPC geography lookup table and may be invalid.  If so, their mappings will also be invalid.")
            logger.warn(f"Missing GEOIDs: {",".join(list(missingIndex))}")
        df = df.drop(columns="VALID")

    if(includedSumlevel == "M11"):
        parentSumlevel = "M10"
    elif(includedSumlevel == "M25"):
        parentSumlevel = "M24"
    else:
        logger.error(f"SUMLEVEL {includedSumlevel} is not supported. Supported sumlevels are {','.join(supportedSumlevels)}")
        raise RuntimeError

    logger.info(f"Mapping provided geographies in SUMLEVEL {includedSumlevel} ({morpc.HIERARCHY_STRING_LOOKUP[includedSumlevel]}) to parent geographies in SUMLEVEL {parentSumlevel} ({morpc.HIERARCHY_STRING_LOOKUP[parentSumlevel]})")
        
    df = df.reset_index()
    # Identify townships. Township GEOIDs end in 99999
    df["TOWNSHIP"] = df["GEOIDFQ"].str.endswith("99999")
    # Modify the GEOIDs for ALL geographies by changing the SUMLEVEL
    df["GEOIDFQ_PARENT"] = df["GEOIDFQ"].str.slice_replace(start=0, stop=3, repl=parentSumlevel)
    # Modify the GEOIDs for the NON-township geographies only (i.e. cities and villages). In this case we need to remove the 
    # three-digit suffix that specifies the county that the part belongs to.
    df.loc[df["TOWNSHIP"] != True, "GEOIDFQ_PARENT"] = df["GEOIDFQ_PARENT"].str.slice_replace(start=-3)
    
    # Check for null values in the translated GEOIDs. Throw an error if any appear.
    failedTranslationIndex = df.loc[df["GEOIDFQ_PARENT"].isna()].index
    if(len(failedTranslationIndex) > 0):
        logger.error(f"Translation failed for the following geographies: {list(failedTranslationIndex)}")
        raise RuntimeError

    df = df.filter(items=["GEOIDFQ","GEOIDFQ_PARENT"], axis="columns")

    # If the user requested to validate the GEOIDs and we were able to load the lookup table, join the VALID
    # flag from the lookup table for each parent GEOID that appears in the lookup table. If some GEOIDs
    # did not appear in the lookup table, warn the user and continue.
    if(not naiveTranslation):            
        df = df.merge(morpcGeosLookup["VALID"], left_on="GEOIDFQ_PARENT", right_on="GEOIDFQ")
        missingIndex = df.loc[df["VALID"] != True].index
        if(not len(missingIndex) == 0):
            logger.warn("The following parent GEOIDs were not found in the MORPC geography lookup table and may be invalid.")
            logger.warn(f"Missing parent GEOIDs: {",".join(list(missingIndex))}")
        df = df.drop(columns="VALID")
    
    mappingDataFrame = df.copy()
    
    return mappingDataFrame
    
def census_geoid_to_morpc(geoidSeries, targetSumlevel, validateTranslation=True, gitRootPath="../", verbose=False):
    """Given a series of fully-qualified Census GEOIDs and a target MORPC SUMLEVEL, this function translates each GEOID in 
    the series to its equivalent MORPC GEOID.  MORPC maintains a set of fully-qualified geographic identifiers (GEOIDFQs) 
    that mimic the fully qualified GEOIDs used by the Census Bureau. Similar to Census GEOIDFQs, MORPC GEOIDFQs have the form 
    XXX0000USYYYYYYYY, where XXX reflects the three-digit geographic summary level (SUMLEVEL) of the geography, "0000US" is a 
    string literal which means nothing but is included to mimic Census GEOIDFQs, and YYYYYYYY short-form GEOID for each geography
    that is unique within the SUMLEVEL and whose length and composition depends on the SUMLEVEL. For cases where a MORPC geography
    corresponds to a Census geography, the short-form GEOID must match the Census geography, however a MORPC SUMLEVEL may be
    comprised of geographies from multiple Census SUMLEVELs. Nonetheless, the short-form GEOID must still be unique within
    the MORPC SUMLEVEL.  There is a one-to-many mapping between a Census GEOID and MORPC GEOIDs, therefore it is necessary to
    specify the target SUMLEVEL for the desired MORPC GEOIDs.

    See also morpc.census.geos.morpc_geoid_to_census()
    
    Parameters
    ----------
    geoidSeries : pandas.core.series.Series
        A Pandas Series object which contains a list of Census GEOIDs. GEOIDs from multiple SUMLEVELs may be 
        included. The included GEOIDs must translate to a single MORPC SUMLEVEL, as specified by targetSumlevel (see below). 
        The Census SUMLEVELs which may be included vary depending on the MORPC SUMLEVEL.
    targetSumlevel : str
        A three-digit string designating the MORPC SUMLEVEL to use when translating the Census GEOIDs.  The following SUMLEVELs
        are supported:
            M10 - Active and prospective MORPC member jurisdictions, including whole cities and villages (Census SUMLEVEL 160),
                  and non-incorporated townships (Census SUMLEVEL 070).  Non-incorporated townships are assumed to be fully 
                  contained in a single county. As of March 2026, there are some cases where townships span county boundaries, 
                  however in each of these cases the out-of-county portion of the township is coterminus with a city or village 
                  and thus the incorporated place takes precedence. These geographies are defined using Census-maintained (i.e. TIGER) 
                  boundaries. Also known as "JURIS" geos.
            M11 - County parts for active and prospective MORPC member jurisdictions, including non-incorporated townships (Census
                  SUMLEVEL 070) and parts of cities and villages (Census SUMLEVEL 155).  These geographies are defined using Census-
                  maintained (i.e. TIGER) boundaries. Also known as "JURIS-COUNTY" geos.
            M23 - These are whole counties (like Census SUMLEVEL 050), however they are defined using MORPC-maintained boundaries
                  rather than Census boundaries. Also known as "COUNTY-MORPC" geos.
            M24 - Like M10, these are whole cities, villages, and non-incorporated townships, however these are defined using
                  MORPC-maintained boundaries rather than Census boundaries.  Also known as "JURIS-MORPC" geos.
            M25 - Like M11, these are county parts of cities, villages, and non-incorporated townships, however these are defined 
                  using MORPC-maintained boundaries rather than Census boundaries.  Also known as "JURIS-COUNTY-MORPC" geos.
    validateTranslation : bool
        When validateTranslation is True (default), the function will attempt to validate the provided list of GEOIDs using the 
        lookup table output from the morpc-geos-collect workflow prior to attempting to translate them.  If validateTranslation 
        is False or if the lookup table is not availble, the function will attempt a naive translation of the GEOID, however the 
        resulting GEOID may not be valid.  The lookup table is located via gitRootPath (see below).
    gitRootPath : str
        The path to a folder containing the Git repository for the morpc-geos-collect workflow. Defaults to the parent 
        directory ("../").  .
    verbose : bool
        Set verbose to True to increase logging output from the function.

    Returns
    -------
    mappingDataFrame : pandas.core.frame.DataFrame
        A Pandas DataFrame object which maps each of the input Census GEOIDs to its MORPC equivalent in the context of the 
        specified target SUMLEVEL.
    """
    import pandas as pd
    import logging
    import os
    import morpc

    logger  = logging.getLogger(__name__)    

    supportedSumlevels = ["M10","M11","M23","M24","M25"]

    sumlevelMap = {
        "M10": [morpc.SUMLEVEL_LOOKUP["COUNTY-TOWNSHIP-REMAINDER"], morpc.SUMLEVEL_LOOKUP["PLACE"]],
        "M11": [morpc.SUMLEVEL_LOOKUP["COUNTY-TOWNSHIP-REMAINDER"], morpc.SUMLEVEL_LOOKUP["PLACE-COUNTY"]],
        "M23": [morpc.SUMLEVEL_LOOKUP["COUNTY"]],
        "M24": [morpc.SUMLEVEL_LOOKUP["COUNTY-TOWNSHIP-REMAINDER"], morpc.SUMLEVEL_LOOKUP["PLACE"]],
        "M25": [morpc.SUMLEVEL_LOOKUP["COUNTY-TOWNSHIP-REMAINDER"], morpc.SUMLEVEL_LOOKUP["PLACE-COUNTY"]]
    }
    
    # Verify that the user-specified target SUMLEVEL is supported
    if(not targetSumlevel in supportedSumlevels):
        logger.error(f"SUMLEVEL {sumlevel} is not supported. Supported sumlevels are {','.join(supportedSumlevels)}")
        raise RuntimeError
    
    # Create a copy of the user-provided series that we can manipulate. Preserve the name of the series so we can name
    # the returned series accordingly
    myGeoidSeries = geoidSeries.copy()
    myGeoidSeries.name = "GEOIDFQ"

    # Convert the series to a dataframe and extract the original sumlevels. Create a field to capture the
    # translated GEOID
    df = pd.DataFrame(myGeoidSeries)
    df["SUMLEVEL_ORIG"] = df["GEOIDFQ"].apply(lambda x:x[0:3])
    df["GEOIDFQ_MORPC"] = None
    df["GEOIDFQ_MORPC"] = df["GEOIDFQ_MORPC"].astype("string")
    df = df.set_index("GEOIDFQ")

    # Check the Census SUMLEVELs present in the series to make sure they have equivalents in the user-specified target
    # SUMLEVEL. If the set of SUMLEVELs included in the series is not a subset of the possible Census SUMLEVELS in the
    # target MORPC SUMLEVEL, then throw an error.
    if(not (set(df["SUMLEVEL_ORIG"].unique()) <= set(sumlevelMap[targetSumlevel]))):
        logger.error(f"The user-provided series includes geographies in the following SUMLEVEL(s) which do not have equivalent geographies in the target SUMLEVEL ({targetSumlevel}): {",".join(list(set(df["SUMLEVEL_ORIG"].unique()) - set(sumlevelMap[targetSumlevel])))}")
        raise RuntimeError
    
    # Try to load the geography lookup table output from the morpc-geos-collect workflow from a local copy of the repository
    # to be found in a subdirectory of gitRootPath. This is the authoritative list of geographies known to MORPC. If a GEOID
    # is not listed here it may be invalid. If the attempt to load the lookup table fails, flag the translation as naive
    # and warn the user.
    naiveTranslation = True
    if(validateTranslation == True):
        try:
            morpcGeosLookupPath = os.path.join(os.path.normpath(gitRootPath), "morpc-geos-collect", "output_data", "morpc-geos-lookup.resource.yaml")
            logger.info(f"Attempting to load MORPC geography lookup table from path: {morpcGeosLookupPath}")
            (morpcGeosLookup, morpcGeosLookupResource, morpcGeosLookupSchema) = morpc.frictionless.load_data(morpcGeosLookupPath)
            morpcGeosLookup = morpcGeosLookup.set_index("GEOIDFQ")
            # Add a "VALID" flag to the records in the table. When joined to the user-provided GEOIDs, a missing flag will
            # indicate that the GEOID was not found in the lookup table.
            morpcGeosLookup["VALID"] = True
            morpcGeosLookup["VALID"] = morpcGeosLookup["VALID"].astype("bool")
            naiveTranslation = False
        except Exception as e:
            logger.warning(f"Failed to MORPC geography lookup table. GEOID translations will be naive (not validated). {e}")
    else:
        logger.warning("Not attempting to validate translations per user instruction. GEOID translations will be naive.")

    # If the user requested to validate the GEOIDs and we were able to load the lookup table, join the VALID
    # flag from the lookup table for each user-provided GEOID that appears in the lookup table. If some GEOIDs
    # did not appear in the lookup table, warn the user and continue.
    if(not naiveTranslation):            
        df = df.join(morpcGeosLookup["VALID"])
        missingIndex = df.loc[df["VALID"] != True].index
        if(not len(missingIndex) == 0):
            logger.warn("The following GEOIDs were not found in the MORPC geography lookup table and may be invalid.  If so, their translations will also be invalid.")
            logger.warn(f"Missing GEOIDs: {",".join(list(missingIndex))}")
        df = df.drop(columns="VALID")

    # Since we've already verified that all of the user-provided geographies have an equivalent in the target SUMLEVEL, we can simply replace
    # the SUMLEVEL portion of their GEOIDs all at once.
    df = df.reset_index()
    df["GEOIDFQ_MORPC"] = df["GEOIDFQ"].str.slice_replace(start=0, stop=3, repl=targetSumlevel)

    # Check for null values in the translated GEOIDs. Throw an error if any appear.
    failedTranslationIndex = df.loc[df["GEOIDFQ_MORPC"].isna()].index
    if(len(failedTranslationIndex) > 0):
        logger.error(f"Translation failed for the following geographies: {list(failedTranslationIndex)}")
        raise RuntimeError
        
    df = df.filter(items=["GEOIDFQ","GEOIDFQ_MORPC"], axis="columns")

    # If the user requested to validate the GEOIDs and we were able to load the lookup table, join the VALID
    # flag from the lookup table for each parent GEOID that appears in the lookup table. If some GEOIDs
    # did not appear in the lookup table, warn the user and continue.
    if(not naiveTranslation):            
        df = df.merge(morpcGeosLookup["VALID"], left_on="GEOIDFQ_MORPC", right_on="GEOIDFQ", how="left")
        missingGeoids = df.loc[df["VALID"] != True, "GEOIDFQ_MORPC"]
        if(not len(missingGeoids) == 0):
            logger.warn(f"The following GEOIDs were not found in the MORPC geography lookup table and may be invalid: {','.join(list(missingGeoids))}")
        df = df.drop(columns="VALID")
    
    mappingDataFrame = df.copy().rename(columns={"GEOIDFQ":geoidSeries.name})
    
    return mappingDataFrame
    
def morpc_geoid_to_census(geoidSeries, validateTranslation=True, gitRootPath="../", verbose=False):
    """Given a series of fully-qualified MORPC GEOIDs, this function translates each GEOID in the series to its equivalent
    Census GEOID.  MORPC maintains a set of fully-qualified geographic identifiers (GEOIDFQs) that mimic the fully qualified 
    GEOIDs used by the Census Bureau. Similar to Census GEOIDFQs, MORPC GEOIDFQs have the form XXX0000USYYYYYYYY, where XXX 
    reflects the three-digit geographic summary level (SUMLEVEL) of the geography, "0000US" is a string literal which 
    means nothing but is included to mimic Census GEOIDFQs, and YYYYYYYY short-form GEOID for each geography that is 
    unique within the SUMLEVEL and whose length and composition depends on the SUMLEVEL. For cases where a MORPC geography
    corresponds to a Census geography, the short-form GEOID must match the Census geography, however a MORPC SUMLEVEL may be
    comprised of geographies from multiple Census SUMLEVELs. Nonetheless, the short-form GEOID must still be unique within
    the MORPC SUMLEVEL.

    See also morpc.census.geos.census_geoid_to_morpc()
    
    Parameters
    ----------
    geoidSeries : pandas.core.series.Series
        A Pandas Series object which contains a list of MORPC GEOIDs. GEOIDs from multiple SUMLEVELs may be 
        included, in which case each SUMLEVEL will be handled separately.  The following SUMLEVELs are supported:
            M10 - Active and prospective MORPC member jurisdictions, including whole cities, villages, and non-incorporated
                  townships.  Non-incorporated townships are assumed to be fully contained in a single county. As of March 2026,
                  there are some cases where townships span county boundaries, however in each of these cases the out-of-county
                  portion of the township is coterminus with a city or village and thus the incorporated place takes precedence.
                  These geographies are defined using Census-maintained (i.e. TIGER) boundaries. Also known as "JURIS" geos.
            M11 - County parts for active and prospective MORPC member jurisdictions, including non-incorporated townships and
                  parts of cities and villages.  These geographies are defined using Census-maintained (i.e. TIGER) boundaries.
                  Also known as "JURIS-COUNTY" geos.
            M23 - These are whole counties (like Census SUMLEVEL 050), however they are defined using MORPC-maintained boundaries
                  rather than Census boundaries. Also known as "COUNTY-MORPC" geos.
            M24 - Like M10, these are whole cities, villages, and non-incorporated townships, however these are defined using
                  MORPC-maintained boundaries rather than Census boundaries.  Also known as "JURIS-MORPC" geos.
            M25 - Like M11, these are county parts of cities, villages, and non-incorporated townships, however these are defined 
                  using MORPC-maintained boundaries rather than Census boundaries.  Also known as "JURIS-COUNTY-MORPC" geos.
    validateTranslation : bool
        When validateTranslation is True (default), the function will attempt to validate the provided list of GEOIDs using the 
        lookup table output from the morpc-geos-collect workflow prior to attempting to translate them.  If validateTranslation 
        is False or if the lookup table is not availble, the function will attempt a naive translation of the GEOID, however the 
        resulting GEOID may not be valid.  The lookup table is located via gitRootPath (see below).
    gitRootPath : str
        The path to a folder containing the Git repository for the morpc-geos-collect workflow. Defaults to the parent 
        directory ("../").  .
    verbose : bool
        Set verbose to True to increase logging output from the function.

    Returns
    -------
    mappingDataFrame : pandas.core.frame.DataFrame
        A Pandas DataFrame object which maps each of the input MORPC GEOIDs to its Census equivalent

    """
    import pandas as pd
    import logging
    import morpc
    import os

    logger  = logging.getLogger(__name__)    

    supportedSumlevels = ["M10","M11","M23","M24","M25"]

    # Create a copy of the user-provided series that we can manipulate. Preserve the name of the series so we can name
    # the returned series accordingly
    myGeoidSeries = geoidSeries.copy()
    myGeoidSeries.name = "GEOIDFQ"

    # Convert the series to a dataframe and extract the original sumlevels. Create a field to capture the
    # translated GEOID
    df = pd.DataFrame(myGeoidSeries)
    df["SUMLEVEL_ORIG"] = df["GEOIDFQ"].apply(lambda x:x[0:3])
    df["GEOIDFQ_CENSUS"] = None
    df["GEOIDFQ_CENSUS"] = df["GEOIDFQ_CENSUS"].astype("string")
    df = df.set_index("GEOIDFQ")

    # Verify that the SUMLEVELs for the user-provided GEOIDs are all supported
    for sumlevel in df["SUMLEVEL_ORIG"].unique():
        if(not sumlevel in supportedSumlevels):
            logger.error(f"SUMLEVEL {sumlevel} is not supported. Supported sumlevels are {','.join(supportedSumlevels)}")
            raise RuntimeError

    # Try to load the geography lookup table output from the morpc-geos-collect workflow from a local copy of the repository
    # to be found in a subdirectory of gitRootPath. This is the authoritative list of geographies known to MORPC. If a GEOID
    # is not listed here it may be invalid. If the attempt to load the lookup table fails, flag the translation as naive
    # and warn the user.
    naiveTranslation = True
    if(validateTranslation == True):
        try:
            morpcGeosLookupPath = os.path.join(os.path.normpath(gitRootPath), "morpc-geos-collect", "output_data", "morpc-geos-lookup.resource.yaml")
            logger.info(f"Attempting to load MORPC geography lookup table from path: {morpcGeosLookupPath}")
            (morpcGeosLookup, morpcGeosLookupResource, morpcGeosLookupSchema) = morpc.frictionless.load_data(morpcGeosLookupPath)
            morpcGeosLookup = morpcGeosLookup.set_index("GEOIDFQ")
            # Add a "VALID" flag to the records in the table. When joined to the user-provided GEOIDs, a missing flag will
            # indicate that the GEOID was not found in the lookup table.
            morpcGeosLookup["VALID"] = True
            morpcGeosLookup["VALID"] = morpcGeosLookup["VALID"].astype("bool")
            naiveTranslation = False
        except Exception as e:
            logger.warning("Failed to MORPC geography lookup table. GEOID translations will be naive (not validated). {e}")
    else:
        logger.warning("Not attempting to validate translations per user instruction. GEOID translations will be naive.")

    # If the user requested to validate the GEOIDs and we were able to load the lookup table, join the VALID
    # flag from the lookup table for each user-provided GEOID that appears in the lookup table. If some GEOIDs
    # did not appear in the lookup table, warn the user and continue.
    if(not naiveTranslation):            
        df = df.join(morpcGeosLookup["VALID"])
        missingIndex = df.loc[df["VALID"] != True].index
        if(not len(missingIndex) == 0):
            logger.warn("The following GEOIDs were not found in the MORPC geography lookup table and may be invalid.  If so, their translations will also be invalid.")
            logger.warn(f"Missing GEOIDs: {",".join(list(missingIndex))}")
        df = df.drop(columns="VALID")

    # We'll handle the collection of geographies in each SUMLEVEL separately. Iterate through the SUMLEVELs
    for sumlevel in df["SUMLEVEL_ORIG"].unique():
        if(verbose):
            logger.info(f"Processing geographies in SUMLEVEL {sumlevel} ({morpc.HIERARCHY_STRING_LOOKUP[sumlevel]})")
        # Extract only the records in this SUMLEVEL
        thisSumlevel = df.loc[df["SUMLEVEL_ORIG"] == sumlevel].copy().reset_index()
        if(sumlevel == "M10" or sumlevel == "M24"):
            if(verbose):
                logger.info(f"MORPC SUMLEVEL {sumlevel} is comprised of complete cities, villages, and non-incorporated townships.")
                logger.info(f"Substituting Census SUMLEVEL {morpc.SUMLEVEL_LOOKUP["COUNTY-TOWNSHIP-REMAINDER"]} for non-incorporated townships.")
                logger.info(f"Substituting Census SUMLEVEL {morpc.SUMLEVEL_LOOKUP["PLACE"]} for places (cities and villages.)")
            # Identify townships. Township GEOIDs end in 99999
            thisSumlevel["TOWNSHIP"] = thisSumlevel["GEOIDFQ"].str.endswith("99999")
            # Modify the GEOIDs for the township geographies
            thisSumlevel.loc[thisSumlevel["TOWNSHIP"] == True, "GEOIDFQ_CENSUS"] = morpc.SUMLEVEL_LOOKUP["COUNTY-TOWNSHIP-REMAINDER"] + thisSumlevel["GEOIDFQ"].str.removeprefix(sumlevel)
            # Modify the GEOIDs for the place (city, village) geographies
            thisSumlevel.loc[thisSumlevel["TOWNSHIP"] != True, "GEOIDFQ_CENSUS"] = morpc.SUMLEVEL_LOOKUP["PLACE"] + thisSumlevel["GEOIDFQ"].str.removeprefix(sumlevel)
            # Drop the township identifier flag
            thisSumlevel = thisSumlevel.drop(columns=["TOWNSHIP"])
            # Update the values for this SUMLEVEL only in the working dataframe
            df.update(thisSumlevel.set_index("GEOIDFQ"))
        elif(sumlevel == "M11" or sumlevel == "M25"):
            if(verbose):
                logger.info(f"MORPC SUMLEVEL {sumlevel} is comprised of county parts of cities, villages, and non-incorporated townships.")
                logger.info(f"Substituting Census SUMLEVEL {morpc.SUMLEVEL_LOOKUP["COUNTY-TOWNSHIP-REMAINDER"]} for county parts of non-incorporated townships.")
                logger.info(f"Substituting Census SUMLEVEL {morpc.SUMLEVEL_LOOKUP["PLACE-COUNTY"]} for county parts of places (cities and villages).")
            # Identify townships. Township GEOIDs end in 99999
            thisSumlevel["TOWNSHIP"] = thisSumlevel["GEOIDFQ"].str.endswith("99999")
            # Modify the GEOIDs for the township geographies
            thisSumlevel.loc[thisSumlevel["TOWNSHIP"] == True, "GEOIDFQ_CENSUS"] = morpc.SUMLEVEL_LOOKUP["COUNTY-TOWNSHIP-REMAINDER"] + thisSumlevel["GEOIDFQ"].str.removeprefix(sumlevel)
            # Modify the GEOIDs for the place (city, village) geographies
            thisSumlevel.loc[thisSumlevel["TOWNSHIP"] != True, "GEOIDFQ_CENSUS"] = morpc.SUMLEVEL_LOOKUP["PLACE-COUNTY"] + thisSumlevel["GEOIDFQ"].str.removeprefix(sumlevel)
            # Drop the township identifier flag
            thisSumlevel = thisSumlevel.drop(columns=["TOWNSHIP"])
            # Update the values for this SUMLEVEL only in the working dataframe
            df.update(thisSumlevel.set_index("GEOIDFQ"))
        elif(sumlevel == "M23"):
            if(verbose):
                logger.info(f"MORPC SUMLEVEL {sumlevel} is comprised of counties.")
                logger.info(f"Substituting Census SUMLEVEL {morpc.SUMLEVEL_LOOKUP["COUNTY"]} for counties.")
            # Modify the GEOIDs for all geos in this SUMLEVEL (all counties)
            thisSumlevel["GEOIDFQ_CENSUS"] = morpc.SUMLEVEL_LOOKUP["COUNTY"] + thisSumlevel["GEOIDFQ"].str.removeprefix(sumlevel)
            # Update the values for this SUMLEVEL only in the working dataframe
            df.update(thisSumlevel.set_index("GEOIDFQ"))
        else:
            # Included just for completeness. Unsupported sumlevels should have been caught earlier.
            logger.error(f"SUMLEVEL {sumlevel} is not supported. Supported sumlevels are {','.join(supportedSumlevels)}")
            raise RuntimeError

    # Check for null values in the translated GEOIDs. Throw an error if any appear.
    failedTranslationIndex = df.loc[df["GEOIDFQ_CENSUS"].isna()].index
    if(len(failedTranslationIndex) > 0):
        logger.error(f"Translation failed for the following geographies: {list(failedTranslationIndex)}")
        raise RuntimeError

    df = df.filter(items=["GEOIDFQ","GEOIDFQ_CENSUS"], axis="columns")

    # If the user requested to validate the GEOIDs and we were able to load the lookup table, join the VALID
    # flag from the lookup table for each parent GEOID that appears in the lookup table. If some GEOIDs
    # did not appear in the lookup table, warn the user and continue.
    if(not naiveTranslation):            
        df = df.merge(morpcGeosLookup["VALID"], left_on="GEOIDFQ_CENSUS", right_on="GEOIDFQ", how="left")
        missingGeoids = df.loc[df["VALID"] != True, "GEOIDFQ_CENSUS"]
        if(not len(missingGeoids) == 0):
            logger.warn(f"The following GEOIDs were not found in the MORPC geography lookup table and may be invalid: {','.join(list(missingGeoids))}")
        df = df.drop(columns="VALID")
    
    mappingDataFrame = df.copy().rename(columns={"GEOIDFQ":geoidSeries.name})
    
    return mappingDataFrame

def geoidfq_to_columns(geoidfqs: Series | DataFrame):
    import pandas as pd
    import re

    if isinstance(geoidfqs, pd.Series):
        logger.debug(f"Converting GEOIDFQs from Series")
        df = pd.DataFrame(geoidfqs, columns=['geoidfq']).set_index('geoidfq')
    else:
        df = geoidfqs
        if df.index.name in ['GEOIDFQ', 'geoidfq']:
            df = df.reset_index()
        df.columns = [x.lower() for x in df.columns]
        if 'geoidfq' not in df.columns:
            logger.error(f"GEOIDFQs not in DataFrame.")
            raise ValueError
        df = df.set_index('geoidfq')
        
    df['sumlevel'] = [x[0:3] for x in df.reset_index()['geoidfq']]
    df['variant'] = [x[3:5] for x in df.reset_index()['geoidfq']]
    df['geocomp'] = [x[5:7] for x in df.reset_index()['geoidfq']]

    sumlevel_dfs=[]
    sumlevels = list(set(df['sumlevel']))
    for sumlevel in sumlevels:
        logger.debug(f"Converting SUMLEVEL {sumlevel}")
        temp = df.loc[df['sumlevel']==sumlevel]
        temp = temp.drop(columns=temp.columns)
        template = morpc.SUMLEVEL_DESCRIPTIONS[sumlevel]['geoidfq_format']
        columns = [[y[0].lower(), y[1]] for y in [x.split(':') for x in re.findall(r'\{(.+?)\}', template)] if y[0] not in ['SUMLEVEL', 'VARIANT', 'GEOCOMP']]
        start = 9
        for column in columns:
            name = column[0]
            end = start + int(column[1])
            temp[name] = [x[start:end] for x in temp.reset_index()['geoidfq']]
            start = end
        sumlevel_dfs.append(temp)
    sumlevel_dfs = pd.concat(sumlevel_dfs)
    overlap = df.columns.intersection(sumlevel_dfs.columns)
    if len(overlap) > 0:
        logger.warning(f"Columns overlap: using columns from new columns {overlap}")
        df = df.drop(columns = overlap)
    df = df.join(sumlevel_dfs)
    geo_col = df.pop('geometry')
    df.insert(len(df.columns),'geometry', geo_col)


    return df
