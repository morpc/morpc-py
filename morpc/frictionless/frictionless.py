"""
Functions for manipulating schemas in Frictionless TableSchema format
Reference: https://specs.frictionlessdata.io/table-schema/
"""

import logging
from math import e
from os import chdir, PathLike, getcwd
from typing import Literal, List
import datetime
from frictionless import Resource, Schema
import frictionless
from pandas import NaT
import pandas
from semantic_version import Version
import contextlib
import dateutil


logger = logging.getLogger(__name__)

@contextlib.contextmanager
def tempWorkingDirectory(dir):
    cwd = getcwd()
    chdir(dir)
    try:
        yield
    finally:
        chdir(cwd)


def load_schema(path: str | PathLike) -> frictionless.Schema:
    """Given the path to a Frictionless schema file in JSON or YAML format, load the file into memory as a Frictionless Schema object.
    Parameters:
    -----------
    path : path
        Path to the schema file
    """
    import frictionless
    logger.debug(f"Loading schema from {path}")
    return frictionless.Schema(path)


def load_resource(path: str | PathLike) -> frictionless.Resource:
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


def get_field_names(schema: frictionless.Schema) -> list[str]:
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


def name_to_dtype_map(schema: frictionless.Schema) -> dict:
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


def name_to_desc_map(schema: frictionless.Schema) -> dict:
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

  
def cast_field_types(df, schema, forceInteger:bool=False, forceInt64:bool=False, forceNumber:bool=False, forceDateTime:Literal['coerce','error']='coerce', nullBoolValue=False, handleMissingFields="error", handleMissingValues=True, logLevel=None):
    """
    Given a dataframe and the Frictionless Schema object (see load_schema), recast each of the fields in the 
    dataframe to the data type specified in the schema.

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
    
    forceNumber : bool
        Optional. If True, then coerce columns that are converted to "number" using pd.to_numeric(errors='coerce').
        
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
        
    logLevel : str or int as defined by logging package. See https://docs.python.org/3/library/logging.html#levels
        Optional. Temporarily override the default log level with the specified log level. Typically you would specify "WARNING" to suppress less critical 
        output when the function is called iteratively many times. 

    Returns:
    -------
    outDF : pandas.Dataframe
        A copy of the input dataframe with the field types cast according to the schema.

    """
    import morpc
    import frictionless
    import pandas as pd
    import shapely
    import json
    import numpy as np
    import re
    import math
    outDF = df.copy()

    # If the user has specified an override for the logging level, tell the logger to use that level.
    # Preserve the original log level so we can restore it later.
    originalLogLevel = None
    if logLevel != None:
        originalLogLevel = logger.level
        logger.setLevel(logLevel)

    if handleMissingValues:
        logger.info(f"handleMissingValues set to True, converting {schema.missing_values} to np.nan")
        for nullValue in schema.missing_values:
            outDF = outDF.replace(nullValue, None)

    for field in schema.fields:
        fieldName = field.name
        fieldType = field.type 
        if(not fieldName in df.columns):
            if(handleMissingFields == "ignore"):
                logger.info("Skipping field {} which is not present in dataframe".format(fieldName))
                continue
            elif(handleMissingFields == "add"):
                logger.info("Adding field {} which is not present in dataframe".format(fieldName))
                add_missing_fields(df, schema, fieldNames=fieldName)
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
                        outDF[fieldName] = pd.to_numeric(outDF[fieldName], errors='coerce').round(0).astype("Int64")
                    else:
                        # If the user has not allow coercion of the values to integers, then throw an error.
                        logger.error("Unable to coerce value to Int64 type.  Ensure that fractional part of values is zero, or set forceInteger=True")
                        raise RuntimeError   
        # If number convert to float          
        elif(fieldType == "number"):
            try:
                outDF[fieldName] = outDF[fieldName].astype("float")
            except Exception as e:
                # If conversion fails either force the conversion 
                if forceNumber == True:
                    logger.debug(f"forceNumber is set to True, Coercing {fieldName} to numeric.")
                    outDF[fieldName] = pd.to_numeric(outDF[fieldName], errors='coerce').astype("float")
                # Or error.
                else:
                    logger.error(f"Unable to set {fieldName} to number. Set forceNumber as True to coerce. {e}")
                    raise ValueError
        # If date or datetime convert to datetime
        elif(fieldType == "date" or fieldType == "datetime"):
            try:
                # outDF[fieldName] = outDF[fieldName].astype('datetime64[ms]')
                outDF[fieldName] = [morpc.utils.datetime_from_string(x, errors=forceDateTime) for x in outDF[fieldName]]
                # outDF[fieldName] = pd.to_datetime(outDF[fieldName], errors='coerce')
            except Exception as e:
                logger.error(f"Unable to parse date. {e}")
                raise ValueError

        elif(fieldType == "year"):
            outDF[fieldName] = [pd.to_datetime(x, format='%Y').year if re.match(r'[0-9]{4}',str(x)) else None for x in outDF[fieldName]]

        elif(fieldType == "geojson"):
            if not str(outDF[fieldName].dtype) == 'geometry':
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
            
        elif(fieldType == 'any'):
            logger.info(f"Field {fieldName} as type 'any' in schema. This may be due to the schema being produced automatically frictionless.Schema.describe(). Converting to string. ")
            outDF[fieldName] = outDF[fieldName].astype('string')
        else:
            outDF[fieldName] = outDF[fieldName].astype(fieldType)

    # Restore the original log level, if necessary
    if(originalLogLevel != None):
        logger.setLevel(originalLogLevel)
            
    return outDF

