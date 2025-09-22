import morpc

# TODO (jinskeep_morpc): Develop function for fetching census geographies leveraging scopes
# Issue URL: https://github.com/morpc/morpc-py/issues/102
#   The current geos-lookup workflow is limited by size and scope. This function will be used
#   to fetch geographies at any scale and scope without the need to store it locally. It is 
#   limited to census geographies. 
#   [ ]: Consider storing the data as a remote frictionless resource similar to the acs data class.
#   [ ]: Define scale and scopes that are used. Possibly lists for benchmarking (i.e. Most populous cities)


import requests

STATE_SCOPES = [{key: {f"state": f"{int(value):02d}"}} for key, value in morpc.CONST_STATE_NAME_TO_ID.items()]

COUNTY_SCOPES = [{key.lower(): {"state": "39", "county": f"{int(value[2:6]):03d}"}} for key, value in morpc.CONST_COUNTY_NAME_TO_ID.items()]

SCOPES = {
    "us": {
        "state": [f"{x:02d}" for x in morpc.CONST_STATE_ID_TO_NAME.keys()]
        },
    "region15": {
        "state": "39", 
        "county": [morpc.CONST_COUNTY_NAME_TO_ID[x][2:6] for x in morpc.CONST_REGIONS['15-County Region']]
        },
    "region10": {
        "state": "39",
        "county": [morpc.CONST_COUNTY_NAME_TO_ID[x][2:6] for x in morpc.CONST_REGIONS['10-County Region']]
        },
    "region7": {
        "state": "39",
        "county": [morpc.CONST_COUNTY_NAME_TO_ID[x][2:6] for x in morpc.CONST_REGIONS['7-County Region']]
        },
    "region-corpo": {
        "state": "39",
        "county": [morpc.CONST_COUNTY_NAME_TO_ID[x][2:6] for x in morpc.CONST_REGIONS["CORPO Region"]]
        },
    "regionmpo-members": {
        "ucgid": [
            '1550000US3902582041',
            '0700000US390410577499999',
            '0700000US390410578899999',
            '0700000US390410942899999',
            '1550000US3918000041',
            '0700000US390411814099999',
            '1550000US3921434041',
            '0700000US390412144899999',
            '1550000US3922694041',
            '1550000US3929148041',
            '0700000US390412969499999',
            '0700000US390413351699999',
            '0700000US390414036299999',
            '0700000US390414310699999',
            '0700000US390414790899999',
            '0700000US390415861899999',
            '1550000US3958940041',
            '0700000US390415926299999',
            '0700000US390416417899999',
            '1550000US3964486041',
            '0700000US390416531299999',
            '0700000US390417084299999',
            '1550000US3971976041',
            '1550000US3975602041',
            '0700000US390417661799999',
            '0700000US390417733699999',
            '0700000US390417756099999',
            '1550000US3983342041',
            '0700000US390450695099999',
            '1550000US3911332045',
            '1550000US3918000045',
            '1550000US3944086045',
            '1550000US3962498045',
            '1550000US3966390045',
            '0700000US390458020699999',
            '1550000US3906278049',
            '0700000US390490692299999',
            '1550000US3908532049',
            '0700000US390490944299999',
            '1550000US3911332049',
            '0700000US390491611299999',
            '1550000US3918000049',
            '1550000US3922694049',
            '0700000US390492828099999',
            '1550000US3929106049',
            '1550000US3931304049',
            '1550000US3932592049',
            '1550000US3932606049',
            '0700000US390493302699999',
            '1550000US3933740049',
            '1550000US3935476049',
            '0700000US390493777299999',
            '0700000US390493861299999',
            '1550000US3944086049',
            '1550000US3944310049',
            '0700000US390494641099999',
            '1550000US3947474049',
            '0700000US390495006499999',
            '1550000US3950862049',
            '1550000US3953970049',
            '0700000US390495734499999',
            '1550000US3957862049',
            '0700000US390496184099999',
            '1550000US3962498049',
            '0700000US390496297499999',
            '0700000US390496325499999',
            '0700000US390496457099999',
            '1550000US3966390049',
            '1550000US3967440049',
            '0700000US390497178799999',
            '0700000US390497771499999',
            '1550000US3979002049',
            '1550000US3979100049',
            '1550000US3979282049',
            '0700000US390498124299999',
            '1550000US3983342049',
            '1550000US3984742049',
            '1550000US3986604049',
            '0700000US390892569099999',
            '1550000US3939340089',
            '1550000US3953970089',
            '1550000US3961112089',
            '1550000US3966390089',
            '1550000US3963030097',
            '1550000US3922694159',
            '0700000US391593904699999',
            '1550000US3963030159'
            ]}
}

for x in STATE_SCOPES:
    SCOPES.update(x)

for x in COUNTY_SCOPES:
    SCOPES.update(x)

def get_query_req(sumlevel):
    """
    Fetches the query requirements for various geographic levels from the Census API.
    """
    r = requests.get("https://api.census.gov/data/2023/geoinfo/geography.json")
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

def in_param_from_scope(scope):
    params = []
    for key in morpc.census.SCOPES[scope]:
        value = morpc.census.SCOPES[scope][key]
        if isinstance(value, str):
            params.append(f"{key}: {value}")
        if isinstance(value, list):
            params.append(f"{key}: {",".join(value)}")
    return params
        
def params_from_scale_scope(scale, scope):
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

   # Get available scales from morpc SUMLEVEL_DESCRIPTIONS
    available_scales = [morpc.SUMLEVEL_DESCRIPTIONS[x]['censusQueryName'] for x in morpc.SUMLEVEL_DESCRIPTIONS]

    # Validate inputs
    if scale not in available_scales:
        raise ValueError(f"Scale '{scale}' is not recognized. Available scales: {available_scales}")
    
    if scope not in SCOPES:
        raise ValueError(f"Scope '{scope}' is not recognized. Available scopes: {list(SCOPES.keys())}")
    
    # Map scale to sumlevel code
    sumlevel = morpc.SUMLEVEL_FROM_CENSUSQUERY[scale]

    # Get query requirements for the specified sumlevel
    query_requirements = get_query_req(sumlevel)

    for_params = f"{morpc.SUMLEVEL_DESCRIPTIONS[sumlevel]['censusQueryName']}:*"

    in_params = in_param_from_scope(scope)

    in_list = [x.split(':')[0] for x in in_params]

    req_list = [value for values in query_requirements.values() for value in values]
    req_list.append(morpc.SUMLEVEL_DESCRIPTIONS[sumlevel]['censusQueryName'])

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

def geoids_from_params(for_params, in_params):
    
    # Fetch UCGIDs from the Census API
    r = requests.get(
        "https://api.census.gov/data/2023/geoinfo",
        params={
            "get": "GEO_ID",
            "for": for_params,
            "in": in_params
        }
    )

    if r.status_code != 200:
        raise requests.ConnectionError(f"Error querying {r.url}: Status Code {r.status_code}")

    # Handle potential JSON decoding errors
    try:
        json = r.json()
    except Exception as e:
        print(r.text)
        raise ValueError(f"Error fetching data from {r.url}: {e}")
    r.close()

    # Extract UCGIDs from the response
    ucgids = [x[0] for x in json[1:]]
    return ucgids


