import logging

logger = logging.getLogger(__name__)


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


