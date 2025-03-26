import json

# Conversion factors
# The following constants represent commonly used conversion factors for various units of measure
## Area
CONST_SQFT_PER_ACRE = 43560  # Square feet per acre

# Commonly used geographic identifiers
# The following are assigned by the U.S. Census Bureau
CONST_COLUMBUS_MSA_ID = '18140'
CONST_OHIO_STATE_ID = '39'
CONST_OHIO_REGION_ID = '2'      # Midwest
CONST_OHIO_DIVISION_ID = '3'    # East North Central

# Region definitions
# The following lists represent various definitions for "Central Ohio" based on collections of counties.
# The long form keys (e.g. "7-County Region") are deprecated in favor of the short-form keys (e.g. "REGION7")
# which correspond to the hierarchy strings in the sumlevel descriptions below.  Long form keys should not be
# used and should be replaced with short form keys in existing scripts when updates are made.
CONST_REGIONS = {}
CONST_REGIONS["REGION7"] = ["Delaware", "Fairfield", "Franklin", "Licking", "Madison", "Pickaway", "Union"]
CONST_REGIONS["7-County Region"] = CONST_REGIONS["REGION7"]
CONST_REGIONS["REGION10"] = CONST_REGIONS["REGION7"] + ["Knox", "Marion", "Morrow"]
CONST_REGIONS["10-County Region"] = CONST_REGIONS["REGION10"]
CONST_REGIONS["REGION15"] = CONST_REGIONS["REGION10"] + ["Fayette", "Hocking", "Logan", "Perry", "Ross"]
CONST_REGIONS["15-County Region"] = CONST_REGIONS["REGION15"]
CONST_REGIONS["REGIONCORPO"] = ["Fairfield", "Knox", "Madison", "Marion", "Morrow", "Pickaway", "Union"]
CONST_REGIONS["CORPO Region"] = CONST_REGIONS["REGIONCORPO"]
CONST_REGIONS["REGIONONECBUS"] = CONST_REGIONS["REGION10"] + ["Logan"]
CONST_REGIONS["One Columbus Region"] = CONST_REGIONS["REGIONONECBUS"]
CONST_REGIONS["REGIONCEDS"] = CONST_REGIONS["REGION10"] + ["Logan"]
CONST_REGIONS["CEDS Region"] = CONST_REGIONS["REGIONCEDS"]
CONST_REGIONS["REGIONMSA"] = CONST_REGIONS["REGION7"] + ["Hocking","Morrow","Perry"]

# Region identifiers
# Note that the Columbus MSA already has a GEOID that is defined by the Census Bureau.  See CONST_COLUMBUS_MSA_ID above.
# It is duplicated here to allow for a consistent interface to obtain the GEOID for all regions.
CONST_REGIONS_GEOID = {}
CONST_REGIONS_GEOID["REGION15"] = "001"
CONST_REGIONS_GEOID["REGION10"] = "001"
CONST_REGIONS_GEOID["REGION7"] = "001"
CONST_REGIONS_GEOID["REGIONCORPO"] = "001"
CONST_REGIONS_GEOID["REGIONCEDS"] = "001"
CONST_REGIONS_GEOID["REGIONONECBUS"] = "001"
CONST_REGIONS_GEOID["REGIONMPO"] = "001"
CONST_REGIONS_GEOID["REGIONTDM"] = "001"
CONST_REGIONS_GEOID["REGIONMSA"] = CONST_COLUMBUS_MSA_ID

# The following regions are comprised of collections of whole counties. Not all region definitions are county-based,
# for example the MPO region.
CONST_REGIONS_COUNTYBASED = ["REGION15","REGION10","REGION7","REGIONCEDS","REGIONCORPO","REGIONONECBUS","REGIONMSA"]

# County name abbreviations
## CONST_COUNTY_ABBREV maps the full county name to its three-letter abbreviation
CONST_COUNTY_ABBREV = {
    'Delaware': 'DEL',
    'Fairfield': 'FAI',
    'Fayette': 'FAY',
    'Franklin': 'FRA',
    'Hocking': 'HOC',
    'Knox': 'KNO',
    'Licking': 'LIC',
    'Logan': 'LOG',
    'Madison': 'MAD',
    'Marion': 'MAR',
    'Morrow': 'MRW',    # ODOT uses this abbreviation, but sometimes 'MOR' is used instead
    'Perry': 'PER',
    'Pickaway': 'PIC',
    'Ross': 'ROS',
    'Union': 'UNI'
}

## CONST_COUNTY_EXPAND inverts the above map, mapping the three-letter county abbreviation to its full name
CONST_COUNTY_EXPAND = {value: key for key, value in CONST_COUNTY_ABBREV.items()}

# County identifiers (Census GEOID)
## CONST_COUNTY_NAME_TO_ID maps the county name to its GEOID
CONST_COUNTY_NAME_TO_ID = {
    'Delaware': '39041',
    'Fairfield': '39045',
    'Fayette': '39047',
    'Franklin': '39049',
    'Hocking': '39073',
    'Knox': '39083',
    'Licking': '39089',
    'Logan': '39091',
    'Madison': '39097',
    'Marion': '39101',
    'Morrow': '39117',
    'Perry': '39127',
    'Pickaway': '39129',
    'Ross': '39141',
    'Union': '39159'    
}

## CONST_COUNTY_ID_TO_NAME inverts the above map, mapping the county GEOID to its name
CONST_COUNTY_ID_TO_NAME = {value: key for key, value in CONST_COUNTY_NAME_TO_ID.items()}

# Branding
## CONST_MORPC_COLORS maps human-readable descriptions of the MORPC brand colors to their hex codes  
CONST_MORPC_COLORS = {
    "darkblue": "#2e5072",
    "blue": "#0077bf",
    "darkgreen": "#2c7f68",
    "lightgreen": "#66b561",
    "bluegreen": "#00b2bf",
    "midblue": "#2c6179"
}

CONST_COLOR_CYCLES = {
    "morpc": list(CONST_MORPC_COLORS.values()),
    # The following corresponds to the matplotlib "Tableau" color palette, which is the default for pandas.
    # See https://matplotlib.org/stable/gallery/color/named_colors.html
    "matplotlib": ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'],
    # The following palettes are from ColorBrewer2. See https://colorbrewer2.org/
    "bold": ['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a','#ffff99','#b15928'],
    "pastel": ['#8dd3c7','#ffffb3','#bebada','#fb8072','#80b1d3','#fdb462','#b3de69','#fccde5','#d9d9d9','#bc80bd','#ccebc5','#ffed6f'],
    "printfriendly": ['#8dd3c7','#ffffb3','#bebada','#fb8072','#80b1d3','#fdb462','#b3de69','#fccde5'],
    "colorblind": ['#a6cee3','#1f78b4','#b2df8a','#33a02c'],
    # The following pallettes are from Colorgorical http://vrl.cs.brown.edu/color
    # distanceX are sets of 20 colors with perceptual distance set to max priority and other factors set to zero priority
    # pairingX are sets of 20 colors with pairing preference set to max priority and other factors set to zero priority
    "distance1": ["#35618f", "#17f46f", "#8a2f6b", "#abd533", "#b32df9", "#3f862d", "#f287d0", "#91e7a4", "#be0332", "#4be8f9", "#f90da0", "#dec651", "#5f4ac2", "#fe8f06", "#11a0aa", "#ff7074", "#b3d9fa", "#883c10", "#f2a68c", "#464a15"],
    "distance2": ["#96e97c", "#860967", "#6ae7e6", "#1c5b5a", "#8dbcf9", "#2c457d", "#fa79f5", "#359721", "#fa2e55", "#46f33e", "#7d2b22", "#f3a4a8", "#32a190", "#1932bf", "#cc96eb", "#7c1cee", "#e3c60b", "#c0710c", "#d3d6c1", "#445a06"],
    "distance3": ["#208eb7", "#902d54", "#48d17f", "#f53176", "#63e118", "#ef6ade", "#097b35", "#a50fa9", "#bce333", "#7212ff", "#b9cda1", "#553096", "#f8ba7c", "#294775", "#fb7810", "#8e80fb", "#6f7d43", "#f2a1c3", "#20d8fd", "#fe2b1c"],
    "pairing1": ["#68affc", "#4233a6", "#85e5dd", "#2a6866", "#66de78", "#15974d", "#b4d170", "#683c00", "#ca7e54", "#821f48", "#f65b68", "#ebcecb", "#6a7f2f", "#fece5f", "#9f2108", "#fe5900", "#2c457d", "#8b6fed", "#ffacec", "#db11ac"],
    "pairing2": ["#35618f", "#17f46f", "#8a2f6b", "#abd533", "#b32df9", "#3f862d", "#f287d0", "#91e7a4", "#be0332", "#4be8f9", "#f90da0", "#dec651", "#5f4ac2", "#fe8f06", "#11a0aa", "#ff7074", "#b3d9fa", "#883c10", "#f2a68c", "#464a15"],
    "pairing3": ["#96e97c", "#860967", "#6ae7e6", "#1c5b5a", "#8dbcf9", "#2c457d", "#fa79f5", "#359721", "#fa2e55", "#46f33e", "#7d2b22", "#f3a4a8", "#32a190", "#1932bf", "#cc96eb", "#7c1cee", "#e3c60b", "#c0710c", "#d3d6c1", "#445a06"]
}
keys = list(CONST_COLOR_CYCLES.keys())
for key in keys:
    value = json.loads(json.dumps(CONST_COLOR_CYCLES[key]))
    value.reverse()
    CONST_COLOR_CYCLES["{}_r".format(key)] = value


