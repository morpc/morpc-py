# morpc.color Demo

## Import morpc package


```python
import morpc
```

## Get standard HEX color codes

The get_colors() class provides access to a json file that contains various useful definitions of colors. It takes one argument `colorDictPath='../morpc/color/morpc_colors.json'` which is the relative path to the json file. 

The json file is stored in the attribute morpc_colors.


```python
morpc.color.get_colors().morpc_colors
```




    {'darkblue': {'key': {'hex': '#2e5072',
       'hls': '(0.5833, 0.3137, 0.425)',
       'position': 8},
      'curves': {'hue': 0.58333,
       'greys': [0.95, 0.87, 0.78, 0.68, 0.58, 0.45, 0.36, 0.29, 0.21, 0.15, 0.08],
       'sats': [0.1,
        0.12,
        0.15,
        0.18,
        0.22,
        0.29,
        0.34,
        0.425,
        0.44,
        0.548,
        0.46]},
      'gradient': {'rgb': [[0.9460205078124999,
         0.9509279306640624,
         0.9558349609375001],
        [0.8575390625, 0.872803344921875, 0.88806640625],
        [0.75377197265625, 0.7858899565429688, 0.81800537109375],
        [0.63456298828125, 0.6903098469726562, 0.74605224609375],
        [0.5076513671875, 0.5964390982421874, 0.6852197265625],
        [0.337666015625, 0.4755914542968749, 0.613505859375],
        [0.25354248046874994, 0.3841604979492187, 0.5147680664062501],
        [0.180950927734375, 0.3147026154785155, 0.448443603515625],
        [0.12796875000000002, 0.22851964687499993, 0.3290625],
        [0.07548046874999997, 0.16699584796874994, 0.25850390625],
        [0.04719726562500001, 0.08740395195312498, 0.127607421875]],
       'hex': ['#f1f2f3',
        '#dadee2',
        '#c0c8d0',
        '#a1b0be',
        '#8198ae',
        '#56799c',
        '#406183',
        '#2e5072',
        '#203a53',
        '#132a41',
        '#0c1620']}},
     'blue': {'key': {'hex': '#0077bf',
       'hls': '(0.5628, 0.3745, 1)',
       'position': 7},
      'curves': {'hue': 0.5628,
       'greys': [0.95, 0.87, 0.78, 0.68, 0.58, 0.43, 0.36, 0.28, 0.21, 0.15, 0.08],
       'sats': [0.5, 0.64, 0.68, 0.74, 0.8, 0.84, 1, 1, 0.98, 0.92, 0.87]},
      'gradient': {'rgb': [[0.9263916015625, 0.9569734375, 0.9754638671875],
        [0.7921972656249999, 0.893272515625, 0.9543847656250001],
        [0.6402929687499999, 0.821763453125, 0.9314843750000001],
        [0.4592236328125, 0.7458773750000001, 0.9191943359375],
        [0.26765136718750004, 0.6733399609374999, 0.9186279296875],
        [0.07121093750000007, 0.537186828125, 0.8189257812499999],
        [0.0, 0.46770429687500004, 0.75048828125],
        [0.0, 0.36363476562499997, 0.58349609375],
        [0.004375000000000018, 0.271572, 0.433125],
        [0.012460937499999991, 0.19107103125, 0.2990625],
        [0.010791015624999983, 0.10080203125000001, 0.15522460937500002]],
       'hex': ['#ecf4f8',
        '#cae3f3',
        '#a3d1ed',
        '#75beea',
        '#44abea',
        '#1288d0',
        '#0077bf',
        '#005c94',
        '#01456e',
        '#03304c',
        '#021927']}},
     'darkgreen': {'key': {'hex': '#2c7f68',
       'hsl': '(0.4538, 0.3359, 0.4853)',
       'position': 7},
      'curves': {'hue': 0.4538,
       'greys': [0.95, 0.87, 0.78, 0.68, 0.58, 0.45, 0.39, 0.28, 0.21, 0.15, 0.08],
       'sats': [0.1, 0.13, 0.18, 0.2, 0.22, 0.32, 0.48, 0.52, 0.54, 0.54, 0.46]},
      'gradient': {'rgb': [[0.9430664062499999,
         0.9534179687500001,
         0.950548515625],
        [0.84633544921875, 0.88169189453125, 0.871891087890625],
        [0.7234375000000001, 0.8078124999999999, 0.78442375],
        [0.5880859375, 0.725390625, 0.6873297656249999],
        [0.4462939453125, 0.6459912109375, 0.59063512890625],
        [0.2760839843749999, 0.5359277343750001, 0.46389904687500005],
        [0.17443359375, 0.49646484375, 0.40719778125],
        [0.1142578125, 0.36181640625, 0.2931931640625],
        [0.08164550781250002, 0.2733349609375, 0.22019864453125],
        [0.05834228515625001, 0.19531982421875, 0.157349650390625],
        [0.03737548828125001, 0.10105224609374999, 0.08340104882812499]],
       'hex': ['#f0f3f2',
        '#d7e0de',
        '#b8cdc8',
        '#95b8af',
        '#71a496',
        '#468876',
        '#2c7e67',
        '#1d5c4a',
        '#144538',
        '#0e3128',
        '#091915']}},
     'lightgreen': {'key': {'hex': '#66b561',
       'hls': '(.3234, 0.5451, 0.3621)',
       'position': 5},
      'curves': {'hue': 0.3234,
       'greys': [0.95, 0.87, 0.78, 0.68, 0.58, 0.45, 0.36, 0.28, 0.21, 0.15, 0.08],
       'sats': [0.12, 0.18, 0.22, 0.32, 0.36, 0.46, 0.58, 0.58, 0.44, 0.36, 0.28]},
      'gradient': {'rgb': [[0.9433114843749999,
         0.9548828125000001,
         0.9425781249999999],
        [0.84358524609375, 0.8892919921875, 0.8406884765625],
        [0.72458048828125, 0.8200439453124999, 0.7185302734375001],
        [0.5603008593749998, 0.7667480468750001, 0.5472167968749999],
        [0.40158672656249983, 0.70921875, 0.38208984375],
        [0.24411928515624984, 0.5991845703124999, 0.22161621093750006],
        [0.15703462890624972, 0.5072509765625001, 0.13483886718749993],
        [0.1221048730468748, 0.39442138671875004, 0.10484619140624996],
        [0.1177497070312499, 0.27685546875, 0.107666015625],
        [0.09520086718749995, 0.18958984375, 0.08921875000000001],
        [0.05692623828124997, 0.09671875, 0.054404296874999994]],
       'hex': ['#f0f3f0',
        '#d7e2d6',
        '#b8d1b7',
        '#8ec38b',
        '#66b461',
        '#3e9838',
        '#288122',
        '#1f641a',
        '#1e461b',
        '#183016',
        '#0e180d']}},
     'bluegreen': {'key': {'hex': '#00b2bf',
       'hls': '(0.5113, 0.3745, 1.000)',
       'position': 6},
      'curves': {'hue': 0.5113,
       'greys': [0.95, 0.87, 0.78, 0.68, 0.58, 0.49, 0.36, 0.28, 0.21, 0.15, 0.08],
       'sats': [0.55, 0.68, 0.72, 0.84, 0.96, 1, 1, 1, 0.98, 0.92, 0.87]},
      'gradient': {'rgb': [[0.90577392578125,
         0.9681102490234375,
         0.97264404296875],
        [0.7202734374999998, 0.9313657578125001, 0.9467187500000002],
        [0.5070117187500001, 0.891762703125, 0.9197460937499999],
        [0.19230468750000007, 0.8797657734374998, 0.9297656249999999],
        [0.017714843749999987, 0.8103761562499999, 0.86802734375],
        [0.0, 0.6909568359374999, 0.7412109375],
        [0.0, 0.5075209960937499, 0.54443359375],
        [0.0, 0.39463740234375, 0.42333984375],
        [0.0031909179687499845, 0.29469914355468746, 0.31590087890625],
        [0.009257812500000018, 0.20775086718749997, 0.22218749999999998],
        [0.008124999999999993, 0.10950175000000001, 0.116875]],
       'hex': ['#e6f6f8',
        '#b7edf1',
        '#81e3ea',
        '#31e0ed',
        '#04cedd',
        '#00b0bd',
        '#00818a',
        '#00646b',
        '#004b50',
        '#023438',
        '#021b1d']}},
     'midblue': {'key': {'hex': '#2c6179',
       'hls': '(0.5519, 0.3235, 0.4667)',
       'position': 7},
      'curves': {'hue': 0.5519,
       'greys': [0.95, 0.87, 0.78, 0.67, 0.56, 0.45, 0.33, 0.26, 0.2, 0.15, 0.08],
       'sats': [0.1, 0.13, 0.2, 0.26, 0.3, 0.38, 0.46, 0.52, 0.54, 0.54, 0.46]},
      'gradient': {'rgb': [[0.94481201171875,
         0.9517215478515625,
         0.95484619140625],
        [0.85240478515625, 0.8757896142578125, 0.88636474609375],
        [0.733984375, 0.795043828125, 0.82265625],
        [0.5801025390625, 0.699430732421875, 0.7533935546875],
        [0.4217285156249999, 0.60551208984375, 0.6886230468750001],
        [0.2751855468750001, 0.50746700390625, 0.6125097656249999],
        [0.17527587890625002, 0.38090434667968753, 0.47389404296875],
        [0.12246093749999998, 0.30516857421875004, 0.38779296875],
        [0.09018066406249997, 0.23597691992187503, 0.30190917968750003],
        [0.06766357421875, 0.1770561572265625, 0.22652587890625],
        [0.042451171875, 0.09225362890625001, 0.114775390625]],
       'hex': ['#f0f2f3',
        '#d9dfe2',
        '#bbcad1',
        '#93b2c0',
        '#6b9aaf',
        '#46819c',
        '#2c6178',
        '#1f4d62',
        '#163c4c',
        '#112d39',
        '#0a171d']}},
     'rose': {'key': {'hex': '#b0503f',
       'hls': '(0.0251, 0.4686, 0.4728)',
       'position': 6},
      'curves': {'hue': 0.0251,
       'greys': [0.95, 0.87, 0.78, 0.67, 0.56, 0.45, 0.33, 0.26, 0.2, 0.15, 0.08],
       'sats': [0.18, 0.24, 0.32, 0.42, 0.47, 0.5, 0.52, 0.52, 0.48, 0.4, 0.34]},
      'gradient': {'rgb': [[0.9605615234375, 0.9458546269531249, 0.9432470703125],
        [0.906298828125, 0.8560316015625, 0.847119140625],
        [0.8604638671875, 0.7489137578125, 0.7291357421875],
        [0.8251220703125, 0.609993271484375, 0.5718505859375],
        [0.7890869140625, 0.471349931640625, 0.4150146484375],
        [0.7528076171875, 0.33287719726562504, 0.2584228515625],
        [0.56814453125, 0.23795687109375002, 0.17941406250000003],
        [0.44753906250000003, 0.18744349218749998, 0.14132812499999997],
        [0.33187988281249997, 0.14902662500000002, 0.11660644531250003],
        [0.23071289062499997, 0.11873144531250002, 0.09887695312500003],
        [0.11613769531250001, 0.066077841796875, 0.05720214843749999]],
       'hex': ['#f4f1f0',
        '#e7dad8',
        '#dbbeb9',
        '#d29b91',
        '#c97869',
        '#bf5441',
        '#903c2d',
        '#722f24',
        '#54261d',
        '#3a1e19',
        '#1d100e']}},
     'gold': {'key': {'hex': '#977118',
       'hls': '(0.1173, 0.342, 0.726)',
       'position': 5},
      'curves': {'hue': 0.1173,
       'greys': [0.95, 0.87, 0.78, 0.67, 0.56, 0.45, 0.33, 0.26, 0.2, 0.15, 0.08],
       'sats': [0.32, 0.4, 0.45, 0.56, 0.63, 0.72, 0.78, 0.78, 0.67, 0.6, 0.54]},
      'gradient': {'rgb': [[0.960654296875, 0.949685640625, 0.923623046875],
        [0.9061035156249999, 0.8690206640625, 0.7809082031250001],
        [0.8504150390624999, 0.777912568359375, 0.6056396484375001],
        [0.809541015625, 0.6659418671874999, 0.324736328125],
        [0.7202880859374999, 0.5553677441406251, 0.16350097656250007],
        [0.5929296875, 0.44589415625, 0.09652343750000003],
        [0.44130615234375, 0.3267470419921875, 0.05454345703125002],
        [0.34765625, 0.2574078125, 0.04296875],
        [0.2601220703125, 0.198298998046875, 0.05140136718749999],
        [0.19140625, 0.14888535156250002, 0.0478515625],
        [0.10019775390625, 0.0793842080078125, 0.029929199218749994]],
       'hex': ['#f4f2eb',
        '#e7ddc7',
        '#d8c69a',
        '#cea952',
        '#b78d29',
        '#977118',
        '#70530d',
        '#58410a',
        '#42320d',
        '#30250c',
        '#191407']}}}