# Given a dataframe and the Frictionless Schema object (see load_schema), add any fields in the schema that
# are missing in the dataframe.  If fieldNames == None, any fields missing from the schema will be added to the dataframe
# with the correct type and null values.  If fieldNames is a string or list of strings, only those fields will be added.
def add_missing_fields(df: pandas.DataFrame, schema: frictionless.Schema, fieldNames:List[str]|None=None):
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
            logger.info("Adding missing field {0}, type {1}, filled with null values.".format(fieldName, fieldType))
            outDF[fieldName] = None
                        
            if((fieldType == "int") or (fieldType == "integer")):
                logger.warning("Field {0} specified as type {1} (pandas type 'int'), which does not support null values in pandas. Casting field as pandas type 'Int64' instead.".format(fieldName, fieldType))
                outDF[fieldName] = outDF[fieldName].astype("Int64")
            elif(fieldType == "number"):
                outDF[fieldName] = outDF[fieldName].astype("float")
            else:
                outDF[fieldName] = outDF[fieldName].astype(fieldType)
        else:
            # If the field is not missing, skip it
            logger.warning("User-specified field {0} is already present in the dataframe. Skipping it.".format(fieldName))
            continue

    return outDF
        
def convert_lineend(path: str | PathLike, target: Literal['dos', 'unix']) -> None:
    import re
    import os

    if not os.path.exists(path):
        logger.error(f"{path} does not exist")
        raise FileExistsError

    logger.info(f"Converting {path} to {target} line ends")
    with open(path, 'rb') as f:
        line = f.readline()
    if line.endswith(b'\r\n'):
        current = 'dos'
    else:
        current = 'unix'

    logger.debug(f"current line ends {current}")
    if current == target:
        pass
    else:
        if target == 'unix':
            try:
                with open(path, 'rb') as file:
                    content = file.read()
                content = content.replace(b'\r\n', b'\n')  
                with open(path, 'wb') as file:
                    file.write(content)      
            except Exception as e:
                logger.error(f"Error changing line endings: {e}") 
                raise RuntimeError

        if target == 'dos':
            try:
                with open(path, 'rb') as file:
                    content = file.read()
                content = re.sub(b'(?<!\r)\n', b'\r\n', content)  
                with open(path, 'wb') as file:
                    file.write(content)    
            except Exception as e:
                logger.error(f"Error changing line endings: {e}") 
                raise RuntimeError

def _is_url(path):
    """Return True if a resource path is a URL rather than a local path."""
    return str(path).startswith(("http://", "https://"))