SUMLEVEL_DESCRIPTIONS = {
    '010': {
        "singular":"United States",
        "plural":"United States",
        "hierarchy_string":"US",
        "authority":"census",
        "idField":"NATIONID",
        "nameField":"NATION"
    },
    '020': {
        "singular":"Census region",
        "plural":"Census regions",
        "hierarchy_string":"CENSUSREGION",
        "authority":"census",
        "idField":"REGIONID",
        "nameField":"REGION"
    },    
    '030': {
        "singular":"division",
        "plural":"divisions",
        "hierarchy_string":"DIVISION",
        "authority":"census",
        "idField":"DIVISONID",
        "nameField":"DIVISION"
    },    
    '040': {
        "singular":"state",
        "plural":"states",
        "hierarchy_string":"STATE",
        "authority":"census",
        "idField":"STATEID",
        "nameField":"STATE"
    },   
    '050': {
        "singular":"county",
        "plural":"counties",
        "hierarchy_string":"COUNTY",
        "authority":"census",
        "idField":"COUNTYID",
        "nameField":"COUNTY"
    },
    '060': {
        "singular":"county subdivision",
        "plural":"county subdivisions",
        "hierarchy_string":"COUNTY-COUSUB",
        "authority":"census",
        "idField":"COUSUBID",
        "nameField":"COUSUB"
    },
    '070': {
        "singular":"county subdivision part/remainder",
        "plural":"county subdivision parts/remainders",
        "hierarchy_string":"COUNTY-TOWNSHIP-REMAINDER",
        "authority":"census",
        "idField":"COUSUBPARTID",
        "nameField":"COUSUBPART"
    },    
    '140': {
        "singular":"tract",
        "plural":"tracts",
        "hierarchy_string":"COUNTY-TRACT",
        "authority":"census",
        "idField":"TRACTID",
        "nameField":"TRACT"
    },
    '150': {
        "singular":"block group",
        "plural":"block groups",
        "hierarchy_string":"COUNTY-TRACT-BG",
        "authority":"census",
        "idField":"BLOCKGROUPID",
        "nameField":"BLOCKGROUP"
    },
    '155': {
        "singular":"place county part",
        "plural":"place county parts",
        "hierarchy_string":"PLACE-COUNTY",
        "authority":"census",
        "idField":"PLACEPARTID",
        "nameField":"PLACEPART"
    }, 
    '160': {
        "singular":"place",
        "plural":"places",
        "hierarchy_string":"PLACE",
        "authority":"census",
        "idField":"PLACEID",
        "nameField":"PLACE"
    },        
    '310': {
        "singular":"metro area",
        "plural":"metro areas",
        "hierarchy_string":"CBSA",
        "authority":"census",
        "idField":"CBSAID",
        "nameField":"CBSA"
    },
    '400': {
        "singular":"urban area",
        "plural":"urban areas",
        "hierarchy_string":"URBANAREA",
        "authority":"census",
        "idField":"URBANAREAID",
        "nameField":"URBANAREA"
    },
    '500': {
        "singular":"congressional district",
        "plural":"congressional districts",
        "hierarchy_string":"CONGRESS",
        "authority":"census",
        "idField":"CONGRESSID",
        "nameField":"CONGRESS"
    },    
    '610': {
        "singular":"state senate district",
        "plural":"state senate districts",
        "hierarchy_string":"STATESENATE",
        "authority":"census",
        "idField":"STATESENATEID",
        "nameField":"STATESENATE"
    },
    '620': {
        "singular":"state house district",
        "plural":"state house districts",
        "hierarchy_string":"STATEHOUSE",
        "authority":"census",
        "idField":"STATEHOUSEID",
        "nameField":"STATEHOUSE"
    },
    '750': {
        "singular":"census block",
        "plural":"census blocks",
        "hierarchy_string":"COUNTY-TRACT-BG-BLOCK",
        "authority":"census",
        "idField":"BLOCKID",
        "nameField":"BLOCK"
    },
    '795': {
        "singular":"public use microdata area",
        "plural":"public use microdata areas",
        "hierarchy_string":"PUMA",
        "authority":"census",
        "idField":"PUMAID",
        "nameField":"PUMA"
    },
    '850': {
        "singular":"zip code tabulation area",
        "plural":"zip code tabulation areas",
        "hierarchy_string":"ZCTA3",
        "authority":"census",
        "idField":"ZCTA3",
        "nameField":None
    },    
    '860': {
        "singular":"zip code tabulation area",
        "plural":"zip code tabulation area",
        "hierarchy_string":"ZCTA5",
        "authority":"census",
        "idField":"ZCTA5",
        "nameField":None
    },
    '930': {
        "singular":"MPO region",
        "plural":"MPO regions",
        "hierarchy_string":"CENSUSMPOREGION",
        "authority":"census",
        "idField":"MPOREGIONID",
        "nameField":"MPOREGION"
    },    
    '950': {
        "singular":"elementary school district",
        "plural":"elementary school districts",
        "hierarchy_string":"SDELEM",
        "authority":"census",
        "idField":"SCHOOLDELEMID",
        "nameField":"SCHOOLDELEM"
    },
    '960': {
        "singular":"high school district",
        "plural":"high school districts",
        "hierarchy_string":"SDHIGH",
        "authority":"census",
        "idField":"SCHOOLDHIGHID",
        "nameField":"SCHOOLDHIGH"
    },
    '970': {
        "singular":"unified school district",
        "plural":"unified school districts",
        "hierarchy_string":"SDUNIFIED",
        "authority":"census",
        "idField":"SCHOOLDID",
        "nameField":"SCHOOLD"
    },
    'M01': {
        "singular":"MORPC 15-county region",
        "plural":"MORPC 15-county region",
        "hierarchy_string":"REGION15",
        "authority":"morpc",
        "idField":"REGION15ID",
        "nameField":"REGION15"
    },
    'M02': {
        "singular":"MORPC 10-county region",
        "plural":"MORPC 10-county region",
        "hierarchy_string":"REGION10",
        "authority":"morpc",
        "idField":"REGION10ID",
        "nameField":"REGION10"
    },
    'M03': {
        "singular":"MORPC 7-county region",
        "plural":"MORPC 7-county region",
        "hierarchy_string":"REGION7",
        "authority":"morpc",
        "idField":"REGION7ID",
        "nameField":"REGION7"
    },
    'M04': {
        "singular":"MORPC CORPO region",
        "plural":"MORPC CORPO region",
        "hierarchy_string":"REGIONCORPO",
        "authority":"morpc",
        "idField":"REGIONCORPOID",
        "nameField":"REGIONCORPO"
    },
    'M05': {
        "singular":"MORPC CEDS region",
        "plural":"MORPC CEDS region",
        "hierarchy_string":"REGIONCEDS",
        "authority":"morpc",
        "idField":"REGIONCEDSID",
        "nameField":"REGIONCEDS"
    },
    'M06': {
        "singular":"MORPC MPO region",
        "plural":"MORPC MPO region",
        "hierarchy_string":"REGIONMPO",
        "authority":"morpc",
        "idField":"REGIONMPOID",
        "nameField":"REGIONMPO"
    },
    'M07': {
        "singular":"MORPC TDM region",
        "plural":"MORPC TDM region",
        "hierarchy_string":"REGIONTDM",
        "authority":"morpc",
        "idField":"REGIONTDMID",
        "nameField":"REGIONTDM"
    },
    'M08': {
        "singular":"OneColumbus region",
        "plural":"OneColumbus region",
        "hierarchy_string":"REGIONONECBUS",
        "authority":"morpc",
        "idField":"REGIONONECBUSID",
        "nameField":"REGIONONECBUS"
    },
    'M10': {
        "singular":"Jurisdiction",
        "plural":"Jurisdictions",
        "hierarchy_string":"JURIS",
        "authority":"morpc",
        "idField":"JURISID",
        "nameField":"JURIS"
    },
    'M11': {
        "singular":"Jurisdiction county part",
        "plural":"Jurisdiction county parts",
        "hierarchy_string":"JURIS-COUNTY",
        "authority":"morpc",
        "idField":"JURISPARTID",
        "nameField":"JURISPART"
    },
    'M20': {
        "singular":"Traffic analysis zone",
        "plural":"Traffic analysis zones",
        "hierarchy_string":"COUNTY-TAZ",
        "authority":"morpc",
        "idField":"TAZ",
        "nameField":None
    },
    'M21': {
        "singular":"Micro analysis zone",
        "plural":"Micro analysis zones",
        "hierarchy_string":"COUNTY-TAZ-MAZ",
        "authority":"morpc",
        "idField":"MAZ",
        "nameField":None
    },    
    'M22': {
        "singular":"GridMAZ zone",
        "plural":"GridMAZ zones",
        "hierarchy_string":"COUNTY-TAZ-MAZ-GRIDMAZ",
        "authority":"morpc",
        "idField":"GridMAZ",
        "nameField":None
    },        
}
# The following summary levels are not implemented as of November 2024
# GRID1MILE
# GRIDQUARTERMILE
# COUNTY-COUSUB-SCD
# COUNTY-TRACT-BG-BLOCK
# RESBLOB
# EMPBLOB
# GQBLOB
# PARCEL

# SUMLEVEL_LOOKUP provides a dictionary that maps each sumlevel hierarchy string (as defined in SUMLEVEL_DESCRIPTIONS)
# to its sumlevel code.  For example, SUMLEVEL_LOOKUP["CBSA"] == '310'.
SUMLEVEL_LOOKUP = {value["hierarchy_string"]:key for key, value in zip(SUMLEVEL_DESCRIPTIONS.keys(), SUMLEVEL_DESCRIPTIONS.values())}

# HIERARCHY_STRING_LOOKUP provides a dictionary that maps each sumlevel code to its hierarchy string (as defined in 
# SUMLEVEL_DESCRIPTIONS) For example, HIERARCHY_STRING_LOOKUP["310"] = "CBSA".
HIERARCHY_STRING_LOOKUP = {key:value["hierarchy_string"] for key, value in zip(SUMLEVEL_DESCRIPTIONS.keys(), SUMLEVEL_DESCRIPTIONS.values())}


# County lookup object
# Upon instantiation, this object is pre-loaded with a dataframe describing a set of counties whose scope is specified by the user.  
# The object includes methods for listing the counties by their names or GEOIDs and for two-way conversion between name and GEOID.
# scope="morpc"     Default. Loads only the counties in the MORPC 15-county region (see CONST_REGIONS['15-County Region'] above)
# scope="corpo"     Loads only the counties in the CORPO region (see CONST_REGIONS['CORPO Region'] above)
# scope="ohio"      Loads all counties in Ohio
# scope="us"      Loads all counties in the United States
# NOTE: As of Jan 2024, some methods are not supported for scope="us".  See details below.
class countyLookup():
    def __init__(self, scope="morpc"):
        import json
        import requests
        import pandas as pd

        # Get name, state identifier, and county identifier for all U.S. counties from the census API and convert it to a data frame
        r = requests.get("https://api.census.gov/data/2020/dec/pl?get=NAME&for=county:*")
        records = r.json()
        columns = records.pop(0)
        df = pd.DataFrame(data=records, columns=columns)

        # Eliminate the " County" suffix in the county name
        df["COUNTY_NAME"] = df["NAME"].str.replace(" County, Ohio","")

        # Construct the nationally-unique GEOID from the state and county identifiers
        df["GEOID"] = df["state"] + df["county"]

        # Filter the counties according to the user-specified scope
        if(scope.lower() == "ohio" or scope.lower() == "oh"):
            print("Loading data for Ohio counties only")
            df = df.loc[df["state"] == '39'].copy()
        elif(scope.lower() == "us"):
            print("Loading data for all U.S. counties")
        elif(scope.lower() == "morpc" or scope.lower() == "15-county region" or scope == "REGION15"):
            print("Loading data for MORPC 15-County region only")
            df = df.loc[df["GEOID"].isin([CONST_COUNTY_NAME_TO_ID[name] for name in CONST_REGIONS["15-County Region"]])].copy()
        elif(scope in CONST_REGIONS.keys()):
            print("Loading data for region {} only".format(scope))
            df = df.loc[df["GEOID"].isin([CONST_COUNTY_NAME_TO_ID[name] for name in CONST_REGIONS[scope]])].copy()
        else:
            print("Scope specified by user is not defined: {}".format(scope))
            raise RuntimeError

        # Sort records alphabetically by county name and eliminate extraneous columns
        df = df \
            .sort_values("COUNTY_NAME") \
            .filter(items=["GEOID","COUNTY_NAME"], axis="columns")
              
        self.scope = scope
        self.df = df
    
    # Given a county name of a county, return its ID
    # NOTE: As of January 2024, this is not supported for scope="us"
    def get_id(self, name):
        if(self.scope == "us"):
            print("ERROR: countyLookup.get_id is not supported for scope='us'")
            raise RuntimeError
        df = self.df.copy().set_index("COUNTY_NAME")
        return df.at[name, "GEOID"]

    # Given the ID of a county, return its name
    # NOTE: As of January 2024, this is not supported for scope="us"
    def get_name(self, geoid):
        if(self.scope == "us"):
            print("ERROR: countyLookup.get_name is not supported for scope='us'")
            raise RuntimeError
        df = self.df.copy().set_index("GEOID")
        return df.at[geoid, "COUNTY_NAME"]

    # List the IDs of all counties in the user-specified scope
    def list_ids(self):
        return self.df["GEOID"].to_list()

    # List the names of all counties in the user-specified scope
    # NOTE: As of January 2024, this is not supported for scope="us"       
    def list_names(self):
        if(self.scope == "us"):
            print("ERROR: countyLookup.list_names is not supported for scope='us'")
            raise RuntimeError
        return self.df["COUNTY_NAME"].to_list()      

