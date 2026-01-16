from .color import *
import itertools

NAMES = [color for color in get_colors().morpc_colors]

SEQ = {}
for color in NAMES:
    SEQ[color] = get_colors().SEQ(color)
    SEQ[f"{color}_r"] = get_colors().SEQ(color)

SEQ2_ALL = {}
for NAME in NAMES:
    for NAME2 in NAMES:
        if NAME != NAME2:
            SEQ2_ALL[f"{NAME}-{NAME2}"] = get_colors().SEQ2([NAME, NAME2])

SEQ2_LIST = ['blue-lightgreen', 'bluegreen-darkblue', 'bluegreen-purple', 'yellow-darkblue', 'yellow-blue', 'yellow-darkgreen', 'yellow-lightgreen', 'yellow-red', 'yellow-purple',
            'tan-lightgreen', 'tan-lightgrey', 'red-blue', 'red-lightgreen', 'purple-blue', 'purple-lightgrey', 'lightgreen-darkgreen']
SEQ2 = {}
for NAMES in SEQ2_ALL:
    NAME1, NAME2 = NAMES.split('-')
    SEQ2[f"{NAME1}-{NAME2}"] = get_colors().SEQ2([NAME1, NAME2])
    SEQ2[f"{NAME2}-{NAME1}"] = get_colors().SEQ2([NAME2, NAME1])

SEQ3 = {}
SEQ3['yellow-lightgreen-darkblue'] = get_colors().SEQ3(['yellow','lightgreen','darkblue'])
SEQ3['yellow-red-purple'] = get_colors().SEQ3(['yellow','red','purple'])
SEQ3['purple-bluegreen-darkblue'] = get_colors().SEQ3(['purple','bluegreen','darkblue'])
SEQ3['lightgrey-lightgreen-darkgreen'] = get_colors().SEQ3(['purple','bluegreen','darkblue'])
SEQ3['red-yellow-darkgreen'] = get_colors().SEQ3(['red','yellow','darkgreen'])

DIV_LIST = ['red-yellow-lightgreen', 'red-yellow-blue', 'red-lightgrey-blue', 'yellow-lightgrey-darkblue', 'lightgreen-lightgrey-purple', 'darkgreen-lightgrey-darkblue']
DIV = {}
for NAMES in DIV_LIST:
    NAME1, NAME2, NAME3 = NAMES.split('-')
    DIV[NAMES] = get_colors().DIV([NAME1, NAME2, NAME3])

QUAL = {}
QUAL['morpc'] = [get_colors().KEYS[color] for color in ['lightgreen', 'darkblue', 'bluegreen', 'darkgreen', 'blue', 'midblue', 'lightgrey', 'darkgrey']]
QUAL['morpc_ext'] = [get_colors().KEYS[color] for color in ['lightgreen', 'darkblue', 'bluegreen', 'darkgreen', 'red', 'blue', 'yellow', 'midblue', 'purple', 'tan']]

QUAL['light'] = []
for color in ['lightgreen', 'darkblue', 'bluegreen', 'darkgreen', 'red', 'blue', 'yellow', 'midblue', 'purple', 'tan']:
    key = get_colors().morpc_colors[color]['key']['position'] - 1
    if  7 < key > 5:
        light = key-3
    if key >= 7:
        light = key - 4
    else:
        light = key-2
    QUAL['light'].append(get_colors().morpc_colors[color]['gradient']['hex'][light])

QUAL['dark'] = []
for color in ['lightgreen', 'darkblue', 'bluegreen', 'darkgreen', 'red', 'blue', 'yellow', 'midblue', 'purple', 'tan']:
    key = get_colors().morpc_colors[color]['key']['position'] - 1
    if  7 < key > 5:
        dark = key+2
    if key == 7:
        dark = key+2
    if key >= 8:
        dark = key+1
    else:
        dark = key+3
    QUAL['dark'].append(get_colors().morpc_colors[color]['gradient']['hex'][dark])

QUAL['paired'] = []
for i in range(len(QUAL['morpc_ext'])):
    QUAL['paired'].append(QUAL['morpc_ext'][i])
    QUAL['paired'].append(QUAL['light'][i])

QUAL['triples'] = []
for i in range(len(QUAL['morpc_ext'])):
    QUAL['triples'].append(QUAL['dark'][i])
    QUAL['triples'].append(QUAL['morpc_ext'][i])
    QUAL['triples'].append(QUAL['light'][i])
