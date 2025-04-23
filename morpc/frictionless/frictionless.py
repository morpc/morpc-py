    
# md5() computes the MD5 checksum for a file.  When the original checksum is known, the current checksum can be compared 
# to it to determine whether the file has changed.
#
# Input parameters:
#   - fname is a string representing the path to the file for which the checksum is to be computed
#
# Returns:
#   - MD5 checksum for the file



import datetime


def md5(fname):
    """
    md5() computes the MD5 checksum for a file.  When the original checksum is known, the current checksum can be compared to it to determine whether the file has changed.

    Input parameters:
      - fname is a string representing the path to the file for which the checksum is to be computed

     Returns:
       - MD5 checksum for the file
    """
    import hashlib
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
    
# Functions for manipulating schemas in Frictionless TableSchema format
# Reference: https://specs.frictionlessdata.io/table-schema/

# Given the path to a Frictionless schema file in JSON or YAML format, load the file into memory as a Frictionless
# Schema object.
def load_schema(path):
    import frictionless
    return frictionless.Schema(path)

# Given the path to a Frictionless Resource file in JSON or YAML format, load the file into memory as a Frictionless
# Resource object.
def load_resource(path):
    import frictionless
    return frictionless.Resource(path)

# Given a Frictionless TableSchema object, return a list containing the names of the fields defined in the schema.
# NOTE: This is implemented natively using the TableSchema.field_names() method. Functional implementation is just to provide
# consistency with morpc.avro_get_field_names()
def get_field_names(schema):
    import frictionless
    return schema.field_names

# Given a Frictionless TableSchema object, return a dictionary mapping each field name to the corresponding data type
# specified in the schema.  The resulting dictionary is suitable for use by the pandas.DataFrame.astype() method (for example)
def name_to_dtype_map(schema):
    import frictionless
    return {schema.fields[i].name:schema.fields[i].type for i in range(len(schema.fields))}    

# Given a Frictionless TableSchema object, return a dictionary mapping each field name to the corresponding description
# specified in the schema.
def name_to_desc_map(schema):
    import frictionless
    return {schema.fields[i].name:schema.fields[i].description for i in range(len(schema.fields))}

# Given a dataframe and the Frictionless Schema object (see load_schema), recast each of the fields in the 
# dataframe to the data type specified in the schema.    
def cast_field_types(df, schema, forceInteger=False, handleMissingFields="error", verbose=True):
    import frictionless
    import pandas as pd
    import shapely
    import json
    outDF = df.copy()

    for field in schema.fields:
        fieldName = field.name
        fieldType = field.type 
        if(not fieldName in df.columns):
            if(handleMissingFields == "ignore"):
                print("cast_field_types | WARNING | Skipping field {} which is not present in dataframe".format(fieldName))
                continue
            elif(handleMissingFields == "add"):
                print("cast_field_types | WARNING | Adding field {} which is not present in dataframe".format(fieldName))
                add_missing_fields(df, schema, fieldNames=fieldName, verbose=verbose)
                continue
            else:
                print("cast_field_types | ERROR | Field {} is not present in dataframe. To handle missing fields, see argument handleMissingFields.".format(fieldName))
                raise RuntimeError
   
        if(verbose):
            print("cast_field_types | INFO | Casting field {} as type {}.".format(fieldName, fieldType))
        # The following section is necessary because the pandas "int" type does not support null values.  If null values are present,
        # the field must be cast as "Int64" instead.
        if((fieldType == "int") or (fieldType == "integer")):
            try:
                # Try to cast the field as an "int".  This will fail if nulls are present.
                outDF[fieldName] = outDF[fieldName].astype("int")
            except:
                try:
                    # Try to cast as "Int64", which supports nulls. This will fail if the fractional part is non-zero.
                    if(verbose):
                        print("cast_field_types | WARNING | Failed conversion of fieldname {} to type 'int'.  Trying type 'Int64' instead.".format(fieldName))
                    outDF[fieldName] = outDF[fieldName].astype("Int64")
                except:
                    if(forceInteger == True):
                        # If the user has allowed coercion of the values to integers, then round the values to the ones place prior to 
                        # converting to "Int64"
                        print("cast_field_types | WARNING | Failed conversion of fieldname {} to type 'Int64'.  Trying to round first.".format(fieldName))
                        outDF[fieldName] = outDF[fieldName].astype("float").round(0).astype("Int64")
                    else:
                        # If the user has not allow coercion of the values to integers, then throw an error.
                        print("cast_field_types | ERROR | Unable to coerce value to Int64 type.  Ensure that fractional part of values is zero, or set forceInteger=True")
                        raise RuntimeError           
        elif(fieldType == "number"):
            outDF[fieldName] = outDF[fieldName].astype("float")
        elif(fieldType == "date"):
            outDF[fieldName] = pd.to_datetime(outDF[fieldName])
        elif(fieldType == "geojson"):
            try:
                print(f"cast_field_types | INFO | Fieldname {fieldName} as geojson. Attempting to convert to geometry.")
                outDF[fieldName] = [shapely.geometry.shape(json.loads(x)) for x in outDF[fieldName]]
            except RuntimeError as r:
                print(f"cast_field_types | ERROR | Unable to convert to geometry.")
            finally:
                print(f"cast_field_types | INFO | Fieldname {fieldName} cast as geometry. {r}")
        elif(fieldType == "boolean"): 
            if(outDF[fieldName].dtype == "bool"):
                print("cast_field_types | WARNING | Fieldname {} already cast as boolean type. Skipping casting for this field.".format(fieldName))
                continue
            elif(outDF[fieldName].dtype != "string"):
                print("cast_field_types | WARNING | Standardizing fieldname {} as a string prior to conversion to boolean.".format(fieldName))
                outDF[fieldName] = outDF[fieldName].astype("string")
            
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
                print("cast_field_types | ERROR | Fieldname {0} contains values that are not recognized as true or false: {1}".format(fieldName, ", ".join(list(foundValuesSet-validValuesSet))))
                raise RuntimeError

            # Now that we are confident that all of the values are valid in string form, map them to actual boolean values
            outDF[fieldName] = outDF[fieldName].map(truthMap)

            # Finally, make the change official by changing the pandas field type to "bool".
            outDF[fieldName] = outDF[fieldName].astype("bool")
            
        else:
            outDF[fieldName] = outDF[fieldName].astype(fieldType)
            
    return outDF

