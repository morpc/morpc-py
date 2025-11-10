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

HIGHLEVEL_GROUP_DESC = {
    "01": "Sex, Age, and Population",
    "02": "Race",
    "03": "Ethnicity",
    "04": "Ancestry",
    "05": "Nativity and Citizenship",
    "06": "Place of Birth",
    "07": "Geographic Mobility",
    "08": "Transportation to Work",
    "09": "Children",
    "10": "Grandparents and Grandchildren",
    "11": "Household Type",
    "12": "Marriage and Marital Status",
    "13": "Mothers and Births",
    "14": "School Enrollment",
    "15": "Educational Attainment",
    "16": "Language Spoken at Home",
    "17": "Poverty",
    "18": "Disability",
    "19": "Household Income",
    "20": "Earnings",
    "21": "Veterans",
    "22": "Food Stamps/SNAP",
    "23": "Workers and Employment Status",
    "24": "Occupation, Industry, Class",
    "25": "Housing Units, Tenure, Housing Costs",
    "26": "Group Quarters",
    "27": "Health Insurance",
    "28": "Computers and Internet",
    "29": "Voting-Age",
    "98": "Coverage Rates and Allocation Rates",
    "99": "Allocations",
}

MISSING_VALUES = ["","-222222222","-333333333","-555555555","-666666666","-888888888","-999999999", "*****"]

VARIABLE_TYPES = {
    "E": "estimate",
    "M": "moe",
    "PE": "percent_estimate",
    "PM": "percent_moe",
    "N": "total"
}

STANDARD_AGEGROUP_MAP = {
    'Under 5 years': 'Under 5 years',
    '5 to 9 years': '5 to 9 years',
    '10 to 14 years': '10 to 14 years',
    '15 to 17 years': '15 to 19 years',
    '18 and 19 years': '15 to 19 years',
    '20 years': '20 to 24 years',
    '21 years': '20 to 24 years',
    '22 to 24 years': '20 to 24 years',
    '25 to 29 years': '25 to 29 years',
    '30 to 34 years': '30 to 34 years',
    '35 to 39 years': '35 to 39 years',
    '40 to 44 years': '40 to 44 years',
    '45 to 49 years': '45 to 49 years',
    '50 to 54 years': '50 to 54 years',
    '55 to 59 years': '55 to 59 years',
    '60 and 61 years': '60 to 64 years',
    '62 to 64 years': '60 to 64 years',
    '65 and 66 years': '65 to 69 years',
    '67 to 69 years': '65 to 69 years',
    '70 to 74 years': '70 to 74 years',
    '75 to 79 years': '75 to 79 years',
    '80 to 84 years': '80 to 84 years',
    '85 years and over': '85 years and over'
}

AGEGROUP_SORT_ORDER = {
    'Under 5 years': 1,
    '5 to 9 years': 2,
    '10 to 14 years': 3,
    '15 to 19 years': 4,
    '20 to 24 years': 5,
    '25 to 29 years': 6,
    '30 to 34 years': 7,
    '35 to 39 years': 8,
    '40 to 44 years': 9,
    '45 to 49 years': 10,
    '50 to 54 years': 11, 
    '55 to 59 years': 12,
    '60 to 64 years': 13,
    '65 to 69 years': 14,
    '70 to 74 years': 15,
    '75 to 79 years': 16,
    '80 to 84 years': 17,
    '85 years and over': 18
}

CENSUS_DATA_BASE_URL = 'https://api.census.gov/data'

ALL_AVAIL_ENDPOINTS = {}
for x in get_json_safely(CENSUS_DATA_BASE_URL)['dataset']:
    if 'c_vintage' in x:
        endpoint = "/".join(x['c_dataset'])
        if endpoint not in ALL_AVAIL_ENDPOINTS:
            ALL_AVAIL_ENDPOINTS.update({endpoint: [x['c_vintage']]})
        else:
            ALL_AVAIL_ENDPOINTS[endpoint].append(x['c_vintage'])
ALL_AVAIL_ENDPOINTS = dict(sorted(ALL_AVAIL_ENDPOINTS.items()))

IMPLEMENTED_ENDPOINTS = [
    'acs/acs1',
    'acs/acs1/profile',
    'acs/acs1/subject',
    'acs/acs5',
    'acs/acs5/profile',
    'acs/acs5/subject',
    'dec/pl',
    'dec/dhc',
    'dec/ddhca',
    'dec/ddhcb',
    'dec/sf1',
    'dec/sf2',
    'dec/sf3',
]

