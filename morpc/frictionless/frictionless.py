"""
Functions for manipulating schemas in Frictionless TableSchema format
Reference: https://specs.frictionlessdata.io/table-schema/
"""

import logging

from sqlalchemy import False_

logger = logging.getLogger(__name__)

import datetime


def load_schema(path):
    """Given the path to a Frictionless schema file in JSON or YAML format, load the file into memory as a Frictionless Schema object.
    Parameters:
    -----------
    path : path
        Path to the schema file
    """
    import frictionless
    logger.debug(f"Loading schema from {path}")
    return frictionless.Schema(path)


def load_resource(path):
    """
    Given the path to a Frictionless Resource file in JSON or YAML format, load the file into memory as a Frictionless
    Resource object.

    Parameters:
    -----------
    path : path
        Path to the resource file
    """
    import frictionless
    logger.debug(f"Loading resource from {path}")

    return frictionless.Resource(path)


def get_field_names(schema):
    """
    Given a Frictionless TableSchema object, return a list containing the names of the fields defined in the schema.
    NOTE: This is implemented natively using the TableSchema.field_names() method. Functional implementation is just to provide
    consistency with morpc.avro_get_field_names()

    Parameters:
    -----------
    schema : frictionless.Schema
    """

    import frictionless
    logger.debug(f"Getting field name from schema.")
    return schema.field_names


def name_to_dtype_map(schema):
    """
    Given a Frictionless TableSchema object, return a dictionary mapping each field name to the corresponding data type
    specified in the schema.  The resulting dictionary is suitable for use by the pandas.DataFrame.astype() method (for example)

    Parameters:
    -----------
    schema : frictionless.Schema
    """
    import frictionless
    logger.debug(f"Mapping data type from field name.")
    return {schema.fields[i].name:schema.fields[i].type for i in range(len(schema.fields))}    


def name_to_desc_map(schema):
    """
    Given a Frictionless TableSchema object, return a dictionary mapping each field name to the corresponding description
    specified in the schema.

    parameters:
    -----------
    schema :  frictionless.Schema
    """
    import frictionless
    logger.debug(f"Mapping schema names to description.")
    return {schema.fields[i].name:schema.fields[i].description for i in range(len(schema.fields))}

  