# Standard variable lookup class
# Reads the list of "standard" variables from a lookup table.  Provides dataframe access to the list of variables, as
# well as an alias cross-reference table.
class varLookup():
    def __init__(self, variableList=None, aliasList=None, context=None, dictionaryPath="../morpc-lookup/variable_dictionary.xlsx"):
        import pandas as pd
        import os

        dictionaryPath = os.path.normpath(dictionaryPath)
        
        try:
            variables = pd.read_excel(dictionaryPath, sheet_name="Variables")
            aliases = pd.read_excel(dictionaryPath, sheet_name="Aliases")
            contexts = pd.read_excel(dictionaryPath, sheet_name="Contexts")
        except Error as e:
            print("morpc.varLookup | ERROR | Failed to read variable dictionary spreadsheet. Verify that the variable dictionary is available at {} or specify another path using the dictionaryPath argument.".format(dictionaryPath))
            print(e)
            raise RuntimeError

        variablesSchema = frictionless_load_schema(dictionaryPath.replace(".xlsx","-Variables.schema.yaml"))
        aliasesSchema = frictionless_load_schema(dictionaryPath.replace(".xlsx","-Aliases.schema.yaml"))
        contextsSchema = frictionless_load_schema(dictionaryPath.replace(".xlsx","-Contexts.schema.yaml"))

        variables = frictionless_cast_field_types(variables, variablesSchema, verbose=False)
        aliases = frictionless_cast_field_types(aliases, aliasesSchema, verbose=False)
        contexts = frictionless_cast_field_types(contexts, contextsSchema, verbose=False)      

        self.dictionaryPath = dictionaryPath
        self.variables = variables.copy()
        self.aliases = aliases.copy()
        self.contexts = contexts.copy()
        self.variableList = variableList
        self.aliasList = aliasList
        self.context = context
       
        if(variableList != None):
            self.filter_variables()
        if(aliasList != None):
            self.filter_aliases()
   
    def add_var_from_dict(self, variableDict, prepend=False):
        import pandas as pd
        if(prepend == True):
            self.variables = pd.concat([pd.DataFrame.from_dict([variableDict]), self.variables], axis="index")
        else:
            self.variables = pd.concat([self.variables, pd.DataFrame.from_dict([variableDict])], axis="index")
    
    def filter_variables(self):
        self.variables = self.variables.loc[self.variables["NAME"].isin(self.variableList)]

    def filter_aliases(self):
        self.aliases = self.aliases.loc[self.aliases["ALIAS"].isin(self.aliasList)]

    def list_variables(self):
        return list(self.variables["NAME"])

    def alias_to_name(self, context=None):
        if(context == None):
            context = self.context

        if(context != None):
            df = self.aliases.copy()

            df = df \
                .loc[df["CONTEXT"] == context].copy() \
                .filter(items=["ALIAS","NAME"], axis="columns")        
        else:
            print("morpc.varLookup.alias_to_name | ERROR | Must specify a valid context to map alias to name.")
            raise RuntimeError

        aliases = list(df["ALIAS"])
        names = list(df["NAME"])

        if(len(set(aliases)) != len(aliases)):
            print("morpc.varLookup.alias_to_name | ERROR | Each alias may only be used once per context.  Eliminate duplicated aliases for the specified context or create a different context with a unique set of aliases.")
            raise RuntimeError

        aliasToNameMap = {alias:name for (alias, name) in zip(aliases, names)}
   
        return aliasToNameMap

    def name_to_alias(self, context=None):
        if(context == None):
            context = self.context

        if(context != None):
            df = self.aliases.copy()

            df = df \
                .loc[df["CONTEXT"] == context].copy() \
                .filter(items=["ALIAS","NAME"], axis="columns")        
        else:
            print("morpc.varLookup.name_to_alias | ERROR | Must specify a valid context to map name to alias.")
            raise RuntimeError

        aliases = list(df["ALIAS"])
        names = list(df["NAME"])

        if(len(set(names)) != len(names)):
            print("morpc.varLookup.name_to_alias | ERROR | Muliple aliases map to the same variable name in the specified context. This is OK when mapping aliases to names, but not in reverse. Eliminate duplicate mappings for this context or create a different context with a 1-to-1 mapping between aliases and variables.")
            raise RuntimeError

        nameToAliasMap = {name:alias for (name, alias) in zip(names, aliases)}
   
        return nameToAliasMap
        

    def to_dict(self):
        df = self.variables.copy().set_index("NAME")
        df.columns = [x.lower() for x in df.columns]
        df = df.rename(columns={
            "minlength":"minLength",
            "maxlength":"maxLength",
            "rdftype":"rdfType"
        })
        return df.to_dict(orient="index")
        
    def to_list(self):
        df = self.variables.copy()
        df.columns = [x.lower() for x in df.columns]
        df = df.rename(columns={
            "minlength":"minLength",
            "maxlength":"maxLength",
            "rdftype":"rdfType"
        })
        return df.to_dict(orient="records")

    def to_frictionless_schema(self, missingValues=None, primaryKey=None, foreignKeys=None, useAliases=False, context=None):
        import math
        import frictionless

        if(useAliases == True):
            print("morpc.varLookup.to_frictionless_schema | WARNING | Creating schema using aliases instead of standard variable names.")
            nameToAliasMap = self.name_to_alias(context=context)

        fields = self.to_list()
        # Remove the context property from all fields in the list
        schemaFields = []
        for i in range(0, len(fields)):
            schemaFields.append({})
            schemaFields[i]["constraints"] = {}
            for fieldAttr in fields[i]:
                if(fieldAttr == "context"):
                    # If this is the "context" attribute, skip it. It doesn't belong in the schema
                    continue
                if(type(fields[i][fieldAttr]) == float):
                    # If the attribute is a float and its value is nan, skip it.
                    if(math.isnan(fields[i][fieldAttr])):
                        continue
                if(fields[i][fieldAttr] == None):
                    # Othewise if the value is None, skip it.
                    continue                    

                if(fieldAttr in ["minimum","maximum","minLength","maxLength","pattern","enum"]):
                    # If the field attribute is a constraint, put it in the constraints object
                    schemaFields[i]["constraints"][fieldAttr] = fields[i][fieldAttr]
                else:
                    # Otherwise, put it in the top level
                    schemaFields[i][fieldAttr] = fields[i][fieldAttr] 
                    if(fieldAttr == "name"):
                        # If the user requested to use aliases, replace the standard variable name with the alias.
                        if(useAliases == True):
                            try:
                                schemaFields[i]["name"] = nameToAliasMap[schemaFields[i]["name"]]
                            except KeyError:
                                print("morpc.varLookup.to_frictionless_schema | INFO | No alias defined for variable {}. Using name as-is.".format(schemaFields[i]["name"]))

        
        schemaDescriptor = {'fields': schemaFields}
        if(missingValues != None):
            schemaDescriptor["missingValues"] = missingValues
        if(primaryKey != None):
            schemaDescriptor["primaryKey"] = primaryKey
        if(foreignKeys != None):
            schemaDescriptor["foreignKeys"] = foreignKeys
        schema = frictionless.Schema.from_descriptor(schemaDescriptor) 
        return schema


# Functions for manipulating schemas in Apache Avro format
# Reference: https://avro.apache.org/docs/1.11.1/specification/

## Read an Avro schema specified as JSON in a plain text file. Return it as a Python dictionary.
def load_avro_schema(filepath):
    import os
    import json
    path = os.path.normpath(filepath)
    with open(filepath) as f:
        schema = json.load(f)
    return schema  

# Given an Avro dictionary object (see load_avro_schema), return a list containing the names of the fields defined in the schema.
def avro_get_field_names(schema):
    return [x["name"] for x in schema["fields"]]

# Given an Avro dictionary object (see load_avro_schema), return a dictionary mapping each field name to the corresponding data type
# specified in the schema.  The resulting dictionary is suitable for use by the pandas.DataFrame.astype() method (for example)
def avro_to_pandas_dtype_map(schema):
    return {schema["fields"][i]["name"]:schema["fields"][i]["type"] for i in range(len(schema["fields"]))}    

# Given an Avro dictionary object (see load_avro_schema), return a dictionary mapping each field name to the first element in the list 
# of aliases associated with that field. If no aliases are defined for a field, the dictionary will map that field name to itself.  
# The resulting dictionary may be used with the pandas.DataFrame.rename() method to rename each of the columns to its first alias 
# (for example).
def avro_map_to_first_alias(schema):
    fields = schema["fields"]
    fieldMap = {}
    for field in fields:
        if "aliases" in field.keys():
            fieldMap[field["name"]] = field["aliases"][0]
        else:
            fieldMap[field["name"]] = field["name"]
    return fieldMap

# Given an Avro dictionary object (see load_avro_schema), return a dictionary mapping the first element in the list of aliases associated with 
# a field to the field name specified for that field.  The resulting dictionary is suitable for use by the pandas.DataFrame.rename() 
# method (for example). This is the inverse of the avro_map_to_first_alias() method above.
def avro_map_from_first_alias(schema):
    fields = schema["fields"]
    fieldMap = {}
    for field in fields:
        if "aliases" in field.keys():
            fieldMap[field["aliases"][0]] = field["name"]
        else:
            fieldMap[field["name"]] = field["name"]
    return fieldMap

# Wrapper for backward compatibility
def cast_field_types(df, schema, forceInteger=False, handleMissingFields='error', verbose=True):
    # If schema is a dict object, assume it is in Avro format
    if(type(schema) == dict):
        outDF = avro_cast_field_types(df, schema, forceInteger=forceInteger, verbose=verbose)
    # Otherwise, assume it is in Frictionless format
    else:
        outDF = frictionless_cast_field_types(df, schema, forceInteger=forceInteger, handleMissingFields=handleMissingFields, verbose=verbose)
    return outDF

# Given a dataframe and the Avro dictionary object that describes its schema (see load_avro_schema), recast each of the fields in the dataframe
# to the data type specified in the schema.    
def avro_cast_field_types(df, schema, forceInteger=False, verbose=True):
    outDF = df.copy()
    for field in schema["fields"]:
        fieldName = field["name"]
        fieldType = field["type"]    
        if(verbose):
            print("Casting field {} as type {}.".format(fieldName, fieldType))
        # The following section is necessary because the pandas "int" type does not support null values.  If null values are present,
        # the field must be cast as "Int64" instead.
        if((fieldType == "int") or (fieldType == "integer")):
            try:
                # Try to cast the field as an "int".  This will fail if nulls are present.
                outDF[fieldName] = outDF[fieldName].astype(fieldType)
            except:
                try:
                    # Try to cast as "Int64", which supports nulls. This will fail if the fractional part is non-zero.
                    print("WARNING: Failed conversion of fieldname {} to type 'int'.  Trying type 'Int64' instead.".format(fieldName))
                    outDF[fieldName] = outDF[fieldName].astype("Int64")
                except:
                    if(forceInteger == True):
                        # If the user has allowed coercion of the values to integers, then round the values to the ones place prior to 
                        # converting to "Int64"
                        print("WARNING: Failed conversion of fieldname {} to type 'Int64'.  Trying to round first.".format(fieldName))
                        outDF[fieldName] = outDF[fieldName].astype("float").round(0).astype("Int64")
                    else:
                        # If the user has not allow coercion of the values to integers, then throw an error.
                        print("WARNING: Unable to coerce value to Int64 type.  Ensure that fractional part of values is zero, or set forceInteger=True")
                        raise RuntimeError           
        else:
            outDF[fieldName] = outDF[fieldName].astype(fieldType)
            
    return outDF

