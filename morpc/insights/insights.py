"""
Functions for assembling and validating tileset packages for the MORPC
Insights platform
Reference: https://github.com/morpc/morpc-insights
"""

import logging
import frictionless

logger = logging.getLogger(__name__)

class DataPackage(frictionless.Package):
    _requiredProps = ["resources","name","title","description","version","contributors","_vintage","_updateInterval","_techDetailsUrl"]

    def from_descriptor(self, descriptor):
        import os
        self.basepath = os.path.normpath(os.path.dirname(descriptor))
        package = super().from_descriptor(descriptor)
        package.__class__ = DataPackage
        return package

    def get_property(self, prop):
        if(prop[0] == "_"):
            return self.custom[prop]
        else:
            return getattr(self, prop)

    def set_property(self, prop, value):
        if(prop[0] == "_"):
            self.custom[prop] = value
        else:
            setattr(self, prop, value)
            
    def is_complete(self):
        # Verify that required properties have been defined
        definedProps = self.list_defined()
        for key in self.custom.keys():
            definedProps.append(key)
        missingProps = set(self._requiredProps).difference(set(definedProps))
        if(len(missingProps) > 0):
            logger.error(f"The following required properties are not defined: {missingProps}")
            return False
        else:
            return True

        complete = True
        if(not "table" in self.resources):
            logger.error(f"Resources must include one resource named 'table' which provides the metadata for the long-form data table")
            complete = False
        if(not "process" in self.resource_names):
            logger.error(f"Resources must include one resource named 'process' which provides the metadata for a document describing the process by which the data was produced.")
            complete = False

        return complete
            
 
class PresentationPackage(frictionless.Package):
    _requiredProps = ["resources","name","title","description","version","contributors","_visualizationSpec","_visualizationSpecOverride","_moreContextUrl"]
    
    def from_descriptor(self, descriptor):
        import os
        self.basepath = os.path.normpath(os.path.dirname(descriptor))
        package = super().from_descriptor(descriptor)
        package.__class__ = PresentationPackage
        return package

    def get_property(self, prop):
        if(prop[0] == "_"):
             return self.custom[prop]
        else:
            return getattr(self, prop)

    def set_property(self, prop, value):
        if(prop[0] == "_"):
            self.custom[prop] = value
        else:
            setattr(self, prop, value)

    def is_complete(self):
        # Verify that required properties have been defined
        definedProps = self.list_defined()
        for key in self.custom.keys():
            definedProps.append(key)
        missingProps = set(self._requiredProps).difference(set(definedProps))
        if(len(missingProps) > 0):
            logger.error(f"The following required properties are not defined: {missingProps}")
            return False
        else:
            return True

        complete = True
        if(not "commentary" in self.resource_names):
            logger.error(f"Resources must include one resource named 'commentary' which provides a descriptor for the commentary table")
            complete = False

        return complete
        
class TilesetPackage(frictionless.Package):
    _nativeProps = ["name","title","description","version"]
    _requiredProps = ["resources","name","title","description","version","contributors","_vintage",
                      "_updateInterval","_techDetailsUrl","_visualizationSpec","_visualizationSpecOverride",
                      "_moreContextUrl"]    
    
    def from_descriptor(self, descriptor):
        import os
        self.basepath = os.path.normpath(os.path.dirname(descriptor))        
        package = super().from_descriptor(descriptor)
        package.__class__ = PresentationPackage
        return package

    def props_from_packages(self, dataPackage, presentationPackage):
        self.resources = []
        self.dataPackageBasepath = dataPackage.basepath
        self.presentationPackageBasepath = presentationPackage.basepath
        for prop in dataPackage._requiredProps:
            if((prop in self._nativeProps) or (prop == "resources")):
                continue
            else:
                self.set_property(prop, dataPackage.get_property(prop))
        for prop in presentationPackage._requiredProps:
            if((prop in self._nativeProps) or (prop == "resources")):
                continue
            else:
                self.set_property(prop, presentationPackage.get_property(prop))
            
    def get_property(self, prop):
        if(prop[0] == "_"):
             return self.custom[prop]
        else:
            return getattr(self, prop)

    def set_property(self, prop, value):
        if(prop[0] == "_"):
            self.custom[prop] = value
        else:
            setattr(self, prop, value)

    def is_complete(self):
        # Verify that required properties have been defined
        definedProps = self.list_defined()
        for key in self.custom.keys():
            definedProps.append(key)
        missingProps = set(self._requiredProps).difference(set(definedProps))
        if(len(missingProps) > 0):
            logger.error(f"The following required properties are not defined: {missingProps}")
            return False

        complete = True
        if(not "catalog" in self.resource_names):
            logger.error(f"Resources must include one resource named 'catalog' which provides the metadata for an Excel document which includes the details required for this tileset for inclusion in the Insights platform catalog")
            complete = False
        if(not "table" in self.resource_names):
            logger.error(f"Resources must include one resource named 'table' which provides the metadata for the long-form data table")
            complete = False
        if(not "process" in self.resource_names):
            logger.error(f"Resources must include one resource named 'process' which provides the metadata for a document describing the process by which the data was produced.")
            complete = False
        if(not "readme" in self.resource_names):
            logger.error(f"Resources must include one resource named 'readme' which provides the metadata for a document (ideally named README.md and in Markdown format) which provides human-readable notes and metadata for this tileset.")
            complete = False
        if(not "maintainer" in self.resource_names):
            logger.error(f"Resources must include one resource named 'maintainer' which provides the metadata for a document (ideally named MAINTAINER.md and in Markdown format) which describes the process to update the tileset.")
            complete = False
        
        return complete