def _compute_hash(path, algorithm='md5'):
    """Compute the hash of a file in the form that is emitted in a resource descriptor.

    md5 is emitted as a bare hex digest, which is the Data Package v1 form and what MORPC resources have
    always carried. sha256 is emitted in the self-describing v2 form "sha256:<hex>".
    """
    import morpc

    if(algorithm == 'md5'):
        return morpc.md5(path)
    elif(algorithm == 'sha256'):
        return "sha256:{}".format(morpc.sha256(path))
    else:
        logger.error("Unsupported hash algorithm: {}. Use 'md5' or 'sha256'.".format(algorithm))
        raise RuntimeError


def _verify_hash(path, expected):
    """Raise if the file at path does not match the hash recorded in a resource descriptor.

    Accepts both the bare hex digest that MORPC resources have historically carried, which is assumed to
    be md5, and the self-describing "<algorithm>:<hex>" form.
    """
    import morpc

    if(expected == None):
        logger.warning("Resource carries no hash, so the integrity of {} cannot be verified.".format(path))
        return

    if(":" in expected):
        (algorithm, _, digest) = expected.partition(":")
        algorithm = algorithm.lower()
    else:
        (algorithm, digest) = ('md5', expected)

    if(algorithm == 'md5'):
        actual = morpc.md5(path)
    elif(algorithm == 'sha256'):
        actual = morpc.sha256(path)
    else:
        logger.error("Resource hash uses unsupported algorithm '{}'. Unable to verify {}.".format(algorithm, path))
        raise RuntimeError

    if(actual != digest):
        logger.error("Hash mismatch for {}. The resource records {} but the file computes {}. The data does not match the resource that describes it.".format(path, digest, actual))
        raise RuntimeError

    logger.info("Verified {} against the {} hash recorded in the resource.".format(path, algorithm))