def cast_field_types(df, schema, forceInteger=False, forceInt64=False, nullBoolValue=False, handleMissingFields="error", handleMissingValues=True, verbose=False):
    """
    Given a dataframe and the Frictionless Schema object (see load_schema), recast each of the fields in the 
    dataframe to the data type specified in the schema. s

    Parameters:
    ----------
    df : pandas.Dataframe
        The dataframe to apply the data types to. 

    schema : frictionless.Schema
        The Frictionless Schema object which defines the desired data types for each field.

    forceInteger : bool
        Optional. If True, then try harder to cast integer fields.  This may involve rounding
        the values to the ones places. Defaults to False.
    
    forceInt64 : bool
        Optional. If True, then cast all integer fields as Int64 regardless of whether this is
        necessary.  This is useful when trying to merge dataframes which would otherwise have mixed
        int32 and Int64 fields. Defaults to False.
    
    nullBoolValue : bool
        Optional. When casting boolean fields, this parameter specifies whether null values
        should be interpreted as True or False.  Defaults to False.

    handleMissingFields : str
        Optional. Specifies how to handle fields that are defined in the schema but not present
        in the dataframe.  If "error", an error will be raised.  If "ignore", the field will be skipped.
        If "add", the field will be added to the dataframe with null values and the correct type.  Defaults to "error".

    handleMissingValues : boolean
        Optional. Specifies how to handle missing values as defined in the schema. 
        If True, convert all values in missing values to np.nan.

    Returns:
    -------
    outDF : pandas.Dataframe
        A copy of the input dataframe with the field types cast according to the schema.

    """

    import frictionless
    import pandas as pd
    import shapely
    import json
    import numpy as np
    outDF = df.copy()

    if handleMissingValues:
        logger.info(f"handleMissingValues set to True, converting {schema.missing_values} to np.nan")
        for field in schema.fields:
            outDF[field.name] = [np.nan if x in schema.missing_values else x for x in outDF[field.name]]

    for field in schema.fields:
      
        fieldName = field.name
        fieldType = field.type 
        if(not fieldName in df.columns):
            if(handleMissingFields == "ignore"):
                logger.info("Skipping field {} which is not present in dataframe".format(fieldName))
                continue
            elif(handleMissingFields == "add"):
                logger.info("Adding field {} which is not present in dataframe".format(fieldName))
                add_missing_fields(df, schema, fieldNames=fieldName, verbose=False)
                continue
            else:
                logger.error("Field {} is not present in dataframe. To handle missing fields, see argument handleMissingFields.".format(fieldName))
                raise RuntimeError
   
        logger.debug("Casting field {} as type {}.".format(fieldName, fieldType))
        # The following section is necessary because the pandas "int" type does not support null values.  If null values are present,
        # the field must be cast as "Int64" instead.
        if((fieldType == "int") or (fieldType == "integer")):
            try:
                if(forceInt64 == True):
                    # Cast all integer fields as Int64 whether this is necessary or not.  This is useful when trying to merge
                    # dataframes with mixed int32 and Int64 values.
                    outDF[fieldName] = outDF[fieldName].astype("Int64")
                else:
                    # Try to cast the field as an "int".  This will fail if nulls are present.
                    outDF[fieldName] = outDF[fieldName].astype("int")
            except:
                try:
                    # Try to cast as "Int64", which supports nulls. This will fail if the fractional part is non-zero.
                    logger.info("Failed conversion of fieldname {} to type 'int'.  Trying type 'Int64' instead.".format(fieldName))
                    outDF[fieldName] = outDF[fieldName].astype("Int64")
                except:
                    if(forceInteger == True):
                        # If the user has allowed coercion of the values to integers, then round the values to the ones place prior to 
                        # converting to "Int64"
                        logger.warning("Failed conversion of fieldname {} to type 'Int64'.  Trying to round first.".format(fieldName))
                        outDF[fieldName] = outDF[fieldName].astype("float").round(0).astype("Int64")
                    else:
                        # If the user has not allow coercion of the values to integers, then throw an error.
                        logger.error("Unable to coerce value to Int64 type.  Ensure that fractional part of values is zero, or set forceInteger=True")
                        raise RuntimeError           
        elif(fieldType == "number"):
            outDF[fieldName] = outDF[fieldName].astype("float")
        elif(fieldType == "date" or fieldType == "datetime"):
            outDF[fieldName] = pd.to_datetime(outDF[fieldName])
        elif(fieldType == "geojson"):
            try:
                logger.info(f"Fieldname {fieldName} as geojson. Attempting to convert to geometry.")
                outDF[fieldName] = [shapely.geometry.shape(json.loads(x)) for x in outDF[fieldName]]
            except RuntimeError as r:
                logger.error(f"Unable to convert to geometry. {r}")
            finally:
                logger.info(f"Field {fieldName} cast as geometry.")
        elif(fieldType == "boolean"): 
            if(outDF[fieldName].dtype == "bool"):
                logger.warning("Field {} already cast as boolean type. Skipping casting for this field.".format(fieldName))
                continue
            elif(pd.api.types.is_numeric_dtype(outDF[fieldName])):
                logger.warning("Field {} is numeric type. Using standard numeric boolean associations. Nulls will be interpreted as {}. To change this, set nullBoolValue.".format(fieldName, nullBoolValue))
                if(nullBoolValue == True):
                    outDF[fieldName] = outDF[fieldName].fillna(1)
                else:
                    outDF[fieldName] = outDF[fieldName].fillna(0)
                outDF[fieldName] = outDF[fieldName].astype("bool")
            elif((outDF[fieldName].dtype == "string") | (outDF[fieldName].dtype == "object")):
                # If the field is object type, make sure we can interpret it as a string
                if(outDF[fieldName].dtype == "object"):
                    try:
                        outDF[fieldName] = outDF[fieldName].astype("string")
                    except:
                        print("morpc.frictionless.cast_field_types | ERROR | Failed to convert field {} from object type to string type prior to interpretation of boolean values.".format(fieldName))
                        raise RuntimeError

                print("morpc.frictionless.cast_field_types | WARNING | Field {} is string type. Will interpret using truth values specified in schema (or Frictionless defaults). Nulls will be interpreted as {}. To change this, set nullBoolValue.".format(fieldName, nullBoolValue))
                # The field definition in the schema may contain properties trueValues and/or falseValues which specify what values
                # represent True and False, respectively. If trueVales or falseValues are unspecified, Frictionless recognizes the 
                # following values by default:
                #   trueValues: ['true', 'True', 'TRUE', '1']
                #   falseValues: ['false', 'False', 'FALSE', '0']
                trueValues = field.true_values
                falseValues = field.false_values

                # Map each of the true and false values to the appropriate Python boolean values
                truthMap = {}
                for value in trueValues:
                    truthMap[value] = True
                for value in falseValues:
                    truthMap[value] = False

                # Compare the values found in the field to the set of valid true and false values.  If there are values in the
                # data that are among the valid values, throw an error.
                validValuesSet = set(list(truthMap.keys()))
                foundValuesSet = set(outDF[fieldName].unique())
                if(foundValuesSet > validValuesSet):
                    logger.error("Fieldname {0} contains values that are not recognized as true or false: {1}".format(fieldName, ", ".join(list(foundValuesSet-validValuesSet))))
                    raise RuntimeError

                # Now that we are confident that all of the values are valid in string form, map them to actual boolean values
                outDF[fieldName] = outDF[fieldName].map(truthMap)

                # Fill nulls will the first of the specified true values or false values, depending on the setting of nullBoolValue
                if(nullBoolValue == True):
                    outDF[fieldName] = outDF[fieldName].fillna(trueValues[0])
                else:
                    outDF[fieldName] = outDF[fieldName].fillna(falseValues[0])
                outDF[fieldName] = outDF[fieldName].astype("bool")                
                            
                # Finally, make the change official by changing the pandas field type to "bool".
                outDF[fieldName] = outDF[fieldName].astype("bool")
            else:
                logger.error("Field {} is a type that is not currently supported for casting to boolean. Convert it to boolean, numeric, or string types first.".format(fieldName))
                raise RuntimeError
            
        else:
            outDF[fieldName] = outDF[fieldName].astype(fieldType)
            
    return outDF

