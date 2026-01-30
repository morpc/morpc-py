"""
Purpose: This module is used to access metadata and establish classes for US Census Bureau data. 

For more information on the workflow and use of this module see './doc/api module diagram.drawio'

Examples:

req = morpc.census.api.get_api_req('acs/acs5', 2023, 'B01001', 'region15', scale = 'tract', variables = 'B01001_001E')

morpc.req.get_json_safely(req)
"""

import logging
from types import NoneType

from numpy import var

logger = logging.getLogger(__name__)

from morpc.req import get_json_safely
from collections import OrderedDict

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

HIGHLEVEL_DESC_FROM_ID = {v: k for k, v in HIGHLEVEL_GROUP_DESC.items()}

MISSING_VALUES = ["","-222222222","-333333333","-555555555","-666666666","-888888888","-999999999", "*****"]

VARIABLE_TYPES = {
    "E": "estimate",
    "M": "moe",
    "PE": "percent_estimate",
    "PM": "percent_moe",
    "N": "total"
}

AGEGROUP_MAP = {
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
    'Total': 1,
    'Under 5 years': 2,
    '5 to 9 years': 3,
    '10 to 14 years': 4,
    '15 to 19 years': 5,
    '20 to 24 years': 6,
    '25 to 29 years': 7,
    '30 to 34 years': 8,
    '35 to 39 years': 9,
    '40 to 44 years': 10,
    '45 to 49 years': 11,
    '50 to 54 years': 12, 
    '55 to 59 years': 13,
    '60 to 64 years': 14,
    '65 to 69 years': 15,
    '70 to 74 years': 16,
    '75 to 79 years': 17,
    '80 to 84 years': 18,
    '85 years and over': 19
}

RACE_TABLE_MAP = {
    'A': 'White Alone',
    'B': 'Black or African American Alone',
    'C': 'American Indian and Alaska Native Alone',
    'D': 'Asian Alone',
    'E': 'Native Hawaiian and Other Pacific Islander Alone',
    'F': 'Some Other Race Alone',
    'G': 'Two or More Races',
    'H': 'White Alone, Not Hispanic or Latino',
    'I': 'Hispanic or Latino',
}

EDUCATION_ATTAIN_MAP = {
'No schooling completed': 'No high school diploma',
'Nursery school': 'No high school diploma',
'Kindergarten': 'No high school diploma',
'1st grade': 'No high school diploma',
'2nd grade': 'No high school diploma',
'3rd grade': 'No high school diploma',
'4th grade': 'No high school diploma',
'5th grade': 'No high school diploma',
'6th grade': 'No high school diploma',
'7th grade': 'No high school diploma',
'8th grade': 'No high school diploma',
'9th grade': 'No high school diploma',
'10th grade': 'No high school diploma',
'11th grade': 'No high school diploma',
'12th grade, no diploma': 'No high school diploma',
'Regular high school diploma': "High school diploma or equivalent",
'GED or alternative credential': "High school diploma or equivalent",
'Some college, less than 1 year': "High school diploma or equivalent",
'Some college, 1 or more years, no degree': "High school diploma or equivalent",
"Associate's degree": "Associate's degree",
"Bachelor's degree": "Bachelor's degree",
"Master's degree": "More than Bachelor's",
'Professional school degree': "More than Bachelor's",
'Doctorate degree': "More than Bachelor's"
}

EDUCATION_ATTAIN_SORT_ORDER = {
    'Total': 1,
    'No high school diploma': 2,
    "High school diploma or equivalent": 3,
    "Associate's degree": 4,
    "Bachelor's degree": 5,
    "More than Bachelor's": 6
}

def find_replace_variable_map(labels, variables, map, order):
    labels = list(labels)
    new_labels = labels
    for i in range(len(labels)):
        for key, value in map.items():    
            if key in labels[i]:
                x = labels[i].replace(key, value)
                new_labels[i] = x

    new_variables = [f"{y.split("_")[0]}_M{order[x.split('!!')[-1]]:02d}" for x, y in zip(labels, variables)]

    return new_labels, new_variables


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
    'geoinfo'
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
    """
    See all available table group for a survey and year

    Parameters
    ----------
    survey_table : string
        The survey to get groups for, see morpc.census.api.IMPLEMENTED_ENDPOINTS
    year : string
        The year of the survey to get groups for.

    Returns
    -------
    dict
        a dictionary keyed by name of the group with a description and variables.
    """
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

