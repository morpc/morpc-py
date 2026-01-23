
"""
This module is used to set up logging when developing a workflow. Call morpc.logs.config_logs() after importing wanted packages. 

See https://stackoverflow.com/questions/42388844/where-to-configure-logging for logging set up for packages, modules, class, and instances. 
"""

import logging 

logger = logging.getLogger(__name__)

LOGFORMAT = '%(asctime)s | %(levelname)s | %(name)s.%(funcName)s: %(message)s'

LEVEL_MAP = {
    "debug": 10,
    "info": 20,
    "warning": 30,
    "error": 40,
    "critical": 50
}

def config_logs(filename=None, level='info', mode = 'w'):
    """
    Set up logs within a notebook to store log outputs in filename, and display in output.
    """
    import logging
    import sys
    import os
    import ipykernel
    import json
    
    fileSpecified = True
    if(filename is None):
        fileSpecified = False
        connectionInfo = json.loads(ipykernel.get_connection_info())
        scriptFilename = os.path.basename(os.path.normpath(connectionInfo["jupyter_session"]))
        filename = f"{scriptFilename}.log"
    
    logging.basicConfig(
        level=LEVEL_MAP[level],
        force=True,
        format=LOGFORMAT,
        handlers=[
            logging.FileHandler(filename=filename, mode=mode),
            logging.StreamHandler(sys.stdout)
        ]
                        )
    logging.getLogger(__name__).setLevel(LEVEL_MAP[level])

    if(fileSpecified == False):
        logger.info(f'Log filename not specified.  Using default filename.')

    logger.info(f'Set up logging save to file "{filename}", log level "{level}"')
