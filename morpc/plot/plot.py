class from_resource:
    def __init__(self, data, schema, x, y=None, group=None):
        """
        Plot data stored in a frictionless resource with reasonable values. 

        Parameters:
        -----------
        resourcePath : str
            Path to the resource file
        x : str
            Column to plot on x axis
        y : str
            Column to plot on y axis
        
        Returns:
        --------
        plotnine.ggplot.ggplot
            Plot of data
        """

        self.data = data
        self.schema = schema

        self.x = self.schema.get_field(x)
        if y:
            self.y = self.schema.get_field(y)
        if group:
            self.group = self.schema.get_field(group)
        else:
            self.group = None

        self.labs = self.get_labs()
        self.xscale = self.get_xscale()
        self.yscale = self.get_yscale()
    
    def get_labs(self):
        from plotnine import labs

        __labs = labs(
            x = self.x.title, 
            y = "Count", 
            fill = [self.group.title if self.group else None]
            )
        
        return __labs
    
    def get_xscale(self):
        from plotnine import scale_x_continuous, scale_x_datetime, scale_x_discrete

        if self.x.type == 'numeric':
            __xscale = scale_x_continuous()
        if self.x.type == 'year':
            __xscale == scale_x_datetime()
        if self.x.type == 'string':
            __xscale = scale_x_discrete()
        if self.x.type == 'integer':
            __xscale = scale_x_discrete()
        
        return __xscale
    
    def get_yscale(self):
        from plotnine import scale_y_continuous, scale_y_datetime, scale_y_discrete

        if self.y.type == 'numeric':
            __yscale = scale_y_continuous()
        if self.y.type == 'year':
            __yscale = scale_y_datetime()
        if self.y.type == 'string':
            __yscale = scale_y_discrete()
        if self.y.type == 'integer':
            __yscale = scale_y_discrete()
        
        return __yscale
        
    def bar(self):
        import plotnine

        self.plot = (plotnine.ggplot()
        + plotnine.geom_bar(
            data=self.data, 
            mapping=plotnine.aes(
                x=self.x.name, 
                fill=[self.group.name if self.group else None]
                )
            )
        )
        return self
    
    def point(self):
        import plotnine
        self.plot = (plotnine.ggplot()
        + plotnine.geom_point(
            data=self.data, 
            mapping=plotnine.aes(
                x=self.x.name, 
                y=self.y.name,
                fill=[self.group.name if self.group else None]
                )
            )
        )

        return self
    
    def line(self):
        import plotnine
        self.plot = (plotnine.ggplot()
        + plotnine.geom_line(
            data=self.data, 
            mapping=plotnine.aes(
                x=self.x.name, 
                y=self.y.name,
                fill=[self.group.name if self.group else None]
                )
            )
        )

        return self

    def show(self):
        return self.plot + self.labs + self.xscale + self.yscale
    
    def save(self, path, dpi = 100, adjust_size=False):
        from plotnine import ggsave
        if adjust_size:
            ggsave(self.plot, path = path, dpi = dpi, width=adjust_size[0], height=adjust_size[1])
        else:
            ggsave(self.plot, path = path, dpi = dpi)