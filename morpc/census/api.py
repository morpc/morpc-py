"""
Purpose: This module is used to access metadata and establish classes for US Census Bureau data. 

For more information on the workflow and use of this module see './doc/api module diagram.drawio'

Examples:

req = morpc.census.api.get_api_req('acs/acs5', 2023, 'B01001', 'region15', scale = 'tract', variables = 'B01001_001E')

morpc.req.get_json_safely(req)
"""

import logging

logger = logging.getLogger(__name__)

from morpc.req import get_json_safely

CENSUS_DATA_BASE_URL = 'https://api.census.gov/data'

ALL_AVAIL_ENDPOINTS = get_json_safely(CENSUS_DATA_BASE_URL)

IMPLEMENTED_ENDPOINTS = [
    'acs/acs1',
    'acs/acs1/profile',
    'acs/acs5',
    'acs/acs5/profile',
    'dec/pl',
    'geoinfo'
]

AVAIL_VINTAGES = {}
for endpoint in ALL_AVAIL_ENDPOINTS['dataset']:
    dataset = "/".join(endpoint['c_dataset'])
    if dataset in IMPLEMENTED_ENDPOINTS:
        vintage = endpoint['c_vintage']
        if dataset not in AVAIL_VINTAGES:
            AVAIL_VINTAGES.update({dataset: [vintage]})
        else:
            AVAIL_VINTAGES[dataset].append(vintage)

def valid_survey_table(survey_table):
    logger.debug(f"Validating survey and table {survey_table}.")
    if survey_table in IMPLEMENTED_ENDPOINTS:
        logger.info(f"{survey_table} is valid and implemented.")
        return True
    else:
        logger.error(f"survey and table {survey_table} combination not available or not yet implemented.")

def valid_vintage(survey_table, year):
    logger.debug(f"Validating {survey_table} and {year}")
    if not isinstance(year, int):
        logger.debug(f'Year converted to integer from {type(year)}.')
        year = int(year)
    if year in AVAIL_VINTAGES[survey_table]:
        logger.info(f"{year} is valid vintage for {survey_table}")
        return True
    else:
        logger.error(f"{year} not an available vintage for {survey_table}")

def get_query_url(survey_table, year):
    logger.debug(f"Building query url.")
    if valid_survey_table(survey_table):
        if valid_vintage(survey_table, year):
            url = f"{CENSUS_DATA_BASE_URL}/{year}/{survey_table}?"
            logger.info(f"Base URL for query is {url}")
    return url  

def get_table_groups(survey_table, year):
    logger.debug(f"Getting available variable groups for {year} {survey_table}")
    if valid_survey_table(survey_table):
        if valid_vintage(survey_table, year):
            json = get_json_safely(f"{CENSUS_DATA_BASE_URL}/{year}/{survey_table}/groups.json")

    groups = {}
    for group in json['groups']:
        groups.update({
            group['name']: {
                'description': group['description'],
                'variables': group['variables'],
                'universe': group['universe ']
            }
        })
    groups = dict(sorted(groups.items()))
    
    return groups

def valid_group(group, survey_table, year):
    logger.debug(f"Validating {group} for {year} {survey_table}.")
    groups = get_table_groups(survey_table, year)
    if group in groups.keys():
        logger.info(f"Group {group} valid group for {year} {survey_table}.")
        return True
    else:
        logger.error(f"{group} is not a valid group in {year} {survey_table}")

def get_group_variables(survey_table, year, group):
    logger.debug(f"Getting list of variables for {group} in {year} {survey_table}.")
    if valid_group(group, survey_table, year):
        json = get_json_safely(f"{CENSUS_DATA_BASE_URL}/{year}/{survey_table}/groups/{group}.json")

        variables = {k: json['variables'][k] for k in sorted(json['variables'].keys()) if k not in ['GEO_ID', 'NAME']}
    return variables

def valid_variables(survey_table, year, group, variables):
    logger.debug(f"Validating variables {variables}.")
    if valid_group(group, survey_table, year):
        avail_variables = get_group_variables(survey_table, year, group)
        valid = True
        for variable in variables:
            if variable not in avail_variables:
                valid = False
                logger.error(f"{variable} not a valid variable in {group} survey {survey_table}")
        return valid

def get_params(survey_table, year, group, variables=None):
    from morpc.census.acs import ACS_ID_FIELDS

    logger.debug(f"Getting parameters to pass to get parameter.")
    if valid_group(group, survey_table, year):
        if variables != None:
            if valid_variables(survey_table, year, group, variables):
                get_param = f"NAME,GEO_ID,{",".join(variables)}"
        else:
            get_param = f"NAME,GEO_ID,group({group})"
    logger.info(f"'get=' parameters for query are {get_param}")
    
    return get_param

def valid_scale(scale):
    from morpc import SUMLEVEL_DESCRIPTIONS

    logger.debug(f"Validating scale {scale} against implemented morpc.SUMLEVEL_DESCRIPTIONS.")
    # Get available scales from morpc SUMLEVEL_DESCRIPTIONS
    available_scales = [SUMLEVEL_DESCRIPTIONS[x]['censusQueryName'] for x in SUMLEVEL_DESCRIPTIONS if SUMLEVEL_DESCRIPTIONS[x]['censusQueryName'] != None]

    # Validate inputs
    if scale not in available_scales:
        logger.error(f"Scale '{scale}' is not recognized. Available scales: {available_scales}")
    else:
        return True
        
def valid_scope(scope):
    from morpc.census.geos import SCOPES

    logger.debug(f"Validating scope {scope} against implemented morpc.census.geos.SCOPES")
    if scope != None:
        if scope not in SCOPES:
            logger.error(f"Scope '{scope}' is not recognized. Available scopes: {list(SCOPES.keys())}")
        else:
            return True

def geo_params_from_scope_scale(scope, scale=None):
    from morpc.census.geos import SCOPES

    logger.debug(f"Building parameters to pass for geographies Scope: {scope} and Scale: {scale}")
    if scale == None:
        if valid_scope:
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
        else:
            logger.error(f'{scope} is not a valid scope.')

    return params

def geoids_from_scope(scope):
    from morpc.req import get_json_safely
    from morpc.census.geos import SCOPES

    logger.debug(f"Fetching geoids from scope parameters {SCOPES[scope]}.")
    if valid_scope:
        baseurl = "https://api.census.gov/data/2023/geoinfo?get=GEO_ID"
        json = get_json_safely(baseurl, params = SCOPES[scope])
        geoids = [row[0] for row in json[1:]]

        return geoids
    
def pseudos_from_scale_scope(scale, scope):
    from morpc import SUMLEVEL_FROM_CENSUSQUERY
    from morpc.census.geos import PSEUDOS

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

def get_api_request(survey_table, year, group, scope, variables=None, scale=None):

    logger.debug(f"Building final requests parameters and url.")
    url = get_query_url(survey_table, year)

    get_param = get_params(survey_table, year, group, variables=variables)

    geo_param = geo_params_from_scope_scale(scope, scale)

    params = {
        'get': get_param,
    }

    params.update(geo_param)

    req = {
        'url': url,
        'params': params
    }

    logger.info(f"api request as URL: {url} and PARAMETERS: {params}")
    return req
    

    
    



            

                    


            
    



