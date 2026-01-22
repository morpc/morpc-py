from yaml import safe_load
import morpc
from importlib.resources import files

import json

try:
    with files('morpc').joinpath('color', 'morpc_colors_2026.yaml').open('r') as file: 
        morpc_colors_2026 = safe_load(file)
except ValueError as e:
    print(e)

try:
    with files('morpc').joinpath('color', 'morpc_colors.json').open('r') as file: 
        morpc_colors = json.load(file)
except ValueError as e:
    print(e)

class get_colors():

    def __init__(self, morpc_colors=morpc_colors):
        import os
        ## Use importlib.resources to access non-package files.
        ## See https://docs.python.org/3/library/importlib.resources.html#importlib-resources-functional
        self.morpc_colors = morpc_colors

        self.KEYS = {}
        for __COLOR in self.morpc_colors:
            __key = self.morpc_colors[__COLOR]['key']['position'] - 1
            self.KEYS[__COLOR] = self.morpc_colors[__COLOR]['gradient']['hex'][__key]

    def SEQ(self, color, reverse=False):
        self.hex_list = self.morpc_colors[color]['gradient']['hex']
        self.hex_list_r = self.hex_list[::-1]

        if reverse:
            return self.hex_list_r
        else:
            return self.hex_list

    def SEQ2(self, colors, reverse=False):
        if len(colors) != 2:
            raise ValueError('Pass two color names')

        left = self.morpc_colors[colors[0]]['gradient']['hex'][0:2]
        start = self.morpc_colors[colors[0]]['gradient']['hex'][2]
        stop = self.morpc_colors[colors[1]]['gradient']['hex'][-4]
        right = self.morpc_colors[colors[1]]['gradient']['hex'][-3:]

        _cmap = get_continuous_cmap([start, stop], N=6)
        self.hex_list = left + rgb_list_to_hex_list([_cmap(i) for i in range(_cmap.N)]) + right
        self.hex_list_r = self.hex_list[::-1]

        if reverse:
            return self.hex_list_r
        else:
            return self.hex_list

    def SEQ3(self, colors, reverse=False):
        if len(colors) != 3:
            raise ValueError('Pass three color names')

        first = self.morpc_colors[colors[0]]['gradient']['hex'][0:2]
        start1 = self.morpc_colors[colors[0]]['gradient']['hex'][2]
        stop1 = self.morpc_colors[colors[1]]['gradient']['hex'][6]
        middle = self.morpc_colors[colors[1]]['gradient']['hex'][6]
        start2 = self.morpc_colors[colors[1]]['gradient']['hex'][6]
        stop2 = self.morpc_colors[colors[2]]['gradient']['hex'][8]
        last = self.morpc_colors[colors[2]]['gradient']['hex'][9:10]

        _cmap1 = get_continuous_cmap([start1, stop1], N=4)
        _cmap1 = rgb_list_to_hex_list([_cmap1(i) for i in range(_cmap1.N)])
        _cmap2 = get_continuous_cmap([start2, stop2], N=5)
        _cmap2 = rgb_list_to_hex_list([_cmap2(i) for i in range(_cmap2.N)])
        self.hex_list = first + _cmap1[0:-1] + [middle] + _cmap2[1:5] + last
        self.hex_list_r = self.hex_list[::-1]

        if reverse:
            return self.hex_list_r
        else:
            return self.hex_list

    def DIV(self, colors, reverse=False):
        if len(colors) != 3:
            raise ValueError('Pass three color names')

        first = self.morpc_colors[colors[0]]['gradient']['hex'][5:8]
        start1 = self.morpc_colors[colors[0]]['gradient']['hex'][4]
        stop1 = self.morpc_colors[colors[1]]['gradient']['hex'][1]
        middle = self.morpc_colors[colors[1]]['gradient']['hex'][1]
        start2 = self.morpc_colors[colors[1]]['gradient']['hex'][1]
        stop2 = self.morpc_colors[colors[2]]['gradient']['hex'][4]
        last = self.morpc_colors[colors[2]]['gradient']['hex'][6:8]

        _cmap1 = get_continuous_cmap([start1, stop1], N=3)
        _cmap1 = rgb_list_to_hex_list([_cmap1(i) for i in range(_cmap1.N)])
        _cmap2 = get_continuous_cmap([start2, stop2], N=4)
        _cmap2 = rgb_list_to_hex_list([_cmap2(i) for i in range(_cmap2.N)])
        self.hex_list = first[::-1] + _cmap1[0:2] + [middle] + _cmap2[1:4] + last
        self.hex_list_r = self.hex_list[::-1]
        self.hex_list_r = self.hex_list[::-1]

        if reverse:
            return self.hex_list_r
        else:
            return self.hex_list

    def QUAL(self, n):
        self.hex_list = []
        if n <= 10:
            for color in self.morpc_colors:
                if not 'grey' in color:
                    __key = self.morpc_colors[color]['key']['position']-1
                    self.hex_list.append(self.morpc_colors[color]['gradient']['hex'][__key])
        if 10 < n <= 20:
            for color in self.morpc_colors:
                if not 'grey' in color:
                    key_pos = self.morpc_colors[color]['key']['position']-1
                    positions = [key_pos - 2, key_pos]
                    for pos in positions:
                        self.hex_list.append(self.morpc_colors[color]['gradient']['hex'][pos])
        if 20 < n <= 30:
            for color in self.morpc_colors:
                if not 'grey' in color:
                    key_pos = self.morpc_colors[color]['key']['position']-1
                    positions = [key_pos - 2, key_pos, key_pos + 2]
                    for pos in positions:
                        self.hex_list.append(self.morpc_colors[color]['gradient']['hex'][pos])

        self.hex_list = self.hex_list[0:n]
        
        return self.hex_list

