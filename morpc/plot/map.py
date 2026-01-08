class MAP:
    def __init__(self, gdf, id_col, verbose=True):
        """
        Create an interactive choropleth map from a GeoDataFrame.

        Parameters
        ----------
        gdf : geopandas.GeoDataFrame
            A GeoDataFrame containing geometries and data to visualize.

        Returns
        -------
        folium.Map
            An interactive folium map with choropleth layers for each data column.

        
        """
        
        self.MAPDATA = gdf.copy()
        self.MAP = self.define_map(id_col=id_col, verbose=verbose)

    def define_map(self, id_col, verbose=True):
        """
        Define the folium map with choropleth layers.
        
        Returns
        -------
        folium.Map
            An interactive folium map with choropleth layers for each data column.


        """
        import morpc
        import folium
        from branca.colormap import LinearColormap

        map_data = self.MAPDATA # Load the GeoDataFrame

        # Check for multilevel columns, concat if true
        if map_data.columns.nlevels > 1:
            map_data.columns = [", ".join(filter(None, x)) for x in map_data.columns]


        # Ensure the id_col is in the dataframe
        if id_col not in map_data.reset_index().columns:
            raise ValueError(f"morpc.plot.map.MAP: The specified id_col '{id_col}' is not in the GeoDataFrame columns.")
        
        # Create choropleth layers for each column except 'geometry'
        self.choros = []
        self.cmaps = []

        for i in range(len(map_data.columns)):
            if verbose:
                print(f"morpc.plot.map.MAP: Processing column {i+1} of {len(map_data.columns)} : {map_data.columns[i]}")
            column = map_data.columns[i]
            if column != 'geometry':

                # Create tooltip
                tooltip = folium.GeoJsonTooltip(
                    fields=['NAME', column]
                )
                # Create colormap
                cmap = LinearColormap(
                    colors=[morpc.color.rgb_to_dec(morpc.color.hex_to_rgb(x)) for x in morpc.palette.SEQ2['bluegreen-darkblue']],
                    vmin=map_data[column].min(),
                    vmax=map_data[column].max(),
                    caption = column
                )
                #   Create choropleth layer
                choro = folium.Choropleth(
                    geo_data=map_data.reset_index()[[id_col, column, 'geometry']],
                    data=map_data.reset_index()[[id_col, column]],
                    key_on=f'properties.{id_col}',
                    columns=[id_col, column],
                    name=column,
                    cmap=cmap,
                    fill_opacity=0.9,
                    line_opacity=0.1,
                    show=False,
                )

                choro.geojson.add_child(tooltip)

                # Remove default colormaps and add custom colormaps
                for child in choro._children:
                    if child.startswith("color_map"):
                        del choro._children[child]

                self.choros.append(choro)
                self.cmaps.append(cmap)
        if verbose:
            print("morpc.plot.map.MAP: Rendering map...")
        m = folium.Map()
        
        # Add each choropleth and its colormap to the map
        for choro, cmap in zip(self.choros, self.cmaps):
            m.add_child(cmap)

            m.add_child(choro)

            bc = BindColormap(choro, cmap)

            m.add_child(bc)

        # Add layer control and fit bounds
        folium.LayerControl(collapsed=True, position='topleft').add_to(m)
        m.fit_bounds(m.get_bounds())
        return m
    
    def explore(self):
        return self.MAP
    
    def save(self, filepath):
        self.MAP.save(filepath)


from branca.element import MacroElement
from jinja2 import Template

class BindColormap(MacroElement):
    """Binds a colormap to a given layer. For mor information, see:
    https://nbviewer.org/gist/BibMartin/f153aa957ddc5fadc64929abdee9ff2e

    Parameters
    ----------
    colormap : branca.colormap.ColorMap
        The colormap to bind.
    """

    def __init__(self, layer, colormap):
        super(BindColormap, self).__init__()
        self.layer = layer
        self.colormap = colormap
        self._template = Template(u"""
        {% macro script(this, kwargs) %}
            {{this.colormap.get_name()}}.svg[0][0].style.display = 'none';
            {{this._parent.get_name()}}.on('overlayadd', function (eventLayer) {
                if (eventLayer.layer == {{this.layer.get_name()}}) {
                    {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
                }});
            {{this._parent.get_name()}}.on('overlayremove', function (eventLayer) {
                if (eventLayer.layer == {{this.layer.get_name()}}) {
                    {{this.colormap.get_name()}}.svg[0][0].style.display = 'none';
                }});
        {% endmacro %}
        """)
