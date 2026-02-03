from types import NoneType
from yaml import safe_load
from importlib.resources import files

from morpc.color.utils import *


import logging

logger = logging.getLogger(__name__)

try:
    with files('morpc').joinpath('color', 'morpc_colors_2026.yaml').open('r') as file: 
        morpc_colors = safe_load(file)
except ValueError as e:
    print(e)

ALL_COLORS = {}
for y in [x for x in morpc_colors.values()]:
    if y.keys() != 'KEY':
        for k, v in y.items():
            if k != "KEY":
                ALL_COLORS.update({k: v})

def get_key_color_name(color):
    if color not in morpc_colors:
        logger.error(f"{color} not a valid color.")
        raise ValueError
    color_values = morpc_colors[color]
    # find the hex value for key
    for k, v in color_values.items():
        if k == 'KEY':
            key_value = v
    # match it to other values
    for k,v in color_values.items():
        if k != 'KEY':
            if v == key_value:
                return k
        

class GetColors:
    _get_color_logger = logging.getLogger(__name__).getChild(__qualname__)

    def __init__(self, morpc_colors=morpc_colors):
        from datetime import datetime
        self.logger = logging.getLogger(__name__).getChild(self.__class__.__name__).getChild(str(datetime.now()))

        self.morpc_colors = morpc_colors

        self.COLOR = []

    def KEYS(self):
        self.KEYS = {}
        for color in self.morpc_colors:
            self.KEYS[color] = self.morpc_colors[color][get_key_color_name(color)]
        
        return self.KEYS

    def SEQ(self, color = None, n=11):
        from morpc.color.utils import get_continuous_cmap, rgb_list_to_hex_list
        from numpy import linspace
        from random import randint

        # Get random color if not assigned
        if color == None:
            colors = [key for key, values in self.KEYS().items() if key not in ['WarmGrey', 'CoolGrey']]
            self.COLOR = colors[randint(0,len(colors))]
        else:
            self.COLOR = color

        # load hex from yaml
        hex = [v for k, v in self.morpc_colors[self.COLOR].items() if k != 'KEY']

        # create cmap
        self.cmap = get_continuous_cmap(hex)

        # extract number of slices from cmap
        self.hex_list = rgb_list_to_hex_list(self.cmap(list(linspace(0,1,n))))
        self.hex_list_r = self.hex_list[::-1]

        return self

    def SEQ2(self, colors=None, n=11):
        from morpc.color import get_continuous_cmap, rgb_list_to_hex_list
        from numpy import linspace
        logger.debug(f"colors = {colors}")

        if not isinstance(colors, list):
            raise RuntimeError(f'{colors} not valid. Pass a list of colors to use.')
        
        if len(colors) != 2:
            raise RuntimeError('Pass two color names')
        
        for color in colors:
            if color in morpc_colors.keys():
                self.COLOR.append(get_key_color_name(color))
            elif color in ALL_COLORS.keys():
                self.COLOR.append(color)
            else:
                logger.error(f"{color} not a valid color")
                raise RuntimeError

        start = [x for x in ALL_COLORS[self.COLOR[0]].values()][1]
        stop = [x for x in ALL_COLORS[self.COLOR[1]].values()][-1]

        self.cmap = get_continuous_cmap([start, stop])
        self.hex_list = rgb_list_to_hex_list([self.cmap(i) for i in list(linspace(0,1,n))])
        self.hex_list_r = self.hex_list[::-1]
        
        return self

    def SEQ3(self, colors=None, n=11):
        from morpc.color import get_continuous_cmap, rgb_list_to_hex_list
        from numpy import linspace

        if not isinstance(colors, list):
            raise ValueError('{colors} not valid. Pass a list of colors to use.')
        if len(colors) != 3:
            raise ValueError('Pass three color names')
        
        for color in colors:
            if color in morpc_colors.keys():
                self.COLOR.append(get_key_color_name(color))
            elif color in ALL_COLORS.keys():
                self.COLOR.append(color)
            else:
                logger.error(f"{color} not a valid color")
                raise RuntimeError


        start = [x for x in ALL_COLORS[self.COLOR[0]].values()][2]
        middle = [x for x in ALL_COLORS[self.COLOR[1]].values()][3]
        stop = [x for x in ALL_COLORS[self.COLOR[2]].values()][-2]

        self.cmap = get_continuous_cmap([start, middle, stop])
        self.hex_list = rgb_list_to_hex_list([self.cmap(i) for i in list(linspace(0,1,n))])
        self.hex_list_r = self.hex_list[::-1]
        
        return self

    def DIV(self, colors=None, n = 11):
        from morpc.color import get_continuous_cmap, rgb_list_to_hex_list
        from numpy import linspace

        if not isinstance(colors, list):
            raise ValueError(f'{colors} not valid. Pass a list of colors to use.')
        if len(colors) != 3:
            raise ValueError('Pass three color names')
        
        for color in colors:
            if color in morpc_colors.keys():
                self.COLOR.append(get_key_color_name(color))
            elif color in ALL_COLORS.keys():
                self.COLOR.append(color)
            else:
                logger.error(f"{color} not a valid color")
                raise RuntimeError

        self.cmap = get_continuous_cmap([ALL_COLORS[x] for x in self.COLOR])
        self.hex_list = rgb_list_to_hex_list([self.cmap(i) for i in list(linspace(0,1,n))])

        self.hex_list_r = self.hex_list[::-1]

        return self

    def QUAL(self, colors = None, paired = False):
        import pandas as pd
        if colors == None:
            colors = ['Navy', 'Orange', 'Forest', 'Ocean', 'Purple', 'Green', 'Blue', 'Red', 'Sky', 'Brown', 'Yellow']

        for color in colors:
            if color in morpc_colors.keys():
                self.COLOR.append(get_key_color_name(color))
            elif color in ALL_COLORS.keys():
                self.COLOR.append(color)
            else:
                logger.error(f"{color} not a valid color")
                raise RuntimeError
            
        self.hex_list = []

        for color in self.COLOR:
            if paired == False:
                self.hex_list.append(ALL_COLORS[color])

            if paired ==  True:
                self.hex_list.append(ALL_COLORS[color])   
                color_pair = f"{color[0:-1]}{int(color[-1]+2)}"
                self.hex_list.append(ALL_COLORS[color_pair])

        self.hex_list = [v for v in self.hex_list]
        self.hex_list_r = self.hex_list[::-1]

        return self
        
# def select_color_array(_list, key, n):
#     import numpy as np
#     if key not in list(range(0, len(_list))):
#         raise ValueError("key not in list.")
#     if n > len(_list):
#         raise ValueError("Too many values requested.")

#     result = [key]
#     left = key - 1
#     right = key + 1

#     while len(result) < n:
#         if left >= 0:
#             result.append(left)
#             left -= 1
#             if len(result) == n:
#                 break
#         if right < len(_list):
#             result.append(right)
#             right += 1
#     result.sort()
    
#     return [_list[i] for i in result]


