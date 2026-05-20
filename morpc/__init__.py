__version__ = "0.5.3"

import logging
logger = logging.getLogger(__name__)

from .morpc import *
from .logs import *
from .geocode import *
import morpc.frictionless
import morpc.plot
import morpc.color.colors as colors
import morpc.color.palette as palette
import morpc.rest_api
import morpc.utils
