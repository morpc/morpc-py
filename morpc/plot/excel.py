
import logging
from types import NoneType

import xlsxwriter
import xlsxwriter.exceptions
import xlsxwriter.utility

logger = logging.getLogger(__name__)

class ExcelChart:
    _excelchart_logger = logging.getLogger(__name__).getChild(__qualname__)
    def __init__(self, df, path=None, sheetname=None, config=None):
        """
        Creates a excel document with table and chart using MORPC defaults.

        Parameters:
        -----------
        df : pandas.Dataframe
            A pandas data from with the data. Typically in wide format. The row index is used as the x axis, and the column index is used as the categories (series) in the data. 
            df.index.name is used as the x axis label, and df.columns.name is used as the legend name.

        path : str, path-like
            The path for the writer to save the xlsx workbook to.

        sheetname : str
            The sheetname for the excel workbook.

        config : dict, Optional
            A config file defining the parameters of the plot. See https://xlsxwriter.readthedocs.io/chart.html.
        """
        import xlsxwriter
        from xlsxwriter.utility import xl_rowcol_to_cell
        import pandas as pd
        import logging
        from datetime import datetime
        from pprint import pformat
        from types import NoneType

        # setup logger
        self.logger = logging.getLogger(__name__).getChild(self.__class__.__name__).getChild(str(datetime.now()))
        logging.getLogger('pandas')

        # Store data
        self.logger.debug(f"Storing data to DATA. \n{df.to_markdown()}")
        self.DATA = df   

        # If preconstructed config file passed use that.
        # NOT YET IMPLMENTED
        if config != None:
            self.logger.debug(f"Config file passed. #### NOT YET IMPLEMENTED. #### \n{pprint(config)}")
            self.CONFIG = config
        ## Construct config instance to store paramters in useful format.
        else:
            self.CONFIG = {
                'workbook': {
                    'path': path
                },
                'worksheet': {
                    'name': sheetname,
                }
            }
            self.logger.debug(f"No config passed. Building intial config from parameters. \n{pformat(self.CONFIG)}")

        self.CONFIG['worksheet'].update({
            'data': {
                'nrows': len(df.index),
                'ncols': len(df.columns),
                'topleft': (df.columns.nlevels, df.index.nlevels)
                    }
                })

        # Construct the workbook and worksheet.
        self.logger.debug(f"Writing workbook at path: {self.CONFIG['workbook']['path']} with sheet named {self.CONFIG['worksheet']['name']}")

        self.WRITER = pd.ExcelWriter(path, engine='xlsxwriter')
        df.to_excel(self.WRITER, sheet_name=sheetname, merge_cells=True)

        self.WORKBOOK = self.WRITER.book
        self.WORKSHEET = self.WRITER.sheets[sheetname]


        ## Depreciated for using pandas.Dataframe.to_excel
        # ## Use the columns.names parameter
        # if not isinstance(df.columns.name, NoneType):
        #     self.WORKSHEET.write('A1', df.columns.name)
        #     self.CONFIG['worksheet']['data'].update({'columnsname': df.columns.name})

        # for i in range(len(df.columns)):
        #     self.WORKSHEET.write(0, i+1, df.columns[i])        

        # # Write index to first column, skip first row for column names
        # if not isinstance(df.index.name, NoneType):
        #     self.WORKSHEET.write('A2', df.index.name)
        #     self.CONFIG['worksheet']['data'].update({'indexname': df.index.name})

        #     for i in range(len(df.index)):
        #         self.WORKSHEET.write(i+2, 0, df.index[i])
        #     for row in range(df.shape[0]):
        #         for column in range(df.shape[1]):
        #             self.WORKSHEET.write(row+2, column+1, df.iat[row, column])
        # else:
        #     for i in range(len(df.index)):
        #         self.WORKSHEET.write(i+1, 0, df.index[i])
        #     for row in range(df.shape[0]):
        #         for column in range(df.shape[1]):
        #             self.WORKSHEET.write(row+1, column+1, df.iat[row, column])
    
    def write(self, autofit=True):
        """
        Writes and closes the workbook
        """
        if autofit:
            self.logger.debug(f"Autofittting columns.")
            self.WORKSHEET.autofit()

        self.logger.debug(f"Writing workbook to {self.CONFIG['workbook']['path']}")
        try:
            self.WORKBOOK.close()
        except Exception as e:
            self.logger.error(f"Write Error: {e}, Is the workbook open in excel?.")
            raise RuntimeError
    
    def add_chart(self, type, subtype=None, title=None, y_label=None, x_label=None, series=None, data_labels=None):
        """
        Add a chart to the worksheet.

        Parameters
        ----------
        type : {'area', 'bar', 'column', 'doughnut', 'line', 'pie', 'radar', 'scatter', 'stock'}
            The type of chart to add to the 
        subtype : _str, optional
            Set the subtype of the chart, by default None. See https://xlsxwriter.readthedocs.io/chart.html#the-chart-class
        title : str, optional
            Name of chart and used as title, by default None
        series : list of str, optional
            A list of the variables in index to use in the series of the chart. Does not filter table, just the chart. Defaults to None which shows all variables.
        data_lables : {'center', 'above', 'outside_end', None}
            defaults None, center is used for all charts, Above for more line, and outside_end for column.
        """            
        from morpc.color.colors import GetColors, overlay_color

        if type not in {'area', 'bar', 'column', 'line', 'scatter'}:
            logger.error(f"{type} not a valid or implemented chart type.")
            raise RuntimeError

        if 'chart' not in self.CONFIG:
        # Add chart to config
            self.CONFIG.update(
                {"chart":
                 {'type': type}
                })

            # if there is a subtype add that too
            if subtype != None:
                self.CONFIG['chart'].update({'subtype': subtype})

        logger.debug(f"Setting up chart with type {type}, subtype {subtype}, and name {title}")

        # add some default values to chart config
        self.CONFIG['chart'].update({
            'legend': {'position': 'bottom'},
            'y_axis': {'major_gridlines': {'visible': False}},
            'x_axis': {'major_gridlines': {'visible': False}},
            'gap': 20
            })
        
        if title != None:
            self.CONFIG['chart'].update({'title':{'name':title,
                                                  'font': {'size': 11}}})
        
        if y_label != None:
            self.CONFIG['chart']['y_axis'].update({'name': y_label})
        
        if x_label != None:
            self.CONFIG['chart']['x_axis'].update({'name': x_label})
        # create the chart object

        self.CHART = self.WORKBOOK.add_chart(self.CONFIG['chart'])
    
        self.CHART.set_legend(self.CONFIG['chart']['legend'])
        self.CHART.set_y_axis(self.CONFIG['chart']['y_axis'])
        self.CHART.set_x_axis(self.CONFIG['chart']['x_axis'])
        self.CHART.set_title(self.CONFIG['chart']['title'])

        # update series tp all variables if not defined
        if series == None:
            series = [str(x[-1]) if isinstance(x, tuple) else str(x) for x in self.DATA.index]
            logger.debug(f"No series parameter, using all variable as series: {series}")
        else:
            logger.debug(f"Series parameter defined, using following variable as series: {series}")

        colors = GetColors().QUAL().hex_list[0:len(series)]
        self.CONFIG['chart'].update({'colors': colors})
        logger.debug(f"added colors {colors} to config")

        # Add the columns as series
        self.CONFIG['chart'].update({'series': []})
        series_added = 0
        for i in range(self.CONFIG['worksheet']['data']['nrows']):
            # Add to config
            if [str(x) for x in self.DATA.index][i] in series:
                logger.debug(f"Adding {[x for x in self.DATA.index][i]} to series config")
                self.CONFIG['chart']['series'].append({
                        'name': [str(x) for x in self.DATA.index][i],
                        'categories': [
                            self.CONFIG['worksheet']['name'], # Sheet name
                            self.CONFIG['worksheet']['data']['topleft'][0] - 1, # first row
                            self.CONFIG['worksheet']['data']['topleft'][1], # first column
                            self.CONFIG['worksheet']['data']['topleft'][0] - 1, # last row
                            self.CONFIG['worksheet']['data']['topleft'][1] + self.CONFIG['worksheet']['data']['ncols'] - 1, # last column
                        ],
                        'values': [
                            self.CONFIG['worksheet']['name'], # Sheet name
                            self.CONFIG['worksheet']['data']['topleft'][0] + i , # first row
                            self.CONFIG['worksheet']['data']['topleft'][1], # first column
                            self.CONFIG['worksheet']['data']['topleft'][0] + i, # last row
                            self.CONFIG['worksheet']['data']['topleft'][1] + self.CONFIG['worksheet']['data']['ncols'] - 1, # last column                    
                            ]
                        }
                    )
                
        # for each series add colors and data labels
        for i in range(len(self.CONFIG['chart']['series'])):
            color = self.CONFIG['chart']['colors'][i]
            logger.debug(f"assigning color {color} to {self.CONFIG['chart']['series'][i]['name']}")
            # Add color to series
            if self.CONFIG['chart']['type'] == 'column':
                self.CONFIG['chart']['series'][i].update(
                    {'fill': {'color': color},
                    'border': {'none': True}}
                    )
            if self.CONFIG['chart']['type'] == 'bar':
                self.CONFIG['chart']['series'][i].update(
                    {'fill': {'color': color},
                    'border': {'none': True}}
                    )
            if self.CONFIG['chart']['type'] == 'line':
                self.CONFIG['chart']['series'][i].update(
                    {'line': color,
                    'marker': {
                        'fill': {'color': color},
                        'border': {'none':True},
                        'type': 'circle',
                        'size': 5
                                }}
                    )
            if self.CONFIG['chart']['type'] == 'scatter':
                self.CONFIG['chart']['series'][i].update(
                    {'marker': {
                        'fill': {'color': color},
                        'border': {'none':True},
                        'type': 'circle',
                        'size': 5
                    }}
                    )
            if self.CONFIG['chart']['type'] == 'area':
                self.CONFIG['chart']['series'][i].update(
                    {'fill': {'color': color},
                    'border': {'none': True}}
                        )
        
            if data_labels != None:
                self.CONFIG['chart']['series'][i].update({
                    'data_labels': {
                        'value': True,
                        'position': data_labels,
                        'font': {'color': color if data_labels != 'center' else overlay_color([color])[0]}

                    }
                })

            self.CONFIG['chart']['series'][i].update(
                {'gap': 20})


        for series in self.CONFIG['chart']['series']:
            # add from config to the chart object
            self.CHART.add_series(series)

            
        self.WORKSHEET.insert_chart(row=self.CONFIG['worksheet']['data']['nrows']+self.CONFIG['worksheet']['data']['topleft'][0]+1, col=0, chart=self.CHART)

        return self

