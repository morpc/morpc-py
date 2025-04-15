
class scatter_plot:

    def __init__(self, data, x, y, color = None):
        """
        Create an altair scatter plot, defaulting to MORPC standards.

        Parameters:
        -----------
        data : pd.Dataframe, dict, or str
            A dataframe, dictionary, or string (path) to identify the data to plot. 
        x : str
            The column in the data that represents the x variable.
        y : str
            The column in that dat that represents the y variable
        """

        self.define_data(data)
        self.define_x(x)
        self.define_y(y)
    
        if color:
            self.define_color(columnname=color)

        self.define_chart()

    def define_data(self, data):
        """Define the data"""
        import pandas as pd

        try:
            if isinstance(data, pd.DataFrame):
                self.data = data
            if isinstance(data, dict):
                self.data = pd.DataFrame.from_dict(data)
            if isinstance(data, str):
                if data.endswith('.csv'):
                    self.data = pd.read_csv(data)
                if data.endswith('.json'):
                    self.data = pd.read_json(data)
                if data.endswith('.xlsx'):
                    self.data = pd.read_excel(data)
        except:
            print("Unable to read data. Must be Dataframe, dict, or location of csv, json, or excel file")
            raise RuntimeError

    def define_x(self, columnname):
        """Define the x variable"""
        if columnname in self.data.columns:
            self.x = f"{columnname}:Q"
        else:
            print(f"{columnname}, not in data")
            raise KeyError
            

    def define_y(self, columnname):
        """Define the y variable"""
        if columnname in self.data.columns:
            self.y = f"{columnname}:Q"
        else:
            print(f"{columnname}, not in data")
            raise KeyError
    
    def define_color(self, columnname):
        """Define the color variable"""

        from morpc import CONST_MORPC_COLORS
        from math import ceil

        if columnname in self.data.columns:
            self.color_column = columnname
        else:
            print(f"{columnname}, not in data")
            raise KeyError
        
        if columnname in self.data.columns:
            try:
                self.__colordomain__ = self.data[columnname].unique()
                n = len(self.__colordomain__)
                colors = [x for x in CONST_MORPC_COLORS.values()]
                reps = ceil(n / len(colors))
                pal = [color for color in CONST_MORPC_COLORS.values()]*reps
                pal = pal[:n]
                self.__colorrange__ = pal
            except:
                print("unable to solve color palatte")
                raise RuntimeError
        else:
            print(f"{columnname}, not in data")
            raise KeyError
            

    def define_chart(self):
        import altair as alt
        """Create the chart"""

        self.chart = alt.Chart(self.data).mark_point().encode(
            x = self.x,
            y = self.y,
            color = alt.Color(self.color_column).scale(domain = self.__colordomain__, range = self.__colorrange__)
        )

    def plot(self):
        """Display plot"""
        return self.chart
    
    def jupyter_plot(self):
        """Plot in jupyter"""
        import altair
        return altair.JupyterChart(self.chart)