# Load spatial data
def load_spatial_data(sourcePath, layerName=None, driverName=None, archiveDir=None, archiveFileName=None, verbose=True):
    """Often we want to make a copy of some input data and work with the copy, for example to protect 
    the original data or to create an archival copy of it so that we can replicate the process later.  
    With tabular data this is simple, but with spatial data it can be tricky.  Shapefiles actually consist 
    of up to six files, so it is necessary to copy them all.  Geodatabases may contain many layers in addition 
    to the one we care about.  The `load_spatial_data()` function simplifies the process of reading the data and 
    (optionally) making an archival copy. 
    
    Example usage:

    Parameters
    ----------
    sourcePath : str
        The path to the geospatial data. It may be a file path or URL. In the case of a Shapefile, this should 
        point to the .shp file or a zipped file that contains all of the Shapefile components. You can point to 
        other zipped contents as well, but see caveats below.
    layerName : str
        Required for GPKG and GDB, optional for SHP. The name of the layer that you wish to extract from a 
        GeoPackage or File Geodatabase.  Not required for Shapefiles, but may be specified for use in the 
        archival copy (see below)
    driverName : str
        Required for zipped data or data with non-standard file extension. Which GDAL driver
        (https://gdal.org/drivers/vector/index.html) to use to read the file. Script will attempt to infer 
        this from the file extension, but you must specify it if the data is zipped, if the file extension is 
        non-standard, or if the extension cannot be determined from the path (e.g. if the path is an API query)
    archiveDir : str
        Optional. The path to the directory where a copy of a data should be archived.  If this is specified, 
        the data will be archived in this location as a GeoPackage.  The function will determine the file name 
        and layer name from the specified parameters, using generic values if necessary.
    archiveFileName : str
        Optional. If `archiveDir` is specified, you may use this to specify the name of the archival GeoPackage.  
        Omit the extension.  If this is unspecified, the function will assign the file name automatically using a 
        generic value if necessary.
    verbose : bool
        Set verbose to False to reduce the text output from the function.

    Returns
    -------
    gdf : pandas.core.frame.DataFrame
        A GeoPandas GeoDataframe constructed from the data at the location specified by sourcePath and layerName
    
    """

    import geopandas as gpd
    import os    

    if(verbose):
        print("morpc.load_spatial_data | INFO | Loading spatial data from location: {}".format(sourcePath))

    if(driverName == None):
        if(verbose):
            print("morpc.load_spatial_data | INFO | Driver name is unspecified.  Will attempt to infer driver from file extension in source path.")
        fileExt = os.path.splitext(sourcePath)[1]
        if(fileExt == ".gpkg"):
            driverName = "GPKG"
        elif(fileExt == ".shp"):
            driverName = "ESRI Shapefile"
        elif(fileExt == ".gdb"):
            driverName = "OpenFileGDB"
        else:
            print("morpc.load_spatial_data | ERROR | File extension is unsupported: {}.  It is possible to load zipped spatial data, but you must specify the driver name.".format(fileExt))
            raise RuntimeError
        if(verbose):
            print("morpc.load_spatial_data | INFO | Selecting driver {} based on file extension {}".format(driverName, fileExt))
    else:
        if(verbose):
            print("morpc.load_spatial_data | INFO | Using driver {} as specified by user.".format(driverName))

    if(layerName) == None:
        if(driverName == "GPKG" or driverName == "OpenFileGDB"):
            print("morpc.load_spatial_data | ERROR | Must specify layerName when using driver {}".format(driverName))
            raise RuntimeError

    if(verbose):
        print("morpc.load_spatial_data | INFO | Reading spatial data...")
    if(driverName == "ESRI Shapefile"):
        # Geopandas will throw an error if we attempt to specify a layer name when reading a Shapefile
        gdf = gpd.read_file(sourcePath, layer=None, driver=driverName, engine="pyogrio", fid_as_index=True)
    else:
        gdf = gpd.read_file(sourcePath, layer=layerName, driver=driverName, engine="pyogrio", fid_as_index=True)

    # When reading a File Geodatabase, Geopandas automatically sets the FID (OBJECTID) field to the index.  
    # In this case, reset the index, preserving the name of this field.
    if(driverName == "OpenFileGDB"):
        gdf.index.name="OBJECTID"
        gdf = gdf.reset_index()

    # If the user has specified an archive directory, create an archival copy of the data as a layer in a GeoPackage
    if(archiveDir != None):
        # If no file name was specified, we need to assign one
        if(archiveFileName) == None:
            # First try to determine whether we are retrieving data from an API. In this case we may not be able to extract
            # a file name from the source path.  Specifically, look for a "?" character in the path. This is forbidden in
            # Windows file paths and suggests that a query string is present.
            if(sourcePath.find("?") > -1):
                if(verbose):
                    print("morpc.load_spatial_data | INFO | File name is unspecified and source path appears to be an API query. Will assign an alternate file name.")
                # If the layer name is specified, use that as the file name. Otherwise use a generic file name.
                if(layerName != None):
                    archiveFileName = layerName
                else:
                    archiveFileName == "spatialData"

            # If the source path doesn't look like an API query, then attempt to extract the file name from the path
            else:
                if(verbose):
                    print("morpc.load_spatial_data | INFO | File name is unspecified.  Will infer file name from source path.")
                archiveFileName = os.path.splitext(os.path.split(sourcePath)[-1])[0]
                if(verbose):
                    print("morpc.load_spatial_data | INFO | Using automatically-selected file name: {}".format(archiveFileName)) 
        
        archivePath = os.path.join(archiveDir, "{}.gpkg".format(archiveFileName))

        # If the layer name was unspecified (e.g. for Shapefiles), use the file name as the layer name (sans extension)
        if(layerName != None):
            archiveLayer = layerName
        else:
            archiveLayer = archiveFileName
            if(verbose):
                print("morpc.load_spatial_data | INFO | Layer name is unspecified. Using automatically-selected layer name: {}".format(archiveLayer)) 

        if(verbose):
            print("morpc.load_spatial_data | INFO | Creating archival copy of geospatial layer at {}, layer {}".format(archivePath, archiveLayer))
        gdf.to_file(archivePath, layer=layerName, driver="GPKG")
    
    return gdf    

# Assign geographic identifiers
# Sometimes we have a set of locations and we would like to know what geography (county, zipcode, etc.) they fall in. The 
# `assign_geo_identifiers()` function takes a set of georeference points and a list of geography levels and determines for each 
# level which area each point falls in.  The function takes two parameters:
#  - `points` - a GeoPandas GeoDataFrame consisting of the points of interest
#  - `geographies` - A Python list of one or more strings in which each element corresponds to a geography level. You can specify as 
#     many levels as you want from the following list, however note that the function must download the polygons and perform the analysis 
#     for each level so if you specify many levels it may take a long time.
#    - "county" - County (Census TIGER)
#    - "tract" - *Not currently implemented*
#    - "blockgroup" - *Not currently implemented*
#    - "block" - *Not currently implemented*
#    - "zcta" - *Not currently implemented*
#    - "place" - Census place (Census TIGER)
#    - "placecombo" - *Not currently implemented*
#    - "juris" - *Not currently implemented*
#    - "region15County" - *Not currently implemented*
#    - "region10County" - *Not currently implemented*
#    - "regionCORPO" - *Not currently implemented*
#    - "regionMPO" - *Not currently implemented*
#
# **NOTE:** Many of the geography levels are not currently implemented.  They are being implemented as they are needed.  If you need one
# that has not yet been implemented, please contact Adam Porr (or implement it yourself).
def assign_geo_identifiers(points, geographies):
    import geopandas as gpd

 
    # Create a copy of the input data so Python doesn't manipulate the original object.
    points = points.copy()

    # Loop through each of the specified geography levels, doing a point-in-polygon assignment for each level.
    for geography in geographies:
        print("morpc.assign_geo_identifiers | INFO | Determining identifiers for geography {}".format(geography))
        # First establish the parameters for the polygon geometries. In each case we need to know:
        #   - filePath - The source file or URL where we can fetch the geometries
        #   - layerName - If the geometries are in a geodatabase, which layer are they in
        #   - driverName - What GDAL driver should we use to read the data
        #   - polyIdField - What field/attribute contains the unique identifiers for the polygons
        if(geography == "county"):
            filePath = "https://www2.census.gov/geo/tiger/TIGER2020PL/LAYER/COUNTY/2020/tl_2020_39_county20.zip"
            layerName = None
            driverName = "ESRI Shapefile"
            polyIdField = "GEOID20"
        elif(geography == "tract"):
            print("ERROR: Geography is currently unsupported: {}".format(geography))
            raise RuntimeError
        elif(geography == "blockgroup"):
            print("ERROR: Geography is currently unsupported: {}".format(geography))
            raise RuntimeError      
        elif(geography == "block"):        
            print("ERROR: Geography is currently unsupported: {}".format(geography))
            raise RuntimeError
        elif(geography == "zcta"):        
            print("ERROR: Geography is currently unsupported: {}".format(geography))
            raise RuntimeError
        elif(geography == "place"):
            filePath = "https://www2.census.gov/geo/tiger/TIGER2020/PLACE/tl_2020_39_place.zip"
            layerName = None
            driverName = "ESRI Shapefile"
            polyIdField = "GEOID"               
        elif(geography == "placecombo"):        
            print("ERROR: Geography is currently unsupported: {}".format(geography))
            raise RuntimeError                
        elif(geography == "juris"):
            print("ERROR: Geography is currently unsupported: {}".format(geography))
            raise RuntimeError        
        elif(geography == "region15County"):
            print("ERROR: Geography is currently unsupported: {}".format(geography))
            raise RuntimeError
        elif(geography == "region10County"):
            print("ERROR: Geography is currently unsupported: {}".format(geography))
            raise RuntimeError      
        elif(geography == "regionCORPO"):
            print("ERROR: Geography is currently unsupported: {}".format(geography))
            raise RuntimeError
        elif(geography == "regionMPO"):
            print("ERROR: Geography is currently unsupported: {}".format(geography))
            raise RuntimeError
        else:
            print("morpc.load_spatial_data | ERROR | Geography is unknown: {}".format(geography))
            raise RuntimeError
        
        # Read the polygon data
        polys = gpd.read_file(filePath, layer=layerName, driver=driverName)

        # Extract only the fields containing the polygon geometries and the unique IDs. Rename the unique ID field
        # using the following format "id_{}".format(geography), for example "id_county" for the "county" geography level
        polys = polys \
            .filter(items=[polyIdField,"geometry"], axis="columns") \
            .rename(columns={polyIdField:"id_{}".format(geography, polyIdField)})

        # Spatially join the polygon unique IDs to the points
        points = points.sjoin(polys.to_crs(points.crs), how="left")
        
        # Drop the index field from the polygon data
        points = points.drop(columns="index_right")
    return points

# The following function performs "bucket rounding" on a pandas Series object.  Bucket rounding 
# refers to a rounding technique for a series of data in which each element 
# is rounded to the specified number of digits in such a way that the sum of the series is 
# preserved. For example, a model may produce non-integer population values for small 
# geographies such as GridMAZ. Population must be an integer, and therefore the population for
# each GridMAZ must be rounded. Bucket rounding ensures that the rounding error resulting from 
# each of tens of thousands of individual GridMAZ does not accumulate and cause significant 
# error for combined population of all GridMAZ.
def round_preserve_sum(inputValues, digits=0, verbose=False):
    import math
    import pandas as pd

    # Make a copy of the input so that we avoid altering it due to chains or views.
    inputValuesCopy = inputValues.copy()
    
    # Create a new numerical index that is used exclusively within this function.  This is necessary due to some
    # nuances of the implementation that use the indices of the records with the largest fractional values to
    # allocate residuals.  Original index will be restored before series is returned.
    previousIndexName = inputValuesCopy.index.name
    if(previousIndexName == None):
        previousIndexName = "index"
    previousColumnName = inputValuesCopy.name
    outputValues = inputValuesCopy.copy().reset_index()

    # Extract a series using the new index.
    rawValues = outputValues.drop(columns=previousIndexName).iloc[:,0]
  
    # Compute a multiplier to be used to "inflate" the series such that the desired decimal digit ends up in the ones place so we can 
    # truncate the values to the ones place using floor
    multiplier = 10**digits

    # Compute the "inflated" values
    inflatedValues = rawValues * multiplier
  
    # Truncate the values to the ones place
    truncatedValues = inflatedValues.apply(lambda x:math.floor(x))

    # Compute the residual for each data point, i.e. the difference between the full value and the truncated value.
    # Note: Floating point arithmetic results in extraneous decimal places due to high-precision rounding error, however this 
    # should be insignificant for our purposes.
    residual = (inflatedValues-truncatedValues).round(10)
    
    # Create an array of the indices of the datapoints in ascending order according to their residual, i.e. the first element in 
    # this array is the index of the datapoint with the smallest residual and the last element is the index of the datapoint with 
    # the largest residual.
    residualOrder = residual.sort_values().index
    
    # Compute the overall residual, i.e. the difference between the sum of the full values and the sum of the truncated values
    # Note: Floating point arithmetic results in extraneous decimal places due to high-precision rounding error, however this 
    # should be insignificant for our purposes.
    overallResidual = inflatedValues.sum() - truncatedValues.sum()
    
    # Round the overall residual to determine the combined number of integer units that need to be reallocated. For example, if the 
    # series represents population, these units represent the "whole" people that were formed from the "partial" people that were 
    # removed from each individual record via the truncation.
    unitsToReallocate = round(overallResidual)

    # If there are units to reallocate, then do so. Otherwise, leave the values unadjusted
    adjustedValues = truncatedValues.copy()
    if(unitsToReallocate > 0):

        # First, select the indices for the N records with the largest residuals, where N is the number of integer units available for 
        # reallocation.
        indicesToReceiveReallocatedUnit = residualOrder[-unitsToReallocate:]

        # Reallocate one unit to each record selected to receive one
        adjustedValues[indicesToReceiveReallocatedUnit] = adjustedValues[indicesToReceiveReallocatedUnit] + 1       

    # Undo the inflation that we did at the beginning.  This completes the bucket rounding process.
    bucketRoundedValues = (adjustedValues/multiplier).astype("int")

    outputValues[previousColumnName] = bucketRoundedValues
    outputValues = outputValues.set_index(previousIndexName)[previousColumnName]

    # Show the intermediate steps of the function (for demonstration purposes only)
    if(verbose):
        print("Multiplier: {}".format(multiplier))
        print("Inflated values: {}".format(inflatedValues.tolist()))
        print("Truncated values: {}".format(truncatedValues.tolist()))
        print("Residuals for individual records: {}".format(residual.tolist()))
        print("Order of residuals: {}".format(residualOrder.tolist()))
        print("Overall residual: {}".format(overallResidual))
        print("Units to reallocate: {}".format(unitsToReallocate))
        print("Indices of records to receive reallocated units: {}".format(indicesToReceiveReallocatedUnit.tolist()))
        print("Adjusted values (still inflated): {}".format(adjustedValues.tolist()))
        print("Bucket-rounded values (deflated): {}".format(outputValues.tolist()))
  
    return(outputValues)


