class MAP:
    def __init__(self, gdf):

        self.MAPDATA = gdf.copy()
        self.MAP = self.define_map()

    def define_map(self):
        import geopandas as gpd
        import morpc
        import numpy as np
        import folium
        from branca.colormap import LinearColormap

        map_data = self.MAPDATA

        # Check for multilevel columns, concat if true
        if map_data.columns.nlevels > 1:
            map_data.columns = [", ".join(x) for x in map_data.columns]

        self.choros = []
        self.cmaps = []
        for i in range(len(map_data.columns)):
            column = map_data.columns[i]
            if column != 'geometry':

                tooltip = folium.GeoJsonTooltip(
                    fields=['NAME', column]
                )

                cmap = LinearColormap(
                    colors=[morpc.color.rgb_to_dec(morpc.color.hex_to_rgb(x)) for x in morpc.palette.SEQ2['bluegreen-darkblue']],
                    vmin=map_data[column].min(),
                    vmax=map_data[column].max(),
                    caption = column
                )

                choro = folium.Choropleth(
                    geo_data=map_data.reset_index()[['NAME', column, 'geometry']],
                    data=map_data.reset_index()[['NAME', column]],
                    key_on='properties.NAME',
                    columns=['NAME', column],
                    name=column,
                    cmap=cmap,
                    fill_opacity=0.9,
                    line_opacity=0.1,
                    show=False,
                )
                choro.geojson.add_child(tooltip)

                for child in choro._children:
                    if child.startswith("color_map"):
                        del choro._children[child]

                self.choros.append(choro)
                self.cmaps.append(cmap)

        m = folium.Map()

        for choro, cmap in zip(self.choros, self.cmaps):
            m.add_child(cmap)

            m.add_child(choro)

            bc = BindColormap(choro, cmap)

            m.add_child(bc)

        folium.LayerControl(collapsed=True, position='topleft').add_to(m)
        m.fit_bounds(m.get_bounds())
        return m
    
    def explore(self):
        return self.MAP

from branca.element import MacroElement
from jinja2 import Template

class BindColormap(MacroElement):
    """Binds a colormap to a given layer.

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
