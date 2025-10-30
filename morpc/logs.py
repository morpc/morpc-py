
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

def config_logs(filename, level, mode = 'w'):
    """
    Set up logs within a notebook to store log outputs in filename, and display in output.
    """
    import logging
    import sys
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

    logger.info(f'Set up logging save to file {filename}')