def select_color_array(_list, key, n):
    import numpy as np
    if key not in list(range(0, len(_list))):
        raise ValueError("key not in list.")
    if n > len(_list):
        raise ValueError("Too many values requested.")

    result = [key]
    left = key - 1
    right = key + 1

    while len(result) < n:
        if left >= 0:
            result.append(left)
            left -= 1
            if len(result) == n:
                break
        if right < len(_list):
            result.append(right)
            right += 1
    result.sort()
    
    return [_list[i] for i in result]



# Everything below is used for constructing the palette 
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


def hls_to_hex(h, l, s):
    """Converts HLS color values to a hexadecimal color code.

    Args:
        h: Hue (0-1).
        l: Lightness (0-1).
        s: Saturation (0-1).

    Returns:
        A hexadecimal color code string (e.g., "#RRGGBB").
    """
    import colorsys

    r, g, b = colorsys.hls_to_rgb(h, l, s)
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)
    return f"#{r:02x}{g:02x}{b:02x}"

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

def plot_from_rgb_list(rgb_colors, labels = ['hls', 'grey', 'hex'], position=None, title=None):
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
        rgb = rgb[0:3]
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

        if 'hex' in labels:
            ax.text(i + 0.5, 0.23, hex_color, color=text_color, ha='center', va='center', fontsize=10, weight='bold')
        if 'grey' in labels:
            ax.text(i + 0.5, 0.5, grey_text, color=text_color, ha='center', va='center', fontsize=10, weight='bold')
        if 'hls' in labels:
            ax.text(i + 0.5, 0.78, hls_text, color=text_color, ha='center', va='center', fontsize=10, weight='bold')

    if position:
        outline = plt.Rectangle((position-1, 0), 1, 1, lw=3, edgecolor='white', facecolor='none')
        ax.add_patch(outline)
    ax.set_xlim(0, len(rgb_colors))
    ax.set_ylim(0, 1)
    if title:
        plt.text(0, 1.05, title, fontsize=10, weight='bold')
    plt.tight_layout()
    plt.show()

def rgb_list_to_hex_list(rgb_colors):
    hex_colors = []
    for i, rgb in enumerate(rgb_colors):
        hex_color = rgb_to_hex(rgb)
        hex_colors.append(hex_color)
    return hex_colors

def plot_from_hex_list(hex_colors, labels = ['hls', 'grey', 'hex'], position=None, title=None):
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
        if not str(hex).startswith("#"):
            hex = f"#{hex}"
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

        if 'hex' in labels:
            ax.text(i + 0.5, 0.23, hex, color=text_color, ha='center', va='center', fontsize=10, weight='bold')
        if 'grey' in labels:
            ax.text(i + 0.5, 0.5, grey_text, color=text_color, ha='center', va='center', fontsize=10, weight='bold')
        if 'hls' in labels:
            ax.text(i + 0.5, 0.78, hls_text, color=text_color, ha='center', va='center', fontsize=10, weight='bold')

    if position:
        outline = plt.Rectangle((position-1, 0), 1, 1, lw=3, edgecolor='white', facecolor='none')
        ax.add_patch(outline)
    ax.set_xlim(0, len(hex_colors))
    ax.set_ylim(0, 1)
    if title:
        plt.text(0, 1.05, title, fontsize=10, weight='bold')
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

def overlay_color(rgb_hex_colors, light="white", dark="black", threshold=4, reverse=False):
    """
    Decide which color is suitable to write onto the given colors
    """

    if reverse:
        light2 = dark
        dark2 = light
        light = light2
        dark = dark2
    return [light if float(check_contrast(x,'#FFFFFF')['ratio']) > threshold else dark for x in rgb_hex_colors]

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

def get_continuous_cmap(hex_list, float_list=None, N=256):
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
    cmp = LinearSegmentedColormap('my_cmp', segmentdata=cdict, N=N)
    return cmp

def hex_to_rgb(value):
    '''
    Converts hex to rgb colours
    value: string of 6 characters representing a hex colour.
    Returns: list length 3 of RGB values'''
    if value.startswith("#"):
        value = value.strip("#") # removes hash symbol if present
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def rgb_to_dec(value):
    '''
    Converts rgb to decimal colours (i.e. divides each value by 256)
    value: list (length 3) of RGB values
    Returns: list (length 3) of decimal values'''
    return [v/256 for v in value]