# Given a pandas DataFrame, append a new column "GROUP_SUM" containing the sum of 
# the values in a specified column. Optionally, populate "GROUP_SUM" with subtotals 
# for groups using group names from a specified column.
#
# Parameters:
# 
# inputDf is a pandas DataFrame with a column containing the values and (optionally) 
# a column containing the group labels
# 
# valueField is the name of the column of inputDf that contains the values. This may 
# be omitted if the DataFrame contains only one column.
#
# Optional: groupbyField is the name of the column of inputDf that contains the group 
# labels.
def compute_group_sum(inputDf, valueField=None, groupbyField=None):
    import pandas as pd

    if(type(inputDf) != pd.core.frame.DataFrame):
        print("ERROR: inputDf must be a pandas DataFrame")
        raise RuntimeError

    # Create a copy of the DataFrame to avoid operating on a reference to the original DataFrame
    df = inputDf.copy()

    if("GROUP_SUM" in df.columns):
        print("morpc.compute_group_sum | WARNING | Existing field GROUP_SUM in input dataframe will be overwritten.")
        df = df.drop(columns="GROUP_SUM")
    
    # If name of column containing the values is not specified, try to use the only column in the DataFrame. If
    # multiple columns are present, force the user to specify one.
    if(valueField == None):
        if(df.shape[1] > 1):
            print("ERROR: Must specify valueField for DataFrame with multiple columns")
            raise RuntimeError
        valueField = df.columns[0]

    # If the name of a column containing group labels is specified, try to reference the column. Throw an error if this fails.  
    if(groupbyField != None):
        try:
            temp = df[groupbyField]
        except:
            print("ERROR: inputDf does not contain groupbyField specified by user: {}".format(groupbyField))
            raise RuntimeError

    if(groupbyField != None):
        # If group field is specified, sum the values grouping by the specified field. Join the resulting group sums back to
        # the original DataFrame using the group label as the key, then name the appended column "GROUP_SUM".
        temp = df.copy() \
            .filter(items=[groupbyField, valueField], axis="columns") \
            .groupby(groupbyField).sum() \
            .reset_index() \
            .rename(columns={valueField:"GROUP_SUM"})

        # Preserve the original index through the merge operation.
        if(df.index.name == None):
            df.index.name = "NoIndexName"
        indexName = df.index.name
        df = df.reset_index().merge(temp, on=groupbyField).set_index(indexName)
        if(indexName == "NoIndexName"):
            df.index.name = None
        
    else:
        # If group field is not specified, sum all of the values and store the sum in a new column "GROUP_SUM"
        df["GROUP_SUM"] = df[valueField].sum()
        
    return df

# Given a pandas DataFrame with a column containing a set of values and another 
# column containing a set of sums representing the total of a group to which the 
# value belongs, append a new column "GROUP_SHARE" which contains the share of the 
# group total represented by each value.
#
# Parameters:
# 
# inputDf is a pandas DataFrame with a column containing the values and and a column 
# containing the group sums
# 
# valueField is the name of the column of inputDf that contains the values.
#
# Optional: groupSumField is the name of the column of inputDf that contains the group 
# sums. If this is not specified, the column "GROUP_SUM" will be used.
def compute_group_share(inputDf, valueField, groupSumField="GROUP_SUM"):
    import pandas as pd

    if(type(inputDf) != pd.core.frame.DataFrame):
        print("ERROR: inputData must be a pandas DataFrame")
        raise RuntimeError

    # Create a copy of the DataFrame to avoid operating on a reference to the original DataFrame
    df = inputDf.copy()

    if("GROUP_SHARE" in df.columns):
        print("morpc.compute_group_share | WARNING | Existing field GROUP_SHARE in input dataframe will be overwritten.")
        df = df.drop(columns="GROUP_SHARE")

    # Try to reference the column that contains the values. Throw an error if this fails.  
    try:
        temp = df[valueField]
    except:
        print("ERROR: inputDf does not contain valueField specified by user: {}".format(valueField))
        raise RuntimeError

    # Try to reference the column that contains the group sums. Throw an error if this fails.  
    try:
        temp = df[groupSumField]
    except:
        print("ERROR: inputDf does not contain groupSumField specified by user: {}".format(groupSumField))
        raise RuntimeError

    # Compute shares
    df["GROUP_SHARE"] = df[valueField] / df[groupSumField]
    df["GROUP_SHARE"] = df["GROUP_SHARE"].fillna(0)
    
    return df

# Given a pandas DataFrame with a column containing a set of shares of some values
# relative to a group total and a separate series containing a set of control totals
# for the groups, append a new column "CONTROLLED_VALUE" that contains a set of modified
# values that have been scaled such that their group share remains unchanged but their
# sum is equal to the control total.  Append another new column "CONTROL_TOTAL" that
# contains the control total for the group to which the value belongs.
#
# Parameters:
# 
# inputDf is a pandas DataFrame with a column containing the group shares and (optionally)
# a column containg the group labels.
# 
# controlValues is one of the following:
#   - If groupbyField == None: controlValues is a scalar number (integer or float)
#   - If groupbyField != None: controlValues is a pandas Series of numbers indexed by group labels
#
# Optional: groupbyField is the name of the column of inputDf that contains the group labels.
#
# Optional: shareField is the name of the column of inputDf containing the shares that the values
# comprise.  If this is not specified, "GROUP_SHARE" will be used.
#
# Optional: roundPreserveSumDigits is the number of decimal places that the scaled values
# (i.e. the values in the "CONTROLLED_VALUE" column) should be rounded to. A "bucket rounding"
# technique will be used to ensure that the sum of the values in the group is preserved. If
# this is not specified, the scaled values will be left unrounded.
def compute_controlled_values(inputDf, controlValues, groupbyField=None, shareField="GROUP_SHARE", roundPreserveSumDigits=None):
    import pandas as pd

    if(type(inputDf) != pd.core.frame.DataFrame):
        print("ERROR: inputData must be a pandas DataFrame")
        raise RuntimeError

    # Create a copy of the DataFrame to avoid operating on a reference to the original DataFrame
    df = inputDf.copy()

    if("CONTROL_TOTAL" in df.columns):
        print("morpc.compute_controlled_values | WARNING | Existing field CONTROL_TOTAL in input dataframe will be overwritten.")
        df = df.drop(columns="CONTROL_TOTAL")
    
    if("CONTROLLED_VALUE" in df.columns):
        print("morpc.compute_controlled_values | WARNING | Existing field CONTROLLED_VALUE in input dataframe will be overwritten.")
        df = df.drop(columns="CONTROLLED_VALUE")
    
    # If a field name is specified for the group labels, try to reference the column by creating a list of unique
    # groups which we can use later. Throw an error if this fails.  
    if(groupbyField != None):
        try:
            groups = df[groupbyField].unique()
        except:
            print("ERROR: inputDf does not contain groupbyField specified by user: {}".format(groupbyField))
            raise RuntimeError

    # Try to reference the column containing the shares. Throw an error if this fails.
    try:
        temp = df[shareField]
    except:
        print("ERROR: inputDf does not contain shareField specified by user: {}".format(shareField))
        raise RuntimeError

    if(groupbyField != None):
        # If groups are specified, convert the series of control totals to a dataframe with one column named "CONTROL_TOTAL" 
        # and merge this column with the dataframe using the group name. First check to make sure the control totals were provided
        # as a pandas series.

        if(type(controlValues) != pd.core.series.Series):
            print("ERROR: If groupbyField is specified, controlValues must be a pandas series of numbers indexed by group labels.")
            raise RuntimeError
        temp = controlValues.copy()
        temp.name = "CONTROL_TOTAL"
        temp = pd.DataFrame(temp)

        # Preserve the original index through the merge operation.
        if(df.index.name == None):
            df.index.name = "NoIndexName"
        indexName = df.index.name
        df = df.reset_index().merge(temp, on=groupbyField).set_index(indexName)
        if(indexName == "NoIndexName"):
            df.index.name = None
    else:
        # Otherwise, create a new column called "CONTROL_TOTAL" and assign the scalar control total to it.  First try to convert the
        # control total to a float. If so, assume it is a number.
        try:
            float(controlValues)
        except:
            print("ERROR: If groupbyField is not specified, controlValues must be a scalar number (int or float).")
            raise RuntimeError

        df["CONTROL_TOTAL"] = controlValues

    # Compute the scaled (controlled) values by multiplying the group share by the control total
    df["CONTROLLED_VALUE"] = (df[shareField] * df["CONTROL_TOTAL"]).astype("float")
    
    # If a rounding precision is provided, round the values in each group (or the entire series) to the specified precision
    # while ensuring that the group sum is preserved.
    if(roundPreserveSumDigits != None):
        if(groupbyField == None):
            # If no groups are specified, round all values in the series preserving the sum for the entire series.
            df["CONTROLLED_VALUE"] = round_preserve_sum(df["CONTROLLED_VALUE"], digits=roundPreserveSumDigits)
        else:
            # Otherwise, iterate through each group rounding the values in that group and preserving the sum for the group.
            for group in groups:
                temp = df.loc[df[groupbyField] == group].copy()
                temp["CONTROLLED_VALUE"] = round_preserve_sum(temp["CONTROLLED_VALUE"], digits=roundPreserveSumDigits)
                df.update(temp, overwrite=True, errors="ignore")
    
    return df

# Given a series of values in a group and a control total for that group, compute a set of alternate values (i.e. "controlled values") such
# that the the share of each value in the group is preserved but they sum to the control total.  Put another way, scale all of the values
# in a series uniformly such that the scaled values sum to an arbitrary value (the control total).
def control_variable_to_group(inputDf, controlValues, valueField=None, groupbyField=None, roundPreserveSumDigits=None):
    import pandas as pd

    if(type(inputDf) != pd.core.frame.DataFrame):
        print("ERROR: inputDf must be a pandas DataFrame")
        raise RuntimeError

    # Create a copy of the DataFrame to avoid operating on a reference to the original DataFrame
    df = inputDf.copy()
    
    # If name of column containing the values is not specified, try to use the only column in the DataFrame. If
    # multiple columns are present, force the user to specify one.
    if(valueField == None):
        if(df.shape[1] > 1):
            print("ERROR: Must specify valueField for DataFrame with multiple columns")
            raise RuntimeError
        valueField = df.columns[0]
    
    # Sum the values in the series, or in the groups within the series if groupbyField is specified
    df = compute_group_sum(df, valueField=valueField, groupbyField=groupbyField)
    
    # Divide each value in the series by the series sum (or each value by the group sum) to get the share of the value within the group
    df = compute_group_share(df, valueField)
 
    # Multiply each share by the control total for the group to get the controlled value
    df = compute_controlled_values(df, controlValues, groupbyField=groupbyField, roundPreserveSumDigits=roundPreserveSumDigits)
    
    return df
    