def create_resource(dataPath, title=None, name=None, description=None, sources=None, resourcePath=None, schemaPath=None, resFormat=None,
                                 resProfile=None, resMediaType=None, computeHash=True, computeBytes=True, ignoreSchema=False, 
                                 writeResource=False, validate=False, control=None, lineEnds: Literal['dos', 'unix'] = 'dos',
                                 cache=None, hashAlgorithm: Literal['md5', 'sha256'] = 'md5'):
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
    control : frictionless.formats.Control
        Optional. For formats that are not standard tables, add a control from frictionless.formats
    lineEnds : ['\r\n', '\n']
        Convert all line endings in text files to DOS or UNIX stile endings. Defaults to '\r\n', DOS endings.
    cache : str
        Optional. The path to the local working copy of the data, RELATIVE TO THE LOCATION OF THE RESOURCE FILE.  Emitted in
        the resource as the custom "_cache" property.  Specify this when dataPath is a URL, such as a GitHub release asset:
        the authoritative copy lives at the URL, but the hash and size must be computed from the local file, and consumers
        who already have the file on disk can read it without downloading.  See morpc.frictionless.publish_paths().
    hashAlgorithm : ['md5', 'sha256']
        Optional. The algorithm used to compute the hash attribute.  Defaults to 'md5', which is emitted as a bare hex digest
        for backward compatibility (Data Package v1 style).  'sha256' is emitted in the self-describing Data Package v2 form
        "sha256:<hex>".

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
        },
        ".sqlite": {
            "format": "sqlite",
            "mediatype": "application/vnd.sqlite3"
        },
        ".zip": {
            "format": "zip",
            "mediatype": "application/zip"
        }
    }

    # A URL must not be passed through normpath, which would collapse the "//" in the scheme.
    if _is_url(dataPath):
        dataFilePath = dataPath
    else:
        dataFilePath = os.path.normpath(dataPath)
    dataFileName = os.path.splitext(os.path.basename(dataFilePath))[0]
    dataFileExtension = os.path.splitext(os.path.basename(dataFilePath))[1]

    if(not _is_url(dataFilePath) and os.path.basename(dataFilePath) != os.path.normpath(dataFilePath)):
        # If dataFilePath is not simply a filename
        logger.warning("You seem to have specified a data path that is not simply a file name.  This implies that the data is located in a different directory than the resource file.  Typically the data is located in the same directory as the resource file and the path is simply the filename.")

    resourceFilePath = None
    if(resourcePath != None):
        if(not writeResource):
            # Warn the user if they specified a resource file location but did not enable writeResource
            logger.warning("You specified a path for the resource file, however writeResource is not set to True. Resource file will not be written to disk.")   

        # If the user has specified a path to the resource file, we'll use it without modification. Warn the user if the choice is unusual.
        if(not _is_url(dataFilePath) and os.path.basename(dataFilePath) != os.path.normpath(dataFilePath)):
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
            if(not _is_url(dataFilePath) and os.path.basename(dataFilePath) != os.path.normpath(dataFilePath)):
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

    resourceDescriptor = {
        "name": resourceName,
        "title": resourceTitle,
        "description": resourceDescription,
        "profile": resourceProfile,
        "path": dataFilePath,
        "format": resourceFormat,
        "mediatype": resourceMediaType,
    }
    # Frictionless has no built-in parser for GeoPackage, so morpc.frictionless.gpkg registers a
    # "gpkg" resource type. That registration is only picked up if "type" is set explicitly here --
    # otherwise Frictionless falls back to its generic FileResource, which GpkgResource.validate()
    # is needed to avoid.
    if resourceFormat == "gpkg":
        resourceDescriptor["type"] = "gpkg"

    resource = frictionless.Resource.from_descriptor(resourceDescriptor)

    if control != None:
        resource = frictionless.Resource(resource.to_dict(), control=control)

    if(not ignoreSchema):
        resource.schema = schemaFilePath

    if(cache != None):
        resource.custom["_cache"] = cache

    # The hash and size describe the bytes of the data.  When the path is a URL those bytes are not locally
    # addressable, so resolve them from the cache, which is the local working copy of the same data.
    if(cache != None):
        localDataPath = cache
    else:
        localDataPath = dataFilePath

    if(resourceFilePath != None):
        localDataPath = os.path.join(os.path.dirname(resourceFilePath), localDataPath)
    elif(computeHash or computeBytes):
        logger.warning("Data path is specified relative to resource file, however no resource file path was specified. Assuming data path is relative to current working directory.")

    if(dataFileExtension == ".csv" and not _is_url(dataFilePath)):
        if os.linesep == '\n':
            logger.info(f'Changing line endings.')
            if resourceFilePath == None:
                logger.error(f"Unable to find resource as {resourceFilePath}")
                raise RuntimeError
            else:
                convert_lineend(localDataPath, lineEnds)

    if((computeHash or computeBytes) and _is_url(localDataPath)):
        logger.error("Unable to compute hash or file size because the data path is a URL. Specify cache to point at the local working copy of the data.")
        raise RuntimeError

    if(computeHash):
        try:
            resource.hash = _compute_hash(localDataPath, hashAlgorithm)
        except FileNotFoundError:
            logger.error("Unable to compute hash.  Data file could not be located at {}.".format(localDataPath))
            raise RuntimeError

    if(computeBytes):
        try:
            resource.bytes = os.path.getsize(localDataPath)
        except FileNotFoundError:
            logger.error("Unable to compute file size (bytes).  Data file could not be located at {}.".format(localDataPath))
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
        os.chdir(os.path.dirname(os.path.abspath(resourcePath)))
        resource.to_yaml(os.path.basename(resourcePath))
    except Exception as e:
        os.chdir(cwd)
        logger.error("An unhandled error occurred while trying to write the Frictionless resource: {}".format(e))
        raise RuntimeError
        
    os.chdir(cwd)

def validate_resource(resourcePath):
    import os
    import frictionless

    with tempWorkingDirectory(os.path.dirname(os.path.abspath(resourcePath))):
        try:
        
            logger.info("Validating resource on disk including data and schema (if applicable). This may take some time.")
            resourceOnDisk = frictionless.Resource(os.path.basename(resourcePath))

            results = resourceOnDisk.validate()

        except Exception as e:
            logger.error("An unhandled error occurred while trying to validate the Frictionless resource: {}".format(e))
            raise RuntimeError
        
    
    if(results.valid == True):
        logger.info("Resource is valid")
        return True
    else:
        logger.error(f"Resource is NOT valid. Errors follow. {results}")
        return False

