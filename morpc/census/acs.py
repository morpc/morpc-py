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

class ACS:
    _ACS_logger = logging.getLogger(__name__).getChild(__qualname__)
    def __init__(self, group, year, survey):
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
            type of survey - acs1, acs5 currently impemented
        """
        self.logger = logging.getLogger(__name__).getChild(self.__class__.__name__).getChild(str(id(self)))

        from datetime import datetime
        self.logger.info(f"Initializing ACS object for {group} for {year} ACS {survey}-year survey.")
        self.GROUP = group.upper()
        self.YEAR = year
        self.SURVEY = survey

        self.VARS = get_variable_dict(year, survey, group)
        self.logger.info(f"Concept '{self.VARS[[x for x in self.VARS][0]]['concept']}' has {len(self.VARS)} variables.")

    def load(self, resource_path):
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
        from datetime import datetime

        # Define the path to the resource file and extract the directory and filename.
        self.RESOURCE_PATH = resource_path
        self.DIRNAME = os.path.dirname(self.RESOURCE_PATH)
        self.FILENAME = os.path.basename(self.RESOURCE_PATH)

        # Need to change directories to location of file to read using load data.
        cwd = os.getcwd()
        if not os.path.exists(self.RESOURCE_PATH):
            self.logger.error(f"File {self.RESOURCE_PATH} does not exist. Please check the path and try again.")
            raise FileNotFoundError(logstr)
        os.chdir(self.DIRNAME)

        # Load data and store some of the constants from resource.
        self.logger.info(f"Loading data from {self.RESOURCE_PATH}...")
        self.DATA, self.RESOURCE, self.SCHEMA = morpc.frictionless.load_data(os.path.basename(self.RESOURCE_PATH))
        self.NAME = self.RESOURCE.get_defined('name')
        self.API_PARAMS = self.RESOURCE.get_defined('sources')[0]['_params']
        self.API_URL = self.RESOURCE.get_defined('sources')[0]['path']

        # change back to working directory
        os.chdir(cwd)

        # Rebuild dimension tables and store geographies
        self.DATA = self.DATA.set_index('GEO_ID')
        self.DIM_TABLE = morpc.census.DIMTABLE(self.DATA, self.SCHEMA, self.YEAR)

        self.logger.info(f"Creating tables from data. {len(self.DIM_TABLE.LONG)} observations.")

        self.GEOS = self.define_geos()
        self.logger.info(f"Retrieving geometries. {len(self.GEOS)} total geometries.")

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
        from datetime import datetime

        params = morpc.census.geos.params_from_scale_scope(scale, scope)

        scope_name = f"{scale}-{scope}"

        self.logger.info(f" Using scale and scope to retrieve all {scale} in {scope}.")

        self.query(for_param=params[0], in_param=params[1], scope=scope_name)

        return self

    
    def query(self, for_param=None, in_param=None, get_param=None, ucgid_param = None, scope=None):
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

        self.logger.info(f"Querying data for {self.GROUP} for {self.SURVEY}-year survey in {self.YEAR}...")

        # Check to make sure that variables in the get parameters are in the data.
        if get_param is not None:
            if not isinstance(get_param, list):
                self.logger.error(f"Get parameters {get_param} must be a list.")
            temp = {}
            for VAR in self.VARS:
                if VAR not in get_param:
                    self.logger.error(f"{VAR} not in list of variables for {self.GROUP}")
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
            self.NAME = f"morpc-{self.SURVEY}-{self.YEAR}-custom-{self.GROUP}-{datetime.now().strftime(format='%Y%m%d')}".lower()
        else:
            self.NAME = f"morpc-{self.SURVEY}-{self.YEAR}-{self.SCOPE}-{self.GROUP}-{datetime.now().strftime(format='%Y%m%d')}".lower()
            self.logger.info(f"NAME set to {self.NAME}...")

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
        self.API_URL = f"https://api.census.gov/data/{self.YEAR}/acs/{self.SURVEY}"

        self.logger.info(f"Querying data from {self.API_URL} with parameters: {self.API_PARAMS}")

        # Query the data
        self.DATA = morpc.census.api_get(self.API_URL, self.API_PARAMS)

        # Wrangle data types and index
        self.DATA = morpc.cast_field_types(self.DATA.reset_index(), self.SCHEMA)
        self.DATA = self.DATA.filter(items=self.SCHEMA.field_names, axis='columns')
        self.DATA = self.DATA.set_index('GEO_ID')

        # Construct the dimension tables.
        self.logger.info("Wrangling data types and building dimension tables...")
        self.DIM_TABLE = morpc.census.DIMTABLE(self.DATA, self.SCHEMA, self.YEAR, self.GROUP, self.SURVEY)

        self.logger.info("Fetching geometries...")
        self.GEOS = fetch_geos(self.DATA.index, self.YEAR, 'ACS')
        return self
    
    def map(self, table='TOTALS'):
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
        self.logger.info(f"Table type set to {table}")

        if table == 'TOTALS':
            map_data = self.DIM_TABLE.WIDE.T.copy()
        if table == 'PERCENTS':
            map_data = self.DIM_TABLE.PERCENT.copy()

        # Flatten multiindex columns if needed
        if map_data.columns.nlevels > 1:
            map_data.columns = [", ".join(filter(None, x)) for x in map_data.columns]

        # Join the geometries to the data
        self.logger.info("Joining geometries to data...")
        if not isinstance(map_data, gpd.GeoDataFrame):
            map_data['geometry'] = [self.GEOS.loc[x, 'geometry'] for x in map_data.reset_index()['GEO_ID']]
            map_data = gpd.GeoDataFrame(map_data, geometry='geometry', crs=self.GEOS.crs)

        # Create the map object and return the folium map
        self.logger.info("Creating map...")
        self.MAP = morpc.plot.map.MAP(map_data, id_col='NAME')
        
    def explore(self, table='TOTALS'):
        """
        Method for exploring the data using a folium map. Leverages morpc.plot.map.MAP class.
        """
        self.MAP = self.map(table=table)

        return self.MAP.explore()
    
    def save(self, output_dir="./output_data"):
        """
        Saves data in an output directory as a frictionless resource and validates the resource.

        Parameters
        ----------
        output_dir : str or pathlike
            The directory where to save the resource. default = "./output_data
        """
        
        import os
        import frictionless
        from frictionless import errors

        # Make the output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        # Store some needed values for the frictionless resource
        self.DATA_FILENAME = f"{self.NAME}.csv"
        self.DATA_PATH = os.path.join(output_dir, self.DATA_FILENAME)

        # Save the data
        self.logger.info(f"Saving data to {self.DATA_PATH}...")
        self.DATA.reset_index().to_csv(self.DATA_PATH, index=False)

        # Save the schema
        self.SCHEMA_FILENAME = f"{self.NAME}.schema.yaml"
        self.SCHEMA_PATH = os.path.join(output_dir, self.SCHEMA_FILENAME)
        self.logger.info(f"Saving schema to {self.SCHEMA_PATH}")

        dummy = self.SCHEMA.to_yaml(self.SCHEMA_PATH)

        # Create the resource file
        self.RESOURCE_FILENAME = f"{self.NAME}.resource.yaml"
        self.RESOURCE_PATH = os.path.join(output_dir, self.RESOURCE_FILENAME)
        self.logger.info(f"Saving resource file to {self.RESOURCE_PATH} in {output_dir}")
        self.RESOURCE = self.define_resource()

        # Change the working directory to the output directory due to write_resource and validation behavior
        cwd = os.getcwd() # save current working dir
        os.chdir(output_dir)

        # Write the resource
        dummy = self.RESOURCE.to_yaml(self.RESOURCE_FILENAME)
        self.logger.info(f"Validating resource...")
        validation = frictionless.Resource(self.RESOURCE_FILENAME).validate()

        # Return to the current working directory
        os.chdir(cwd)
    
        # Validate the resource
        if validation.valid == True:
            self.logger.info(f"Resource is valid and saved to {self.RESOURCE_PATH}.")
        else:
            print(f'Resource is NOT valid. Errors follow. {validation}')
            raise errors.ResourceError()

        
    def define_schema(self):
        """
        Creates a frictionless schema for ACS data for a specified group and year. 

        Raises:
            RuntimeError: Failed to validate the schema

        Returns:
            frictionless.Schema: A schema representing the fields in the acs data. 
        """
        import frictionless
        from frictionless import errors
        import morpc
        import IPython

        self.logger.info(f"Defining schema for {self.GROUP} for {self.SURVEY}-year survey in {self.YEAR}...")
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
            self.logger.info(f"Schema is valid.")
        else:
            self.logger.error("Schema is NOT valid. Errors follow. {results}")
            raise errors.SchemaError

        schema = frictionless.Schema.from_descriptor(acsSchema)

        return schema
    
    def define_resource(self):
        """Create a frictionless resource for ACS data with sane defaults.

        Returns:
            frictionless.Resource: A frictionless resource based on the metadata from the ACS data.
        """
        import frictionless
        import morpc
        import datetime
        import os


        # Build the resource dictionary
        self.logger.info(f"Defining resource for {self.GROUP} for {self.SURVEY}-year survey in {self.YEAR}...")

        acsResource = {
          "profile": "tabular-data-resource",
          "name": self.NAME,
          "path": self.DATA_FILENAME, # Just file name due to frictionless using paths relative to resource
          # A title with basic data and scope
          # TODO: Implement a custom description for the scope here as well as in .query().
          # Issue URL: https://github.com/morpc/morpc-py/issues/43
          "title": f"{self.YEAR} American Community Survey {self.SURVEY}-Year Estimates for {'custom geography (see sources._params)' if self.SCOPE == None else self.SCOPE}.".title(),
          # A full description of the data. 
          "description": f"Selected variables from {self.YEAR} ACS {self.SURVEY}-Year estimates for {'custom geography (see sources._params)' if self.SCOPE == None else self.SCOPE}. Data was retrieved {datetime.datetime.today().strftime('%Y-%m-%d')}",
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
