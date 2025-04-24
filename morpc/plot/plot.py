import plotnine as pn


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
        self.x = self.schema.get_field(x)
        self.y = self.schema.get_field(y)

        self.plot = (pn.ggplot()
                     + pn.theme_bw())
        self.title = resource.title
        self.xscale = self.get_xaxis()
        self.yscale = self.get_yaxis()

    def get_xaxis(self):
        import numpy as np

        if self.x.type == 'string':
            _xscale = pn.scale_x_discrete(name=self.x.title)

        if self.x.type.isin(['number', 'integer']):
            lower = self.data[self.x.name].min()
            upper = self.data[self.x.name].max()
            base = (10**(len(str(upper))-2))*5
            breaks = np.linspace(lower//base*base, upper//base*base, 12, dtype=int)
            breaks = list(set([x // base * base for x in breaks]))
            breaks.sort()

            _xscale = pn.scale_x_continuous(name = self.x.title, breaks=breaks)

        if self.x.type == 'date':
            import mizani
            if self.data[self.x.name].abs().sum() < 10:
                breaks = mizani.breaks.breaks_date(width = "1 year")
            if self.data[self.x.name].abs().sum() >= 10:
                breaks = mizani.breaks.breaks_date(width = "5 years")
            if self.data[self.x.name].abs().sum() >= 100:
                breaks = mizani.breaks.breaks_date(width = "10 years")

            _xscale = pn.scale_x_date(name=self.x.title, breaks=breaks)

        max_len_label = [len(label) for label in self.data[self.x.name]].sort()
        if max_len_label[-1] > 3:
            _xscale = (_xscale + pn.theme(axis_text_x=pn.element_text(rotation=90)))

        return _xscale
    
    def get_yaxis(self):
        import numpy as np

        if self.y.type == 'string':
            _yscale = pn.scale_x_discrete(name=self.y.title)

        if self.y.type.isin(['number', 'integer']):
            lower = self.data[self.y.name].min()
            upper = self.data[self.y.name].max()
            base = (10**(len(str(upper))-2))*5
            breaks = np.linspace(lower//base*base, upper//base*base, 12, dtype=int)
            breaks = list(set([x // base * base for x in breaks]))
            breaks.sort()

            _yscale = pn.scale_x_continuous(name = self.y.title, breaks=breaks)

        if self.y.type == 'date':
            import mizani
            if self.data[self.y.name].abs().sum() < 10:
                breaks = mizani.breaks.breaks_date(width = "1 year")
            if self.data[self.y.name].abs().sum() >= 10:
                breaks = mizani.breaks.breaks_date(width = "5 years")
            if self.data[self.y.name].abs().sum() >= 100:
                breaks = mizani.breaks.breaks_date(width = "10 years")

            _yscale = pn.scale_x_date(name=self.y.title, breaks=breaks)

        return _yscale

    def line(self, color=None, linetype=None, group=None):

        self.plot = (self.plot
        + pn.geom_line(
            data=self.data, 
            mapping=pn.aes(
                x = self.x.name,
                y = self.y.name,
                color=color,
                group=group,
                linetype=linetype
                )
            )
        + pn.scale_color_manual(self.pal)
        + pn.theme_bw()
        )

    
    def bar(self, x, group=None, fill=None):
        import plotnine

        self.plot = (self.plot
        + pn.geom_bar(
            data=self.data, 
            mapping=pn.aes(
                x=x, 
                fill=fill,
                group=group
                )
            )
        + pn.scale_fill_manual(self.pal)
        + pn.theme_bw()
        )
        return self

    def hbar(self):
        import plotnine

        self.plot = (self.plot
        + pn.geom_bar(
            data=self.data, 
            mapping=pn.aes(
                x=self.x.name, 
                fill=[self.group.name if self.group else None]
                )
            )
        + pn.scale_fill_manual(self.pal)
        + pn.theme_bw()
        + pn.coord_flip()
        )
        return self
    
    def point(self):
        import plotnine
        self.plot = (self.plot()
        + pn.geom_point(
            data=self.data, 
            mapping=pn.aes(
                x=self.x.name, 
                y=self.y.name,
                fill=[self.group.name if self.group else None]
                )
            )
        + pn.scale_fill_manual(self.pal)
        + pn.theme_bw()
        )

        return self

    def col(self):
        import plotnine
        self.plot = (self.plot
        + pn.geom_col(
            data=self.data, 
            mapping=pn.aes(
                x=self.x.name, 
                y=self.y.name,
                fill=[self.group.name if self.group else None]
                )
            )
        + pn.scale_fill_manual(self.pal)
        + pn.theme_bw()
        )

        return self
    

        return self
    def get_pallete(self, pal, color):
        import morpc
        if self.group: 
            n = len(self.data[self.group.name].unique())
        else: 
            n = 1

        if pal == "SEQ":
            __pal = morpc.color.get_colors().SEQ(color, n).hex_list
        if pal == "SEQ2":
            __pal = morpc.color.get_colors().SEQ2(color, n).hex_list
        if pal == "SEQ3":
            __pal = morpc.color.get_colors().SEQ3(color, n).hex_list
        if pal == "DIV":
            __pal = morpc.color.get_colors().DIV(color, n).hex_list
        if pal == "QUAL":
            __pal = morpc.color.get_colors().QUAL(color, n).hex_list

        return __pal

    def show(self):
        return (self.plot 
                + self.labs 
                + self.xscale 
                + self.yscale
                )
    
    def save(self, path, dpi = 100, adjust_size=False):
        from plotnine import ggsave
        if adjust_size:
            ggsave(self.plot, path = path, dpi = dpi, width=adjust_size[0], height=adjust_size[1])
        else:
            ggsave(self.plot, path = path, dpi = dpi)