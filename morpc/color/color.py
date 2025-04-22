import json
import itertools

class get_colors():

    def __init__(self, colorDictPath='../morpc/color/morpc_colors.json'):
        import os

        try: 
            with open(os.path.normpath(colorDictPath)) as file:
                self.morpc_colors = json.load(file)
        except ValueError as e:
            print(e)

        self.KEYS = {}
        for __COLOR in self.morpc_colors:
            self.KEYS[__COLOR] = self.morpc_colors[__COLOR]['key']['hex']

    def SEQ(self, color='darkblue'):
        
        self.hex_list = self.morpc_colors[color]['gradient']['hex']
        self.rgb_list = self.morpc_colors[color]['gradient']['rgb']
        self.hex_list_r = self.hex_list[::-1]
        self.rgb_list_r = self.rgb_list[::-1]

        return self
    
    def SEQ2(self, colors=['gold','darkblue']):
        import itertools

        self.hex_list = [x for x in itertools.chain.from_iterable([self.morpc_colors[colors[1]]['gradient']['hex'][0:6:1], 
                                                                            self.morpc_colors[colors[2]]['gradient']['hex'][6:12:1]])]
        self.rgb_list = [x for x in itertools.chain.from_iterable([self.morpc_colors[colors[1]]['gradient']['rgb'][0:6:1], 
                                                                            self.morpc_colors[colors[2]]['gradient']['rgb'][6:12:1]])]
        self.hex_list_r = self.hex_list[::-1]
        self.rgb_list_r = self.rgb_list[::-1]

        return self

    def DIV(self, colors=['rose', 'darkgreen']):
        import itertools

        self.hex_list = [x for x in itertools.chain.from_iterable([self.morpc_colors[colors[1]]['gradient']['hex'][12:0:-2], 
                                                                    self.morpc_colors[colors[2]]['gradient']['hex'][0:12:2]])]
        self.rgb_list = [x for x in itertools.chain.from_iterable([self.morpc_colors[colors[1]]['gradient']['rgb'][12:0:-2], 
                                                                    self.morpc_colors[colors[2]]['gradient']['rgb'][0:12:2]])]
        self.hex_list_r = self.hex_list[::-1]
        self.rgb_list_r = self.rgb_list[::-1]

        return self
    
    def QUAL(self, n):
        self.hex_list = []
        if n <= 8:
            for color in self.morpc_colors:
                self.hex_list.append(self.morpc_colors[color]['key']['hex'])
        if 8 < n <= 16:
            for color in self.morpc_colors:
                key_pos = self.morpc_colors[color]['key']['position']
                positions = [key_pos - 2, key_pos]
                for pos in positions:
                    self.hex_list.append(self.morpc_colors['gradient']['hex'][pos])
        if 16 < n <= 24:
            for color in self.morpc_colors:
                key_pos = self.morpc_colors[color]['key']['position']
                positions = [key_pos - 2, key_pos, key_pos + 2]
                for pos in positions:
                    self.hex_list.append(self.morpc_colors['gradient']['hex'][pos])

        self.hex_list = self.hex_list[0:n]
        self.hex_list_r = self.hex_list[::-1]

        return self


# Everything below is used for constructing the pallate 
def hex_to_hls(hex_color):
    """
    Convert a HEX color to HLS (Hue, Lightness, Saturation).

    Parameters:
    - hex_color (str): HEX color string, e.g., '#ff9900' or 'ff9900'

    Returns:
    - tuple: (h, l, s) with values in [0, 1]
    """
    from colorsys import rgb_to_hls

    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError("HEX color must be 6 characters long")

    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0

    return rgb_to_hls(r, g, b)

def rgb_to_greyscale(rgb):
    """Convert RGB color to grayscale using luminance weights."""
    r, g, b = rgb
    return 0.299 * r + 0.587 * g + 0.114 * b

def solve_lightness_for_greyscale(hue, saturation, target_grey, tol=1e-4):
    """
    Finds the lightness value that produces the target grayscale intensity.

    Parameters:
    - hue (float): Hue [0, 1]
    - saturation (float): Saturation [0, 1]
    - target_grey (float): Desired grayscale intensity [0, 1]
    - tol (float): Tolerance

    Returns:
    - lightness (float): Value [0, 1] that gives the target greyscale
    """
    from colorsys import hls_to_rgb
    low, high = 0.0, 1.0

    for _ in range(100):
        mid = (low + high) / 2
        rgb = hls_to_rgb(hue, mid, saturation)
        grey = rgb_to_greyscale(rgb)

        if abs(grey - target_grey) < tol:
            return mid
        elif grey < target_grey:
            low = mid
        else:
            high = mid

    return (low + high) / 2  # best approximation

def rgb_to_hex(rgb):
    """Convert RGB (0–1 floats) to HEX string."""
    return '#{:02x}{:02x}{:02x}'.format(*(int(c * 255) for c in rgb))

def is_dark(rgb):
    """Determine if a color is dark based on perceived brightness."""
    hex = rgb_to_hex(rgb)
    dict = check_contrast(hex)

    return dict['AA'] == 'pass'

