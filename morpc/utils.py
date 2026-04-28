import datetime
from os import PathLike
import pandas as pd
import logging

from pandas import DataFrame
from geopandas import GeoDataFrame
from typing import List
logger = logging.getLogger(__name__)

def datetime_from_string(datestring) -> datetime.datetime:

    import datetime
    import pandas as pd
    import dateutil
    import re
    
    try:
        # Catch and convert negative numbers
        if isinstance(datestring, float):
            if datestring < 0:
                datestring = abs(datestring)

        # If already a date or time class, use that
        if isinstance(datestring, pd.api.typing.NaTType):
            dt = datestring
        elif isinstance(datestring, datetime.datetime):
            dt = datestring

        # Otherwise try some stuff
        else:
            # Try to convert from unix timestamp
            try:
                dt = datetime.datetime.fromtimestamp(int(datestring))
            except:
                # and timestamp in milliseconds
                try:
                    dt = datetime.datetime.fromtimestamp(int(datestring)/1000)
                except:
                    # If that still doesn't work, convert to a string so we can use regex
                    if not isinstance(datestring, str):
                        try:
                            datestring = str(round(datestring))
                        except:
                            datestring = str(datestring)

                        if (datestring.startswith('-')):
                            datestring = datestring.strip('-')
                    # Try to match patterns that make sense

                    # Timestamps with some other characters maybe?
                    if re.match(r'[0-9]{10:14}', datestring):
                        datestring = re.sub(r'[^0-9]', "", datestring)
                        try:
                            dt = datetime.datetime.fromtimestamp(int(datestring))
                        except:
                            try:
                                dt = datetime.datetime.fromtimestamp(int(datestring)/1000)
                            except Exception as e:
                                logger.error(f"Maybe found timestamp ({datestring}) but couldn't convert. {e}")

                    # Just the date as digits?           
                    elif re.match(r'[0-9]{6}', datestring):
                        try:
                            dt = dateutil.parser.parse(datestring)
                        except Exception as e:
                            logger.error(f"Maybe found a date as digits in ({datestring}) but couldn't convert. {e}")

                    elif re.match(r'[0-9]+[/\-\.][0-9]+[/\-\.][0-9]+', datestring):
                        try:
                            dt = dateutil.parser.parse(datestring)
                        except Exception as e:
                            logger.error(f"Maybe found date with separators in {datestring} but couldn't convert. {e}")
                    elif (datestring == 'nan') | (datestring == 'None') | (datestring == 'NaT'):
                        dt = pd.NaT
                    else:
                        logger.error(f"Unable to parse {datestring}")
                        raise ValueError
    except Exception as e:
        raise ValueError
    
    return dt

class DataFrameSummary:
    def __init__(self, df: DataFrame | GeoDataFrame, columns: List[str] | None = None, title: str | None = None):
        """
        Create a summary of descriptives for dataframe columns.

        Parameters
        ----------
        df : DataFrame | GeoDataFrame
            The dataframe to summarize

        columns : List[str] | None, optional
            A list of columns to include, by default all columns

        title : str | None, optional
            A title for the markdown header

        Returns
        -------
        str
            a markdown formatted string
        """

        # if columns is None default to 
        if columns == None:
            columns = df.columns

        # default title if not supplied
        if title == None:
            title = f"Summary of descriptives for each column"

        data_summary = f"# {title}\nTotal Rows: {df.shape[0]}\n"
        for column in df.columns:
            if column in columns:
                type = df[column].dtype.__str__()
                data_summary += f"\n## Column: {column}\n\n*Data type*:   {type}  \n"
                
                if type in ['string', 'object']:
                    data_summary += f"{df[column].describe().to_markdown()}\n"
                    data_summary += f"**Missing**:     {(sum(df[column].isna())/len(df[column]))*100:.2f}%  \n"
                    data_summary += f"**Unique**:      {(len([x for x in df[column].unique()])/len(df[column]))*100:.2f}%  \n"
                    data_summary += f"**Sample**:      {", ".join(df[column].sample(10, ).fillna('<NA>').to_list())}  \n"

                if type in ['Int64', 'int', 'float64', 'datetime64[ns]']:
                    data_summary += f"{df[column].describe().to_markdown()}\n"

                    # data_summary += f"\n{self.textplot_column(df[column])}\n"
                
                if type in ['geometry']:
                    data_summary += f"**Geometry Types**:  \n{df[column].geom_type.value_counts().to_markdown()}  \n"
                    data_summary += f"**Total Bounds**:     {str(df[column].total_bounds)}  \n"
                    data_summary += f"**CRS**:              {str(df['geometry'].crs)}  \n\n"

        self.data_summary = data_summary

    def save(self, path: PathLike) -> None:
        """
        Save the data summary to a file.

        Parameters
        ----------
        path : PathLike
            The path to save the file to
        """
        import os
        path = os.path.normpath(path)

        if not os.path.exists(os.path.dirname(path)):
            os.mkdir(os.path.dirname(path))

        with open(path, "w") as path:
            path.write(self.data_summary)

    def print(self):
        """Print the summary"""

        print(self.data_summary)

    # def textplot_column(self, column):
    #     import termplotlib as tpl
    #     import numpy as np

    #     counts, bins = np.histogram([x for x in column.to_list() if not np.isnan(x)], bins=25)
    #     fig = tpl.figure()
    #     fig.hist(counts, bins, force_ascii=False)
    #     string = fig.get_string()

    #     return string