# Given a dataframe and the Frictionless Schema object (see load_schema), add any fields in the schema that
# are missing in the dataframe.  If fieldNames == None, any fields missing from the schema will be added to the dataframe
# with the correct type and null values.  If fieldNames is a string or list of strings, only those fields will be added.
def add_missing_fields(df, schema, fieldNames=None):
    import frictionless
    outDF = df.copy()
    
    if(fieldNames == None):
        myFieldNames = schema.field_names
    elif(type(fieldNames) == str):
        myFieldNames = [fieldNames]
    elif(type(fieldNames) == list):
        myFieldNames = fieldNames
    else:
        logger.error("If provided, argument fieldNames must be a string containing a single field name or a list of strings")
        raise RuntimeError
    
    # Iterate through all of the fields defined in the schema    
    for field in schema.fields:
        fieldName = field.name
        fieldType = field.type    

        # If this field is not in the list of fields to add, skip it and move on to the next
        if(not fieldName in myFieldNames):
            continue

        # If the requested field is actually missing then add it. Otherwise notify the user that it is already present and skip it.
        if(not fieldName in df.columns):
            # If the field is missing, add it.
            logger.info("add_missing_fields | INFO | Adding missing field {0}, type {1}, filled with null values.".format(fieldName, fieldType))
            outDF[fieldName] = None
                        
            if((fieldType == "int") or (fieldType == "integer")):
                logger.warning("Field {0} specified as type {1} (pandas type 'int'), which does not support null values in pandas. Casting field as pandas type 'Int64' instead.".format(fieldName, fieldType))
                df[fieldName] = df[fieldName].astype("Int64")
            elif(fieldType == "number"):
                outDF[fieldName] = outDF[fieldName].astype("float")
            else:
                outDF[fieldName] = outDF[fieldName].astype(fieldType)
        else:
            # If the field is not missing, skip it
            logger.warning("User-specified field {0} is already present in the dataframe. Skipping it.".format(fieldName))
            continue

    return outDF
        