def get_group_universe(survey_table, year, group):
    logger.debug(f"Getting list of variables for {group} in {year} {survey_table}.")
    json = get_json_safely(f"{CENSUS_DATA_BASE_URL}/{year}/{survey_table}/groups/{group}.json")

    variables = {k: json['variables'][k] for k in sorted(json['variables'].keys()) if k not in ['GEO_ID', 'NAME']}
    return [x for x in variables.values()][0]['universe']

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

def get_params(group, variables=None):

    logger.debug(f"Getting parameters to pass to get parameter.")
    if variables != None:
        get_param = f"GEO_ID,NAME,{",".join(variables)}"
    else:
        get_param = f"GEO_ID,NAME,group({group})"
    logger.info(f"'get' parameters for query are {get_param}")
    
    return get_param

def get_api_request(survey_table, year, group, scope, variables=None, scale=None):
    from morpc.census.geos import geo_params_from_scope_scale

    logger.debug(f"Building final requests parameters and url.")
    url = get_query_url(survey_table, year)

    get_param = get_params(group, variables=variables)

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
    from morpc.req import get_json_safely, get_text_safely
    from morpc.census.api import get_group_variables
    import pandas as pd
    import re
    from io import StringIO

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
                censusData = censusData.join(df.set_index("GEO_ID")).reset_index()
            
            requestCount += 1
    else:        
        group = re.findall(r'group\((.+)\)', params['get'])[0]

        logger.info(f'Found group {group} parameter. Ignoring variable limits.')

        params_string = "&".join([f"{k}={v}" for k, v in params.items()])

        text = get_text_safely(f"{url}{params_string}")

        try:
            censusData = pd.read_csv(StringIO(text.replace("[",'').replace("]",'')), sep=",", quotechar='"')

        except Exception as e:
            logger.error(f"Error creating Dataframe from records. {e}")
            raise RuntimeError
        
    return censusData