# Given a dataframe and the Frictionless Schema object (see load_schema), add any fields in the schema that
# are missing in the dataframe.  If fieldNames == None, any fields missing from the schema will be added to the dataframe
# with the correct type and null values.  If fieldNames is a string or list of strings, only those fields will be added.
def add_missing_fields(df, schema, fieldNames=None, verbose=True):
    import frictionless
    outDF = df.copy()
    
    if(fieldNames == None):
        myFieldNames = schema.field_names
    elif(type(fieldNames) == str):
        myFieldNames = [fieldNames]
    elif(type(fieldNames) == list):
        myFieldNames = fieldNames
    else:
        print("add_missing_fields | ERROR | If provided, argument fieldNames must be a string containing a single field name or a list of strings")
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
            if(verbose == True):
                print("add_missing_fields | INFO | Adding missing field {0}, type {1}, filled with null values.".format(fieldName, fieldType))
            outDF[fieldName] = None
                        
            if((fieldType == "int") or (fieldType == "integer")):
                if(verbose == True):
                    print("add_missing_fields | WARNING | Field {0} specified as type {1} (pandas type 'int'), which does not support null values in pandas. Casting field as pandas type 'Int64' instead.".format(fieldName, fieldType))
                df[fieldName] = df[fieldName].astype("Int64")
            elif(fieldType == "number"):
                outDF[fieldName] = outDF[fieldName].astype("float")
            else:
                outDF[fieldName] = outDF[fieldName].astype(fieldType)
        else:
            # If the field is not missing, skip it
            print("add_missing_fields | WARNING | User-specified field {0} is already present in the dataframe. Skipping it.".format(fieldName))
            continue

    return outDF
        