def create_resource(dataPath, title=None, name=None, description=None, sources=None, resourcePath=None, schemaPath=None, resFormat=None, 
                                 resProfile=None, resMediaType=None, computeHash=True, computeBytes=True, ignoreSchema=False, 
                                 writeResource=False, validate=False):
    """Create a Frictionless resource object using sane default values for some attributes.  Optionally, write the 
    resource file to disk and validate the resource file, schema, and data. 

    Parameters
    ----------
    dataPath : str
        The path to the data file that the resource file will describe, as you want it to appear in the resource file.  
        Typically the data lives in the same directory as the resource file, in which case dataPath is simply the data file name.  
        Could instead be a relative path (RELATIVE TO THE LOCATION OF THE RESOURCE FILE) or a URL.  It may NOT be an absolute path.
    title : str
        Optional. The value for the title attribute in the resource file. A human-readable title that describes the data. If 
        unspecified, defaults to a title derived from the data file name.
    name : str
        Optional. The value for the name attribute in the resource file.  A unique, machine-readable string to refer to the resource.
        Must be lowercase and must not contain spaces. If unspecified, defaults to a name derived from the data file name.
    description : str
        Optional. The value for the description attribute in the resource file. A human-readable detailed description of the data and
        any interpretation or usage guidelines as required.  If unspecified, defaults to a generic description attributing
        the data to MORPC.
    sources : list of dict
        Optional. The value for the sources attribute in the resource file.  A list of dictionaries containing source information for the data
        include name and path and _params.  If unspecified, no source information will be included in the resource.
        ex. [{"name": "MORPC", "path": "https://www.morpc.org"}]
    resourcePath : str
        Optional. If you wish to write the resource object to disk as a resource file (see writeResource), you may specify the target 
        path here. Can be an absolute path or a path RELATIVE TO THE CURRENT WORKING DIRECTORY of the script. The values for dataPath 
        and schemaPath typically should be specified relative to this location. If unspecified, the resource will be created in the 
        directory specified or implied by dataPath. In that case it will have the same basename as the data file but with 
        the extension replaced by ".resource.yaml"
    schemaPath : str
        Optional. The path to the schema file that describes the data.  Typically the schema lives in the same directory as the 
        resource file, in which case this is just the schema file name.  Could instead by a relative path (RELATIVE TO THE LOCATION OF THE
        RESOURCE file) or a URL.  It may NOT be an absolute path.  If unspecified, it will be assumed that the schema is in the same
        directory as the data and that it hase same basename as the data file but with the extension replaced by ".schema.yaml".  If
        ignoreSchema is True, the schema will be omitted from the resource, regardless of whether a path is specified.
    resFormat : str
        Optional. The value for the format attribute in the resource file.  The file type in which the data is formatted (e.g. csv, xlsx,
        json). If unspecified, will attempt to infer this from the extension of the data file. See Frictionless documentation for supported formats and EXTENSION_MAP in the function code for the subset of formats that can be inferred.
    resProfile : str
        Optional. The value for the profile attribute in the resource file. If unspecified, defaults to "data-resource". Typically you will 
        not have to change this.  See Frictionless documentation for other supported profiles.
    resMediaType : str
        Optional. The value for the mediatype attribute in the resource file.  The MIME type that best describes the data file. If
        unspecified, will attempt to infer this from the extension of the data file. If you need to specify it manually, search the internet for the appropriate MIME type.  See EXTENSION_MAP in the function code for the subset of mediatypes that can be inferred.
    computeHash : bool
        Optional. If True, compute the MD5 hash for the data file and include it in the hash attribute in the resource. Defaults to True. If resourcePath is not specified, assume the data path is relative to the current working directory.  
    computeBytes : bool
        Optional. If True, compute the file size for the data file and include it in the bytes attribute in the resource. Defaults to True. If resourcePath is not specified, assume the data path is relative to the current working directory.  
    ignoreSchema : bool
        Optional. If True, no schema information will be included in the resource even if a path is provided.
    writeResource : bool
        Optional. If True, write the resource file to disk.  Defaults to false.  If resourcePath is provided, use that path.  If resourcePath is not provided, write the resource to the current working directory.
    validate : bool
        Optional. If True, the resource file, schema file, and data file will be validated. Note that writeResource must be True to
        use this option.

    Returns
    -------
    resource : frictionless.resources.table.TableResource
        A Frictionless TableResource object which describes the data
    """
    import os
    import re
    import frictionless
    import morpc

    EXTENSION_MAP = {
        ".gpkg": {
            "format":"gpkg",
            "mediatype":"geopackage+sqlite3"
        },
        ".csv": {
            "format":"csv",
            "mediatype":"text/csv"
        },
        ".xls": {
            "format":"xls",
            "mediatype":"application/vnd.ms-excel"
        },
        ".xlsx": {
            "format":"xlsx",
            "mediatype":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        },
        ".dbf": {
            "format":"dbf",
            "mediatype":"application/dbf"
        }        
    }
    
    dataFilePath = os.path.normpath(dataPath)
    dataFileName = os.path.splitext(os.path.basename(dataFilePath))[0]
    dataFileExtension = os.path.splitext(os.path.basename(dataFilePath))[1]

    if(os.path.basename(dataFilePath) != os.path.normpath(dataFilePath)):
        # If dataFilePath is not simply a filename
        logger.warning("You seem to have specified a data path that is not simply a file name.  This implies that the data is located in a different directory than the resource file.  Typically the data is located in the same directory as the resource file and the path is simply the filename.")   

    resourceFilePath = None
    if(resourcePath != None):
        if(not writeResource):
            # Warn the user if they specified a resource file location but did not enable writeResource
            logger.warning("You specified a path for the resource file, however writeResource is not set to True. Resource file will not be written to disk.")   

        # If the user has specified a path to the resource file, we'll use it without modification. Warn the user if the choice is unusual.
        if(os.path.basename(dataFilePath) != os.path.normpath(dataFilePath)):
            # If dataFilePath is not simply a filename
            if(os.path.dirname(os.path.abspath(resourcePath)) != os.path.dirname(os.path.abspath(dataFilePath))):
                # If the absolute path to the resource file and the absolute path to the data put them in different directories
                logger.warning("You seem to have specified a path for the resource file that is in a different directory than the data.  Typically the data is located in the same directory as the resource file and the path is simply the filename.")   
        resourceFilePath = os.path.normpath(resourcePath)
        
    if resFormat != None:
        resourceFormat = resFormat
    else:
        if dataFileExtension.lower() in EXTENSION_MAP:
            resourceFormat = EXTENSION_MAP[dataFileExtension.lower()]["format"]
            logger.info("Format not specified. Using format derived from data file extension: {}".format(resourceFormat))
        else:
            logger.error("Format not specified and could not be determined from data file extension.")
            raise RuntimeError

    if(not ignoreSchema):
        # If ignoreSchema is False, determine the schema file path
        if(schemaPath != None):
            # If the user has specified a path to the resource file, we'll use it without modification. Warn the user if the choice is unusual.
            if(os.path.basename(dataFilePath) != os.path.normpath(dataFilePath)):
                # If dataFilePath is not simply a filename
                if(os.path.dirname(os.path.abspath(schemaPath)) != os.path.dirname(os.path.abspath(dataFilePath))):
                    # If the absolute path to the schema file and the absolute path to the data put them in different directories
                    logger.warning("You seem to have specified a path for the schema file that is in a different directory than the data.  Typically the schema is located in the same directory as the data.")   
            schemaFilePath = os.path.normpath(schemaPath)
        else:
            # If the user has not specified a path to the schema file, we'll assume that it should go in the same directory as the data. In that
            # case, derive the path from the data path.
            schemaFilePath = dataFilePath.replace(dataFileExtension, ".schema.yaml")
            logger.info("morpc.frictionless.create_resource | INFO | Schema path not specified. Using path derived from data file path: {}".format(schemaFilePath))

    if title != None:
        resourceTitle = title
    else: 
        resourceTitle = dataFileName
        logger.info("Title not specified. Using placeholder value derived from data filename: {}".format(resourceTitle))

    if name != None:
        resourceName = name
    else:
        resourceName = re.sub(r"\W+", "-", dataFileName).lower()
        logger.info("Name not specified. Using placeholder value derived from data filename: {}".format(resourceName))

    if description != None:
        resourceDescription = description
    else:
        resourceDescription = "This dataset was produced by MORPC. For more information, please contact dataandmaps@morpc.org."
        logger.info("Description not specified. Using boilerplate placeholder value: {}".format(resourceDescription))

    if sources != None:
        resourceSources = sources
    else:
        resourceSources = None  
        logger.info("Sources not specified. No source information will be included in the resource.")

    if resMediaType != None:
        resourceMediaType = resMediaType
    else:
        if dataFileExtension.lower() in EXTENSION_MAP:
            resourceMediaType = EXTENSION_MAP[dataFileExtension.lower()]["mediatype"]
        else:
            logger.error("Media type not specified and could not be determined from data file extension.")
            raise RuntimeError        

    if resProfile != None:
        resourceProfile = resProfile
    else:
        resourceProfile = "data-resource"

    resource = frictionless.Resource.from_descriptor({
        "name": resourceName,
        "title": resourceTitle,
        "description": resourceDescription,
        "profile": resourceProfile,
        "path": dataFilePath,
        "format": resourceFormat,
        "mediatype": resourceMediaType,
    })

    if(not ignoreSchema):
        resource.schema = schemaFilePath

    unlocatedDataWarningIssued = False
    if(computeHash):
        if(resourceFilePath != None):
            resource.hash = morpc.md5(os.path.join(os.path.dirname(resourceFilePath), dataFilePath))
        else:
            try:
                logger.warning("Data path is specified relative to resource file, however no resource file path was specified. Assuming data path is relative to current working directory.")
                unlocatedDataWarningIssued = True
                resource.hash = morpc.md5(dataFilePath)
            except:
                logger.error("Unable to compute MD5 hash.  Data file could not be located.")
                raise RuntimeError            

    if(computeBytes):
        # If the data path is relative, we need to know the resource file path
        if(resourceFilePath != None):
            resource.bytes = os.path.getsize(os.path.join(os.path.dirname(resourceFilePath), dataFilePath))
        else:
            try:
                if(not unlocatedDataWarningIssued):
                    logger.warning("Data path is specified relative to resource file, however no resource file path was specified. Assuming data path is relative to current working directory.")
                resource.hash = morpc.md5(dataFilePath)
            except:
                logger.error("Unable to compute file size (bytes).  Data file could not be located.")
                raise RuntimeError

    if(writeResource):
        if(resourceFilePath != None):
            logger.info("Writing Frictionless Resource file to {}".format(resourceFilePath))
            write_resource(resource, resourceFilePath)
        else:
            logger.error("Unable to validate resource.  No resource file path specified.")
            raise RuntimeError            

    if(validate == True):
        if(resourceFilePath != None):
            logger.info("Validating resource on disk.")
            validate_resource(resourceFilePath)
        else:
            logger.error("Unable to validate resource.  No resource file path specified.")
            raise RuntimeError            
        
    return resource

    

