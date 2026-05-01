import datetime
from os import PathLike
from numpy import isin
import pandas as pd
import logging

from pandas import DataFrame
from geopandas import GeoDataFrame
from typing import List, Literal
logger = logging.getLogger(__name__)

test_dates = [
    '2016-12-31T23:59:59+12:30',
    '2021-05-10T09:05:12.000Z',
    '3015-01-01T23:00+02:00',
    '1001-01-31T23:59:59Z',
    '2023-12-20T20:20',
    'June 3, 2026',
    '10/2/2020',
    '20210310',
    1372377600000000000,
    1372809600000,
    1373241600
]

def datetime_from_string(date, errors: Literal['coerce', 'error']='coerce') -> datetime.datetime:
    import datetime
    import pandas as pd
    import dateutil
    import re
    
    try:
        if isinstance(date, int):
            if re.match(r'[0-9]{19}', str(date)):
                dt = pd.to_datetime(date, unit='ns')
            elif re.match(r'[0-9]{13}', str(date)):
                dt = pd.to_datetime(date, unit='ms')
            elif re.match(r'[0-9]{10}', str(date)):
                dt = pd.to_datetime(date, unit='s')
        else:
            try:
                dt = pd.to_datetime(date)
            except OverflowError as e:
                logger.error(f"{date} is out of bounds")
                raise OverflowError
    except:
        try:
            # If already a date or time class, use that
            if isinstance(date, pd.api.typing.NaTType):
                dt = date
            elif isinstance(date, datetime.date):
                dt = date
        except:
            if not pd.api.types.is_string_dtype(date):
                try:
                    date = str(date)
                except:
                    try:
                        date = f"{date}"
                    except Exception as e:
                        logger.error(f"Failed to convert {date} to string.")

            if re.match(r'^\d{4}-(?:0[1-9]|1[0-2])-(?:[0-2][1-9]|[1-3]0|3[01])T(?:[0-1][0-9]|2[0-3])(?::[0-6]\d)(?::[0-6]\d)?(?:\.\d{3})?(?:[+-][0-2]\d:[0-5]\d|Z)?$', date):
                try:
                    dt = pd.to_datetime(date, format='ISO8601')
                except:
                    logger.error(f"Maybe found ISO format in {date} but couldn't convert.")

            elif re.match(r'[0-9]+[/\-\.][0-9]+[/\-\.][0-9]+', date):
                try:
                    dt = dateutil.parser.parse(date)
                except Exception as e:
                    logger.error(f"Maybe found date with separators in {date} but couldn't convert. {e}")
                
            elif re.match(r'[0-9]{6}', date):
                try:
                    dt = dateutil.parser.parse(date)
                except Exception as e:
                    logger.error(f"Maybe found a date as digits in ({date}) but couldn't convert. {e}")

            elif (date == 'nan') | (date == 'None') | (date == 'NaT'):
                dt = pd.NaT

        try:
            dt = dateutil.parser.parse(date)
        except Exception as e:
            logger.error(f"Last ditch effort to convert ({date}) but couldn't convert. {e}")
        
        if not isinstance(dt, datetime.date):
            raise ValueError
            
    if not isinstance(dt, datetime.date):
        logger.error(f"Failed to convert {date} to datetime.")
    
    try:
        dt = pd.to_datetime(dt).to_pydatetime()
    except pd.errors.OutOfBoundsDatetime as e:
        if errors == 'coerce':
            dt = pd.NaT
        else:
            logger.error(f"Date time is out of bounds.")
            raise OverflowError

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