def create_resource(dataPath, title=None, name=None, description=None, resourcePath=None, schemaPath=None, resFormat=None, 
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
        print("morpc.create_resource | WARNING | You seem to have specified a data path that is not simply a file name.  This implies that the data is located in a different directory than the resource file.  Typically the data is located in the same directory as the resource file and the path is simply the filename.")   

    resourceFilePath = None
    if(resourcePath != None):
        if(not writeResource):
            # Warn the user if they specified a resource file location but did not enable writeResource
            print("morpc.create_resource | WARNING | You specified a path for the resource file, however writeResource is not set to True. Resource file will not be written to disk.")   

        # If the user has specified a path to the resource file, we'll use it without modification. Warn the user if the choice is unusual.
        if(os.path.basename(dataFilePath) != os.path.normpath(dataFilePath)):
            # If dataFilePath is not simply a filename
            if(os.path.dirname(os.path.abspath(resourcePath)) != os.path.dirname(os.path.abspath(dataFilePath))):
                # If the absolute path to the resource file and the absolute path to the data put them in different directories
                print("morpc.create_resource | WARNING | You seem to have specified a path for the resource file that is in a different directory than the data.  Typically the data is located in the same directory as the resource file and the path is simply the filename.")   
        resourceFilePath = os.path.normpath(resourcePath)
        
    if resFormat != None:
        resourceFormat = resFormat
    else:
        if dataFileExtension.lower() in EXTENSION_MAP:
            resourceFormat = EXTENSION_MAP[dataFileExtension.lower()]["format"]
            print("morpc.create_resource | INFO | Format not specified. Using format derived from data file extension: {}".format(resourceFormat))
        else:
            print("morpc.create_resource | ERROR | Format not specified and could not be determined from data file extension.")
            raise RuntimeError

    if(not ignoreSchema):
        # If ignoreSchema is False, determine the schema file path
        if(schemaPath != None):
            # If the user has specified a path to the resource file, we'll use it without modification. Warn the user if the choice is unusual.
            if(os.path.basename(dataFilePath) != os.path.normpath(dataFilePath)):
                # If dataFilePath is not simply a filename
                if(os.path.dirname(os.path.abspath(schemaPath)) != os.path.dirname(os.path.abspath(dataFilePath))):
                    # If the absolute path to the schema file and the absolute path to the data put them in different directories
                    print("morpc.create_resource | WARNING | You seem to have specified a path for the schema file that is in a different directory than the data.  Typically the schema is located in the same directory as the data.")   
            schemaFilePath = os.path.normpath(schemaPath)
        else:
            # If the user has not specified a path to the schema file, we'll assume that it should go in the same directory as the data. In that
            # case, derive the path from the data path.
            schemaFilePath = dataFilePath.replace(dataFileExtension, ".schema.yaml")
            print("morpc.create_resource | INFO | Schema path not specified. Using path derived from data file path: {}".format(schemaFilePath))

    if title != None:
        resourceTitle = title
    else: 
        resourceTitle = dataFileName
        print("morpc.create_resource | INFO | Title not specified. Using placeholder value derived from data filename: {}".format(resourceTitle))

    if name != None:
        resourceName = name
    else:
        resourceName = re.sub(r"\W+", "-", dataFileName).lower()
        print("morpc.create_resource | INFO | Name not specified. Using placeholder value derived from data filename: {}".format(resourceName))

    if description != None:
        resourceDescription = description
    else:
        resourceDescription = "This dataset was produced by MORPC. For more information, please contact dataandmaps@morpc.org."
        print("morpc.create_resource | INFO | Description not specified. Using boilerplate placeholder value: {}".format(resourceDescription))

    if resMediaType != None:
        resourceMediaType = resMediaType
    else:
        if dataFileExtension.lower() in EXTENSION_MAP:
            resourceMediaType = EXTENSION_MAP[dataFileExtension.lower()]["mediatype"]
        else:
            print("morpc.create_resource | ERROR | Media type not specified and could not be determined from data file extension.")
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
            resource.hash = md5(os.path.join(os.path.dirname(resourceFilePath), dataFilePath))
        else:
            try:
                print("morpc.create_resource | WARNING | Data path is specified relative to resource file, however no resource file path was specified. Assuming data path is relative to current working directory.")
                unlocatedDataWarningIssued = True
                resource.hash = md5(dataFilePath)
            except:
                print("morpc.create_resource | ERROR | Unable to compute MD5 hash.  Data file could not be located.")
                raise RuntimeError            

    if(computeBytes):
        # If the data path is relative, we need to know the resource file path
        if(resourceFilePath != None):
            resource.bytes = os.path.getsize(os.path.join(os.path.dirname(resourceFilePath), dataFilePath))
        else:
            try:
                if(not unlocatedDataWarningIssued):
                    print("morpc.create_resource | WARNING | Data path is specified relative to resource file, however no resource file path was specified. Assuming data path is relative to current working directory.")
                resource.hash = md5(dataFilePath)
            except:
                print("morpc.create_resource | ERROR | Unable to compute file size (bytes).  Data file could not be located.")
                raise RuntimeError

    if(writeResource):
        if(resourceFilePath != None):
            print("morpc.create_resource | INFO | Writing Frictionless Resource file to {}".format(resourceFilePath))
            write_resource(resource, resourceFilePath)
        else:
            print("morpc.create_resource | ERROR | Unable to validate resource.  No resource file path specified.")
            raise RuntimeError            

    if(validate == True):
        if(resourceFilePath != None):
            print("morpc.create_resource | INFO | Validating resource on disk.")
            validate_resource(resourceFilePath)
        else:
            print("morpc.create_resource | ERROR | Unable to validate resource.  No resource file path specified.")
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
    import frictionless

    cwd = os.getcwd()

    try:
        os.chdir(os.path.dirname(resourcePath))
        resource.to_yaml(os.path.basename(resourcePath))
    except Exception as e:
        os.chdir(cwd)
        print("ERROR: An unhandled error occurred while trying to write the Frictionless resource: {}".format(e))
        raise RuntimeError
        
    os.chdir(cwd)


def validate_resource(resourcePath, verbose=True):
    import os
    import frictionless
    cwd = os.getcwd()

    try:
        os.chdir(os.path.dirname(resourcePath))    
      
        if(verbose):
            print("morpc.validate_resource | INFO | Validating resource on disk (including data and schema). This may take some time.")
        resourceOnDisk = frictionless.Resource(os.path.basename(resourcePath))
        results = resourceOnDisk.validate()

    except Exception as e:
        os.chdir(cwd)
        print("morpc.validate_resource | ERROR | An unhandled error occurred while trying to validate the Frictionless resource: {}".format(e))
        raise RuntimeError
        
    os.chdir(cwd)
    
    if(results.valid == True):
        if(verbose):
            print("morpc.validate_resource | INFO | Resource is valid")
        return True
    else:
        if(verbose):
            print("morpc.validate_resource | ERROR | Resource is NOT valid. Errors follow.")
            print(results)
        return False

def load_data(resourcePath, archiveDir=None, validate=False, verbose=True):
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

    Returns
    -------
    df : pandas.core.frame.DataFrame
        A GeoPandas GeoDataframe constructed from the data at the location specified by sourcePath and layerName
    resource : frictionless.resources.table.TableResource
        A Frictionless TableResource object which describes the data
    schema : frictionless.schema.schema.Schema
        A Frictionless Schema object which describes the data
    """

    import frictionless
    import pandas as pd
    import os
    import json
    import shutil

    myResourcePath = os.path.normpath(resourcePath)

    print("morpc.load_data | INFO | Loading Frictionless Resource file at location {}".format(myResourcePath))    
    
    resource = load_resource(myResourcePath)
    
    sourceDir = os.path.dirname(myResourcePath)
    resourceFilename = os.path.basename(myResourcePath)
    dataFileExtension = os.path.splitext(resource.path)[1]
        
    if(archiveDir != None):

        targetResource = os.path.join(archiveDir, resourceFilename)
        targetData = os.path.join(archiveDir, resource.path)
        # Surely there is a more convenient way to get the schema path from the Resource object?
        targetSchema = os.path.join(archiveDir, json.loads(resource.to_json())["schema"])
        
        try:
            print("morpc.load_data | INFO | Copying data, resource file, and schema to directory {}".format(archiveDir))    

            shutil.copyfile(os.path.join(sourceDir, resourceFilename), targetResource)
            shutil.copyfile(os.path.join(sourceDir, resource.path), targetData)
            shutil.copyfile(os.path.join(sourceDir, json.loads(resource.to_json())["schema"]), targetSchema)
        except Exception as e:
            print("morpc.load_data | ERROR | Unhandled exception when trying to copy data and associated Frictionless files: {}".format(e))
            raise RuntimeError
    
    else:           
        targetResource = os.path.join(sourceDir, resourceFilename)
        targetData = os.path.join(sourceDir, resource.path)
        targetSchema = os.path.join(sourceDir, json.loads(resource.to_json())["schema"])

        print("morpc.load_data | INFO | Loading data, resource file, and schema from their source locations")    

    print("morpc.load_data | INFO | --> Data file: {}".format(targetData))    
    print("morpc.load_data | INFO | --> Resource file: {}".format(targetResource))    
    print("morpc.load_data | INFO | --> Schema file: {}".format(targetSchema))    
    
    if(validate):
        print("morpc.load_data | INFO | Validating resource including data and schema.")    
        resourceValid = validate_resource(targetResource)
        if(not resourceValid):
            print("morpc.load_data | ERROR | Validation failed. Errors should be described above.")    
            raise RuntimeError
      
    print("morpc.load_data | INFO | Loading data.")          
    if(dataFileExtension == ".csv"):
        df = pd.read_csv(targetData, dtype="string")
    elif(dataFileExtension == ".xlsx"):
        df = pd.read_excel(targetData)
    else:
        print("morpc.load_data | ERROR | Unknown data file extension: {}".format(dataFileExtension))
        raise RuntimeError

    df = cast_field_types(df, resource.schema, verbose=verbose)
    
    return df, resource, resource.schema


# Given the path to a schema document in Avro format, load the Avro schema and reformat it as a
# Frictionless Schema object in memory
# WARNING: This function has not been extensively tested.  Be sure to validate the resulting
# Frictionless schema
def schema_from_avro(path):
    import frictionless
    import os
    
    fieldList = []
    avroSchema = load_avro_schema(os.path.normpath(path))
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