def write_resource(resource, resourcePath):
    """Given a Frictionless resource object and a path to a target file, this function writes the resource to disk in YAML
    format. It is a wrapper for frictionless.Resource.to_yaml() that is necessary when the paths to the data and/or schema
    files are specified as relative paths. 

    Parameters
    ----------
    resource : frictionless.resources.table.TableResource
        A Frictionless TableResource object which describes the data
    resourcePath : str
        The path to the Frictionless Resource file that describes the data.
    """

    import os
    cwd = os.getcwd()

    try:
        os.chdir(os.path.dirname(resourcePath))
        resource.to_yaml(os.path.basename(resourcePath))
    except Exception as e:
        os.chdir(cwd)
        logger.error("An unhandled error occurred while trying to write the Frictionless resource: {}".format(e))
        raise RuntimeError
        
    os.chdir(cwd)

def validate_resource(resourcePath):
    import os
    import frictionless
    cwd = os.getcwd()

    try:
        os.chdir(os.path.dirname(resourcePath))    
      
        logger.info("Validating resource on disk including data and schema (if applicable). This may take some time.")
        resourceOnDisk = frictionless.Resource(os.path.basename(resourcePath))
        results = resourceOnDisk.validate()

    except Exception as e:
        os.chdir(cwd)
        logger.error("An unhandled error occurred while trying to validate the Frictionless resource: {}".format(e))
        raise RuntimeError
        
    os.chdir(cwd)
    
    if(results.valid == True):
        logger.info("Resource is valid")
        return True
    else:
        logger.error(f"Resource is NOT valid. Errors follow. {results}")
        return False

