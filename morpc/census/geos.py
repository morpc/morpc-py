import morpc

# TODO (jinskeep_morpc): Develop function for fetching census geographies leveraging scopes
# Issue URL: https://github.com/morpc/morpc-py/issues/102
#   The current geos-lookup workflow is limited by size and scope. This function will be used
#   to fetch geographies at any scale and scope without the need to store it locally. It is 
#   limited to census geographies. 
#   [ ]: Consider storing the data as a remote frictionless resource similar to the acs data class.
#   [ ]: Define scale and scopes that are used. Possibly lists for benchmarking (i.e. Most populous cities)


import requests

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

def psuedo_from_scale_scope(scale, scope, scope_scale):
    import morpc

    if validate_scale(scale):
        child = f"{morpc.SUMLEVEL_FROM_CENSUSQUERY[scale]}0000"
    
    if validate_scope(scope):
        params = params_from_scale_scope(scope_scale, scope)

    parents = geoids_from_params(params[0], params[1])

    psuedos = [f"{parent}${child}" for parent in parents]

    return psuedos
    
def get_query_req(sumlevel, year='2023'):
    """
    Fetches the query requirements for various geographic levels from the Census API.
    """
    r = requests.get(f"https://api.census.gov/data/{year}/geoinfo/geography.json")
    json = r.json()
    r.close()

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

    return query_requirements

def param_from_scope(scope):
    params = []
    for key in morpc.census.SCOPES[scope]:
        value = morpc.census.SCOPES[scope][key]
        if isinstance(value, str):
            params.append(f"{key}: {value}")
        if isinstance(value, list):
            params.append(f"{key}: {",".join(value)}")
    return params
        
def params_from_scale_scope(scale=None, scope=None):
    """
    Fetches UCGIDs from the Census API based on the specified geographic scale and scope.
    Parameters:
    ----------
    scale : str
        The geographic scale (e.g., 'county', 'tract', 'block group').
    scope : str
        The geographic scope (e.g., 'us', 'ohio', 'region15').
    
    Returns:
    -------
    list
        A list of UCGIDs corresponding to the specified scale and scope.
    
    Raises:
    ------
    ValueError
        If the provided scale or scope is not recognized, or if the scope does not satisfy
        the query requirements for the specified scale.

    """
    import morpc

    if scale != None:
    # Get available scales from morpc SUMLEVEL_DESCRIPTIONS
        available_scales = [morpc.SUMLEVEL_DESCRIPTIONS[x]['censusQueryName'] for x in morpc.SUMLEVEL_DESCRIPTIONS]

        # Validate inputs
        if scale not in available_scales:
            raise ValueError(f"Scale '{scale}' is not recognized. Available scales: {available_scales}")
    
    if scope != None:
        if scope not in SCOPES:
            raise ValueError(f"Scope '{scope}' is not recognized. Available scopes: {list(SCOPES.keys())}")
    
    sumlevel = morpc.SUMLEVEL_FROM_CENSUSQUERY[scale]

    for_params = f"{morpc.SUMLEVEL_DESCRIPTIONS[sumlevel]['censusQueryName']}:*"

    in_params = param_from_scope(scope)

    in_list = [x.split(':')[0] for x in in_params]

    # Get query requirements for the specified sumlevel
    query_requirements = get_query_req(sumlevel)

    # Check if the requirements are more than None
    if len([x for x in query_requirements.values() if x != None]) > 0:
        req_list = [value for values in query_requirements.values() for value in values]
        req_list.append(morpc.SUMLEVEL_DESCRIPTIONS[sumlevel]['censusQueryName'])
    else:
        req_list = [None]

    for x in in_list:
        if x not in req_list:
            print(f"{x} in 'in_params' but not in query requirements {req_list}. Invalid scope.")
            raise ValueError


    # Remove any overlapping parameters between 'for' and 'in'
    if for_params.split(':')[0] in in_list:
        for_params = in_params.pop(in_list.index(for_params.split(':')[0]))

    #  Add in wildcards if not in parameters.
    for wildcard in query_requirements['wildcard']:
        if wildcard not in in_list:
            in_params.append(f"{wildcard}:*")
            in_list.append(wildcard)
    
    # Check if in parameters meet requirements for scope.
    for req in query_requirements['requires']:
        if req not in in_list:
            raise ValueError(f"Parameter {in_list} does not satisfy the query requirement '{req}' for scale '{scale}'. Please choose a different scope.")

    return (for_params, in_params)

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
    
    json = morpc.req.get_json_safely(url, params = params)

    # Extract UCGIDs from the response
    ucgids = [x[0] for x in json[1:]]
    return ucgids

def geoids_from_psuedo(psuedos, year=2023):
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
        'ucgid': f"pseudo({",".join(psuedos)})"
    }
    
    json = morpc.req.get_json_safely(baseurl,params = params)

    # Extract UCGIDs from the response
    ucgids = [x[0] for x in json[1:]]
    return ucgids