def recursiveUpdate(original, updates):
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(original.get(key), dict):
            original[key] = recursiveUpdate(original[key], value)
        else:
            original[key] = value
    return original

def data_chart_to_excel(df, writer, sheet_name="Sheet1", chartType="column", dataOptions=None, chartOptions=None):
    """
    Create an Excel worksheet consisting of the contents of a pandas dataframe (as a formatted table)
    and, optionally, a chart to visualize the series included in the dataframe.  The simplest invocation
    will produce a table and a basic column (vertical bar) chart with default formatting that is consistent
    with MORPC branding guidelines, however the user can specify many of options supported by the xlsxwriter library 
    (https://xlsxwriter.readthedocs.io/).

    Example usage:
        import pandas as pd
        import xlsxwriter
        d = {'col1': [1, 2, 3, 4], 'col2':[3, 4, 5, 6]}
        df = pd.DataFrame(data=d)
        writer = pd.ExcelWriter("./foo.xlsx", engine='xlsxwriter')
        # Simplest invocation. Creates table and column chart on Sheet1 worksheet with default presentation settings.
        morpc.data_chart_to_excel(df, writer)  
        # Creates a table and line chart on the "LineChart" worksheet with default presentation settings.
        morpc.data_chart_to_excel(df, writer, sheet_name="LineChart", chartType="line")
        # Creates a table and stacked column chart on the "Stacked" worksheet with default presentation settings.
        morpc.data_chart_to_excel(df, writer, sheet_name="Stacked", chartType="column", chartOptions={"subtype":"stacked"})
        # Creates a table and bar chart on the "Custom" worksheet with some custom presentation settings.
        morpc.data_chart_to_excel(df, writer, sheet_name="Custom", chartType="bar", chartOptions={
            "colors": ["cyan","magenta"],                   # Specify a custom color
            "hideLegend": True,                             # Hide the legend
            "titles": {                                     # Specify the chart title and axis titles
                "chartTitle": "My Chart",
                "xTitle": "My independent variable",
                "yTitle": "My dependent variable",
            }
        })
        writer.close()
                
    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        The pandas dataframe which contains the data to export.  The dataframe column index will be used as the
        column headers (i.e. the first row) in the output table.  By default, the dataframe row index will become
        the first column in the output table (this can be overridden using the dataOptions argument).  The columns
        in the dataframe will become series in the chart.
    writer : pandas.io.excel._xlsxwriter.XlsxWriter
        An existing xlsxwriter object created using pd.ExcelWriter(..., engine='xlsxwriter'). This represents the
        Excel workbook to which the data and chart will be written. See https://xlsxwriter.readthedocs.io/working_with_pandas.html
    sheet_name : str, optional
        The label for a new worksheet that will be created in the Excel workbook.  Must be unique and cannot exist
        already.  Default value is "Sheet1"
    chartType : str, optional
        A chart type as recognized by xlsxwriter workbook.add_chart. Options include "area", "bar", "column", "doughnut", 
        "line", "pie","radar","scatter","stock". Default is "column". Set to "omit" to omit the chart and include only the
        data table.  Bar and line charts are well-supported. Results with other types may vary. See
        https://xlsxwriter.readthedocs.io/workbook.html#add_chart
    dataOptions: dict, optional
        Various configuration options for the output data table. Currently the following options are supported.
            "index": bool
                Whether to write the index as a column in the Excel file.  Default is True. Set to False to omit the index.
            "numberFormat" : str, list, or dict
                Excel number format string to use for the values in the output table. 
                If a string, the same format will be applied to all columns.
                If a list, the listed formats will be applied to the columns in sequence.  
                If a dict, the dict keys must match the column names and the dict values will contain the format
                    string to use for the column.
                Default is "#,##0.0".  See https://xlsxwriter.readthedocs.io/format.html#set_num_format
            "columnWidth" : int, list, or dict
                Widths of columns in output table. 
                If an int, the same width will be applied to all columns.
                If a list, the listed widths will be applied to the columns in sequence.  
                If a dict, the dict keys must match the column names and the dict values will contain the width
                    to use for the column.            
                Default is 12.  
    chartOptions: dict, optional
        Various configuration options for the output chart. Currently the following options are supported.
            "colors" : str, list, or dict
                Simplified method of specifying the color or color to use for the series in the chart.  Will be 
                overridden by series-specific options in chartOptions["seriesOptions"]. By default will cycle
                through MORPC brand colors.
                If a string, the same color will be used for all series. 
                If a list, the listed colors will be repeated in sequence. 
                If a dict, the dict keys must match the series names and the dict values will determine the colors
                for the corresponding series.
            "hideLegend" : bool
                Simplified method of hiding the legend, which is shown by default.  Set hideLegend = True to hide the
                legend. Will be overridden by settings in chartOptions["legendOptions"].
            "titles" : str or dict
                Simplified method of specifying the chart and axis titles.  Will be overridden by settings in 
                chartOptions["titleOptions"]. 
                If a string, it will be used as the chart title. 
                If a dict, it should have the following form. If any key/value is unspecified, it will default to the
                values shown below.
                    {
                        "chartTitle": sheet_name,
                        "xTitle": df.index.name,
                        "yTitle": df.columns.name
                    }
            "labelOptions" : dict or list of dicts,
                Simplified method of specifying data labels.  Will be overidden by settings in seriesOptions.
                If a dict, the same settings will be applied to all series
                If a list of dicts, the dict keys must match the series names and the dict values will determine the
                settings for the labels for the corresponding series.
                The dict will be used as the data_labels argument for chart.add_series().  See 
                https://xlsxwriter.readthedocs.io/chart.html#chart-add-series and
                https://xlsxwriter.readthedocs.io/working_with_charts.html#chart-series-option-data-labels
            "subtype" : str
                The desired subtype of the specified chartType, as recognized by workbook.add_chart(). Your mileage may
                vary. Some subtypes may not be well supported yet. If unspecified, this will default to whatever default
                xlsxwriter uses for the specified chartType.
                See https://xlsxwriter.readthedocs.io/workbook.html#workbook-add-chart
            "location" : list or str        
                Coordinates specifying where to place the chart on the worksheet.  Default location is to the right of table in
                the first row.  Specify "below" as shorthand to place the chart below the table in the first column.
                Used by worksheet.insert_chart( ). See https://xlsxwriter.readthedocs.io/worksheet.html#worksheet-insert-chart 
                and https://xlsxwriter.readthedocs.io/working_with_cell_notation.html#cell-notation
            "sizeOptions" : dict
                Options to control the size of the chart.  Will be used directly by chart.set_size(). Defaults to xlsxwriter
                defaults. See https://xlsxwriter.readthedocs.io/chart.html#chart-set-size       
            "plotAreaLayout" : dict
                Settings to control the layout of the plot area within the chart.  Will be used directly by chart.set_plotarea().
                Defaults to xlsxwriter defaults.  See https://xlsxwriter.readthedocs.io/working_with_charts.html#chart-layout
            "titleOptions" : dict
                Options to control the appearance of the chart title.  Will be used directly by chart.set_title(). Title text
                defaults to sheet_name. Style defaults to MORPC branding.
                See https://xlsxwriter.readthedocs.io/chart.html#chart-set-title
            "seriesOptions" : dict of dicts or list of dicts
                Options to control how series are displayed.  Used directly by chart.add_series().
                If a dict of dicts, the top level keys must correspond to the column names and the values will be applied to the
                corresponding series. If a key/value is not present for a column name, that series will revert to default settings.
                If a list of dicts, the dicts will be applied to the columns in sequence.
                corresponding series. If there are not enough items in the list for all of the columns, the remaining series will 
                revert to default settings.
                See https://xlsxwriter.readthedocs.io/chart.html#chart-add-series
            "xAxisOptions": dict
                Options to control the appearance of the x axis.  Will be used directly by chart.set_x_axis(). Axis title defaults 
                to df.index.name. Style defaults to MORPC branding. Title will be overridden by "titles" parameter (see above). See 
                https://xlsxwriter.readthedocs.io/chart.html#chart-set-x-axis
            "yAxisOptions": dict
                Options to control the appearance of the y axis.  Will be used directly by chart.set_y_axis(). Axis title defaults 
                to df.columns.name. Style defaults to MORPC branding. Title will be overridden by "titles" parameter (see above). See https://xlsxwriter.readthedocs.io/chart.html#chart-set-y-axis
            "legendOptions": dict
                Options to control the appearance of the legend. Will be used directly by chart.set_legend(). Legend is displayed by
                default and positioned at the bottom of the chart.  Style defaults to MORPC branding. See
                https://xlsxwriter.readthedocs.io/chart.html#chart-set-legend
    
    Returns
    -------
    None
    
    """

    import pandas as pd
    import json
    import xlsxwriter
    from morpc.color.colors import GetColors, overlay_color

    axisSwapTypes = ["bar"]

    colorsDefault = GetColors().QUAL().hex_list

    styleDefaults = {
        "fontName": "Arial",
        "fontSize": 10,
        "titleFontSize": 14,
        "axisNameFontSize": 9,
        "axisNumFontSize": 8,
        "legendFontSize": 10,
        "seriesColor": colorsDefault[0],
        "numberFormat": "#,##0.0",
        "columnWidth": 12
    }

    titleDefaults = {
        "chartTitle": sheet_name,
        "xTitle": df.index.name,
        "yTitle": df.columns.name
    }

    titleOptionsDefaults = {
        "name": titleDefaults["chartTitle"],
        "overlay": False,
        "name_font": {
            "name": styleDefaults["fontName"],
            "size": styleDefaults["titleFontSize"]
        }
    }

    axisOptionsDefaults = {
        "name_font": {
            "name": styleDefaults["fontName"],
            "size": styleDefaults["axisNameFontSize"]
        },
        "num_font": {
            "name": styleDefaults["fontName"],
            "size": styleDefaults["axisNumFontSize"]
        },
        "label_position": 'low',
        "reverse": False
    }


    xAxisOptionsDefaults = json.loads(json.dumps(axisOptionsDefaults))
    xAxisOptionsDefaults["name"] = titleDefaults["xTitle"]

    yAxisOptionsDefaults = json.loads(json.dumps(axisOptionsDefaults))
    yAxisOptionsDefaults["name"] = titleDefaults["yTitle"]

    legendOptionsDefaults = {
        "none": False,
        "position": "bottom",
        "font": {
            "name": styleDefaults["fontName"],
            "size": styleDefaults["legendFontSize"]
        }
    }

    seriesOptionsDefault = {
        "common": {
        }
    }

    seriesOptionsDefault["bar"] = json.loads(json.dumps(seriesOptionsDefault["common"]))
    seriesOptionsDefault["bar"] = recursiveUpdate(seriesOptionsDefault["bar"], {
        "border": {"none":True},
        "fill": {
            "color": styleDefaults["seriesColor"]
        }
    })
    seriesOptionsDefault["column"] = json.loads(json.dumps(seriesOptionsDefault["bar"]))

    seriesOptionsDefault["line"] = json.loads(json.dumps(seriesOptionsDefault["common"]))
    seriesOptionsDefault["line"] = recursiveUpdate(seriesOptionsDefault["line"], {
        "line": {
            "color": styleDefaults["seriesColor"],
            "width": 2.5          
        },
        "marker": {
            "type": "circle",
            "size": 5,
            "border": {"none":True},
            "fill": {
                "color": styleDefaults["seriesColor"]
            }
        },
        "smooth": False
    })

    subtypesDefaults = {
        "bar": None,
        "column": None,
        "line": None
    }

    myDataOptions = {
        "index": True,               # Write the index to the Excel file by default
        # String, list, or dict. If a string, the same format will be applied to all columns.  If a 
        # list, the listed formats will be applied to the columns in sequence.  If a dict, the keys must 
        # match the columns names and the values will format for each.
        "numberFormat": styleDefaults["numberFormat"],
        "columnWidth": styleDefaults["columnWidth"]
    }
    if(dataOptions != None):
        myDataOptions = recursiveUpdate(myDataOptions, dataOptions)

    myChartOptions = {
        # String, list, or dict.  Simplified method of specifying series colors. Overridden by setting in 
        # chartOptions["seriesOptions"]. If a string, the same color will be used for all series. If a 
        # list, the listed colors will be repeated in sequence. If a dict, the keys must match the series 
        # names and the values will determine the colors.
        "colors": None,
        # Bool. Simplified method of hiding the legend. Overridden by setting in chartOptions["legendOptions"]
        "hideLegend": False,
        # String or dict. Simplified method of specifying the chart and axis titles.  Overridden by setting in chartOptions["titleOptions"]. If a string, it will be used as the chart title. If a dict, it will have the same format as titleDefaults
        "titles": None,
        # Dict to be applied to all series or list of dicts, one per series. Simplified method of specifying data labels.  
        # Used by chart.add_series()
        "labelOptions": None,
        "subtype": None,          # String. Defer to chart-specific default. Used by workbook.add_chart()
        "location": None,         # List. Default location is to the right of data. Will be determined later.
        "sizeOptions": None,      # Dict. Will be used by chart.set_size()
        "plotAreaOptions": None,   # Dict. Will be used by chart.set_plotarea()
        "titleOptions": None,     # Dict. Will be used by chart.set_title()
        "seriesOptions": None,    # Dict to be applied to all series or list of dicts, one per series. Used by chart.add_series()
        "xAxisOptions": None,     # Dict. Will be used by chart.set_x_axis()
        "yAxisOptions": None,     # Dict. Will be used by chart.set_y_axis()
        "legendOptions": None,    # Dict. Will be used by chart.set_legend()
        "includeColumns": None    # List of columns to be added as series to chart.   
    }
    if(chartOptions != None):
        myChartOptions = recursiveUpdate(myChartOptions, chartOptions)

    myLegendOptions = json.loads(json.dumps(legendOptionsDefaults))
    if(myChartOptions["hideLegend"] == True):
        myLegendOptions["none"] = True
    if(myChartOptions["legendOptions"] != None):
        myLegendOptions = recursiveUpdate(myLegendOptions, chartOptions["legendOptions"])

    if(myChartOptions["includeColumns"] == None):
        myChartOptions["includeColumns"] = list(df.columns)

    workbook = writer.book

    df.to_excel(writer, sheet_name=sheet_name, index=myDataOptions["index"])

    worksheet = writer.sheets[sheet_name]

    if(type(myDataOptions["numberFormat"]) == str):
        numberFormats = workbook.add_format({'num_format': myDataOptions["numberFormat"]})
    elif(type(myDataOptions["numberFormat"]) == list):
        numberFormats = [workbook.add_format({'num_format': value}) for value in myDataOptions["numberFormat"]] 
    elif(type(myDataOptions["numberFormat"]) == dict):
        numberFormats = {key: workbook.add_format({'num_format': value}) for key, value in zip(myDataOptions["numberFormat"].keys(), myDataOptions["numberFormat"].values())}

    columnWidths = json.loads(json.dumps(myDataOptions["columnWidth"]))

    if(myDataOptions["index"] == True):
        indexName = df.index.name
        if(indexName == None):
            indexName = "index"
        df = df.reset_index()
    nRows = df.shape[0]
    nColumns = df.shape[1]
    for i in range(0, nColumns):
        colname = df.columns[i]

        if(type(numberFormats) == xlsxwriter.format.Format):
            columnNumberFormat = numberFormats
        elif(type(numberFormats) == list):
            try:
                columnNumberFormat = numberFormats[i]
            except:
                print(f"WARNING: Number format not specified for column {i} (column {colname}). Using default.")
                columnNumberFormat = styleDefaults["numberFormat"]
        elif(type(numberFormats) == dict):
            try:
                columnNumberFormat = numberFormats[colname]
            except:
                print(f"WARNING: Number format not specified for column {colname}). Using default.")
                columnNumberFormat = styleDefaults["numberFormat"]

        if(type(columnWidths) == int):
            columnWidth = columnWidths
        elif(type(columnWidths) == list):
            try:
                columnWidth = columnWidths[i]
            except:
                print(f"WARNING: Column width not specified for column {i} (column {colname}). Using default.")
                columnWidth = styleDefaults["columnWidth"]
        elif(type(columnWidths) == dict):
            try:
                columnWidth = columnWidths[colname]
            except:
                print(f"WARNING: Column width not specified for column {colname}). Using default.")
                columnWidth = styleDefaults["columnWidth"]

        worksheet.set_column(i, i, columnWidth, columnNumberFormat)

    if(myDataOptions["index"] == True):
        df = df.set_index(indexName)

    if(chartType == "omit"):
        print("WARNING: Chart type is set to omit.  Chart will be omitted.")
        return


    chart = workbook.add_chart({
        "type": chartType, 
        "subtype": (myChartOptions["subtype"] if myChartOptions["subtype"] != None else subtypesDefaults[chartType])
    })

    nRows = df.shape[0]
    nColumns = len(myChartOptions["includeColumns"])
    for i in range(1, nColumns+1):
        colname = myChartOptions["includeColumns"][i-1]
        # Get the position of this column in the worksheet.  It may not match the value of i because of columns omitted by the user. 
        colpos = list(df.columns).index(colname) + 1

        mySeriesOptions = json.loads(json.dumps(seriesOptionsDefault[chartType]))

        color = None
        # If the user specified a color or set of colors in chartOptions["colors"], use those instead of the defaults.
        if(myChartOptions["colors"] != None):
            if(type(myChartOptions["colors"]) == str):
                color = myChartOptions["colors"]
            elif(type(myChartOptions["colors"]) == list):
                color = myChartOptions["colors"][(i-1) % len(myChartOptions["colors"])]        
            elif(type(myChartOptions["colors"]) == dict):
                color = myChartOptions["colors"].get(colname, styleDefaults["seriesColor"])   # Revert to default if color is not specified for column
            json.dumps(mySeriesOptions, indent=4)
        # Else if we have more than one series, cycle through the default set of colors
        elif(nColumns > 1):
            color = colorsDefault[(i-1) % len(colorsDefault)]
        # Else, simply stick with the single default color defined above in seriesOptionsDefault

        if(color != None):
            if "fill" in mySeriesOptions.keys():
                mySeriesOptions["fill"]["color"] = color
            if "line" in mySeriesOptions.keys():
                mySeriesOptions["line"]["color"] = color
            if "marker" in mySeriesOptions.keys():                
                mySeriesOptions["marker"]["fill"]["color"] = color
            if "labels" in mySeriesOptions.keys():
                mySeriesOptions["labels"]["fill"]["color"] = '#ffffff'

        if(type(myChartOptions["seriesOptions"]) == list):
            try:
                mySeriesOptions = recursiveUpdate(mySeriesOptions, myChartOptions["seriesOptions"][i-1])
            except Exception as e:
                print(f"WARNING: Failed to get chartOptions['seriesOptions'] for list item {i-1} (column {colname}). Using defaults.") 
        elif(type(myChartOptions["seriesOptions"]) == dict):
            try:
                mySeriesOptions = recursiveUpdate(mySeriesOptions, myChartOptions["seriesOptions"][colname])
            except Exception as e:
                print(f"WARNING: Failed to get chartOptions['seriesOptions'] for column {colname}). Using defaults.") 

        mySeriesOptions["name"] = [sheet_name, 0, colpos]
        mySeriesOptions["categories"] = [sheet_name, 1, 0, nRows, 0]
        mySeriesOptions["values"] = [sheet_name, 1, colpos, nRows, colpos]

        # Configure chart title
        # Start with default values
        myTitleOptions = json.loads(json.dumps(titleOptionsDefaults))
        # If user provided a dict of title options, update the default values with provided values
        if(myChartOptions["titleOptions"] != None):
            myTitleOptions = recursiveUpdate(myTitleOptions, myChartOptions["titleOptions"])
        # Otherwise, if user provided only the chart title as a string using the simplified form, override the default string
        elif(type(myChartOptions["titles"]) == str):
            myTitleOptions["name"] = myChartOptions["titles"]
        # Otherwise, if user provided a simplified dict of chart titles and axis titles, try to use the provided chart title. If
        # the chart title was not provided in the dict, revert to the default. 
        elif(type(myChartOptions["titles"]) == dict):
            myTitleOptions["name"] = myChartOptions["titles"].get("chartTitle", titleOptionsDefaults["name"])

        # Configure the x-axis
        # Start with default values
        myXAxisOptions = json.loads(json.dumps(xAxisOptionsDefaults))
        # If user provided a dict of x-axis options, update the default values with provided values
        if(myChartOptions["xAxisOptions"] != None):
            myXAxisOptions = recursiveUpdate(myXAxisOptions, myChartOptions["xAxisOptions"])
        # Otherwise, if user provided a simplified dict of chart titles and axis titles, try to use the provided x-axis title. If
        # the x-axis title was not provided in the dict, revert to the default. 
        if(type(myChartOptions["titles"]) == dict):
            myXAxisOptions["name"] = myChartOptions["titles"].get("xTitle", xAxisOptionsDefaults["name"])

        # Configure the y-axis
        # Start with default values
        myYAxisOptions = json.loads(json.dumps(yAxisOptionsDefaults))
        # If user provided a dict of y-axis options, update the default values with provided values
        if(myChartOptions["yAxisOptions"] != None):
            myYAxisOptions = recursiveUpdate(myYAxisOptions, myChartOptions["yAxisOptions"])
        # Otherwise, if user provided a simplified dict of chart titles and axis titles, try to use the provided y-axis title. If
        # the y-axis title was not provided in the dict, revert to the default. 
        if(type(myChartOptions["titles"]) == dict):
            myYAxisOptions["name"] = myChartOptions["titles"].get("yTitle", yAxisOptionsDefaults["name"])

        chart.add_series(mySeriesOptions)

    if(chartType in axisSwapTypes):
        tempX = myXAxisOptions["name"]
        tempY = myYAxisOptions["name"]
        myXAxisOptions["name"] = tempY
        myYAxisOptions["name"] = tempX

    chart.set_title(myTitleOptions)
    chart.set_x_axis(myXAxisOptions)
    chart.set_y_axis(myYAxisOptions)        
    chart.set_legend(myLegendOptions)   
    # If the user specified chart size options, use them as-is. There are 
    # no defaults for this.
    if(myChartOptions["sizeOptions"] != None):
            chart.set_size(myChartOptions["sizeOptions"])
    # If the user specified a plot area layout, use it as-is. There are 
    # no defaults for this.
    if(myChartOptions["plotAreaOptions"] != None):
        chart.set_plotarea(myChartOptions["plotAreaOptions"])

    if(myChartOptions['location'] == "below"):
        # If the user specifies "below", put the chart below the table in the first column
        myLocation = [worksheet.dim_rowmax+2, 0]
    elif(myChartOptions['location'] != None):
        # If the user specified the location in some other way, use their specification as-is
        myLocation = myChartOptions['location']
    else:
        # Otherwise, if the user did not specify the location, then put the chart to the right of the table in the first row
        myLocation = [0, worksheet.dim_colmax+2]

    if(type(myLocation) == list):
        worksheet.insert_chart(myLocation[0], myLocation[1], chart)
    elif(type(myLocation) == str):
        worksheet.insert_chart(myLocation, chart)
    else:
        print('ERROR: Chart location must be specified in list form as [row,col] or as a cell reference string like "A5"')
        raise RuntimeError
    
    return worksheet