def censusapi_name(survey_table, year, scope, group, scale = None, variables=None):
    """
    Create a name in default format for CensusAPI class.

    Parameters
    ----------
    survey_table : str
        The survey and table. morpc.census.api.IMPLEMENTED_ENDPOINTS
    year : str
        The year if the survey
    scale : str, Optional
        The sumlevel name for the scale of the data
    scope : str
        the geographic scope of the data. see morpc.census.geos.SCOPE
    group : str
        The group id for the data table, ie. B01001
    variables : list, Optional
        A list of string to include in the data. For the purpose of the name, if present then with append -selectvariable

    Returns
    -------
    str
        the name used for the data in CensusAPI
    """

    return f"census-{survey_table.replace("/","-")}-{year}-{"" if scale is None else HIERARCHY_STRING_FROM_SINGULAR[scale].replace("-","").lower() + '-'}{scope}-{group}{"-select-variables" if variables is not None else ""}".lower()


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
        from morpc import HIERARCHY_STRING_FROM_SINGULAR
        
        self.NAME = f"census-{survey_table.replace("/","-")}-{year}-{"" if scale is None else HIERARCHY_STRING_FROM_SINGULAR[scale].replace("-","").lower() + '-'}{scope}-{group}{"-select-variables" if variables is not None else ""}".lower()

        self.logger = logging.getLogger(__name__).getChild(self.__class__.__name__).getChild(self.NAME)

        self.logger.info(f"Initializing CENSUS_API_DATA object for {self.NAME}.")

        self.SURVEY = survey_table
        self.YEAR = year
        self.GROUP = group.upper()
        self.CONCEPT = get_table_groups(self.SURVEY, self.YEAR)[self.GROUP]['description']
        self.UNIVERSE = get_group_universe(self.SURVEY, [2023 if self.YEAR < 2023 else self.YEAR][0], self.GROUP)
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

        self.VARS = get_group_variables(self.SURVEY, self.YEAR, self.GROUP)
        if self.VARIABLES is not None:
            temp = {}
            for VAR in self.VARS:
                if VAR not in self.VARIABLES:
                    self.logger.debug(f"{VAR} not in list of variables for {self.GROUP}, removing from variable list.")
                if VAR in self.VARIABLES:
                    temp[VAR] = self.VARS[VAR]
            self.VARS = temp

        logger.info(f"Building Request URL and Parameters.")
        logger.debug(f"{self.SURVEY,} {self.YEAR}, {self.GROUP}, {self.SCOPE}, {self.VARIABLES}, {self.SCALE}")
        self.REQUEST = get_api_request(survey_table=self.SURVEY, year=self.YEAR, group=self.GROUP, scope=self.SCOPE, variables=self.VARIABLES, scale=self.SCALE)

        try:
            logger.info(f"Getting data from {self.REQUEST['url']} with parameters {self.REQUEST['params']}.")
            self.DATA = get(self.REQUEST['url'], self.REQUEST['params'])
            logger.debug(f"Request converted to DataFrame:")
            logger.debug(f"\n\n{self.DATA.head(5).to_markdown()}")

        except Exception as e:
            self.logger.error(f"Error retrieving data: {e}")
            raise RuntimeError("Failed to retrieve data from Census API.")
        
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
        import pandas as pd
        import re

        logger.info(f"Melting data into long format.")


        long = self.DATA.reset_index().melt(id_vars=['GEO_ID', 'NAME'], var_name='variable', value_name='value')
        logger.debug(f"\n\n{long.head(5).to_markdown()}")

        long = long.loc[~long['value'].isna()]
        long = long.loc[long['variable'].str.endswith(('E', 'M'))]
        logger.debug(f"Removing unneeded variable types, variables remaining: {[x for x in long['variable'].unique()]}")

        long['variable_type'] = [re.findall(r"_[0-9]+([A-Z]{1,2})", x)[0] for x in long['variable']]

        logger.debug(f"included variable types: {[x for x in long['variable_type']]}")

        long = long.loc[~long['variable_type'].str.endswith('A')]

        long['variable_type'] = [VARIABLE_TYPES[x] for x in long['variable_type']]

        long['variable_label'] = [re.split("!!", self.VARS[variable]['label'],maxsplit=1)[1] for variable in long['variable']]

        long['variable'] = [re.findall(r"([A-Z0-9_]+[0-9]+)[A-Z]+", x)[0] for x in long['variable']]

        long['reference_period'] = self.YEAR

        long['universe'] = self.UNIVERSE

        long['concept'] = self.CONCEPT.capitalize()

        long = long.pivot(index=['GEO_ID', 'NAME', 'reference_period', 'concept', 'universe', 'variable_label', 'variable'], columns='variable_type', values='value').reset_index().rename_axis(None, axis=1)
        long = long.sort_values(by=['GEO_ID', 'variable', 'reference_period'])

        for column in long.columns:
            if column in VARIABLE_TYPES.values():
                long[column] = [pd.to_numeric(x) if x not in MISSING_VALUES else np.nan for x in long[column]]

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
        allFields.append({"name":"concept", "type":"string", "description":"The description of the concept for the table"})
        allFields.append({'name':'universe', 'type':'string', 'description':'The universe which represent the total for the data'})
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
        from morpc.census.geos import valid_scope, valid_scale
        
        self.logger.info(f"Validating selected parameters")

        self.VALID = True
        if not valid_survey_table(self.SURVEY):
            self.VALID = False
        if not valid_vintage(self.SURVEY, self.YEAR):
            self.VALID = False
        if not valid_group(self.GROUP, self.SURVEY, self.YEAR):
            self.VALID = False
        if not valid_scope(self.SCOPE):
            self.VALID = False
        if self.SCALE is not None:
            if not valid_scale(self.SCALE):
                self.VALID = False
        if self.VARIABLES is not None:
            if not valid_variables(self.SURVEY, self.YEAR, self.GROUP, self.VARIABLES):
                self.VALID = False            
        if self.VALID == False:
            self.logger.error("One or more parameters are invalid. Please check the logs for details.")
            raise RuntimeError("Invalid parameters for CENSUS_API_DATA object initialization.")
        

