__version__ = "0.4.0"

import logging
logger = logging.getLogger(__name__)

from .morpc import *
from .logs import *
from .geocode import *
import morpc.frictionless
import morpc.census
import morpc.plot
import morpc.color
import morpc.color.palette as palette
import morpc.rest_api
