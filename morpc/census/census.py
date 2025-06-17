import json

ACS_MISSING_VALUES = ["","-222222222","-333333333","-555555555","-666666666","-888888888","-999999999"]

ACS_PRIMARY_KEY = "GEO_ID"

ACS_ID_FIELDS = {
    "blockgroup": [
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
    "msa": [
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
        r = requests.get(url, params=shortListParams)
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
    
    labelSeries = labelSeries \
        .apply(lambda x:x.split("|")[0]) \
        .str.strip() \
        .str.replace("!!","") \
        .apply(lambda x:x.split(":"))    
    df = labelSeries \
        .apply(pd.Series) \
        .drop(columns=0) \
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
def acs_generate_dimension_table(acsDataRaw, schema, idFields, dimensionNames):
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
        .join(morpc.census.acs_label_to_dimensions(dimensionTable['description'], dimensionNames=dimensionNames), how="left") \
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
# inDf is a pandas dataframe that was created using acs_generate_dimension_table()
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