def _detect_sqlite_geometry_column(con, tableName):
    """Return the name of the geometry column in a SQLite table, or None if there is none.

    Spatial SQLite tables produced for MORPC workflows store geometry as raw WKB in a BLOB column with no
    accompanying metadata to distinguish it from an ordinary BLOB. We identify the geometry column by sampling
    each column's first non-null value and checking whether it parses as WKB.
    """
    import pandas as pd
    import shapely.wkb

    columns = pd.read_sql_query('SELECT * FROM "{}" LIMIT 0'.format(tableName), con).columns
    cursor = con.cursor()
    for column in columns:
        row = cursor.execute('SELECT "{}" FROM "{}" WHERE "{}" IS NOT NULL LIMIT 1'.format(column, tableName, column)).fetchone()
        if(row == None):
            continue
        value = row[0]
        if(not isinstance(value, (bytes, bytearray))):
            continue
        try:
            shapely.wkb.loads(bytes(value))
            return column
        except Exception:
            continue
    return None


def resolve_data_path(resource, sourceDir, download=True):
    """Return the path to the local data file described by a resource, downloading it if necessary.

    A resource may describe its data in two places. The path attribute is authoritative and may be a URL,
    typically a GitHub release asset. The custom _cache attribute, when present, names the local working
    copy relative to the resource file. This function resolves the two to a single local path:

      1. If _cache is present and that file exists, use it.
      2. Otherwise, if path is a URL and download is True, download it to the _cache location, or to a
         temporary directory if no cache is specified.
      3. Otherwise, join path to sourceDir, which is the behavior for an ordinary local resource.

    In cases 1 and 2 the file is verified against the hash recorded in the resource. A mismatch raises
    rather than warns, because a descriptor that disagrees with its own data cannot be reasoned about.

    Parameters
    ----------
    resource : frictionless.Resource
        The resource that describes the data.
    sourceDir : str
        The directory containing the resource file. Both path and _cache are interpreted relative to it.
    download : bool
        Optional. If False, a URL path raises rather than being downloaded. Defaults to True.

    Returns
    -------
    str
        The path to the local data file.
    """
    import os
    import shutil
    import tempfile
    import morpc.req

    cache = resource.custom.get("_cache") if resource.custom else None

    if(cache != None):
        cachePath = os.path.join(sourceDir, cache)
        if(os.path.exists(cachePath)):
            logger.info("Using local cached copy of the data at {}".format(cachePath))
            _verify_hash(cachePath, resource.hash)
            return cachePath
        logger.info("Resource specifies a cache at {} but no file is present there.".format(cachePath))

    if(_is_url(resource.path)):
        if(not download):
            logger.error("Data path is a URL and no local cache is available, but downloading is disabled.")
            raise RuntimeError

        if(cache != None):
            targetPath = os.path.join(sourceDir, cache)
        else:
            logger.warning("Resource specifies a URL but no _cache, so the download cannot be reused. Downloading to a temporary directory.")
            targetPath = os.path.join(tempfile.mkdtemp(), os.path.basename(resource.path))

        targetDir = os.path.dirname(os.path.abspath(targetPath))
        os.makedirs(targetDir, exist_ok=True)

        logger.info("Downloading data from {} to {}".format(resource.path, targetPath))
        downloadedPath = morpc.req.get_file_safely(resource.path, targetDir, returnPath=True)

        # get_file_safely names the downloaded file after the URL. If the cache calls it something else, move it.
        if(os.path.abspath(downloadedPath) != os.path.abspath(targetPath)):
            shutil.move(downloadedPath, targetPath)

        _verify_hash(targetPath, resource.hash)
        return targetPath

    return os.path.join(sourceDir, resource.path)


