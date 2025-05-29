---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.17.1
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# morpc.color Demo

+++

## Import morpc package

```{code-cell} ipython3
import morpc
```

## Get standard HEX color codes

+++

The get_colors() class provides access to a json file that contains various useful definitions of colors. It takes one argument `colorDictPath='../morpc/color/morpc_colors.json'` which is the relative path to the json file. 

The json file is stored in the attribute morpc_colors.

```{code-cell} ipython3
morpc.color.get_colors().morpc_colors
```

## Key Colors

+++

The standard colors are retrieved using `.KEYS` instance.

```{code-cell} ipython3
morpc.color.get_colors().KEYS
```

## Plot color strips from hex lists to see colors

+++

You can plot a list of hex codes using the `plot_from_hex_list()` function. In the following example, we pass the values of the key colors to see them. The plot includes the HLS values, a grey values, and the hex code. 

```{code-cell} ipython3
morpc.color.plot_from_hex_list(morpc.color.get_colors().KEYS.values())
```

## Sequential color gradients for each color

+++

Each color has an associated gradient. These gradients can be returned using the `.SEQ()` function. Simply pass the color name to the funcion.

```{code-cell} ipython3
morpc.color.plot_from_hex_list(morpc.color.get_colors().SEQ('midblue').hex_list)
```

```{code-cell} ipython3
for color in morpc.color.get_colors().KEYS.keys():
    morpc.color.plot_from_hex_list(morpc.color.get_colors().SEQ(color).hex_list)
```

Limit the number of colors returned in the gradient by passing an integer 1 through 12 to the `n = ` attribute.

```{code-cell} ipython3
morpc.color.plot_from_hex_list(morpc.color.get_colors().SEQ('gold', 4).hex_list)
```

## Two color sequential gradients

+++

Pass a list of two color names to `.SEQ2()` method to get a split gradient. 

```{code-cell} ipython3
morpc.color.plot_from_hex_list(morpc.color.get_colors().SEQ2(['gold', 'darkblue']).hex_list)
```

```{code-cell} ipython3
morpc.color.plot_from_hex_list(morpc.color.get_colors().SEQ2(['rose', 'blue']).hex_list)
```

## Three color sequential gradients

+++

The same can be done with three colors using `.SEQ3()` method.

```{code-cell} ipython3
morpc.color.plot_from_hex_list(morpc.get_colors().SEQ3(['gold', 'darkgreen', 'darkblue']).hex_list)
```

## Color maps

+++

Using any method, you can return a color map in the form of the gradient using the `.cmap` instance.

```{code-cell} ipython3
morpc.color.get_colors().SEQ3(['gold', 'darkgreen', 'darkblue']).cmap
```

## Diverging color gradients

+++

Use the `.DIV()` method can be used to create diverging gradients and color maps. 

```{code-cell} ipython3
morpc.color.plot_from_hex_list(morpc.get_colors().DIV(['gold','darkblue']).hex_list)
```

```{code-cell} ipython3
morpc.color.plot_from_hex_list(morpc.color.get_colors().DIV(['rose','darkgreen']).hex_list)
```

## Qualitative color groups

+++

Use the `.QUAL()` method to return groups for qualitative data. It selects a number of grouped lightness variations of each color. 

```{code-cell} ipython3
morpc.color.plot_from_hex_list(morpc.color.get_colors().QUAL(20).hex_list)
```

## Testing color maps for color blindness accessibility

```{code-cell} ipython3
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(19680801)
data = np.random.randn(30, 30)
fig, ax = plt.subplots()
psm = ax.pcolormesh(data, cmap=morpc.color.get_colors().DIV(['gold', 'bluegreen']).cmap, rasterized=True, vmin=-4, vmax=4)
fig.colorbar(psm, ax=ax)
```

```{code-cell} ipython3
from daltonize import daltonize
daltonize.simulate_mpl(fig, color_deficit='p')
```

```{code-cell} ipython3

```
