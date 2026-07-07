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
    """
    Best-effort conversion of a wide range of date/datetime representations to a
    timezone-naive ``datetime.datetime``.

    Handled inputs, in order of preference:

    - ``pandas.NaT`` / ``None`` / empty-ish strings (``''``, ``'nan'``, ``'None'``,
      ``'NaT'``) -> ``pandas.NaT``
    - existing ``datetime.datetime`` / ``datetime.date`` objects
    - numeric epochs, dispatched by digit count: 19 -> ns, 13 -> ms, 10 -> s
      (works for ``int`` *and* ``float``)
    - compact numeric dates: 8 digits -> ``YYYYMMDD``, 6 digits -> ``YYYYMM``
      (``int``, ``float``, or ``str``)
    - ISO 8601 strings (validated/parsed by pandas)
    - general date strings parsed month-first / US order (via ``dateutil``)
    - natural-language, relative, and localized strings (via ``dateparser``, if
      installed; otherwise this final fallback is skipped)

    Ambiguous numeric dates such as ``'10/2/2020'`` are interpreted month-first
    (US): October 2, 2020.

    Timezone-aware inputs (e.g. ISO strings with an offset, or aware ``datetime``
    objects) are returned tz-naive, preserving the written wall-clock time, so
    results never mix aware and naive values.

    Parameters
    ----------
    date : Any
        The value to convert.
    errors : {'coerce', 'error'}, default 'coerce'
        ``'coerce'`` returns ``pandas.NaT`` on failure; ``'error'`` re-raises.

    Returns
    -------
    datetime.datetime or pandas.NaT
    """
    import datetime
    import math
    import re
    import pandas as pd
    import dateutil.parser

    def _from_number(value):
        """Interpret a number as an epoch (by digit count) or compact YYYYMMDD/YYYYMM date."""
        n = int(value)
        digits = len(str(abs(n)))
        if digits == 19:
            return pd.to_datetime(n, unit='ns').to_pydatetime()
        if digits == 13:
            return pd.to_datetime(n, unit='ms').to_pydatetime()
        if digits == 10:
            return pd.to_datetime(n, unit='s').to_pydatetime()
        if digits == 8:
            return datetime.datetime.strptime(str(n), '%Y%m%d')
        if digits == 6:
            return datetime.datetime.strptime(str(n), '%Y%m')
        raise ValueError(
            f"Numeric value {value!r} does not match a recognized epoch length "
            f"(10, 13, or 19 digits) or compact date (8=YYYYMMDD, 6=YYYYMM)."
        )

    def _make_naive(value):
        """Drop tzinfo (preserving wall-clock) so outputs are consistently tz-naive."""
        if isinstance(value, datetime.datetime) and value.tzinfo is not None:
            return value.replace(tzinfo=None)
        return value

    dt = pd.NaT

    try:
        if isinstance(date, pd.api.typing.NaTType) or date is None:
            dt = pd.NaT

        elif isinstance(date, float):
            dt = pd.NaT if math.isnan(date) else _from_number(date)

        # datetime.datetime must be checked before datetime.date (it's a subclass)
        elif isinstance(date, datetime.datetime):
            dt = date

        elif isinstance(date, datetime.date):
            dt = datetime.datetime.combine(date, datetime.time.min)

        elif isinstance(date, int):
            dt = _from_number(date)

        else:
            if not isinstance(date, str):
                try:
                    date = str(date)
                except Exception as e:
                    logger.error(f"Failed to convert {date!r} to string.")
                    raise e

            date = date.strip()

            if date in ('nan', 'None', 'NaT', ''):
                dt = pd.NaT

            # Pure-digit strings share the numeric epoch / compact-date logic so that,
            # e.g., '20210310' and 20210310 resolve identically.
            elif re.fullmatch(r'\d{6}|\d{8}|\d{10}|\d{13}|\d{19}', date):
                dt = _from_number(int(date))

            else:
                dt = None

                # 1) ISO 8601 (pandas validates and raises if the string isn't ISO).
                try:
                    dt = pd.to_datetime(date, format='ISO8601').to_pydatetime()
                except Exception:
                    dt = None

                # 2) General date strings, US month-first ordering.
                if dt is None:
                    try:
                        dt = dateutil.parser.parse(date, dayfirst=False)
                    except Exception:
                        dt = None

                # 3) Natural-language / relative / localized strings. dateparser is an
                #    optional catch-all; if it isn't installed we simply skip it.
                if dt is None:
                    try:
                        import dateparser
                        dt = dateparser.parse(date, settings={'DATE_ORDER': 'MDY'})
                    except ImportError:
                        dt = None
                    except Exception:
                        dt = None

                if dt is None:
                    raise ValueError(f"Could not parse {date!r} as a date/datetime.")

        dt = _make_naive(dt)

    except Exception as e:
        if errors == 'error':
            logger.error(f"Failed to convert to datetime: {e}")
            raise e
        else:
            dt = pd.NaT

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
                    data_summary += f"**Sample**:      {', '.join(df[column].sample(10, ).fillna('<NA>').to_list())}  \n"

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