# groupAssignmentRandom() takes a population from a superior (i.e. "next level") geography and randomly assigns people to 
# groups in a set of inferior ("this level") geographies such that (1) next level population count is respected, 
# (2) this level population count is respected, and (3) this level group membership has the same proportions (on average)
# as next-level group membership.
#
# Example: The tract-level population is distributed among age groups "17 and under", "18 to 64", and "65 and over".  We want to know
# how many people in each GridMAZ fall in each of these groups, but there is no data about this so we must infer it. Moreover, the population of 
# some GridMAZ are so low (say, <5) that we can simply multiply the tract-level proportion in each group by the GridMAZ total.  This script will
# randomly assign the people to each GridMAZ until the total GridMAZ population is reached.  Each person will be assigned to one of the age groups
# with probability as determined by the tract-level proportions of the groups.  Thus, the group membership in any given GridMAZ may not be representative
# of the tract-level proportions, but the combined group membership across all GridMAZ will approximate the tract membership.
# 
# Input parameters:
#   - inDf is a pandas dataframe where each record represents one "this level" geography.  Optionally, the dataframe may include a column that includes the
#     total population for the geography (see 'budgetThisLevel' below)
#   - budgetThisLevel is one of the following:
#     - the name of the column (i.e. a string) in inDf which contains the total populations
#     - a pandas series with the same index as inDf which contains the total populations
#   - groupsNextLevel is a dataframe which describes the groups to which population will be assigned, including the group label, proportion of the population 
#       in the next level geography that belongs to the group, and total population in the next level geography that belongs to the group.  See example
#       below.
#   - firstRoundGroupsExcluded is a list of group labels from groupsNextLevel which should not be assigned to the first person placed in each "this level" 
#     geography. This is useful, for example, when you are allocating population by age and you don't want the only person in geography to be a child.
#     NOTE: firstRoundGroupsExcluded is not implemented as of 2/2024.  
#
# Returns:
#   - outDf is a copy of inDf with one or more columns appended (dtype=int) where each new column includes the population for a group as defined in groupNextLevel
#
# Notes:
#   1. The groupsNextLevel input must be structured as follows:
#     - One record per group
#     - Index consists of the group labels (will be used as column headings in the output)
#     - The following columns must be included:
#       - probability - a float between 0 and 1 which indicates the probability that a person will be assigned 
#           to the group.  Typically this will be the proportion of the population of the next level geography 
#           that belongs to the group
#   2. If the entries in the "probability" column do not sum to 1, the function will interpret this to mean that 
#       there are members of the next level population that do not belong to any group.  Internally, the function
#       will assign these people to a dummy "NOT_ASSIGNED" group, however this group will not be included
#       in the output.  In this case, the sum of group members in the output will not necessdarily sum to the 
#       total population for each "this level" geography.
def groupAssignmentRandom(inDf, budgetThisLevel, groupsNextLevel, firstRoundGroupsExcluded=None):
    import pandas as pd
    import random
    
    # Create a copy of the input dataframe that will be enriched and returned to the user
    outDf = inDf.copy()

    # If budgetThisLevel is a string, interpret this as a field name and extract the series from the
    # input dataframe.  Otherwise, assume it is a series and use it as-is.
    if(type(budgetThisLevel) == str):
        totalsThisLevel = outDf[budgetThisLevel]
    else:
        totalsThisLevel = budgetThisLevel

    for group in groupsNextLevel.index:
        outDf[group] = 0

    # Check whether the total weights assigned to the groups sum to 1.  If not, create a new group
    # called "NOT_ASSIGNED" and give it the remaining weight. 
    assignedWeight = groupsNextLevel["probability"].sum()
    if(assignedWeight < 1):
        groupsNextLevel = pd.concat([groupsNextLevel, pd.DataFrame.from_dict({
            "NOT_ASSIGNED": {
                "probability": 1-assignedWeight
            }
        }, orient="index")], axis="index")
    
    # Create a copy of the group details that we can modify.
    groupsAvailable = groupsNextLevel.copy()
    
    # Iterate through each geography at this level.  For each, randomly assign the total population 
    # to the various groups according to the frequency of each of these groups in the next level geography.
    for idThisLevel in totalsThisLevel.index.to_list():

        # If the total population at this level is zero, leave the population of each group set to zero
        if(totalsThisLevel[idThisLevel] == 0):
            continue

        # Record the number of people at this level that need to be assigned to a group
        totalRemaining = totalsThisLevel[idThisLevel]
    
        # Assign a group label to each person in the geography
        while(totalRemaining > 0):

            # Randomly assign one person to a group. The zero index
            # extracts the age group string from a one-element list.
            try:
                groupLabels = list(groupsAvailable.index)
                groupWeights = list(groupsAvailable["probability"])
                groupAssigned = random.choices(groupLabels, weights=groupWeights, k=1)[0]
            except:
                print("An error occurred during assignment for geography {}".format(idThisLevel))
                raise
 
            # Increment the count in the selected group for this level geography
            if(groupAssigned != "NOT_ASSIGNED"):
                outDf.at[idThisLevel, groupAssigned] += 1
                          
            # Decrement the number of people in the geography waiting to be
            # assigned to a group
            totalRemaining = totalRemaining - 1
        
    return outDf

def recursiveUpdate(original, updates):
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(original.get(key), dict):
            original[key] = recursiveUpdate(original[key], value)
        else:
            original[key] = value
    return original

