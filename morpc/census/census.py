import json
from re import I
from tabnanny import verbose

import IPython

import morpc
from importlib.resources import files

import morpc.census

# Import the variable groups dimensions using import lib.
try:
    with files('morpc').joinpath('census', 'acs_variable_groups.json').open('r') as file:
        ACS_VAR_GROUPS = json.load(file)
except ValueError as e:
    print(e)

# Define some of the high level table descriptions to assist with looking up tables.
# Potentional later use this as in input for people to select variables of interest based on these categories.

ACS_HIGHLEVEL_GROUP_DESC = {
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
    "14": "School Enrollement",
    "15": "Educational Attainment",
    "16": "Language Spoken at Home",
    "17": "Poverty",
    "18": "Disability",
    "19": "Household Income",
    "20": "Earnings",
    "21": "Veterns",
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

ACS_MISSING_VALUES = ["","-222222222","-333333333","-555555555","-666666666","-888888888","-999999999"]

ACS_PRIMARY_KEY = "GEO_ID"

ACS_ID_FIELDS = {
    "block group": [
        {"name":"GEO_ID", "type":"string", "description":"Unique identifier for geography"},
        {"name":"SUMLEVEL", "type":"string", "description":"Code representing the geographic summary level for the data"},
        {"name":"STATE","type":"string","description":"Unique identifier for state in which geography is located"},
        {"name":"COUNTY","type":"string","description":"Unique identifier for county in which geography is located"},
        {"name":"TRACT","type":"string","description":"Unique identifier for tract in which geography is located"}
    ],
    "tract": [
        {"name":"GEO_ID", "type":"string", "description":"Unique identifier for geography"},
        {"name":"SUMLEVEL", "type":"string", "description":"Code representing the geographic summary level for the data"},
        {"name":"STATE","type":"string","description":"Unique identifier for state in which geography is located"},
        {"name":"COUNTY","type":"string","description":"Unique identifier for county in which geography is located"}
    ],
    "county subdivision": [
        {"name":"GEO_ID", "type":"string", "description":"Unique identifier for geography"},
        {"name":"SUMLEVEL", "type":"string", "description":"Code representing the geographic summary level for the data"},
        {"name":"STATE","type":"string","description":"Unique identifier for state in which geography is located"},
        {"name":"COUNTY","type":"string","description":"Unique identifier for county in which geography is located"}
    ],
    "county": [
        {"name":"GEO_ID", "type":"string", "description":"Unique identifier for geography"},
        {"name":"SUMLEVEL", "type":"string", "description":"Code representing the geographic summary level for the data"},
        {"name":"NAME", "type":"string", "description":"Name by which geography is known"},
        {"name":"STATE","type":"string","description":"Unique identifier for state in which geography is located"},
        {"name":"COUNTY","type":"string","description":"Unique identifier for county in which geography is located"},
    ],
    "state": [
        {"name":"GEO_ID", "type":"string", "description":"Unique identifier for geography"},
        {"name":"SUMLEVEL", "type":"string", "description":"Code representing the geographic summary level for the data"},
        {"name":"NAME", "type":"string", "description":"Name by which geography is known"},
        {"name":"STATE","type":"string","description":"Unique identifier for state in which geography is located"},
    ],
    "metropolitan statistical area/micropolitan statistical area": [
        {"name":"GEO_ID", "type":"string", "description":"Unique identifier for geography"},
        {"name":"SUMLEVEL", "type":"string", "description":"Code representing the geographic summary level for the data"},
        {"name":"NAME", "type":"string", "description":"Name by which geography is known"}
    ],
    "division": [
        {"name":"GEO_ID", "type":"string", "description":"Unique identifier for geography"},
        {"name":"SUMLEVEL", "type":"string", "description":"Code representing the geographic summary level for the data"},
        {"name":"NAME", "type":"string", "description":"Name by which geography is known"},
    ],
    "us": [
        {"name":"GEO_ID", "type":"string", "description":"Unique identifier for geography"},
        {"name":"SUMLEVEL", "type":"string", "description":"Code representing the geographic summary level for the data"},
        {"name":"NAME", "type":"string", "description":"Name by which geography is known"}
    ]
}

DEC_MISSING_VALUES = [""]

DEC_PRIMARY_KEY = "GEO_ID"

DEC_ID_FIELDS = json.loads(json.dumps(ACS_ID_FIELDS))  # Start with same fields as ACS, then adjust
DEC_ID_FIELDS["block"] = [
    {"name":"GEO_ID", "type":"string", "description":"Unique identifier for geography"},
    {"name":"SUMLEVEL", "type":"string", "description":"Code representing the geographic summary level for the data"},
    {"name":"STATE","type":"string","description":"Unique identifier for state in which geography is located"},
    {"name":"COUNTY","type":"string","description":"Unique identifier for county in which geography is located"},
    {"name":"TRACT","type":"string","description":"Unique identifier for tract in which geography is located"},
    # Note: Block is subsidiary to block group, however the API does not provide the block group (BLKGRP) identifiers
]

DEC_API = {
    "sdhc": {
        "title": "Supplemental Demographic and Housing Characteristics File",
        "abbrev": "S-DHC",
        "url": "https://api.census.gov/data/{year}/dec/sdhc"
    },
    "ddhcb": {
        "title": "Detailed Demographic and Housing Characteristics File B",
        "abbrev": "Detailed DHC-B",
        "url": "https://api.census.gov/data/{year}/dec/ddhcb"
    },
    "ddhca": {
        "title": "Detailed Demographic and Housing Characteristics File A",
        "abbrev": "Detailed DHC-A",
        "url": "https://api.census.gov/data/{year}/dec/ddhca"
    },
    "dhc": {
        "title": "Demographic Profile",
        "abbrev": "S-DHC",
        "url": "https://api.census.gov/data/{year}/dec/dhc"
    },
    "dp": {
        "title": "Demographic and Housing Characteristics File",
        "abbrev": "DP",
        "url": "https://api.census.gov/data/{year}/dec/dp"
    },
    "pl": {
        "title": "Redistricting Data",
        "abbrev": "PL 94-171",
        "url": "https://api.census.gov/data/{year}/dec/pl"
    },
    "pes": {
        "title": "Decennial Post-Enumeration Survey",
        "abbrev": "PES",
        "url": "https://api.census.gov/data/{year}/dec/pes"
    }
}

ACS_STANDARD_AGEGROUP_MAP = {
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

ACS_AGEGROUP_SORT_ORDER = {
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

def api_get(url, params, varBatchSize=20, verbose=True):
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

    verbose : boolean
        If True, the function will display text updates of its status, otherwise it will be silent.

    Returns
    -------
    pandas.Dataframe
        dataframe indexed by GEO_ID and having a column for each requested variable
    """
    
    import json         # We need json to make a deep copy of the params dict
    import requests
    import pandas as pd

    # Add headers to request to look like a browser.
    headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}

    # We need to reserve one variable in each batch for GEO_ID.  If the user requests more than 49 variables per
    # batch, reduce the batch size to 49 to respect the API limit
    if(varBatchSize > 49):
        print("WARNING: Requested variable batch size exceeds API limit. Reducing batch size to 50 (including GEO_ID).")
        varBatchSize = 49
    
    # Extract a list of all of the requested variables from the request parameters
    allVars = params["get"].split(",")
    if(verbose == True):
        print("Total variables requested: {}".format(len(allVars)))
       
    remainingVars = allVars   
    requestCount = 1
    while(len(remainingVars) > 0):
        if(verbose == True):
            print("Starting request #{0}. {1} variables remain.".format(requestCount, len(remainingVars)))

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
        r = requests.get(url, params=shortListParams, headers=headers)
        if(r.status_code != 200):
            print("ERROR: Request finished with status {}.".format(r.status_code))
            print("Request URL: " + r.url)
            print("Response text: " + r.text)
            raise RuntimeError

        # Extract the JSON-formatted records from the response
        records = r.json()
        
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

    return censusData

class ACS:
    def __init__(self, group, year, survey, verbose=True):
        """
        Class for working with ACS Survey Data. Creates an object representing data for a variable by year by survey. 
        Use .query() method to retrieve data for a specific geography.


        Parameters
        ----------
        group : str
            string representing the variable group

        year : str
            The year of the survey. For 5 year survey it is the ending year

        survey : str
            Number of years representing the ACS Survey, "1" or "5"
        """

        if verbose:
            print(f"MESSAGE | morpc.census.ACS.init | Initializing ACS object for {group} for {year} ACS {survey}-year survey ...")
        self.GROUP = group
        self.YEAR = year
        self.SURVEY = survey

        if verbose:
            print(f"MESSAGE | morpc.census.ACS.init | Loading variable dictionary for {self.GROUP} for {self.SURVEY}-year survey in {self.YEAR}...")
        self.VARS = get_variable_dict(year, survey, group)

    def load(self, resource_path, verbose = True):
        """
        Method for loading ACS data from a cached file. Will load all variables from the resource file, schema, and data.

        Parameters:
        ----------
        scope : str
            The geographic scope to load the data for. See morpc.census.SCOPES for available scopes.

        dirname : str
            The directory where the resource file is located. This is typically the directory where the resource file was downloaded to.

        Returns:
        -------
        morpc.census.ACS
            The ACS object with the data, resource, schema, and dimension table loaded.

        """

        import morpc
        import os

        # Define the path to the resource file and extract the directory and filename.
        self.RESOURCE_PATH = resource_path
        self.DIRNAME = os.path.dirname(self.RESOURCE_PATH)
        self.FILENAME = os.path.basename(self.RESOURCE_PATH)

        # Need to change directories to location of file to read using load data.
        cwd = os.getcwd()
        if not os.path.exists(self.RESOURCE_PATH):
            raise FileNotFoundError(f"ERROR | morpc.census.ACS.load |File {self.RESOURCE_PATH} does not exist. Please check the path and try again.")
        os.chdir(self.DIRNAME)

        # Load data and store some of the constants from resource.
        if verbose:
            print(f"MESSAGE | morpc.census.ACS.load | Loading data from {self.RESOURCE_PATH}...")
        self.DATA, self.RESOURCE, self.SCHEMA = morpc.frictionless.load_data(os.path.basename(self.RESOURCE_PATH), verbose=True)
        self.NAME = self.RESOURCE.get_defined('name')
        self.API_PARAMS = self.RESOURCE.get_defined('sources')[0]['_params']
        self.API_URL = self.RESOURCE.get_defined('sources')[0]['path']

        # change back to working directory
        os.chdir(cwd)

        # Rebuild dimension tables and store geographies
        if verbose:
            print("MESSAGE | morpc.census.ACS.load | Wrangling data types and rebuilding dimension tables...")

        self.DATA = self.DATA.set_index('GEO_ID')
        self.DIM_TABLE = morpc.census.DimensionTable(self.DATA, self.SCHEMA, self.YEAR)
        if verbose:
            print("MESSAGE | morpc.census.ACS.load | Fetching geometries...")
        self.GEOS = self.define_geos()

        return self
    
    def scope(self, scale, scope):
        """
        Creates a list of geoidsfq before querying.

        Parameters:
        -----------
        scale : str
            The scale of geography to return from the query.

        scope : str
            The scope of the query. See morpc.census.geos.SCOPES

        """
        import morpc

        geoids = morpc.census.geos.geoids(scale, scope)

        ucgid_param = f"{",".join(geoids)}"

        scope_name = f"{scale}-{scope}"

        self.query(ucgid_param=ucgid_param, scope=scope_name)

        return self

    
    def query(self, for_param=None, in_param=None, get_param=None, ucgid_param = None, scope=None, verbose=True):
        """
        Method for retrieving data. Relies on morpc.census.api_get().

        Parameters
        ----------
        for_param : str
            The parameters for the "for" parameter for the api_get() call. Typically, the ACS geographic sumlevel name and an asterisk. ex. "county subdivision:*"

        in_param : list (optional)
            The parameters for the "in" parameter for the api_get() call. Typically, a parameter to filter the for_param with. ex. "state:39" for all the for geographies in the state of Ohio. For for all geographies in Franklin County pass ["state:39", "county:049"]

        get_param : list (optional)
            The field names to retrieve from the Census. Defaults to all available variables for variable group number.

        """

        import morpc
        from datetime import datetime

        if verbose:
            print(f"MESSAGE | morpc.census.ACS.query | Querying data for {self.GROUP} for {self.SURVEY}-year survey in {self.YEAR}...")


        # Check to make sure that 
        if get_param is not None:
            if not isinstance(get_param, list):
                print('get_param must be a list')
            temp = {}
            for VAR in self.VARS:
                if VAR not in get_param:
                    print(f"ERROR | {VAR} not in list of variables for {self.GROUP}")
                    raise RuntimeError
                if VAR in get_param:
                    temp[VAR] = self.VARS[VAR]
            self.VARS = temp

        # If using scope pass name to SCOPE
        self.SCOPE = scope

        # If custom query parameters are passed to .query then the name of the resource is custom and includes date.
        # TODO: Find a better way of naming custom queries, possibly by passing a custom parameter.
        # Issue URL: https://github.com/morpc/morpc-py/issues/46

        if scope is None:
            self.NAME = f"morpc-acs{self.SURVEY}-{self.YEAR}-custom-{self.GROUP}-{datetime.now().strftime(format='%Y%m%d')}".lower()
        else:
            self.NAME = f"morpc-acs{self.SURVEY}-{self.YEAR}-{self.SCOPE}-{self.GROUP}-{datetime.now().strftime(format='%Y%m%d')}".lower()
            print(f"MESSAGE | morpc.census.ACS.query | NAME set to {self.NAME}...")

        # Build the schema from the list of variables.
        self.SCHEMA = self.define_schema()
            
        # Construct the full query string to pass to api_get
        getFields = ",".join(self.SCHEMA.field_names)
        self.API_PARAMS = {}
        self.API_PARAMS['get'] = getFields
        if for_param != None:
            self.API_PARAMS['for'] = for_param
        if in_param != None:
            self.API_PARAMS['in'] = in_param
        if ucgid_param != None:
            self.API_PARAMS['ucgid'] = ucgid_param

        # Construct the url
        self.API_URL = f"https://api.census.gov/data/{self.YEAR}/acs/acs{self.SURVEY}"

        if verbose:
            print(f"MESSAGE | morpc.census.ACS.query | Querying data from {self.API_URL} with parameters:")
            print(f"{self.API_PARAMS}...")

        # Query the data
        self.DATA = morpc.census.api_get(self.API_URL, self.API_PARAMS)

        # Wrangle data types and index
        self.DATA = morpc.cast_field_types(self.DATA.reset_index(), self.SCHEMA, verbose=False)
        self.DATA = self.DATA.filter(items=self.SCHEMA.field_names, axis='columns')
        self.DATA = self.DATA.set_index('GEO_ID')

        # Construct the dimension tables.
        if verbose:
            print("MESSAGE | morpc.census.ACS.query | Wrangling data types and building dimension tables...")
        self.DIM_TABLE = morpc.census.DimensionTable(self.DATA, self.SCHEMA, self.YEAR, self.GROUP, self.SURVEY)

        if verbose:
            print("MESSAGE | morpc.census.ACS.query | Fetching geometries...")
        self.GEOS = fetch_geos(self.DATA.index, self.YEAR, 'ACS')
        return self
    
    def map(self, table='TOTALS', verbose=True):
        """
        Method for exploring the data using a folium map. Leverages morpc.plot.map.MAP class.

        Parameters
        ----------
        table : str
            The table to explore. Options are 'TOTALS' or 'PERCENTS'. Default is 'TOTALS'

        Returns
        -------
        folium.Map
            A folium map object with the data plotted.

        
        """
        import geopandas as gpd
        import morpc

        # Get the data to plot
        if table == 'TOTALS':
            map_data = self.DIM_TABLE.WIDE.T.copy()
        if table == 'PERCENTS':
            map_data = self.DIM_TABLE.PERCENT.copy()

        # Flatten multiindex columns if needed
        if map_data.columns.nlevels > 1:
            map_data.columns = [", ".join(filter(None, x)) for x in map_data.columns]

        # Join the geometries to the data
        if verbose:
            print("MESSAGE | morpc.census.ACS.explore | Joining geometries to data...")
        if not isinstance(map_data, gpd.GeoDataFrame):
            map_data['geometry'] = [self.GEOS.loc[x, 'geometry'] for x in map_data.reset_index()['GEO_ID']]
            map_data = gpd.GeoDataFrame(map_data, geometry='geometry', crs=self.GEOS.crs)

        # Create the map object and return the folium map
        if verbose:
            print("MESSAGE | morpc.census.ACS.explore | Creating map...")
        self.MAP = morpc.plot.map.MAP(map_data, id_col='NAME')
        
    def explore(self, table='TOTALS', verbose=True):
        """
        Method for exploring the data using a folium map. Leverages morpc.plot.map.MAP class.
        """
        if not hasattr(self, 'MAP'):
            self.MAP = self.map(table=table, verbose=verbose)
        return self.MAP.explore()
    
    def save(self, output_dir="./output_data", verbose=True):
        """
        Saves data in an output directory as a frictionless resource and validates the resource.

        Parameters
        ----------
        output_dir : str or pathlike
            The directory where to save the resource. default = "./output_data
        """
        
        import os
        import frictionless

        # Make the output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        # Store some needed values for the frictionless resource
        self.DATA_FILENAME = f"{self.NAME}.csv"
        self.DATA_PATH = os.path.join(output_dir, self.DATA_FILENAME)

        # Save the data
        if verbose:
            print(f"MESSAGE | morpc.census.ACS.save | Saving data to {self.DATA_PATH}...")
        self.DATA.reset_index().to_csv(self.DATA_PATH, index=False)

        # Save the schema
        self.SCHEMA_FILENAME = f"{self.NAME}.schema.yaml"
        self.SCHEMA_PATH = os.path.join(output_dir, self.SCHEMA_FILENAME)
        dummy = self.SCHEMA.to_yaml(self.SCHEMA_PATH)

        # Create the resource file
        self.RESOURCE_FILENAME = f"{self.NAME}.resource.yaml"
        self.RESOURCE_PATH = os.path.join(output_dir, self.RESOURCE_FILENAME)
        self.RESOURCE = self.define_resource()

        # Change the working directory to the output directory due to write_resource and validation behavior
        cwd = os.getcwd() # save current working dir
        os.chdir(output_dir)

        # Write the resource
        dummy = self.RESOURCE.to_yaml(self.RESOURCE_FILENAME)
        if verbose:
            print(f"MESSAGE | morpc.census.ACS.save | Resource saved to {self.RESOURCE_PATH}. Validating resource...")
        validation = frictionless.Resource(self.RESOURCE_FILENAME).validate()

        # Return to the current working directory
        os.chdir(cwd)
    
        # Validate the resource
        if validation.valid == True:
            print(f"MESSAGE | morpc.census.ACS.save | Resource is valid and saved to {self.RESOURCE_PATH}.")
        else:
            print('ERROR | morpc.census.ACS.save | Resource is NOT valid. Errors follow.')
            print(validation)
            raise RuntimeError

        
    def define_schema(self, verbose=True):
        """
        Creates a frictionless schema for ACS data for a specified group and year. 

        Raises:
            RuntimeError: Failed to validate the schema

        Returns:
            frictionless.Schema: A schema representing the fields in the acs data. 
        """
        import frictionless
        import morpc
        import IPython

        if verbose:
            print(f"MESSAGE | morpc.census.ACS.define_schema | Defining schema for {self.GROUP} for {self.SURVEY}-year survey in {self.YEAR}...")
        variables = self.VARS

        allFields = []
        # Add GEO_ID and NAME as default index fields as they are not included in the var list.
        allFields.append({"name":"GEO_ID", "type":"string", "description":"Unique identifier for geography"})
        allFields.append({"name":"NAME", "type":"string", "description":"Name of the geography"})

        # Create an entry for each field and apply friction data types.
        acsVarDict = variables
        for var in [x for x in acsVarDict.keys()]:
            field = {}
            field["name"] = var
            field["type"] = acsVarDict[var]['predicateType']
            if(field["type"] == "int"):
                field["type"] = "integer"
            elif(field["type"] == "float"):
                field["type"] = "number"
            field["description"] = f"{acsVarDict[var]['label']} | {acsVarDict[var]['concept']} | Estimate"
            allFields.append(field)

            # Add a field for the MOE
            field = {}
            field["name"] = var[:-1] + "M"
            field["type"] = acsVarDict[var]['predicateType']
            if(field["type"] == "int"):
                field["type"] = "integer"
            elif(field["type"] == "float"):
                field["type"] = "number"
            field["description"] = f"{acsVarDict[var]['label']} | {acsVarDict[var]['concept']} | MOE"
            allFields.append(field)

        # Combine to construct the whole schema
        acsSchema = {
            "fields": allFields,
            "missingValues": morpc.census.ACS_MISSING_VALUES,
            "primaryKey": morpc.census.ACS_PRIMARY_KEY
        }

        # Validate
        results = frictionless.Schema.validate_descriptor(acsSchema)
        if(results.valid == True):
            if verbose:
                print(f"MESSAGE | morpc.census.ACS.define_schema | Schema is valid.")
        else:
            print("ERROR | morpc.census.ACS.define_schema | Schema is NOT valid. Errors follow.")
            print(results)
            raise RuntimeError

        schema = frictionless.Schema.from_descriptor(acsSchema)

        return schema
    
    def define_resource(self, verbose=True):
        """Create a frictionless resource for ACS data with sane defaults.

        Returns:
            frictionless.Resource: A frictionless resource based on the metadata from the ACS data.
        """
        import frictionless
        import morpc
        import datetime
        import os


        # Build the resource dictionary
        if verbose:
            print(f"MESSAGE | morpc.census.ACS | Defining resource for {self.GROUP} for {self.SURVEY}-year survey in {self.YEAR}...")

        acsResource = {
          "profile": "tabular-data-resource",
          "name": self.NAME,
          "path": self.DATA_FILENAME, # Just file name due to frictionless using paths relative to resource
          # A title with basic data and scope
          # TODO: Implement a custom description for the scope here as well as in .query().
          # Issue URL: https://github.com/morpc/morpc-py/issues/43
          "title": f"{self.YEAR} American Community Survey {self.SURVEY}-Year Estimates for {'Custom Geography' if self.SCOPE == None else morpc.census.geos.SCOPES[self.SCOPE]['desc']}.".title(),
          # A full description of the data. 
          "description": f"Selected variables from {self.YEAR} ACS {self.SURVEY}-Year estimates for {'custom geography (see sources._params)' if self.SCOPE == None else morpc.census.geos.SCOPES[self.SCOPE]['desc']}. Data was retrieved {datetime.datetime.today().strftime('%Y-%m-%d')}",
          "format": "csv",
          "mediatype": "text/csv",
          "encoding": "utf-8",
          "bytes": os.path.getsize(self.DATA_PATH), # The reason we need to change locations when saving the resource
          "hash": morpc.md5(self.DATA_PATH),
          "rows": self.DATA.shape[0],
          "columns": self.DATA.shape[1],
          "schema": self.SCHEMA_FILENAME,
          "sources": [{
              "title": f"{self.YEAR} American Community Survey {self.SURVEY}-Year Estimates, U.S. Census Bureau",
              "path": self.API_URL,
              "_params": self.API_PARAMS # Custom parameter signfied by _ are not validated by frictionless.
          }]
        }

        resource = frictionless.Resource(acsResource)
        return resource

def fetch_geos(geoidfqs, year, survey, verbose=True):
    """
    Fetches a table of geometries from a list of Census GEOIDFQs using the Rest API.

    Parameters:
    geoidfqs : list
        A list of fully qualified Census GEOIDs, i.e. ['0550000US39049', '0550000US39045']

    year : str
        The year of the data to ret
    """
    import morpc.rest_api
    import pandas as pd
    import geopandas as gpd

    # Get sum levels in the data
    sumlevels = set([x[0:3] for x in geoidfqs])

    geometries = []
    for sumlevel in sumlevels: # Get geometries for each sumlevel iteratively
        if verbose:
            print(f"MESSAGE | morpc.census.fetch_geos | Fetching geometries for {morpc.SUMLEVEL_DESCRIPTIONS[sumlevel]['censusRestAPI_layername']} ({sumlevel})...")
        # Get rest api layer name and get url
        layerName = morpc.SUMLEVEL_DESCRIPTIONS[sumlevel]['censusRestAPI_layername']
        url = morpc.rest_api.get_layer_url(year, layer_name=layerName, survey=survey)

        # Construct a list of geoids from data to us to query API
        geoids = ",".join([f"'{x.split('US')[-1]}'" for x in geoidfqs if x.startswith(sumlevel)])

        # Build resource file and query API
        resource = morpc.rest_api.resource(name='temp', url=url, where= f"GEOID in ({geoids})")
        geos = morpc.rest_api.gdf_from_resource(resource)
        geos['GEOIDFQ'] = [f"{sumlevel}0000US{x}" for x in geos['GEOID']]

        geometries.append(geos[['GEOIDFQ', 'geometry']])
    if verbose:
        print("MESSAGE | morpc.census.fetch_geos | Combining geometries...")
    geometries = pd.concat(geometries)
    geometries = geometries.rename(columns={'GEOIDFQ': 'GEO_ID'})
    geometries = geometries.set_index('GEO_ID')

    return gpd.GeoDataFrame(geometries, geometry='geometry')

def get_variable_dict(year, survey, group):
    """
    Fetch the list of variables from Census Metadata for an ACD variable group.
    """
    import requests

    varlist_url = f"https://api.census.gov/data/{year}/acs/acs{survey}/variables.json"
    r = requests.get(varlist_url)
    json = r.json()
    variables = {}
    for variable in sorted(json['variables']): # Sort in alphanum order
        if json['variables'][variable]['group'] == group:
            variables[variable] = json['variables'][variable]
    
    return variables

class DimensionTable:
    def __init__(self, data, schema, year, group, survey, dimension_names = None, verbose=True):
        """
        A class for dimension table for ACS census data.

        Parameters:
        ----------
        data : pandas.DataFrame
            The data indexed by GEO_ID and NAME and the columns are variables

        schema : frictionless.Schema
            The schema for the data

        Returns:
        --------
        morpc.census.DimensionTable
        """
        self.GROUP = group
        self.SURVEY = survey
        self.YEAR = year
        self.DATA = data
        self.SCHEMA = schema
        if dimension_names is not None:
            self.DIMENSIONS = dimension_names
        else:
            self.DIMENSIONS = None

        self.LONG = self.define_long(verbose=verbose)
        # self.LONG_SCHEMA = self.define_long_schema(schema, dimensions, year)
        self.WIDE = self.define_wide(verbose=verbose)
        self.PERCENT = self.define_percent(verbose=verbose)


    def define_long(self, verbose=verbose):
        """Creates a dataframe in long format showing the variables as dimensions of the data.

        Parameters:
        -----------
            data : morpc.census.ACS.DATA
                The data from acs data class to use
            schema : morpc.census.ACS.SCHEMA
                The schema for the acs data
            dimensions : list
                A list of the dimension to use in the dimension table. 
            year (_type_): _description_


        """
        import pandas as pd
        import numpy as np
        if 'geometry' in self.DATA.columns:
            index = ['GEO_ID', 'NAME', 'geometry']
        else:
            index = ['GEO_ID', 'NAME']

        if verbose:
            print(f"MESSAGE | morpc.census.DimensionTable.define_long | Creating long format table.")

        # Pivot the data long
        long = self.DATA.reset_index().melt(id_vars=index, value_name="VALUE", var_name='VARIABLE')

        # Add variable type column
        long['VAR_TYPE'] = long['VARIABLE'].apply(lambda x:'Estimate' if x[-1] == 'E' else 'MOE')

        if verbose:
            print(f"MESSAGE | morpc.census.DimensionTable.define_long | Creating description table.")
        # Create the table with a column for each dimension in the the descriptions.
        self.DESC_TABLE = self.get_desc_table()
        

        # Name each column in the description table as a dimension
        if self.DIMENSIONS is not None:
            if verbose:
                print(f"MESSAGE | morpc.census.DimensionTable.define_long | Using custom dimension names: {self.DIMENSIONS}")
                self.DESC_TABLE.columns = self.DIMENSIONS[0:len(self.DESC_TABLE.columns)]
        else:
            
            self.DIMENSIONS = [f"DIM_{x}" for x in range(len(self.DESC_TABLE.columns))]
            if verbose:
                print(f"MESSAGE | morpc.census.DimensionTable.define_long | Using default dimension names: {", ".join(self.DIMENSIONS)}.")
            self.DESC_TABLE.columns = self.DIMENSIONS

        # Rejoin the dimensions and descriptions to the table
        long = long.set_index('VARIABLE').join(self.DESC_TABLE, how='left').reset_index()

        # # Make each dimension column as a categorical to preserve order later on
        # for dim in self.DESC_TABLE.columns:
        #     long[dim] = pd.Categorical(long[dim], categories=long[dim].unique())

        # Add year column to facilitate concatenating multiple year later on
        # TODO: Add function for timeseries data, maybe separate class.
        # Issue URL: https://github.com/morpc/morpc-py/issues/38
        long['REFERENCE_YEAR'] = self.YEAR

        # Replace missing values with np.nan
        if verbose:
            print(f"MESSAGE | morpc.census.DimensionTable.define_long | Replacing missing values with NaN...")
        for missing in [pd.to_numeric(x) for x in self.SCHEMA.missing_values]:
            long['VALUE'] = long['VALUE'].replace(missing, np.nan)

        # Filter and order columns of long table.
        index_columns = ['GEO_ID', 'NAME', 'REFERENCE_YEAR', 'VARIABLE', 'VAR_TYPE']
        dim_columns = [x for x in self.DIMENSIONS]
        columns = index_columns + dim_columns + ['VALUE']
        long = long[[x for x in columns]]

        return long

    def get_desc_table(self):
        import requests
        import pandas as pd
        from numpy import nan

        r = requests.get(f'https://api.census.gov/data/{self.YEAR}/acs/acs{self.SURVEY}/variables.json')
        try:
            varjson = r.json()
        except:
            print(r.url)

        group = {}
        group[self.GROUP] = {}

        for variable in varjson['variables']:
            if variable not in ['for', 'in', 'ucgid', 'GEO_ID', 'AIANHH', 'AIHHTL', 'AIRES', 'ANRC']:
                if varjson['variables'][variable]['group'] == self.GROUP:
                    group[self.GROUP]['concept'] = varjson['variables'][variable]['concept']
                    variables = {}
                    for variable in varjson['variables']:
                        if varjson['variables'][variable]['group'] == self.GROUP:
                            variables[variable] = varjson['variables'][variable]['label'].replace(":","").split('Estimate!!')[-1].split('!!')
                    variables = {k: v for k, v in sorted(variables.items(), key=lambda item: item[0])}
                    group[self.GROUP]['variables'] = variables
        variables = group[self.GROUP]['variables']
        var_list = [v for k, v in variables.items()]
        var_df = pd.DataFrame(var_list)
        var_set = set([item for sublist in var_list for item in sublist])
        var_set.discard('')
        var_columns = {}
        for var in var_set:
            var_columns[var] = {}
            for column in var_df.columns:
                if var in var_df[column].value_counts():
                    count = var_df[column].value_counts()[var]
                    var_columns[var][column] = count
        column_map = {}
        for column in var_columns:
            column_map[column] = max(var_columns[column], key=var_columns[column].get)
        for k, v in column_map.items():
            for column in var_df.columns:
                for i, row in var_df.iterrows():
                    if var_df.iloc[i, column] == k:
                        var_df.iloc[i, column] = None
                        var_df.iloc[i, v] = k
                        var_df = var_df.replace(nan, "")
        var_df['VARIABLE'] = [x for x in variables.keys()]
        var_df = var_df.set_index('VARIABLE')
        # var_dict = {}
        # for i, row in var_df.iterrows():
        #     var_dict[[x for x in variables.keys()][i]] = row.to_list()
        # self.VAR_DICT = var_dict

        return var_df

    def define_long_schema(self, schema, dimensions, year):
        long_schema = {
            "fields": [{
                self.schema.get_field('GEO_ID'),
                self.schema.get_field('NAME'),
                
            }]
        }

    def define_wide(self, verbose=verbose):

        if verbose:
            print(f"MESSAGE | morpc.census.DimensionTable.define_wide | Creating wide format table.")   
        wide = self.LONG.loc[self.LONG['VAR_TYPE']=='Estimate'] \
            .drop(columns = ['VARIABLE', 'VAR_TYPE']) \
            .pivot_table(values = 'VALUE', columns = ['GEO_ID', 'NAME', 'REFERENCE_YEAR'], index = self.DIMENSIONS).T
        return wide.T

    def define_percent(self, verbose=verbose):
        if verbose:
            print(f"MESSAGE | morpc.census.DimensionTable.define_percent | Creating percent table.")
        total = self.WIDE.T.iloc[:,0].copy()
        percent = self.WIDE.T.iloc[:,1:].copy()
        for column in percent:
            percent[column] = percent[column] / total * 100
        
        return percent

# acs_label_to_dimensions obtains the data dimensions associated with a particular variable by decomposing the "Label" column as described in the 
# Census API variable list, e.g. https://api.census.gov/data/2022/acs/acs5/variables.html. There is a label associated with each variable provided 
# by the API. For example, one label (for B25127_004E) looks like this:
#
# Estimate!!Total:!!Owner occupied:!!Built 2020 or later:!!1, detached or attached
#
# The dimensions for the variable are simply the collections of words are separated by ":!!".  For example, "Owner occupied" refers to tenure, "Built 2020 or later" 
# refers to the structure age, and "1, detached or attached" refers to the structure configuration or class.  Thus, the dimensions might be described as follows:
# dimensionNames = ["Tenure","Structure age","Structure class"]
#
# Inputs:
#   - labelSeries is a pandas Series object that contains a set of labels, one for each ACS variable of interest.  The indices of this series typically should match 
#         the dataframe that you want to join the dimension values to.
#   - dimensionNames is a list contains descriptions of the dimensions represented by each element in the label.  These will be used as column headers in the output
#         dataframe.  If dimensionNames is not provided, no column headers will be assigned.
#
# Outputs:
#    - df is a dataframe where each record represents the set of dimensions for an ACS variable and each column represents the value of one dimension for that 
#         variable. Continuing with the example above, a truncated output may look like this:
#
#         |              | Tenure         | Struture age        | Structure class         |
#         |--------------|----------------|---------------------|-------------------------|
#         | B25127_004E  | Owner occupied | Built 2020 or later | 1, detached or attached |
#

def acs_variables_by_group(ACS_GROUP, ACS_YEAR, ACS_SURVEY):
    """
    Retrieves a dictionary of variables from acs variable metadata table.
    """
    import requests

    varlist_url = f"https://api.census.gov/data/{ACS_YEAR}/acs/acs{ACS_SURVEY}/variables.json"
    r = requests.get(varlist_url)
    json = r.json()
    variables = {}
    for variable in sorted(json['variables']):
        if json['variables'][variable]['group'] == ACS_GROUP:
            variables[variable] = json['variables'][variable]

    return variables

def acs_schema(ACS_GROUP, ACS_YEAR, ACS_SURVEY, GEO_SUMLEVEL, OUTPUT_DIR):
    import frictionless
    import morpc
    import os
    
    allFields = []

    for field in ACS_ID_FIELDS[GEO_SUMLEVEL]:
        allFields.append(field)

    acsVarDict = acs_variables_by_group(ACS_GROUP, ACS_YEAR, ACS_SURVEY)
    for var in [x for x in acsVarDict.keys()]:
        field = {}
        field["name"] = var
        field["type"] = acsVarDict[var]['predicateType']
        if(field["type"] == "int"):
            field["type"] = "integer"
        elif(field["type"] == "float"):
            field["type"] = "number"
        field["description"] = f"{acsVarDict[var]['label']} | {acsVarDict[var]['concept']} | Estimate"
        allFields.append(field)

        field = {}
        field["name"] = var[:-1] + "M"
        field["type"] = acsVarDict[var]['predicateType']
        if(field["type"] == "int"):
            field["type"] = "integer"
        elif(field["type"] == "float"):
            field["type"] = "number"
        field["description"] = f"{acsVarDict[var]['label']} | {acsVarDict[var]['concept']} | MOE"
        allFields.append(field)

    acsSchema = {
      "fields": allFields,
      "missingValues": ACS_MISSING_VALUES,
      "primaryKey": ACS_PRIMARY_KEY
    }

    results = frictionless.Schema.validate_descriptor(acsSchema)
    if(results.valid == True):
        print(f"acs{ACS_SURVEY}-{ACS_YEAR}-{ACS_GROUP}-{morpc.HIERARCHY_STRING_FROM_SINGULAR[GEO_SUMLEVEL]} schema is valid")
    else:
        print("ERROR: Schema is NOT valid. Errors follow.")
        print(results)
        raise RuntimeError

    schema = frictionless.Schema.from_descriptor(acsSchema)
    
    GEO_HIER = morpc.HIERARCHY_STRING_FROM_SINGULAR[GEO_SUMLEVEL]
    ACS_SCHEMA_FILENAME = f"morpc-acs{ACS_SURVEY}-{ACS_YEAR}-{ACS_GROUP}-{GEO_HIER}.schema.yaml"
    ACS_SCHEMA_PATH = os.path.join(OUTPUT_DIR, ACS_SCHEMA_FILENAME)
    
    schema.to_yaml(ACS_SCHEMA_PATH)
    return schema

def acs_resource(ACS_GROUP, ACS_YEAR, ACS_SURVEY, GEO_SUMLEVEL):

    for sumlevel in morpc.SUMLEVEL_DESCRIPTIONS:
        if sumlevel['singular'] == GEO_SUMLEVEL:
            geoDescription = sumlevel

    

def acs_label_to_dimensions(labelSeries, dimensionNames=None):
    """
    acs_label_to_dimensions(labelSeries, dimensionNames=None)

    obtains the data dimensions associated with a particular variable by decomposing the "Label" column as described in the Census API variable list.

    Parameters
    ----------
    labelSeries : pandas.Series object 
        Contains a set of labels, one for each ACS variable of interest.  The indices of this series typically should match the dataframe that you want to join the dimension values to.

    dimensionNames : list
        Contains descriptions of the dimensions represented by each element in the label.  These will be used as column headers in the output dataframe.  If dimensionNames is not provided, no column headers will be assigned.
        
    Returns
    -------
    Pandas.Dataframe
        Where each record represents the set of dimensions for an ACS variable and each column represents the value of one dimension for that variable.
    """
    import numpy as np
    import pandas as pd
    #TODO: add support for single variable as string.
    #Issue URL: https://github.com/morpc/morpc-py/issues/36
    
    labelSeries = labelSeries \
        .apply(lambda x:x.split("|")[0]) \
        .str.strip() \
        .str.replace("Estimate!!","") \
        .apply(lambda x:x.split(":"))
    df = labelSeries \
        .apply(pd.Series) \
        .drop(columns=[0, 1]) \
        .replace("", np.nan)
    if(type(dimensionNames) == list):
        df.columns = dimensionNames
    return df

# From a raw ACS data extract produced by morpc-acs-fetch, produce a table that includes the
# the universe (total) estimate and MOE for the indicated variable
#   
#   acsDataRaw is a pandas dataframe resulting from using from reading an output of morpc-census-acs-fetch as follows:
#    
#      resource = frictionless.Resource(ACS_COUNTY_RESOURCE_SOURCE_PATH)
#      acsDataRaw = resource.to_pandas()
#
#   universeVar is the ACS variable included in acsDataRaw that represents the universe/total. Omit the "E" or "M" suffix.
#      For example: universeVar = "B25003_001"
def acs_generate_universe_table(acsDataRaw, universeVar):
    import pandas as pd
    
    acsUniverse = acsDataRaw.copy() \
        .filter(like=universeVar, axis="columns") \
        .rename(columns=(lambda x:("Universe" if x[-1] == "E" else "Universe MOE"))) \
        .reset_index()
    acsUniverse["GEOID"] = acsUniverse["GEO_ID"].apply(lambda x:x.split("US")[1])
    acsUniverse = acsUniverse \
        .set_index("GEOID") \
        .filter(items=["NAME","Universe","Universe MOE"], axis="columns")
    
    return acsUniverse
    
# From a raw ACS data extract produced by morpc-acs-fetch, produce a table that includes the
# the universe (total) estimate and MOE for the indicated variable
#   
#   acsDataRaw is a pandas dataframe resulting from using from reading an output of morpc-census-acs-fetch as follows:
#    
#      resource = frictionless.Resource(ACS_COUNTY_RESOURCE_SOURCE_PATH)
#      acsDataRaw = resource.to_pandas()
#
#   universeVar is the ACS variable included in acsDataRaw that represents the universe/total. Omit the "E" or "M" suffix.
#      For example: universeVar = "B25003_001"
def acs_generate_DimensionTable(acsDataRaw, schema, idFields, dimensionNames):
    import pandas as pd
    import frictionless
    import morpc
        
    # Convert the GEOID to short form. Melt the data from wide to long form. Create a descripton field containing the variable label provided by the Census API.
    dimensionTable = acsDataRaw.copy().reset_index()
    dimensionTable["GEOID"] = dimensionTable["GEO_ID"].apply(lambda x:x.split("US")[1])
    dimensionTable = dimensionTable \
        .drop(columns=idFields) \
        .melt(id_vars=["GEOID"], var_name="Variable", value_name='Value')
    dimensionTable["description"] = dimensionTable["Variable"].map(morpc.frictionless.name_to_desc_map(schema))

    # Split the description string into dimensions and drop the description.  Add a field annotating whether the variable is a margin of error or an estimate.  
    # Show example results for Franklin County so it is possible to get a sense of the dimensions.
    dimensionTable = dimensionTable \
        .join(acs_label_to_dimensions(dimensionTable['description'], dimensionNames=dimensionNames), how="left") \
        .drop(columns=["description"])
    dimensionTable["Variable type"] = dimensionTable["Variable"].apply(lambda x:("Estimate" if x[-1]=="E" else "MOE"))

    return dimensionTable
    
# Sometimes ACS data has one dimension that represents subclasses of another.  For example, see this excerpt from C24030 (Sex by Industry)
# which shows subclasses for agriculture, forestry, etc.  However some top level categories - such as construciton - do not have subclasses.
# acs_flatten_category identifies the top level categories that have no subclasses and flattens those categories with the subclasses. This
# allows for more convenient comparison and summarizing across industries.  It is likely that there is a more intuitive or efficient way to
# do this.
#
# For example, this is what C24030 (partial) looks like before flattening:
#
#   Label	United States!!Estimate
#   Total:	162590221
#       Male:	85740285
#           Agriculture, forestry, fishing and hunting, and mining:	1984422
#               Agriculture, forestry, fishing and hunting	1453344
#               Mining, quarrying, and oil and gas extraction	531078
#           Construction	9968254
#           Manufacturing	11394524
#           Wholesale trade	2467558
#           Retail trade	9453931
#
# This is what it looks like after flattening.  Note that the top level category for agriculture, etc was dropped (actually, the
# entire field for the top-level category is dropped).
#
#   Label	United States!!Estimate
#   Total:	162590221
#       Male:	85740285
#         Agriculture, forestry, fishing and hunting	1453344
#         Mining, quarrying, and oil and gas extraction	531078
#         Construction	9968254
#         Manufacturing	11394524
#         Wholesale trade	2467558
#         Retail trade	9453931
#
# inDf is a pandas dataframe that was created using acs_generate_DimensionTable()
#
# categoryField is a string representing the field name of the field that holds top-level categories.
#
# subclassField is a string representing the field name of the field that holds the sub-classes
def acs_flatten_category(inDf, categoryField, subclassField):
    import pandas as pd
    df = inDf.copy()
    noSubClasses = []
    for category in df[categoryField].dropna().unique():
        uniqueByCategory = df.loc[df[categoryField] == category].dropna(subset=subclassField)[subclassField].unique()
        if(len(uniqueByCategory) == 0):
            noSubClasses.append(category)
        
    df = df.dropna(subset=categoryField)
    temp = df.filter(items=[categoryField, subclassField], axis="columns").copy()
    temp = temp.loc[temp[categoryField].isin(noSubClasses)].copy()
    temp[subclassField] = temp[categoryField]
    df.update(temp)
    df = df.drop(columns=categoryField)
    return df