def load_data(resourcePath, archiveDir=None, validate=False, forceInteger=False, forceInt64=False, useSchema="default", sheetName=None, layerName=None, driverName=None, verbose=True):
    """Often we want to make a copy of some input data and work with the copy, for example to protect 
    the original data or to create an archival copy of it so that we can replicate the process later.  
    The `load_data()` function simplifies the process of reading the data and 
    (optionally) validating the data and/or making an archival copy. 

    Parameters
    ----------
    resourcePath : str
        The path to the Frictionless Resource file that describes the data.
    archiveDir : str
        Optional. The path to the directory where a copy of a data should be archived.  If this is specified, 
        the Resource file, schema file, and data file will be archived in this location.
    validate : bool
        Optional. If True, the resource file, schema file, and data file will be validated.  If archiveDir is
        specified, the copies of the files will be validated.  If not, the original files will be validated.
        Defaults to False.
    forceInteger : bool
        Optional. If True, then try harder to cast integer fields.  This may involve rounding the values to the ones places.
        Defaults to False.
    forceInt64 : bool
        Optional. If True, then cast all integer fields as Int64 regardless of whether this is necessary.  This is useful
        when trying to merge dataframes which would otherwise have mixed int32 and Int64 fields. Defaults to False.
    useSchema : str
        Optional. If "default", use the schema specified in the resource file.  If any other string, treat that string as a path
        to a Frictionless schema file in YAML format.  If None, do not attempt to load the schema.  Note that Frictionless does
        have an option to ignore the schema specified in the resource file, so if one is specified there it will be included during validation 
        if validate == True
    sheetName : str
        The name of the desired sheet in an Excel file.  Required when reading an Excel workbook that contains multiple sheets.        
    layerName : str
        The name of the desired layer in the spatial data file. Required when reading as spatial data file that contains multiple layers, such
        as a GeoPackage.
    driverName : str
        The driver to use to load spatial data. Typically the driver can be inferred from the file extension, but must be specified
        in some situations including when the data is zipped. See morpc.load_spatial_data for more details.
    verbose : bool
        Optional.  If False, then most output will be suppressed.  Defaults to True.

    Returns
    -------
    data : pandas.core.frame.DataFrame or geopandas.geodataframe.GeoDataFrame
        A pandas DataFrame or geopandas GeoDataframe constructed from the data at the location specified by sourcePath and layerName
    resource : frictionless.resources.table.TableResource
        A Frictionless TableResource object which describes the data
    schema : frictionless.schema.schema.Schema
        A Frictionless Schema object which describes the data
    """

    import morpc
    import frictionless
    import pandas as pd
    import geopandas as gpd
    import os
    import json
    import shutil

    myResourcePath = os.path.normpath(resourcePath)

    logger.info("Loading Frictionless Resource file at location {}".format(myResourcePath))    
    
    resource = load_resource(myResourcePath)
    
    sourceDir = os.path.dirname(myResourcePath)
    resourceFilename = os.path.basename(myResourcePath)
    dataFileExtension = os.path.splitext(resource.path)[1]
    
    # Surely there is a more convenient way to get the schema path from the Resource object?
    if(useSchema == None):
        logger.info("Ignoring schema as directed by useSchema parameter.")
        schemaFilename = None
        schemaSourcePath = None
        schema = None
    elif(useSchema == "default"):
        logger.info("Using schema path specified in resource file.")
        try:
            schemaFilename = json.loads(resource.to_json())["schema"]
        except:
            logger.error("Schema path not present in resource file. Specify the schema path in useSchema or set useSchema=None to ignore schema.")

        schemaSourcePath = os.path.join(sourceDir, schemaFilename)
        schema = resource.schema
    else:
        logger.info("Using schema path specified in useSchema parameter: {}".format(useSchema))
        schemaFilename = os.path.basename(useSchema)
        schemaSourcePath = useSchema
        schema = morpc.frictionless.load_schema(useSchema)
    
    if(archiveDir != None):

        targetResource = os.path.join(archiveDir, resourceFilename)
        targetData = os.path.join(archiveDir, resource.path)
        if(schemaFilename != None):
            targetSchema = os.path.join(archiveDir, schemaFilename)
        else:
            targetSchema = None

        try:
            logger.info("Copying data, resource file, and schema (if applicable) to directory {}".format(archiveDir))    

            shutil.copyfile(os.path.join(sourceDir, resourceFilename), targetResource)
            shutil.copyfile(os.path.join(sourceDir, resource.path), targetData)
            if(targetSchema != None):
                shutil.copyfile(schemaSourcePath, targetSchema)
        except Exception as e:
            logger.error("Unhandled exception when trying to copy data and associated Frictionless files: {}".format(e))
            raise RuntimeError
    
    else:           
        targetResource = os.path.join(sourceDir, resourceFilename)
        targetData = os.path.join(sourceDir, resource.path)
        if(schemaFilename != None):
            targetSchema = schemaSourcePath
        else:
            targetSchema = None

        logger.info("Loading data, resource file, and schema (if applicable) from their source locations")    

    logger.info("--> Data file: {}".format(targetData))    
    logger.info("--> Resource file: {}".format(targetResource))   
    if(targetSchema == None):
        logger.info("--> Schema file: Not available. Ignoring schema.")
    else:
        logger.info("--> Schema file: {}".format(targetSchema))
    
    if(validate):
        logger.info("Validating resource including data and schema (if applicable).")    
        resourceValid = validate_resource(targetResource)
        if(not resourceValid):
            logger.error("Validation failed. Errors should be described above.")    
            raise RuntimeError
      
    logger.info("Loading data.")          
    if(dataFileExtension == ".csv"):
        data = pd.read_csv(targetData, dtype="str")
    elif(dataFileExtension == ".xlsx"):
        data = pd.read_excel(targetData, sheet_name=sheetName)
    elif(dataFileExtension in [".gpkg",".shp",".geojson",".gdb"]):
        data = morpc.load_spatial_data(targetData, layerName=layerName, driverName=driverName, verbose=verbose)
    else:
        logger.error("Unknown data file extension: {}".format(dataFileExtension))
        raise RuntimeError

    if(useSchema == None):
        logger.info("Skipping casting of field types since we are ignoring schema.")
    else:
        data = cast_field_types(data, schema, forceInteger=forceInteger, forceInt64=forceInt64, verbose=verbose)
    
    return data, resource, schema