def load_data(resourcePath, archiveDir=None, validate=False, forceInteger=False, forceInt64=False, useSchema="default", sheetName=None, layerName=None, tableName=None, driverName=None, targetCRS=None, lineEnds: Literal['\n', '\b\n'] = '\b\n'):
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
    tableName : str
        The name of the desired table in a SQLite database. Required when reading a SQLite file unless the table name is specified in the
        resource's SQL control (e.g. one created by create_resource with a frictionless.formats.SqlControl).
    driverName : str
        The driver to use to load spatial data. Typically the driver can be inferred from the file extension, but must be specified
        in some situations including when the data is zipped. See morpc.load_spatial_data for more details.
    targetCRS : str
        Optional. The coordinate reference system to reproject the geometry to when loading a spatial SQLite database. Only used
        when a geometry column is detected in a SQLite file. SQLite WKB geometry carries no CRS information, so it is assumed to be
        "epsg:4326" on read. If None (the default), the data's native CRS is returned without reprojection. See morpc.load_spatial_data.
    lineEnds : ['\n', '\b\n']
        The type of line end separator to use for the data. If does not match, try to convert. Defaults to '\b\n'

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

    # Resolve the resource's path and _cache to a single local file, downloading it if the path is a
    # release asset URL and no local copy is present. The extension must come from the resolved local
    # file rather than from resource.path, which may be a URL.
    sourceDataPath = resolve_data_path(resource, sourceDir)
    dataFileExtension = os.path.splitext(sourceDataPath)[1]
    
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
        targetData = os.path.join(archiveDir, os.path.basename(sourceDataPath))
        if(schemaFilename != None):
            targetSchema = os.path.join(archiveDir, schemaFilename)
        else:
            targetSchema = None

        try:
            logger.info("Copying data, resource file, and schema (if applicable) to directory {}".format(archiveDir))    

            shutil.copyfile(os.path.join(sourceDir, resourceFilename), targetResource)
            shutil.copyfile(sourceDataPath, targetData)
            if(targetSchema != None):
                shutil.copyfile(schemaSourcePath, targetSchema)
        except Exception as e:
            logger.error("Unhandled exception when trying to copy data and associated Frictionless files: {}".format(e))
            raise RuntimeError
    
    else:           
        targetResource = os.path.join(sourceDir, resourceFilename)
        targetData = sourceDataPath
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
    elif(dataFileExtension == ".gpkg"):
        if(layerName == None):
            # Fall back to the layer name stored in the resource's gpkg control, if present.
            gpkgControl = resource.dialect.get_control("gpkg") if resource.dialect.has_control("gpkg") else None
            if(gpkgControl != None and gpkgControl.layer != None):
                layerName = gpkgControl.layer
                logger.info("Layer name not specified. Using layer name from resource gpkg control: {}".format(layerName))
        data = morpc.load_spatial_data(targetData, layerName=layerName, driverName=driverName)
    elif(dataFileExtension in [".shp",".geojson",".gdb"]):
        data = morpc.load_spatial_data(targetData, layerName=layerName, driverName=driverName)
    elif(dataFileExtension == ".sqlite"):
        import sqlite3
        if(tableName == None):
            # Fall back to the table name stored in the resource's SQL control, if present.
            sqlControl = resource.dialect.get_control("sql") if resource.dialect.has_control("sql") else None
            if(sqlControl != None and sqlControl.table != None):
                tableName = sqlControl.table
                logger.info("Table name not specified. Using table name from resource SQL control: {}".format(tableName))
            else:
                logger.error("No table name available. Specify tableName or include a SQL control with a table name in the resource.")
                raise RuntimeError
        con = sqlite3.connect(targetData)
        try:
            # A spatial SQLite database stores geometry as raw WKB in a BLOB column with no metadata to
            # distinguish it. Detect such a column by parsing a sample value as WKB. If one is found, defer
            # to morpc.load_spatial_data() which reads the table as a GeoDataFrame.
            geometryColumn = _detect_sqlite_geometry_column(con, tableName)
        finally:
            con.close()

        if(geometryColumn != None):
            logger.info("Detected geometry column '{}' in SQLite table '{}'. Loading as spatial data.".format(geometryColumn, tableName))
            data = morpc.load_spatial_data(targetData, layerName=tableName, driverName="SQLite", geometryColumn=geometryColumn, targetCRS=targetCRS)
        else:
            con = sqlite3.connect(targetData)
            try:
                data = pd.read_sql_query('SELECT * FROM "{}"'.format(tableName), con)
            finally:
                con.close()

        # SQLite stores column names in lowercase while Frictionless schemas often use camelCase. Now that
        # the data is loaded (whether as a tabular DataFrame or a spatial GeoDataFrame), select only the
        # fields described by the schema (matching column names case-insensitively) and restore each column
        # to the casing used in the schema. For spatial data, the geometry column is retained and renamed
        # to "geometry".
        if(schema != None):
            lowerToActual = {column.lower(): column for column in data.columns}
            renameMap = {}
            for field in schema.fields:
                actualColumn = lowerToActual.get(field.name.lower())
                if(actualColumn == None):
                    logger.error("Schema field '{}' not found in SQLite table '{}'.".format(field.name, tableName))
                    raise RuntimeError
                renameMap[actualColumn] = field.name
            keepColumns = list(renameMap.keys())
            if(geometryColumn != None):
                renameMap[geometryColumn] = "geometry"
                keepColumns.append(geometryColumn)
            data = data[keepColumns].rename(columns=renameMap)
            if(geometryColumn != None):
                data = data.set_geometry("geometry")
    else:
        logger.error("Unknown data file extension: {}".format(dataFileExtension))
        raise RuntimeError

    if(useSchema == None):
        logger.info("Skipping casting of field types since we are ignoring schema.")
    else:
        data = cast_field_types(data, schema, forceInteger=forceInteger, forceInt64=forceInt64)

    return data, resource, schema