def data_chart_to_excel(df, writer, sheet_name="Sheet1", chartType="column", dataOptions=None, chartOptions=None):
    """Create an Excel worksheet consisting of the contents of a pandas dataframe (as a formatted table)
    and, optionally, a chart to visualize the series included in the dataframe.  The simplest invocation
    will produce a table and a basic column (vertical bar) chart with default formatting that is consistent
    with MORPC branding guidelines, however the user can specify many of options supported by the xlsxwriter library 
    (https://xlsxwriter.readthedocs.io/).

    Example usage:
        import pandas as pd
        import xlsxwriter
        d = {'col1': [1, 2, 3, 4], 'col2':[3, 4, 5, 6]}
        df = pd.DataFrame(data=d)
        writer = pd.ExcelWriter("./foo.xlsx", engine='xlsxwriter')
        # Simplest invocation. Creates table and column chart on Sheet1 worksheet with default presentation settings.
        morpc.data_chart_to_excel(df, writer)  
        # Creates a table and line chart on the "LineChart" worksheet with default presentation settings.
        morpc.data_chart_to_excel(df, writer, sheet_name="LineChart", chartType="line")
        # Creates a table and stacked column chart on the "Stacked" worksheet with default presentation settings.
        morpc.data_chart_to_excel(df, writer, sheet_name="Stacked", chartType="column", chartOptions={"subtype":"stacked"})
        # Creates a table and bar chart on the "Custom" worksheet with some custom presentation settings.
        morpc.data_chart_to_excel(df, writer, sheet_name="Custom", chartType="bar", chartOptions={
            "colors": ["cyan","magenta"],                   # Specify a custom color
            "hideLegend": True,                             # Hide the legend
            "titles": {                                     # Specify the chart title and axis titles
                "chartTitle": "My Chart",
                "xTitle": "My independent variable",
                "yTitle": "My dependent variable",
            }
        })
        writer.close()
                
    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        The pandas dataframe which contains the data to export.  The dataframe column index will be used as the
        column headers (i.e. the first row) in the output table.  By default, the dataframe row index will become
        the first column in the output table (this can be overridden using the dataOptions argument).  The columns
        in the dataframe will become series in the chart.
    writer : pandas.io.excel._xlsxwriter.XlsxWriter
        An existing xlsxwriter object created using pd.ExcelWriter(..., engine='xlsxwriter'). This represents the
        Excel workbook to which the data and chart will be written. See https://xlsxwriter.readthedocs.io/working_with_pandas.html
    sheet_name : str, optional
        The label for a new worksheet that will be created in the Excel workbook.  Must be unique and cannot exist
        already.  Default value is "Sheet1"
    chartType : str, optional
        A chart type as recognized by xlsxwriter workbook.add_chart. Options include "area", "bar", "column", "doughnut", 
        "line", "pie","radar","scatter","stock". Default is "column". Set to "omit" to omit the chart and include only the
        data table.  Bar and line charts are well-supported. Results with other types may vary. See
        https://xlsxwriter.readthedocs.io/workbook.html#add_chart
    dataOptions: dict, optional
        Various configuration options for the output data table. Currently the following options are supported.
            "index": bool
                Whether to write the index as a column in the Excel file.  Default is True. Set to False to omit the index.
            "numberFormat" : str, list, or dict
                Excel number format string to use for the values in the output table. 
                If a string, the same format will be applied to all columns.
                If a list, the listed formats will be applied to the columns in sequence.  
                If a dict, the dict keys must match the column names and the dict values will contain the format
                    string to use for the column.
                Default is "#,##0.0".  See https://xlsxwriter.readthedocs.io/format.html#set_num_format
            "columnWidth" : int, list, or dict
                Widths of columns in output table. 
                If an int, the same width will be applied to all columns.
                If a list, the listed widths will be applied to the columns in sequence.  
                If a dict, the dict keys must match the column names and the dict values will contain the width
                    to use for the column.            
                Default is 12.  
    chartOptions: dict, optional
        Various configuration options for the output chart. Currently the following options are supported.
            "colors" : str, list, or dict
                Simplified method of specifying the color or color to use for the series in the chart.  Will be 
                overridden by series-specific options in chartOptions["seriesOptions"]. By default will cycle
                through MORPC brand colors.
                If a string, the same color will be used for all series. 
                If a list, the listed colors will be repeated in sequence. 
                If a dict, the dict keys must match the series names and the dict values will determine the colors
                for the corresponding series.
            "hideLegend" : bool
                Simplified method of hiding the legend, which is shown by default.  Set hideLegend = True to hide the
                legend. Will be overridden by settings in chartOptions["legendOptions"].
            "titles" : str or dict
                Simplified method of specifying the chart and axis titles.  Will be overridden by settings in 
                chartOptions["titleOptions"]. 
                If a string, it will be used as the chart title. 
                If a dict, it should have the following form. If any key/value is unspecified, it will default to the
                values shown below.
                    {
                        "chartTitle": sheet_name,
                        "xTitle": df.index.name,
                        "yTitle": df.columns.name
                    }
            "labelOptions" : dict or list of dicts,
                Simplified method of specifying data labels.  Will be overidden by settings in seriesOptions.
                If a dict, the same settings will be applied to all series
                If a list of dicts, the dict keys must match the series names and the dict values will determine the
                settings for the labels for the corresponding series.
                The dict will be used as the data_labels argument for chart.add_series().  See 
                https://xlsxwriter.readthedocs.io/chart.html#chart-add-series and
                https://xlsxwriter.readthedocs.io/working_with_charts.html#chart-series-option-data-labels
            "subtype" : str
                The desired subtype of the specified chartType, as recognized by workbook.add_chart(). Your mileage may
                vary. Some subtypes may not be well supported yet. If unspecified, this will default to whatever default
                xlsxwriter uses for the specified chartType.
                See https://xlsxwriter.readthedocs.io/workbook.html#workbook-add-chart
            "location" : list or str        
                Coordinates specifying where to place the chart on the worksheet.  Default location is to the right of table in
                the first row.  Specify "below" as shorthand to place the chart below the table in the first column.
                Used by worksheet.insert_chart( ). See https://xlsxwriter.readthedocs.io/worksheet.html#worksheet-insert-chart 
                and https://xlsxwriter.readthedocs.io/working_with_cell_notation.html#cell-notation
            "sizeOptions" : dict
                Options to control the size of the chart.  Will be used directly by chart.set_size(). Defaults to xlsxwriter
                defaults. See https://xlsxwriter.readthedocs.io/chart.html#chart-set-size       
            "plotAreaLayout" : dict
                Settings to control the layout of the plot area within the chart.  Will be used directly by chart.set_plotarea().
                Defaults to xlsxwriter defaults.  See https://xlsxwriter.readthedocs.io/working_with_charts.html#chart-layout
            "titleOptions" : dict
                Options to control the appearance of the chart title.  Will be used directly by chart.set_title(). Title text
                defaults to sheet_name. Style defaults to MORPC branding.
                See https://xlsxwriter.readthedocs.io/chart.html#chart-set-title
            "seriesOptions" : dict of dicts or list of dicts
                Options to control how series are displayed.  Used directly by chart.add_series().
                If a dict of dicts, the top level keys must correspond to the column names and the values will be applied to the
                corresponding series. If a key/value is not present for a column name, that series will revert to default settings.
                If a list of dicts, the dicts will be applied to the columns in sequence.
                corresponding series. If there are not enough items in the list for all of the columns, the remaining series will 
                revert to default settings.
                See https://xlsxwriter.readthedocs.io/chart.html#chart-add-series
            "xAxisOptions": dict
                Options to control the appearance of the x axis.  Will be used directly by chart.set_x_axis(). Axis title defaults 
                to df.index.name. Style defaults to MORPC branding. Title will be overridden by "titles" parameter (see above). See 
                https://xlsxwriter.readthedocs.io/chart.html#chart-set-x-axis
            "yAxisOptions": dict
                Options to control the appearance of the y axis.  Will be used directly by chart.set_y_axis(). Axis title defaults 
                to df.columns.name. Style defaults to MORPC branding. Title will be overridden by "titles" parameter (see above). See https://xlsxwriter.readthedocs.io/chart.html#chart-set-y-axis
            "legendOptions": dict
                Options to control the appearance of the legend. Will be used directly by chart.set_legend(). Legend is displayed by
                default and positioned at the bottom of the chart.  Style defaults to MORPC branding. See
                https://xlsxwriter.readthedocs.io/chart.html#chart-set-legend
    
    Returns
    -------
    None
    
    """

    import pandas as pd
    import json
    import xlsxwriter

    axisSwapTypes = ["bar"]

    colorsDefault = CONST_COLOR_CYCLES['morpc'] 

    styleDefaults = {
        "fontName": "Arial",
        "fontSize": 10,
        "titleFontSize": 14,
        "axisNameFontSize": 9,
        "axisNumFontSize": 8,
        "legendFontSize": 10,
        "seriesColor": colorsDefault[0],
        "numberFormat": "#,##0.0",
        "columnWidth": 12
    }
    

    titleDefaults = {
        "chartTitle": sheet_name,
        "xTitle": df.index.name,
        "yTitle": df.columns.name
    }
    
    titleOptionsDefaults = {
        "name": titleDefaults["chartTitle"],
        "overlay": False,
        "name_font": {
            "name": styleDefaults["fontName"],
            "size": styleDefaults["titleFontSize"]
        }
    }
  
    axisOptionsDefaults = {
        "name_font": {
            "name": styleDefaults["fontName"],
            "size": styleDefaults["axisNameFontSize"]
        },
        "num_font": {
            "name": styleDefaults["fontName"],
            "size": styleDefaults["axisNumFontSize"]
        },
        "label_position": 'low',
        "reverse": False
    }


    xAxisOptionsDefaults = json.loads(json.dumps(axisOptionsDefaults))
    xAxisOptionsDefaults["name"] = titleDefaults["xTitle"]

    yAxisOptionsDefaults = json.loads(json.dumps(axisOptionsDefaults))
    yAxisOptionsDefaults["name"] = titleDefaults["yTitle"]

    legendOptionsDefaults = {
        "none": False,
        "position": "bottom",
        "font": {
            "name": styleDefaults["fontName"],
            "size": styleDefaults["legendFontSize"]
        }
    }
 
    seriesOptionsDefault = {
        "common": {
        }
    }

    seriesOptionsDefault["bar"] = json.loads(json.dumps(seriesOptionsDefault["common"]))
    seriesOptionsDefault["bar"] = recursiveUpdate(seriesOptionsDefault["bar"], {
        "border": {"none":True},
        "fill": {
            "color": styleDefaults["seriesColor"]
        }
    })
    seriesOptionsDefault["column"] = json.loads(json.dumps(seriesOptionsDefault["bar"]))

    seriesOptionsDefault["line"] = json.loads(json.dumps(seriesOptionsDefault["common"]))
    seriesOptionsDefault["line"] = recursiveUpdate(seriesOptionsDefault["line"], {
        "line": {
            "color": styleDefaults["seriesColor"],
            "width": 2.5          
        },
        "marker": {
            "type": "circle",
            "size": 5,
            "border": {"none":True},
            "fill": {
                "color": styleDefaults["seriesColor"]
            }
        },
        "smooth": False
    })
    
    subtypesDefaults = {
        "bar": None,
        "column": None,
        "line": None
    }
     
    myDataOptions = {
        "index": True,               # Write the index to the Excel file by default
        # String, list, or dict. If a string, the same format will be applied to all columns.  If a 
        # list, the listed formats will be applied to the columns in sequence.  If a dict, the keys must 
        # match the columns names and the values will format for each.
        "numberFormat": styleDefaults["numberFormat"],
        "columnWidth": styleDefaults["columnWidth"]
    }
    if(dataOptions != None):
        myDataOptions = recursiveUpdate(myDataOptions, dataOptions)

    myChartOptions = {
        # String, list, or dict.  Simplified method of specifying series colors. Overridden by setting in 
        # chartOptions["seriesOptions"]. If a string, the same color will be used for all series. If a 
        # list, the listed colors will be repeated in sequence. If a dict, the keys must match the series 
        # names and the values will determine the colors.
        "colors": None,
        # Bool. Simplified method of hiding the legend. Overridden by setting in chartOptions["legendOptions"]
        "hideLegend": False,
        # String or dict. Simplified method of specifying the chart and axis titles.  Overridden by setting in chartOptions["titleOptions"]. If a string, it will be used as the chart title. If a dict, it will have the same format as titleDefaults
        "titles": None,
        # Dict to be applied to all series or list of dicts, one per series. Simplified method of specifying data labels.  
        # Used by chart.add_series()
        "labelOptions": None,
        "subtype": None,          # String. Defer to chart-specific default. Used by workbook.add_chart()
        "location": None,         # List. Default location is to the right of data. Will be determined later.
        "sizeOptions": None,      # Dict. Will be used by chart.set_size()
        "plotAreaOptions": None,   # Dict. Will be used by chart.set_plotarea()
        "titleOptions": None,     # Dict. Will be used by chart.set_title()
        "seriesOptions": None,    # Dict to be applied to all series or list of dicts, one per series. Used by chart.add_series()
        "xAxisOptions": None,     # Dict. Will be used by chart.set_x_axis()
        "yAxisOptions": None,     # Dict. Will be used by chart.set_y_axis()
        "legendOptions": None,    # Dict. Will be used by chart.set_legend()
        "includeColumns": None    # List of columns to be added as series to chart.   
    }
    if(chartOptions != None):
        myChartOptions = recursiveUpdate(myChartOptions, chartOptions)

    myLegendOptions = json.loads(json.dumps(legendOptionsDefaults))
    if(myChartOptions["hideLegend"] == True):
        myLegendOptions["none"] = True
    if(myChartOptions["legendOptions"] != None):
        myLegendOptions = recursiveUpdate(myLegendOptions, chartOptions["legendOptions"])

    if(myChartOptions["includeColumns"] == None):
        myChartOptions["includeColumns"] = list(df.columns)
       
    workbook = writer.book

    df.to_excel(writer, sheet_name=sheet_name, index=myDataOptions["index"])

    worksheet = writer.sheets[sheet_name]

    if(type(myDataOptions["numberFormat"]) == str):
        numberFormats = workbook.add_format({'num_format': myDataOptions["numberFormat"]})
    elif(type(myDataOptions["numberFormat"]) == list):
        numberFormats = [workbook.add_format({'num_format': value}) for value in myDataOptions["numberFormat"]] 
    elif(type(myDataOptions["numberFormat"]) == dict):
        numberFormats = {key: workbook.add_format({'num_format': value}) for key, value in zip(myDataOptions["numberFormat"].keys(), myDataOptions["numberFormat"].values())}

    columnWidths = json.loads(json.dumps(myDataOptions["columnWidth"]))

    if(myDataOptions["index"] == True):
        indexName = df.index.name
        if(indexName == None):
            indexName = "index"
        df = df.reset_index()
    nRows = df.shape[0]
    nColumns = df.shape[1]
    for i in range(0, nColumns):
        colname = df.columns[i]
        
        if(type(numberFormats) == xlsxwriter.format.Format):
            columnNumberFormat = numberFormats
        elif(type(numberFormats) == list):
            try:
                columnNumberFormat = numberFormats[i]
            except:
                print(f"WARNING: Number format not specified for column {i} (column {colname}). Using default.")
                columnNumberFormat = styleDefaults["numberFormat"]
        elif(type(numberFormats) == dict):
            try:
                columnNumberFormat = numberFormats[colname]
            except:
                print(f"WARNING: Number format not specified for column {colname}). Using default.")
                columnNumberFormat = styleDefaults["numberFormat"]

        if(type(columnWidths) == int):
            columnWidth = columnWidths
        elif(type(columnWidths) == list):
            try:
                columnWidth = columnWidths[i]
            except:
                print(f"WARNING: Column width not specified for column {i} (column {colname}). Using default.")
                columnWidth = styleDefaults["columnWidth"]
        elif(type(columnWidths) == dict):
            try:
                columnWidth = columnWidths[colname]
            except:
                print(f"WARNING: Column width not specified for column {colname}). Using default.")
                columnWidth = styleDefaults["columnWidth"]
        
        worksheet.set_column(i, i, columnWidth, columnNumberFormat)

    if(myDataOptions["index"] == True):
        df = df.set_index(indexName)

    if(chartType == "omit"):
        print("WARNING: Chart type is set to omit.  Chart will be omitted.")
        return

  
    chart = workbook.add_chart({
        "type": chartType, 
        "subtype": (myChartOptions["subtype"] if myChartOptions["subtype"] != None else subtypesDefaults[chartType])
    })

    nRows = df.shape[0]
    nColumns = len(myChartOptions["includeColumns"])
    for i in range(1, nColumns+1):
        colname = myChartOptions["includeColumns"][i-1]
        # Get the position of this column in the worksheet.  It may not match the value of i because of columns omitted by the user. 
        colpos = list(df.columns).index(colname) + 1

        mySeriesOptions = json.loads(json.dumps(seriesOptionsDefault[chartType]))
        
        color = None
        # If the user specified a color or set of colors in chartOptions["colors"], use those instead of the defaults.
        if(myChartOptions["colors"] != None):
            if(type(myChartOptions["colors"]) == str):
                color = myChartOptions["colors"]
            elif(type(myChartOptions["colors"]) == list):
                color = myChartOptions["colors"][(i-1) % len(myChartOptions["colors"])]        
            elif(type(myChartOptions["colors"]) == dict):
                color = myChartOptions["colors"].get(colname, styleDefaults["seriesColor"])   # Revert to default if color is not specified for column
            json.dumps(mySeriesOptions, indent=4)
        # Else if we have more than one series, cycle through the default set of colors
        elif(nColumns > 1):
            color = colorsDefault[(i-1) % len(colorsDefault)]
        # Else, simply stick with the single default color defined above in seriesOptionsDefault

        if(color != None):
            if "fill" in mySeriesOptions.keys():
                mySeriesOptions["fill"]["color"] = color
            if "line" in mySeriesOptions.keys():
                mySeriesOptions["line"]["color"] = color
            if "marker" in mySeriesOptions.keys():                
                mySeriesOptions["marker"]["fill"]["color"] = color

        if(type(myChartOptions["seriesOptions"]) == list):
            try:
                mySeriesOptions = recursiveUpdate(mySeriesOptions, myChartOptions["seriesOptions"][i-1])
            except Exception as e:
                print(f"WARNING: Failed to get chartOptions['seriesOptions'] for list item {i-1} (column {colname}). Using defaults.") 
        elif(type(myChartOptions["seriesOptions"]) == dict):
            try:
                mySeriesOptions = recursiveUpdate(mySeriesOptions, myChartOptions["seriesOptions"][colname])
            except Exception as e:
                print(f"WARNING: Failed to get chartOptions['seriesOptions'] for column {colname}). Using defaults.") 

        mySeriesOptions["name"] = [sheet_name, 0, colpos]
        mySeriesOptions["categories"] = [sheet_name, 1, 0, nRows, 0]
        mySeriesOptions["values"] = [sheet_name, 1, colpos, nRows, colpos]
                
        # Configure chart title
        # Start with default values
        myTitleOptions = json.loads(json.dumps(titleOptionsDefaults))
        # If user provided a dict of title options, update the default values with provided values
        if(myChartOptions["titleOptions"] != None):
            myTitleOptions = recursiveUpdate(myTitleOptions, myChartOptions["titleOptions"])
        # Otherwise, if user provided only the chart title as a string using the simplified form, override the default string
        elif(type(myChartOptions["titles"]) == str):
            myTitleOptions["name"] = myChartOptions["titles"]
        # Otherwise, if user provided a simplified dict of chart titles and axis titles, try to use the provided chart title. If
        # the chart title was not provided in the dict, revert to the default. 
        elif(type(myChartOptions["titles"]) == dict):
            myTitleOptions["name"] = myChartOptions["titles"].get("chartTitle", titleOptionsDefaults["name"])

        # Configure the x-axis
        # Start with default values
        myXAxisOptions = json.loads(json.dumps(xAxisOptionsDefaults))
        # If user provided a dict of x-axis options, update the default values with provided values
        if(myChartOptions["xAxisOptions"] != None):
            myXAxisOptions = recursiveUpdate(myXAxisOptions, myChartOptions["xAxisOptions"])
        # Otherwise, if user provided a simplified dict of chart titles and axis titles, try to use the provided x-axis title. If
        # the x-axis title was not provided in the dict, revert to the default. 
        if(type(myChartOptions["titles"]) == dict):
            myXAxisOptions["name"] = myChartOptions["titles"].get("xTitle", xAxisOptionsDefaults["name"])

        # Configure the y-axis
        # Start with default values
        myYAxisOptions = json.loads(json.dumps(yAxisOptionsDefaults))
        # If user provided a dict of y-axis options, update the default values with provided values
        if(myChartOptions["yAxisOptions"] != None):
            myYAxisOptions = recursiveUpdate(myYAxisOptions, myChartOptions["yAxisOptions"])
        # Otherwise, if user provided a simplified dict of chart titles and axis titles, try to use the provided y-axis title. If
        # the y-axis title was not provided in the dict, revert to the default. 
        if(type(myChartOptions["titles"]) == dict):
            myYAxisOptions["name"] = myChartOptions["titles"].get("yTitle", yAxisOptionsDefaults["name"])
           
        chart.add_series(mySeriesOptions)

    if(chartType in axisSwapTypes):
        tempX = myXAxisOptions["name"]
        tempY = myYAxisOptions["name"]
        myXAxisOptions["name"] = tempY
        myYAxisOptions["name"] = tempX
 
    chart.set_title(myTitleOptions)
    chart.set_x_axis(myXAxisOptions)
    chart.set_y_axis(myYAxisOptions)        
    chart.set_legend(myLegendOptions)   
    # If the user specified chart size options, use them as-is. There are 
    # no defaults for this.
    if(myChartOptions["sizeOptions"] != None):
            chart.set_size(myChartOptions["sizeOptions"])
    # If the user specified a plot area layout, use it as-is. There are 
    # no defaults for this.
    if(myChartOptions["plotAreaOptions"] != None):
        chart.set_plotarea(myChartOptions["plotAreaOptions"])
    
    if(myChartOptions['location'] == "below"):
        # If the user specifies "below", put the chart below the table in the first column
        myLocation = [worksheet.dim_rowmax+2, 0]
    elif(myChartOptions['location'] != None):
        # If the user specified the location in some other way, use their specification as-is
        myLocation = myChartOptions['location']
    else:
        # Otherwise, if the user did not specify the location, then put the chart to the right of the table in the first row
        myLocation = [0, worksheet.dim_colmax+2]
    
    if(type(myLocation) == list):
        worksheet.insert_chart(myLocation[0], myLocation[1], chart)
    elif(type(myLocation) == str):
        worksheet.insert_chart(myLocation, chart)
    else:
        print('ERROR: Chart location must be specified in list form as [row,col] or as a cell reference string like "A5"')
        raise RuntimeError

