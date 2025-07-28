import plotnine as pn

morpc_theme = (pn.theme_classic() +
                pn.theme(
                  strip_background=pn.element_blank(),
                  strip_text=pn.element_text(weight='bold'),
                  axis_title=pn.element_text(weight='bold'),
                  plot_title = pn.element_text(weight='bold', size=12, linespacing = 1.3, ma='center', ha = 'center'),
                  plot_caption = pn.element_text(weight='normal', size=7, ha='left')
                )
            )

class from_resource:
    def __init__(self, data, resource, schema, x, y):
        """
        Plot data stored in a frictionless resource with reasonable values. 

        Parameters:
        -----------
        data : pandas.DataFrame
            long form dataframe
        resource : json
            frictionless.resource
        schema : json
            frictionless.schema

        Returns:
        --------
        pn.ggplot.ggplot
            Plot of data
        """

        self.data = data
        self.schema = schema
        self.resource = resource
        self.theme = morpc_theme

        self.x = self.schema.get_field(x)
        self.y = self.schema.get_field(y)

    def get_xaxis(self):
        import numpy as np

        if self.x.type == 'string':
            _xscale = pn.scale_x_discrete(name=self.x.title)

        if self.x.type in ['number', 'integer']:
            lower = self.data[self.x.name].min()
            upper = self.data[self.x.name].max()
            base = (10**(len(str(upper))-2))*5
            upper = base * round(upper/base)
            breaks = range(lower//base*base, upper, base)
            breaks = [x for x in breaks] + [upper]
            breaks.sort()

            _xscale = pn.scale_x_continuous(name = self.x.title, breaks=breaks)

        if self.x.type == 'date':
            import mizani
            from datetime.datetime import timedelta
            diff = self.data[self.x.name].max() - self.data[self.x.name].min()
            if diff < timedelta(10):
                breaks = mizani.breaks.breaks_date(width = "1 year")
            if diff >= 10:
                breaks = mizani.breaks.breaks_date(width = "5 years")
            if diff >= 100:
                breaks = mizani.breaks.breaks_date(width = "10 years")

            _xscale = pn.scale_x_date(name=self.x.title, breaks=breaks)

        max_len_label = max([len(str(label)) for label in self.data[self.x.name]])
        if max_len_label > 3:
            self.theme = self.theme + pn.theme(axis_text_x=pn.element_text(rotation=90))

        return _xscale

    def get_yaxis(self):
        import numpy as np

        if self.y.type == 'string':
            _yscale = pn.scale_y_discrete(name=self.y.title)

        if self.y.type in ['number', 'integer']:
            lower = self.data[self.y.name].min()
            upper = self.data[self.y.name].max()
            base = (10**(len(str(upper))-2))*5
            upper = base * round(upper/base)
            breaks = range(lower//base*base, upper, base)
            breaks = [x for x in breaks] + [upper]
            breaks.sort()

            _yscale = pn.scale_y_continuous(name = self.y.title, breaks=breaks)

        if self.y.type == 'date':
            import mizani
            diff = self.data[self.y.name].max() - self.data[self.y.name].min()
            if diff < 10:
                breaks = mizani.breaks.breaks_date(width = "1 year")
            if diff >= 10:
                breaks = mizani.breaks.breaks_date(width = "5 years")
            if diff >= 100:
                breaks = mizani.breaks.breaks_date(width = "10 years")

            _yscale = pn.scale_y_date(name=self.y.title, breaks=breaks)

        return _yscale

    def hbar(self):
        import plotnine

        self.geom = (pn.geom_col(
            data=self.data,
            mapping=pn.aes(
                x=self.x.name,
                y=self.y.name
                )
            )
                    )
        self.coord = pn.coord_flip()

        return self

    def show(self):
        import textwrap
        return (pn.ggplot()
                + self.geom
                + self.get_xaxis()
                + self.get_yaxis()
                + self.coord
                + self.theme
                + pn.labs(title='\n'.join(textwrap.wrap(self.resource.title, width=60))))

    def save(self, path, dpi = 100, adjust_size=False):
        from plotnine import ggsave
        if adjust_size:
            ggsave(self.plot, path = path, dpi = dpi, width=adjust_size[0], height=adjust_size[1])
        else:
            ggsave(self.plot, path = path, dpi = dpi)