## Key Colors

The standard colors are retrieved using `.KEYS` instance.


```python
morpc.color.get_colors().KEYS
```




    {'darkblue': '#2e5072',
     'blue': '#0077bf',
     'darkgreen': '#2c7f68',
     'lightgreen': '#66b561',
     'bluegreen': '#00b2bf',
     'midblue': '#2c6179',
     'rose': '#b0503f',
     'gold': '#977118'}



## Plot color strips from hex lists to see colors

You can plot a list of hex codes using the `plot_from_hex_list()` function. In the following example, we pass the values of the key colors to see them. The plot includes the HLS values, a grey values, and the hex code. 


```python
morpc.color.plot_from_hex_list(morpc.color.get_colors().KEYS.values())
```


    
![png](/morpc-color-demo/output_11_0.png)
    


## Sequential color gradients for each color

Each color has an associated gradient. These gradients can be returned using the `.SEQ()` function. Simply pass the color name to the funcion.


```python
morpc.color.plot_from_hex_list(morpc.color.get_colors().SEQ('midblue').hex_list)
```


    
![png](/morpc-color-demo/output_14_0.png)
    



```python
for color in morpc.color.get_colors().KEYS.keys():
    morpc.color.plot_from_hex_list(morpc.color.get_colors().SEQ(color).hex_list)
```


    
![png](/morpc-color-demo/output_15_0.png)
    



    
![png](/morpc-color-demo/output_15_1.png)
    



    
![png](/morpc-color-demo/output_15_2.png)
    



    
![png](/morpc-color-demo/output_15_3.png)
    



    
![png](/morpc-color-demo/output_15_4.png)
    



    
![png](/morpc-color-demo/output_15_5.png)
    



    
![png](/morpc-color-demo/output_15_6.png)
    



    
![png](/morpc-color-demo/output_15_7.png)
    


