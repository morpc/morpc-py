from matplotlib.pyplot import plot


class from_resource:
    def __init__(self, data, schema, resource, x, y=None, group=None, pal="SEQ", color='darkblue'):
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
        self.resource = resource

        self.x = self.schema.get_field(x)
        if y:
            self.y = self.schema.get_field(y)
        if group:
            self.group = self.schema.get_field(group)
        
        self.pal = self.get_pallete(pal, color)
        #self.xscale = self.get_xscale()
        #self.yscale = self.get_yscale()
        self.labs = self.get_labs()

    
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
        if self.x.type == 'date':
            __xscale = scale_x_datetime()
        if self.x.type == 'string':
            __xscale = scale_x_discrete()
        if self.x.type == 'integer':
            __xscale = scale_x_discrete()
        
        return __xscale
    
    def get_yscale(self):
        from plotnine import scale_y_continuous, scale_y_datetime, scale_y_discrete

        if self.y.type == 'numeric':
            __yscale = scale_y_continuous()
        if self.y.type == 'date':
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
        + plotnine.scale_fill_manual(self.pal)
        + plotnine.theme_bw()
        )
        return self

    def hbar(self):
        import plotnine

        self.plot = (plotnine.ggplot()
        + plotnine.geom_bar(
            data=self.data, 
            mapping=plotnine.aes(
                x=self.x.name, 
                fill=[self.group.name if self.group else None]
                )
            )
        + plotnine.scale_fill_manual(self.pal)
        + plotnine.theme_bw()
        + plotnine.coord_flip()
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
        + plotnine.scale_fill_manual(self.pal)
        + plotnine.theme_bw()
        )

        return self

    def col(self):
        import plotnine
        self.plot = (plotnine.ggplot()
        + plotnine.geom_col(
            data=self.data, 
            mapping=plotnine.aes(
                x=self.x.name, 
                y=self.y.name,
                fill=[self.group.name if self.group else None]
                )
            )
        + plotnine.scale_fill_manual(self.pal)
        + plotnine.theme_bw()
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
        + plotnine.scale_fill_manual(self.pal)
        + plotnine.theme_bw()
        )

        return self

    def show(self):
        return (self.plot 
                + self.labs 
                #+ self.xscale 
                #+ self.yscale
                )
    
    def save(self, path, dpi = 100, adjust_size=False):
        from plotnine import ggsave
        if adjust_size:
            ggsave(self.plot, path = path, dpi = dpi, width=adjust_size[0], height=adjust_size[1])
        else:
            ggsave(self.plot, path = path, dpi = dpi)