def extract_vintage(df, vintage=None, refPeriods=None, vintagePeriodField="VINTAGE_PERIOD", refPeriodField="REFERENCE_PERIOD"):
    """From a long-form dataset containing values of various vintages, extract the value for a select vintage for each period.
    If the desired periods are not specified, extract all available periods.  If a single desired vintage is not specified,
    extract the latest available vintage for each period.

    WARNING: This function assumes that if a vintage is available for any records for a reference period, then that vintage is 
    available for all records associated with that reference period.  This is an opportunity for improvement, but until then
    check the output yourself.

    Example usage: See morpc-common-demos.ipynb
                
    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        The pandas dataframe which contains the data from which to generate an extract. The data must contain a column whose
        values represent the reference period for each record (see refPeriodField) and a column whose values represent the
        vintage period for each record (see vintagePeriodField)
    refPeriods: list, optional
        A list containing the desired reference period(s) to extract from the data. List items should have the same type as the
        reference period column (refPeriodField).  If refPeriods == None, all available reference periods will be included in
        the output.
    vintage: scalar (usually int), optional
        A value indicating the desired vintage of the records to be extracted from the data. This should have the same type as
        vintage period column (vintagePeriodField) and must be a type that is compatible with numpy.max (see https://numpy.org/doc/stable//reference/generated/numpy.max.html)  If vintage == None, the most recent available 
        vintage for each reference period will be extracted.
    refPeriodField: scalar, optional
        The name of the column in df that contains the reference periods. If unspecified, defaults to "REFERENCE_PERIOD".
    vintagePeriodField: scalar, optional
        The name of the column in df that contains the vintage periods. If unspecified, defaults to "VINTAGE_PERIOD".
    
    Returns
    -------
    outDf : pandas.core.frame.DataFrame
        A subset of df that contains only the specified (or most recent) vintage for the requested reference periods
    
    """
    import pandas as pd
    
    # If user specified a set of reference periods, verify that all requested periods are present and extract those. 
    # Otherwise keep the whole input dataframe.
    if refPeriods == None:
        tempDf = df.copy()
        refPeriods = list(tempDf[refPeriodField].unique())
    else:
        tempDf = df.loc[df[refPeriodField].isin(refPeriods)].copy()
        if not set(tempDf[refPeriodField]) == set(refPeriods):
            # If any of the requested periods are not available, list those and throw an error
            print("ERROR: The following requested reference periods are not available in the data: {}".format(
                ", ".join([str(x) for x in set(refPeriods) - set(tempDf[refPeriodField])])
            ))
            raise RuntimeError

    # Construct a dictionary mapping each reference period to a particular vintage
    selectedVintages = {}
    for period in refPeriods:
        # Make a list of the available vintages for each reference period.  See warning in docstring above.
        availableVintages = tempDf.loc[tempDf[refPeriodField] == period, vintagePeriodField].unique()
        if vintage != None:
            # If the user specified a vintage, make sure that the vintage is available for this reference period
            if not vintage in availableVintages:
                # If requested vintage is not available, throw an error
                print("ERROR: Requested vintage is not available for reference period {}".format(period))
                raise RuntimeError
            else:
                # Otherwise, select that vintage
                selectedVintages[period] = vintage
        else:
            # If the user did not specify a vintage, select the largest (most recent) vintage available for this period
            selectedVintages[period] = availableVintages.max()

    # For each reference period, extract the records associated with the selected vintage for that period.
    # TBD - Is there a more efficient way to do this?
    firstTime = True
    for thisPeriod in selectedVintages:
        # Extract the records for this period which are associated with the selected vintage
        temp = tempDf.loc[(tempDf[refPeriodField] == thisPeriod) & (tempDf[vintagePeriodField] == selectedVintages[thisPeriod])].copy()
        if(firstTime):
            # If this is the first reference period (i.e. the first time through the loop) construct the output dataframe from the extract
            firstTime = False
            outDf = temp.copy()
        else:
            # If this is not the first reference period, append the extract to the existing output
            outDf = pd.concat([outDf, temp], axis="index")

    return outDf
    
def qcew_areas_to_suppress(areaPolygonsGDF, qcewPointsGDF, employmentColumn="EMP", verbose=True):
    """The jobs data included in MORPC's GridMAZ forecasts is derived from point-level data from the Quarterly 
    Census of Employment and Wages (QCEW) and may contain data that could identify specific employers.  To protect 
    employer privacy and ensure compliance with our data use agreement, values must be suppressed in the following 
    conditions:
        1. There are fewer than 3 employers in a geography
        2. There are 3 or more employers but a single employer represents 80% or more of the employment in the 
           geography by industry.
 
    Given a set of polygons that represent areas intended to summarize QCEW data, this function determines the areas for 
    which data must be suppressed to satsify the above two conditions.  The function uses a spatial join to assign each 
    QCEW employer location to a polygon, summarizes the points in each polygon, and checks both of the conditions. The
    function returns a pandas Series object indicating which of the indices in the polygon geodataframe need to be
    suppressed due to meeting one or more of the criteria.

    CAVEAT: Regarding the second condition, this function only supports suppression of TOTAL JOBS, not an industry
    subset.  Since we are not breaking down the jobs by industry, it is sufficient to suppress the geographies where an 
    employer represents 80% or more of the the total employment.
    
    Example usage:

    Parameters
    ----------
    areaPolygonsGDF : geopandas.geodataframe.GeoDataFrame with polygon geometry type
        A GeoPandas GeoDataFrame containing the polygons for which the QCEW would be summarized.  Only the geometries
        are required.  The other columns will not be used and no summary is provided by this function.  It is assumed
        that the area polygons are non-overlapping.
    qcewPointsGDF : geopandas.geodataframe.GeoDataFrame with point geometry type
        A GeoPandas GeoDataFrame containing the QCEW employer locations (points). Must include a column containing
        the total employment provided by the employer (see below).  Only the geometry and the employment column
        will be used.
    employmentColumn : str
        Optional. Name of the column in qcewPointsGDF that contains the employment provided by each employer. If unspecified, 
        this will default to "EMP".
    verbose : boolean
        Optional. Default value is True. Set to False to suppress informational text output from the function.

    Returns
    -------
    areaPolygonsSuppressed : pandas.core.series.Series
        A Pandas Series using the same index as areaPolygonsGDF whose values indicate whether the record must be 
        suppressed (True) or not (False)
    
    """
    import pandas as pd
    import geopandas as gpd
    
    employerLocations = qcewPointsGDF.copy()

    # Get the index column name so that we'll know what it is after we reset the index
    if(areaPolygonsGDF.index.name == None):
        indexColumn = "index"
    else:
        indexColumn = areaPolygonsGDF.index.name

    # Use a spatial join to associate each of the points with one of the area polygons
    employerLocationsEnriched = employerLocations.sjoin(areaPolygonsGDF.reset_index()[[indexColumn,"geometry"]])

    # Verify that all employers now have a polygon ID assigned
    temp = employerLocationsEnriched.loc[employerLocationsEnriched[indexColumn].isna()].copy()
    if not temp.empty:
        print("morpc.qcew_areas_to_suppress | WARNING | Some employer locations were not assigned to a polygon.")

    ## Determine which geographies have fewer than 3 employers.  Store the list of geography identifiers in `lowCountGeos`.
    # Create a temporary dataframe with minimal attributes.
    temp = employerLocationsEnriched[[indexColumn]].copy()
    # Create a field to tabulate the count.  Set it to 1 since each record counts as 1.
    temp["COUNT"] = 1
    # Count the records in each geography
    temp = temp.groupby(indexColumn).count().reset_index()
    # Create a list of the unique geography IDs that have fewer than 3 employers.
    lowCountGeos = temp.loc[temp["COUNT"] < 3, indexColumn].unique()
    # Don't print out the entire list of IDs, but rather just the number of geographies in the list.
    if(verbose):
        print("morpc.qcew_areas_to_suppress | INFO | There are {} geographies containing fewer than 3 employers".format(len(lowCountGeos)))

    ## Determine which geographies have 3 or more employers and in which a single employer represents 80% or more of 
    ## the total employment.
    # Create a temporary dataframe with minimal attributes.
    temp = employerLocationsEnriched \
        .loc[employerLocationsEnriched[indexColumn].isin(lowCountGeos) == False, [indexColumn, employmentColumn]] \
        .copy()
    # Include only the employers who employ one or more workers.
    temp = temp.loc[temp[employmentColumn] > 0].copy()
    # Sum the employees in each geography and associate the geography sum with each record in the geography
    temp = temp.merge(temp.groupby(indexColumn).sum().rename(columns={employmentColumn:"GRID_SUM"}), on=indexColumn)
    # Compute the share of the geography sum that each employer represents
    temp["GRID_SHARE"] = temp[employmentColumn] / temp["GRID_SUM"]
    # Identify the geographies containing an employer whose geography share is 80% or more.
    highShareGeos = temp.loc[temp["GRID_SHARE"] >= 0.8, indexColumn].unique()
    if(verbose):
        print("morpc.qcew_areas_to_suppress | INFO | There are {} geographies containing employers with a share 80% or greater".format(len(highShareGeos)))

    ## Create a single list of the geographies that meet either of the two suppression conditions.  
    ## The blocks above are structured in such a way that the two lists are mutually exclusive, therefore the 
    ## length of the combined list should be the sum of the lengths of the individual lists.
    suppressGrids = pd.Index(lowCountGeos).union(pd.Index(highShareGeos))
    if(verbose):
        print("morpc.qcew_areas_to_suppress | INFO | There are {} geographies that must be suppressed.".format(len(suppressGrids)))

    return suppressGrids
    
def add_placecombo(df, countyField="COUNTY", jurisField="JURIS", munitypeField="MUNITYPE"):
    import pandas
    import geopandas
    outDf = df.copy()
    outDf["PLACECOMBO"] = outDf[countyField].str.upper() + "_" + outDf[jurisField].str.upper() + "_" + outDf[munitypeField].str.upper()
    return outDf