import datetime
import pandas as pd
import logging
logger = logging.getLogger(__name__)

def datetime_from_string(datestring) -> datetime.datetime:

    import datetime
    import pandas as pd
    import dateutil
    import re
    import math

    if isinstance(datestring, float):
        if datestring < 0:
            datestring = abs(datestring)

    if not isinstance(datestring, str):
        try:
            datestring = str(round(datestring))
        except:
            datestring = str(datestring)

        if (datestring.startswith('-')):
            datestring = datestring.strip('-')

    if isinstance(datestring, pd.api.typing.NaTType):
        dt = datestring
    elif isinstance(datestring, datetime.datetime):
        dt = datestring
    elif re.match(r'[0-9]{13}', datestring):
        datestring = re.sub(r'[^0-9]', "", datestring)
        dt = datetime.datetime.fromtimestamp(int(datestring)/1000)
    elif re.match(r'[0-9]{10}', datestring):
        dt = datetime.datetime.fromtimestamp(int(datestring))
    elif re.match(r'[0-9]{6}', datestring):
        dt = dateutil.parser.parse(datestring)
    elif re.match(r'[0-9]+[/\-\.][0-9]+[/\-\.][0-9]+', datestring):
        dt = dateutil.parser.parse(datestring)
    elif (datestring == 'nan') | (datestring == 'None') | (datestring == 'NaT'):
        dt = pd.NaT
    else:
        logger.error(f"Unable to parse {datestring}")
        raise ValueError
    
    return dt