def schema_from_avro(path):
    """
    Given the path to a schema document in Avro format, load the Avro schema and reformat it as a
    Frictionless Schema object in memory
    WARNING: This function has not been extensively tested.  Be sure to validate the resulting
    Frictionless schema
    """
    import frictionless
    import os
    import morpc
    
    fieldList = []
    avroSchema = morpc.load_avro_schema(os.path.normpath(path))
    for field in avroSchema["fields"]:
        thisField = {}
        for key in field:
            if key == "name":
                thisField["name"] = field[key]
            elif key == "type":
                if field[key] == "int":
                    thisField["type"] = "integer"
                elif field[key] == "float":
                    thisField["type"] = "number"
                else:
                    thisField["type"] = field[key]
            elif key == "doc":
                thisField["description"] = field[key]
        fieldList.append(thisField)

    frictionlessSchemaDescriptor = {
        "fields": fieldList
    }

    results = frictionless.Schema.validate_descriptor(frictionlessSchemaDescriptor)
    if(results.valid == True):
        print("Schema is valid")
    else:
        print("ERROR: Schema is NOT valid. Errors follow.")
        print(results)
        raise RuntimeError
        
    frictionlessSchema = frictionless.Schema.from_descriptor(frictionlessSchemaDescriptor)
    
    return frictionlessSchema

# TODO: reinclude the geojson specific functions

# TODO: reinclude the ArcGIS functions