Limit the number of colors returned in the gradient by passing an integer 1 through 12 to the `n = ` attribute.


```python
morpc.color.plot_from_hex_list(morpc.color.get_colors().SEQ('gold', 4).hex_list)
```


    
![png](/morpc-color-demo/output_17_0.png)
    


## Two color sequential gradients

Pass a list of two color names to `.SEQ2()` method to get a split gradient. 


```python
morpc.color.plot_from_hex_list(morpc.color.get_colors().SEQ2(['gold', 'darkblue']).hex_list)
```


    
![png](/morpc-color-demo/output_20_0.png)
    



```python
morpc.color.plot_from_hex_list(morpc.color.get_colors().SEQ2(['rose', 'blue']).hex_list)
```


    
![png](/morpc-color-demo/output_21_0.png)
    


## Three color sequential gradients

The same can be done with three colors using `.SEQ3()` method.


```python
morpc.color.plot_from_hex_list(morpc.get_colors().SEQ3(['gold', 'darkgreen', 'darkblue']).hex_list)
```


    
![png](/morpc-color-demo/output_24_0.png)
    


## Color maps

Using any method, you can return a color map in the form of the gradient using the `.cmap` instance.


```python
morpc.color.get_colors().SEQ3(['gold', 'darkgreen', 'darkblue']).cmap
```