def load_package(packagePath, resources=None, archiveDir=None, validate=False, **kwargs):
    """Load selected resources from a Frictionless data package, e.g. one GitHub release bundling
    several GeoPackage layers as separate resources.

    Requires the package descriptor's resources to be inline objects, which is what create_package()
    writes as of the fix in #180 -- a package written by an older create_package() (bare filename
    strings) is not loadable through frictionless.Package() at all and needs to be re-cut before this
    will work against it.

    Each selected resource is written out as a standalone .resource.yaml in archiveDir and then loaded
    through load_data(), rather than duplicating load_data()'s format-dispatch logic here. Pointing
    every resource at the same archiveDir is what makes this efficient for the common case where every
    resource in the package shares one underlying data file (e.g. one GeoPackage's several layers):
    load_data()'s own resolve_data_path() cache-hit check means the file is downloaded once, for the
    first resource, and reused by every later one -- not re-fetched per resource.

    Parameters
    ----------
    packagePath : str
        Local path or URL to a *.package.yaml.
    resources : str or list of str, optional
        Name(s) of the resources to load, matched against each resource's `name` field. Defaults to
        every resource in the package. Raises if a named resource isn't found.
    archiveDir : str, optional
        Directory each resource's underlying data is resolved/cached into (see above). Required when
        packagePath is a URL, since there is then no directory implied by the package's own location.
        Defaults to packagePath's own directory when packagePath is local.
    validate : bool
        Passed through to load_data() for every selected resource.
    **kwargs
        Passed through to load_data() for every selected resource (forceInteger, useSchema, layerName,
        etc.), applied identically to all of them.

    Returns
    -------
    dict
        Resource name -> (data, resource, schema), the same triple load_data() returns for one
        resource, one entry per selected resource.
    """
    import os
    import shutil
    import frictionless

    if archiveDir is None:
        if _is_url(packagePath):
            logger.error("archiveDir is required when packagePath is a URL, so every resource's "
                         "underlying data is cached to the same location instead of each downloading "
                         "to its own temporary directory.")
            raise RuntimeError
        archiveDir = os.path.dirname(os.path.abspath(packagePath))
    os.makedirs(archiveDir, exist_ok=True)

    packageDir = None if _is_url(packagePath) else os.path.dirname(os.path.abspath(packagePath))

    logger.info(f"Loading Frictionless Package at {packagePath}")
    package = frictionless.Package(packagePath)

    if isinstance(resources, str):
        resources = [resources]
    selected = package.resources if resources is None else [
        r for r in package.resources if r.name in resources
    ]
    if resources is not None:
        missing = set(resources) - {r.name for r in selected}
        if missing:
            logger.error(f"Resource(s) not found in package: {', '.join(sorted(missing))}. "
                         f"Available: {', '.join(r.name for r in package.resources)}")
            raise RuntimeError

    results = {}
    for resource in selected:
        # A loaded Resource retains its schema's original path for lossless round-tripping (the same
        # issue #180 fixed for a Package's resources list), so writing it out as-is would emit a bare
        # "schema: whatever.schema.yaml" reference pointing at a file that doesn't exist next to it in
        # archiveDir. Write the already-resolved schema out as a real sibling file instead, so the
        # resource we write matches the plain resource.yaml + schema.yaml shape load_data() expects.
        resourceDict = resource.to_dict()
        if resource.schema is not None:
            schemaFilePath = os.path.join(archiveDir, f"{resource.name}.schema.yaml")
            resource.schema.to_yaml(schemaFilePath)
            resourceDict["schema"] = os.path.basename(schemaFilePath)
        # The resource we write lands in archiveDir, which is not necessarily the package's own
        # directory (a caller may redirect where cached data lands). A local, non-URL path is only
        # meaningful relative to where the package actually lives, and frictionless refuses to accept
        # an absolute path in a descriptor ("is not safe") so it can't just be resolved that way either
        # -- copy the data file itself into archiveDir instead, the same place a URL would be
        # downloaded to, and leave the written path as the bare filename that now resolves there.
        # Skipped once the file is already present, so this is a one-time cost when archiveDir differs
        # from the package's own directory, not a copy per resource that shares the same file.
        if packageDir is not None and not _is_url(resourceDict.get("path", "")):
            sourceDataPath = os.path.join(packageDir, resourceDict["path"])
            targetDataPath = os.path.join(archiveDir, os.path.basename(resourceDict["path"]))
            if os.path.abspath(sourceDataPath) != os.path.abspath(targetDataPath) and not os.path.exists(targetDataPath):
                shutil.copyfile(sourceDataPath, targetDataPath)
            resourceDict["path"] = os.path.basename(resourceDict["path"])
        inlineResource = frictionless.Resource(resourceDict)
        resourceFilePath = os.path.join(archiveDir, f"{resource.name}.resource.yaml")
        write_resource(inlineResource, resourceFilePath)
        results[resource.name] = load_data(resourceFilePath, archiveDir=None, validate=validate, **kwargs)

    return results


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