def valid_survey_table(survey_table):
    logger.debug(f"Validating survey and table {survey_table}.")
    if survey_table in IMPLEMENTED_ENDPOINTS:
        logger.info(f"{survey_table} is valid and implemented.")
        return True
    else:
        logger.error(f"survey and table {survey_table} combination not available or not yet implemented.")
        raise ValueError(f"survey and table {survey_table} combination not available or not yet implemented.")

def valid_vintage(survey_table, year):
    logger.debug(f"Validating {survey_table} and {year}")
    if not isinstance(year, int):
        logger.debug(f'Year converted to integer from {type(year)}.')
        year = int(year)
    if year in ALL_AVAIL_ENDPOINTS[survey_table]:
        logger.info(f"{year} is valid vintage for {survey_table}")
        return True
    else:
        logger.error(f"{year} not an available vintage for {survey_table}")
        raise ValueError(f"{year} not an available vintage for {survey_table}")

def get_query_url(survey_table, year):
    url = f"{CENSUS_DATA_BASE_URL}/{year}/{survey_table}?"
    logger.info(f"Base URL for query is {url}")
    return url  

def get_table_groups(survey_table, year):
    logger.debug(f"Getting available variable groups for {year} {survey_table}")
    json = get_json_safely(f"{CENSUS_DATA_BASE_URL}/{year}/{survey_table}/groups.json")

    groups = {}
    for group in json['groups']:
        groups.update({
            group['name']: {
                'description': group['description'],
                'variables': group['variables'],
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
        raise ValueError(f"{group} is not a valid group in {year} {survey_table}")

def get_group_variables(survey_table, year, group):
    logger.debug(f"Getting list of variables for {group} in {year} {survey_table}.")
    json = get_json_safely(f"{CENSUS_DATA_BASE_URL}/{year}/{survey_table}/groups/{group}.json")

    variables = {k: json['variables'][k] for k in sorted(json['variables'].keys()) if k not in ['GEO_ID', 'NAME']}
    return variables

def valid_variables(survey_table, year, group, variables):
    logger.debug(f"Validating variables {variables}.")
    avail_variables = get_group_variables(survey_table, year, group)
    valid = True
    for variable in variables:
        if variable not in avail_variables:
            valid = False
            logger.error(f"{variable} not a valid variable in {group} survey {survey_table}")
            raise ValueError(f"{variable} not a valid variable in {group} survey {survey_table}")
    return valid

def get_params(survey_table, year, group, variables=None):

    logger.debug(f"Getting parameters to pass to get parameter.")
    if variables != None:
        get_param = f"GEO_ID,NAME,{",".join(variables)}"
    else:
        get_param = f"GEO_ID,NAME,group({group})"
    logger.info(f"'get' parameters for query are {get_param}")
    
    return get_param

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
    from morpc.census.geos import SCOPES

    logger.debug(f"Validating scope {scope} against implemented morpc.census.geos.SCOPES")
    if scope != None:
        if scope not in SCOPES:
            logger.error(f"Scope '{scope}' is not recognized. Available scopes: {list(SCOPES.keys())}")
            raise ValueError(f"Scope '{scope}' is not recognized. Available scopes: {list(SCOPES.keys())}")
        else:
            return True

def geo_params_from_scope_scale(scope, scale=None):
    from morpc.census.geos import SCOPES

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

def get(url, params, varBatchSize=20):
    """
    api_get() is a low-level wrapper for Census API requests that returns the results as a pandas dataframe. If necessary, it
    splits the request into several smaller requests to bypass the 50-variable limit imposed by the API.  The resulting dataframe
    is indexed by GEOID (regardless of whether it was requested) and omits other fields that are not requested but which are returned 
    automatically with each API request (e.g. "state", "county")

    Parameters
    ----------
    url : string
        url is the base URL of the desired Census API endpoint.  For example: https://api.census.gov/data/2022/acs/acs1

    params : dict 
        (in requests format) the parameters for the query string to be sent to the Census API. For example:

        {
            "get": "GEO_ID,NAME,B01001_001E",
            "for": "county:049,041",
            "in": "state:39"
        }

    varBatchSize : integer, default = 20
        representing the number of variables to request in each batch. 
        Defaults to 20, Limited to 49.

    Returns
    -------
    pandas.Dataframe
        dataframe indexed by GEO_ID and having a column for each requested variable
    """
    
    import json         # We need json to make a deep copy of the params dict
    from morpc.req import get_json_safely
    from morpc.census.api import get_group_variables
    import pandas as pd
    import re

    if len(re.findall(r'group\((.+)\)', params['get'])) == 0:
        # We need to reserve one variable in each batch for GEO_ID.  If the user requests more than 49 variables per
        # batch, reduce the batch size to 49 to respect the API limit
        if(varBatchSize > 49):
            logger.warning("Requested variable batch size exceeds API limit. Reducing batch size to 50 (including GEO_ID).")
            varBatchSize = 49
        
        # Extract a list of all of the requested variables from the request parameters
        allVars = params["get"].split(",")
        logger.info("Total variables requested: {}".format(len(allVars)))
        
        remainingVars = allVars
        requestCount = 1
        while(len(remainingVars) > 0):
            logger.info("Starting request #{0}. {1} variables remain.".format(requestCount, len(remainingVars)))

            # Create a short list of variables to download in this batch. Reserve one place for GEO_ID
            shortList = remainingVars[0:varBatchSize-2]
            # Check to see if GEO_ID was already included in the short list. If not, append it to the list.
            # If so, try to append another variable from the list of remaining variables.  In either case,
            # remove the items in the shortlist from the list of remaining variables.
            if(not "GEO_ID" in shortList):
                shortList.append("GEO_ID")
                remainingVars = remainingVars[varBatchSize-2:]
            else:
                try:
                    shortList.append(remainingVars[varBatchSize-2])
                except:
                    pass
                remainingVars = remainingVars[varBatchSize-1:]            

            # Create a set of API query parameters for this request. It will be a copy of the original parameters,
            # but with the list of variables replaced by the short list
            shortListParams = json.loads(json.dumps(params))
            shortListParams["get"] = ",".join(shortList)

            # Send the API request. Throw an error if the resulting status code indicates a failure condition.
            records = get_json_safely(url, params=shortListParams)
            
            # The first record is actually the column headers. Remove this from the list of records and keep it.
            columns = records.pop(0)
            
            # Construct a temporary pandas dataframe from the records
            df = pd.DataFrame.from_records(records, columns=columns)

            # Extract only the requested columns (plus GEO_ID) from the dataframe. This has the effect of removing
            # unrequested variables like "state" and "county"
            df = df.filter(items=shortList, axis="columns")
            
            # If this is our first request, construct the output dataframe by copying the temporary one. Otherwise,
            # join the temporary dataframe to the existing one using the GEO_ID.
            if(requestCount == 1):
                censusData = df.set_index("GEO_ID").copy()
            else:
                censusData = censusData.join(df.set_index("GEO_ID"))
            
            requestCount += 1
    else:
        logger.info('Found group parameter. Ignoring variable limits.')

        year = url.replace('https://api.census.gov/data/', '').replace('?','')[0:4]
        survey_table = url.replace('https://api.census.gov/data/', '').replace('?','')[5:]
        group = re.findall(r'group\((.+)\)', params['get'])[0]

        variables = get_group_variables(survey_table, year, group)

        vars = ['GEO_ID', 'NAME']
        for x in variables:
            vars.append(x) 

        records = get_json_safely(url, params=params)
        columns = records.pop(0)

        censusData = pd.DataFrame.from_records(records, columns=columns)
        censusData = censusData.filter(items=vars, axis='columns')

    return censusData.reset_index()

class CensusAPI:
    _CensusAPI_logger = logging.getLogger(__name__).getChild(__qualname__)
    def __init__(self, survey_table, year, group, scope, scale=None, variables=None):
        """
        Class for working with Census API Survey Data. Creates an object representing data for a variable by year by survey. 

        Parameters:
        ----------
        survey_table : str
            The survey table to use. For options see morpc.census.api.IMPLEMENTED_ENDPOINTS. 
            ex. 'acs/acs5/profile', 'acs/acs5', 'acs/acs1', 'dec/sf1',  'dec/pl'

        year : int
            The vintage year of the survey. ex. 2021, 2022, 2023. See morpc.census.api.ALL_AVAIL_ENDPOINTS for available years by survey.

        group : str
            The variable group to retrieve. ex. 'B01001' for age and sex. 
            For available groups see morpc.census.api.get_available_groups().
            ex. 'B01001', 'DP05', 'S0101'

        scope : str     
            The geographic scope to retrieve data for. See morpc.census.SCOPES for available scopes.
            ex. 'region15', 'us', 'ohio', 'franklin'

        scale : str (optional)
            The geographic scale to retrieve data for. 
            ex. 'block group', 'tract', 'county subdivision', 'county', 'state', 'metropolitan statistical area/micropolitan statistical area', 'division', 'us'. See morpc.census.SCALES for available scales.

        variables : list (optional)
            A list of specific variables to retrieve from the group. If None, all variables in the group are retrieved. 
            ex. ['B01001_001E', 'B01001_002E']

        Raises: 
            RuntimeError: Failed to validate parameters

        """
        from morpc.census import api
        
        self.NAME = f"census-{survey_table.replace("/","-")}-{year}-{"" if scale is None else scale + '-'}{scope}-{group}".lower()

        self.logger = logging.getLogger(__name__).getChild(self.__class__.__name__).getChild(self.NAME)

        self.logger.info(f"Initializing CENSUS_API_DATA object for {self.NAME}.")

        self.SURVEY = survey_table
        self.YEAR = year
        self.GROUP = group.upper()
        self.CONCEPT = api.get_table_groups(self.SURVEY, self.YEAR)[self.GROUP]['description']
        self.SCOPE = scope.lower() 
        if scale is not None:
            self.SCALE = scale.lower()
        else:
            self.SCALE = None
        if variables is not None:
            self.VARIABLES = [variable.upper() for variable in variables]
        else:
            self.VARIABLES = None
        
        self.validate()

        logger.info(f"Building Request URL and Parameters.")
        self.REQUEST = api.get_api_request(self.SURVEY, self.YEAR, self.GROUP, self.SCOPE, self.VARIABLES, self.SCALE)

        try:
            logger.info(f"Getting data from {self.REQUEST['url']} with parameters {self.REQUEST['params']}.")
            self.DATA = api.get(self.REQUEST['url'], self.REQUEST['params'])
        except Exception as e:
            self.logger.error(f"Error retrieving data: {e}")
            raise RuntimeError("Failed to retrieve data from Census API.")
        
        self.VARS = api.get_group_variables(self.SURVEY, self.YEAR, self.GROUP)
        if self.VARIABLES is not None:
            temp = {}
            for VAR in self.VARS:
                if VAR not in self.VARIABLES:
                    self.logger.debug(f"{VAR} not in list of variables for {self.GROUP}, removing from variable list.")
                if VAR in self.VARIABLES:
                    temp[VAR] = self.VARS[VAR]
            self.VARS = temp

        self.LONG = self.melt()

    def melt(self):
        """
        Method for melting the data into long format.

        Returns:
        -------
        pandas.DataFrame
            The melted data in long format with columns for GEO_ID, NAME, variable, value, and variable_type (estimate or moe),
            variable_label and reference_year.
        """
        import numpy as np
        import re

        logger.info(f"Melting data into long format.")

        long = self.DATA.melt(id_vars=['GEO_ID', 'NAME'], var_name='variable', value_name='value')
        long = long.loc[~long['value'].isna()]
        long = long.loc[~long['value'].isin(MISSING_VALUES)]
        long['variable_type'] = [re.findall(r"[0-9]+([A-Z]+)", x)[0] for x in long['variable']]
        long = long.loc[~long['variable_type'].str.endswith('A')]
        long['variable_type'] = [VARIABLE_TYPES[x] for x in long['variable_type']]

        long['variable_label'] = [re.split("!!", self.VARS[variable]['label'],maxsplit=1)[1] for variable in long['variable']]
        long['variable'] = [re.findall(r"([A-Z0-9_]+[0-9]+)[A-Z]+", x)[0] for x in long['variable']]

        long['reference_period'] = self.YEAR

        long = long.pivot(index=['GEO_ID', 'NAME', 'reference_period', 'variable_label', 'variable'], columns='variable_type', values='value').reset_index().rename_axis(None, axis=1)
        long = long.sort_values(by=['GEO_ID', 'variable'])

        return long
    
    def define_schema(self):
        """
        Creates a frictionless schema for Census data for a specified group and year.
        Raises:
            RuntimeError: Failed to validate the schema
            
        Returns:
            frictionless.Schema: A schema representing the fields in the api data.
        """
        import frictionless
        from frictionless import errors

        self.logger.info(f"Defining schema for {self.GROUP} for {self.SURVEY}-year survey in {self.YEAR}...")

        allFields = []
        # Add GEO_ID and NAME as default index fields as they are not included in the var list.
        allFields.append({"name":"GEO_ID", "type":"string", "description":"Unique identifier for geography"})
        allFields.append({"name":"NAME", "type":"string", "description":"Name of the geography"})
        allFields.append({"name":"reference_period", "type":"integer", "description":"Reference year for the data"})
        allFields.append({"name":"variable_label", "type":"string", "description":"Label describing the variable"})
        allFields.append({"name":"variable", "type":"string", "description":"Variable code"})

        # Create an entry for each field and apply friction data types.
        self.logger.info(f"Adding fields for value columns...")
        for column in self.LONG.columns:
            if column not in [field['name'] for field in allFields]:
                if column == 'estimate':
                    field = {"name":"estimate", "type":"number", "description":"Estimate value for the variable"}
                if column == 'moe':
                    field = {"name":"moe", "type":"number", "description":"Margin of error for the estimate"}
                if column == 'percent_estimate':
                    field = {"name":"percent_estimate", "type":"number", "description":"Percent estimate value for the variable"}
                if column == 'percent_moe':
                    field = {"name":"percent_moe", "type":"number", "description":"Margin of error for the percent estimate"}
                if column == 'total':
                    field = {"name":"total", "type":"integer", "description":"Total value for the variable"}
                if column not in ['estimate', 'moe', 'percent_estimate', 'percent_moe', 'total']:
                    self.logger.error(f"Unknown column {column} found in data. Cannot define schema.")
                    raise errors.SchemaError
                allFields.append(field)

        # Combine to construct the whole schema
        _Schema = {
            "fields": allFields,
            "missingValues": MISSING_VALUES,
            "primaryKey": ["GEO_ID", "reference_period", "variable"]
        }

        # Validate
        results = frictionless.Schema.validate_descriptor(_Schema)
        if(results.valid == True):
            self.logger.info(f"Schema is valid.")
        else:
            self.logger.error("Schema is NOT valid. Errors follow. {results}")
            raise errors.SchemaError

        return frictionless.Schema.from_descriptor(_Schema)
    
    def save(self, output_path):
        """
        Save data with schema and resource file to specified output path.

        Parameters:
        output_path : str
            The directory where to save the resource.

        """

        from morpc.frictionless import write_resource, validate_resource

        self.DATAPATH = output_path

        self.logger.info(f"Saving data to {output_path}...")

        self.FILENAME = f"{self.NAME}.long.csv"

        self.logger.info(f"Writing data to {output_path}/{self.FILENAME}.")
        self.LONG.to_csv(f"{output_path}/{self.FILENAME}", index=False)

        self.SCHEMA_PATH = f"{self.NAME}.schema.yaml"

        self.logger.info(f"Writing schema to {output_path}/{self.SCHEMA_PATH}.")
        self.SCHEMA = self.define_schema()
        self.SCHEMA.to_yaml(f"{output_path}/{self.SCHEMA_PATH}")

        self.logger.info(f"Creating resource for {self.NAME}...")
        resource = self.create_resource()

        self.logger.info(f"Writing resource to {output_path}/{self.NAME}.resource.yaml.")
        resource_path = f"{output_path}/{self.NAME}.resource.yaml"

        write_resource(resource, resource_path)

        self.logger.info(f"Validating resource at {resource_path}.")
        validate_resource(resource_path)

    
    def create_resource(self):
        """
        Creates a frictionless resource for the Census data.

        Returns:
            frictionless.Resource: A resource representing the Census data.
        """

        from morpc.frictionless import create_resource

        self.logger.info(f"Defining resource for {self.NAME}...")

        resource = create_resource(
            resourcePath=f"{self.DATAPATH}/{self.NAME}.resource.yaml",
            name=self.NAME,
            dataPath=self.FILENAME,
            title=f"{self.YEAR} {self.CONCEPT} for {f"{self.SCALE}s in " if self.SCALE != None else ""}{self.SCOPE}.",
            schemaPath=self.SCHEMA_PATH,
            description=f"Census API data for {self.GROUP}: {self.CONCEPT} from {self.SURVEY} survey in {self.YEAR} for {f"{self.SCALE}s in " if self.SCALE != None else ""}{self.SCOPE}.",
            sources=[
                {
                    "title": "Census API",
                    "path": self.REQUEST['url'],
                    "_params": self.REQUEST['params']
                }
            ],
            computeBytes=True,
            computeHash=True,
            resFormat="csv",
            resMediaType="text/csv",
            writeResource=False
        )

        return resource

    def validate(self):
        import morpc.census.api as api
        
        self.logger.info(f"Validating selected parameters")

        self.VALID = True
        if not api.valid_survey_table(self.SURVEY):
            self.VALID = False
        if not api.valid_vintage(self.SURVEY, self.YEAR):
            self.VALID = False
        if not api.valid_group(self.GROUP, self.SURVEY, self.YEAR):
            self.VALID = False
        if not api.valid_scope(self.SCOPE):
            self.VALID = False
        if self.SCALE is not None:
            if not api.valid_scale(self.SCALE):
                self.VALID = False
        if self.VARIABLES is not None:
            if not api.valid_variables(self.SURVEY, self.YEAR, self.GROUP, self.VARIABLES):
                self.VALID = False            
        if self.VALID == False:
            self.logger.error("One or more parameters are invalid. Please check the logs for details.")
            raise RuntimeError("Invalid parameters for CENSUS_API_DATA object initialization.")
        

class DimensionTable:
    _DimensionTable_logger = logging.getLogger(__name__).getChild(__qualname__)
    def __init__(self, CensusAPI_LONG):
        """
        Class for creating dimension tables from CensusAPI data in long format.

        Parameters:
        ----------
        CensusAPI : morpc.census.CensusAPI
            The CensusAPI object to create dimension tables from.
        """

        from uuid import uuid4
        self.LONG = CensusAPI_LONG.copy() # Store a copy of the data

        self.logger = logging.getLogger(__name__).getChild(self.__class__.__name__).getChild(str(uuid4()))
        self.logger.info(f"Initializing DIMENSION_TABLE object.")

    def wide(self):
        import pandas as pd

        self.logger.info(f"Pivoting data into wide format.")
        self.DESC_TABLE = self.create_description_table()

        wide = self.LONG.pivot(index='variable', columns=['GEO_ID', 'NAME', 'reference_period'], values='estimate')
        columns_levels = wide.columns.names
        wide.columns = wide.columns.to_list()
        wide = wide.join(self.DESC_TABLE)
        wide = wide.set_index([x for x in self.DESC_TABLE.columns])
        wide.columns = pd.MultiIndex.from_tuples(wide.columns)
        wide.columns.names = columns_levels
        wide = wide.sort_index(level='GEO_ID', axis=1)
        wide = wide.drop_duplicates()

        return wide

    def percent(self):

        self.WIDE = self.wide()
        
        self.logger.info(f"Creating percent table.")
        total = self.WIDE.T.iloc[:,0].copy()
        percent = self.WIDE.T.iloc[:,1:].copy()
        for column in percent:
            percent[column] = percent[column].astype(float) / total.astype(float) * 100
        
        return percent.T

    def create_description_table(self):
        """
        Method for creating a description table from variable labels.
        """
        import pandas as pd
        import numpy as np

        self.logger.info(f"Creating description table from variable labels.")
        var_df = self.LONG[['variable', 'variable_label']].drop_duplicates().set_index('variable')
        var_df = var_df.join(var_df['variable_label'].str.split("!!", expand=True)).drop(columns = 'variable_label')

        # Get a list of all unique values in the dataframe
        values = []
        for column in var_df.columns:
            for value in var_df[column]:
                if value not in values:
                    if value != None:
                        values.append(value)

        # Count occurrences of each value in each column
        var_columns = {}
        for var in values:
            var_columns[var] = {}
            for column in var_df.columns:
                if var in var_df[column].value_counts():
                    count = var_df[column].value_counts()[var]
                    var_columns[var][column] = count

        # Map each variable to the column where it appears most frequently
        column_map = {}
        for column in var_columns:
            column_map[column] = max(var_columns[column], key=var_columns[column].get)

        # Create a dataframe with the fixed columns
        var_df_fix = pd.DataFrame(dtype=str).reindex_like(var_df)
        for column in var_df_fix:
            var_df_fix[column] = None
            var_df_fix[column].astype(str)
        for i, row in var_df.iterrows():
            for j in range(len(row)):
                if row[j] not in column_map:
                    if row[j] != None:
                        var_df_fix.iloc[i,j] = row[j]
                else:
                    new_column = column_map[row[j]]
                    var_df_fix.loc[i,new_column] = row[j]

        var_df_fix = var_df_fix.replace(np.nan, "")

        return var_df_fix
    




            

                    


            
    