def plot_from_rgb_list(rgb_colors, position=None):
    """
    Plot a list of RGB colors as squares with hex value overlays.

    Parameters:
    - rgb_colors (list of tuples): List of RGB colors with values between 0 and 1
    """

    from colorsys import rgb_to_hls
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(len(rgb_colors), 2))
    ax.axis('off')

    for i, rgb in enumerate(rgb_colors):
        hex_color = rgb_to_hex(rgb)
        r,g,b = [x for x in rgb]
        hls_color = rgb_to_hls(r,g,b)
        h,l,s = [x for x in hls_color]
        hls_text=f"{h:.3f}\n{l:.3f}\n{s:.3f}"
        grey_text = f"{100 * rgb_to_greyscale(rgb):.0f}"

        text_color = 'white' if is_dark(rgb) else 'black'

        # Draw color square
        square = plt.Rectangle((i, 0), 1, 1, color=rgb)
        ax.add_patch(square)

        # Add hex text overlay
        ax.text(i + 0.5, 0.23, hex_color, color=text_color,
                ha='center', va='center', fontsize=10, weight='bold')
        ax.text(i + 0.5, 0.5, grey_text, color=text_color,
                ha='center', va='center', fontsize=10, weight='bold')        
        ax.text(i + 0.5, 0.78, hls_text, color=text_color,
                ha='center', va='center', fontsize=10, weight='bold')

    if position:
        outline = plt.Rectangle((position-1, 0), 1, 1, lw=2, edgecolor='white', facecolor='none')
        ax.add_patch(outline)
    ax.set_xlim(0, len(rgb_colors))
    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.show()

def rgb_list_to_hex_list(rgb_colors):
    hex_colors = []
    for i, rgb in enumerate(rgb_colors):
        hex_color = rgb_to_hex(rgb)
        hex_colors.append(hex_color)
    return hex_colors

def plot_from_hex_list(hex_colors, position=None):
    """
    Plot a list of RGB colors as squares with hex value overlays.

    Parameters:
    - rgb_colors (list of tuples): List of RGB colors with values between 0 and 1
    """

    from colorsys import rgb_to_hls
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(len(hex_colors), 2))
    ax.axis('off')

    for i, hex in enumerate(hex_colors):
        rgb = rgb_to_dec(hex_to_rgb(hex))
        r,g,b = [x for x in rgb]
        hls_color = rgb_to_hls(r,g,b)
        h,l,s = [x for x in hls_color]
        hls_text=f"{h:.3f}\n{l:.3f}\n{s:.3f}"
        grey_text = f"{100 * rgb_to_greyscale(rgb):.0f}"

        text_color = 'white' if is_dark(rgb) else 'black'

        # Draw color square
        square = plt.Rectangle((i, 0), 1, 1, color=hex)
        ax.add_patch(square)

        # Add hex text overlay
        ax.text(i + 0.5, 0.23, hex, color=text_color,
                ha='center', va='center', fontsize=10, weight='bold')
        ax.text(i + 0.5, 0.5, grey_text, color=text_color,
                ha='center', va='center', fontsize=10, weight='bold')        
        ax.text(i + 0.5, 0.78, hls_text, color=text_color,
                ha='center', va='center', fontsize=10, weight='bold')

    if position:
        outline = plt.Rectangle((position-1, 0), 1, 1, lw=2, edgecolor='white', facecolor='none')
        ax.add_patch(outline)
    ax.set_xlim(0, len(hex_colors))
    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.show()

def rgb_scale_from_hue(hue, sats, greys=None):
    """
    get a list of rgb values with def
    """
    import colorsys
    scale=[]
    if not greys:
        greys = [.96, .90, .82, .74, .68, .60, .50, .42, .33, .25, .17, .08]
    for i in range(len(greys)):
        grey=greys[i]
        sat=sats[i]
        lum = solve_lightness_for_greyscale(hue, sat, grey)
        rgb=colorsys.hls_to_rgb(hue, lum, sat)
        scale.append(rgb)
    return scale


def check_contrast(bkgcolor, textcolor = "#FFFFFF"):
    """
    Test if a color text has approved contrast ratios on a background color

    Parameters:
    -----------
    bkgcolor : str
        A hex color code of the color of the background, e.g #2e5072
    
    textcolor : str (default: #FFFFFF)
        A hex color code of the color of the forground
    """
    import requests
    import json
    fcolor = textcolor.lstrip("#")
    bcolor = bkgcolor.lstrip("#")

    url = f"https://webaim.org/resources/contrastchecker/?fcolor={fcolor}&bcolor={bcolor}&api"

    r = requests.get(url)
    dict = r.json()

    return dict

def get_continuous_cmap(hex_list, float_list=None):
    ''' creates and returns a color map that can be used in heat map figures.
        If float_list is not provided, colour map graduates linearly between each color in hex_list.
        If float_list is provided, each color in hex_list is mapped to the respective location in float_list. 
        
        Parameters
        ----------
        hex_list: list of hex code strings
        float_list: list of floats between 0 and 1, same length as hex_list. Must start with 0 and end with 1.
        
        Returns
        ----------
        colour map'''
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap
    rgb_list = [rgb_to_dec(hex_to_rgb(i)) for i in hex_list]
    if float_list:
        pass
    else:
        float_list = list(np.linspace(0,1,len(rgb_list)))
        
    cdict = dict()
    for num, col in enumerate(['red', 'green', 'blue']):
        col_list = [[float_list[i], rgb_list[i][num], rgb_list[i][num]] for i in range(len(float_list))]
        cdict[col] = col_list
    cmp = LinearSegmentedColormap('my_cmp', segmentdata=cdict, N=256)
    return cmp

def hex_to_rgb(value):
    '''
    Converts hex to rgb colours
    value: string of 6 characters representing a hex colour.
    Returns: list length 3 of RGB values'''
    value = value.strip("#") # removes hash symbol if present
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def rgb_to_dec(value):
    '''
    Converts rgb to decimal colours (i.e. divides each value by 256)
    value: list (length 3) of RGB values
    Returns: list (length 3) of decimal values'''
    return [v/256 for v in value]