def create_package(dir: PathLike, resources: List[str], name: str, version: str | Version, keywords: List[str] | None = None):
    """
    Create a data package from a list of resources
    """
    import os
    import frictionless

    if isinstance(version, str):
        try:
            version = Version(version)
        except ValueError as e:
            logger.error(f"Version is not valid: {e}")

    with tempWorkingDirectory(dir):
        # Resource.to_dict() is rebuilt into a fresh Resource rather than used directly: a Resource
        # loaded from a descriptor path retains that path for lossless round-tripping, so passing it
        # straight into Package() would serialize it back out as a bare filename string instead of an
        # inline descriptor. That collapsed form fails to reload (Frictionless requires each package
        # resource to be an object, not a string), so it must be expanded here before bundling.
        resources = [frictionless.Resource(frictionless.Resource(x).to_dict()) for x in resources]

        package = frictionless.Package(
            name=name,
            resources=resources,
            # Emitted as an ISO 8601 string rather than a datetime. Frictionless passes the value
            # through to the descriptor unchanged, and the Data Package spec requires a string here.
            created=datetime.datetime.now().isoformat(),
            version=str(version),
            keywords=keywords
        )

        package.to_yaml(f"{name}.package.yaml")

    return package


# TODO: reinclude the geojson specific functions

# TODO: reinclude the ArcGIS functions
