__version__ = "0.3.5"

import logging
logger = logging.getLogger(__name__)

from .morpc import *
from .logs import *
import morpc.frictionless
import morpc.census
import morpc.plot
import morpc.color
import morpc.color.palette as palette
import morpc.rest_api