def assemble_tileset_package(tilesetSlug, tilesetTitle, tilesetBasepath="./", dataPackagePath=None, presentationPackagePath=None, tilesetVersion=None, tilesetDescription=None, thumbnailUrlBase=None):
    """
    Given an Insights Data Package and an Insights Presentation Package, create an Insights Tileset Package including the associated 
    Frictionless package file and all of metadata and artifacts provided in the two input packages.

    Parameters
    ----------
    tilesetSlug : str
        A short string that uniquely identifies the tileset. Typically the GitHub repository slug, e.g. "insights-pop".
    tilesetTitle : str
        The title for the tileset package.  This will be combined with TITLE_PREFIX (see below) and the result will be 
        used for the Frictionless "title" property 
    tilesetBasepath : str
        A string representing the path to the root directory for the tileset contents.  This directory will be created if
        it doesn't already exist. If no path is provided, the current working directory will be used.
    dataPackagePath : str
        A string representing the path to the Frictionless YAML file that defines an Insights Data Package. This should
        be present in the root folder of the Data Package and should have the name "data.package.yaml". If no path is provided,
        the script will look for "data.package.yaml" in in the directory specified for tilesetBasepath.
    presentationPackagePath : str
        A string representing the path to the Frictionless YAML file that defines an Insights Presentation Package. This should
        be present in the root folder of the Presentation Package and should have the name "presentation.package.yaml". If no 
        path is provided, the script will look for "presentation.package.yaml" in in the directory specified for tilesetBasepath.
    tilesetVersion : str
        A string that uniquely identifies this version of the tileset. Typically using the format YYYY.mm.dd. If tilesetVersion
        is not specified by the user, it will be constructed using the current date.
    tilesetDescription : str
        A brief description of the subject matter covered by the tileset.  Will be used for the Frictionless "description"
        property. If tilesetDescription is not specified by the user, the description from the Presentation Package will be
        used.
    thumbnailUrlBase : str
        The base URL by which the thumbnail images will be accessed. Each thumbnail should be accessible by appending the thumbnail
        filename to the base URL. Typically the URL would point to a GitHub repository. If thumbnailUrlBase is not specified, the script
        will assume that GitHub is being used and will construct a URL using the tilesetSlug and the figures directory (see below)

    Returns
    -------
    tp : morpc.insights.TilesetPackage
        An object representing an Insights Tileset Package.  Includes metadata from the referenced Data Package and 
        Presentation Package
    """    
    # ## Setup
    # ### Import required packages
    import morpc
    import frictionless
    import datetime
    import xlsxwriter
    import pandas as pd
    import os
    import posixpath
    import shutil
    import logging

    # ### Static parameters
    # Prefix that will be applied to the tileset title
    TITLE_PREFIX = "MORPC Insights"
    # Subdirectory of tileset directory where output data will be stored
    OUTPUT_DATA_DIR = "output_data"
    # Subdirectory of tileset directory where input data will be stored
    INPUT_DATA_DIR = "input_data"
    # Subdirectory of tileset directory where figures will be stored
    FIGURES_DIR = "figures"
    # Subdirectory of tileset directory where non-required will be stored        
    MISC_DIR = "misc"
    # Default file name to use for data package if no path is provided
    DEFAULT_DATAPACKAGE_FILENAME = "data.package.yaml"
    # Default file name to use for presentation package if no path is provided
    DEFAULT_PRESENTATIONPACKAGE_FILENAME = "presentation.package.yaml"
    # Filename for the tileset package when written to disk
    TILESET_PACKAGE_FILENAME = "tileset.package.yaml"

    # ### Start logging
    logger = logging.getLogger(__name__)
    
    # ### Interpret arguments
    if(dataPackagePath is None):
        dataPackagePath = os.path.normpath(os.path.join("./", DEFAULT_DATAPACKAGE_FILENAME))
        logger.info(f"Data Package path was not specified. Using default path {dataPackagePath}")        
    if(presentationPackagePath is None):
        presentationPackagePath = os.path.normpath(os.path.join("./", DEFAULT_PRESENTATIONPACKAGE_FILENAME))
        logger.info(f"Presentation Package path was not specified. Using default path {presentationPackagePath}")  
    if(tilesetVersion is None):
        tilesetVersion = datetime.datetime.now().strftime("%Y.%m.%d")
        logger.info(f"Tileset version was not specified. Using version derived from today's date {tilesetVersion}") 
    if(thumbnailUrlBase is None):
        thumbnailUrlBase = f"https://raw.githubusercontent.com/morpc-insights/{tilesetSlug}/refs/heads/main/{FIGURES_DIR}/"
        logger.info(f"Thumbnail base URL was not specified. Using URL constructed from the tileset slug and the figures directory name: {thumbnailUrlBase}") 
        
    # ## Prepare inputs
    # ### Read data package configuration
    dp = morpc.insights.DataPackage().from_descriptor(dataPackagePath)
    results = dp.validate()
    if(not results.valid):
        logger.error("Input Data Package is not a valid Frictionless Package. Details follow.")
        logger.error(results)
        raise RuntimeError
    if(not dp.is_complete()):
        logger.error("Input Data Package is missing one or more required elements.")
        raise RuntimeError
    else:
        logger.info(f"Reading Data Package at {dataPackagePath}")

    # ### Read presentation package configuration
    pp = morpc.insights.PresentationPackage().from_descriptor(presentationPackagePath)
    results = pp.validate()
    if(not results.valid):
        logger.error("Input Presentation Package is not a valid Frictionless Package. Details follow.")
        logger.error(results)
        raise RuntimeError
    if(not pp.is_complete()):
        logger.error("Input Presentation Package is missing one or more required elements.")
        raise RuntimeError
    else:
        logger.info(f"Reading Presentation Package at {presentationPackagePath}")

    if(tilesetDescription is None):
        tilesetDescription = pp.description
        logger.info(f"Tileset description was not specified. Using description provided in Presentation Package")       
    
    # ## Create tileset package
    # ### Create tileset directory structure
    logger.info("Creating tileset directory structure (as needed)")
    tilesetBasepath = os.path.normpath(tilesetBasepath)
    tilesetOutputDataPath = os.path.join(tilesetBasepath, OUTPUT_DATA_DIR)
    tilesetInputDataPath = os.path.join(tilesetBasepath, INPUT_DATA_DIR)    
    tilesetFiguresPath = os.path.join(tilesetBasepath, FIGURES_DIR)
    tilesetMiscPath = os.path.join(tilesetBasepath, MISC_DIR)
    if not os.path.exists(tilesetBasepath):
        os.makedirs(tilesetBasepath)
    if not os.path.exists(tilesetOutputDataPath):
        os.makedirs(tilesetOutputDataPath)
    if not os.path.exists(tilesetInputDataPath):
        os.makedirs(tilesetInputDataPath)        
    if not os.path.exists(tilesetFiguresPath):
        os.makedirs(tilesetFiguresPath)
    if not os.path.exists(tilesetMiscPath):
        os.makedirs(tilesetMiscPath)    

    # ### Define tileset package properties
    logger.info("Defining tileset package properties")
    tp = morpc.insights.TilesetPackage()
    tp.props_from_packages(dp, pp)
    tp.basepath = tilesetBasepath
    tp.set_property("name", tilesetSlug)
    tp.set_property("title", tilesetTitle)
    tp.set_property("description", tilesetDescription)
    tp.set_property("version", tilesetVersion)
    tp.dataPackageBasepath = posixpath.dirname(dataPackagePath)
    tp.presentationPackageBasepath = posixpath.dirname(presentationPackagePath)
    tp.resources = []

    # ### Add resources to tileset package
    # #### README
    logger.info("Adding README.md resource to tileset package.")
    readmeResource = frictionless.Resource()
    readmeResource.name = "readme"
    readmeResource.title= f"{TITLE_PREFIX} | {tilesetTitle} | README"
    readmeResource.description = "This document provides an overview and metadata about the insights-pop (Historic and Forecasted Population by Year) tileset in a human-readable form."
    readmeResource.path = "README.md"
    tp.add_resource(readmeResource);

    # #### Maintainer guide
    logger.info("Adding Maintainer Guide resource to tileset package.")
    maintainerResource = frictionless.Resource()
    maintainerResource.name = "maintainer"
    maintainerResource.title= f"{TITLE_PREFIX} | {tilesetTitle} | Maintainer Guide"
    maintainerResource.description = f"This document describes how to update the {tilesetSlug} ({tilesetTitle}) tileset."
    maintainerResource.path = "MAINTAINER.md"
    tp.add_resource(maintainerResource);

    # #### Resources from data package
    # Add resources to tileset package.
    logger.info("Adding resources defined in data package.")
    for resource in dp.resources:
        if(resource.name in tp.resource_names):
            logger.error(f"Resource {resource.name} already defined in tileset package")
            raise RuntimeError
        else:
            logger.info(f"--> Resource: {resource.name}")
            if((resource.name == "table") or (resource.name.find("output") != -1)):
                # Put the data table (and schema and resource file if available) in the data directory. If there are other outputs, do the same for those.
                destinationDir = posixpath.normpath(OUTPUT_DATA_DIR)
            elif(resource.name.find("process") != -1):
                # Put any process definitions (i.e. any resources whose names include "process") in the root directory
                destinationDir = ""
            elif(resource.name.find("input") != -1):
                # Put any input data (and schema and resource file if available) in the input data directory
                destinationDir = posixpath.normpath(INPUT_DATA_DIR)
            else:
                # Put all other resources in the misc direcotry
                destinationDir = posixpath.normpath(MISC_DIR)
            resource.path = posixpath.join(destinationDir, posixpath.basename(resource.path))
            tp.add_resource(resource)

    # Copy files specified as resources from the data package file structure to the tileset package file structure. For data files, attempt
    # to copy the schema and resource files too, if available.
    for resourceName in dp.resource_names:
        logger.info(f"Copying files associated with Data Package resource '{resourceName}'")
        resource = dp.get_resource(resourceName)
        sourcePath = os.path.normpath(os.path.join(tp.dataPackageBasepath, resource.path))
        destinationPath = os.path.normpath(os.path.join(tp.basepath, resource.path))

        if(os.path.abspath(sourcePath) == os.path.abspath(destinationPath)):
            logger.info(f"--> Destination path and source path resolve to the same absolute path ({os.path.abspath(sourcePath)}). Will not copy file.")
        else:
            logger.info(f"--> Copying file from {sourcePath} to {destinationPath}")
            shutil.copyfile(sourcePath, destinationPath)
        
        # For the long form table (required) the and any resources designated as inputs or outputs (optional), we also need to copy
        # the schema and standalone resource file. The schema is required for the long form table, but optional for others.
        if((resourceName == "table") or (resource.name.find("input") != -1) or (resource.name.find("output") != -1)):
            # In the next line, I would think you could access the schema filename as resource.schema,
            # however frictionless seems to dereference the schema automatically and it returns a
            # schema object. It is possible to get the schema filename through metadata_export, but
            # maybe there is a better way?
            if("schema" in resource.metadata_export()):
                schemaPath = resource.metadata_export()["schema"]
                sourcePath = os.path.normpath(os.path.join(tp.dataPackageBasepath, schemaPath))           
                if(os.path.exists(sourcePath)):
                    logger.info(f"--> Detected schema associated with resource {resourceName}. Copying schema from data package to tileset package")
                    destinationPath = os.path.normpath(os.path.join(tp.basepath, schemaPath))
                    if(os.path.abspath(sourcePath) == os.path.abspath(destinationPath)):
                        logger.info(f"--> Destination path and source path resolve to the same absolute path ({os.path.abspath(sourcePath)}). Will not copy file.")
                    else:
                        logger.info(f"--> Copying file from {sourcePath} to {destinationPath}")
                        shutil.copyfile(sourcePath, destinationPath)
                else:
                    logger.error(f"--> Schema defined for resource '{resource}' but specified file does not exist ({sourcePath})")
                    raise RuntimeError
            else:
                if(resourceName == "table"):
                    logger.error(f"--> Schema is required for resource 'table' but schema path was not specified.")
                    raise RuntimeError
                else:
                    logger.warning(f"--> Schema path not specified for resource '{resourceName}'. Schema will not be included in Tileset Package.")
                    
            # There may not be a standalone resource file because the resource information is required to be captured in the package file. 
            # Guess at the name of a standalone resource. If it exists, we'll grab that too. Our guess assumes that the resource file is located 
            # in the same directory as the data file and is named similarly but with extension ".resource.yaml"
            extension = os.path.splitext(resource.path)[1]
            sourcePath = os.path.normpath(os.path.join(tp.dataPackageBasepath, resource.path.replace(extension,".resource.yaml")))
            if(os.path.exists(sourcePath)):
                logger.info("--> Detected standalone resource file. Copying resource file from data package to tileset package")
                destinationPath = os.path.normpath(os.path.join(tp.basepath, resource.path.replace(extension,".resource.yaml")))
                if(os.path.abspath(sourcePath) == os.path.abspath(destinationPath)):
                    logger.info(f"--> Destination path and source path resolve to the same absolute path ({os.path.abspath(sourcePath)}). Will not copy file.")
                else:
                    logger.info(f"--> Copying file from {sourcePath} to {destinationPath}")
                    shutil.copyfile(sourcePath, destinationPath)    

    # #### Resources from presentation package
    # Add resources to tileset package.
    logger.info("Adding resources defined in presentation package.")
    for resource in pp.resources:
        if(resource.name in tp.resource_names):
            logger.error(f"Resource {resource.name} already defined in tileset package")
            raise RuntimeError
        else:
            logger.info(f"--> Resource: {resource.name}")
            if(resource.name == "catalog"):
                # Put the catalog in the root directory
                destinationDir = ""
            else:
                # Put all other resources in the misc direcotry
                destinationDir = posixpath.normpath(os.path.join(tp.basepath, MISC_DIR))
            resource.path = posixpath.join(destinationDir, posixpath.basename(resource.path))
            tp.add_resource(resource)

    # Copy files specified as resources from the presentation package file structure to the tileset package file structure.
    resource_names = pp.resource_names
    # We will not copy the catalog. Rather, we'll read it, make some adjustments, and write the adjusted version
    resource_names.remove("catalog")
    for resourceName in pp.resource_names:
        logger.info(f"Copying files associated with Presentation Package resource '{resourceName}'")
        resource = pp.get_resource(resourceName)
        sourcePath = os.path.normpath(os.path.join(tp.dataPackageBasepath, resource.path))
        destinationPath = os.path.normpath(os.path.join(tp.basepath, resource.path))
        if(os.path.abspath(sourcePath) == os.path.abspath(destinationPath)):
            logger.info(f"--> Destination path and source path resolve to the same absolute path ({os.path.abspath(sourcePath)}). Will not copy file.")
        else:
            logger.info(f"--> Copying file from {sourcePath} to {destinationPath}")
            shutil.copyfile(sourcePath, destinationPath)

    # ## Update catalog
    logger.info("Loading catalog provided with presentation package")
    catalogResource = pp.get_resource("catalog")
    catalog = pd.read_excel(catalogResource.path)

    # Ensure that all values expected in the Presentation Package have been populated.
    missingFlag = False
    for column in ["GeographyType","GeographyName","Headline","Commentary","ThumbnailURL","DataProductURL"]:
        if(not catalog.loc[catalog[column].isna()].empty):
            missingFlag = True
            if(column == "Headline"):
                additionalInstructions = "The headlines for community-level geographies may be identical."
            elif(column == "Commentary"):
                additionalInstructions = "The commentary for community-level geographies may be identical."
            elif(column == "ThumbnailURL"):
                additionalInstructions = "Please enter URLs or paths for all geographies. If a local path is provided it will be converted to a URL using the thumbnailUrlBase value."
            elif(column == "DataProductURL"):
                additionalInstructions = "Please enter a data product URLs for all geographies. Each geography may have a unique URL, or any set of geographies may share a common URL."
            logger.error(f"Blank values detected in column {column}. Please enter a value for for all geographies. {additionalInstructions}")
    if(missingFlag == True):
        raise RuntimeError
    else:
        logger.info("No missing values detected.")

    # Update thumbnail URLs and copy provided images from the presentation package to the tileset package if necessary
    visualizationSpec = pp.get_property("_visualizationSpec")
    if(visualizationSpec == "useProvidedCopy"):
        logger.info("Creating copies of the thumbnails in the tileset package.")
        filenames = catalog["ThumbnailURL"].apply(lambda x:os.path.basename(x))
        catalog["ThumbnailURL"] = thumbnailUrlBase + filenames
        showNotification = True
        for file in filenames:
            sourcePath = os.path.normpath(os.path.join(tp.presentationPackageBasepath, FIGURES_DIR, file))
            destinationPath = os.path.normpath(os.path.join(tp.basepath, FIGURES_DIR, file))
            if(os.path.abspath(sourcePath) == os.path.abspath(destinationPath)):
                if(showNotification == True):
                    logger.info(f"Destination path and source path resolve to the same absolute path ({os.path.abspath(sourcePath)}). Will not copy file. Notifications will be suppressed for remaining files.")
                    showNotification = False
            else:
                shutil.copyfile(sourcePath, destinationPath)            
    elif(visualizationSpec == "useProvidedInPlace"):
        # In this case, we'll use the provided URL as-is. Make no changes.
        logger.info("Using provided thumbnail URLs as-is. No changes required")  
    else:
        # Eventually we will support construction of figures from a visualization specification. As of September 2026, 
        # this is not implemented. Return an error.
        logger.error("Only visualizationSpec values useProvidedCopy and useProvidedInPlace are currently supported.")
        raise RuntimeError

    # Ensure TileID, TilesetID, Category, and ShareURL are blank.  These are managed by a downstream workflow.
    catalog["TileID"] = None
    catalog["TilesetID"] = None
    catalog["Category"] = None
    catalog["ShareURL"] = None

    # Populate Contributor, Vintage, and UpdateInterval from metadata originally from the Data Package
    catalog["Contributor"] = tp.contributors[0]["title"]
    catalog["Vintage"] = tp.get_property("_vintage")
    catalog["UpdateInterval"] = tp.get_property("_updateInterval")

    # Write the updated catalog to disk in the Tileset Package file structure
    logger.info("Writing updated catalog to disk")
    sourcePath = os.path.normpath(os.path.join(tp.presentationPackageBasepath, catalogResource.path))
    destinationPath = os.path.normpath(os.path.join(tp.basepath, os.path.basename(catalogResource.path)))
    if(os.path.abspath(sourcePath) == os.path.abspath(destinationPath)):
        logger.info(f"Destination path and source path resolve to the same absolute path ({os.path.abspath(sourcePath)}). Existing catalog will be updated in-place.")
    else:
        logger.info(f"Destination path ({os.path.abspath(destinationPath)}) is different than source path ({os.path.abspath(sourcePath)}). Catalog provided with Presentation Package will be left unaltered.")       
    catalog.to_excel(destinationPath, index=False)
    
    # ### Validate tileset package
    logger.info("Checking completeness of Tileset Package object")
    if(not tp.is_complete()):
        logger.error("--> Tileset package object is missing one or more required elements")
        raise RuntimeError
    else:
        logger.info("--> Tileset package object is complete")

    # ## Create README.md file
    logger.info("Creating README.md file")

    README_TEMPLATE = f'''
    # {tp.title}

    ## Version

    Current version: {tp.version}

    ## Contributors

    {"\n".join([f"{x['title']}, {x['organization']}, {x['email']}" for x in tp.contributors])}

    ## Introduction

    {tp.description}

    ## Data

    Data file: {tp.get_resource("table").path}

    Schema: {schemaPath}

    ## Processes

    Process documentation: {tp.get_resource("process").path}
    '''

    with open(os.path.join(tilesetBasepath, readmeResource.path), "w") as f:
        f.write(README_TEMPLATE)
   
    # ## Write tileset package to disk and validate it
    logger.info(f"Writing tileset package descriptor to disk")
    destinationPath = os.path.normpath(os.path.join(tilesetBasepath, TILESET_PACKAGE_FILENAME))
    tp.to_yaml(destinationPath);
    results = morpc.frictionless.validate(destinationPath)
    if(not results.valid):
        logger.error("Tileset Package is not a valid Frictionless Package. Details follow.")
        logger.error(results)

    # ## Clean up
    # Delete the misc directory if it is empty.  Not all tilesets include misc content. Same with input data directory.
    if(len(os.listdir(tilesetMiscPath)) == 0):
        os.rmdir(tilesetMiscPath)
    if(len(os.listdir(tilesetInputDataPath)) == 0):
        os.rmdir(tilesetInputDataPath)        
    
    return tp                

                