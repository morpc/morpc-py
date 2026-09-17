# insights_assemble_tileset_package.py
#
# This script is a wrapper for morpc.insights.assemble_tileset_package(). Given an Insights Data Package 
# and an Insights Presentation Package, create an Insights Tileset Package including the associated 
# Frictionless package file and all of metadata and artifacts provided in the two input packages.

import morpc
import logging
import argparse
import sys
import os

LOGLEVEL = "info"

LOGFORMAT = '%(asctime)s | %(levelname)s | %(name)s.%(funcName)s: %(message)s'

LEVEL_MAP = {
    "debug": 10,
    "info": 20,
    "warning": 30,
    "error": 40,
    "critical": 50
}

logging.basicConfig(
    level=LEVEL_MAP[LOGLEVEL],
    force=True,
    format=LOGFORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
                        )
logging.getLogger(__name__).setLevel(LEVEL_MAP[LOGLEVEL])

epilogString = '''
# Examples
   
## Create tileset package in-situ (most common, least complex)

Typically, you\'ll already have a GitHub repository which contains the Data Package elements and Presentation Package 
elements and you just want to create the tileset Frictionless metadata (tileset.package.yaml) and update metadata in 
the catalog. In that case, you can rely on the defaults for most arguments. 

NOTE: Your catalog.xlsx will be overwritten in this case and some values will be altered. 

python insights_assemble_tileset_package.py "insights-pop" "Historic and Forecasted Population by Year" "C:\\Users\\yourname\\github\\insights-pop" 

## Create separate tileset package in new folder using all optional arguments (for reference only, real use cases are uncommon) 

python insights_assemble_tileset_package.py "insights-pop" "Historic and Forecasted Population by Year" "C:\\Users\\yourname\\github\\insights-pop" --dataPackagePath "C:\\some_path_to\\data.package.yaml" --presentationPackagePath "C:\\another_path_to\\presentation.package.yaml" --tilesetVersion "2026.09.17" --tilesetDescription "I didn\'t like the description in the Presentation Package so I wrote this one instead" --thumbnailUrlBase "https://www.myserver.com/somedir/"
'''
 
parser = argparse.ArgumentParser(
    description = "This script is a wrapper for morpc.insights.assemble_tileset_package(). Given an Insights Data Package and an Insights Presentation Package, create an Insights Tileset Package including the associated Frictionless package file and all of metadata and artifacts provided in the two input packages.",
    epilog = epilogString.replace("\\\\","\\"),
    formatter_class=argparse.RawDescriptionHelpFormatter    
)
parser.add_argument("tilesetSlug", 
    help = "A short string that uniquely identifies the tileset. Typically the GitHub repository slug, e.g. 'insights-pop'."
)
parser.add_argument("tilesetTitle", 
    help = "The title for the tileset package.  This will be combined with TITLE_PREFIX (see morpc.insights code) and the result will be used for the Frictionless 'title' property")
parser.add_argument("tilesetBasepath", 
    help = "A string representing the path to the root directory for the tileset contents.  This directory will be created if  it doesn't already exist. If no path is provided, the current working directory will be used."
)
parser.add_argument("--dataPackagePath", 
    help = "A string representing the path to the Frictionless YAML file that defines an Insights Data Package. This should be present in the root folder of the Data Package and should have the name 'data.package.yaml'. If no path is provided, the script will look for 'data.package.yaml' in in the directory specified for tilesetBasepath."
)
parser.add_argument("--presentationPackagePath", 
    help = "A string representing the path to the Frictionless YAML file that defines an Insights Presentation Package. This should be present in the root folder of the Presentation Package and should have the name 'presentation.package.yaml'. If no path is provided, the script will look for 'presentation.package.yaml' in in the directory specified for tilesetBasepath."
)
parser.add_argument("--tilesetVersion", 
    help = "A string that uniquely identifies this version of the tileset. Typically using the format YYYY.mm.dd. If tilesetVersion is not specified by the user, it will be constructed using the current date."
)
parser.add_argument("--tilesetDescription", 
    help = "A brief description of the subject matter covered by the tileset.  Will be used for the Frictionless 'description' property. If tilesetDescription is not specified by the user, the description from the Presentation Package will be used."
)
parser.add_argument("--thumbnailUrlBase", 
    help = "The base URL by which the thumbnail images will be accessed. Each thumbnail should be accessible by appending the thumbnail filename to the base URL. Typically the URL would point to a GitHub repository. If thumbnailUrlBase is not specified, the script will assume that GitHub is being used and will construct a URL using the tilesetSlug and the figures directory (see morpc.insights code)"
)
args = parser.parse_args()

morpc.insights.assemble_tileset_package(args.tilesetSlug, args.tilesetTitle, os.path.normpath(args.tilesetBasepath), 
    dataPackagePath = args.dataPackagePath, 
    presentationPackagePath = args.presentationPackagePath, 
    tilesetVersion = args.tilesetVersion, 
    tilesetDescription = args.tilesetDescription,
    thumbnailUrlBase = args.thumbnailUrlBase
)