<div style="vertical-align: middle;"><strong>my_cmp</strong> </div><div class="cmap"><img alt="my_cmp colormap" title="my_cmp" style="border: 1px solid #555;" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAgAAAABACAYAAABsv8+/AAAAFXRFWHRUaXRsZQBteV9jbXAgY29sb3JtYXAlV7erAAAAG3RFWHREZXNjcmlwdGlvbgBteV9jbXAgY29sb3JtYXBswK9PAAAAMXRFWHRBdXRob3IATWF0cGxvdGxpYiB2My4xMC4zLCBodHRwczovL21hdHBsb3RsaWIub3Jnhnp4VQAAADN0RVh0U29mdHdhcmUATWF0cGxvdGxpYiB2My4xMC4zLCBodHRwczovL21hdHBsb3RsaWIub3JnI15roQAAAjhJREFUeJzt1sFSgzAARdGo//+j7hy3hThKCRImgDPu3jkbTEkC02J7Xz4/3msppdQ6fx++/3gelmMp63h0ft6Pu2Mtg3VX529e98/7Pvc73n8/fx7st18/ntefH123v6+7+432X8fTczztzm+v78fb+v+af2+fv+77KG8/x6m+LseyHpfXH924nX/Ob+vbvMHrdT8e7rte9+791PPrzu0xXv6Yu+d3Prw+n867Ht9c3/4f/+f6te1XzsfL8Nf/w735h+scXt+v2w539z2fv36Q62PcPtip7h7rbd5+XWmP//l+7fx0vl+73nSxbnT9fr/tDTl9H4/jbn33XDXd+3z8/i+D34ub+17Mq/3vWbv//nu8m3fxO3V8v/rrnP+eHu63fbCj64/ub1m3fOsAAFEEAAAEEgAAEEgAAEAgAQAAgQQAAAQSAAAQSAAAQCABAACBBAAABBIAABBIAABAIAEAAIEEAAAEEgAAEEgAAEAgAQAAgQQAAAQSAAAQSAAAQCABAACBBAAABBIAABBIAABAIAEAAIEEAAAEEgAAEEgAAEAgAQAAgQQAAAQSAAAQSAAAQCABAACBBAAABBIAABBIAABAIAEAAIEEAAAEEgAAEEgAAEAgAQAAgQQAAAQSAAAQSAAAQCABAACBBAAABBIAABBIAABAIAEAAIEEAAAEEgAAEEgAAEAgAQAAgQQAAAQSAAAQSAAAQCABAACBBAAABBIAABBIAABAIAEAAIEEAAAEEgAAEOgLO0UR3IDRAN0AAAAASUVORK5CYII="></div><div style="vertical-align: middle; max-width: 514px; display: flex; justify-content: space-between;"><div style="float: left;"><div title="#f3f1eaff" style="display: inline-block; width: 1em; height: 1em; margin: 0; vertical-align: middle; border: 1px solid #555; background-color: #f3f1eaff;"></div> under</div><div style="margin: 0 auto; display: inline-block;">bad <div title="#00000000" style="display: inline-block; width: 1em; height: 1em; margin: 0; vertical-align: middle; border: 1px solid #555; background-color: #00000000;"></div></div><div style="float: right;">over <div title="#0c1620ff" style="display: inline-block; width: 1em; height: 1em; margin: 0; vertical-align: middle; border: 1px solid #555; background-color: #0c1620ff;"></div></div></div>