class DimensionTable:
    _DimensionTable_logger = logging.getLogger(__name__).getChild(__qualname__)
    def __init__(self, CensusAPI_LONG, droplevels=None, variable_map=None, variable_order=None):
        """
        Class for creating dimension tables from CensusAPI data in long format.

        Parameters:
        ----------
        CensusAPI : morpc.census.CensusAPI
            The CensusAPI object to create dimension tables from.
        """
        from datetime import datetime
        self.LONG = CensusAPI_LONG.copy() # Store a copy of the data

        if variable_map!=None:
            logger.info(f"Passed a variable map. Adjusting variables ({", ".join([x for x in variable_map.keys()])}) to new variables ({", ".join([x for x in variable_order.keys()])}).")
            if variable_order == None:
                logger.error(f"If passing map must all pass order.")
            else:
                self.LONG['variable_label'], self.LONG['variable'] = find_replace_variable_map(self.LONG['variable_label'], self.LONG['variable'], map=variable_map, order=variable_order)
                self.LONG = self.LONG.groupby(['concept', 'universe', 'GEO_ID', 'NAME', 'reference_period', 'variable_label', 'variable']).agg({'estimate': 'sum'}).reset_index()

        self.logger = logging.getLogger(__name__).getChild(self.__class__.__name__).getChild(str(datetime.now()))
        self.logger.info(f"Initializing DimensionTable object.")

        self.WIDE = self.wide(droplevels=droplevels)
        self.PERCENT = self.percent(droplevels=droplevels)

    def wide(self, droplevels=None):
        import pandas as pd
        import numpy as np

        self.logger.info(f"Pivoting data into wide format.")
        self.DESC_TABLE = self.create_description_table()

        long = self.LONG
        for column in long.columns:
            long[column] = [np.nan if value in MISSING_VALUES else value for value in long[column]]
        self._columns = [column for column in long if column not in ['variable', 'estimate', 'variable_label', 'moe']]

        wide = long.pivot(index='variable', columns=[x for x in self._columns], values='estimate')
        columns_levels = wide.columns.names
        wide.columns = wide.columns.to_list()
        wide = wide.join(self.DESC_TABLE)
        wide = wide.set_index([x for x in self.DESC_TABLE.columns])
        wide.columns = pd.MultiIndex.from_tuples(wide.columns)
        wide.columns.names = columns_levels
        wide = wide.sort_index(level='GEO_ID', axis=1)
        wide = wide.drop_duplicates()

        if droplevels != None:
            indexnames = wide.index.names
            wide = wide.reset_index()
            if not isinstance(droplevels, list):
                droplevels = [droplevels]
            for droplevel in droplevels:
                logger.info(f"Dropping dimension {droplevel} from dimension table.")
                if len(indexnames) == 1:
                    logger.error(f"Can not drop only level: {droplevel}")
                if not droplevel in indexnames:
                    logger.error(f"Level {droplevel} not in index ({indexnames}).")
                    raise ValueError
                if droplevel == indexnames[-1]:
                    logger.info(f"Dropping last level: {droplevel}.")
                    wide = wide.loc[wide[droplevel]==""]
                    wide = wide.drop(columns=[droplevel])
                if droplevel == 0:
                    logger.warning(f"Dropping Total Column. This may cause issues with percentages later. CAUTION")
                    wide = wide.loc[wide[droplevel+1]!=""]
                    wide = wide.drop(columns=[droplevel])
                if droplevel in indexnames[1:-1]:
                    logger.info(f"Dropping level: {droplevel}. Aggregating on other levels.")
                    wide = pd.concat([wide.loc[(wide[droplevel]=='')], wide.loc[(wide[droplevel]!='')&(wide[droplevel+1]!='')]])
                    wide = wide.drop(columns=[droplevel])
                    wide = wide.groupby([x for x in indexnames if x not in droplevels]).sum().reset_index()
                # if indexnames-1 > 1:
                #     wide.index.names = [x for x in range(len(wide.index.names))]
                # if indexnames-1 == 1:
                #     wide.index.name = 0
            wide = wide.set_index([x for x in indexnames if x not in droplevels])

        return wide

    def percent(self, droplevels=None, decimals=2):
        
        self.logger.info(f"Creating percent table.")

        self.WIDE = self.wide(droplevels=droplevels)

        total = self.WIDE.T.iloc[:,0].copy()
        percent = self.WIDE.T.iloc[:,1:].copy()
        for column in percent:
            percent[column] = round(percent[column].astype(float) / total.astype(float) * 100, decimals)
        percent.columns = percent.columns.droplevel(0)
        percent = percent.reset_index()
        percent['universe'] = [f"% of {x.lower()}" for x in percent['universe']]
        percent = percent.set_index([x for x in self._columns])
        
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
    
    def plot_bar(self, value, x_axis, dimension, variables=None, x_ordered=None, x_ascending=False, variables_ordered=False, value_labels='overlay', hex_list=None, aspect_ratio=1):
        """
        Plot the dimension table as bar plot with reasonable defaults.

        Parameters
        ----------
        value : {'totals', 'percent'}
            The value to plot, either totals or percent.
        x_axis : str
            the name of column to plot on x-axis.
        y_axis : str
            The name of column to plot on y-axis.
        dimension : int
            The dimension that has the variables interested in plotting.
        variables : list, optional
            A list of the variables to include in the the plot. Searches dimensions and filters columns by list.
        x_ordered : {None, list, 'by_y'}, optional
            How to order x axis.
            If list, orders x axis values based on list.
            'by_y' orders the x axis by the y values. 
        x_ascending : boolean
            If x_ordered is "by_y", whether to sort ascending or descending. 
        variables_ordered : boolean
            If true, convert variables to categorical.
        value_labels : {None, 'overlay', 'above'}
            If and how to label bars with values.
        aspect_ratio : float
            Aspect ratio y/x for the figure dimensions
            
        Returns
        -------
        plotnine.ggplot.ggplot
        """

        import textwrap
        from plotnine import guides, guide_legend, element_text, ggplot, aes, geom_col, geom_text, after_stat, position_stack, scale_x_discrete, scale_fill_manual, scale_color_manual, scale_y_continuous, labs, theme, element_text, stage, coord_fixed
        import pandas as pd
        from morpc.plot import morpc_theme
        from morpc.color.colors import overlay_color, GetColors

        logger.info(f"Creating plot for dimension table for {value}")

        # load dimtable for value to plot
        if value == 'totals':
            self.dim_table = self.WIDE
        if value == 'percent':
            self.dim_table = self.PERCENT

        logger.debug(f"Normalizing index values")

        # normalize index names
        index_levels = []
        index_values = []
        for level in self.dim_table.index.names:
            index_levels.append(level)
        self.dim_table = self.dim_table.reset_index()
        for column in index_levels:
            logger.debug(f"Index level: {column} ")
            values = [x.capitalize().replace(':', '') for x in self.dim_table[column]]
            logger.debug(f'Index values: {values}')
            self.dim_table[column] = values
            # store unique values
            for value in values:
                if value not in index_values:
                    index_values.append(value)
        self.dim_table = self.dim_table.set_index(index_levels)

        if variables != None:
        # normalize variables
            variables = [x.capitalize().replace(':','') for x in variables]
            logger.debug(f"Normalized variables: {variables}")
            # check variables are in table

            logger.debug(f"Verifying variables are in index")
            for variable in variables:         
                if variable not in index_values:
                    logger.error(f"{variable} not in dimensions: {index_values}")
                    raise ValueError
            variables_to_plot = [x.capitalize() for x in variables]
        else:
            logger.debug(f"No variables selected. Using all variables in dimension {dimension}")

        # pivot long for plotting.
        logger.debug(f"Converting dim_table in to standardized long table for plotting.")
        id_vars = [x for x in self.dim_table.reset_index().columns.difference(self.dim_table.columns)]
        logger.debug(f"Melting table based on {id_vars}")
        to_plot = self.dim_table.reset_index().melt(id_vars=id_vars)
        columns = [x for x in to_plot.columns]
        for i in range(len(columns)):
            name = columns[i]
            if name in id_vars:
                columns[i] = f"dimension_{i+1}"
        to_plot.columns = columns

        # store dimension to plot
        dimension_to_plot = f"dimension_{dimension}"
        to_plot = to_plot.rename(columns={dimension_to_plot:'variable'})

        # filter and remove other dimensions
        for column in to_plot.columns:
            if column.startswith('dimension'):
                if int(column.split('_')[-1])>dimension:
                    to_plot = to_plot.loc[to_plot[column]=='']
                    to_plot = to_plot.drop(columns=column)
                if int(column.split('_')[-1])<dimension:
                    to_plot = to_plot.drop(columns = column)


        # filter for variables
        if variables != None:
            to_plot = to_plot.loc[to_plot['variable'].isin(variables_to_plot)]

        # order variables by list if categorical
        if variables_ordered == True:
            if variables == None:
                logger.error(f"Unable to order variables, not list of variables supplied. Pass list in order to variables parameter.")
            to_plot['variable'] = pd.Categorical(to_plot['variable'], categories=variables, ordered=True)
        
        # order x axis if by categorical
        if isinstance(x_ordered, list):
            for value in x_ordered:
                if value not in to_plot[x_axis].to_list():
                    logger.debug(f"{to_plot[x_axis].to_list()}")
                    logger.error(f"{value} not in column {x_axis}. unable to order axis")
                    raise ValueError
            to_plot[x_axis] = pd.Categorical(to_plot[x_axis], categories=x_ordered, ordered=True)
    
        # store table to plot from
        self.to_plot = to_plot

        # if order by y then edit x axis string to use reorder
        if (x_ordered == 'by_y'):
            x_axis = f"reorder({x_axis}, value, ascending={x_ascending})"
    
        if hex_list == None:
            hex_list = GetColors().QUAL().hex_list

        # Build initial plot
        plot = (
            ggplot(to_plot)
            + geom_col(
                aes(x = x_axis, y='value', fill='variable'), 
                position = 'stack'
                )
            + scale_x_discrete(
                name='', 
                labels=self.wraping_func)
            + scale_y_continuous(
                name=textwrap.fill(list(to_plot['universe'])[0],len(list(to_plot['universe'])[0])/1.6)
                )
            + scale_fill_manual(
                hex_list,
                name=textwrap.fill(list(to_plot['concept'])[0],len(list(to_plot['concept'])[0])/1.6)
                )
            + scale_color_manual(
                hex_list
                )
            + morpc_theme(base_size=11)
            + guides(
                fill = guide_legend(
                    direction='vertical',
                    position='bottom',
                )
            )
            + labs(
                fill="",
            )
            + coord_fixed(aspect_ratio)
            )
        

        if value == 'percent':
            format_string = "{:.2f}%"
        else:
            format_string = None

        if value_labels == None:
            label_geom = None
        else: 
            if value_labels == 'overlay':
                label_geom = geom_text(
                    aes(x = x_axis, y='value', label="value", 
                        color=stage('variable', after_scale='overlay_color(color)'),
                        ),  # new
                    size = 9,
                    show_legend=False,
                    va='top',
                    ha='center',
                    format_string="{:.2f}%",
                    position=position_stack(vjust=0.6),
                                    )
                plot = plot + label_geom
            elif value_labels == 'above':
                label_geom = geom_text(
                    aes(x = x_axis, y='value', label="value", 
                        color=stage('variable', after_scale='color'),
                        ),  # new
                    size = 9,
                    show_legend=False,
                    va='bottom',
                    ha='center',
                    format_string=format_string,
                    position=position_stack(),
                                    )
                plot = plot + label_geom

        return plot

    def wraping_func(self, text):
        import textwrap
        return [textwrap.fill(str(wraped_text), width=9) for wraped_text in text]
