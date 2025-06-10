from .color import *
import itertools

NAMES = [color for color in get_colors().morpc_colors]

SEQ = {}
for color in NAMES:
    SEQ[color] = get_colors().SEQ(color)
    SEQ[f"{color}_r"] = get_colors().SEQ(color)

SEQ2 = {}
for NAME in NAMES:
    for NAME2 in NAMES:
        if NAME != NAME2:
            SEQ2[f"{NAME}-{NAME2}"] = get_colors().SEQ2([NAME, NAME2])

SEQ3 = {}
SEQ3['yellow-lightgreen-darkblue'] = get_colors().SEQ3(['yellow','lightgreen','darkblue'])
SEQ3['yellow-red-purple'] = get_colors().SEQ3(['yellow','red','purple'])
SEQ3['purple-bluegreen-darkblue'] = get_colors().SEQ3(['purple','bluegreen','darkblue'])
SEQ3['lightgrey-lightgreen-darkgreen'] = get_colors().SEQ3(['purple','bluegreen','darkblue'])

QUAL = {}
QUAL['morpc'] = [get_colors().KEYS[color] for color in ['darkblue', 'lightgreen', 'blue', 'darkgreen', 'bluegreen', 'midblue']]
QUAL['morpc_ext'] = [get_colors().KEYS[color] for color in ['darkblue', 'lightgreen', 'blue', 'red', 'yellow', 'darkgreen', 'bluegreen', 'midblue', 'purple', 'tan']]
QUAL['light'] = []
for color in ['darkblue', 'lightgreen', 'blue', 'red', 'yellow', 'darkgreen', 'bluegreen', 'midblue', 'purple', 'tan']:
    key = get_colors().morpc_colors[color]['key']['position'] - 1
    if  7 < key > 5:
        light = key-3
    if key >= 7:
        light = key - 4
    else:
        light = key-2
    QUAL['light'].append(get_colors().morpc_colors[color]['gradient']['hex'][light])
QUAL['dark'] = []
for color in ['darkblue', 'lightgreen', 'blue', 'red', 'yellow', 'darkgreen', 'bluegreen', 'midblue', 'purple', 'tan']:
    key = get_colors().morpc_colors[color]['key']['position'] - 1
    if  7 < key > 5:
        dark = key+2
    if key >= 7:
        dark = key+2
    else:
        dark = key+3
    QUAL['dark'].append(get_colors().morpc_colors[color]['gradient']['hex'][dark])