## Diverging color gradients

Use the `.DIV()` method can be used to create diverging gradients and color maps. 


```python
morpc.color.plot_from_hex_list(morpc.get_colors().DIV(['gold','darkblue']).hex_list)
```


    
![png](/morpc-color-demo/output_30_0.png)
    



```python
morpc.color.plot_from_hex_list(morpc.color.get_colors().DIV(['rose','darkgreen']).hex_list)
```


    
![png](/morpc-color-demo/output_31_0.png)
    


## Qualitative color groups

Use the `.QUAL()` method to return groups for qualitative data. It selects a number of grouped lightness variations of each color. 


```python
morpc.color.plot_from_hex_list(morpc.color.get_colors().QUAL(20).hex_list)
```


    
![png](/morpc-color-demo/output_34_0.png)
    


## Testing color maps for color blindness accessibility


```python
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(19680801)
data = np.random.randn(30, 30)
fig, ax = plt.subplots()
psm = ax.pcolormesh(data, cmap=morpc.color.get_colors().DIV(['gold', 'bluegreen']).cmap, rasterized=True, vmin=-4, vmax=4)
fig.colorbar(psm, ax=ax)
```




    <matplotlib.colorbar.Colorbar at 0x1baaaa349e0>




    
![png](/morpc-color-demo/output_36_1.png)
    



```python
from daltonize import daltonize
daltonize.simulate_mpl(fig, color_deficit='p')
```




    
![png](/morpc-color-demo/output_37_0.png)
    



