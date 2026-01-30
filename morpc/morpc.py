import json
import pandas as pd


# PANDAS_EXPORT_ARGS_OVERRIDE is a dictionary indexed by tabular output format (csv, xlsx, etc.) whose
# keys contain overrides for the default values for the arguments for the pandas functions used to
# export data in those formats.  For example, the values associated with the "csv" key are used
# by morpc.write_table() to override the defaults for pandas.DataFrame.to_csv().  The primary need
# for this is to force text files to be written with Windows-style line endings (i.e. "\r\n") to 
# ensure that their checksums can be interpreted correctly when the file is validated.
PANDAS_EXPORT_ARGS_OVERRIDE = {
    "csv": {
        "lineterminator": "\r\n",
    },
    "xlsx": None
}

# Conversion factors
# The following constants represent commonly used conversion factors for various units of measure
## Area
CONST_SQFT_PER_ACRE = 43560  # Square feet per acre

# TODO: add other conversion rates

# Commonly used geographic identifiers
# The following are assigned by the U.S. Census Bureau
CONST_COLUMBUS_CBSA_ID = '18140'
CONST_OHIO_STATE_ID = '39'
CONST_OHIO_REGION_ID = '2'      # Midwest
CONST_OHIO_DIVISION_ID = '3'    # East North Central

# Functions to fetch and define geographic identifiers and scopes
def get_state_ids():
    """
    Returns a list of all state FIPS codes.
    """
    import requests
    url = 'https://api.census.gov/data/2023/geoinfo?get=NAME&for=state:*'

    r = requests.get(url)
    data = r.json()
    # convert to dictionary
    state_dict = {item[0].lower(): pd.to_numeric(item[1]) for item in data[1:]}
    r.close()

    return state_dict

# State name and abbreviation lookups
CONST_STATE_NAME_TO_ID = get_state_ids()
CONST_STATE_ID_TO_NAME = {value: key for key, value in CONST_STATE_NAME_TO_ID.items()}
CONST_STATE_NAME_TO_ABBR = {
    "alabama": "al",
    "alaska": "ak",
    "arizona": "az",
    "arkansas": "ar",
    "california": "ca",
    "colorado": "co",
    "connecticut": "ct",
    "delaware": "de",
    "florida": "fl",
    "georgia": "ga",
    "hawaii": "hi",
    "idaho": "id",
    "illinois": "il",
    "indiana": "in",
    "iowa": "ia",
    "kansas": "ks",
    "kentucky": "ky",
    "louisiana": "la",
    "maine": "me",
    "maryland": "md",
    "massachusetts": "ma",
    "michigan": "mi",
    "minnesota": "mn",
    "mississippi": "ms",
    "missouri": "mo",
    "montana": "mt",
    "nebraska": "ne",
    "nevada": "nv",
    "new hampshire": "nh",
    "new jersey": "nj",
    "new mexico": "nm",
    "new york": "ny",
    "north carolina": "nc",
    "north dakota": "nd",
    "ohio": "oh",
    "oklahoma": "ok",
    "oregon": "or",
    "pennsylvania": "pa",
    "rhode island": "ri",
    "south carolina": "sc",
    "south dakota": "sd",
    "tennessee": "tn",
    "texas": "tx",
    "utah": "ut",
    "vermont": "vt",
    "virginia": "va",
    "washington": "wa",
    "west virginia": "wv",
    "wisconsin": "wi",
    "wyoming": "wy",
    "district of columbia": "dc"
}
CONST_STATE_ABBR_TO_NAME = {value: key for key, value in CONST_STATE_NAME_TO_ABBR.items()}

CONST_STATE_ABBR_TO_ID = {value: CONST_STATE_NAME_TO_ID[key] for key, value in CONST_STATE_NAME_TO_ABBR.items()}


# Region definitions
# The following lists represent various definitions for "Central Ohio" based on collections of counties.
# The long form keys (e.g. "7-County Region") are deprecated in favor of the short-form keys (e.g. "REGION7")
# which correspond to the hierarchy strings in the sumlevel descriptions below.  Long form keys should not be
# used and should be replaced with short form keys in existing scripts when updates are made.
CONST_REGIONS = {}
CONST_REGIONS["REGION7"] = ["Delaware", "Fairfield", "Franklin", "Licking", "Madison", "Pickaway", "Union"]
CONST_REGIONS["7-County Region"] = CONST_REGIONS["REGION7"]
CONST_REGIONS["REGION10"] = CONST_REGIONS["REGION7"] + ["Knox", "Marion", "Morrow"]
CONST_REGIONS["10-County Region"] = CONST_REGIONS["REGION10"]
CONST_REGIONS["REGION15"] = CONST_REGIONS["REGION10"] + ["Fayette", "Hocking", "Logan", "Perry", "Ross"]
CONST_REGIONS["15-County Region"] = CONST_REGIONS["REGION15"]
CONST_REGIONS["REGIONCORPO"] = ["Fairfield", "Knox", "Madison", "Marion", "Morrow", "Pickaway", "Union"]
CONST_REGIONS["CORPO Region"] = CONST_REGIONS["REGIONCORPO"]
CONST_REGIONS["REGIONONECBUS"] = CONST_REGIONS["REGION10"] + ["Logan"]
CONST_REGIONS["OneColumbus Region"] = CONST_REGIONS["REGIONONECBUS"]
CONST_REGIONS["REGIONCEDS"] = CONST_REGIONS["REGION10"] + ["Logan"]
CONST_REGIONS["CEDS Region"] = CONST_REGIONS["REGIONCEDS"]
CONST_REGIONS["CBSA"] = CONST_REGIONS["REGION7"] + ["Hocking","Morrow","Perry"]

# Region identifiers
# Note that the Columbus MSA already has a GEOID that is defined by the Census Bureau.  See CONST_COLUMBUS_MSA_ID above.
# It is duplicated here to allow for a consistent interface to obtain the GEOID for all regions.
CONST_REGIONS_GEOID = {}
CONST_REGIONS_GEOID["REGION15"] = "001"
CONST_REGIONS_GEOID["REGION10"] = "001"
CONST_REGIONS_GEOID["REGION7"] = "001"
CONST_REGIONS_GEOID["REGIONCORPO"] = "001"
CONST_REGIONS_GEOID["REGIONCEDS"] = "001"
CONST_REGIONS_GEOID["REGIONONECBUS"] = "001"
CONST_REGIONS_GEOID["REGIONMPO"] = "001"
CONST_REGIONS_GEOID["REGIONTDM"] = "001"
CONST_REGIONS_GEOID["CBSA"] = CONST_COLUMBUS_CBSA_ID

# The following regions are comprised of collections of whole counties. Not all region definitions are county-based,
# for example the MPO region.
CONST_REGIONS_COUNTYBASED = ["REGION15","REGION10","REGION7","REGIONCEDS","REGIONCORPO","REGIONONECBUS","CBSA"]

# County name abbreviations
## CONST_COUNTY_ABBREV maps the full county name to its three-letter abbreviation
CONST_COUNTY_ABBREV = {
    'Delaware': 'DEL',
    'Fairfield': 'FAI',
    'Fayette': 'FAY',
    'Franklin': 'FRA',
    'Hocking': 'HOC',
    'Knox': 'KNO',
    'Licking': 'LIC',
    'Logan': 'LOG',
    'Madison': 'MAD',
    'Marion': 'MAR',
    'Morrow': 'MRW',    # ODOT uses this abbreviation, but sometimes 'MOR' is used instead
    'Perry': 'PER',
    'Pickaway': 'PIC',
    'Ross': 'ROS',
    'Union': 'UNI'
}

## CONST_COUNTY_EXPAND inverts the above map, mapping the three-letter county abbreviation to its full name
CONST_COUNTY_EXPAND = {value: key for key, value in CONST_COUNTY_ABBREV.items()}

# County identifiers (Census GEOID)
## CONST_COUNTY_NAME_TO_ID maps the county name to its GEOID
CONST_COUNTY_NAME_TO_ID = {
    'Delaware': '39041',
    'Fairfield': '39045',
    'Fayette': '39047',
    'Franklin': '39049',
    'Hocking': '39073',
    'Knox': '39083',
    'Licking': '39089',
    'Logan': '39091',
    'Madison': '39097',
    'Marion': '39101',
    'Morrow': '39117',
    'Perry': '39127',
    'Pickaway': '39129',
    'Ross': '39141',
    'Union': '39159'
}

## CONST_COUNTY_ID_TO_NAME inverts the above map, mapping the county GEOID to its name
CONST_COUNTY_ID_TO_NAME = {value: key for key, value in CONST_COUNTY_NAME_TO_ID.items()}

# Branding
## CONST_MORPC_COLORS maps human-readable descriptions of the MORPC brand colors to their hex codes
CONST_MORPC_COLORS = {
    "darkblue": "#2e5072",
    "blue": "#0077bf",
    "darkgreen": "#2c7f68",
    "lightgreen": "#66b561",
    "bluegreen": "#00b2bf",
    "midblue": "#2c6179"
}

CONST_MORPC_COLORS_EXP = {
    'darkblue': '#2e5072',
    'blue': '#0077bf',
    'darkgreen': '#2c7f68',
    'lightgreen': '#66b561',
    'bluegreen': '#00b2bf',
    'midblue': '#2c6179',
    'tan': '#c4a499',
    'rust': '#8c3724',
    'peach':'#ef7e58',
    'red': '#d6061a',
    'gold': '#ba881a',
    'brown': '#694e0b'
 }

# TODO: add more colors to the morpc specific color and define colors for plots

CONST_COLOR_CYCLES = {
    "morpc": list(CONST_MORPC_COLORS.values()),
    # The following corresponds to the matplotlib "Tableau" color palette, which is the default for pandas.
    # See https://matplotlib.org/stable/gallery/color/named_colors.html
    "matplotlib": ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'],
    # The following palettes are from ColorBrewer2. See https://colorbrewer2.org/
    "bold": ['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a','#ffff99','#b15928'],
    "pastel": ['#8dd3c7','#ffffb3','#bebada','#fb8072','#80b1d3','#fdb462','#b3de69','#fccde5','#d9d9d9','#bc80bd','#ccebc5','#ffed6f'],
    "printfriendly": ['#8dd3c7','#ffffb3','#bebada','#fb8072','#80b1d3','#fdb462','#b3de69','#fccde5'],
    "colorblind": ['#a6cee3','#1f78b4','#b2df8a','#33a02c'],
    # The following pallettes are from Colorgorical http://vrl.cs.brown.edu/color
    # distanceX are sets of 20 colors with perceptual distance set to max priority and other factors set to zero priority
    # pairingX are sets of 20 colors with pairing preference set to max priority and other factors set to zero priority
    "distance1": ["#35618f", "#17f46f", "#8a2f6b", "#abd533", "#b32df9", "#3f862d", "#f287d0", "#91e7a4", "#be0332", "#4be8f9", "#f90da0", "#dec651", "#5f4ac2", "#fe8f06", "#11a0aa", "#ff7074", "#b3d9fa", "#883c10", "#f2a68c", "#464a15"],
    "distance2": ["#96e97c", "#860967", "#6ae7e6", "#1c5b5a", "#8dbcf9", "#2c457d", "#fa79f5", "#359721", "#fa2e55", "#46f33e", "#7d2b22", "#f3a4a8", "#32a190", "#1932bf", "#cc96eb", "#7c1cee", "#e3c60b", "#c0710c", "#d3d6c1", "#445a06"],
    "distance3": ["#208eb7", "#902d54", "#48d17f", "#f53176", "#63e118", "#ef6ade", "#097b35", "#a50fa9", "#bce333", "#7212ff", "#b9cda1", "#553096", "#f8ba7c", "#294775", "#fb7810", "#8e80fb", "#6f7d43", "#f2a1c3", "#20d8fd", "#fe2b1c"],
    "pairing1": ["#68affc", "#4233a6", "#85e5dd", "#2a6866", "#66de78", "#15974d", "#b4d170", "#683c00", "#ca7e54", "#821f48", "#f65b68", "#ebcecb", "#6a7f2f", "#fece5f", "#9f2108", "#fe5900", "#2c457d", "#8b6fed", "#ffacec", "#db11ac"],
    "pairing2": ["#35618f", "#17f46f", "#8a2f6b", "#abd533", "#b32df9", "#3f862d", "#f287d0", "#91e7a4", "#be0332", "#4be8f9", "#f90da0", "#dec651", "#5f4ac2", "#fe8f06", "#11a0aa", "#ff7074", "#b3d9fa", "#883c10", "#f2a68c", "#464a15"],
    "pairing3": ["#96e97c", "#860967", "#6ae7e6", "#1c5b5a", "#8dbcf9", "#2c457d", "#fa79f5", "#359721", "#fa2e55", "#46f33e", "#7d2b22", "#f3a4a8", "#32a190", "#1932bf", "#cc96eb", "#7c1cee", "#e3c60b", "#c0710c", "#d3d6c1", "#445a06"]
}
keys = list(CONST_COLOR_CYCLES.keys())
for key in keys:
    value = json.loads(json.dumps(CONST_COLOR_CYCLES[key]))
    value.reverse()
    CONST_COLOR_CYCLES["{}_r".format(key)] = value


SUMLEVEL_DESCRIPTIONS = {
    '010': {
        "singular":"United States",
        "plural":"United States",
        "hierarchy_string":"US",
        "authority":"census",
        "idField":"NATIONID",
        "nameField":"NATION",
        "censusQueryName": "us",
        "censusRestAPI_layername": None,
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{NATION}"
    },
    '020': {
        "singular":"Census region",
        "plural":"Census regions",
        "hierarchy_string":"CENSUSREGION",
        "authority":"census",
        "idField":"REGIONID",
        "nameField":"REGION",
        "censusQueryName": "region",
        "censusRestAPI_layername": 'regions',
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{REGION}"
    },
    '030': {
        "singular":"division",
        "plural":"divisions",
        "hierarchy_string":"DIVISION",
        "authority":"census",
        "idField":"DIVISONID",
        "nameField":"DIVISION",
        "censusQueryName": "division",
        "censusRestAPI_layername": 'divisions',
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{DIVISION}"
    },
    '040': {
        "singular":"state",
        "plural":"states",
        "hierarchy_string":"STATE",
        "authority":"census",
        "idField":"STATEFP",
        "nameField":"STATE",
        "censusQueryName": "state",
        "censusRestAPI_layername": 'states',
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{STATE}"
    },
    '050': {
        "singular":"county",
        "plural":"counties",
        "hierarchy_string":"COUNTY",
        "authority":"census",
        "idField":"COUNTYFP",
        "nameField":"COUNTY",
        "censusQueryName": "county",
        "censusRestAPI_layername": 'counties',
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{STATE}{COUNTY}"
    },
    '060': {
        "singular":"county subdivision",
        "plural":"county subdivisions",
        "hierarchy_string":"COUNTY-COUSUB",
        "authority":"census",
        "idField":"COUSUBFP",
        "nameField":"COUSUB",
        "censusQueryName": "county subdivision",
        "censusRestAPI_layername": None,
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{STATE}{COUNTY}{COUSUB}"
    },
    '070': {
        "singular":"county subdivision part/remainder",
        "plural":"county subdivision parts/remainders",
        "hierarchy_string":"COUNTY-TOWNSHIP-REMAINDER",
        "authority":"census",
        "idField":"COUSUBPARTID",
        "nameField":"COUSUBPART",
        "censusQueryName": "county subdivision/remainder (or part)",
        "censusRestAPI_layername": 'county subdivisions',
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{STATE}{COUNTY}{COUSUB}{PLACEREM}"

    },
    # NOTE: Some references use SUMLEVEL 750 for block in the PL94 data, but the API
    # uses SUMLEVEL 100
    '100': {
        "singular":"census block",
        "plural":"census blocks",
        "hierarchy_string":"COUNTY-TRACT-BG-BLOCK",
        "authority":"census",
        "idField":"BLOCKCE",
        "nameField":None,
        "censusQueryName": None,
        "censusRestAPI_layername": 'blocks',
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{STATE}{TRACT}{BLKGRP}{BLOCK}"
    },
    '140': {
        "singular":"tract",
        "plural":"tracts",
        "hierarchy_string":"COUNTY-TRACT",
        "authority":"census",
        "idField":"TRACTCE",
        "nameField":None,
        "censusQueryName": "tract",
        "censusRestAPI_layername": 'tracts',
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{STATE}{TRACT}"
    },
    '150': {
        "singular":"block group",
        "plural":"block groups",
        "hierarchy_string":"COUNTY-TRACT-BG",
        "authority":"census",
        "idField":"BLKGRPCE",
        "nameField":None,
        "censusQueryName": "block group",
        "censusRestAPI_layername": 'block groups',
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{STATE}{TRACT}{BLKGRP}"
    },
    '155': {
        "singular":"place county part",
        "plural":"place county parts",
        "hierarchy_string":"PLACE-COUNTY",
        "authority":"census",
        "idField":"PLACEPARTID",
        "nameField":"PLACEPART",
        "censusQueryName": "county (or part)",
        "censusRestAPI_layername": None,
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{STATE}{PLACE}{COUNTY}"
    },
    '160': {
        "singular":"place",
        "plural":"places",
        "hierarchy_string":"PLACE",
        "authority":"census",
        "idField":"PLACEFP",
        "nameField":"PLACE",
        "censusQueryName": "place",
        "censusRestAPI_layername": 'incorporated places',
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{STATE}{PLACE}"
    },
    '310': {
        "singular":"core-based statistical area",
        "plural":"core-based statistical areas",
        "hierarchy_string":"CBSA",
        "authority":"census",
        "idField":"CBAFP",
        "nameField":"CBSA",
        "censusQueryName": "metropolitan statistical area/micropolitan statistical area",
        "censusRestAPI_layername": 'metropolitan statistical areas',
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{CBSA}"
    },
    '330': {
        "singular":"combined statistical area",
        "plural":"combined statistical areas",
        "hierarchy_string":"CSA",
        "authority":"census",
        "idField":"CSAFP",
        "nameField":"CSA",
        "censusQueryName": "combined statistical area",
        "censusRestAPI_layername": 'combined statistical areas',
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{CSA}"
    },
    '400': {
        "singular":"urban area",
        "plural":"urban areas",
        "hierarchy_string":"URBANAREA",
        "authority":"census",
        "idField":"UACE",
        "nameField":"URBANAREA",
        "censusQueryName": "urban area",
        "censusRestAPI_layername": 'urban areas',
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{UA}"
    },
    '500': {
        "singular":"congressional district",
        "plural":"congressional districts",
        "hierarchy_string":"CONGRESS",
        "authority":"census",
        "idField":"CDFP",  # Census uses CDNNNFP where NNN is the congressional session number
        "nameField":"CONGRESS",
        "censusQueryName": "congressional district",
        "censusRestAPI_layername": 'congressional districts',
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{STATE}{CD}"
    },
    '610': {
        "singular":"state senate district",
        "plural":"state senate districts",
        "hierarchy_string":"STATESENATE",
        "authority":"census",
        "idField":"SLDUST",
        "nameField":None,
        "censusQueryName": "state legislative district (upper chamber)",
        "censusRestAPI_layername": 'state legislative districts - upper',
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{STATE}{SLDU}"
    },
    '620': {
        "singular":"state house district",
        "plural":"state house districts",
        "hierarchy_string":"STATEHOUSE",
        "authority":"census",
        "idField":"SLDLST",
        "nameField":None,
        "censusQueryName": "state legislative district (lower chamber)",
        "censusRestAPI_layername": 'state legislative districts - lower',
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{STATE}{SLDL}"
    },
    '795': {
        "singular":"public use microdata area",
        "plural":"public use microdata areas",
        "hierarchy_string":"PUMA",
        "authority":"census",
        "idField":"PUMACE",
        "nameField":"PUMA",
        "censusQueryName": "public use microdata area",
        "censusRestAPI_layername": 'public use microdata areas',
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{STATE}{PUMA}"
    },
    ### Jordan removed 2025-12 due to not finding support by Census
    # '850': {
    #     "singular":"zip code tabulation area",
    #     "plural":"zip code tabulation areas",
    #     "hierarchy_string":"ZCTA3",
    #     "authority":"census",
    #     "idField":"ZCTA3CE",
    #     "nameField":None,
    #     "censusQueryName": None,
    #     "censusRestAPI_layername": None
    # },
    '860': {
        "singular":"zip code tabulation area",
        "plural":"zip code tabulation areas",
        "hierarchy_string":"ZCTA5",
        "authority":"census",
        "idField":"ZCTA5CE",
        "nameField":None,
        "censusQueryName": "zip code tabulation area",
        "censusRestAPI_layername": '2020 zip code tabulation areas',
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{ZCTA}"
    },
    '861': {
        'singular': 'zip code',
        'plural': 'Zip codes',
        'hierarchy_string': 'ZIPCODE',
        'authority': 'census',
        'idField': 'ZIPCODE',
        'nameField': None,
        'censusQueryName': None,
        'censusRestAPI_layername': None,
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{ZIPCODE}"
    },
    '930': {
        "singular":"MPO region",
        "plural":"MPO regions",
        "hierarchy_string":"CENSUSMPOREGION",
        "authority":"census",
        "idField":"MPOREGIONID",
        "nameField":"MPOREGION",
        "censusQueryName": None,
        "censusRestAPI_layername": None,
        "geoidfq_format": None
    },
    '950': {
        "singular":"elementary school district",
        "plural":"elementary school districts",
        "hierarchy_string":"ELSD",
        "authority":"census",
        "idField":"ELSDLEA",
        "nameField":"SCHOOLDELEM",
        "censusQueryName": "school district (elementry)",
        "censusRestAPI_layername": 'elementary school districts',
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{STATE}{SDELM}"
    },
    '960': {
        "singular":"high school district",
        "plural":"high school districts",
        "hierarchy_string":"SCSD",
        "authority":"census",
        "idField":"SCSDLEA",
        "nameField":"SCHOOLDHIGH",
        "censusQueryName": "school district (secondary)",
        "censusRestAPI_layername": 'secondary school districts',
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{STATE}{SDSEC}"
    },
    '970': {
        "singular":"unified school district",
        "plural":"unified school districts",
        "hierarchy_string":"UNSD",
        "authority":"census",
        "idField":"UNSDLEA",
        "nameField":"SCHOOLD",
        "censusQueryName": "school district (unified)",
        "censusRestAPI_layername": 'unified school districts',
        "geoidfq_format": "{SUMLEVEL}{VARIANT}{COMPONENT}US{STATE}{SDUNI}"
    },
    'M01': {
        "singular":"MORPC 15-county region",
        "plural":"MORPC 15-county region",
        "hierarchy_string":"REGION15",
        "authority":"morpc",
        "idField":"REGION15ID",
        "nameField":"REGION15",
        "censusQueryName": "region15",
        "censusRestAPI_layername": None
    },
    'M02': {
        "singular":"MORPC 10-county region",
        "plural":"MORPC 10-county region",
        "hierarchy_string":"REGION10",
        "authority":"morpc",
        "idField":"REGION10ID",
        "nameField":"REGION10",
        "censusQueryName": "region10",
        "censusRestAPI_layername": None
    },
    'M03': {
        "singular":"MORPC 7-county region",
        "plural":"MORPC 7-county region",
        "hierarchy_string":"REGION7",
        "authority":"morpc",
        "idField":"REGION7ID",
        "nameField":"REGION7",
        "censusQueryName": "region7",
        "censusRestAPI_layername": None

    },
    'M04': {
        "singular":"MORPC CORPO region",
        "plural":"MORPC CORPO region",
        "hierarchy_string":"REGIONCORPO",
        "authority":"morpc",
        "idField":"REGIONCORPOID",
        "nameField":"REGIONCORPO",
        "censusQueryName": "regioncorpo",
        "censusRestAPI_layername": None
    },
    'M05': {
        "singular":"MORPC CEDS region",
        "plural":"MORPC CEDS region",
        "hierarchy_string":"REGIONCEDS",
        "authority":"morpc",
        "idField":"REGIONCEDSID",
        "nameField":"REGIONCEDS",
        "censusQueryName": "regionceds",
        "censusRestAPI_layername": None
    },
    'M06': {
        "singular":"MORPC MPO region",
        "plural":"MORPC MPO region",
        "hierarchy_string":"REGIONMPO",
        "authority":"morpc",
        "idField":"REGIONMPOID",
        "nameField":"REGIONMPO",
        "censusQueryName": "regionmpo",
        "censusRestAPI_layername": None
    },
    'M07': {
        "singular":"MORPC TDM region",
        "plural":"MORPC TDM region",
        "hierarchy_string":"REGIONTDM",
        "authority":"morpc",
        "idField":"REGIONTDMID",
        "nameField":"REGIONTDM",
        "censusQueryName": "regiontdm",
        "censusRestAPI_layername": None
    },
    'M08': {
        "singular":"OneColumbus region",
        "plural":"OneColumbus region",
        "hierarchy_string":"REGIONONECBUS",
        "authority":"morpc",
        "idField":"REGIONONECBUSID",
        "nameField":"REGIONONECBUS",
        "censusQueryName": 'regiononecbus',
        "censusRestAPI_layername": None
    },
    'M10': {
        "singular":"Jurisdiction",
        "plural":"Jurisdictions",
        "hierarchy_string":"JURIS",
        "authority":"morpc",
        "idField":"JURISID",
        "nameField":"JURIS",
        "censusQueryName": None,
        "censusRestAPI_layername": None
    },
    'M11': {
        "singular":"Jurisdiction county part",
        "plural":"Jurisdiction county parts",
        "hierarchy_string":"JURIS-COUNTY",
        "authority":"morpc",
        "idField":"JURISPARTID",
        "nameField":"JURISPART",
        "censusQueryName": None,
        "censusRestAPI_layername": None
    },
    'M20': {
        "singular":"Traffic analysis zone",
        "plural":"Traffic analysis zones",
        "hierarchy_string":"COUNTY-TAZ",
        "authority":"morpc",
        "idField":"TAZ2020",
        "nameField":None,
        "censusQueryName": None,
        "censusRestAPI_layername": None
    },
    'M21': {
        "singular":"Micro analysis zone",
        "plural":"Micro analysis zones",
        "hierarchy_string":"COUNTY-TAZ-MAZ",
        "authority":"morpc",
        "idField":"MAZ2020",
        "nameField":None,
        "censusQueryName": None,
        "censusRestAPI_layername": None
    },
    'M22': {
        "singular":"GridMAZ zone",
        "plural":"GridMAZ zones",
        "hierarchy_string":"COUNTY-TAZ-MAZ-GRIDMAZ",
        "authority":"morpc",
        "idField":"GridMAZ20",
        "nameField":None,
        "censusQueryName": None,
        "censusRestAPI_layername": None
    },
    # Sumlevels M23 to M29 correspond to sumlevels defined above, but are
    # derived from MORPC-maintained geographies rather than Census-maintained
    # geographies
    'M23': {  # Corresponds to 050 (COUNTY)
        "singular":"county",
        "plural":"counties",
        "hierarchy_string":"COUNTY-MORPC",
        "authority":"morpc",
        "idField":"COUNTYFP",
        "nameField":"COUNTY",
        "censusQueryName": None,
    },
    'M24': {  # Corresponds to M10 (JURIS)
        "singular":"Jurisdiction",
        "plural":"Jurisdictions",
        "hierarchy_string":"JURIS-MORPC",
        "authority":"morpc",
        "idField":"JURISID",
        "nameField":"JURIS",
        "censusQueryName": None
    },
    'M25': {  # Corresponds to M11 (JURIS-COUNTY)
        "singular":"Jurisdiction county part",
        "plural":"Jurisdiction county parts",
        "hierarchy_string":"JURIS-COUNTY-MORPC",
        "authority":"morpc",
        "idField":"JURISPARTID",
        "nameField":"JURISPART",
        "censusQueryName": None
    },
    'M26': {  # Corresponds to M16 (REGIONMPO)
        "singular":"MORPC MPO region",
        "plural":"MORPC MPO region",
        "hierarchy_string":"REGIONMPO-MORPC",
        "authority":"morpc",
        "idField":"REGIONMPOID",
        "nameField":"REGIONMPO",
        "censusQueryName": None
    },
    'M27': {  # Corresponds to M17 (REGIONTDM)
        "singular":"MORPC TDM region",
        "plural":"MORPC TDM region",
        "hierarchy_string":"REGIONTDM-MORPC",
        "authority":"morpc",
        "idField":"REGIONTDMID",
        "nameField":"REGIONTDM",
        "censusQueryName": None
    },
    'M30': {
        "singular":"SWACO region",
        "plural":"SWACO region",
        "hierarchy_string":"REGIONSWACO",
        "authority":"morpc",
        "idField":"REGIONSWACOID",
        "nameField":"REGIONSWACO",
        "censusQueryName": None
    },    
}

# TODO: include the following sumlevels

# The following summary levels are not implemented as of November 2024
# GRID1MILE
# GRIDQUARTERMILE
# COUNTY-COUSUB-SCD
# RESBLOB
# EMPBLOB
# GQBLOB
# PARCEL

# SUMLEVEL_LOOKUP provides a dictionary that maps each sumlevel hierarchy string (as defined in SUMLEVEL_DESCRIPTIONS)
# to its sumlevel code.  For example, SUMLEVEL_LOOKUP["CBSA"] == '310'.
SUMLEVEL_LOOKUP = {value["hierarchy_string"]:key for key, value in zip(SUMLEVEL_DESCRIPTIONS.keys(), SUMLEVEL_DESCRIPTIONS.values())}

SUMLEVEL_FROM_CENSUSQUERY = {value['censusQueryName']:key for key, value in SUMLEVEL_DESCRIPTIONS.items() if value['censusQueryName'] is not None}  
# HIERARCHY_STRING_LOOKUP provides a dictionary that maps each sumlevel code to its hierarchy string (as defined in
# SUMLEVEL_DESCRIPTIONS) For example, HIERARCHY_STRING_LOOKUP["310"] = "CBSA".
HIERARCHY_STRING_LOOKUP = {key:value["hierarchy_string"] for key, value in zip(SUMLEVEL_DESCRIPTIONS.keys(), SUMLEVEL_DESCRIPTIONS.values())}

HIERARCHY_STRING_FROM_SINGULAR = {name['singular']:hierarchy["hierarchy_string"] for name, hierarchy in zip(SUMLEVEL_DESCRIPTIONS.values(), SUMLEVEL_DESCRIPTIONS.values())}

# County lookup object
# Upon instantiation, this object is pre-loaded with a dataframe describing a set of counties whose scope is specified by the user.
# The object includes methods for listing the counties by their names or GEOIDs and for two-way conversion between name and GEOID.
# scope="morpc"     Default. Loads only the counties in the MORPC 15-county region (see CONST_REGIONS['15-County Region'] above)
# scope="corpo"     Loads only the counties in the CORPO region (see CONST_REGIONS['CORPO Region'] above)
# scope="ohio"      Loads all counties in Ohio
# scope="us"      Loads all counties in the United States
# TODO: As of Jan 2024, some methods are not supported for scope="us".  See details below.
class countyLookup():
    def __init__(self, scope="morpc"):
        import json
        import requests
        import pandas as pd

        # Get name, state identifier, and county identifier for all U.S. counties from the census API and convert it to a data frame
        r = requests.get("https://api.census.gov/data/2020/dec/pl?get=NAME&for=county:*", headers={"User-Agent": "Firefox"})
        records = r.json()
        columns = records.pop(0)
        df = pd.DataFrame(data=records, columns=columns)

        # Eliminate the " County" suffix in the county name
        df["COUNTY_NAME"] = df["NAME"].str.replace(" County, Ohio","")

        # Construct the nationally-unique GEOID from the state and county identifiers
        df["GEOID"] = df["state"] + df["county"]

        # Filter the counties according to the user-specified scope
        if(scope.lower() == "ohio" or scope.lower() == "oh"):
            print("Loading data for Ohio counties only")
            df = df.loc[df["state"] == '39'].copy()
        elif(scope.lower() == "us"):
            print("Loading data for all U.S. counties")
        elif(scope.lower() == "morpc" or scope.lower() == "15-county region" or scope == "REGION15"):
            print("Loading data for MORPC 15-County region only")
            df = df.loc[df["GEOID"].isin([CONST_COUNTY_NAME_TO_ID[name] for name in CONST_REGIONS["15-County Region"]])].copy()
        elif(scope in CONST_REGIONS.keys()):
            print("Loading data for region {} only".format(scope))
            df = df.loc[df["GEOID"].isin([CONST_COUNTY_NAME_TO_ID[name] for name in CONST_REGIONS[scope]])].copy()
        else:
            print("Scope specified by user is not defined: {}".format(scope))
            raise RuntimeError

        # Sort records alphabetically by county name and eliminate extraneous columns
        df = df \
            .sort_values("COUNTY_NAME") \
            .filter(items=["GEOID","COUNTY_NAME"], axis="columns")

        self.scope = scope
        self.df = df

    # Given a county name of a county, return its ID
    # NOTE: As of January 2024, this is not supported for scope="us"
    def get_id(self, name):
        """
        TODO: add docstring
        """
        if(self.scope == "us"):
            print("ERROR: countyLookup.get_id is not supported for scope='us'")
            raise RuntimeError
        df = self.df.copy().set_index("COUNTY_NAME")
        return df.at[name, "GEOID"]

    # Given the ID of a county, return its name
    # NOTE: As of January 2024, this is not supported for scope="us"
    def get_name(self, geoid):
        """
        TODO: add docstring
        """
        if(self.scope == "us"):
            print("ERROR: countyLookup.get_name is not supported for scope='us'")
            raise RuntimeError
        df = self.df.copy().set_index("GEOID")
        return df.at[geoid, "COUNTY_NAME"]

    # List the IDs of all counties in the user-specified scope
    def list_ids(self):
        """
        TODO: add docstring
        """
        return self.df["GEOID"].to_list()

    # List the names of all counties in the user-specified scope
    # NOTE: As of January 2024, this is not supported for scope="us"       
    def list_names(self):
        """
        TODO: add docstring
        """
        if(self.scope == "us"):
            print("ERROR: countyLookup.list_names is not supported for scope='us'")
            raise RuntimeError
        return self.df["COUNTY_NAME"].to_list()      

# Standard variable lookup class
# Reads the list of "standard" variables from a lookup table.  Provides dataframe access to the list of variables, as
# well as an alias cross-reference table.
class varLookup():
    def __init__(self, variableList=None, aliasList=None, context=None, dictionaryPath="../morpc-lookup/variable_dictionary.xlsx"):
        import pandas as pd
        import os
        import morpc

        dictionaryPath = os.path.normpath(dictionaryPath)

        try:
            variables = pd.read_excel(dictionaryPath, sheet_name="Variables")
            aliases = pd.read_excel(dictionaryPath, sheet_name="Aliases")
            contexts = pd.read_excel(dictionaryPath, sheet_name="Contexts")
        except Error as e:
            print("morpc.varLookup | ERROR | Failed to read variable dictionary spreadsheet. Verify that the variable dictionary is available at {} or specify another path using the dictionaryPath argument.".format(dictionaryPath))
            print(e)
            raise RuntimeError

        variablesSchema = morpc.frictionless.load_schema(dictionaryPath.replace(".xlsx","-Variables.schema.yaml"))
        aliasesSchema = morpc.frictionless.load_schema(dictionaryPath.replace(".xlsx","-Aliases.schema.yaml"))
        contextsSchema = morpc.frictionless.load_schema(dictionaryPath.replace(".xlsx","-Contexts.schema.yaml"))

        variables = morpc.frictionless.cast_field_types(variables, variablesSchema, verbose=False)
        aliases = morpc.frictionless.cast_field_types(aliases, aliasesSchema, verbose=False)
        contexts = morpc.frictionless.cast_field_types(contexts, contextsSchema, verbose=False)

        self.dictionaryPath = dictionaryPath
        self.variables = variables.copy()
        self.aliases = aliases.copy()
        self.contexts = contexts.copy()
        self.variableList = variableList
        self.aliasList = aliasList
        self.context = context

        if(variableList != None):
            self.filter_variables()
        if(aliasList != None):
            self.filter_aliases()

    def add_var_from_dict(self, variableDict, prepend=False):
        import pandas as pd
        if(prepend == True):
            self.variables = pd.concat([pd.DataFrame.from_dict([variableDict]), self.variables], axis="index")
        else:
            self.variables = pd.concat([self.variables, pd.DataFrame.from_dict([variableDict])], axis="index")

    def filter_variables(self):
        import pandas as pd
        # self.variables = self.variables.loc[self.variables["NAME"].isin(self.variableList)]
        # Iterater returns rows in order of variableList
        rows = []
        for variable in self.variableList:
            row = self.variables.loc[self.variables['NAME']==variable]
            rows.append(row)
        self.variables = pd.concat(rows)

    def filter_aliases(self):
        self.aliases = self.aliases.loc[self.aliases["ALIAS"].isin(self.aliasList)]

    def list_variables(self):
        return list(self.variables["NAME"])

    def alias_to_name(self, context=None):
        if(context == None):
            context = self.context

        if(context != None):
            df = self.aliases.copy()

            df = df \
                .loc[df["CONTEXT"] == context].copy() \
                .filter(items=["ALIAS","NAME"], axis="columns")
        else:
            print("morpc.varLookup.alias_to_name | ERROR | Must specify a valid context to map alias to name.")
            raise RuntimeError

        aliases = list(df["ALIAS"])
        names = list(df["NAME"])

        if(len(set(aliases)) != len(aliases)):
            print("morpc.varLookup.alias_to_name | ERROR | Each alias may only be used once per context.  Eliminate duplicated aliases for the specified context or create a different context with a unique set of aliases.")
            raise RuntimeError

        aliasToNameMap = {alias:name for (alias, name) in zip(aliases, names)}

        return aliasToNameMap

    def name_to_alias(self, context=None):
        if(context == None):
            context = self.context

        if(context != None):
            df = self.aliases.copy()

            df = df \
                .loc[df["CONTEXT"] == context].copy() \
                .filter(items=["ALIAS","NAME"], axis="columns")
        else:
            print("morpc.varLookup.name_to_alias | ERROR | Must specify a valid context to map name to alias.")
            raise RuntimeError

        aliases = list(df["ALIAS"])
        names = list(df["NAME"])

        if(len(set(names)) != len(names)):
            print("morpc.varLookup.name_to_alias | ERROR | Muliple aliases map to the same variable name in the specified context. This is OK when mapping aliases to names, but not in reverse. Eliminate duplicate mappings for this context or create a different context with a 1-to-1 mapping between aliases and variables.")
            raise RuntimeError

        nameToAliasMap = {name:alias for (name, alias) in zip(names, aliases)}

        return nameToAliasMap


    def to_dict(self):
        df = self.variables.copy().set_index("NAME")
        df.columns = [x.lower() for x in df.columns]
        df = df.rename(columns={
            "minlength":"minLength",
            "maxlength":"maxLength",
            "rdftype":"rdfType"
        })
        return df.to_dict(orient="index")

    def to_list(self):
        df = self.variables.copy()
        df.columns = [x.lower() for x in df.columns]
        df = df.rename(columns={
            "minlength":"minLength",
            "maxlength":"maxLength",
            "rdftype":"rdfType"
        })
        return df.to_dict(orient="records")

    def to_frictionless_schema(self, missingValues=None, primaryKey=None, foreignKeys=None, useAliases=False, context=None):
        import math
        import frictionless

        if(useAliases == True):
            print("morpc.varLookup.to_frictionless_schema | WARNING | Creating schema using aliases instead of standard variable names.")
            nameToAliasMap = self.name_to_alias(context=context)

        fields = self.to_list()
        # Remove the context property from all fields in the list
        schemaFields = []
        for i in range(0, len(fields)):
            schemaFields.append({})
            schemaFields[i]["constraints"] = {}
            for fieldAttr in fields[i]:
                if(fieldAttr == "context"):
                    # If this is the "context" attribute, skip it. It doesn't belong in the schema
                    continue
                if(type(fields[i][fieldAttr]) == float):
                    # If the attribute is a float and its value is nan, skip it.
                    if(math.isnan(fields[i][fieldAttr])):
                        continue
                if(fields[i][fieldAttr] == None):
                    # Othewise if the value is None, skip it.
                    continue

                if(fieldAttr in ["minimum","maximum","minLength","maxLength","pattern","enum"]):
                    # If the field attribute is a constraint, put it in the constraints object
                    schemaFields[i]["constraints"][fieldAttr] = fields[i][fieldAttr]
                else:
                    # Otherwise, put it in the top level
                    schemaFields[i][fieldAttr] = fields[i][fieldAttr] 
                    if(fieldAttr == "name"):
                        # If the user requested to use aliases, replace the standard variable name with the alias.
                        if(useAliases == True):
                            try:
                                schemaFields[i]["name"] = nameToAliasMap[schemaFields[i]["name"]]
                            except KeyError:
                                print("morpc.varLookup.to_frictionless_schema | INFO | No alias defined for variable {}. Using name as-is.".format(schemaFields[i]["name"]))


        schemaDescriptor = {'fields': schemaFields}
        if(missingValues != None):
            schemaDescriptor["missingValues"] = missingValues
        if(primaryKey != None):
            schemaDescriptor["primaryKey"] = primaryKey
        if(foreignKeys != None):
            schemaDescriptor["foreignKeys"] = foreignKeys
        schema = frictionless.Schema.from_descriptor(schemaDescriptor)
        return schema



# Functions for manipulating schemas in Apache Avro format
# Reference: https://avro.apache.org/docs/1.11.1/specification/

## Read an Avro schema specified as JSON in a plain text file. Return it as a Python dictionary.
def load_avro_schema(filepath):
    import os
    import json
    path = os.path.normpath(filepath)
    with open(filepath) as f:
        schema = json.load(f)
    return schema  

# Given an Avro dictionary object (see load_avro_schema), return a list containing the names of the fields defined in the schema.
def avro_get_field_names(schema):
    return [x["name"] for x in schema["fields"]]

# Given an Avro dictionary object (see load_avro_schema), return a dictionary mapping each field name to the corresponding data type
# specified in the schema.  The resulting dictionary is suitable for use by the pandas.DataFrame.astype() method (for example)
def avro_to_pandas_dtype_map(schema):
    return {schema["fields"][i]["name"]:schema["fields"][i]["type"] for i in range(len(schema["fields"]))}    

# Given an Avro dictionary object (see load_avro_schema), return a dictionary mapping each field name to the first element in the list 
# of aliases associated with that field. If no aliases are defined for a field, the dictionary will map that field name to itself.  
# The resulting dictionary may be used with the pandas.DataFrame.rename() method to rename each of the columns to its first alias 
# (for example).
def avro_map_to_first_alias(schema):
    fields = schema["fields"]
    fieldMap = {}
    for field in fields:
        if "aliases" in field.keys():
            fieldMap[field["name"]] = field["aliases"][0]
        else:
            fieldMap[field["name"]] = field["name"]
    return fieldMap

# Given an Avro dictionary object (see load_avro_schema), return a dictionary mapping the first element in the list of aliases associated with 
# a field to the field name specified for that field.  The resulting dictionary is suitable for use by the pandas.DataFrame.rename() 
# method (for example). This is the inverse of the avro_map_to_first_alias() method above.
def avro_map_from_first_alias(schema):
    fields = schema["fields"]
    fieldMap = {}
    for field in fields:
        if "aliases" in field.keys():
            fieldMap[field["aliases"][0]] = field["name"]
        else:
            fieldMap[field["name"]] = field["name"]
    return fieldMap

# Wrapper for backward compatibility
def cast_field_types(df, schema, forceInteger=False, forceInt64=False, handleMissingFields='error', verbose=True):
    """
    Wrapper for backward compatibility with AVRO Schema

    """
    import morpc
    # If schema is a dict object, assume it is in Avro format
    if(type(schema) == dict):
        outDF = avro_cast_field_types(df, schema, forceInteger=forceInteger, forceInt64=forceInt64, verbose=verbose)
    # Otherwise, assume it is in Frictionless format
    else:
        outDF = morpc.frictionless.cast_field_types(df, schema, forceInteger=forceInteger, forceInt64=forceInt64, handleMissingFields=handleMissingFields, verbose=verbose)
    return outDF

# Given a dataframe and the Avro dictionary object that describes its schema (see load_avro_schema), recast each of the fields in the dataframe
# to the data type specified in the schema.    
def avro_cast_field_types(df, schema, forceInteger=False, forceInt64=False, verbose=True):
    outDF = df.copy()
    for field in schema["fields"]:
        fieldName = field["name"]
        fieldType = field["type"]    
        if(verbose):
            print("Casting field {} as type {}.".format(fieldName, fieldType))
        # The following section is necessary because the pandas "int" type does not support null values.  If null values are present,
        # the field must be cast as "Int64" instead.
        if((fieldType == "int") or (fieldType == "integer")):
            try:
                if(forceInt64 == True):
                    # Cast all integer fields as Int64 whether this is necessary or not.  This is useful when trying to merge
                    # dataframes with mixed int32 and Int64 values.
                    outDF[fieldName] = outDF[fieldName].astype("Int64")
                else:
                    # Try to cast the field as an "int".  This will fail if nulls are present.
                    outDF[fieldName] = outDF[fieldName].astype("int")
            except:
                try:
                    # Try to cast as "Int64", which supports nulls. This will fail if the fractional part is non-zero.
                    print("WARNING: Failed conversion of fieldname {} to type 'int'.  Trying type 'Int64' instead.".format(fieldName))
                    outDF[fieldName] = outDF[fieldName].astype("Int64")
                except:
                    if(forceInteger == True):
                        # If the user has allowed coercion of the values to integers, then round the values to the ones place prior to 
                        # converting to "Int64"
                        print("WARNING: Failed conversion of fieldname {} to type 'Int64'.  Trying to round first.".format(fieldName))
                        outDF[fieldName] = outDF[fieldName].astype("float").round(0).astype("Int64")
                    else:
                        # If the user has not allow coercion of the values to integers, then throw an error.
                        print("WARNING: Unable to coerce value to Int64 type.  Ensure that fractional part of values is zero, or set forceInteger=True")
                        raise RuntimeError
        else:
            outDF[fieldName] = outDF[fieldName].astype(fieldType)

    return outDF

def wget(url, archive_dir = './input_data', filename = None, verbose=True):
    """
    This function uses wget within a subprocess call to retrieve a file from an ftp site. This is used as a means of retrieving Census TigerLine shapefiles.

    Parameters
    ----------
    url : string
        The url for the location of the file.

    archive_dir : string, path like
        The location to save the file.

    filename : string
        Optional: filename for archived file

    """
    import subprocess
    import os

    if not filename:
        filename = os.path.basename(url)

    cmd = ['wget', url]
    cmd.extend(['-O', os.path.normpath(f'./{archive_dir}/{filename}')])

    if not os.path.exists(archive_dir):
        os.mkdir(archive_dir)

    try:
        results = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if verbose:
            print(results.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Failed to download file: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")



# Load spatial data
def load_spatial_data(sourcePath, layerName=None, driverName=None, archiveDir=None, archiveFileName=None, verbose=True):
    """Often we want to make a copy of some input data and work with the copy, for example to protect 
    the original data or to create an archival copy of it so that we can replicate the process later.  
    With tabular data this is simple, but with spatial data it can be tricky.  Shapefiles actually consist 
    of up to six files, so it is necessary to copy them all.  Geodatabases may contain many layers in addition 
    to the one we care about.  The `load_spatial_data()` function simplifies the process of reading the data and 
    (optionally) making an archival copy.
    
    Example usage:

    Parameters
    ----------
    sourcePath : str
        The path to the geospatial data. It may be a file path or URL. In the case of a Shapefile, this should 
        point to the .shp file or a zipped file that contains all of the Shapefile components. You can point to 
        other zipped contents as well, but see caveats below.
    layerName : str
        Required for GPKG and GDB, optional for SHP. The name of the layer that you wish to extract from a 
        GeoPackage or File Geodatabase.  Not required for Shapefiles, but may be specified for use in the 
        archival copy (see below)
    driverName : str
        Required for zipped data or data with non-standard file extension. Which GDAL driver
        (https://gdal.org/drivers/vector/index.html) to use to read the file. Script will attempt to infer 
        this from the file extension, but you must specify it if the data is zipped, if the file extension is 
        non-standard, or if the extension cannot be determined from the path (e.g. if the path is an API query)
    archiveDir : str
        Optional. The path to the directory where a copy of a data should be archived.  If this is specified, 
        the data will be archived in this location as a GeoPackage.  The function will determine the file name 
        and layer name from the specified parameters, using generic values if necessary.
    archiveFileName : str
        Optional. If `archiveDir` is specified, you may use this to specify the name of the archival GeoPackage.  
        Omit the extension.  If this is unspecified, the function will assign the file name automatically using a 
        generic value if necessary.
    verbose : bool
        Set verbose to False to reduce the text output from the function.

    Returns
    -------
    gdf : pandas.core.frame.DataFrame
        A GeoPandas GeoDataframe constructed from the data at the location specified by sourcePath and layerName

    """

    import geopandas as gpd
    import os
    import shutil

    if(verbose):
        print("morpc.load_spatial_data | INFO | Loading spatial data from location: {}".format(sourcePath))

    # Due to changes at the Census gpd.read_file() and requests.get() are blocked. Using wget as work around.
    if sourcePath.find('www2.census.gov') > -1:
        if(verbose):
            print("morpc.load_spatial_data | INFO | Attempting to load data from Census FTP site. Using wget to archive file.")
            print("morpc.load_spatial_data | WARNING | Data from Census FTP must be temp saved. Using ./temp_data.")
        tempDir = './temp_data'
        wget(url = sourcePath, archive_dir = tempDir)
        driverName = 'Census Shapefile'
        tempFileName = os.path.normpath(f"./{tempDir}/{os.path.split(sourcePath)[-1]}")

    if(driverName == None):
        if(verbose):
            print("morpc.load_spatial_data | INFO | Driver name is unspecified.  Will attempt to infer driver from file extension in source path.")
        fileExt = os.path.splitext(sourcePath)[1]
        if(fileExt == ".gpkg"):
            driverName = "GPKG"
        elif(fileExt == ".shp"):
            driverName = "ESRI Shapefile"
        elif(fileExt == ".gdb"):
            driverName = "OpenFileGDB"
        else:
            print("morpc.load_spatial_data | ERROR | File extension is unsupported: {}.  It is possible to load zipped spatial data, but you must specify the driver name.".format(fileExt))
            raise RuntimeError
        if(verbose):
            print("morpc.load_spatial_data | INFO | Selecting driver {} based on file extension {}".format(driverName, fileExt))
    else:
        if(verbose):
            print("morpc.load_spatial_data | INFO | Using driver {} as specified by user.".format(driverName))

    if(layerName) == None:
        if(driverName == "GPKG" or driverName == "OpenFileGDB"):
            print("morpc.load_spatial_data | ERROR | Must specify layerName when using driver {}".format(driverName))
            raise RuntimeError

    if(verbose):
        print("morpc.load_spatial_data | INFO | Reading spatial data...")
    # Geopandas will throw an error if we attempt to specify a layer name when reading a Shapefile
    if(driverName == "ESRI Shapefile"):
        gdf = gpd.read_file(sourcePath, layer=None, driver=driverName, engine="pyogrio", fid_as_index=True)

    # When reading a shapefile from Census FTP site, read the data from temp zip
    elif(driverName == 'Census Shapefile'):
        gdf = gpd.read_file(tempFileName, layer=None, driver='ESRI Shapefile', engine='pyogrio', fid_as_index=True)
        if os.path.exists(tempFileName):
            os.unlink(tempFileName)

    # Everything else
    else:
        gdf = gpd.read_file(sourcePath, layer=layerName, driver=driverName, engine="pyogrio", fid_as_index=True)

    # If the user has specified an archive directory, create an archival copy of the data as a layer in a GeoPackage
    if(archiveDir != None):
        # If no file name was specified, we need to assign one
        if(archiveFileName) == None:
            # First try to determine whether we are retrieving data from an API. In this case we may not be able to extract
            # a file name from the source path.  Specifically, look for a "?" character in the path. This is forbidden in
            # Windows file paths and suggests that a query string is present.
            if(sourcePath.find("?") > -1):
                if(verbose):
                    print("morpc.load_spatial_data | INFO | File name is unspecified and source path appears to be an API query. Will assign an alternate file name.")
                # If the layer name is specified, use that as the file name. Otherwise use a generic file name.
                if(layerName != None):
                    archiveFileName = layerName
                else:
                    archiveFileName == "spatialData"

            # If the source path doesn't look like an API query, then attempt to extract the file name from the path
            else:
                if(verbose):
                    print("morpc.load_spatial_data | INFO | File name is unspecified.  Will infer file name from source path.")
                archiveFileName = os.path.splitext(os.path.split(sourcePath)[-1])[0]
                if(verbose):
                    print("morpc.load_spatial_data | INFO | Using automatically-selected file name: {}".format(archiveFileName)) 

        archivePath = os.path.join(archiveDir, "{}.gpkg".format(archiveFileName))

        # If the layer name was unspecified (e.g. for Shapefiles), use the file name as the layer name (sans extension)
        if(layerName != None):
            archiveLayer = layerName
        else:
            archiveLayer = archiveFileName
            if(verbose):
                print("morpc.load_spatial_data | INFO | Layer name is unspecified. Using automatically-selected layer name: {}".format(archiveLayer))

        if(verbose):
            print("morpc.load_spatial_data | INFO | Creating archival copy of geospatial layer at {}, layer {}".format(archivePath, archiveLayer))
        gdf.to_file(archivePath, layer=layerName, driver="GPKG")

    return gdf

# Load tabular data
def load_tabular_data(sourcePath, sheetName=None, fileType=None, archiveDir=None, archiveFileName=None, verbose=True, sep=None, encoding=None):
    """Often we want to make a copy of some input data and work with the copy, for example to protect 
    the original data or to create an archival copy of it so that we can replicate the process later.  
    The `load_tabular_data()` function simplifies the process of reading the data and (optionally) making 
    an archival copy.
    
    Example usage: df = morpc.load_tabular_data("somefile.xlsx", sheetName="Sheet1", archiveDir="./input_data"))

    Parameters
    ----------
    sourcePath : str
        The path to the tabular data. It may be a file path or URL.
    sheetName : str
        Optional. The name of the sheet that you wish to extract from an Excel workbook.  If unspecified, the
        function will read the first sheet in the workbook.
    fileType : str
        Optional. One of "csv" or "xlsx" or "xls". If unspecified, the function will attempt to infer from sourcePath.
    archiveDir : str
        Optional. The path to the directory where a copy of a data should be archived.  If this is specified, 
        the data will be copied to this location.
    archiveFileName : str
        Optional. If `archiveDir` is specified, you may use this to specify the name of the archived file.
        If this is unspecified, the function will preserve the original filename as-is.
    verbose : bool
        Set verbose to False to reduce the text output from the function.
    sep : str
        Optional. Delimiter to use for delimited text files.  Defaults to "," (i.e. CSV file).  Tabs ("\t")
        and pipes ("|") are also common.
    encoding : str
        Optional. Character encoding to use for delimited text files. Defaults to "utf-8" which works in most cases.
        Sometimes other encodings are required. Notably, Census PEP tables require the "ISO-8859-1" encoding.

    Returns
    -------
    df : pandas.core.frame.DataFrame
        A Pandas GeoDataframe constructed from the data at the location specified by sourcePath and sheetName

    """

    import pandas as pd
    import os

    if(verbose):
        print("morpc.load_tabular_data | INFO | Loading tabular data from location: {}".format(sourcePath))

    # Due to changes at the Census pd.read_csv(), pd.read_excel(), and requests.get() are blocked. Using wget as work around.
    if sourcePath.find('www2.census.gov') > -1:
        if(verbose):
            print("morpc.load_tabular_data | INFO | Attempting to load data from Census FTP site. Using wget to retrieve file.")
            print("morpc.load_tabular_data | WARNING | Data from Census FTP must be temp saved. Using ./temp_data.")
        tempDir = os.path.normpath('./temp_data')
        if not os.path.exists(tempDir):
            os.makedirs(tempDir)
        wget(url = sourcePath, archive_dir = tempDir)
        sourcePath = os.path.join(tempDir, os.path.split(sourcePath)[-1])

    if(fileType == None):
        if(verbose):
            print("morpc.load_tabular_data | INFO | File type is unspecified.  Will attempt to infer file type from file extension in source path.")
        fileExt = os.path.splitext(sourcePath)[1]
        if(fileExt == ".csv"):
            fileType = "csv"
        elif(fileExt == ".xlsx"):
            fileType = "xlsx"
        elif(fileExt == ".xls"):
            fileType = "xls"
        else:
            print("morpc.load_tabular_data | ERROR | File extension is unsupported: {}.".format(fileExt))
            raise RuntimeError
        if(verbose):
            print("morpc.load_tabular_data | INFO | Selecting file type {} based on file extension {}".format(fileType, fileExt))
    else:
        if(verbose):
            print("morpc.load_tabular_data | INFO | Using file type {} as specified by user.".format(fileType))

    if("sheetName") == None:
        if(fileType == "xlsx" or fileType == "xls"):
            print("morpc.load_tabular_data | WARNING | Sheet name was not specified. Will load first sheet in workbook.")

    if(verbose):
        print("morpc.load_tabular_data | INFO | Reading tabular data...")

    if(fileType == "csv"):
        df = pd.read_csv(sourcePath, sep=sep, encoding=encoding)
    elif(fileType == "xlsx" or fileType == "xls"):
        df = pd.read_excel(sourcePath, sheet_name=sheetName)        
    else:
        print("morpc.load_tabular_data | ERROR | File type {} is not handled. Troubleshoot function.".format(fileType))
        raise RuntimeError

    # If the user has specified an archive directory, create an archival copy of the data
    if(archiveDir != None):
        # If no file name was specified, we need to assign one
        if(archiveFileName) == None:
            # First try to determine whether we are retrieving data from an API. In this case we may not be able to extract
            # a file name from the source path.  Specifically, look for a "?" character in the path. This is forbidden in
            # Windows file paths and suggests that a query string is present.
            if(sourcePath.find("?") > -1):
                if(verbose):
                    print("morpc.load_tabular_data | INFO | File name is unspecified and source path appears to be an API query. Will assign an alternate file name.")
                # If the sheet name is specified, use that as the file name. Otherwise use a generic file name.
                if(sheetName != None):
                    archiveFileName = "{0}.{1}".format(sheetName, fileType)
                else:
                    archiveFileName == "tabularData.{}".format(fileType)

            # If the source path doesn't look like an API query, then attempt to extract the file name from the path
            else:
                if(verbose):
                    print("morpc.load_tabular_data | INFO | File name is unspecified.  Will infer file name from source path.")
                archiveFileName = os.path.split(sourcePath)[-1]
                if(verbose):
                    print("morpc.load_tabular_data | INFO | Using automatically-selected file name: {}".format(archiveFileName)) 

        archivePath = os.path.join(archiveDir, archiveFileName)

        if(verbose):
            print("morpc.load_tabular_data | INFO | Creating archival copy of tabular data at {}".format(archivePath))
        if(fileType == "csv"):
            df.to_csv(archivePath, sep=sep, encoding=encoding, index=False)
        elif(fileType == "xlsx" or fileType == "xls"):
            df.to_excel(archivePath, sheet_name=sheetName, index=False)
        else:
            print("morpc.load_tabular_data | ERROR | File type {} is not handled. Troubleshoot function.".format(fileType))
            raise RuntimeError
            
    return df

# Assign geographic identifiers
# Sometimes we have a set of locations and we would like to know what geography (county, zipcode, etc.) they fall in. The
# `assign_geo_identifiers()` function takes a set of georeference points and a list of geography levels and determines for each
# level which area each point falls in.  The function takes two parameters:
#  - `points` - a GeoPandas GeoDataFrame consisting of the points of interest
#  - `geographies` - A Python list of one or more strings in which each element corresponds to a geography level. You can specify as
#     many levels as you want from the following list, however note that the function must download the polygons and perform the analysis
#     for each level so if you specify many levels it may take a long time.
#    - "county" - County (Census TIGER)
#    - "tract" - *Not currently implemented*
#    - "blockgroup" - *Not currently implemented*
#    - "block" - *Not currently implemented*
#    - "zcta" - *Not currently implemented*
#    - "place" - Census place (Census TIGER)
#    - "placecombo" - *Not currently implemented*
#    - "juris" - *Not currently implemented*
#    - "region15County" - *Not currently implemented*
#    - "region10County" - *Not currently implemented*
#    - "regionCORPO" - *Not currently implemented*
#    - "regionMPO" - *Not currently implemented*
#
# **NOTE:** Many of the geography levels are not currently implemented.  They are being implemented as they are needed.  If you need one
# that has not yet been implemented, please contact Adam Porr (or implement it yourself).
def assign_geo_identifiers(points, geographies):
    """
    Assign geographic identifiers
    Sometimes we have a set of locations and we would like to know what geography (county, zipcode, etc.) they fall in. The
    `assign_geo_identifiers()` function takes a set of georeference points and a list of geography levels and determines for each
    level which area each point falls in

    Parameters
    ----------
    points : geopandas.GeoDataFrame
        a GeoPandas GeoDataFrame consisting of the points of interest
    geographies : list of str
        A Python list of one or more strings in which each element corresponds to a geography level. You can specify as
        many levels as you want from the following list, however note that the function must download the polygons and perform the analysis
        for each level so if you specify many levels it may take a long time.
        - "county" - County (Census TIGER)
        - "tract" - *Not currently implemented*
        - "blockgroup" - *Not currently implemented*
        - "block" - *Not currently implemented*
        - "zcta" - Census ZCTA (tl_2024_us_zcta520)
        - "place" - Census place (Census TIGER)
        - "placecombo" - *Not currently implemented*
        - "juris" - *Not currently implemented*
        - "region15County" - *Not currently implemented*
        - "region10County" - *Not currently implemented*
        - "regionCORPO" - *Not currently implemented*
        - "regionMPO" - *Not currently implemented*

    Returns
    -------
    geopandas.GeoDataFrame
        A geodataframe with column name id_{geographies} representing the id from the geographies passed
    """
    import geopandas as gpd
    import pyogrio
    import requests
    from io import BytesIO

    # Create a copy of the input data so Python doesn't manipulate the original object.
    points = points.copy()

    # Loop through each of the specified geography levels, doing a point-in-polygon assignment for each level.
    for geography in geographies:
        print("morpc.assign_geo_identifiers | INFO | Determining identifiers for geography {}".format(geography))
        # First establish the parameters for the polygon geometries. In each case we need to know:
        #   - filePath - The source file or URL where we can fetch the geometries
        #   - layerName - If the geometries are in a geodatabase, which layer are they in
        #   - driverName - What GDAL driver should we use to read the data
        #   - polyIdField - What field/attribute contains the unique identifiers for the polygons
        if(geography == "county"):
            filePath = "https://www2.census.gov/geo/tiger/TIGER2020PL/LAYER/COUNTY/2020/tl_2020_39_county20.zip"
            layerName = None
            driverName = "Census Shapefile" # Custom driver name for load_spatial_data
            polyIdField = "GEOID20"
        elif(geography == "tract"):
            filePath = "https://www2.census.gov/geo/tiger/TIGER2020PL/LAYER/TRACT/2020/tl_2020_39_tract20.zip"
            layerName = None
            driverName = "Census Shapefile" # Custom driver name for load_spatial_data
            polyIdField = "GEOID20"
        elif(geography == "blockgroup"):
            print("ERROR: Geography is currently unsupported: {}".format(geography))
            raise RuntimeError
        elif(geography == "block"):
            print("ERROR: Geography is currently unsupported: {}".format(geography))
            raise RuntimeError
        elif(geography == "zcta"):
            filePath = "https://www2.census.gov/geo/tiger/TIGER2024/ZCTA520/tl_2024_us_zcta520.zip"
            layerName = None
            driverName = "Census Shapefile"
            polyIdField = ""
        elif(geography == "place"):
            filePath = "https://www2.census.gov/geo/tiger/TIGER2020/PLACE/tl_2020_39_place.zip"
            layerName = None
            driverName = "Census Shapefile"
            polyIdField = "GEOID"
        elif(geography == "placecombo"):
            print("ERROR: Geography is currently unsupported: {}".format(geography))
            raise RuntimeError
        elif(geography == "juris"):
            print("ERROR: Geography is currently unsupported: {}".format(geography))
            raise RuntimeError
        elif(geography == "region15County"):
            print("ERROR: Geography is currently unsupported: {}".format(geography))
            raise RuntimeError
        elif(geography == "region10County"):
            print("ERROR: Geography is currently unsupported: {}".format(geography))
            raise RuntimeError
        elif(geography == "regionCORPO"):
            print("ERROR: Geography is currently unsupported: {}".format(geography))
            raise RuntimeError
        elif(geography == "regionMPO"):
            print("ERROR: Geography is currently unsupported: {}".format(geography))
            raise RuntimeError
        else:
            print("morpc.load_spatial_data | ERROR | Geography is unknown: {}".format(geography))
            raise RuntimeError

        polys = load_spatial_data(sourcePath = filePath, layerName = layerName, verbose=False)

        # Extract only the fields containing the polygon geometries and the unique IDs. Rename the unique ID field
        # using the following format "id_{}".format(geography), for example "id_county" for the "county" geography level
        polys = polys \
            .filter(items=[polyIdField,"geometry"], axis="columns") \
            .rename(columns={polyIdField:"id_{}".format(geography, polyIdField)})

        # Spatially join the polygon unique IDs to the points
        points = points.sjoin(polys.to_crs(points.crs), how="left")

        # Drop the index field from the polygon data
        points = points.loc[:, ~points.columns.str.startswith('fid_')]
    return points


def round_preserve_sum(inputValues, digits=0, verbose=False):
    """
    The following function performs "bucket rounding" on a pandas Series object.  Bucket rounding
    refers to a rounding technique for a series of data in which each element
    is rounded to the specified number of digits in such a way that the sum of the series is
    preserved. For example, a model may produce non-integer population values for small
    geographies such as GridMAZ. Population must be an integer, and therefore the population for
    each GridMAZ must be rounded. Bucket rounding ensures that the rounding error resulting from
    each of tens of thousands of individual GridMAZ does not accumulate and cause significant
    error for combined population of all GridMAZ.
    """
    import math
    import pandas as pd

    # Make a copy of the input so that we avoid altering it due to chains or views.
    inputValuesCopy = inputValues.copy()

    # Create a new numerical index that is used exclusively within this function.  This is necessary due to some
    # nuances of the implementation that use the indices of the records with the largest fractional values to
    # allocate residuals.  Original index will be restored before series is returned.
    previousIndexName = inputValuesCopy.index.name
    if(previousIndexName == None):
        previousIndexName = "index"
    previousColumnName = inputValuesCopy.name
    outputValues = inputValuesCopy.copy().reset_index()

    # Extract a series using the new index.
    rawValues = outputValues.drop(columns=previousIndexName).iloc[:,0]

    # Compute a multiplier to be used to "inflate" the series such that the desired decimal digit ends up in the ones place so we can 
    # truncate the values to the ones place using floor
    multiplier = 10**digits

    # Compute the "inflated" values
    inflatedValues = rawValues * multiplier

    # Truncate the values to the ones place
    truncatedValues = inflatedValues.apply(lambda x:math.floor(x))

    # Compute the residual for each data point, i.e. the difference between the full value and the truncated value.
    # Note: Floating point arithmetic results in extraneous decimal places due to high-precision rounding error, however this 
    # should be insignificant for our purposes.
    residual = (inflatedValues-truncatedValues).round(10)

    # Create an array of the indices of the datapoints in ascending order according to their residual, i.e. the first element in
    # this array is the index of the datapoint with the smallest residual and the last element is the index of the datapoint with
    # the largest residual.
    residualOrder = residual.sort_values().index

    # Compute the overall residual, i.e. the difference between the sum of the full values and the sum of the truncated values
    # Note: Floating point arithmetic results in extraneous decimal places due to high-precision rounding error, however this
    # should be insignificant for our purposes.
    overallResidual = inflatedValues.sum() - truncatedValues.sum()

    # Round the overall residual to determine the combined number of integer units that need to be reallocated. For example, if the
    # series represents population, these units represent the "whole" people that were formed from the "partial" people that were
    # removed from each individual record via the truncation.
    unitsToReallocate = round(overallResidual)

    # If there are units to reallocate, then do so. Otherwise, leave the values unadjusted
    adjustedValues = truncatedValues.copy()
    if(unitsToReallocate > 0):

        # First, select the indices for the N records with the largest residuals, where N is the number of integer units available for
        # reallocation.
        indicesToReceiveReallocatedUnit = residualOrder[-unitsToReallocate:]

        # Reallocate one unit to each record selected to receive one
        adjustedValues[indicesToReceiveReallocatedUnit] = adjustedValues[indicesToReceiveReallocatedUnit] + 1

    # Undo the inflation that we did at the beginning.  This completes the bucket rounding process.
    bucketRoundedValues = (adjustedValues/multiplier).astype("int")

    outputValues[previousColumnName] = bucketRoundedValues
    outputValues = outputValues.set_index(previousIndexName)[previousColumnName]

    # Show the intermediate steps of the function (for demonstration purposes only)
    if(verbose):
        print("Multiplier: {}".format(multiplier))
        print("Inflated values: {}".format(inflatedValues.tolist()))
        print("Truncated values: {}".format(truncatedValues.tolist()))
        print("Residuals for individual records: {}".format(residual.tolist()))
        print("Order of residuals: {}".format(residualOrder.tolist()))
        print("Overall residual: {}".format(overallResidual))
        print("Units to reallocate: {}".format(unitsToReallocate))
        print("Indices of records to receive reallocated units: {}".format(indicesToReceiveReallocatedUnit.tolist()))
        print("Adjusted values (still inflated): {}".format(adjustedValues.tolist()))
        print("Bucket-rounded values (deflated): {}".format(outputValues.tolist()))

    return(outputValues)


def compute_group_sum(inputDf, valueField=None, groupbyField=None):
    """
    Given a pandas DataFrame, append a new column "GROUP_SUM" containing the sum of the values in a specified column. Optionally, 
    populate "GROUP_SUM" with subtotals for groups using group names from a specified column.
    
    Parameters
    ----------
    inputDf : pandas.core.frame.DataFrame
        a pandas DataFrame with a column containing the values and (optionally) a column containing the group labels
    valueField : str
        the name of the column of inputDf that contains the values. This may be omitted if the DataFrame contains only one column.
    groupbyField : str
        Optional. the name of the column of inputDf that contains the group labels.

    Returns
    -------
    df : pandas.core.frame.DataFrame 
        A copy of inputDf to which a new column "GROUP_SUM" has been added which contains the sum of the values in the specified column 
        or the sums of the values for each group.
    """
    import pandas as pd

    if(type(inputDf) != pd.core.frame.DataFrame):
        print("ERROR: inputDf must be a pandas DataFrame")
        raise RuntimeError

    # Create a copy of the DataFrame to avoid operating on a reference to the original DataFrame
    df = inputDf.copy()

    if("GROUP_SUM" in df.columns):
        print("morpc.compute_group_sum | WARNING | Existing field GROUP_SUM in input dataframe will be overwritten.")
        df = df.drop(columns="GROUP_SUM")
    
    # If name of column containing the values is not specified, try to use the only column in the DataFrame. If
    # multiple columns are present, force the user to specify one.
    if(valueField == None):
        if(df.shape[1] > 1):
            print("ERROR: Must specify valueField for DataFrame with multiple columns")
            raise RuntimeError
        valueField = df.columns[0]

    # If the name of a column containing group labels is specified, try to reference the column. Throw an error if this fails.  
    if(groupbyField != None):
        try:
            temp = df[groupbyField]
        except:
            print("ERROR: inputDf does not contain groupbyField specified by user: {}".format(groupbyField))
            raise RuntimeError

    if(groupbyField != None):
        # If group field is specified, sum the values grouping by the specified field. Join the resulting group sums back to
        # the original DataFrame using the group label as the key, then name the appended column "GROUP_SUM".
        temp = df.copy() \
            .filter(items=[groupbyField, valueField], axis="columns") \
            .groupby(groupbyField).sum() \
            .reset_index() \
            .rename(columns={valueField:"GROUP_SUM"})

        # Preserve the original index through the merge operation.
        if(df.index.name == None):
            df.index.name = "NoIndexName"
        indexName = df.index.name
        df = df.reset_index().merge(temp, on=groupbyField).set_index(indexName)
        if(indexName == "NoIndexName"):
            df.index.name = None
        
    else:
        # If group field is not specified, sum all of the values and store the sum in a new column "GROUP_SUM"
        df["GROUP_SUM"] = df[valueField].sum()
        
    return df

def compute_group_share(inputDf, valueField, groupSumField="GROUP_SUM"):
    """
    Given a pandas DataFrame with a column containing a set of values and another column containing a set of sums representing the 
    total of a group to which the value belongs, append a new column "GROUP_SHARE" which contains the share of the group total represented 
    by each value.
    
    Parameters
    ----------
    inputDf : pandas.core.frame.DataFrame
        A pandas DataFrame with a column containing the values and and a column containing the group sums
    valueField : str
        The name of the column of inputDf that contains the values.
    groupSumField : str
        Optional. The name of the column of inputDf that contains the group sums. If this is not specified, the column "GROUP_SUM" will be used.

    Returns
    -------
    df : pandas.core.frame.DataFrame 
        A copy of inputDf to which a new column "GROUP_SHARE" has been added which contains the share of the group total represented by each value.
    """
    import pandas as pd

    if(type(inputDf) != pd.core.frame.DataFrame):
        print("ERROR: inputData must be a pandas DataFrame")
        raise RuntimeError

    # Create a copy of the DataFrame to avoid operating on a reference to the original DataFrame
    df = inputDf.copy()

    if("GROUP_SHARE" in df.columns):
        print("morpc.compute_group_share | WARNING | Existing field GROUP_SHARE in input dataframe will be overwritten.")
        df = df.drop(columns="GROUP_SHARE")

    # Try to reference the column that contains the values. Throw an error if this fails.  
    try:
        temp = df[valueField]
    except:
        print("ERROR: inputDf does not contain valueField specified by user: {}".format(valueField))
        raise RuntimeError

    # Try to reference the column that contains the group sums. Throw an error if this fails.  
    try:
        temp = df[groupSumField]
    except:
        print("ERROR: inputDf does not contain groupSumField specified by user: {}".format(groupSumField))
        raise RuntimeError

    # Compute shares
    df["GROUP_SHARE"] = df[valueField] / df[groupSumField]
    df["GROUP_SHARE"] = df["GROUP_SHARE"].fillna(0)
    
    return df

# Given a pandas DataFrame with a column containing a set of shares of some values
# relative to a group total and a separate series containing a set of control totals
# for the groups, append a new column "CONTROLLED_VALUE" that contains a set of modified
# values that have been scaled such that their group share remains unchanged but their
# sum is equal to the control total.  Append another new column "CONTROL_TOTAL" that
# contains the control total for the group to which the value belongs.
#
# Parameters:
# 
# inputDf is a pandas DataFrame with a column containing the group shares and (optionally)
# a column containg the group labels.
# 
# controlValues is one of the following:
#   - If groupbyField == None: controlValues is a scalar number (integer or float)
#   - If groupbyField != None: controlValues is a pandas Series of numbers indexed by group labels
#
# Optional: groupbyField is the name of the column of inputDf that contains the group labels.
#
# Optional: shareField is the name of the column of inputDf containing the shares that the values
# comprise.  If this is not specified, "GROUP_SHARE" will be used.
#
# Optional: roundPreserveSumDigits is the number of decimal places that the scaled values
# (i.e. the values in the "CONTROLLED_VALUE" column) should be rounded to. A "bucket rounding"
# technique will be used to ensure that the sum of the values in the group is preserved. If
# this is not specified, the scaled values will be left unrounded.
def compute_controlled_values(inputDf, controlValues, groupbyField=None, shareField="GROUP_SHARE", roundPreserveSumDigits=None):
    """
    TODO: add docstring
    """
    import pandas as pd

    if(type(inputDf) != pd.core.frame.DataFrame):
        print("ERROR: inputData must be a pandas DataFrame")
        raise RuntimeError

    # Create a copy of the DataFrame to avoid operating on a reference to the original DataFrame
    df = inputDf.copy()

    if("CONTROL_TOTAL" in df.columns):
        print("morpc.compute_controlled_values | WARNING | Existing field CONTROL_TOTAL in input dataframe will be overwritten.")
        df = df.drop(columns="CONTROL_TOTAL")
    
    if("CONTROLLED_VALUE" in df.columns):
        print("morpc.compute_controlled_values | WARNING | Existing field CONTROLLED_VALUE in input dataframe will be overwritten.")
        df = df.drop(columns="CONTROLLED_VALUE")
    
    # If a field name is specified for the group labels, try to reference the column by creating a list of unique
    # groups which we can use later. Throw an error if this fails.  
    if(groupbyField != None):
        try:
            groups = df[groupbyField].unique()
        except:
            print("ERROR: inputDf does not contain groupbyField specified by user: {}".format(groupbyField))
            raise RuntimeError

    # Try to reference the column containing the shares. Throw an error if this fails.
    try:
        temp = df[shareField]
    except:
        print("ERROR: inputDf does not contain shareField specified by user: {}".format(shareField))
        raise RuntimeError

    if(groupbyField != None):
        # If groups are specified, convert the series of control totals to a dataframe with one column named "CONTROL_TOTAL" 
        # and merge this column with the dataframe using the group name. First check to make sure the control totals were provided
        # as a pandas series.

        if(type(controlValues) != pd.core.series.Series):
            print("ERROR: If groupbyField is specified, controlValues must be a pandas series of numbers indexed by group labels.")
            raise RuntimeError
        temp = controlValues.copy()
        temp.name = "CONTROL_TOTAL"
        temp = pd.DataFrame(temp)

        # Preserve the original index through the merge operation.
        if(df.index.name == None):
            df.index.name = "NoIndexName"
        indexName = df.index.name
        df = df.reset_index().merge(temp, on=groupbyField).set_index(indexName)
        if(indexName == "NoIndexName"):
            df.index.name = None
    else:
        # Otherwise, create a new column called "CONTROL_TOTAL" and assign the scalar control total to it.  First try to convert the
        # control total to a float. If so, assume it is a number.
        try:
            float(controlValues)
        except:
            print("ERROR: If groupbyField is not specified, controlValues must be a scalar number (int or float).")
            raise RuntimeError

        df["CONTROL_TOTAL"] = controlValues

    # Compute the scaled (controlled) values by multiplying the group share by the control total
    df["CONTROLLED_VALUE"] = (df[shareField] * df["CONTROL_TOTAL"]).astype("float")
    
    # If a rounding precision is provided, round the values in each group (or the entire series) to the specified precision
    # while ensuring that the group sum is preserved.
    if(roundPreserveSumDigits != None):
        if(groupbyField == None):
            # If no groups are specified, round all values in the series preserving the sum for the entire series.
            df["CONTROLLED_VALUE"] = round_preserve_sum(df["CONTROLLED_VALUE"], digits=roundPreserveSumDigits)
        else:
            # Otherwise, iterate through each group rounding the values in that group and preserving the sum for the group.
            for group in groups:
                temp = df.loc[df[groupbyField] == group].copy()
                temp["CONTROLLED_VALUE"] = round_preserve_sum(temp["CONTROLLED_VALUE"], digits=roundPreserveSumDigits)
                df.update(temp, overwrite=True, errors="ignore")
    
    return df

# Given a series of values in a group and a control total for that group, compute a set of alternate values (i.e. "controlled values") such
# that the the share of each value in the group is preserved but they sum to the control total.  Put another way, scale all of the values
# in a series uniformly such that the scaled values sum to an arbitrary value (the control total).
def control_variable_to_group(inputDf, controlValues, valueField=None, groupbyField=None, roundPreserveSumDigits=None):
    """
    TODO: add docstring
    """
    import pandas as pd

    if(type(inputDf) != pd.core.frame.DataFrame):
        print("ERROR: inputDf must be a pandas DataFrame")
        raise RuntimeError

    # Create a copy of the DataFrame to avoid operating on a reference to the original DataFrame
    df = inputDf.copy()
    
    # If name of column containing the values is not specified, try to use the only column in the DataFrame. If
    # multiple columns are present, force the user to specify one.
    if(valueField == None):
        if(df.shape[1] > 1):
            print("ERROR: Must specify valueField for DataFrame with multiple columns")
            raise RuntimeError
        valueField = df.columns[0]
    
    # Sum the values in the series, or in the groups within the series if groupbyField is specified
    df = compute_group_sum(df, valueField=valueField, groupbyField=groupbyField)
    
    # Divide each value in the series by the series sum (or each value by the group sum) to get the share of the value within the group
    df = compute_group_share(df, valueField)
 
    # Multiply each share by the control total for the group to get the controlled value
    df = compute_controlled_values(df, controlValues, groupbyField=groupbyField, roundPreserveSumDigits=roundPreserveSumDigits)
    
    return df
    
# groupAssignmentRandom() takes a population from a superior (i.e. "next level") geography and randomly assigns people to 
# groups in a set of inferior ("this level") geographies such that (1) next level population count is respected, 
# (2) this level population count is respected, and (3) this level group membership has the same proportions (on average)
# as next-level group membership.
#
# Example: The tract-level population is distributed among age groups "17 and under", "18 to 64", and "65 and over".  We want to know
# how many people in each GridMAZ fall in each of these groups, but there is no data about this so we must infer it. Moreover, the population of 
# some GridMAZ are so low (say, <5) that we can simply multiply the tract-level proportion in each group by the GridMAZ total.  This script will
# randomly assign the people to each GridMAZ until the total GridMAZ population is reached.  Each person will be assigned to one of the age groups
# with probability as determined by the tract-level proportions of the groups.  Thus, the group membership in any given GridMAZ may not be representative
# of the tract-level proportions, but the combined group membership across all GridMAZ will approximate the tract membership.
# 
# Input parameters:
#   - inDf is a pandas dataframe where each record represents one "this level" geography.  Optionally, the dataframe may include a column that includes the
#     total population for the geography (see 'budgetThisLevel' below)
#   - budgetThisLevel is one of the following:
#     - the name of the column (i.e. a string) in inDf which contains the total populations
#     - a pandas series with the same index as inDf which contains the total populations
#   - groupsNextLevel is a dataframe which describes the groups to which population will be assigned, including the group label, proportion of the population 
#       in the next level geography that belongs to the group, and total population in the next level geography that belongs to the group.  See example
#       below.
#   - firstRoundGroupsExcluded is a list of group labels from groupsNextLevel which should not be assigned to the first person placed in each "this level" 
#     geography. This is useful, for example, when you are allocating population by age and you don't want the only person in geography to be a child.
#     NOTE: firstRoundGroupsExcluded is not implemented as of 2/2024.  
#
# Returns:
#   - outDf is a copy of inDf with one or more columns appended (dtype=int) where each new column includes the population for a group as defined in groupNextLevel
#
# Notes:
#   1. The groupsNextLevel input must be structured as follows:
#     - One record per group
#     - Index consists of the group labels (will be used as column headings in the output)
#     - The following columns must be included:
#       - probability - a float between 0 and 1 which indicates the probability that a person will be assigned 
#           to the group.  Typically this will be the proportion of the population of the next level geography 
#           that belongs to the group
#   2. If the entries in the "probability" column do not sum to 1, the function will interpret this to mean that 
#       there are members of the next level population that do not belong to any group.  Internally, the function
#       will assign these people to a dummy "NOT_ASSIGNED" group, however this group will not be included
#       in the output.  In this case, the sum of group members in the output will not necessdarily sum to the 
#       total population for each "this level" geography.
def groupAssignmentRandom(inDf, budgetThisLevel, groupsNextLevel, firstRoundGroupsExcluded=None):
    """
    TODO: add docsting
    """
    import pandas as pd
    import random
    
    # Create a copy of the input dataframe that will be enriched and returned to the user
    outDf = inDf.copy()

    # If budgetThisLevel is a string, interpret this as a field name and extract the series from the
    # input dataframe.  Otherwise, assume it is a series and use it as-is.
    if(type(budgetThisLevel) == str):
        totalsThisLevel = outDf[budgetThisLevel]
    else:
        totalsThisLevel = budgetThisLevel

    for group in groupsNextLevel.index:
        outDf[group] = 0

    # Check whether the total weights assigned to the groups sum to 1.  If not, create a new group
    # called "NOT_ASSIGNED" and give it the remaining weight. 
    assignedWeight = groupsNextLevel["probability"].sum()
    if(assignedWeight < 1):
        groupsNextLevel = pd.concat([groupsNextLevel, pd.DataFrame.from_dict({
            "NOT_ASSIGNED": {
                "probability": 1-assignedWeight
            }
        }, orient="index")], axis="index")
    
    # Create a copy of the group details that we can modify.
    groupsAvailable = groupsNextLevel.copy()
    
    # Iterate through each geography at this level.  For each, randomly assign the total population 
    # to the various groups according to the frequency of each of these groups in the next level geography.
    for idThisLevel in totalsThisLevel.index.to_list():

        # If the total population at this level is zero, leave the population of each group set to zero
        if(totalsThisLevel[idThisLevel] == 0):
            continue

        # Record the number of people at this level that need to be assigned to a group
        totalRemaining = totalsThisLevel[idThisLevel]
    
        # Assign a group label to each person in the geography
        while(totalRemaining > 0):

            # Randomly assign one person to a group. The zero index
            # extracts the age group string from a one-element list.
            try:
                groupLabels = list(groupsAvailable.index)
                groupWeights = list(groupsAvailable["probability"])
                groupAssigned = random.choices(groupLabels, weights=groupWeights, k=1)[0]
            except:
                print("An error occurred during assignment for geography {}".format(idThisLevel))
                raise
 
            # Increment the count in the selected group for this level geography
            if(groupAssigned != "NOT_ASSIGNED"):
                outDf.at[idThisLevel, groupAssigned] += 1
                          
            # Decrement the number of people in the geography waiting to be
            # assigned to a group
            totalRemaining = totalRemaining - 1
        
    return outDf

def recursiveUpdate(original, updates):
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(original.get(key), dict):
            original[key] = recursiveUpdate(original[key], value)
        else:
            original[key] = value
    return original

def data_chart_to_excel(df, writer, sheet_name="Sheet1", chartType="column", dataOptions=None, chartOptions=None):
    # TODO: simplify docstring
    """
    Create an Excel worksheet consisting of the contents of a pandas dataframe (as a formatted table)
    and, optionally, a chart to visualize the series included in the dataframe.  The simplest invocation
    will produce a table and a basic column (vertical bar) chart with default formatting that is consistent
    with MORPC branding guidelines, however the user can specify many of options supported by the xlsxwriter library 
    (https://xlsxwriter.readthedocs.io/).

    Example usage:
        import pandas as pd
        import xlsxwriter
        d = {'col1': [1, 2, 3, 4], 'col2':[3, 4, 5, 6]}
        df = pd.DataFrame(data=d)
        writer = pd.ExcelWriter("./foo.xlsx", engine='xlsxwriter')
        # Simplest invocation. Creates table and column chart on Sheet1 worksheet with default presentation settings.
        morpc.data_chart_to_excel(df, writer)  
        # Creates a table and line chart on the "LineChart" worksheet with default presentation settings.
        morpc.data_chart_to_excel(df, writer, sheet_name="LineChart", chartType="line")
        # Creates a table and stacked column chart on the "Stacked" worksheet with default presentation settings.
        morpc.data_chart_to_excel(df, writer, sheet_name="Stacked", chartType="column", chartOptions={"subtype":"stacked"})
        # Creates a table and bar chart on the "Custom" worksheet with some custom presentation settings.
        morpc.data_chart_to_excel(df, writer, sheet_name="Custom", chartType="bar", chartOptions={
            "colors": ["cyan","magenta"],                   # Specify a custom color
            "hideLegend": True,                             # Hide the legend
            "titles": {                                     # Specify the chart title and axis titles
                "chartTitle": "My Chart",
                "xTitle": "My independent variable",
                "yTitle": "My dependent variable",
            }
        })
        writer.close()
                
    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        The pandas dataframe which contains the data to export.  The dataframe column index will be used as the
        column headers (i.e. the first row) in the output table.  By default, the dataframe row index will become
        the first column in the output table (this can be overridden using the dataOptions argument).  The columns
        in the dataframe will become series in the chart.
    writer : pandas.io.excel._xlsxwriter.XlsxWriter
        An existing xlsxwriter object created using pd.ExcelWriter(..., engine='xlsxwriter'). This represents the
        Excel workbook to which the data and chart will be written. See https://xlsxwriter.readthedocs.io/working_with_pandas.html
    sheet_name : str, optional
        The label for a new worksheet that will be created in the Excel workbook.  Must be unique and cannot exist
        already.  Default value is "Sheet1"
    chartType : str, optional
        A chart type as recognized by xlsxwriter workbook.add_chart. Options include "area", "bar", "column", "doughnut", 
        "line", "pie","radar","scatter","stock". Default is "column". Set to "omit" to omit the chart and include only the
        data table.  Bar and line charts are well-supported. Results with other types may vary. See
        https://xlsxwriter.readthedocs.io/workbook.html#add_chart
    dataOptions: dict, optional
        Various configuration options for the output data table. Currently the following options are supported.
            "index": bool
                Whether to write the index as a column in the Excel file.  Default is True. Set to False to omit the index.
            "numberFormat" : str, list, or dict
                Excel number format string to use for the values in the output table. 
                If a string, the same format will be applied to all columns.
                If a list, the listed formats will be applied to the columns in sequence.  
                If a dict, the dict keys must match the column names and the dict values will contain the format
                    string to use for the column.
                Default is "#,##0.0".  See https://xlsxwriter.readthedocs.io/format.html#set_num_format
            "columnWidth" : int, list, or dict
                Widths of columns in output table. 
                If an int, the same width will be applied to all columns.
                If a list, the listed widths will be applied to the columns in sequence.  
                If a dict, the dict keys must match the column names and the dict values will contain the width
                    to use for the column.            
                Default is 12.  
    chartOptions: dict, optional
        Various configuration options for the output chart. Currently the following options are supported.
            "colors" : str, list, or dict
                Simplified method of specifying the color or color to use for the series in the chart.  Will be 
                overridden by series-specific options in chartOptions["seriesOptions"]. By default will cycle
                through MORPC brand colors.
                If a string, the same color will be used for all series. 
                If a list, the listed colors will be repeated in sequence. 
                If a dict, the dict keys must match the series names and the dict values will determine the colors
                for the corresponding series.
            "hideLegend" : bool
                Simplified method of hiding the legend, which is shown by default.  Set hideLegend = True to hide the
                legend. Will be overridden by settings in chartOptions["legendOptions"].
            "titles" : str or dict
                Simplified method of specifying the chart and axis titles.  Will be overridden by settings in 
                chartOptions["titleOptions"]. 
                If a string, it will be used as the chart title. 
                If a dict, it should have the following form. If any key/value is unspecified, it will default to the
                values shown below.
                    {
                        "chartTitle": sheet_name,
                        "xTitle": df.index.name,
                        "yTitle": df.columns.name
                    }
            "labelOptions" : dict or list of dicts,
                Simplified method of specifying data labels.  Will be overidden by settings in seriesOptions.
                If a dict, the same settings will be applied to all series
                If a list of dicts, the dict keys must match the series names and the dict values will determine the
                settings for the labels for the corresponding series.
                The dict will be used as the data_labels argument for chart.add_series().  See 
                https://xlsxwriter.readthedocs.io/chart.html#chart-add-series and
                https://xlsxwriter.readthedocs.io/working_with_charts.html#chart-series-option-data-labels
            "subtype" : str
                The desired subtype of the specified chartType, as recognized by workbook.add_chart(). Your mileage may
                vary. Some subtypes may not be well supported yet. If unspecified, this will default to whatever default
                xlsxwriter uses for the specified chartType.
                See https://xlsxwriter.readthedocs.io/workbook.html#workbook-add-chart
            "location" : list or str        
                Coordinates specifying where to place the chart on the worksheet.  Default location is to the right of table in
                the first row.  Specify "below" as shorthand to place the chart below the table in the first column.
                Used by worksheet.insert_chart( ). See https://xlsxwriter.readthedocs.io/worksheet.html#worksheet-insert-chart 
                and https://xlsxwriter.readthedocs.io/working_with_cell_notation.html#cell-notation
            "sizeOptions" : dict
                Options to control the size of the chart.  Will be used directly by chart.set_size(). Defaults to xlsxwriter
                defaults. See https://xlsxwriter.readthedocs.io/chart.html#chart-set-size       
            "plotAreaLayout" : dict
                Settings to control the layout of the plot area within the chart.  Will be used directly by chart.set_plotarea().
                Defaults to xlsxwriter defaults.  See https://xlsxwriter.readthedocs.io/working_with_charts.html#chart-layout
            "titleOptions" : dict
                Options to control the appearance of the chart title.  Will be used directly by chart.set_title(). Title text
                defaults to sheet_name. Style defaults to MORPC branding.
                See https://xlsxwriter.readthedocs.io/chart.html#chart-set-title
            "seriesOptions" : dict of dicts or list of dicts
                Options to control how series are displayed.  Used directly by chart.add_series().
                If a dict of dicts, the top level keys must correspond to the column names and the values will be applied to the
                corresponding series. If a key/value is not present for a column name, that series will revert to default settings.
                If a list of dicts, the dicts will be applied to the columns in sequence.
                corresponding series. If there are not enough items in the list for all of the columns, the remaining series will 
                revert to default settings.
                See https://xlsxwriter.readthedocs.io/chart.html#chart-add-series
            "xAxisOptions": dict
                Options to control the appearance of the x axis.  Will be used directly by chart.set_x_axis(). Axis title defaults 
                to df.index.name. Style defaults to MORPC branding. Title will be overridden by "titles" parameter (see above). See 
                https://xlsxwriter.readthedocs.io/chart.html#chart-set-x-axis
            "yAxisOptions": dict
                Options to control the appearance of the y axis.  Will be used directly by chart.set_y_axis(). Axis title defaults 
                to df.columns.name. Style defaults to MORPC branding. Title will be overridden by "titles" parameter (see above). See https://xlsxwriter.readthedocs.io/chart.html#chart-set-y-axis
            "legendOptions": dict
                Options to control the appearance of the legend. Will be used directly by chart.set_legend(). Legend is displayed by
                default and positioned at the bottom of the chart.  Style defaults to MORPC branding. See
                https://xlsxwriter.readthedocs.io/chart.html#chart-set-legend
    
    Returns
    -------
    None
    
    """

    import pandas as pd
    import json
    import xlsxwriter

    axisSwapTypes = ["bar"]

    colorsDefault = CONST_COLOR_CYCLES['morpc'] 

    styleDefaults = {
        "fontName": "Arial",
        "fontSize": 10,
        "titleFontSize": 14,
        "axisNameFontSize": 9,
        "axisNumFontSize": 8,
        "legendFontSize": 10,
        "seriesColor": colorsDefault[0],
        "numberFormat": "#,##0.0",
        "columnWidth": 12
    }
    

    titleDefaults = {
        "chartTitle": sheet_name,
        "xTitle": df.index.name,
        "yTitle": df.columns.name
    }
    
    titleOptionsDefaults = {
        "name": titleDefaults["chartTitle"],
        "overlay": False,
        "name_font": {
            "name": styleDefaults["fontName"],
            "size": styleDefaults["titleFontSize"]
        }
    }
  
    axisOptionsDefaults = {
        "name_font": {
            "name": styleDefaults["fontName"],
            "size": styleDefaults["axisNameFontSize"]
        },
        "num_font": {
            "name": styleDefaults["fontName"],
            "size": styleDefaults["axisNumFontSize"]
        },
        "label_position": 'low',
        "reverse": False
    }


    xAxisOptionsDefaults = json.loads(json.dumps(axisOptionsDefaults))
    xAxisOptionsDefaults["name"] = titleDefaults["xTitle"]

    yAxisOptionsDefaults = json.loads(json.dumps(axisOptionsDefaults))
    yAxisOptionsDefaults["name"] = titleDefaults["yTitle"]

    legendOptionsDefaults = {
        "none": False,
        "position": "bottom",
        "font": {
            "name": styleDefaults["fontName"],
            "size": styleDefaults["legendFontSize"]
        }
    }
 
    seriesOptionsDefault = {
        "common": {
        }
    }

    seriesOptionsDefault["bar"] = json.loads(json.dumps(seriesOptionsDefault["common"]))
    seriesOptionsDefault["bar"] = recursiveUpdate(seriesOptionsDefault["bar"], {
        "border": {"none":True},
        "fill": {
            "color": styleDefaults["seriesColor"]
        }
    })
    seriesOptionsDefault["column"] = json.loads(json.dumps(seriesOptionsDefault["bar"]))

    seriesOptionsDefault["line"] = json.loads(json.dumps(seriesOptionsDefault["common"]))
    seriesOptionsDefault["line"] = recursiveUpdate(seriesOptionsDefault["line"], {
        "line": {
            "color": styleDefaults["seriesColor"],
            "width": 2.5          
        },
        "marker": {
            "type": "circle",
            "size": 5,
            "border": {"none":True},
            "fill": {
                "color": styleDefaults["seriesColor"]
            }
        },
        "smooth": False
    })
    
    subtypesDefaults = {
        "bar": None,
        "column": None,
        "line": None
    }
     
    myDataOptions = {
        "index": True,               # Write the index to the Excel file by default
        # String, list, or dict. If a string, the same format will be applied to all columns.  If a 
        # list, the listed formats will be applied to the columns in sequence.  If a dict, the keys must 
        # match the columns names and the values will format for each.
        "numberFormat": styleDefaults["numberFormat"],
        "columnWidth": styleDefaults["columnWidth"]
    }
    if(dataOptions != None):
        myDataOptions = recursiveUpdate(myDataOptions, dataOptions)

    myChartOptions = {
        # String, list, or dict.  Simplified method of specifying series colors. Overridden by setting in 
        # chartOptions["seriesOptions"]. If a string, the same color will be used for all series. If a 
        # list, the listed colors will be repeated in sequence. If a dict, the keys must match the series 
        # names and the values will determine the colors.
        "colors": None,
        # Bool. Simplified method of hiding the legend. Overridden by setting in chartOptions["legendOptions"]
        "hideLegend": False,
        # String or dict. Simplified method of specifying the chart and axis titles.  Overridden by setting in chartOptions["titleOptions"]. If a string, it will be used as the chart title. If a dict, it will have the same format as titleDefaults
        "titles": None,
        # Dict to be applied to all series or list of dicts, one per series. Simplified method of specifying data labels.  
        # Used by chart.add_series()
        "labelOptions": None,
        "subtype": None,          # String. Defer to chart-specific default. Used by workbook.add_chart()
        "location": None,         # List. Default location is to the right of data. Will be determined later.
        "sizeOptions": None,      # Dict. Will be used by chart.set_size()
        "plotAreaOptions": None,   # Dict. Will be used by chart.set_plotarea()
        "titleOptions": None,     # Dict. Will be used by chart.set_title()
        "seriesOptions": None,    # Dict to be applied to all series or list of dicts, one per series. Used by chart.add_series()
        "xAxisOptions": None,     # Dict. Will be used by chart.set_x_axis()
        "yAxisOptions": None,     # Dict. Will be used by chart.set_y_axis()
        "legendOptions": None,    # Dict. Will be used by chart.set_legend()
        "includeColumns": None    # List of columns to be added as series to chart.   
    }
    if(chartOptions != None):
        myChartOptions = recursiveUpdate(myChartOptions, chartOptions)

    myLegendOptions = json.loads(json.dumps(legendOptionsDefaults))
    if(myChartOptions["hideLegend"] == True):
        myLegendOptions["none"] = True
    if(myChartOptions["legendOptions"] != None):
        myLegendOptions = recursiveUpdate(myLegendOptions, chartOptions["legendOptions"])

    if(myChartOptions["includeColumns"] == None):
        myChartOptions["includeColumns"] = list(df.columns)
       
    workbook = writer.book

    df.to_excel(writer, sheet_name=sheet_name, index=myDataOptions["index"])

    worksheet = writer.sheets[sheet_name]

    if(type(myDataOptions["numberFormat"]) == str):
        numberFormats = workbook.add_format({'num_format': myDataOptions["numberFormat"]})
    elif(type(myDataOptions["numberFormat"]) == list):
        numberFormats = [workbook.add_format({'num_format': value}) for value in myDataOptions["numberFormat"]] 
    elif(type(myDataOptions["numberFormat"]) == dict):
        numberFormats = {key: workbook.add_format({'num_format': value}) for key, value in zip(myDataOptions["numberFormat"].keys(), myDataOptions["numberFormat"].values())}

    columnWidths = json.loads(json.dumps(myDataOptions["columnWidth"]))

    if(myDataOptions["index"] == True):
        indexName = df.index.name
        if(indexName == None):
            indexName = "index"
        df = df.reset_index()
    nRows = df.shape[0]
    nColumns = df.shape[1]
    for i in range(0, nColumns):
        colname = df.columns[i]
        
        if(type(numberFormats) == xlsxwriter.format.Format):
            columnNumberFormat = numberFormats
        elif(type(numberFormats) == list):
            try:
                columnNumberFormat = numberFormats[i]
            except:
                print(f"WARNING: Number format not specified for column {i} (column {colname}). Using default.")
                columnNumberFormat = styleDefaults["numberFormat"]
        elif(type(numberFormats) == dict):
            try:
                columnNumberFormat = numberFormats[colname]
            except:
                print(f"WARNING: Number format not specified for column {colname}). Using default.")
                columnNumberFormat = styleDefaults["numberFormat"]

        if(type(columnWidths) == int):
            columnWidth = columnWidths
        elif(type(columnWidths) == list):
            try:
                columnWidth = columnWidths[i]
            except:
                print(f"WARNING: Column width not specified for column {i} (column {colname}). Using default.")
                columnWidth = styleDefaults["columnWidth"]
        elif(type(columnWidths) == dict):
            try:
                columnWidth = columnWidths[colname]
            except:
                print(f"WARNING: Column width not specified for column {colname}). Using default.")
                columnWidth = styleDefaults["columnWidth"]
        
        worksheet.set_column(i, i, columnWidth, columnNumberFormat)

    if(myDataOptions["index"] == True):
        df = df.set_index(indexName)

    if(chartType == "omit"):
        print("WARNING: Chart type is set to omit.  Chart will be omitted.")
        return

  
    chart = workbook.add_chart({
        "type": chartType, 
        "subtype": (myChartOptions["subtype"] if myChartOptions["subtype"] != None else subtypesDefaults[chartType])
    })

    nRows = df.shape[0]
    nColumns = len(myChartOptions["includeColumns"])
    for i in range(1, nColumns+1):
        colname = myChartOptions["includeColumns"][i-1]
        # Get the position of this column in the worksheet.  It may not match the value of i because of columns omitted by the user. 
        colpos = list(df.columns).index(colname) + 1

        mySeriesOptions = json.loads(json.dumps(seriesOptionsDefault[chartType]))
        
        color = None
        # If the user specified a color or set of colors in chartOptions["colors"], use those instead of the defaults.
        if(myChartOptions["colors"] != None):
            if(type(myChartOptions["colors"]) == str):
                color = myChartOptions["colors"]
            elif(type(myChartOptions["colors"]) == list):
                color = myChartOptions["colors"][(i-1) % len(myChartOptions["colors"])]        
            elif(type(myChartOptions["colors"]) == dict):
                color = myChartOptions["colors"].get(colname, styleDefaults["seriesColor"])   # Revert to default if color is not specified for column
            json.dumps(mySeriesOptions, indent=4)
        # Else if we have more than one series, cycle through the default set of colors
        elif(nColumns > 1):
            color = colorsDefault[(i-1) % len(colorsDefault)]
        # Else, simply stick with the single default color defined above in seriesOptionsDefault

        if(color != None):
            if "fill" in mySeriesOptions.keys():
                mySeriesOptions["fill"]["color"] = color
            if "line" in mySeriesOptions.keys():
                mySeriesOptions["line"]["color"] = color
            if "marker" in mySeriesOptions.keys():                
                mySeriesOptions["marker"]["fill"]["color"] = color

        if(type(myChartOptions["seriesOptions"]) == list):
            try:
                mySeriesOptions = recursiveUpdate(mySeriesOptions, myChartOptions["seriesOptions"][i-1])
            except Exception as e:
                print(f"WARNING: Failed to get chartOptions['seriesOptions'] for list item {i-1} (column {colname}). Using defaults.") 
        elif(type(myChartOptions["seriesOptions"]) == dict):
            try:
                mySeriesOptions = recursiveUpdate(mySeriesOptions, myChartOptions["seriesOptions"][colname])
            except Exception as e:
                print(f"WARNING: Failed to get chartOptions['seriesOptions'] for column {colname}). Using defaults.") 

        mySeriesOptions["name"] = [sheet_name, 0, colpos]
        mySeriesOptions["categories"] = [sheet_name, 1, 0, nRows, 0]
        mySeriesOptions["values"] = [sheet_name, 1, colpos, nRows, colpos]
                
        # Configure chart title
        # Start with default values
        myTitleOptions = json.loads(json.dumps(titleOptionsDefaults))
        # If user provided a dict of title options, update the default values with provided values
        if(myChartOptions["titleOptions"] != None):
            myTitleOptions = recursiveUpdate(myTitleOptions, myChartOptions["titleOptions"])
        # Otherwise, if user provided only the chart title as a string using the simplified form, override the default string
        elif(type(myChartOptions["titles"]) == str):
            myTitleOptions["name"] = myChartOptions["titles"]
        # Otherwise, if user provided a simplified dict of chart titles and axis titles, try to use the provided chart title. If
        # the chart title was not provided in the dict, revert to the default. 
        elif(type(myChartOptions["titles"]) == dict):
            myTitleOptions["name"] = myChartOptions["titles"].get("chartTitle", titleOptionsDefaults["name"])

        # Configure the x-axis
        # Start with default values
        myXAxisOptions = json.loads(json.dumps(xAxisOptionsDefaults))
        # If user provided a dict of x-axis options, update the default values with provided values
        if(myChartOptions["xAxisOptions"] != None):
            myXAxisOptions = recursiveUpdate(myXAxisOptions, myChartOptions["xAxisOptions"])
        # Otherwise, if user provided a simplified dict of chart titles and axis titles, try to use the provided x-axis title. If
        # the x-axis title was not provided in the dict, revert to the default. 
        if(type(myChartOptions["titles"]) == dict):
            myXAxisOptions["name"] = myChartOptions["titles"].get("xTitle", xAxisOptionsDefaults["name"])

        # Configure the y-axis
        # Start with default values
        myYAxisOptions = json.loads(json.dumps(yAxisOptionsDefaults))
        # If user provided a dict of y-axis options, update the default values with provided values
        if(myChartOptions["yAxisOptions"] != None):
            myYAxisOptions = recursiveUpdate(myYAxisOptions, myChartOptions["yAxisOptions"])
        # Otherwise, if user provided a simplified dict of chart titles and axis titles, try to use the provided y-axis title. If
        # the y-axis title was not provided in the dict, revert to the default. 
        if(type(myChartOptions["titles"]) == dict):
            myYAxisOptions["name"] = myChartOptions["titles"].get("yTitle", yAxisOptionsDefaults["name"])
           
        chart.add_series(mySeriesOptions)

    if(chartType in axisSwapTypes):
        tempX = myXAxisOptions["name"]
        tempY = myYAxisOptions["name"]
        myXAxisOptions["name"] = tempY
        myYAxisOptions["name"] = tempX
 
    chart.set_title(myTitleOptions)
    chart.set_x_axis(myXAxisOptions)
    chart.set_y_axis(myYAxisOptions)        
    chart.set_legend(myLegendOptions)   
    # If the user specified chart size options, use them as-is. There are 
    # no defaults for this.
    if(myChartOptions["sizeOptions"] != None):
            chart.set_size(myChartOptions["sizeOptions"])
    # If the user specified a plot area layout, use it as-is. There are 
    # no defaults for this.
    if(myChartOptions["plotAreaOptions"] != None):
        chart.set_plotarea(myChartOptions["plotAreaOptions"])
    
    if(myChartOptions['location'] == "below"):
        # If the user specifies "below", put the chart below the table in the first column
        myLocation = [worksheet.dim_rowmax+2, 0]
    elif(myChartOptions['location'] != None):
        # If the user specified the location in some other way, use their specification as-is
        myLocation = myChartOptions['location']
    else:
        # Otherwise, if the user did not specify the location, then put the chart to the right of the table in the first row
        myLocation = [0, worksheet.dim_colmax+2]
    
    if(type(myLocation) == list):
        worksheet.insert_chart(myLocation[0], myLocation[1], chart)
    elif(type(myLocation) == str):
        worksheet.insert_chart(myLocation, chart)
    else:
        print('ERROR: Chart location must be specified in list form as [row,col] or as a cell reference string like "A5"')
        raise RuntimeError

def extract_vintage(df, vintage=None, refPeriods=None, vintagePeriodField="VINTAGE_PERIOD", refPeriodField="REFERENCE_PERIOD"):
    """From a long-form dataset containing values of various vintages, extract the value for a select vintage for each period.
    If the desired periods are not specified, extract all available periods.  If a single desired vintage is not specified,
    extract the latest available vintage for each period.

    WARNING: This function assumes that if a vintage is available for any records for a reference period, then that vintage is 
    available for all records associated with that reference period.  This is an opportunity for improvement, but until then
    check the output yourself.

    Example usage: See morpc-common-demos.ipynb
                
    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        The pandas dataframe which contains the data from which to generate an extract. The data must contain a column whose
        values represent the reference period for each record (see refPeriodField) and a column whose values represent the
        vintage period for each record (see vintagePeriodField)
    refPeriods: list, optional
        A list containing the desired reference period(s) to extract from the data. List items should have the same type as the
        reference period column (refPeriodField).  If refPeriods == None, all available reference periods will be included in
        the output.
    vintage: scalar (usually int), optional
        A value indicating the desired vintage of the records to be extracted from the data. This should have the same type as
        vintage period column (vintagePeriodField) and must be a type that is compatible with numpy.max (see https://numpy.org/doc/stable//reference/generated/numpy.max.html)  If vintage == None, the most recent available 
        vintage for each reference period will be extracted.
    refPeriodField: scalar, optional
        The name of the column in df that contains the reference periods. If unspecified, defaults to "REFERENCE_PERIOD".
    vintagePeriodField: scalar, optional
        The name of the column in df that contains the vintage periods. If unspecified, defaults to "VINTAGE_PERIOD".
    
    Returns
    -------
    outDf : pandas.core.frame.DataFrame
        A subset of df that contains only the specified (or most recent) vintage for the requested reference periods
    
    """
    import pandas as pd
    
    # If user specified a set of reference periods, verify that all requested periods are present and extract those. 
    # Otherwise keep the whole input dataframe.
    if refPeriods == None:
        tempDf = df.copy()
        refPeriods = list(tempDf[refPeriodField].unique())
    else:
        tempDf = df.loc[df[refPeriodField].isin(refPeriods)].copy()
        if not set(tempDf[refPeriodField]) == set(refPeriods):
            # If any of the requested periods are not available, list those and throw an error
            print("ERROR: The following requested reference periods are not available in the data: {}".format(
                ", ".join([str(x) for x in set(refPeriods) - set(tempDf[refPeriodField])])
            ))
            raise RuntimeError

    # Construct a dictionary mapping each reference period to a particular vintage
    selectedVintages = {}
    for period in refPeriods:
        # Make a list of the available vintages for each reference period.  See warning in docstring above.
        availableVintages = tempDf.loc[tempDf[refPeriodField] == period, vintagePeriodField].unique()
        if vintage != None:
            # If the user specified a vintage, make sure that the vintage is available for this reference period
            if not vintage in availableVintages:
                # If requested vintage is not available, throw an error
                print("ERROR: Requested vintage is not available for reference period {}".format(period))
                raise RuntimeError
            else:
                # Otherwise, select that vintage
                selectedVintages[period] = vintage
        else:
            # If the user did not specify a vintage, select the largest (most recent) vintage available for this period
            selectedVintages[period] = availableVintages.max()

    # For each reference period, extract the records associated with the selected vintage for that period.
    # TBD - Is there a more efficient way to do this?
    firstTime = True
    for thisPeriod in selectedVintages:
        # Extract the records for this period which are associated with the selected vintage
        temp = tempDf.loc[(tempDf[refPeriodField] == thisPeriod) & (tempDf[vintagePeriodField] == selectedVintages[thisPeriod])].copy()
        if(firstTime):
            # If this is the first reference period (i.e. the first time through the loop) construct the output dataframe from the extract
            firstTime = False
            outDf = temp.copy()
        else:
            # If this is not the first reference period, append the extract to the existing output
            outDf = pd.concat([outDf, temp], axis="index")

    return outDf
    
def qcew_areas_to_suppress(areaPolygonsGDF, qcewPointsGDF, employmentColumn="EMP", verbose=True):
    """The jobs data included in MORPC's GridMAZ forecasts is derived from point-level data from the Quarterly 
    Census of Employment and Wages (QCEW) and may contain data that could identify specific employers.  To protect 
    employer privacy and ensure compliance with our data use agreement, values must be suppressed in the following 
    conditions:
        1. There are fewer than 3 employers in a geography
        2. There are 3 or more employers but a single employer represents 80% or more of the employment in the 
           geography by industry.
 
    Given a set of polygons that represent areas intended to summarize QCEW data, this function determines the areas for 
    which data must be suppressed to satsify the above two conditions.  The function uses a spatial join to assign each 
    QCEW employer location to a polygon, summarizes the points in each polygon, and checks both of the conditions. The
    function returns a pandas Series object indicating which of the indices in the polygon geodataframe need to be
    suppressed due to meeting one or more of the criteria.

    CAVEAT: Regarding the second condition, this function only supports suppression of TOTAL JOBS, not an industry
    subset.  Since we are not breaking down the jobs by industry, it is sufficient to suppress the geographies where an 
    employer represents 80% or more of the the total employment.
    
    Example usage:

    Parameters
    ----------
    areaPolygonsGDF : geopandas.geodataframe.GeoDataFrame with polygon geometry type
        A GeoPandas GeoDataFrame containing the polygons for which the QCEW would be summarized.  Only the geometries
        are required.  The other columns will not be used and no summary is provided by this function.  It is assumed
        that the area polygons are non-overlapping.
    qcewPointsGDF : geopandas.geodataframe.GeoDataFrame with point geometry type
        A GeoPandas GeoDataFrame containing the QCEW employer locations (points). Must include a column containing
        the total employment provided by the employer (see below).  Only the geometry and the employment column
        will be used.
    employmentColumn : str
        Optional. Name of the column in qcewPointsGDF that contains the employment provided by each employer. If unspecified, 
        this will default to "EMP".
    verbose : boolean
        Optional. Default value is True. Set to False to suppress informational text output from the function.

    Returns
    -------
    areaPolygonsSuppressed : pandas.core.series.Series
        A Pandas Series using the same index as areaPolygonsGDF whose values indicate whether the record must be 
        suppressed (True) or not (False)
    
    """
    import pandas as pd
    import geopandas as gpd
    
    employerLocations = qcewPointsGDF.copy()

    # Get the index column name so that we'll know what it is after we reset the index
    if(areaPolygonsGDF.index.name == None):
        indexColumn = "index"
    else:
        indexColumn = areaPolygonsGDF.index.name

    # Use a spatial join to associate each of the points with one of the area polygons
    employerLocationsEnriched = employerLocations.sjoin(areaPolygonsGDF.reset_index()[[indexColumn,"geometry"]])

    # Verify that all employers now have a polygon ID assigned
    temp = employerLocationsEnriched.loc[employerLocationsEnriched[indexColumn].isna()].copy()
    if not temp.empty:
        print("morpc.qcew_areas_to_suppress | WARNING | Some employer locations were not assigned to a polygon.")

    ## Determine which geographies have fewer than 3 employers.  Store the list of geography identifiers in `lowCountGeos`.
    # Create a temporary dataframe with minimal attributes.
    temp = employerLocationsEnriched[[indexColumn]].copy()
    # Create a field to tabulate the count.  Set it to 1 since each record counts as 1.
    temp["COUNT"] = 1
    # Count the records in each geography
    temp = temp.groupby(indexColumn).count().reset_index()
    # Create a list of the unique geography IDs that have fewer than 3 employers.
    lowCountGeos = temp.loc[temp["COUNT"] < 3, indexColumn].unique()
    # Don't print out the entire list of IDs, but rather just the number of geographies in the list.
    if(verbose):
        print("morpc.qcew_areas_to_suppress | INFO | There are {} geographies containing fewer than 3 employers".format(len(lowCountGeos)))

    ## Determine which geographies have 3 or more employers and in which a single employer represents 80% or more of 
    ## the total employment.
    # Create a temporary dataframe with minimal attributes.
    temp = employerLocationsEnriched \
        .loc[employerLocationsEnriched[indexColumn].isin(lowCountGeos) == False, [indexColumn, employmentColumn]] \
        .copy()
    # Include only the employers who employ one or more workers.
    temp = temp.loc[temp[employmentColumn] > 0].copy()
    # Sum the employees in each geography and associate the geography sum with each record in the geography
    temp = temp.merge(temp.groupby(indexColumn).sum().rename(columns={employmentColumn:"GRID_SUM"}), on=indexColumn)
    # Compute the share of the geography sum that each employer represents
    temp["GRID_SHARE"] = temp[employmentColumn] / temp["GRID_SUM"]
    # Identify the geographies containing an employer whose geography share is 80% or more.
    highShareGeos = temp.loc[temp["GRID_SHARE"] >= 0.8, indexColumn].unique()
    if(verbose):
        print("morpc.qcew_areas_to_suppress | INFO | There are {} geographies containing employers with a share 80% or greater".format(len(highShareGeos)))

    ## Create a single list of the geographies that meet either of the two suppression conditions.  
    ## The blocks above are structured in such a way that the two lists are mutually exclusive, therefore the 
    ## length of the combined list should be the sum of the lengths of the individual lists.
    suppressGrids = pd.Index(lowCountGeos).union(pd.Index(highShareGeos))
    if(verbose):
        print("morpc.qcew_areas_to_suppress | INFO | There are {} geographies that must be suppressed.".format(len(suppressGrids)))

    return suppressGrids
    
def add_placecombo(df, countyField="COUNTY", jurisField="JURIS", munitypeField="MUNITYPE"):
    import pandas
    import geopandas
    outDf = df.copy()
    outDf["PLACECOMBO"] = outDf[countyField].str.upper() + "_" + outDf[jurisField].str.upper() + "_" + outDf[munitypeField].str.upper()
    return outDf

def md5(fname):
    """
    md5() computes the MD5 checksum for a file.  When the original checksum is known, the current checksum can be compared to it to determine whether the file has changed.

    Input parameters:
      - fname is a string representing the path to the file for which the checksum is to be computed

     Returns:
       - MD5 checksum for the file
    """
    import hashlib
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def write_table(df, path, format=None, index=None):
    """Write a pandas dataframe to a tabular data file applying MORPC file standards
    
    Example usage: morpc.write_table(myDf, "./path/to/somefile.csv")

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        A pandas DataFrame that is to be written to a tabular data file.
    path : str
        The path to the data file to be written
    format : str
        Optional. The file format to use. Currently "csv" and "xlsx" are supported.  If format is not specified, it will be inferred from the file
        extension provided in path
    index : bool
        Optional. Set to True to include the dataframe index in the output. Set to False otherwise. Specifying a value here overrides the MORPC default
        specified in morpc.PANDAS_EXPORT_ARGS_OVERRIDE.
        

    Returns
    -------
    None
    
    """
    import os
    import pandas
    import json
    
    outDf = df.copy()

    if(format == None):
        print("morpc.write_table | INFO | Format is unspecified. Will attempt to determine format based on file extension.")
        format = os.path.splitext(path)[1]

    format = format.lower()

    try:
        exportArgs = json.loads(json.dumps(PANDAS_EXPORT_ARGS_OVERRIDE[format]))
    except KeyError:
        print("morpc.write_table | ERROR | This function does not currently support format {}.  Add export arguments for this format in morpc.PANDAS_EXPORT_ARGS_OVERRIDE or use the native pandas export functions.".format(format))
        raise RuntimeError

    if(index != None):
        exportArgs["index"] = index
   
    print("morpc.write_table | INFO | Writing dataframe to file {}".format(path))     
    if(format == "csv"):
        outDf.to_csv(path, **exportArgs)
    elif(format == "xlsx"):
        outDf.to_excel(path, **exportArgs)
    else:
        print("morpc.write_table | ERROR | This function does not currently support format {}.  Add export arguments for this format in morpc.PANDAS_EXPORT_ARGS_OVERRIDE or use the native pandas export functions.".format(format))
        raise RuntimeError

def reapportion_by_area(targetGeos, sourceGeos, apportionColumns=None, summaryType="sum", roundPreserveSum=None, partialCoverageStrategy="error", zeroCoverageStrategy="error", sourceShareTolerance=6, targetShareTolerance=6, returnIntersectData=False):
    """
    Given you have some variable(s) summarized at one geography level, reapportion those variables to other geographies in proportion 
    # to the area of overlap of the target geographies with the source geographies.  This is accomplished by intersecting the target 
    # geographies with the source geographies, then summarizing the variable(s)     by the target geography index.
    
    Example usage: 
        # Reapportion block-level decennial census counts to library districts.  Included only the "POP" column from the census data.  
        # Round reapportioned values to integers. Throw warning if the source shares do not sum to 1 after rounding to the 3rd decimal place.
        libraryDistrictPop = morpc.reapportion_by_area(libraryDistrictGeos, censusBlockPopulation, apportionColumns=["POP"], roundPreserveSum=0, overlayShareTolerance=3)

    Parameters
    ----------
    targetGeos : geopandas.geodataframe.GeoDataFrame with polygon geometry type
        A GeoPandas GeoDataFrame containing the polygons for which you want to summarize the variables.for which the QCEW would be 
        summarized.  Only the geometries are required.  The other columns will be preserved but will not be used. It is assumed that 
        the target polygons are non-overlapping and fully cover the source geographies.
    sourceGeos : geopandas.geodataframe.GeoDataFrame with polygon geometry type
        A GeoPandas GeoDataFrame containing the variables to be reapportioned (summarized) for the target geographies. It is assumed 
        that the source polygons are non-overlapping.
    apportionColumns : str
        Optional. List of columns containing the variables to be reapportioned.  If apportionColumns is unspecified, the function will 
        attempt to reapportion all columns other than geometry.  This will lead to an error if non-numeric columns are present.
    roundPreserveSum : int
        Optional. If set to an integer, round the reapportioned values to the specified number of decimal places while preserving their 
        sum.  Uses morpc.round_preserve_sum().  Note that the sum for the entire collection of values is preserved, not the sums by target 
        geo.  Set to None to skip rounding. Ignored when summaryType == "mean".
    summaryType: str
        Optional. The name of the function to use to summarize the variables for the target geos. The default is to sum the variables within 
        the target geos.  Supported functions include "sum", "mean"
    partialCoverageStrategy: str
        Optional. How to handle cases where the target geographies only partially cover a source geography. Use "error" to throw an error.
        Use "ignore" to do nothing. This leaves some portion of the variable(s) unapportioned. Use "distribute" to distribute the remainder 
        of the variable(s) to the target geographies in proportion to their area of overlap.  Ignored when summaryType == "mean".
    zeroCoverageStrategy: str
        Optional. How to handle cases where no target geographies overlap a source geography. Use "error" to throw an error. Use "ignore" 
        to do nothing. This the full variable(s) for that source geography unapportioned. Use "distribute" to distribute the variable(s) 
        to ALL target geographies in such a manner that their global shares of the variable remain constant. Ignored when summaryType == "mean".     
    sourceShareTolerance : int
        Optional. If set to an integer, warn the user if the source shares for intersection polygons associated with one or more source 
        geographies do not sum to 1.  Round the sums to the specified decimal place prior to evaluation.  Sum greater than 1 may indicate 
        that there are overlapping polygons in the target geos or source geos. Sum less than 1 may indicate that target geo coverage of 
        source geos is incomplete.  Set to None to allow no tolerance (warning will be generated if shares do not sum to exactly 1).
    targetShareTolerance : int
        Optional. If set to an integer, warn the user if the target shares for intersection polygons associated with one or more target 
        geographies do not sum to 1.  Round the sums to the specified decimal place prior to evaluation.  Sum greater than 1 may indicate 
        that there are overlapping polygons in the target geos or source geos. Sum less than 1 may indicate that portions of the target geos
        do not overlap the source geos. Set to None to allow no tolerance (warning will be generated if shares do not sum to exactly 1).
    returnIntersectData : bool
        Optional. If False, return only one output consisting of the reapportioned data (default). If true, return a second output (GeoDataFrame)
        consisting of the intersection geometries and their attributes.
        
    Returns
    -------
    targetGeosUpdated :  geopandas.geodataframe.GeoDataFrame with polygon geometry type
        An updated version of targetGeos that includes the reapportioned variables.
    intersectGeosUpdate : geopandas.geodataframe.GeoDataFrame with polygon geometry type
        If requested. The results of the intersection of the source geos and target geos, including
        areas and shares for both, plus geometry and area for the intersection polygon.
    """

    import pandas as pd
    import geopandas as gpd

    # Verify that the user specified a valid summary type before we get started
    if(not summaryType in ["sum","mean"]):
        print("morpc.reapportion_by_area | ERROR | Summary type '{}' is not supported".format(summaryType))
        raise RuntimeError        
    
    # Check whether the user has specified which variables are to be reapportioned.
    # If not, assume that all variables are to be reapportioned (except geometry)
    if(apportionColumns == None):
        apportionColumns = list(sourceGeos.columns.drop("geometry"))

    # Verify that the coordinate reference systems for the two sets of geographies are
    # the same.  If not, spatial operations will produce incorrect results.
    if(targetGeos.crs != sourceGeos.crs):
        print("morpc.reapportion_by_area | ERROR | Target geos and source geos must use the same coordinate reference system")
        raise RuntimeError

    # Create a working copy of the target geos dataframe.  Temporarily separate the attributes for 
    # the target geos from the geometries. This will make it easier to summarize the reapportioned 
    # variables later.
    myTargetGeosAttr = targetGeos.copy().drop(columns="geometry")
    targetGeosUpdated = targetGeos.copy().filter(items=["geometry"], axis="columns")
    
    # Create a working copy of the source geos and eliminate unneeded variables
    mySourceGeos = sourceGeos.copy().filter(items=apportionColumns+["geometry"], axis="columns")

    # Store the name of the indexes used for the target geos and source geos and then reset the index for each dataframe
    # to bring the identifiers out into a series. Standardize the names of the identifier fields.  This will preserve the identifiers
    # to summarize the reapportioned variables. The target geos index will be restored in the output.
    if(targetGeosUpdated.index.name is None):
        targetGeosUpdated.index.name = "None"
    targetGeosIndexName = targetGeosUpdated.index.name
    targetGeosUpdated = targetGeosUpdated.reset_index()
    targetGeosUpdated = targetGeosUpdated.rename(columns={targetGeosIndexName:"targetIndex"})
    if(mySourceGeos.index.name is None):
        mySourceGeos.index.name = "None"
    sourceGeosIndexName = mySourceGeos.index.name
    mySourceGeos = mySourceGeos.reset_index()
    mySourceGeos = mySourceGeos.rename(columns={sourceGeosIndexName:"sourceIndex"})

    # Compute the areas of the source geos
    mySourceGeos["SOURCE_GEOS_AREA"] = mySourceGeos.area

    # Compute the areas of the target geos
    targetGeosUpdated["TARGET_GEOS_AREA"] = targetGeosUpdated.area
    
    # Intersect the source geos with the target geos
    intersectGeos = targetGeosUpdated.overlay(mySourceGeos, keep_geom_type=True)

    # Compute the areas of the intersection polygons
    intersectGeos["INTERSECT_GEOS_AREA"] = intersectGeos.area

    # Compute the share of the source geo that each intersection polygon represents
    intersectGeos["SOURCE_SHARE"] = intersectGeos["INTERSECT_GEOS_AREA"] / intersectGeos["SOURCE_GEOS_AREA"]

    # Compute the share of the target geo that each intersection polygon represents
    intersectGeos["TARGET_SHARE"] = intersectGeos["INTERSECT_GEOS_AREA"] / intersectGeos["TARGET_GEOS_AREA"]

    # Create a copy of the intersection data that we can output if the user requested it. Put the columns in a sensible order.
    intersectGeosOutput = intersectGeos.copy()
    intersectGeosOutput = intersectGeosOutput.filter(items=["sourceIndex","targetIndex","SOURCE_GEOS_AREA","TARGET_GEOS_AREA","INTERSECT_GEOS_AREA",
                                                            "SOURCE_SHARE","TARGET_SHARE","geometry"], axis="columns")
    
    # Make a list of the source geo IDs that appeared in the original source data but do not appear in the intersection data.  
    # These are source geos that had zero overlap with the target geos. If there are entries in the list, throw an error if appropriate.
    if(summaryType == "sum"):
        zeroOverlapSourceGeoList = list(set(list(mySourceGeos["sourceIndex"].unique())).difference(set(list(intersectGeos["sourceIndex"].unique()))))
        if(len(zeroOverlapSourceGeoList) > 0):
            if(zeroCoverageStrategy == "error"):
                print("morpc.reapportion_by_area | ERROR | One or more source geographies is not overlapped by any target geographies. If this is expected, you can suppress this error by setting zeroCoverageStrategy to 'ignore' or 'distribute'.")
                raise RuntimeError         
            elif(zeroCoverageStrategy == "ignore"):
                print("morpc.reapportion_by_area | INFO | Ignoring zero coverage of some source geographies. See zeroCoverageStrategy argument.")                
            elif(zeroCoverageStrategy == "distribute"):
                print("morpc.reapportion_by_area | INFO | Distributing variable(s) from zero-coverage source geographies to target geographies.  See zeroCoverageStrategy argument.")
            else:
                print("morpc.reapportion_by_area | ERROR | Argument value for zeroCoverageStrategy is not supported: {}".format(zeroCoverageStrategy))
                raise RuntimeError            

        if(roundPreserveSum is not None):
            if(type(roundPreserveSum) == int):
                print("morpc.reapportion_by_area | INFO | Rounding variable(s) to {} digits while preserving sum.".format(roundPreserveSum))
            else:
                print("morpc.reapportion_by_area | ERROR | Argument value for roundPreserveSum is not supported: {}".format(roundPreserveSum))
                raise RuntimeError       
    
    # Sum the source shares by source geography and verify that they sum to 1.  This indicates that there are no overlapping polygons 
    # in the target geos or source geos and that the coverage of the source geos by the target geos is complete.  If the shares do not 
    # sum to 1 for one or more source geos, warn the user.  If source geographies are not fully covered, throw errors if appropriate.
    sourceGroupSums = intersectGeos.groupby("sourceIndex")[["SOURCE_SHARE"]].sum()
    sourceGroupSums = sourceGroupSums.rename(columns={"SOURCE_SHARE":"SOURCE_SHARE_SUM"})
    intersectGeos = intersectGeos.merge(sourceGroupSums, on="sourceIndex")
    if(sourceShareTolerance is not None):
        sourceGroupSums["SOURCE_SHARE_SUM"] = sourceGroupSums["SOURCE_SHARE_SUM"].round(decimals=sourceShareTolerance)
    sourceShareMax = sourceGroupSums["SOURCE_SHARE_SUM"].max()
    sourceShareMin = sourceGroupSums["SOURCE_SHARE_SUM"].min()
    if((sourceShareMax != 1) | (sourceShareMin != 1)):
        print("morpc.reapportion_by_area | WARNING | The source shares of the intersection geographies should sum to 1, however they sum to another value in at least one case.  This could mean that the there are overlapping polygons in the target geos or in the source geos (overlay sum > 1), or that the target geos coverage of the overlay geos is incomplete (overlay sum < 1).  The greatest overlay sum is {0} and the smallest overlay sum is {1}. Assess the severity of the discrepancy and troubleshoot the geometries if necessary prior to proceeding.".format(sourceShareMax, sourceShareMin))
        if(summaryType == "sum"):
            if(sourceShareMin < 1):
                if(partialCoverageStrategy == "error"):
                    print("morpc.reapportion_by_area | ERROR | One or more source geographies is not fully covered by target geographies. If this is expected, you can suppress this error by setting partialCoverageStrategy to 'ignore' or 'distribute'.")
                    raise RuntimeError
                elif(partialCoverageStrategy == "ignore"):
                    print("morpc.reapportion_by_area | INFO | Ignoring partial coverage of some source geographies. See partialCoverageStrategy argument.")                
                elif(partialCoverageStrategy == "distribute"):
                    print("morpc.reapportion_by_area | INFO | Distributing variable(s) from non-covered portion of source geographies to covered portions. See partialCoverageStrategy argument.")
                else:
                    print("morpc.reapportion_by_area | ERROR | Argument value for partialCoverageStrategy is not supported: {}".format(partialCoverageStrategy))
                    raise RuntimeError
    
    # Sum the target shares by target geography and verify that they sum to 1.  This indicates that there are no overlapping polygons in the
    # target geos or source geos and that there are no portions of the target geos that did not overlap with the source geos. If the shares do 
    # not sum to 1 for one or more target geos, warn the user.
    targetGroupSums = intersectGeos.groupby("targetIndex")[["TARGET_SHARE"]].sum()
    targetGroupSums = targetGroupSums.rename(columns={"TARGET_SHARE":"TARGET_SHARE_SUM"})
    targetShareMax = targetGroupSums["TARGET_SHARE_SUM"].max()
    targetShareMin = targetGroupSums["TARGET_SHARE_SUM"].min()    
    if(targetShareTolerance is not None):
        targetGroupSums["TARGET_SHARE_SUM"] = targetGroupSums["TARGET_SHARE_SUM"].round(decimals=targetShareTolerance)
    if((targetShareMax != 1) | (targetShareMin != 1)):
        print("morpc.reapportion_by_area | WARNING | The target shares of the intersection geographies should sum to 1, however they sum to another value in at least one case.  This could mean that there are overlapping polygons in the target geos or in the source geos (overlay sum > 1), or that portions of the target geos did not overlap the source geos (overlay sum < 1).  The greatest overlay sum is {0} and the smallest overlay sum is {1}. Assess the severity of the discrepancy and troubleshoot the geometries if necessary prior to proceeding.".format(targetShareMax, targetShareMin))
        
    # For each of the variables to be reapportioned, compute the reapportioned values
    for column in apportionColumns:
        if(summaryType == "sum"):
            print("morpc.reapportion_by_area | INFO | Reapportioning variable {} by sum".format(column))

            # Apportion the total value for the source geography to the intersect polygons in proportion to how
            # much of the area of the source geography the intersection represents. For example, an intersection
            # polygon that covers 40% of the source geography will get 40% of the value associated with that geography
            intersectGeos[column] = (intersectGeos[column] * intersectGeos["SOURCE_SHARE"])

            # If any source geos were only partially overlapped by target geos, apply the strategy specified by the user
            if((sourceShareMin < 1) & (partialCoverageStrategy == "distribute")):
                intersectGeos[column] = (intersectGeos[column] / intersectGeos["SOURCE_SHARE_SUM"])

            # If any source geos had zero overlap by target geos, apply the strategy specified by the user
            if((len(zeroOverlapSourceGeoList) > 0) & (zeroCoverageStrategy == "distribute")):              
                # Compute global shares of values in this column
                intersectGeos["GLOBAL_SHARE"] = intersectGeos[column] / intersectGeos[column].sum()

                # Compute the total of the values for zero-overlap source geos for this column
                zeroOverlapSourceGeoTotal = mySourceGeos.loc[mySourceGeos["sourceIndex"].isin(zeroOverlapSourceGeoList)][column].sum()
                print("morpc.reapportion_by_area | INFO | ---> Redistributing {} ({}% of total) for variable {} from {} zero-overlap source geographies.".format(zeroOverlapSourceGeoTotal, round(zeroOverlapSourceGeoTotal/mySourceGeos[column].sum()*100, 2), column, len(zeroOverlapSourceGeoList)))    
                
                # Multiply the global shares by the totals to get the portion to allocate to each intersect geo
                intersectGeos["ADDITIONAL_PORTION"] = intersectGeos["GLOBAL_SHARE"] * zeroOverlapSourceGeoTotal 
                
                # Add the additional portion for each intersect geo
                intersectGeos[column] = intersectGeos[column] + intersectGeos["ADDITIONAL_PORTION"]

                # Delete temporary columns
                intersectGeos = intersectGeos.drop(columns=["GLOBAL_SHARE","ADDITIONAL_PORTION"])
                
            # If the user specified a value for roundPreserveSum, execute the rounding
            if(roundPreserveSum is not None):
                intersectGeos[column] = round_preserve_sum(intersectGeos[column], digits=roundPreserveSum).astype("int")
            
        elif(summaryType == "mean"):
            # In this case we want the intersect polygon to have the same value as the source geography, however we need to weight the
            # value according to the share of the target geo that the intersection represents.  That way when we summarize the values
            # by target geo later we'll get a weighted mean.
            print("morpc.reapportion_by_area | INFO | Reapportioning variable {} by mean".format(column))
            intersectGeos[column] = (intersectGeos[column] * intersectGeos["TARGET_SHARE"]).astype("float")
        else:
            print("morpc.reapportion_by_area | ERROR | Unsupported summary type. This error should never happen. Troubleshoot code.")
            raise RuntimeError

    # Drop some columns which are no longer needed now that the variables have been reapportioned
    intersectGeos = intersectGeos.drop(columns=["sourceIndex", "SOURCE_GEOS_AREA", "TARGET_GEOS_AREA", "INTERSECT_GEOS_AREA", "SOURCE_SHARE", "TARGET_SHARE", "geometry"])

    # Summarize the variable values for the intersection polygons, grouping by target geo identifier.
    # In the resulting dataframe, the variables are fully reapportioned to the target geos.
    targetGeosUpdate = intersectGeos.groupby("targetIndex").sum()
        
    # Recombine the target geometries with their attributes and add the reapportioned variables
    targetGeosUpdated = targetGeosUpdated.rename(columns={"targetIndex":targetGeosIndexName}).set_index(targetGeosIndexName).join(myTargetGeosAttr).join(targetGeosUpdate)
    if(targetGeosUpdated.index.name == "None"):
        targetGeosUpdated.index.name = None

    # Reorder the target geos columns as they were originally and append the reapportioned variables
    # to the end.
    targetGeosUpdated = targetGeosUpdated.filter(items=list(targetGeos.columns)+apportionColumns, axis="columns")

    if(returnIntersectData == True):
        return (targetGeosUpdated, intersectGeosOutput)
    else:
        return targetGeosUpdated
    
def hist_scaled(series, logy="auto", yRatioThreshold=100, xClassify=False, xRatioThreshold=100, scheme="NaturalBreaks", bins=10, retBinsCounts=False, figsize=None):
    """
    Wrapper for pandas.Series.hist() method which provides additional flexibility for how the data is displayed. By default, function
    automatically decides whether to use a linear scale or a log scale for the y-axis based on the ratio of the counts in the most 
    frequent bin and the least frequent bin (zeros excluded).  Optionally allows for automatic determination of bin edges based on
    classification of data according to a specified scheme and number of classes.  The mapclassify package is used for data classification
    since this is also used by geopandas.plot() and therefore is likely to be installed already in MORPC Python environments.
    
    Parameters
    ----------
    series : pandas.core.series.Series
        A pandas Series containing the data to be displayed in the histogram.  
    logy : bool or "auto"
        Set to True to use log scale on y-axis. Set to "auto" to automatically determine whether to use log scale based on the ratio
        of the counts in the most frequent bin to the least frequent bin (zeros excluded). Specify the threshold above which to use
        log scale using yRatioThreshold.
    yRatioThreshold: numeric value (usually int)
        Threshold for ratio of count in most frequent bin to count in least frequent bin (excluding zeros) above which a 
        log scale will be used.
    xClassify : bool or "auto"
        Set to True to determine bins based on classified data. Specify classification scheme using scheme parameter and bins 
        parameter.  Set to "auto" to automatically determine whether to use classified data based on the ratio of the maximum 
        absolute value in the series to the minimum absolute value in the series. Specify the threshold above which to use
        classified data using xRatioThreshold.
    xRatioThreshold: numeric value (usually int)
        Threshold for ratio of maximum absoulute value in series to minimum absolute value (excluding zeros) above which classified 
        data will be used.
    scheme : str
        Classification scheme supported by mapclassify.classify.
        See https://pysal.org/mapclassify/generated/mapclassify.classify.html#mapclassify.classify
    bins : int
        The number of bins to use for the histogram.  This also serves as the number of classes when classified data is
        used (k parameter for mapclassify.classify).  The range of of the series is extended by .1% on each side to include 
        the minimum and maximum series values as in pandas.cut().
    retBinsCounts : bool
        Set to true to include lists of bins and counts in the return false. Set to false to omit these.
    figsize : tuple
        Figure size tuple as used by pandas.hist()

    Returns
    -------
    retval :  matplotlib.AxesSubplot
        Matplotlib axis object for histogram plot
    binsList : list
        List of bins used for the histogram.
    countsList : list
        List of counts used for the histogram.
    
    """

    import pandas as pd
    import mapclassify

    # If xClassify is set to auto, determine the ratio of the maximum absolute series value
    # to the minimum absolute series value (excluding zero) and compare this to the specified 
    # threshold to determine whether to classify the data. If yes, set xClassify to True. If no, 
    # set xClassify to False.
    if(xClassify == "auto"):
        seriesMin = series.loc[series != 0].abs().min()
        seriesMax = series.abs().max()
        xRatio = seriesMax/seriesMin
        xClassify = (True if (xRatio > xRatioThreshold) else False)

    # If xClassify is set to True (because the user specified this or because it was determined
    # automatically), classify the data using the specified classification scheme and number of bins.
    # Expand the left and right bins by .1% of the series range to ensure the min and max series
    # values are included. If xClassify is set to False, simply cut the data into the specified number
    # of equally spaced bins.
    if(xClassify == True):
        temp = mapclassify.classify(series, scheme=scheme, k=bins)
        counts = pd.Series(temp.counts)
        seriesRange = series.max() - series.min()
        binsList = [series.min()-seriesRange*.001]+ list(temp.bins)
        binsList[-1] = binsList[-1]+seriesRange*.001
    else:
        (temp, binsList) = pd.cut(series, bins=bins, retbins=True)
        binsList=list(binsList)
        counts = temp.value_counts()

    # If logy is set to auto, determine the ratio of the counts in the most frequent bin to
    # the counts in the least frequent bin (excluding zero) and compare this to the specified 
    # threshold to determine use a log scale on the y-axis.  If yes, set logy to True. If no, set 
    # logy to False.
    if(logy == "auto"):
        countMin = counts.loc[counts > 0].min()
        countMax = counts.max()
        yRatio = countMax/countMin
        logy = (True if (yRatio > yRatioThreshold) else False)

    # Generate the histogram
    ax = series.hist(bins=binsList, log=logy, figsize=figsize, edgecolor="black")
    
    countsList = list(counts)
    
    if(retBinsCounts == True):
        return (ax, binsList, countsList)
    else:
        return ax

def save_notebook():
    """
    Programmatically save the calling Jupyter notebook to disk. Works in JupyterLab only.
    
    Parameters
    ----------
    (None)
        
    Returns
    -------
    (None)
        
    """

    from ipylab import JupyterFrontEnd
    print("morpc.save_notebook | INFO | Saving notebook to disk")
    app = JupyterFrontEnd()
    app.commands.execute('docmanager:save')

    
def notebook_to_html(path=None, saveFirst=True):
    """
    Programmatically convert a Jupyter notebook to HTML format via nbconvert. Saves the HTML 
    file in the same directory as the Jupyter notebook. By default, the calling notebook will 
    be converted and it will be saved to disk prior to initiating the conversion.
    
    Parameters
    ----------
    path : string
        Optional. Filesystem path of Jupyter notebook to be converted. If unspecified, the path 
        of the calling notebook will be used.
    saveFirst : bool
        Optional. If True or unspecified, save the calling notebook to disk before initiating
        the conversion. If False, convert the version of the notebook already on disk.

    Returns
    -------
    htmlPath : string
        Filesystem path of the HTML export of the Jupyter notebook
        
    """
    import re
    import os
    import json
    import ipykernel
    
    if(path is None):
        print("morpc.notebook_to_html | INFO | Notebook path was not specified. Using path of calling notebook.")
        connectionInfo = json.loads(ipykernel.get_connection_info())
        path = os.path.normpath(connectionInfo["jupyter_session"])  
        
    if(saveFirst is True):
        save_notebook()

    htmlPath = re.sub(".ipynb$", ".html", path)
    print("morpc.notebook_to_html | INFO | Converting notebook to HTML...")
    print("morpc.notebook_to_html | INFO | --> Source: {}".format(path))
    print("morpc.notebook_to_html | INFO | --> Target: {}".format(htmlPath))    
    # For some reason nbconvert doesn't always like absolute paths so we'll change to the directory of the notebook so we can 
    # give only its filename to nbconvert, then we'll change back.
    cwd = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(path)))
    os.system("jupyter nbconvert --to html {}".format(os.path.basename(path)))
    os.chdir(cwd)
 
    return htmlPath
    
class generations():
    """
    Class-based tools for working with population generations.

    The names and starting years come from the following report from the Census Bureau:
    
    https://www2.census.gov/library/publications/2025/demo/acs-60.pdf
    
    However, the Census Bureau does not define generations.  The linked report includes the following footnote: "The U.S. 
    Census Bureau does not have official definitions for these birth cohorts. The birth year ranges for each birth cohort 
    may vary slightly across Census Bureau products. The use of these categories does not imply that this is the preferred 
    method of presenting or analyzing data."  Instead, the report cites the following Pew Research report as the source of 
    the generation definitions that were used:
    
    https://www.pewresearch.org/short-reads/2019/01/17/where-millennials-end-and-generation-z-begins/    

    Initialization
    --------------
    No parameters are required for initialization.

    Attributes
    ----------
    attribute_list : list
        List of dicts, each of which represents a generation. The generations are listed from oldest to newest. The dicts include the 
        name of the generation as well as the start year, end year, and number of years spanned.
    attributes : dict
        Identical content to self.attribute_list but in dictionary form indexed by generation name.
    name_list : list
        List of generation names (strings) ordered from oldest to newest
    startyear_list : list
        List of starting years of generations (integers) ordered from oldest to newest
    endyear_list : list
        List of ending years of generations (integers) ordered from oldest to newest.  The end year for the most recent generation may be 
        None (NoneType) if there is not consensus on the ending year.  Commonly the end year for a generation is not specified until the start
        year for a new generation is defined.
    stats: dict
        Contains statistics summarizing the spans of the set of generations.
        
    Methods
    --------
    ages_in_year
        For a user specified year or list of years, provides a dictionary containing the ages that are assigned to each generation for each
        requested year. Infers an end year for generations where the end year is unspecified.
    
    """

    def __init__(self):
        attribute_list = [
            { "name": "Lost Generation", "start_year":1883, "end_year":1900 },
            { "name": "Greatest Generation", "start_year":1901, "end_year":1927 },
            { "name": "Silent Generation", "start_year":1928, "end_year":1945 },
            { "name": "Baby Boomers", "start_year":1946, "end_year":1964 },
            { "name": "Generation X", "start_year":1965, "end_year":1980 },
            { "name": "Millenials", "start_year":1981, "end_year":1996 },
            { "name": "Generation Z", "start_year":1997, "end_year":2012 },
            { "name": "Generation Alpha", "start_year":2013, "end_year":None }
        ]

        for i in range(0, len(attribute_list)):
            attribute_list[i]["span"] = (None if attribute_list[i]["end_year"] is None else (attribute_list[i]["end_year"] - attribute_list[i]["start_year"]))
        
        name_list = [x["name"] for x in attribute_list]
        
        startyear_list =  [x["start_year"] for x in attribute_list]

        endyear_list =  [x["end_year"] for x in attribute_list]
        
        attributes = {}
        for generation in attribute_list:
            attributes[generation["name"]] = {attribute:value for attribute,value in generation.items() if attribute != "name"}

        stats = {
            "min_span": min([generation["span"] for generation in attribute_list if generation["span"] is not None]),
            "max_span": max([generation["span"] for generation in attribute_list if generation["span"] is not None]),
            "mean_span": round(sum([generation["span"] for generation in attribute_list if generation["span"] is not None])/(len(attribute_list)-1))
        }
        
        self.attribute_list = attribute_list
        self.attributes = attributes
        self.name_list = name_list
        self.startyear_list = startyear_list
        self.endyear_list = endyear_list
        self.stats = stats

    def ages_in_year(self, years, generations=None):
        """
        Identify which ages of persons belong to each generation in a user specified year or list of years.  For example, given the
        year 2020, for each generation list the possible ages of the people who belong to that generation in that year.

        Parameters
        ----------
        years : int or list
            An integer year (four digits) or list of integer years for which the age listings should be provided.
        generations : str or list
            Optional. The name of a single generation or a list of the names of generations for which the age listings should be provided.
            If this parameter is not specified, age listings will be provided for all available generations.

        Returns
        -------
        dict
            A two-level dictionary. First level is indexed by generation name. Second level is indexed by year. Each value is a list of
            possible ages of persons belong to that generation in that year.  For generations where the end year is undefined, a likely 
            end year is inferred based on the mean span of all known generations.  Note that the ages are unconstrained and may contain
            unrealistic or impossible values for older generations.  It is up to the user to constrain the set of ages in whatever way
            is appropriate for their application.
        """
        warningFlag = False
        if(generations == None):
            generations = self.name_list
        if(type(generations) == str):
            generations = [generations]
        if(type(years) == int):
              years = [years]
        agesInYear = {}
        for generation in generations:
            agesInYear[generation] = {}
            for year in years:
                oldest_age = year - self.attributes[generation]["start_year"]                
                if(self.attributes[generation]["end_year"] == None):
                    if(warningFlag == False):
                        print("WARNING | End year is not defined for generation {}. Using mean span of all generations ({})".format(generation, self.stats["mean_span"]))
                        warningFlag = True
                    youngest_age = year - (self.attributes[generation]["start_year"] + self.stats["mean_span"])
                else:
                    youngest_age = year - self.attributes[generation]["end_year"]
                youngest_age = max(youngest_age, 0)
                agesInYear[generation][year] = list(range(youngest_age, oldest_age+1))
                
        return agesInYear
        
def updateExistingTable(newData, schema, existingData=None, sortColumns=None, overwrite=False):
    """
    This function takes a data table in a well-defined form (as captured in a Frictionless schema) and attempts to update
    an existing table in the same form if it exists or otherwise outputs the new data as-is.  If records with identical primary
    key values exist in both tables, the existing data will be overwritten by the new data for those records (unless overwrite is
    set to False).  Records in the new data which are not already present in the existing data will be appended.  The resulting
    dataframe will be transformed to be compliant with the provided schema and, optionally, will be sorted by a user-specified
    set of columns.
    
    Parameters
    ----------
    newData : pandas.dataframe.DataFrame
        A Pandas DataFrame containing the new data to update the existing table if it exists
    schema : frictionless.schema.schema.Schema
        A Frictionless schema object that applies to both newData and existingData. Often created using morpc.frictionless.load_schema().
    existingData : pandas.dataframe.DataFrame
        If provided, a Pandas DataFrame containing existing data to which the updated data in newData will be applied. It may be the case
        that no data exists yet (the first time a script is run, for example).  In that case, simply omit existingData or set it explicitly
        to None and the function will return newData in a form that is compliant with the schema and (optionally) sorted.
    sortColumns : str or list
        Optional. A specification of the columns to use to sort the updated table.  If set to None, no sorting will occur.  If set to 
        "primary_key", the columns identified in schema.primary_key will be used.  Otherwise, provide a list of strings representing the 
        names of columns to be used.
    overwrite : bool
        Optional. If True, records that already exist in existingData will be overwritten by equivalent records in newData (as identified 
        by identical primary key values in both dataframes).  If False, an error will be raised if this case occurs.
        
    Returns
    -------
    outputData : pandas.dataframe.DataFrame
        A dataframe that consists of the merged contents of existingData (if provided) and newData.
    """

    import morpc
    import pandas as pd
    import logging

    logger  = logging.getLogger(__name__)    

    myNewData = newData.copy()
    # Verify that the primary key exists in the new data and that the index is in a known state
    if(set(schema.primary_key).issubset(set(myNewData.columns))):
        pass
    elif(myNewData.index.names == schema.primary_key):
        myNewData = myNewData.reset_index()
    else:
        logger.error("New data does not seem to contain the primary key, either as columns or as an index.")
        raise RuntimeError

    logger.info("Extracting required fields in new data and reordering them as specified in the schema.")
    myNewData = myNewData.filter(items=schema.field_names, axis="columns")

    logger.info("Casting new data to data types specified in schema.")
    myNewData = morpc.frictionless.cast_field_types(myNewData, schema)
    
    if(existingData is None):
        myExistingData = None
    else:
        myExistingData = existingData.copy()   
        # Verify that the primary key exists in the existing data and that the index is in a known state
        if(set(schema.primary_key).issubset(set(myExistingData.columns))):
            pass
        elif(myExistingData.index.names == schema.primary_key):
            myExistingData = myExistingData.reset_index()
        else:
            logger.error("Existing data does not seem to contain the primary key, either as columns or as an index.")
            raise RuntimeError

        logger.info("Confirming existing data includes only the required fields and that they are in the order specified in the schema.")
        myNewData = myNewData.filter(items=schema.field_names, axis="columns")
        
        logger.info("Confirming existing data is cast as data types specified in schema.")
        myExistingData = morpc.frictionless.cast_field_types(myExistingData, schema)

        
    if(myExistingData is None):
        logger.info("No existing data was found. Creating output data from scratch.")
        outputData = myNewData.copy()
    else:
        logger.info("Existing output data was found. Merging new data with existing data.")

        outputData = myExistingData.copy()

        logger.info("Setting new data index to primary key specified in schema.")
        myNewData = myNewData.set_index(schema.primary_key)
        
        logger.info("Setting existing data index to primary key specified in schema.")
        outputData = outputData.set_index(schema.primary_key)   

        logger.info("Analyzing differences between new and existing data.")
        recordsToUpdate = myNewData.index.intersection(outputData.index)
        logger.info(f"--> Found {len(recordsToUpdate)} records which are present in existing data and will be updated.")   
        recordsToAppend = myNewData.index.difference(outputData.index)
        logger.info(f"--> Found {len(recordsToAppend)} records which are not present in existing data and will be appended.")   
        
        # Update entries that were already present in output table
        if(not myNewData.loc[recordsToUpdate].empty):
            try:
                outputData.update(myNewData.loc[recordsToUpdate], overwrite=True, errors=("ignore" if overwrite == True else "raise"))
            except Exception as e:
                logger.error(f"Failed to update existing data with new data: {e}")
                logger.info("To force update when data overlaps, set overwrite parameter to True.") 
                raise
        
        # Append new entries that were not present in output table
        if(not myNewData.loc[recordsToAppend].empty):
            outputData = pd.concat([outputData, myNewData.loc[recordsToAppend]], axis="index")
        
        logger.info("Resetting indices of all datasets.") 
        myNewData = myNewData.reset_index()
        outputData = outputData.reset_index()

    logger.info("Casting merged data to data types specified in schema.")
    outputData = morpc.frictionless.cast_field_types(outputData, schema)

    if(sortColumns == "primary_key"):
        mySortColumns = schema.primary_key
        logger.info(f"Sorting merged data by columns specified in primary key: {mySortColumns}")
    elif(sortColumns is None):
        logger.info(f"Column sort order is unspecified. Not sorting columns.")
    elif(type(sortColumns) == "list"):
        mySortColumns = sortColumns
        logger.info(f'Sorting merged data by user-specified columns: {",".join(mySortColumns)}')
    else:
        logger.error('User-specified value for sortColumns parameter is not supported.')
        raise RuntimeError
        
    if(sortColumns is not None):
        outputData = outputData.sort_values(mySortColumns) 
    
    return outputData
    
## The following content supports interaction with BLS data.  It is being staged here with the intent that it
## will ultimately be migrated to it's own module (morpc.bls)

class bls():
    def __init__(self):
        
        # Aggregation level code map (see https://www.bls.gov/cew/classifications/aggregation/agg-level-titles.htm)
        AGGLEVEL_CODES = {
            "10": "National, Total Covered",
            "11": "National, Total -- by ownership sector",
            "12": "National, by Domain -- by ownership sector",
            "13": "National, by Supersector -- by ownership sector",
            "14": "National, NAICS Sector -- by ownership sector",
            "15": "National, NAICS 3-digit -- by ownership sector",
            "16": "National, NAICS 4-digit -- by ownership sector",
            "17": "National, NAICS 5-digit -- by ownership sector",
            "18": "National, NAICS 6-digit -- by ownership sector",
            "21": "National, Private, total, by establishment size class",
            "22": "National, Private, Domain, by establishment size class",
            "23": "National, Private, by Supersector, by establishment size class",
            "24": "National, Private, NAICS Sector, by establishment size class",
            "25": "National, Private, NAICS 3-digit, by establishment size class",
            "26": "National, Private, NAICS 4-digit, by establishment size class",
            "27": "National, Private, NAICS 5-digit, by establishment size class",
            "28": "National, Private, NAICS 6-digit, by establishment size class",
            "30": "CMSA or CSA, Total Covered",
            "40": "MSA, Total Covered",
            "41": "MSA, Total -- by ownership sector",
            "42": "MSA, by Domain -- by ownership sector",
            "43": "MSA, by Supersector -- by ownership sector",
            "44": "MSA, NAICS Sector -- by ownership sector",
            "45": "MSA, NAICS 3-digit -- by ownership sector",
            "46": "MSA, NAICS 4-digit -- by ownership sector",
            "47": "MSA, NAICS 5-digit -- by ownership sector",
            "48": "MSA, NAICS 6-digit -- by ownership sector",
            "50": "State, Total Covered",
            "51": "State, Total -- by ownership sector",
            "52": "State, by Domain -- by ownership sector",
            "53": "State, by Supersector -- by ownership sector",
            "54": "State, NAICS Sector -- by ownership sector",
            "55": "State, NAICS 3-digit -- by ownership sector",
            "56": "State, NAICS 4-digit -- by ownership sector",
            "57": "State, NAICS 5-digit -- by ownership sector",
            "58": "State, NAICS 6-digit -- by ownership sector",
            "61": "State, Private, total, by establishment size class",
            "62": "State, Private, Domain, by establishment size class",
            "63": "State, Private, by Supersector, by establishment size class",
            "64": "State, Private, NAICS Sector, by establishment size class",
            "70": "County, Total Covered",
            "71": "County, Total -- by ownership sector",
            "72": "County, by Domain -- by ownership sector",
            "73": "County, by Supersector -- by ownership sector",
            "74": "County, NAICS Sector -- by ownership sector",
            "75": "County, NAICS 3-digit -- by ownership sector",
            "76": "County, NAICS 4-digit -- by ownership sector",
            "77": "County, NAICS 5-digit -- by ownership sector",
            "78": "County, NAICS 6-digit -- by ownership sector",
            "80": "MicroSA, Total Covered",
            "91": "Total, all U.S. MSAs",
            "92": "Total, all U.S. CMSAs or all U.S. CSAs",
            "93": "Total, all U.S. non-MSA counties",
            "94": "Total U.I. Covered (U.S.)",
            "95": "Total Government (U.S.)",
            "96": "Total Government, by State"
        }

        # Industry code map (see https://www.bls.gov/cew/classifications/industry/industry-titles.csv)
        INDUSTRY_CODES = {
            "10": "10 Total, all industries",
            "101": "101 Goods-producing",
            "1011": "1011 Natural resources and mining",
            "1012": "1012 Construction",
            "1013": "1013 Manufacturing",
            "102": "102 Service-providing",
            "1021": "1021 Trade, transportation, and utilities",
            "1022": "1022 Information",
            "1023": "1023 Financial activities",
            "1024": "1024 Professional and business services",
            "1025": "1025 Education and health services",
            "1026": "1026 Leisure and hospitality",
            "1027": "1027 Other services",
            "1028": "1028 Public administration",
            "1029": "1029 Unclassified",
            "11": "NAICS 11 Agriculture, forestry, fishing and hunting",
            "111": "NAICS 111 Crop production",
            "1111": "NAICS 1111 Oilseed and grain farming",
            "11111": "NAICS 11111 Soybean farming",
            "111110": "NAICS 111110 Soybean farming",
            "11112": "NAICS 11112 Oilseed (except soybean) farming",
            "111120": "NAICS 111120 Oilseed (except soybean) farming",
            "11113": "NAICS 11113 Dry pea and bean farming",
            "111130": "NAICS 111130 Dry pea and bean farming",
            "11114": "NAICS 11114 Wheat farming",
            "111140": "NAICS 111140 Wheat farming",
            "11115": "NAICS 11115 Corn farming",
            "111150": "NAICS 111150 Corn farming",
            "11116": "NAICS 11116 Rice farming",
            "111160": "NAICS 111160 Rice farming",
            "11119": "NAICS 11119 Other grain farming",
            "111191": "NAICS 111191 Oilseed and grain combination farming",
            "111199": "NAICS 111199 All other grain farming",
            "1112": "NAICS 1112 Vegetable and melon farming",
            "11121": "NAICS 11121 Vegetable and melon farming",
            "111211": "NAICS 111211 Potato farming",
            "111219": "NAICS 111219 Other vegetable (except potato) and melon farming",
            "1113": "NAICS 1113 Fruit and tree nut farming",
            "11131": "NAICS 11131 Orange groves",
            "111310": "NAICS 111310 Orange groves",
            "11132": "NAICS 11132 Citrus (except orange) groves",
            "111320": "NAICS 111320 Citrus (except orange) groves",
            "11133": "NAICS 11133 Noncitrus fruit and tree nut farming",
            "111331": "NAICS 111331 Apple orchards",
            "111332": "NAICS 111332 Grape vineyards",
            "111333": "NAICS 111333 Strawberry farming",
            "111334": "NAICS 111334 Berry (except strawberry) farming",
            "111335": "NAICS 111335 Tree nut farming",
            "111336": "NAICS 111336 Fruit and tree nut combination farming",
            "111339": "NAICS 111339 Other noncitrus fruit farming",
            "1114": "NAICS 1114 Greenhouse, nursery, and floriculture production",
            "11141": "NAICS 11141 Food crops grown under cover",
            "111411": "NAICS 111411 Mushroom production",
            "111419": "NAICS 111419 Other food crops grown under cover",
            "11142": "NAICS 11142 Nursery and floriculture production",
            "111421": "NAICS 111421 Nursery and tree production",
            "111422": "NAICS 111422 Floriculture production",
            "1119": "NAICS 1119 Other crop farming",
            "11191": "NAICS 11191 Tobacco farming",
            "111910": "NAICS 111910 Tobacco farming",
            "11192": "NAICS 11192 Cotton farming",
            "111920": "NAICS 111920 Cotton farming",
            "11193": "NAICS 11193 Sugarcane farming",
            "111930": "NAICS 111930 Sugarcane farming",
            "11194": "NAICS 11194 Hay farming",
            "111940": "NAICS 111940 Hay farming",
            "11199": "NAICS 11199 All other crop farming",
            "111991": "NAICS 111991 Sugar beet farming",
            "111992": "NAICS 111992 Peanut farming",
            "111998": "NAICS 111998 All other miscellaneous crop farming",
            "112": "NAICS 112 Animal production and aquaculture",
            "1121": "NAICS 1121 Cattle ranching and farming",
            "11211": "NAICS 11211 Beef cattle ranching and farming, including feedlots",
            "112111": "NAICS 112111 Beef cattle ranching and farming",
            "112112": "NAICS 112112 Cattle feedlots",
            "11212": "NAICS 11212 Dairy cattle and milk production",
            "112120": "NAICS 112120 Dairy cattle and milk production",
            "1122": "NAICS 1122 Hog and pig farming",
            "11221": "NAICS 11221 Hog and pig farming",
            "112210": "NAICS 112210 Hog and pig farming",
            "1123": "NAICS 1123 Poultry and egg production",
            "11231": "NAICS 11231 Chicken egg production",
            "112310": "NAICS 112310 Chicken egg production",
            "11232": "NAICS 11232 Broilers and other meat type chicken production",
            "112320": "NAICS 112320 Broilers and other meat type chicken production",
            "11233": "NAICS 11233 Turkey production",
            "112330": "NAICS 112330 Turkey production",
            "11234": "NAICS 11234 Poultry hatcheries",
            "112340": "NAICS 112340 Poultry hatcheries",
            "11239": "NAICS 11239 Other poultry production",
            "112390": "NAICS 112390 Other poultry production",
            "1124": "NAICS 1124 Sheep and goat farming",
            "11241": "NAICS 11241 Sheep farming",
            "112410": "NAICS 112410 Sheep farming",
            "11242": "NAICS 11242 Goat farming",
            "112420": "NAICS 112420 Goat farming",
            "1125": "NAICS 1125 Aquaculture",
            "11251": "NAICS 11251 Aquaculture",
            "112511": "NAICS 112511 Finfish farming and fish hatcheries",
            "112512": "NAICS 112512 Shellfish farming",
            "112519": "NAICS 112519 Other aquaculture",
            "1129": "NAICS 1129 Other animal production",
            "11291": "NAICS 11291 Apiculture",
            "112910": "NAICS 112910 Apiculture",
            "11292": "NAICS 11292 Horses and other equine production",
            "112920": "NAICS 112920 Horses and other equine production",
            "11293": "NAICS 11293 Fur-bearing animal and rabbit production",
            "112930": "NAICS 112930 Fur-bearing animal and rabbit production",
            "11299": "NAICS 11299 All other animal production",
            "112990": "NAICS 112990 All other animal production",
            "113": "NAICS 113 Forestry and logging",
            "1131": "NAICS 1131 Timber tract operations",
            "11311": "NAICS 11311 Timber tract operations",
            "113110": "NAICS 113110 Timber tract operations",
            "1132": "NAICS 1132 Forest nurseries and gathering of forest products",
            "11321": "NAICS 11321 Forest nurseries and gathering of forest products",
            "113210": "NAICS 113210 Forest nurseries and gathering of forest products",
            "1133": "NAICS 1133 Logging",
            "11331": "NAICS 11331 Logging",
            "113310": "NAICS 113310 Logging",
            "114": "NAICS 114 Fishing, hunting and trapping",
            "1141": "NAICS 1141 Fishing",
            "11411": "NAICS 11411 Fishing",
            "114111": "NAICS 114111 Finfish fishing",
            "114112": "NAICS 114112 Shellfish fishing",
            "114119": "NAICS 114119 Other marine fishing",
            "1142": "NAICS 1142 Hunting and trapping",
            "11421": "NAICS 11421 Hunting and trapping",
            "114210": "NAICS 114210 Hunting and trapping",
            "115": "NAICS 115 Support activities for agriculture and forestry",
            "1151": "NAICS 1151 Support activities for crop production",
            "11511": "NAICS 11511 Support activities for crop production",
            "115111": "NAICS 115111 Cotton ginning",
            "115112": "NAICS 115112 Soil preparation, planting, and cultivating",
            "115113": "NAICS 115113 Crop harvesting, primarily by machine",
            "115114": "NAICS 115114 Postharvest crop activities (except cotton ginning)",
            "115115": "NAICS 115115 Farm labor contractors and crew leaders",
            "115116": "NAICS 115116 Farm management services",
            "1152": "NAICS 1152 Support activities for animal production",
            "11521": "NAICS 11521 Support activities for animal production",
            "115210": "NAICS 115210 Support activities for animal production",
            "1153": "NAICS 1153 Support activities for forestry",
            "11531": "NAICS 11531 Support activities for forestry",
            "115310": "NAICS 115310 Support activities for forestry",
            "21": "NAICS 21 Mining, quarrying, and oil and gas extraction",
            "211": "NAICS 211 Oil and gas extraction",
            "2111": "NAICS 2111 Oil and gas extraction",
            "21111": "NAICS12 21111 Oil and gas extraction",
            "211111": "NAICS12 211111 Crude petroleum and natural gas extraction",
            "211112": "NAICS12 211112 Natural gas liquid extraction",
            "21112": "NAICS 21112 Crude petroleum extraction",
            "211120": "NAICS 211120 Crude petroleum extraction",
            "21113": "NAICS 21113 Natural gas extraction",
            "211130": "NAICS 211130 Natural gas extraction",
            "212": "NAICS 212 Mining (except oil and gas)",
            "2121": "NAICS 2121 Coal mining",
            "21211": "NAICS 21211 Coal mining",
            "212111": "NAICS17 212111 Bituminous coal and lignite surface mining",
            "212112": "NAICS17 212112 Bituminous coal underground mining",
            "212113": "NAICS17 212113 Anthracite mining",
            "212114": "NAICS 212114 Surface coal mining",
            "212115": "NAICS 212115 Underground coal mining",
            "2122": "NAICS 2122 Metal ore mining",
            "21221": "NAICS 21221 Iron ore mining",
            "212210": "NAICS 212210 Iron ore mining",
            "21222": "NAICS 21222 Gold ore and silver ore mining",
            "212220": "NAICS 212220 Gold ore and silver ore mining",
            "212221": "NAICS17 212221 Gold ore mining",
            "212222": "NAICS17 212222 Silver ore mining",
            "21223": "NAICS 21223 Copper, nickel, lead, and zinc mining",
            "212230": "NAICS 212230 Copper, nickel, lead, and zinc mining",
            "212231": "NAICS12 212231 Lead ore and zinc ore mining",
            "212234": "NAICS12 212234 Copper ore and nickel ore mining",
            "21229": "NAICS 21229 Other metal ore mining",
            "212290": "NAICS 212290 Other metal ore mining",
            "212291": "NAICS17 212291 Uranium-radium-vanadium ore mining",
            "212299": "NAICS17 212299 All other metal ore mining",
            "2123": "NAICS 2123 Nonmetallic mineral mining and quarrying",
            "21231": "NAICS 21231 Stone mining and quarrying",
            "212311": "NAICS 212311 Dimension stone mining and quarrying",
            "212312": "NAICS 212312 Crushed and broken limestone mining and quarrying",
            "212313": "NAICS 212313 Crushed and broken granite mining and quarrying",
            "212319": "NAICS 212319 Other crushed and broken stone mining and quarrying",
            "21232": "NAICS 21232 Sand, gravel, clay, and ceramic and refractory minerals mining and quarrying",
            "212321": "NAICS 212321 Construction sand and gravel mining",
            "212322": "NAICS 212322 Industrial sand mining",
            "212323": "NAICS 212323 Kaolin, clay, and ceramic and refractory minerals mining",
            "212324": "NAICS17 212324 Kaolin and ball clay mining",
            "212325": "NAICS17 212325 Clay, ceramic, and refractory minerals mining",
            "21239": "NAICS 21239 Other nonmetallic mineral mining and quarrying",
            "212390": "NAICS 212390 Other nonmetallic mineral mining and quarrying",
            "212391": "NAICS17 212391 Potash, soda, and borate mineral mining",
            "212392": "NAICS17 212392 Phosphate rock mining",
            "212393": "NAICS17 212393 Other chemical and fertilizer mineral mining",
            "212399": "NAICS17 212399 All other nonmetallic mineral mining",
            "213": "NAICS 213 Support activities for mining",
            "2131": "NAICS 2131 Support activities for mining",
            "21311": "NAICS 21311 Support activities for mining",
            "213111": "NAICS 213111 Drilling oil and gas wells",
            "213112": "NAICS 213112 Support activities for oil and gas operations",
            "213113": "NAICS 213113 Support activities for coal mining",
            "213114": "NAICS 213114 Support activities for metal mining",
            "213115": "NAICS 213115 Support activities for nonmetallic minerals (except fuels) mining",
            "22": "NAICS 22 Utilities",
            "221": "NAICS 221 Utilities",
            "2211": "NAICS 2211 Electric power generation, transmission and distribution",
            "22111": "NAICS 22111 Electric power generation",
            "221111": "NAICS 221111 Hydroelectric power generation",
            "221112": "NAICS 221112 Fossil fuel electric power generation",
            "221113": "NAICS 221113 Nuclear electric power generation",
            "221114": "NAICS 221114 Solar electric power generation",
            "221115": "NAICS 221115 Wind electric power generation",
            "221116": "NAICS 221116 Geothermal electric power generation",
            "221117": "NAICS 221117 Biomass electric power generation",
            "221118": "NAICS 221118 Other electric power generation",
            "221119": "NAICS07 221119 Other electric power generation",
            "22112": "NAICS 22112 Electric power transmission, control, and distribution",
            "221121": "NAICS 221121 Electric bulk power transmission and control",
            "221122": "NAICS 221122 Electric power distribution",
            "2212": "NAICS 2212 Natural gas distribution",
            "22121": "NAICS 22121 Natural gas distribution",
            "221210": "NAICS 221210 Natural gas distribution",
            "2213": "NAICS 2213 Water, sewage and other systems",
            "22131": "NAICS 22131 Water supply and irrigation systems",
            "221310": "NAICS 221310 Water supply and irrigation systems",
            "22132": "NAICS 22132 Sewage treatment facilities",
            "221320": "NAICS 221320 Sewage treatment facilities",
            "22133": "NAICS 22133 Steam and air-conditioning supply",
            "221330": "NAICS 221330 Steam and air-conditioning supply",
            "23": "NAICS 23 Construction",
            "236": "NAICS 236 Construction of buildings",
            "2361": "NAICS 2361 Residential building construction",
            "23611": "NAICS 23611 Residential building construction",
            "236115": "NAICS 236115 New single-family housing construction (except for-sale builders)",
            "236116": "NAICS 236116 New multifamily housing construction (except for-sale builders)",
            "236117": "NAICS 236117 New housing for-sale builders",
            "236118": "NAICS 236118 Residential remodelers",
            "2362": "NAICS 2362 Nonresidential building construction",
            "23621": "NAICS 23621 Industrial building construction",
            "236210": "NAICS 236210 Industrial building construction",
            "23622": "NAICS 23622 Commercial and institutional building construction",
            "236220": "NAICS 236220 Commercial and institutional building construction",
            "237": "NAICS 237 Heavy and civil engineering construction",
            "2371": "NAICS 2371 Utility system construction",
            "23711": "NAICS 23711 Water and sewer line and related structures construction",
            "237110": "NAICS 237110 Water and sewer line and related structures construction",
            "23712": "NAICS 23712 Oil and gas pipeline and related structures construction",
            "237120": "NAICS 237120 Oil and gas pipeline and related structures construction",
            "23713": "NAICS 23713 Power and communication line and related structures construction",
            "237130": "NAICS 237130 Power and communication line and related structures construction",
            "2372": "NAICS 2372 Land subdivision",
            "23721": "NAICS 23721 Land subdivision",
            "237210": "NAICS 237210 Land subdivision",
            "2373": "NAICS 2373 Highway, street, and bridge construction",
            "23731": "NAICS 23731 Highway, street, and bridge construction",
            "237310": "NAICS 237310 Highway, street, and bridge construction",
            "2379": "NAICS 2379 Other heavy and civil engineering construction",
            "23799": "NAICS 23799 Other heavy and civil engineering construction",
            "237990": "NAICS 237990 Other heavy and civil engineering construction",
            "238": "NAICS 238 Specialty trade contractors",
            "2381": "NAICS 2381 Building foundation and exterior contractors",
            "23811": "NAICS 23811 Poured concrete structure contractors",
            "238111": "NAICS 238111 Residential poured foundation contractors",
            "238112": "NAICS 238112 Nonresidential poured foundation contractors",
            "23812": "NAICS 23812 Steel and precast concrete contractors",
            "238121": "NAICS 238121 Residential structural steel contractors",
            "238122": "NAICS 238122 Nonresidential structural steel contractors",
            "23813": "NAICS 23813 Framing contractors",
            "238131": "NAICS 238131 Residential framing contractors",
            "238132": "NAICS 238132 Nonresidential framing contractors",
            "23814": "NAICS 23814 Masonry contractors",
            "238141": "NAICS 238141 Residential masonry contractors",
            "238142": "NAICS 238142 Nonresidential masonry contractors",
            "23815": "NAICS 23815 Glass and glazing contractors",
            "238151": "NAICS 238151 Residential glass and glazing contractors",
            "238152": "NAICS 238152 Nonresidential glass and glazing contractors",
            "23816": "NAICS 23816 Roofing contractors",
            "238161": "NAICS 238161 Residential roofing contractors",
            "238162": "NAICS 238162 Nonresidential roofing contractors",
            "23817": "NAICS 23817 Siding contractors",
            "238171": "NAICS 238171 Residential siding contractors",
            "238172": "NAICS 238172 Nonresidential siding contractors",
            "23819": "NAICS 23819 Other building exterior contractors",
            "238191": "NAICS 238191 Other residential exterior contractors",
            "238192": "NAICS 238192 Other nonresidential exterior contractors",
            "2382": "NAICS 2382 Building equipment contractors",
            "23821": "NAICS 23821 Electrical and wiring contractors",
            "238211": "NAICS 238211 Residential electrical contractors",
            "238212": "NAICS 238212 Nonresidential electrical contractors",
            "23822": "NAICS 23822 Plumbing and hvac contractors",
            "238221": "NAICS 238221 Residential plumbing and hvac contractors",
            "238222": "NAICS 238222 Nonresidential plumbing and hvac contractors",
            "23829": "NAICS 23829 Other building equipment contractors",
            "238291": "NAICS 238291 Other residential equipment contractors",
            "238292": "NAICS 238292 Other nonresidential equipment contractors",
            "2383": "NAICS 2383 Building finishing contractors",
            "23831": "NAICS 23831 Drywall and insulation contractors",
            "238311": "NAICS 238311 Residential drywall contractors",
            "238312": "NAICS 238312 Nonresidential drywall contractors",
            "23832": "NAICS 23832 Painting and wall covering contractors",
            "238321": "NAICS 238321 Residential painting contractors",
            "238322": "NAICS 238322 Nonresidential painting contractors",
            "23833": "NAICS 23833 Flooring contractors",
            "238331": "NAICS 238331 Residential flooring contractors",
            "238332": "NAICS 238332 Nonresidential flooring contractors",
            "23834": "NAICS 23834 Tile and terrazzo contractors",
            "238341": "NAICS 238341 Residential tile and terrazzo contractors",
            "238342": "NAICS 238342 Nonresidential tile and terrazzo contractors",
            "23835": "NAICS 23835 Finish carpentry contractors",
            "238351": "NAICS 238351 Residential finish carpentry contractors",
            "238352": "NAICS 238352 Nonresidential finish carpentry contractors",
            "23839": "NAICS 23839 Other building finishing contractors",
            "238391": "NAICS 238391 Other residential finishing contractors",
            "238392": "NAICS 238392 Other nonresidential finishing contractors",
            "2389": "NAICS 2389 Other specialty trade contractors",
            "23891": "NAICS 23891 Site preparation contractors",
            "238911": "NAICS 238911 Residential site preparation contractors",
            "238912": "NAICS 238912 Nonresidential site preparation contractors",
            "23899": "NAICS 23899 All other specialty trade contractors",
            "238991": "NAICS 238991 All other residential trade contractors",
            "238992": "NAICS 238992 All other nonresidential trade contractors",
            "311": "NAICS 311 Food manufacturing",
            "3111": "NAICS 3111 Animal food manufacturing",
            "31111": "NAICS 31111 Animal food manufacturing",
            "311111": "NAICS 311111 Dog and cat food manufacturing",
            "311119": "NAICS 311119 Other animal food manufacturing",
            "3112": "NAICS 3112 Grain and oilseed milling",
            "31121": "NAICS 31121 Flour milling and malt manufacturing",
            "311211": "NAICS 311211 Flour milling",
            "311212": "NAICS 311212 Rice milling",
            "311213": "NAICS 311213 Malt manufacturing",
            "31122": "NAICS 31122 Starch and vegetable fats and oils manufacturing",
            "311221": "NAICS 311221 Wet corn milling and starch manufacturing",
            "311222": "NAICS07 311222 Soybean processing",
            "311223": "NAICS07 311223 Other oilseed processing",
            "311224": "NAICS 311224 Soybean and other oilseed processing",
            "311225": "NAICS 311225 Fats and oils refining and blending",
            "31123": "NAICS 31123 Breakfast cereal manufacturing",
            "311230": "NAICS 311230 Breakfast cereal manufacturing",
            "3113": "NAICS 3113 Sugar and confectionery product manufacturing",
            "31131": "NAICS 31131 Sugar manufacturing",
            "311311": "NAICS07 311311 Sugarcane mills",
            "311312": "NAICS07 311312 Cane sugar refining",
            "311313": "NAICS 311313 Beet sugar manufacturing",
            "311314": "NAICS 311314 Cane sugar manufacturing",
            "31132": "NAICS07 31132 Confectionery manufacturing from cacao beans",
            "311320": "NAICS07 311320 Confectionery manufacturing from cacao beans",
            "31133": "NAICS07 31133 Confectionery mfg. from purchased chocolate",
            "311330": "NAICS07 311330 Confectionery mfg. from purchased chocolate",
            "31134": "NAICS 31134 Nonchocolate confectionery manufacturing",
            "311340": "NAICS 311340 Nonchocolate confectionery manufacturing",
            "31135": "NAICS 31135 Chocolate and confectionery manufacturing",
            "311351": "NAICS 311351 Chocolate and confectionery manufacturing from cacao beans",
            "311352": "NAICS 311352 Confectionery manufacturing from purchased chocolate",
            "3114": "NAICS 3114 Fruit and vegetable preserving and specialty food manufacturing",
            "31141": "NAICS 31141 Frozen food manufacturing",
            "311411": "NAICS 311411 Frozen fruit, juice, and vegetable manufacturing",
            "311412": "NAICS 311412 Frozen specialty food manufacturing",
            "31142": "NAICS 31142 Fruit and vegetable canning, pickling, and drying",
            "311421": "NAICS 311421 Fruit and vegetable canning",
            "311422": "NAICS 311422 Specialty canning",
            "311423": "NAICS 311423 Dried and dehydrated food manufacturing",
            "3115": "NAICS 3115 Dairy product manufacturing",
            "31151": "NAICS 31151 Dairy product (except frozen) manufacturing",
            "311511": "NAICS 311511 Fluid milk manufacturing",
            "311512": "NAICS 311512 Creamery butter manufacturing",
            "311513": "NAICS 311513 Cheese manufacturing",
            "311514": "NAICS 311514 Dry, condensed, and evaporated dairy product manufacturing",
            "31152": "NAICS 31152 Ice cream and frozen dessert manufacturing",
            "311520": "NAICS 311520 Ice cream and frozen dessert manufacturing",
            "3116": "NAICS 3116 Animal slaughtering and processing",
            "31161": "NAICS 31161 Animal slaughtering and processing",
            "311611": "NAICS 311611 Animal (except poultry) slaughtering",
            "311612": "NAICS 311612 Meat processed from carcasses",
            "311613": "NAICS 311613 Rendering and meat byproduct processing",
            "311615": "NAICS 311615 Poultry processing",
            "3117": "NAICS 3117 Seafood product preparation and packaging",
            "31171": "NAICS 31171 Seafood product preparation and packaging",
            "311710": "NAICS 311710 Seafood product preparation and packaging",
            "311711": "NAICS07 311711 Seafood canning",
            "311712": "NAICS07 311712 Fresh and frozen seafood processing",
            "3118": "NAICS 3118 Bakeries and tortilla manufacturing",
            "31181": "NAICS 31181 Bread and bakery product manufacturing",
            "311811": "NAICS 311811 Retail bakeries",
            "311812": "NAICS 311812 Commercial bakeries",
            "311813": "NAICS 311813 Frozen cakes, pies, and other pastries manufacturing",
            "31182": "NAICS 31182 Cookie, cracker, and pasta manufacturing",
            "311821": "NAICS 311821 Cookie and cracker manufacturing",
            "311822": "NAICS07 311822 Mixes and dough made from purchased flour",
            "311823": "NAICS07 311823 Dry pasta manufacturing",
            "311824": "NAICS 311824 Dry pasta, dough, and flour mixes manufacturing from purchased flour",
            "31183": "NAICS 31183 Tortilla manufacturing",
            "311830": "NAICS 311830 Tortilla manufacturing",
            "3119": "NAICS 3119 Other food manufacturing",
            "31191": "NAICS 31191 Snack food manufacturing",
            "311911": "NAICS 311911 Roasted nuts and peanut butter manufacturing",
            "311919": "NAICS 311919 Other snack food manufacturing",
            "31192": "NAICS 31192 Coffee and tea manufacturing",
            "311920": "NAICS 311920 Coffee and tea manufacturing",
            "31193": "NAICS 31193 Flavoring syrup and concentrate manufacturing",
            "311930": "NAICS 311930 Flavoring syrup and concentrate manufacturing",
            "31194": "NAICS 31194 Seasoning and dressing manufacturing",
            "311941": "NAICS 311941 Mayonnaise, dressing, and other prepared sauce manufacturing",
            "311942": "NAICS 311942 Spice and extract manufacturing",
            "31199": "NAICS 31199 All other food manufacturing",
            "311991": "NAICS 311991 Perishable prepared food manufacturing",
            "311999": "NAICS 311999 All other miscellaneous food manufacturing",
            "312": "NAICS 312 Beverage and tobacco product manufacturing",
            "3121": "NAICS 3121 Beverage manufacturing",
            "31211": "NAICS 31211 Soft drink and ice manufacturing",
            "312111": "NAICS 312111 Soft drink manufacturing",
            "312112": "NAICS 312112 Bottled water manufacturing",
            "312113": "NAICS 312113 Ice manufacturing",
            "31212": "NAICS 31212 Breweries",
            "312120": "NAICS 312120 Breweries",
            "31213": "NAICS 31213 Wineries",
            "312130": "NAICS 312130 Wineries",
            "31214": "NAICS 31214 Distilleries",
            "312140": "NAICS 312140 Distilleries",
            "3122": "NAICS 3122 Tobacco manufacturing",
            "31221": "NAICS07 31221 Tobacco stemming and redrying",
            "312210": "NAICS07 312210 Tobacco stemming and redrying",
            "31222": "NAICS07 31222 Tobacco product manufacturing",
            "312221": "NAICS07 312221 Cigarette manufacturing",
            "312229": "NAICS07 312229 Other tobacco product manufacturing",
            "31223": "NAICS 31223 Tobacco manufacturing",
            "312230": "NAICS 312230 Tobacco manufacturing",
            "313": "NAICS 313 Textile mills",
            "3131": "NAICS 3131 Fiber, yarn, and thread mills",
            "31311": "NAICS 31311 Fiber, yarn, and thread mills",
            "313110": "NAICS 313110 Fiber, yarn, and thread mills",
            "313111": "NAICS07 313111 Yarn spinning mills",
            "313112": "NAICS07 313112 Yarn texturizing and twisting mills",
            "313113": "NAICS07 313113 Thread mills",
            "3132": "NAICS 3132 Fabric mills",
            "31321": "NAICS 31321 Broadwoven fabric mills",
            "313210": "NAICS 313210 Broadwoven fabric mills",
            "31322": "NAICS 31322 Narrow fabric mills and schiffli machine embroidery",
            "313220": "NAICS 313220 Narrow fabric mills and schiffli machine embroidery",
            "313221": "NAICS07 313221 Narrow fabric mills",
            "313222": "NAICS07 313222 Schiffli machine embroidery",
            "31323": "NAICS 31323 Nonwoven fabric mills",
            "313230": "NAICS 313230 Nonwoven fabric mills",
            "31324": "NAICS 31324 Knit fabric mills",
            "313240": "NAICS 313240 Knit fabric mills",
            "313241": "NAICS07 313241 Weft knit fabric mills",
            "313249": "NAICS07 313249 Other knit fabric and lace mills",
            "3133": "NAICS 3133 Textile and fabric finishing and fabric coating mills",
            "31-33": "NAICS 31-33 Manufacturing",
            "31331": "NAICS 31331 Textile and fabric finishing mills",
            "313310": "NAICS 313310 Textile and fabric finishing mills",
            "313311": "NAICS07 313311 Broadwoven fabric finishing mills",
            "313312": "NAICS07 313312 Other textile and fabric finishing mills",
            "31332": "NAICS 31332 Fabric coating mills",
            "313320": "NAICS 313320 Fabric coating mills",
            "314": "NAICS 314 Textile product mills",
            "3141": "NAICS 3141 Textile furnishings mills",
            "31411": "NAICS 31411 Carpet and rug mills",
            "314110": "NAICS 314110 Carpet and rug mills",
            "31412": "NAICS 31412 Curtain and linen mills",
            "314120": "NAICS 314120 Curtain and linen mills",
            "314121": "NAICS07 314121 Curtain and drapery mills",
            "314129": "NAICS07 314129 Other household textile product mills",
            "3149": "NAICS 3149 Other textile product mills",
            "31491": "NAICS 31491 Textile bag and canvas mills",
            "314910": "NAICS 314910 Textile bag and canvas mills",
            "314911": "NAICS07 314911 Textile bag mills",
            "314912": "NAICS07 314912 Canvas and related product mills",
            "31499": "NAICS 31499 All other textile product mills",
            "314991": "NAICS07 314991 Rope, cordage, and twine mills",
            "314992": "NAICS07 314992 Tire cord and tire fabric mills",
            "314994": "NAICS 314994 Rope, cordage, twine, tire cord, and tire fabric mills",
            "314999": "NAICS 314999 All other miscellaneous textile product mills",
            "315": "NAICS 315 Apparel manufacturing",
            "3151": "NAICS 3151 Apparel knitting mills",
            "31511": "NAICS17 31511 Hosiery and sock mills",
            "315110": "NAICS17 315110 Hosiery and sock mills",
            "315111": "NAICS07 315111 Sheer hosiery mills",
            "315119": "NAICS07 315119 Other hosiery and sock mills",
            "31512": "NAICS 31512 Apparel knitting mills",
            "315120": "NAICS 315120 Apparel knitting mills",
            "31519": "NAICS17 31519 Other apparel knitting mills",
            "315190": "NAICS17 315190 Other apparel knitting mills",
            "315191": "NAICS07 315191 Outerwear knitting mills",
            "315192": "NAICS07 315192 Underwear and nightwear knitting mills",
            "3152": "NAICS 3152 Cut and sew apparel manufacturing",
            "31521": "NAICS 31521 Cut and sew apparel contractors",
            "315210": "NAICS 315210 Cut and sew apparel contractors",
            "315211": "NAICS07 315211 Men's and boys' apparel contractors",
            "315212": "NAICS07 315212 Women's, girls', infants' apparel contractors",
            "31522": "NAICS17 31522 Men's and boys' cut and sew apparel mfg.",
            "315220": "NAICS17 315220 Men's and boys' cut and sew apparel mfg.",
            "315221": "NAICS07 315221 Men's and boys' underwear and nightwear mfg.",
            "315222": "NAICS07 315222 Men's and boys' suit, coat, and overcoat mfg.",
            "315223": "NAICS07 315223 Men's and boys' shirt, except work shirt, mfg.",
            "315224": "NAICS07 315224 Men's and boys' pants, except work pants, mfg.",
            "315225": "NAICS07 315225 Men's and boys' work clothing manufacturing",
            "315228": "NAICS07 315228 Other men's and boys' outerwear manufacturing",
            "31523": "NAICS07 31523 Women's and girls' cut and sew apparel mfg.",
            "315231": "NAICS07 315231 Women's and girls' lingerie and nightwear mfg.",
            "315232": "NAICS07 315232 Women's and girls' blouse and shirt mfg.",
            "315233": "NAICS07 315233 Women's and girls' dress manufacturing",
            "315234": "NAICS07 315234 Women's and girls' suit, coat, and skirt mfg.",
            "315239": "NAICS07 315239 Other women's and girls' outerwear mfg.",
            "31524": "NAICS17 31524 Women's, girls', infants' cut-sew apparel mfg.",
            "315240": "NAICS17 315240 Women's, girls', infants' cut-sew apparel mfg.",
            "31525": "NAICS 31525 Cut and sew apparel manufacturing (except contractors)",
            "315250": "NAICS 315250 Cut and sew apparel manufacturing (except contractors)",
            "31528": "NAICS17 31528 Other cut and sew apparel manufacturing",
            "315280": "NAICS17 315280 Other cut and sew apparel manufacturing",
            "31529": "NAICS07 31529 Other cut and sew apparel manufacturing",
            "315291": "NAICS07 315291 Infants' cut and sew apparel manufacturing",
            "315292": "NAICS07 315292 Fur and leather apparel manufacturing",
            "315299": "NAICS07 315299 All other cut and sew apparel manufacturing",
            "3159": "NAICS 3159 Apparel accessories and other apparel manufacturing",
            "31599": "NAICS 31599 Apparel accessories and other apparel manufacturing",
            "315990": "NAICS 315990 Apparel accessories and other apparel manufacturing",
            "315991": "NAICS07 315991 Hat, cap, and millinery manufacturing",
            "315992": "NAICS07 315992 Glove and mitten manufacturing",
            "315993": "NAICS07 315993 Men's and boys' neckwear manufacturing",
            "315999": "NAICS07 315999 All other accessory and apparel manufacturing",
            "316": "NAICS 316 Leather and allied product manufacturing",
            "3161": "NAICS 3161 Leather and hide tanning and finishing",
            "31611": "NAICS 31611 Leather and hide tanning and finishing",
            "316110": "NAICS 316110 Leather and hide tanning and finishing",
            "3162": "NAICS 3162 Footwear manufacturing",
            "31621": "NAICS 31621 Footwear manufacturing",
            "316210": "NAICS 316210 Footwear manufacturing",
            "316211": "NAICS07 316211 Rubber and plastics footwear manufacturing",
            "316212": "NAICS07 316212 House slipper manufacturing",
            "316213": "NAICS07 316213 Men's nonathletic footwear manufacturing",
            "316214": "NAICS07 316214 Women's nonathletic footwear manufacturing",
            "316219": "NAICS07 316219 Other footwear manufacturing",
            "3169": "NAICS 3169 Other leather and allied product manufacturing",
            "31699": "NAICS 31699 Other leather and allied product manufacturing",
            "316990": "NAICS 316990 Other leather and allied product manufacturing",
            "316991": "NAICS07 316991 Luggage manufacturing",
            "316992": "NAICS17 316992 Women's handbag and purse manufacturing",
            "316993": "NAICS07 316993 Other personal leather good manufacturing",
            "316998": "NAICS17 316998 All other leather and allied good mfg.",
            "316999": "NAICS07 316999 All other leather and allied good mfg.",
            "321": "NAICS 321 Wood product manufacturing",
            "3211": "NAICS 3211 Sawmills and wood preservation",
            "32111": "NAICS 32111 Sawmills and wood preservation",
            "321113": "NAICS 321113 Sawmills",
            "321114": "NAICS 321114 Wood preservation",
            "3212": "NAICS 3212 Veneer, plywood, and engineered wood product manufacturing",
            "32121": "NAICS 32121 Veneer, plywood, and engineered wood product manufacturing",
            "321211": "NAICS 321211 Hardwood veneer and plywood manufacturing",
            "321212": "NAICS 321212 Softwood veneer and plywood manufacturing",
            "321213": "NAICS17 321213 Engineered wood member manufacturing",
            "321214": "NAICS17 321214 Truss manufacturing",
            "321215": "NAICS 321215 Engineered wood member manufacturing",
            "321219": "NAICS 321219 Reconstituted wood product manufacturing",
            "3219": "NAICS 3219 Other wood product manufacturing",
            "32191": "NAICS 32191 Millwork",
            "321911": "NAICS 321911 Wood window and door manufacturing",
            "321912": "NAICS 321912 Cut stock, resawing lumber, and planing",
            "321918": "NAICS 321918 Other millwork (including flooring)",
            "32192": "NAICS 32192 Wood container and pallet manufacturing",
            "321920": "NAICS 321920 Wood container and pallet manufacturing",
            "32199": "NAICS 32199 All other wood product manufacturing",
            "321991": "NAICS 321991 Manufactured home (mobile home) manufacturing",
            "321992": "NAICS 321992 Prefabricated wood building manufacturing",
            "321999": "NAICS 321999 All other miscellaneous wood product manufacturing",
            "322": "NAICS 322 Paper manufacturing",
            "3221": "NAICS 3221 Pulp, paper, and paperboard mills",
            "32211": "NAICS 32211 Pulp mills",
            "322110": "NAICS 322110 Pulp mills",
            "32212": "NAICS 32212 Paper mills",
            "322120": "NAICS 322120 Paper mills",
            "322121": "NAICS17 322121 Paper, except newsprint, mills",
            "322122": "NAICS17 322122 Newsprint mills",
            "32213": "NAICS 32213 Paperboard mills",
            "322130": "NAICS 322130 Paperboard mills",
            "3222": "NAICS 3222 Converted paper product manufacturing",
            "32221": "NAICS 32221 Paperboard container manufacturing",
            "322211": "NAICS 322211 Corrugated and solid fiber box manufacturing",
            "322212": "NAICS 322212 Folding paperboard box manufacturing",
            "322213": "NAICS07 322213 Setup paperboard box manufacturing",
            "322214": "NAICS07 322214 Fiber can, tube, and drum manufacturing",
            "322215": "NAICS07 322215 Nonfolding sanitary food container mfg.",
            "322219": "NAICS 322219 Other paperboard container manufacturing",
            "32222": "NAICS 32222 Paper bag and coated and treated paper manufacturing",
            "322220": "NAICS 322220 Paper bag and coated and treated paper manufacturing",
            "322221": "NAICS07 322221 Coated and laminated packaging paper mfg.",
            "322222": "NAICS07 322222 Coated and laminated paper manufacturing",
            "322223": "NAICS07 322223 Coated paper bag and pouch manufacturing",
            "322224": "NAICS07 322224 Uncoated paper and multiwall bag mfg.",
            "322225": "NAICS07 322225 Flexible packaging foil manufacturing",
            "322226": "NAICS07 322226 Surface-coated paperboard manufacturing",
            "32223": "NAICS 32223 Stationery product manufacturing",
            "322230": "NAICS 322230 Stationery product manufacturing",
            "322231": "NAICS07 322231 Die-cut paper office supplies manufacturing",
            "322232": "NAICS07 322232 Envelope manufacturing",
            "322233": "NAICS07 322233 Stationery and related product manufacturing",
            "32229": "NAICS 32229 Other converted paper product manufacturing",
            "322291": "NAICS 322291 Sanitary paper product manufacturing",
            "322299": "NAICS 322299 All other converted paper product manufacturing",
            "323": "NAICS 323 Printing and related support activities",
            "3231": "NAICS 3231 Printing and related support activities",
            "32311": "NAICS 32311 Printing",
            "323110": "NAICS07 323110 Commercial lithographic printing",
            "323111": "NAICS 323111 Commercial printing (except screen and books)",
            "323112": "NAICS07 323112 Commercial flexographic printing",
            "323113": "NAICS 323113 Commercial screen printing",
            "323114": "NAICS07 323114 Quick printing",
            "323115": "NAICS07 323115 Digital printing",
            "323116": "NAICS07 323116 Manifold business forms printing",
            "323117": "NAICS 323117 Books printing",
            "323118": "NAICS07 323118 Blankbook and looseleaf binder manufacturing",
            "323119": "NAICS07 323119 Other commercial printing",
            "32312": "NAICS 32312 Support activities for printing",
            "323120": "NAICS 323120 Support activities for printing",
            "323121": "NAICS07 323121 Tradebinding and related work",
            "323122": "NAICS07 323122 Prepress services",
            "324": "NAICS 324 Petroleum and coal products manufacturing",
            "3241": "NAICS 3241 Petroleum and coal products manufacturing",
            "32411": "NAICS 32411 Petroleum refineries",
            "324110": "NAICS 324110 Petroleum refineries",
            "32412": "NAICS 32412 Asphalt paving, roofing, and saturated materials manufacturing",
            "324121": "NAICS 324121 Asphalt paving mixture and block manufacturing",
            "324122": "NAICS 324122 Asphalt shingle and coating materials manufacturing",
            "32419": "NAICS 32419 Other petroleum and coal products manufacturing",
            "324191": "NAICS 324191 Petroleum lubricating oil and grease manufacturing",
            "324199": "NAICS 324199 All other petroleum and coal products manufacturing",
            "325": "NAICS 325 Chemical manufacturing",
            "3251": "NAICS 3251 Basic chemical manufacturing",
            "32511": "NAICS 32511 Petrochemical manufacturing",
            "325110": "NAICS 325110 Petrochemical manufacturing",
            "32512": "NAICS 32512 Industrial gas manufacturing",
            "325120": "NAICS 325120 Industrial gas manufacturing",
            "32513": "NAICS 32513 Synthetic dye and pigment manufacturing",
            "325130": "NAICS 325130 Synthetic dye and pigment manufacturing",
            "325131": "NAICS07 325131 Inorganic dye and pigment manufacturing",
            "325132": "NAICS07 325132 Synthetic organic dye and pigment mfg.",
            "32518": "NAICS 32518 Other basic inorganic chemical manufacturing",
            "325180": "NAICS 325180 Other basic inorganic chemical manufacturing",
            "325181": "NAICS07 325181 Alkalies and chlorine manufacturing",
            "325182": "NAICS07 325182 Carbon black manufacturing",
            "325188": "NAICS07 325188 All other basic inorganic chemical mfg.",
            "32519": "NAICS 32519 Other basic organic chemical manufacturing",
            "325191": "NAICS07 325191 Gum and wood chemical manufacturing",
            "325192": "NAICS07 325192 Cyclic crude and intermediate manufacturing",
            "325193": "NAICS 325193 Ethyl alcohol manufacturing",
            "325194": "NAICS 325194 Cyclic crude, intermediate, and gum and wood chemical manufacturing",
            "325199": "NAICS 325199 All other basic organic chemical manufacturing",
            "3252": "NAICS 3252 Resin, synthetic rubber, and artificial and synthetic fibers and filaments manufacturing",
            "32521": "NAICS 32521 Resin and synthetic rubber manufacturing",
            "325211": "NAICS 325211 Plastics material and resin manufacturing",
            "325212": "NAICS 325212 Synthetic rubber manufacturing",
            "32522": "NAICS 32522 Artificial and synthetic fibers and filaments manufacturing",
            "325220": "NAICS 325220 Artificial and synthetic fibers and filaments manufacturing",
            "325221": "NAICS07 325221 Cellulosic organic fiber manufacturing",
            "325222": "NAICS07 325222 Noncellulosic organic fiber manufacturing",
            "3253": "NAICS 3253 Pesticide, fertilizer, and other agricultural chemical manufacturing",
            "32531": "NAICS 32531 Fertilizer and compost manufacturing",
            "325311": "NAICS 325311 Nitrogenous fertilizer manufacturing",
            "325312": "NAICS 325312 Phosphatic fertilizer manufacturing",
            "325314": "NAICS 325314 Fertilizer (mixing only) manufacturing",
            "325315": "NAICS 325315 Compost manufacturing",
            "32532": "NAICS 32532 Pesticide and other agricultural chemical manufacturing",
            "325320": "NAICS 325320 Pesticide and other agricultural chemical manufacturing",
            "3254": "NAICS 3254 Pharmaceutical and medicine manufacturing",
            "32541": "NAICS 32541 Pharmaceutical and medicine manufacturing",
            "325411": "NAICS 325411 Medicinal and botanical manufacturing",
            "325412": "NAICS 325412 Pharmaceutical preparation manufacturing",
            "325413": "NAICS 325413 In-vitro diagnostic substance manufacturing",
            "325414": "NAICS 325414 Biological product (except diagnostic) manufacturing",
            "3255": "NAICS 3255 Paint, coating, and adhesive manufacturing",
            "32551": "NAICS 32551 Paint and coating manufacturing",
            "325510": "NAICS 325510 Paint and coating manufacturing",
            "32552": "NAICS 32552 Adhesive manufacturing",
            "325520": "NAICS 325520 Adhesive manufacturing",
            "3256": "NAICS 3256 Soap, cleaning compound, and toilet preparation manufacturing",
            "32561": "NAICS 32561 Soap and cleaning compound manufacturing",
            "325611": "NAICS 325611 Soap and other detergent manufacturing",
            "325612": "NAICS 325612 Polish and other sanitation good manufacturing",
            "325613": "NAICS 325613 Surface active agent manufacturing",
            "32562": "NAICS 32562 Toilet preparation manufacturing",
            "325620": "NAICS 325620 Toilet preparation manufacturing",
            "3259": "NAICS 3259 Other chemical product and preparation manufacturing",
            "32591": "NAICS 32591 Printing ink manufacturing",
            "325910": "NAICS 325910 Printing ink manufacturing",
            "32592": "NAICS 32592 Explosives manufacturing",
            "325920": "NAICS 325920 Explosives manufacturing",
            "32599": "NAICS 32599 All other chemical product and preparation manufacturing",
            "325991": "NAICS 325991 Custom compounding of purchased resins",
            "325992": "NAICS 325992 Photographic film, paper, plate, chemical, and copy toner manufacturing",
            "325998": "NAICS 325998 All other miscellaneous chemical product and preparation manufacturing",
            "326": "NAICS 326 Plastics and rubber products manufacturing",
            "3261": "NAICS 3261 Plastics product manufacturing",
            "32611": "NAICS 32611 Plastics packaging materials and unlaminated film and sheet manufacturing",
            "326111": "NAICS 326111 Plastics bag and pouch manufacturing",
            "326112": "NAICS 326112 Plastics packaging film and sheet (including laminated) manufacturing",
            "326113": "NAICS 326113 Unlaminated plastics film and sheet (except packaging) manufacturing",
            "32612": "NAICS 32612 Plastics pipe, pipe fitting, and unlaminated profile shape manufacturing",
            "326121": "NAICS 326121 Unlaminated plastics profile shape manufacturing",
            "326122": "NAICS 326122 Plastics pipe and pipe fitting manufacturing",
            "32613": "NAICS 32613 Laminated plastics plate, sheet (except packaging), and shape manufacturing",
            "326130": "NAICS 326130 Laminated plastics plate, sheet (except packaging), and shape manufacturing",
            "32614": "NAICS 32614 Polystyrene foam product manufacturing",
            "326140": "NAICS 326140 Polystyrene foam product manufacturing",
            "32615": "NAICS 32615 Urethane and other foam product (except polystyrene) manufacturing",
            "326150": "NAICS 326150 Urethane and other foam product (except polystyrene) manufacturing",
            "32616": "NAICS 32616 Plastics bottle manufacturing",
            "326160": "NAICS 326160 Plastics bottle manufacturing",
            "32619": "NAICS 32619 Other plastics product manufacturing",
            "326191": "NAICS 326191 Plastics plumbing fixture manufacturing",
            "326192": "NAICS07 326192 Resilient floor covering manufacturing",
            "326199": "NAICS 326199 All other plastics product manufacturing",
            "3262": "NAICS 3262 Rubber product manufacturing",
            "32621": "NAICS 32621 Tire manufacturing",
            "326211": "NAICS 326211 Tire manufacturing (except retreading)",
            "326212": "NAICS 326212 Tire retreading",
            "32622": "NAICS 32622 Rubber and plastics hoses and belting manufacturing",
            "326220": "NAICS 326220 Rubber and plastics hoses and belting manufacturing",
            "32629": "NAICS 32629 Other rubber product manufacturing",
            "326291": "NAICS 326291 Rubber product manufacturing for mechanical use",
            "326299": "NAICS 326299 All other rubber product manufacturing",
            "327": "NAICS 327 Nonmetallic mineral product manufacturing",
            "3271": "NAICS 3271 Clay product and refractory manufacturing",
            "32711": "NAICS 32711 Pottery, ceramics, and plumbing fixture manufacturing",
            "327110": "NAICS 327110 Pottery, ceramics, and plumbing fixture manufacturing",
            "327111": "NAICS07 327111 Vitreous china plumbing fixture manufacturing",
            "327112": "NAICS07 327112 Vitreous china and earthenware articles mfg.",
            "327113": "NAICS07 327113 Porcelain electrical supply manufacturing",
            "32712": "NAICS 32712 Clay building material and refractories manufacturing",
            "327120": "NAICS 327120 Clay building material and refractories manufacturing",
            "327121": "NAICS07 327121 Brick and structural clay tile manufacturing",
            "327122": "NAICS07 327122 Ceramic wall and floor tile manufacturing",
            "327123": "NAICS07 327123 Other structural clay product manufacturing",
            "327124": "NAICS07 327124 Clay refractory manufacturing",
            "327125": "NAICS07 327125 Nonclay refractory manufacturing",
            "3272": "NAICS 3272 Glass and glass product manufacturing",
            "32721": "NAICS 32721 Glass and glass product manufacturing",
            "327211": "NAICS 327211 Flat glass manufacturing",
            "327212": "NAICS 327212 Other pressed and blown glass and glassware manufacturing",
            "327213": "NAICS 327213 Glass container manufacturing",
            "327215": "NAICS 327215 Glass product manufacturing made of purchased glass",
            "3273": "NAICS 3273 Cement and concrete product manufacturing",
            "32731": "NAICS 32731 Cement manufacturing",
            "327310": "NAICS 327310 Cement manufacturing",
            "32732": "NAICS 32732 Ready-mix concrete manufacturing",
            "327320": "NAICS 327320 Ready-mix concrete manufacturing",
            "32733": "NAICS 32733 Concrete pipe, brick, and block manufacturing",
            "327331": "NAICS 327331 Concrete block and brick manufacturing",
            "327332": "NAICS 327332 Concrete pipe manufacturing",
            "32739": "NAICS 32739 Other concrete product manufacturing",
            "327390": "NAICS 327390 Other concrete product manufacturing",
            "3274": "NAICS 3274 Lime and gypsum product manufacturing",
            "32741": "NAICS 32741 Lime manufacturing",
            "327410": "NAICS 327410 Lime manufacturing",
            "32742": "NAICS 32742 Gypsum product manufacturing",
            "327420": "NAICS 327420 Gypsum product manufacturing",
            "3279": "NAICS 3279 Other nonmetallic mineral product manufacturing",
            "32791": "NAICS 32791 Abrasive product manufacturing",
            "327910": "NAICS 327910 Abrasive product manufacturing",
            "32799": "NAICS 32799 All other nonmetallic mineral product manufacturing",
            "327991": "NAICS 327991 Cut stone and stone product manufacturing",
            "327992": "NAICS 327992 Ground or treated mineral and earth manufacturing",
            "327993": "NAICS 327993 Mineral wool manufacturing",
            "327999": "NAICS 327999 All other miscellaneous nonmetallic mineral product manufacturing",
            "331": "NAICS 331 Primary metal manufacturing",
            "3311": "NAICS 3311 Iron and steel mills and ferroalloy manufacturing",
            "33111": "NAICS 33111 Iron and steel mills and ferroalloy manufacturing",
            "331110": "NAICS 331110 Iron and steel mills and ferroalloy manufacturing",
            "331111": "NAICS07 331111 Iron and steel mills",
            "331112": "NAICS07 331112 Ferroalloy and related product manufacturing",
            "3312": "NAICS 3312 Steel product manufacturing from purchased steel",
            "33121": "NAICS 33121 Iron and steel pipe and tube manufacturing from purchased steel",
            "331210": "NAICS 331210 Iron and steel pipe and tube manufacturing from purchased steel",
            "33122": "NAICS 33122 Rolling and drawing of purchased steel",
            "331221": "NAICS 331221 Rolled steel shape manufacturing",
            "331222": "NAICS 331222 Steel wire drawing",
            "3313": "NAICS 3313 Alumina and aluminum production and processing",
            "33131": "NAICS 33131 Alumina and aluminum production and processing",
            "331311": "NAICS07 331311 Alumina refining",
            "331312": "NAICS07 331312 Primary aluminum production",
            "331313": "NAICS 331313 Alumina refining and primary aluminum production",
            "331314": "NAICS 331314 Secondary smelting and alloying of aluminum",
            "331315": "NAICS 331315 Aluminum sheet, plate, and foil manufacturing",
            "331316": "NAICS07 331316 Aluminum extruded product manufacturing",
            "331318": "NAICS 331318 Other aluminum rolling, drawing, and extruding",
            "331319": "NAICS07 331319 Other aluminum rolling and drawing",
            "3314": "NAICS 3314 Nonferrous metal (except aluminum) production and processing",
            "33141": "NAICS 33141 Nonferrous metal (except aluminum) smelting and refining",
            "331410": "NAICS 331410 Nonferrous metal (except aluminum) smelting and refining",
            "331411": "NAICS07 331411 Primary smelting and refining of copper",
            "331419": "NAICS07 331419 Primary nonferrous metal, except cu and al",
            "33142": "NAICS 33142 Copper rolling, drawing, extruding, and alloying",
            "331420": "NAICS 331420 Copper rolling, drawing, extruding, and alloying",
            "331421": "NAICS07 331421 Copper rolling, drawing, and extruding",
            "331422": "NAICS07 331422 Copper wire, except mechanical, drawing",
            "331423": "NAICS07 331423 Secondary processing of copper",
            "33149": "NAICS 33149 Nonferrous metal (except copper and aluminum) rolling, drawing, extruding, and alloying",
            "331491": "NAICS 331491 Nonferrous metal (except copper and aluminum) rolling, drawing, and extruding",
            "331492": "NAICS 331492 Secondary smelting, refining, and alloying of nonferrous metal (except copper and aluminum) ",
            "3315": "NAICS 3315 Foundries",
            "33151": "NAICS 33151 Ferrous metal foundries",
            "331511": "NAICS 331511 Iron foundries",
            "331512": "NAICS 331512 Steel investment foundries",
            "331513": "NAICS 331513 Steel foundries (except investment)",
            "33152": "NAICS 33152 Nonferrous metal foundries",
            "331521": "NAICS07 331521 Aluminum die-casting foundries",
            "331522": "NAICS07 331522 Nonferrous, except al, die-casting foundries",
            "331523": "NAICS 331523 Nonferrous metal die-casting foundries",
            "331524": "NAICS 331524 Aluminum foundries (except die-casting)",
            "331525": "NAICS07 331525 Copper foundries, except die-casting",
            "331528": "NAICS07 331528 Other nonferrous foundries, exc. die-casting",
            "331529": "NAICS 331529 Other nonferrous metal foundries (except die-casting)",
            "332": "NAICS 332 Fabricated metal product manufacturing",
            "3321": "NAICS 3321 Forging and stamping",
            "33211": "NAICS 33211 Forging and stamping",
            "332111": "NAICS 332111 Iron and steel forging",
            "332112": "NAICS 332112 Nonferrous forging",
            "332114": "NAICS 332114 Custom roll forming",
            "332115": "NAICS07 332115 Crown and closure manufacturing",
            "332116": "NAICS07 332116 Metal stamping",
            "332117": "NAICS 332117 Powder metallurgy part manufacturing",
            "332119": "NAICS 332119 Metal crown, closure, and other metal stamping (except automotive)",
            "3322": "NAICS 3322 Cutlery and handtool manufacturing",
            "33221": "NAICS 33221 Cutlery and handtool manufacturing",
            "332211": "NAICS07 332211 Cutlery and flatware, except precious, mfg.",
            "332212": "NAICS07 332212 Hand and edge tool manufacturing",
            "332213": "NAICS07 332213 Saw blade and handsaw manufacturing",
            "332214": "NAICS07 332214 Kitchen utensil, pot, and pan manufacturing",
            "332215": "NAICS 332215 Metal kitchen cookware, utensil, cutlery, and flatware (except precious) manufacturing",
            "332216": "NAICS 332216 Saw blade and handtool manufacturing",
            "3323": "NAICS 3323 Architectural and structural metals manufacturing",
            "33231": "NAICS 33231 Plate work and fabricated structural product manufacturing",
            "332311": "NAICS 332311 Prefabricated metal building and component manufacturing",
            "332312": "NAICS 332312 Fabricated structural metal manufacturing",
            "332313": "NAICS 332313 Plate work manufacturing",
            "33232": "NAICS 33232 Ornamental and architectural metal products manufacturing",
            "332321": "NAICS 332321 Metal window and door manufacturing",
            "332322": "NAICS 332322 Sheet metal work manufacturing",
            "332323": "NAICS 332323 Ornamental and architectural metal work manufacturing",
            "3324": "NAICS 3324 Boiler, tank, and shipping container manufacturing",
            "33241": "NAICS 33241 Power boiler and heat exchanger manufacturing",
            "332410": "NAICS 332410 Power boiler and heat exchanger manufacturing",
            "33242": "NAICS 33242 Metal tank (heavy gauge) manufacturing",
            "332420": "NAICS 332420 Metal tank (heavy gauge) manufacturing",
            "33243": "NAICS 33243 Metal can, box, and other metal container (light gauge) manufacturing",
            "332431": "NAICS 332431 Metal can manufacturing",
            "332439": "NAICS 332439 Other metal container manufacturing",
            "3325": "NAICS 3325 Hardware manufacturing",
            "33251": "NAICS 33251 Hardware manufacturing",
            "332510": "NAICS 332510 Hardware manufacturing",
            "3326": "NAICS 3326 Spring and wire product manufacturing",
            "33261": "NAICS 33261 Spring and wire product manufacturing",
            "332611": "NAICS07 332611 Spring, heavy gauge, manufacturing",
            "332612": "NAICS07 332612 Spring, light gauge, manufacturing",
            "332613": "NAICS 332613 Spring manufacturing",
            "332618": "NAICS 332618 Other fabricated wire product manufacturing",
            "3327": "NAICS 3327 Machine shops; turned product; and screw, nut, and bolt manufacturing",
            "33271": "NAICS 33271 Machine shops",
            "332710": "NAICS 332710 Machine shops",
            "33272": "NAICS 33272 Turned product and screw, nut, and bolt manufacturing",
            "332721": "NAICS 332721 Precision turned product manufacturing",
            "332722": "NAICS 332722 Bolt, nut, screw, rivet, and washer manufacturing",
            "3328": "NAICS 3328 Coating, engraving, heat treating, and allied activities",
            "33281": "NAICS 33281 Coating, engraving, heat treating, and allied activities",
            "332811": "NAICS 332811 Metal heat treating",
            "332812": "NAICS 332812 Metal coating, engraving (except jewelry and silverware), and allied services to manufacturers",
            "332813": "NAICS 332813 Electroplating, plating, polishing, anodizing, and coloring",
            "3329": "NAICS 3329 Other fabricated metal product manufacturing",
            "33291": "NAICS 33291 Metal valve manufacturing",
            "332911": "NAICS 332911 Industrial valve manufacturing",
            "332912": "NAICS 332912 Fluid power valve and hose fitting manufacturing",
            "332913": "NAICS 332913 Plumbing fixture fitting and trim manufacturing",
            "332919": "NAICS 332919 Other metal valve and pipe fitting manufacturing",
            "33299": "NAICS 33299 All other fabricated metal product manufacturing",
            "332991": "NAICS 332991 Ball and roller bearing manufacturing",
            "332992": "NAICS 332992 Small arms ammunition manufacturing",
            "332993": "NAICS 332993 Ammunition (except small arms) manufacturing",
            "332994": "NAICS 332994 Small arms, ordnance, and ordnance accessories manufacturing",
            "332995": "NAICS07 332995 Other ordnance and accessories manufacturing",
            "332996": "NAICS 332996 Fabricated pipe and pipe fitting manufacturing",
            "332997": "NAICS07 332997 Industrial pattern manufacturing",
            "332998": "NAICS07 332998 Enameled iron and metal sanitary ware mfg.",
            "332999": "NAICS 332999 All other miscellaneous fabricated metal product manufacturing",
            "333": "NAICS 333 Machinery manufacturing",
            "3331": "NAICS 3331 Agriculture, construction, and mining machinery manufacturing",
            "33311": "NAICS 33311 Agricultural implement manufacturing",
            "333111": "NAICS 333111 Farm machinery and equipment manufacturing",
            "333112": "NAICS 333112 Lawn and garden tractor and home lawn and garden equipment manufacturing",
            "33312": "NAICS 33312 Construction machinery manufacturing",
            "333120": "NAICS 333120 Construction machinery manufacturing",
            "33313": "NAICS 33313 Mining and oil and gas field machinery manufacturing",
            "333131": "NAICS 333131 Mining machinery and equipment manufacturing",
            "333132": "NAICS 333132 Oil and gas field machinery and equipment manufacturing",
            "3332": "NAICS 3332 Industrial machinery manufacturing",
            "33321": "NAICS07 33321 Sawmill and woodworking machinery",
            "333210": "NAICS07 333210 Sawmill and woodworking machinery",
            "33322": "NAICS07 33322 Plastics and rubber industry machinery",
            "333220": "NAICS07 333220 Plastics and rubber industry machinery",
            "33324": "NAICS 33324 Industrial machinery manufacturing",
            "333241": "NAICS 333241 Food product machinery manufacturing",
            "333242": "NAICS 333242 Semiconductor machinery manufacturing",
            "333243": "NAICS 333243 Sawmill, woodworking, and paper machinery manufacturing",
            "333244": "NAICS17 333244 Printing machinery and equipment mfg.",
            "333248": "NAICS 333248 All other industrial machinery manufacturing",
            "333249": "NAICS17 333249 Other industrial machinery manufacturing",
            "33329": "NAICS07 33329 Other industrial machinery manufacturing",
            "333291": "NAICS07 333291 Paper industry machinery manufacturing",
            "333292": "NAICS07 333292 Textile machinery manufacturing",
            "333293": "NAICS07 333293 Printing machinery and equipment mfg.",
            "333294": "NAICS07 333294 Food product machinery manufacturing",
            "333295": "NAICS07 333295 Semiconductor machinery manufacturing",
            "333298": "NAICS07 333298 All other industrial machinery manufacturing",
            "3333": "NAICS 3333 Commercial and service industry machinery manufacturing",
            "33331": "NAICS 33331 Commercial and service industry machinery manufacturing",
            "333310": "NAICS 333310 Commercial and service industry machinery manufacturing",
            "333311": "NAICS07 333311 Automatic vending machine manufacturing",
            "333312": "NAICS07 333312 Commercial laundry and drycleaning machinery",
            "333313": "NAICS07 333313 Office machinery manufacturing",
            "333314": "NAICS17 333314 Optical instrument and lens manufacturing",
            "333315": "NAICS07 333315 Photographic and photocopying equipment mfg.",
            "333316": "NAICS17 333316 Photographic and photocopying equipment mfg.",
            "333318": "NAICS17 333318 Other commercial and service machinery mfg.",
            "333319": "NAICS07 333319 Other commercial and service machinery mfg.",
            "3334": "NAICS 3334 Ventilation, heating, air-conditioning, and commercial refrigeration equipment manufacturing",
            "33341": "NAICS 33341 Ventilation, heating, air-conditioning, and commercial refrigeration equipment manufacturing",
            "333411": "NAICS07 333411 Air purification equipment manufacturing",
            "333412": "NAICS07 333412 Industrial and commercial fan and blower mfg.",
            "333413": "NAICS 333413 Industrial and commercial fan and blower and air purification equipment manufacturing",
            "333414": "NAICS 333414 Heating equipment (except warm air furnaces) manufacturing",
            "333415": "NAICS 333415 Air-conditioning and warm air heating equipment and commercial and industrial refrigeration equipment manufacturing",
            "3335": "NAICS 3335 Metalworking machinery manufacturing",
            "33351": "NAICS 33351 Metalworking machinery manufacturing",
            "333511": "NAICS 333511 Industrial mold manufacturing",
            "333512": "NAICS07 333512 Metal cutting machine tool manufacturing",
            "333513": "NAICS07 333513 Metal forming machine tool manufacturing",
            "333514": "NAICS 333514 Special die and tool, die set, jig, and fixture manufacturing",
            "333515": "NAICS 333515 Cutting tool and machine tool accessory manufacturing",
            "333516": "NAICS07 333516 Rolling mill machinery and equipment mfg.",
            "333517": "NAICS 333517 Machine tool manufacturing",
            "333518": "NAICS07 333518 Other metalworking machinery manufacturing",
            "333519": "NAICS 333519 Rolling mill and other metalworking machinery manufacturing",
            "3336": "NAICS 3336 Engine, turbine, and power transmission equipment manufacturing",
            "33361": "NAICS 33361 Engine, turbine, and power transmission equipment manufacturing",
            "333611": "NAICS 333611 Turbine and turbine generator set units manufacturing",
            "333612": "NAICS 333612 Speed changer, industrial high-speed drive, and gear manufacturing",
            "333613": "NAICS 333613 Mechanical power transmission equipment manufacturing",
            "333618": "NAICS 333618 Other engine equipment manufacturing",
            "3339": "NAICS 3339 Other general purpose machinery manufacturing",
            "33391": "NAICS 33391 Pump and compressor manufacturing",
            "333911": "NAICS12 333911 Pump and pumping equipment manufacturing",
            "333912": "NAICS 333912 Air and gas compressor manufacturing",
            "333913": "NAICS12 333913 Measuring and dispensing pump manufacturing",
            "333914": "NAICS 333914 Measuring, dispensing, and other pumping equipment manufacturing",
            "33392": "NAICS 33392 Material handling equipment manufacturing",
            "333921": "NAICS 333921 Elevator and moving stairway manufacturing",
            "333922": "NAICS 333922 Conveyor and conveying equipment manufacturing",
            "333923": "NAICS 333923 Overhead traveling crane, hoist, and monorail system manufacturing",
            "333924": "NAICS 333924 Industrial truck, tractor, trailer, and stacker machinery manufacturing",
            "33399": "NAICS 33399 All other general purpose machinery manufacturing",
            "333991": "NAICS 333991 Power-driven handtool manufacturing",
            "333992": "NAICS 333992 Welding and soldering equipment manufacturing",
            "333993": "NAICS 333993 Packaging machinery manufacturing",
            "333994": "NAICS 333994 Industrial process furnace and oven manufacturing",
            "333995": "NAICS 333995 Fluid power cylinder and actuator manufacturing",
            "333996": "NAICS 333996 Fluid power pump and motor manufacturing",
            "333997": "NAICS17 333997 Scale and balance manufacturing",
            "333998": "NAICS 333998 All other miscellaneous general purpose machinery manufacturing",
            "333999": "NAICS17 333999 Miscellaneous general purpose machinery mfg.",
            "334": "NAICS 334 Computer and electronic product manufacturing",
            "3341": "NAICS 3341 Computer and peripheral equipment manufacturing",
            "33411": "NAICS 33411 Computer and peripheral equipment manufacturing",
            "334111": "NAICS 334111 Electronic computer manufacturing",
            "334112": "NAICS 334112 Computer storage device manufacturing",
            "334113": "NAICS07 334113 Computer terminal manufacturing",
            "334118": "NAICS 334118 Computer terminal and other computer peripheral equipment manufacturing",
            "334119": "NAICS07 334119 Other computer peripheral equipment mfg.",
            "3342": "NAICS 3342 Communications equipment manufacturing",
            "33421": "NAICS 33421 Telephone apparatus manufacturing",
            "334210": "NAICS 334210 Telephone apparatus manufacturing",
            "33422": "NAICS 33422 Radio and television broadcasting and wireless communications equipment manufacturing",
            "334220": "NAICS 334220 Radio and television broadcasting and wireless communications equipment manufacturing",
            "33429": "NAICS 33429 Other communications equipment manufacturing",
            "334290": "NAICS 334290 Other communications equipment manufacturing",
            "3343": "NAICS 3343 Audio and video equipment manufacturing",
            "33431": "NAICS 33431 Audio and video equipment manufacturing",
            "334310": "NAICS 334310 Audio and video equipment manufacturing",
            "3344": "NAICS 3344 Semiconductor and other electronic component manufacturing",
            "33441": "NAICS 33441 Semiconductor and other electronic component manufacturing",
            "334411": "NAICS07 334411 Electron tube manufacturing",
            "334412": "NAICS 334412 Bare printed circuit board manufacturing",
            "334413": "NAICS 334413 Semiconductor and related device manufacturing",
            "334414": "NAICS07 334414 Electronic capacitor manufacturing",
            "334415": "NAICS07 334415 Electronic resistor manufacturing",
            "334416": "NAICS 334416 Capacitor, resistor, coil, transformer, and other inductor manufacturing",
            "334417": "NAICS 334417 Electronic connector manufacturing",
            "334418": "NAICS 334418 Printed circuit assembly (electronic assembly) manufacturing",
            "334419": "NAICS 334419 Other electronic component manufacturing",
            "3345": "NAICS 3345 Navigational, measuring, electromedical, and control instruments manufacturing",
            "33451": "NAICS 33451 Navigational, measuring, electromedical, and control instruments manufacturing",
            "334510": "NAICS 334510 Electromedical and electrotherapeutic apparatus manufacturing",
            "334511": "NAICS 334511 Search, detection, navigation, guidance, aeronautical, and nautical system and instrument manufacturing",
            "334512": "NAICS 334512 Automatic environmental control manufacturing for residential, commercial, and appliance use",
            "334513": "NAICS 334513 Instruments and related products manufacturing for measuring, displaying, and controlling industrial process variables",
            "334514": "NAICS 334514 Totalizing fluid meter and counting device manufacturing",
            "334515": "NAICS 334515 Instrument manufacturing for measuring and testing electricity and electrical signals",
            "334516": "NAICS 334516 Analytical laboratory instrument manufacturing",
            "334517": "NAICS 334517 Irradiation apparatus manufacturing",
            "334518": "NAICS07 334518 Watch, clock, and part manufacturing",
            "334519": "NAICS 334519 Other measuring and controlling device manufacturing",
            "3346": "NAICS 3346 Manufacturing and reproducing magnetic and optical media",
            "33461": "NAICS 33461 Manufacturing and reproducing magnetic and optical media",
            "334610": "NAICS 334610 Manufacturing and reproducing magnetic and optical media",
            "334611": "NAICS07 334611 Software reproducing",
            "334612": "NAICS07 334612 Audio and video media reproduction",
            "334613": "NAICS17 334613 Blank magnetic and optical media mfg.",
            "334614": "NAICS17 334614 Software and prerecorded media reproducing",
            "335": "NAICS 335 Electrical equipment, appliance, and component manufacturing",
            "3351": "NAICS 3351 Electric lighting equipment manufacturing",
            "33511": "NAICS17 33511 Electric lamp bulb and part manufacturing",
            "335110": "NAICS17 335110 Electric lamp bulb and part manufacturing",
            "33512": "NAICS17 33512 Lighting fixture manufacturing",
            "335121": "NAICS17 335121 Residential electric lighting fixture mfg.",
            "335122": "NAICS17 335122 Nonresidential electric lighting fixture mfg.",
            "335129": "NAICS17 335129 Other lighting equipment manufacturing",
            "33513": "NAICS 33513 Electric lighting equipment manufacturing",
            "335131": "NAICS 335131 Residential electric lighting fixture manufacturing",
            "335132": "NAICS 335132 Commercial, industrial, and institutional electric lighting fixture manufacturing",
            "335139": "NAICS 335139 Electric lamp bulb and other lighting equipment manufacturing",
            "3352": "NAICS 3352 Household appliance manufacturing",
            "33521": "NAICS 33521 Small electrical appliance manufacturing",
            "335210": "NAICS 335210 Small electrical appliance manufacturing",
            "335211": "NAICS07 335211 Electric housewares and household fan mfg.",
            "335212": "NAICS07 335212 Household vacuum cleaner manufacturing",
            "33522": "NAICS 33522 Major household appliance manufacturing",
            "335220": "NAICS 335220 Major household appliance manufacturing",
            "335221": "NAICS12 335221 Household cooking appliance manufacturing",
            "335222": "NAICS12 335222 Household refrigerator and home freezer mfg.",
            "335224": "NAICS12 335224 Household laundry equipment manufacturing",
            "335228": "NAICS12 335228 Other major household appliance manufacturing",
            "3353": "NAICS 3353 Electrical equipment manufacturing",
            "33531": "NAICS 33531 Electrical equipment manufacturing",
            "335311": "NAICS 335311 Power, distribution, and specialty transformer manufacturing",
            "335312": "NAICS 335312 Motor and generator manufacturing",
            "335313": "NAICS 335313 Switchgear and switchboard apparatus manufacturing",
            "335314": "NAICS 335314 Relay and industrial control manufacturing",
            "3359": "NAICS 3359 Other electrical equipment and component manufacturing",
            "33591": "NAICS 33591 Battery manufacturing",
            "335910": "NAICS 335910 Battery manufacturing",
            "335911": "NAICS17 335911 Storage battery manufacturing",
            "335912": "NAICS17 335912 Primary battery manufacturing",
            "33592": "NAICS 33592 Communication and energy wire and cable manufacturing",
            "335921": "NAICS 335921 Fiber optic cable manufacturing",
            "335929": "NAICS 335929 Other communication and energy wire manufacturing",
            "33593": "NAICS 33593 Wiring device manufacturing",
            "335931": "NAICS 335931 Current-carrying wiring device manufacturing",
            "335932": "NAICS 335932 Noncurrent-carrying wiring device manufacturing",
            "33599": "NAICS 33599 All other electrical equipment and component manufacturing",
            "335991": "NAICS 335991 Carbon and graphite product manufacturing",
            "335999": "NAICS 335999 All other miscellaneous electrical equipment and component manufacturing",
            "336": "NAICS 336 Transportation equipment manufacturing",
            "3361": "NAICS 3361 Motor vehicle manufacturing",
            "33611": "NAICS 33611 Automobile and light duty motor vehicle manufacturing",
            "336110": "NAICS 336110 Automobile and light duty motor vehicle manufacturing",
            "336111": "NAICS17 336111 Automobile manufacturing",
            "336112": "NAICS17 336112 Light truck and utility vehicle manufacturing",
            "33612": "NAICS 33612 Heavy duty truck manufacturing",
            "336120": "NAICS 336120 Heavy duty truck manufacturing",
            "3362": "NAICS 3362 Motor vehicle body and trailer manufacturing",
            "33621": "NAICS 33621 Motor vehicle body and trailer manufacturing",
            "336211": "NAICS 336211 Motor vehicle body manufacturing",
            "336212": "NAICS 336212 Truck trailer manufacturing",
            "336213": "NAICS 336213 Motor home manufacturing",
            "336214": "NAICS 336214 Travel trailer and camper manufacturing",
            "3363": "NAICS 3363 Motor vehicle parts manufacturing",
            "33631": "NAICS 33631 Motor vehicle gasoline engine and engine parts manufacturing",
            "336310": "NAICS 336310 Motor vehicle gasoline engine and engine parts manufacturing",
            "336311": "NAICS07 336311 Carburetor, piston, ring, and valve mfg.",
            "336312": "NAICS07 336312 Gasoline engine and engine parts mfg.",
            "33632": "NAICS 33632 Motor vehicle electrical and electronic equipment manufacturing",
            "336320": "NAICS 336320 Motor vehicle electrical and electronic equipment manufacturing",
            "336321": "NAICS07 336321 Vehicular lighting equipment manufacturing",
            "336322": "NAICS07 336322 Other motor vehicle electric equipment mfg.",
            "33633": "NAICS 33633 Motor vehicle steering and suspension components (except spring) manufacturing",
            "336330": "NAICS 336330 Motor vehicle steering and suspension components (except spring) manufacturing",
            "33634": "NAICS 33634 Motor vehicle brake system manufacturing",
            "336340": "NAICS 336340 Motor vehicle brake system manufacturing",
            "33635": "NAICS 33635 Motor vehicle transmission and power train parts manufacturing",
            "336350": "NAICS 336350 Motor vehicle transmission and power train parts manufacturing",
            "33636": "NAICS 33636 Motor vehicle seating and interior trim manufacturing",
            "336360": "NAICS 336360 Motor vehicle seating and interior trim manufacturing",
            "33637": "NAICS 33637 Motor vehicle metal stamping",
            "336370": "NAICS 336370 Motor vehicle metal stamping",
            "33639": "NAICS 33639 Other motor vehicle parts manufacturing",
            "336390": "NAICS 336390 Other motor vehicle parts manufacturing",
            "336391": "NAICS07 336391 Motor vehicle air-conditioning manufacturing",
            "336399": "NAICS07 336399 All other motor vehicle parts manufacturing",
            "3364": "NAICS 3364 Aerospace product and parts manufacturing",
            "33641": "NAICS 33641 Aerospace product and parts manufacturing",
            "336411": "NAICS 336411 Aircraft manufacturing",
            "336412": "NAICS 336412 Aircraft engine and engine parts manufacturing",
            "336413": "NAICS 336413 Other aircraft parts and auxiliary equipment manufacturing",
            "336414": "NAICS 336414 Guided missile and space vehicle manufacturing",
            "336415": "NAICS 336415 Guided missile and space vehicle propulsion unit and propulsion unit parts manufacturing",
            "336419": "NAICS 336419 Other guided missile and space vehicle parts and auxiliary equipment manufacturing",
            "3365": "NAICS 3365 Railroad rolling stock manufacturing",
            "33651": "NAICS 33651 Railroad rolling stock manufacturing",
            "336510": "NAICS 336510 Railroad rolling stock manufacturing",
            "3366": "NAICS 3366 Ship and boat building",
            "33661": "NAICS 33661 Ship and boat building",
            "336611": "NAICS 336611 Ship building and repairing",
            "336612": "NAICS 336612 Boat building",
            "3369": "NAICS 3369 Other transportation equipment manufacturing",
            "33699": "NAICS 33699 Other transportation equipment manufacturing",
            "336991": "NAICS 336991 Motorcycle, bicycle, and parts manufacturing",
            "336992": "NAICS 336992 Military armored vehicle, tank, and tank component manufacturing",
            "336999": "NAICS 336999 All other transportation equipment manufacturing",
            "337": "NAICS 337 Furniture and related product manufacturing",
            "3371": "NAICS 3371 Household and institutional furniture and kitchen cabinet manufacturing",
            "33711": "NAICS 33711 Wood kitchen cabinet and countertop manufacturing",
            "337110": "NAICS 337110 Wood kitchen cabinet and countertop manufacturing",
            "33712": "NAICS 33712 Household and institutional furniture manufacturing",
            "337121": "NAICS 337121 Upholstered household furniture manufacturing",
            "337122": "NAICS 337122 Nonupholstered wood household furniture manufacturing",
            "337124": "NAICS17 337124 Metal household furniture manufacturing",
            "337125": "NAICS17 337125 Household furniture, exc. wood or metal, mfg.",
            "337126": "NAICS 337126 Household furniture (except wood and upholstered) manufacturing",
            "337127": "NAICS 337127 Institutional furniture manufacturing",
            "337129": "NAICS07 337129 Wood tv, radio, and sewing machine housings",
            "3372": "NAICS 3372 Office furniture (including fixtures) manufacturing",
            "33721": "NAICS 33721 Office furniture (including fixtures) manufacturing",
            "337211": "NAICS 337211 Wood office furniture manufacturing",
            "337212": "NAICS 337212 Custom architectural woodwork and millwork manufacturing",
            "337214": "NAICS 337214 Office furniture (except wood) manufacturing",
            "337215": "NAICS 337215 Showcase, partition, shelving, and locker manufacturing",
            "3379": "NAICS 3379 Other furniture related product manufacturing",
            "33791": "NAICS 33791 Mattress manufacturing",
            "337910": "NAICS 337910 Mattress manufacturing",
            "33792": "NAICS 33792 Blind and shade manufacturing",
            "337920": "NAICS 337920 Blind and shade manufacturing",
            "339": "NAICS 339 Miscellaneous manufacturing",
            "3391": "NAICS 3391 Medical equipment and supplies manufacturing",
            "33911": "NAICS 33911 Medical equipment and supplies manufacturing",
            "339111": "NAICS02 339111 Laboratory apparatus and furniture mfg.",
            "339112": "NAICS 339112 Surgical and medical instrument manufacturing",
            "339113": "NAICS 339113 Surgical appliance and supplies manufacturing",
            "339114": "NAICS 339114 Dental equipment and supplies manufacturing",
            "339115": "NAICS 339115 Ophthalmic goods manufacturing",
            "339116": "NAICS 339116 Dental laboratories",
            "3399": "NAICS 3399 Other miscellaneous manufacturing",
            "33991": "NAICS 33991 Jewelry and silverware manufacturing",
            "339910": "NAICS 339910 Jewelry and silverware manufacturing",
            "339911": "NAICS07 339911 Jewelry, except costume, manufacturing",
            "339912": "NAICS07 339912 Silverware and hollowware manufacturing",
            "339913": "NAICS07 339913 Jewelers' material and lapidary work mfg.",
            "339914": "NAICS07 339914 Costume jewelry and novelty manufacturing",
            "33992": "NAICS 33992 Sporting and athletic goods manufacturing",
            "339920": "NAICS 339920 Sporting and athletic goods manufacturing",
            "33993": "NAICS 33993 Doll, toy, and game manufacturing",
            "339930": "NAICS 339930 Doll, toy, and game manufacturing",
            "339931": "NAICS07 339931 Doll and stuffed toy manufacturing",
            "339932": "NAICS07 339932 Game, toy, and children's vehicle mfg.",
            "33994": "NAICS 33994 Office supplies (except paper) manufacturing",
            "339940": "NAICS 339940 Office supplies (except paper) manufacturing",
            "339941": "NAICS07 339941 Pen and mechanical pencil manufacturing",
            "339942": "NAICS07 339942 Lead pencil and art good manufacturing",
            "339943": "NAICS07 339943 Marking device manufacturing",
            "339944": "NAICS07 339944 Carbon paper and inked ribbon manufacturing",
            "33995": "NAICS 33995 Sign manufacturing",
            "339950": "NAICS 339950 Sign manufacturing",
            "33999": "NAICS 33999 All other miscellaneous manufacturing",
            "339991": "NAICS 339991 Gasket, packing, and sealing device manufacturing",
            "339992": "NAICS 339992 Musical instrument manufacturing",
            "339993": "NAICS 339993 Fastener, button, needle, and pin manufacturing",
            "339994": "NAICS 339994 Broom, brush, and mop manufacturing",
            "339995": "NAICS 339995 Burial casket manufacturing",
            "339999": "NAICS 339999 All other miscellaneous manufacturing",
            "42": "NAICS 42 Wholesale trade",
            "423": "NAICS 423 Merchant wholesalers, durable goods",
            "4231": "NAICS 4231 Motor vehicle and motor vehicle parts and supplies merchant wholesalers",
            "42311": "NAICS 42311 Automobile and other motor vehicle merchant wholesalers",
            "423110": "NAICS 423110 Automobile and other motor vehicle merchant wholesalers",
            "42312": "NAICS 42312 Motor vehicle supplies and new parts merchant wholesalers",
            "423120": "NAICS 423120 Motor vehicle supplies and new parts merchant wholesalers",
            "42313": "NAICS 42313 Tire and tube merchant wholesalers",
            "423130": "NAICS 423130 Tire and tube merchant wholesalers",
            "42314": "NAICS 42314 Motor vehicle parts (used) merchant wholesalers",
            "423140": "NAICS 423140 Motor vehicle parts (used) merchant wholesalers",
            "4232": "NAICS 4232 Furniture and home furnishing merchant wholesalers",
            "42321": "NAICS 42321 Furniture merchant wholesalers",
            "423210": "NAICS 423210 Furniture merchant wholesalers",
            "42322": "NAICS 42322 Home furnishing merchant wholesalers",
            "423220": "NAICS 423220 Home furnishing merchant wholesalers",
            "4233": "NAICS 4233 Lumber and other construction materials merchant wholesalers",
            "42331": "NAICS 42331 Lumber, plywood, millwork, and wood panel merchant wholesalers",
            "423310": "NAICS 423310 Lumber, plywood, millwork, and wood panel merchant wholesalers",
            "42332": "NAICS 42332 Brick, stone, and related construction material merchant wholesalers",
            "423320": "NAICS 423320 Brick, stone, and related construction material merchant wholesalers",
            "42333": "NAICS 42333 Roofing, siding, and insulation material merchant wholesalers",
            "423330": "NAICS 423330 Roofing, siding, and insulation material merchant wholesalers",
            "42339": "NAICS 42339 Other construction material merchant wholesalers",
            "423390": "NAICS 423390 Other construction material merchant wholesalers",
            "4234": "NAICS 4234 Professional and commercial equipment and supplies merchant wholesalers",
            "42341": "NAICS 42341 Photographic equipment and supplies merchant wholesalers",
            "423410": "NAICS 423410 Photographic equipment and supplies merchant wholesalers",
            "42342": "NAICS 42342 Office equipment merchant wholesalers",
            "423420": "NAICS 423420 Office equipment merchant wholesalers",
            "42343": "NAICS 42343 Computer and computer peripheral equipment and software merchant wholesalers",
            "423430": "NAICS 423430 Computer and computer peripheral equipment and software merchant wholesalers",
            "42344": "NAICS 42344 Other commercial equipment merchant wholesalers",
            "423440": "NAICS 423440 Other commercial equipment merchant wholesalers",
            "42345": "NAICS 42345 Medical, dental, and hospital equipment and supplies merchant wholesalers",
            "423450": "NAICS 423450 Medical, dental, and hospital equipment and supplies merchant wholesalers",
            "42346": "NAICS 42346 Ophthalmic goods merchant wholesalers",
            "423460": "NAICS 423460 Ophthalmic goods merchant wholesalers",
            "42349": "NAICS 42349 Other professional equipment and supplies merchant wholesalers",
            "423490": "NAICS 423490 Other professional equipment and supplies merchant wholesalers",
            "4235": "NAICS 4235 Metal and mineral (except petroleum) merchant wholesalers",
            "42351": "NAICS 42351 Metal service centers and other metal merchant wholesalers",
            "423510": "NAICS 423510 Metal service centers and other metal merchant wholesalers",
            "42352": "NAICS 42352 Coal and other mineral and ore merchant wholesalers",
            "423520": "NAICS 423520 Coal and other mineral and ore merchant wholesalers",
            "4236": "NAICS 4236 Household appliances and electrical and electronic goods merchant wholesalers",
            "42361": "NAICS 42361 Electrical apparatus and equipment, wiring supplies, and related equipment merchant wholesalers",
            "423610": "NAICS 423610 Electrical apparatus and equipment, wiring supplies, and related equipment merchant wholesalers",
            "42362": "NAICS 42362 Household appliances, electric housewares, and consumer electronics merchant wholesalers",
            "423620": "NAICS 423620 Household appliances, electric housewares, and consumer electronics merchant wholesalers",
            "42369": "NAICS 42369 Other electronic parts and equipment merchant wholesalers",
            "423690": "NAICS 423690 Other electronic parts and equipment merchant wholesalers",
            "4237": "NAICS 4237 Hardware, and plumbing and heating equipment and supplies merchant wholesalers",
            "42371": "NAICS 42371 Hardware merchant wholesalers",
            "423710": "NAICS 423710 Hardware merchant wholesalers",
            "42372": "NAICS 42372 Plumbing and heating equipment and supplies (hydronics) merchant wholesalers",
            "423720": "NAICS 423720 Plumbing and heating equipment and supplies (hydronics) merchant wholesalers",
            "42373": "NAICS 42373 Warm air heating and air-conditioning equipment and supplies merchant wholesalers",
            "423730": "NAICS 423730 Warm air heating and air-conditioning equipment and supplies merchant wholesalers",
            "42374": "NAICS 42374 Refrigeration equipment and supplies merchant wholesalers",
            "423740": "NAICS 423740 Refrigeration equipment and supplies merchant wholesalers",
            "4238": "NAICS 4238 Machinery, equipment, and supplies merchant wholesalers",
            "42381": "NAICS 42381 Construction and mining (except oil well) machinery and equipment merchant wholesalers",
            "423810": "NAICS 423810 Construction and mining (except oil well) machinery and equipment merchant wholesalers",
            "42382": "NAICS 42382 Farm and garden machinery and equipment merchant wholesalers",
            "423820": "NAICS 423820 Farm and garden machinery and equipment merchant wholesalers",
            "42383": "NAICS 42383 Industrial machinery and equipment merchant wholesalers",
            "423830": "NAICS 423830 Industrial machinery and equipment merchant wholesalers",
            "42384": "NAICS 42384 Industrial supplies merchant wholesalers",
            "423840": "NAICS 423840 Industrial supplies merchant wholesalers",
            "42385": "NAICS 42385 Service establishment equipment and supplies merchant wholesalers",
            "423850": "NAICS 423850 Service establishment equipment and supplies merchant wholesalers",
            "42386": "NAICS 42386 Transportation equipment and supplies (except motor vehicle) merchant wholesalers",
            "423860": "NAICS 423860 Transportation equipment and supplies (except motor vehicle) merchant wholesalers",
            "4239": "NAICS 4239 Miscellaneous durable goods merchant wholesalers",
            "42391": "NAICS 42391 Sporting and recreational goods and supplies merchant wholesalers",
            "423910": "NAICS 423910 Sporting and recreational goods and supplies merchant wholesalers",
            "42392": "NAICS 42392 Toy and hobby goods and supplies merchant wholesalers",
            "423920": "NAICS 423920 Toy and hobby goods and supplies merchant wholesalers",
            "42393": "NAICS 42393 Recyclable material merchant wholesalers",
            "423930": "NAICS 423930 Recyclable material merchant wholesalers",
            "42394": "NAICS 42394 Jewelry, watch, precious stone, and precious metal merchant wholesalers",
            "423940": "NAICS 423940 Jewelry, watch, precious stone, and precious metal merchant wholesalers",
            "42399": "NAICS 42399 Other miscellaneous durable goods merchant wholesalers",
            "423990": "NAICS 423990 Other miscellaneous durable goods merchant wholesalers",
            "424": "NAICS 424 Merchant wholesalers, nondurable goods",
            "4241": "NAICS 4241 Paper and paper product merchant wholesalers",
            "42411": "NAICS 42411 Printing and writing paper merchant wholesalers",
            "424110": "NAICS 424110 Printing and writing paper merchant wholesalers",
            "42412": "NAICS 42412 Stationery and office supplies merchant wholesalers",
            "424120": "NAICS 424120 Stationery and office supplies merchant wholesalers",
            "42413": "NAICS 42413 Industrial and personal service paper merchant wholesalers",
            "424130": "NAICS 424130 Industrial and personal service paper merchant wholesalers",
            "4242": "NAICS 4242 Drugs and druggists' sundries merchant wholesalers",
            "42421": "NAICS 42421 Drugs and druggists' sundries merchant wholesalers",
            "424210": "NAICS 424210 Drugs and druggists' sundries merchant wholesalers",
            "4243": "NAICS 4243 Apparel, piece goods, and notions merchant wholesalers",
            "42431": "NAICS 42431 Piece goods, notions, and other dry goods merchant wholesalers",
            "424310": "NAICS 424310 Piece goods, notions, and other dry goods merchant wholesalers",
            "42432": "NAICS17 42432 Men's and boys' clothing merchant wholesalers",
            "424320": "NAICS17 424320 Men's and boys' clothing merchant wholesalers",
            "42433": "NAICS17 42433 Women's and children's clothing merch. whls.",
            "424330": "NAICS17 424330 Women's and children's clothing merch. whls.",
            "42434": "NAICS 42434 Footwear merchant wholesalers",
            "424340": "NAICS 424340 Footwear merchant wholesalers",
            "42435": "NAICS 42435 Clothing and clothing accessories merchant wholesalers",
            "424350": "NAICS 424350 Clothing and clothing accessories merchant wholesalers",
            "4244": "NAICS 4244 Grocery and related product merchant wholesalers",
            "42441": "NAICS 42441 General line grocery merchant wholesalers",
            "424410": "NAICS 424410 General line grocery merchant wholesalers",
            "42442": "NAICS 42442 Packaged frozen food merchant wholesalers",
            "424420": "NAICS 424420 Packaged frozen food merchant wholesalers",
            "42443": "NAICS 42443 Dairy product (except dried or canned) merchant wholesalers",
            "424430": "NAICS 424430 Dairy product (except dried or canned) merchant wholesalers",
            "42444": "NAICS 42444 Poultry and poultry product merchant wholesalers",
            "424440": "NAICS 424440 Poultry and poultry product merchant wholesalers",
            "42445": "NAICS 42445 Confectionery merchant wholesalers",
            "424450": "NAICS 424450 Confectionery merchant wholesalers",
            "42446": "NAICS 42446 Fish and seafood merchant wholesalers",
            "424460": "NAICS 424460 Fish and seafood merchant wholesalers",
            "42447": "NAICS 42447 Meat and meat product merchant wholesalers",
            "424470": "NAICS 424470 Meat and meat product merchant wholesalers",
            "42448": "NAICS 42448 Fresh fruit and vegetable merchant wholesalers",
            "424480": "NAICS 424480 Fresh fruit and vegetable merchant wholesalers",
            "42449": "NAICS 42449 Other grocery and related products merchant wholesalers",
            "424490": "NAICS 424490 Other grocery and related products merchant wholesalers",
            "4245": "NAICS 4245 Farm product raw material merchant wholesalers",
            "42451": "NAICS 42451 Grain and field bean merchant wholesalers",
            "424510": "NAICS 424510 Grain and field bean merchant wholesalers",
            "42452": "NAICS 42452 Livestock merchant wholesalers",
            "424520": "NAICS 424520 Livestock merchant wholesalers",
            "42459": "NAICS 42459 Other farm product raw material merchant wholesalers",
            "424590": "NAICS 424590 Other farm product raw material merchant wholesalers",
            "4246": "NAICS 4246 Chemical and allied products merchant wholesalers",
            "42461": "NAICS 42461 Plastics materials and basic forms and shapes merchant wholesalers",
            "424610": "NAICS 424610 Plastics materials and basic forms and shapes merchant wholesalers",
            "42469": "NAICS 42469 Other chemical and allied products merchant wholesalers",
            "424690": "NAICS 424690 Other chemical and allied products merchant wholesalers",
            "4247": "NAICS 4247 Petroleum and petroleum products merchant wholesalers",
            "42471": "NAICS 42471 Petroleum bulk stations and terminals",
            "424710": "NAICS 424710 Petroleum bulk stations and terminals",
            "42472": "NAICS 42472 Petroleum and petroleum products merchant wholesalers (except bulk stations and terminals)",
            "424720": "NAICS 424720 Petroleum and petroleum products merchant wholesalers (except bulk stations and terminals)",
            "4248": "NAICS 4248 Beer, wine, and distilled alcoholic beverage merchant wholesalers",
            "42481": "NAICS 42481 Beer and ale merchant wholesalers",
            "424810": "NAICS 424810 Beer and ale merchant wholesalers",
            "42482": "NAICS 42482 Wine and distilled alcoholic beverage merchant wholesalers",
            "424820": "NAICS 424820 Wine and distilled alcoholic beverage merchant wholesalers",
            "4249": "NAICS 4249 Miscellaneous nondurable goods merchant wholesalers",
            "42491": "NAICS 42491 Farm supplies merchant wholesalers",
            "424910": "NAICS 424910 Farm supplies merchant wholesalers",
            "42492": "NAICS 42492 Book, periodical, and newspaper merchant wholesalers",
            "424920": "NAICS 424920 Book, periodical, and newspaper merchant wholesalers",
            "42493": "NAICS 42493 Flower, nursery stock, and florists' supplies merchant wholesalers",
            "424930": "NAICS 424930 Flower, nursery stock, and florists' supplies merchant wholesalers",
            "42494": "NAICS 42494 Tobacco product and electronic cigarette merchant wholesalers",
            "424940": "NAICS 424940 Tobacco product and electronic cigarette merchant wholesalers",
            "42495": "NAICS 42495 Paint, varnish, and supplies merchant wholesalers",
            "424950": "NAICS 424950 Paint, varnish, and supplies merchant wholesalers",
            "42499": "NAICS 42499 Other miscellaneous nondurable goods merchant wholesalers",
            "424990": "NAICS 424990 Other miscellaneous nondurable goods merchant wholesalers",
            "425": "NAICS 425 Wholesale trade agents and brokers",
            "4251": "NAICS 4251 Wholesale trade agents and brokers",
            "42511": "NAICS17 42511 Business to business electronic markets",
            "425110": "NAICS17 425110 Business to business electronic markets",
            "42512": "NAICS 42512 Wholesale trade agents and brokers",
            "425120": "NAICS 425120 Wholesale trade agents and brokers",
            "441": "NAICS 441 Motor vehicle and parts dealers",
            "4411": "NAICS 4411 Automobile dealers",
            "44111": "NAICS 44111 New car dealers",
            "441110": "NAICS 441110 New car dealers",
            "44112": "NAICS 44112 Used car dealers",
            "441120": "NAICS 441120 Used car dealers",
            "4412": "NAICS 4412 Other motor vehicle dealers",
            "44121": "NAICS 44121 Recreational vehicle dealers",
            "441210": "NAICS 441210 Recreational vehicle dealers",
            "44122": "NAICS 44122 Motorcycle, boat, and other motor vehicle dealers",
            "441221": "NAICS07 441221 Motorcycle, atv, personal watercraft dealers",
            "441222": "NAICS 441222 Boat dealers",
            "441227": "NAICS 441227 Motorcycle, atv, and all other motor vehicle dealers",
            "441228": "NAICS17 441228 Motorcycle, atv, and other vehicle dealers",
            "441229": "NAICS07 441229 All other motor vehicle dealers",
            "4413": "NAICS 4413 Automotive parts, accessories, and tire retailers",
            "44131": "NAICS17 44131 Automotive parts and accessories stores",
            "441310": "NAICS17 441310 Automotive parts and accessories stores",
            "44132": "NAICS17 44132 Tire dealers",
            "441320": "NAICS17 441320 Tire dealers",
            "44133": "NAICS 44133 Automotive parts and accessories retailers",
            "441330": "NAICS 441330 Automotive parts and accessories retailers",
            "44134": "NAICS 44134 Tire dealers",
            "441340": "NAICS 441340 Tire dealers",
            "442": "NAICS17 442 Furniture and home furnishings stores",
            "4421": "NAICS17 4421 Furniture stores",
            "44211": "NAICS17 44211 Furniture stores",
            "442110": "NAICS17 442110 Furniture stores",
            "4422": "NAICS17 4422 Home furnishings stores",
            "44221": "NAICS17 44221 Floor covering stores",
            "442210": "NAICS17 442210 Floor covering stores",
            "44229": "NAICS17 44229 Other home furnishings stores",
            "442291": "NAICS17 442291 Window treatment stores",
            "442299": "NAICS17 442299 All other home furnishings stores",
            "443": "NAICS17 443 Electronics and appliance stores",
            "4431": "NAICS17 4431 Electronics and appliance stores",
            "44311": "NAICS07 44311 Appliance, tv, and other electronics stores",
            "443111": "NAICS07 443111 Household appliance stores",
            "443112": "NAICS07 443112 Radio, tv, and other electronics stores",
            "44312": "NAICS07 44312 Computer and software stores",
            "443120": "NAICS07 443120 Computer and software stores",
            "44313": "NAICS07 44313 Camera and photographic supplies stores",
            "443130": "NAICS07 443130 Camera and photographic supplies stores",
            "44314": "NAICS17 44314 Electronics and appliance stores",
            "443141": "NAICS17 443141 Household appliance stores",
            "443142": "NAICS17 443142 Electronics stores",
            "444": "NAICS 444 Building material and garden equipment and supplies dealers",
            "4441": "NAICS 4441 Building material and supplies dealers",
            "44411": "NAICS 44411 Home centers",
            "444110": "NAICS 444110 Home centers",
            "44412": "NAICS 44412 Paint and wallpaper retailers",
            "444120": "NAICS 444120 Paint and wallpaper retailers",
            "44413": "NAICS17 44413 Hardware stores",
            "444130": "NAICS17 444130 Hardware stores",
            "44414": "NAICS 44414 Hardware retailers",
            "444140": "NAICS 444140 Hardware retailers",
            "44418": "NAICS 44418 Other building material dealers",
            "444180": "NAICS 444180 Other building material dealers",
            "44419": "NAICS17 44419 Other building material dealers",
            "444190": "NAICS17 444190 Other building material dealers",
            "4442": "NAICS 4442 Lawn and garden equipment and supplies retailers",
            "44421": "NAICS17 44421 Outdoor power equipment stores",
            "444210": "NAICS17 444210 Outdoor power equipment stores",
            "44422": "NAICS17 44422 Nursery, garden, and farm supply stores",
            "444220": "NAICS17 444220 Nursery, garden, and farm supply stores",
            "44423": "NAICS 44423 Outdoor power equipment retailers",
            "444230": "NAICS 444230 Outdoor power equipment retailers",
            "44424": "NAICS 44424 Nursery, garden center, and farm supply retailers",
            "444240": "NAICS 444240 Nursery, garden center, and farm supply retailers",
            "44-45": "NAICS 44-45 Retail trade",
            "445": "NAICS 445 Food and beverage retailers",
            "4451": "NAICS 4451 Grocery and convenience retailers",
            "44511": "NAICS 44511 Supermarkets and other grocery retailers (except convenience retailers)",
            "445110": "NAICS 445110 Supermarkets and other grocery retailers (except convenience retailers)",
            "44512": "NAICS17 44512 Convenience stores",
            "445120": "NAICS17 445120 Convenience stores",
            "44513": "NAICS 44513 Convenience retailers and vending machine operators",
            "445131": "NAICS 445131 Convenience retailers",
            "445132": "NAICS 445132 Vending machine operators",
            "4452": "NAICS 4452 Specialty food retailers",
            "44521": "NAICS17 44521 Meat markets",
            "445210": "NAICS17 445210 Meat markets",
            "44522": "NAICS17 44522 Fish and seafood markets",
            "445220": "NAICS17 445220 Fish and seafood markets",
            "44523": "NAICS 44523 Fruit and vegetable retailers",
            "445230": "NAICS 445230 Fruit and vegetable retailers",
            "44524": "NAICS 44524 Meat retailers",
            "445240": "NAICS 445240 Meat retailers",
            "44525": "NAICS 44525 Fish and seafood retailers",
            "445250": "NAICS 445250 Fish and seafood retailers",
            "44529": "NAICS 44529 Other specialty food retailers",
            "445291": "NAICS 445291 Baked goods retailers",
            "445292": "NAICS 445292 Confectionery and nut retailers",
            "445298": "NAICS 445298 All other specialty food retailers",
            "445299": "NAICS17 445299 All other specialty food stores",
            "4453": "NAICS 4453 Beer, wine, and liquor retailers",
            "44531": "NAICS17 44531 Beer, wine, and liquor stores",
            "445310": "NAICS17 445310 Beer, wine, and liquor stores",
            "44532": "NAICS 44532 Beer, wine, and liquor retailers",
            "445320": "NAICS 445320 Beer, wine, and liquor retailers",
            "446": "NAICS17 446 Health and personal care stores",
            "4461": "NAICS17 4461 Health and personal care stores",
            "44611": "NAICS17 44611 Pharmacies and drug stores",
            "446110": "NAICS17 446110 Pharmacies and drug stores",
            "44612": "NAICS17 44612 Cosmetic and beauty supply stores",
            "446120": "NAICS17 446120 Cosmetic and beauty supply stores",
            "44613": "NAICS17 44613 Optical goods stores",
            "446130": "NAICS17 446130 Optical goods stores",
            "44619": "NAICS17 44619 Other health and personal care stores",
            "446191": "NAICS17 446191 Food, health, supplement stores",
            "446199": "NAICS17 446199 All other health and personal care stores",
            "447": "NAICS17 447 Gasoline stations",
            "4471": "NAICS17 4471 Gasoline stations",
            "44711": "NAICS17 44711 Gasoline stations with convenience stores",
            "447110": "NAICS17 447110 Gasoline stations with convenience stores",
            "44719": "NAICS17 44719 Other gasoline stations",
            "447190": "NAICS17 447190 Other gasoline stations",
            "448": "NAICS17 448 Clothing and clothing accessories stores",
            "4481": "NAICS17 4481 Clothing stores",
            "44811": "NAICS17 44811 Men's clothing stores",
            "448110": "NAICS17 448110 Men's clothing stores",
            "44812": "NAICS17 44812 Women's clothing stores",
            "448120": "NAICS17 448120 Women's clothing stores",
            "44813": "NAICS17 44813 Children's and infants' clothing stores",
            "448130": "NAICS17 448130 Children's and infants' clothing stores",
            "44814": "NAICS17 44814 Family clothing stores",
            "448140": "NAICS17 448140 Family clothing stores",
            "44815": "NAICS17 44815 Clothing accessories stores",
            "448150": "NAICS17 448150 Clothing accessories stores",
            "44819": "NAICS17 44819 Other clothing stores",
            "448190": "NAICS17 448190 Other clothing stores",
            "4482": "NAICS17 4482 Shoe stores",
            "44821": "NAICS17 44821 Shoe stores",
            "448210": "NAICS17 448210 Shoe stores",
            "4483": "NAICS17 4483 Jewelry, luggage, and leather goods stores",
            "44831": "NAICS17 44831 Jewelry stores",
            "448310": "NAICS17 448310 Jewelry stores",
            "44832": "NAICS17 44832 Luggage and leather goods stores",
            "448320": "NAICS17 448320 Luggage and leather goods stores",
            "449": "NAICS 449 Furniture, home furnishings, electronics, and appliance retailers",
            "4491": "NAICS 4491 Furniture and home furnishings retailers",
            "44911": "NAICS 44911 Furniture retailers",
            "449110": "NAICS 449110 Furniture retailers",
            "44912": "NAICS 44912 Home furnishings retailers",
            "449121": "NAICS 449121 Floor covering retailers",
            "449122": "NAICS 449122 Window treatment retailers",
            "449129": "NAICS 449129 All other home furnishings retailers",
            "4492": "NAICS 4492 Electronics and appliance retailers",
            "44921": "NAICS 44921 Electronics and appliance retailers",
            "449210": "NAICS 449210 Electronics and appliance retailers",
            "451": "NAICS17 451 Sports, hobby, music instrument, book stores",
            "4511": "NAICS17 4511 Sporting goods and musical instrument stores",
            "45111": "NAICS17 45111 Sporting goods stores",
            "451110": "NAICS17 451110 Sporting goods stores",
            "45112": "NAICS17 45112 Hobby, toy, and game stores",
            "451120": "NAICS17 451120 Hobby, toy, and game stores",
            "45113": "NAICS17 45113 Sewing, needlework, and piece goods stores",
            "451130": "NAICS17 451130 Sewing, needlework, and piece goods stores",
            "45114": "NAICS17 45114 Musical instrument and supplies stores",
            "451140": "NAICS17 451140 Musical instrument and supplies stores",
            "4512": "NAICS17 4512 Book stores and news dealers",
            "45121": "NAICS17 45121 Book stores and news dealers",
            "451211": "NAICS17 451211 Book stores",
            "451212": "NAICS17 451212 News dealers and newsstands",
            "45122": "NAICS07 45122 Precorded tape, cd, and record stores",
            "451220": "NAICS07 451220 Precorded tape, cd, and record stores",
            "452": "NAICS17 452 General merchandise stores",
            "4521": "NAICS12 4521 Department stores",
            "45211": "NAICS12 45211 Department stores",
            "452111": "NAICS12 452111 Department stores, except discount",
            "452112": "NAICS12 452112 Discount department stores",
            "4522": "NAICS17 4522 Department stores",
            "45221": "NAICS17 45221 Department stores",
            "452210": "NAICS17 452210 Department stores",
            "4523": "NAICS17 4523 General merchandise stores, including warehouse clubs and supercenters",
            "45231": "NAICS17 45231 General merchandise stores, including warehouse clubs and supercenters",
            "452311": "NAICS17 452311 Warehouse clubs and supercenters",
            "452319": "NAICS17 452319 All other general merchandise stores",
            "4529": "NAICS12 4529 Other general merchandise stores",
            "45291": "NAICS12 45291 Warehouse clubs and supercenters",
            "452910": "NAICS12 452910 Warehouse clubs and supercenters",
            "45299": "NAICS12 45299 All other general merchandise stores",
            "452990": "NAICS12 452990 All other general merchandise stores",
            "453": "NAICS17 453 Miscellaneous store retailers",
            "4531": "NAICS17 4531 Florists",
            "45311": "NAICS17 45311 Florists",
            "453110": "NAICS17 453110 Florists",
            "4532": "NAICS17 4532 Office supplies, stationery, and gift stores",
            "45321": "NAICS17 45321 Office supplies and stationery stores",
            "453210": "NAICS17 453210 Office supplies and stationery stores",
            "45322": "NAICS17 45322 Gift, novelty, and souvenir stores",
            "453220": "NAICS17 453220 Gift, novelty, and souvenir stores",
            "4533": "NAICS17 4533 Used merchandise stores",
            "45331": "NAICS17 45331 Used merchandise stores",
            "453310": "NAICS17 453310 Used merchandise stores",
            "4539": "NAICS17 4539 Other miscellaneous store retailers",
            "45391": "NAICS17 45391 Pet and pet supplies stores",
            "453910": "NAICS17 453910 Pet and pet supplies stores",
            "45392": "NAICS17 45392 Art dealers",
            "453920": "NAICS17 453920 Art dealers",
            "45393": "NAICS17 45393 Manufactured, mobile, home dealers",
            "453930": "NAICS17 453930 Manufactured, mobile, home dealers",
            "45399": "NAICS17 45399 All other miscellaneous store retailers",
            "453991": "NAICS17 453991 Tobacco stores",
            "453998": "NAICS17 453998 Store retailers not specified elsewhere",
            "454": "NAICS17 454 Nonstore retailers",
            "4541": "NAICS17 4541 Electronic shopping and mail-order houses",
            "45411": "NAICS17 45411 Electronic shopping and mail-order houses",
            "454110": "NAICS17 454110 Electronic shopping and mail-order houses",
            "454111": "NAICS12 454111 Electronic shopping",
            "454112": "NAICS12 454112 Electronic auctions",
            "454113": "NAICS12 454113 Mail-order houses",
            "4542": "NAICS17 4542 Vending machine operators",
            "45421": "NAICS17 45421 Vending machine operators",
            "454210": "NAICS17 454210 Vending machine operators",
            "4543": "NAICS17 4543 Direct selling establishments",
            "45431": "NAICS17 45431 Fuel dealers",
            "454310": "NAICS17 454310 Fuel dealers",
            "454311": "NAICS07 454311 Heating oil dealers",
            "454312": "NAICS07 454312 Liquefied petroleum gas, bottled gas, dealers",
            "454319": "NAICS07 454319 Other fuel dealers",
            "45439": "NAICS17 45439 Other direct selling establishments",
            "454390": "NAICS17 454390 Other direct selling establishments",
            "455": "NAICS 455 General merchandise retailers",
            "4551": "NAICS 4551 Department stores",
            "45511": "NAICS 45511 Department stores",
            "455110": "NAICS 455110 Department stores",
            "4552": "NAICS 4552 Warehouse clubs, supercenters, and other general merchandise retailers",
            "45521": "NAICS 45521 Warehouse clubs, supercenters, and other general merchandise retailers",
            "455211": "NAICS 455211 Warehouse clubs and supercenters",
            "455219": "NAICS 455219 All other general merchandise retailers",
            "456": "NAICS 456 Health and personal care retailers",
            "4561": "NAICS 4561 Health and personal care retailers",
            "45611": "NAICS 45611 Pharmacies and drug retailers",
            "456110": "NAICS 456110 Pharmacies and drug retailers",
            "45612": "NAICS 45612 Cosmetics, beauty supplies, and perfume retailers",
            "456120": "NAICS 456120 Cosmetics, beauty supplies, and perfume retailers",
            "45613": "NAICS 45613 Optical goods retailers",
            "456130": "NAICS 456130 Optical goods retailers",
            "45619": "NAICS 45619 Other health and personal care retailers",
            "456191": "NAICS 456191 Food (health) supplement retailers",
            "456199": "NAICS 456199 All other health and personal care retailers",
            "457": "NAICS 457 Gasoline stations and fuel dealers",
            "4571": "NAICS 4571 Gasoline stations",
            "45711": "NAICS 45711 Gasoline stations with convenience stores",
            "457110": "NAICS 457110 Gasoline stations with convenience stores",
            "45712": "NAICS 45712 Other gasoline stations",
            "457120": "NAICS 457120 Other gasoline stations",
            "4572": "NAICS 4572 Fuel dealers",
            "45721": "NAICS 45721 Fuel dealers",
            "457210": "NAICS 457210 Fuel dealers",
            "458": "NAICS 458 Clothing, clothing accessories, shoe, and jewelry retailers",
            "4581": "NAICS 4581 Clothing and clothing accessories retailers",
            "45811": "NAICS 45811 Clothing and clothing accessories retailers",
            "458110": "NAICS 458110 Clothing and clothing accessories retailers",
            "4582": "NAICS 4582 Shoe retailers",
            "45821": "NAICS 45821 Shoe retailers",
            "458210": "NAICS 458210 Shoe retailers",
            "4583": "NAICS 4583 Jewelry, luggage, and leather goods retailers",
            "45831": "NAICS 45831 Jewelry retailers",
            "458310": "NAICS 458310 Jewelry retailers",
            "45832": "NAICS 45832 Luggage and leather goods retailers",
            "458320": "NAICS 458320 Luggage and leather goods retailers",
            "459": "NAICS 459 Sporting goods, hobby, musical instrument, book, and miscellaneous retailers",
            "4591": "NAICS 4591 Sporting goods, hobby, and musical instrument retailers",
            "45911": "NAICS 45911 Sporting goods retailers",
            "459110": "NAICS 459110 Sporting goods retailers",
            "45912": "NAICS 45912 Hobby, toy, and game retailers",
            "459120": "NAICS 459120 Hobby, toy, and game retailers",
            "45913": "NAICS 45913 Sewing, needlework, and piece goods retailers",
            "459130": "NAICS 459130 Sewing, needlework, and piece goods retailers",
            "45914": "NAICS 45914 Musical instrument and supplies retailers",
            "459140": "NAICS 459140 Musical instrument and supplies retailers",
            "4592": "NAICS 4592 Book retailers and news dealers",
            "45921": "NAICS 45921 Book retailers and news dealers",
            "459210": "NAICS 459210 Book retailers and news dealers",
            "4593": "NAICS 4593 Florists",
            "45931": "NAICS 45931 Florists",
            "459310": "NAICS 459310 Florists",
            "4594": "NAICS 4594 Office supplies, stationery, and gift retailers",
            "45941": "NAICS 45941 Office supplies and stationery retailers",
            "459410": "NAICS 459410 Office supplies and stationery retailers",
            "45942": "NAICS 45942 Gift, novelty, and souvenir retailers",
            "459420": "NAICS 459420 Gift, novelty, and souvenir retailers",
            "4595": "NAICS 4595 Used merchandise retailers",
            "45951": "NAICS 45951 Used merchandise retailers",
            "459510": "NAICS 459510 Used merchandise retailers",
            "4599": "NAICS 4599 Other miscellaneous retailers",
            "45991": "NAICS 45991 Pet and pet supplies retailers",
            "459910": "NAICS 459910 Pet and pet supplies retailers",
            "45992": "NAICS 45992 Art dealers",
            "459920": "NAICS 459920 Art dealers",
            "45993": "NAICS 45993 Manufactured (mobile) home dealers",
            "459930": "NAICS 459930 Manufactured (mobile) home dealers",
            "45999": "NAICS 45999 All other miscellaneous retailers",
            "459991": "NAICS 459991 Tobacco, electronic cigarette, and other smoking supplies retailers",
            "459999": "NAICS 459999 All other miscellaneous retailers",
            "481": "NAICS 481 Air transportation",
            "4811": "NAICS 4811 Scheduled air transportation",
            "48111": "NAICS 48111 Scheduled air transportation",
            "481111": "NAICS 481111 Scheduled passenger air transportation",
            "481112": "NAICS 481112 Scheduled freight air transportation",
            "4812": "NAICS 4812 Nonscheduled air transportation",
            "48121": "NAICS 48121 Nonscheduled air transportation",
            "481211": "NAICS 481211 Nonscheduled chartered passenger air transportation",
            "481212": "NAICS 481212 Nonscheduled chartered freight air transportation",
            "481219": "NAICS 481219 Other nonscheduled air transportation",
            "482": "NAICS 482 Rail transportation",
            "4821": "NAICS 4821 Rail transportation",
            "48211": "NAICS 48211 Rail transportation",
            "482111": "NAICS 482111 Line-haul railroads",
            "482112": "NAICS 482112 Short line railroads",
            "483": "NAICS 483 Water transportation",
            "4831": "NAICS 4831 Deep sea, coastal, and great lakes water transportation",
            "48311": "NAICS 48311 Deep sea, coastal, and great lakes water transportation",
            "483111": "NAICS 483111 Deep sea freight transportation",
            "483112": "NAICS 483112 Deep sea passenger transportation",
            "483113": "NAICS 483113 Coastal and great lakes freight transportation",
            "483114": "NAICS 483114 Coastal and great lakes passenger transportation",
            "4832": "NAICS 4832 Inland water transportation",
            "48321": "NAICS 48321 Inland water transportation",
            "483211": "NAICS 483211 Inland water freight transportation",
            "483212": "NAICS 483212 Inland water passenger transportation",
            "484": "NAICS 484 Truck transportation",
            "4841": "NAICS 4841 General freight trucking",
            "48411": "NAICS 48411 General freight trucking, local",
            "484110": "NAICS 484110 General freight trucking, local",
            "48412": "NAICS 48412 General freight trucking, long-distance",
            "484121": "NAICS 484121 General freight trucking, long-distance, truckload",
            "484122": "NAICS 484122 General freight trucking, long-distance, less than truckload",
            "4842": "NAICS 4842 Specialized freight trucking",
            "48421": "NAICS 48421 Used household and office goods moving",
            "484210": "NAICS 484210 Used household and office goods moving",
            "48422": "NAICS 48422 Specialized freight (except used goods) trucking, local",
            "484220": "NAICS 484220 Specialized freight (except used goods) trucking, local",
            "48423": "NAICS 48423 Specialized freight (except used goods) trucking, long-distance",
            "484230": "NAICS 484230 Specialized freight (except used goods) trucking, long-distance",
            "48-49": "NAICS 48-49 Transportation and warehousing",
            "485": "NAICS 485 Transit and ground passenger transportation",
            "4851": "NAICS 4851 Urban transit systems",
            "48511": "NAICS 48511 Urban transit systems",
            "485111": "NAICS 485111 Mixed mode transit systems",
            "485112": "NAICS 485112 Commuter rail systems",
            "485113": "NAICS 485113 Bus and other motor vehicle transit systems",
            "485119": "NAICS 485119 Other urban transit systems",
            "4852": "NAICS 4852 Interurban and rural bus transportation",
            "48521": "NAICS 48521 Interurban and rural bus transportation",
            "485210": "NAICS 485210 Interurban and rural bus transportation",
            "4853": "NAICS 4853 Taxi and limousine service",
            "48531": "NAICS 48531 Taxi and ridesharing services",
            "485310": "NAICS 485310 Taxi and ridesharing services",
            "48532": "NAICS 48532 Limousine service",
            "485320": "NAICS 485320 Limousine service",
            "4854": "NAICS 4854 School and employee bus transportation",
            "48541": "NAICS 48541 School and employee bus transportation",
            "485410": "NAICS 485410 School and employee bus transportation",
            "4855": "NAICS 4855 Charter bus industry",
            "48551": "NAICS 48551 Charter bus industry",
            "485510": "NAICS 485510 Charter bus industry",
            "4859": "NAICS 4859 Other transit and ground passenger transportation",
            "48599": "NAICS 48599 Other transit and ground passenger transportation",
            "485991": "NAICS 485991 Special needs transportation",
            "485999": "NAICS 485999 All other transit and ground passenger transportation",
            "486": "NAICS 486 Pipeline transportation",
            "4861": "NAICS 4861 Pipeline transportation of crude oil",
            "48611": "NAICS 48611 Pipeline transportation of crude oil",
            "486110": "NAICS 486110 Pipeline transportation of crude oil",
            "4862": "NAICS 4862 Pipeline transportation of natural gas",
            "48621": "NAICS 48621 Pipeline transportation of natural gas",
            "486210": "NAICS 486210 Pipeline transportation of natural gas",
            "4869": "NAICS 4869 Other pipeline transportation",
            "48691": "NAICS 48691 Pipeline transportation of refined petroleum products",
            "486910": "NAICS 486910 Pipeline transportation of refined petroleum products",
            "48699": "NAICS 48699 All other pipeline transportation",
            "486990": "NAICS 486990 All other pipeline transportation",
            "487": "NAICS 487 Scenic and sightseeing transportation",
            "4871": "NAICS 4871 Scenic and sightseeing transportation, land",
            "48711": "NAICS 48711 Scenic and sightseeing transportation, land",
            "487110": "NAICS 487110 Scenic and sightseeing transportation, land",
            "4872": "NAICS 4872 Scenic and sightseeing transportation, water",
            "48721": "NAICS 48721 Scenic and sightseeing transportation, water",
            "487210": "NAICS 487210 Scenic and sightseeing transportation, water",
            "4879": "NAICS 4879 Scenic and sightseeing transportation, other",
            "48799": "NAICS 48799 Scenic and sightseeing transportation, other",
            "487990": "NAICS 487990 Scenic and sightseeing transportation, other",
            "488": "NAICS 488 Support activities for transportation",
            "4881": "NAICS 4881 Support activities for air transportation",
            "48811": "NAICS 48811 Airport operations",
            "488111": "NAICS 488111 Air traffic control",
            "488119": "NAICS 488119 Other airport operations",
            "48819": "NAICS 48819 Other support activities for air transportation",
            "488190": "NAICS 488190 Other support activities for air transportation",
            "4882": "NAICS 4882 Support activities for rail transportation",
            "48821": "NAICS 48821 Support activities for rail transportation",
            "488210": "NAICS 488210 Support activities for rail transportation",
            "4883": "NAICS 4883 Support activities for water transportation",
            "48831": "NAICS 48831 Port and harbor operations",
            "488310": "NAICS 488310 Port and harbor operations",
            "48832": "NAICS 48832 Marine cargo handling",
            "488320": "NAICS 488320 Marine cargo handling",
            "48833": "NAICS 48833 Navigational services to shipping",
            "488330": "NAICS 488330 Navigational services to shipping",
            "48839": "NAICS 48839 Other support activities for water transportation",
            "488390": "NAICS 488390 Other support activities for water transportation",
            "4884": "NAICS 4884 Support activities for road transportation",
            "48841": "NAICS 48841 Motor vehicle towing",
            "488410": "NAICS 488410 Motor vehicle towing",
            "48849": "NAICS 48849 Other support activities for road transportation",
            "488490": "NAICS 488490 Other support activities for road transportation",
            "4885": "NAICS 4885 Freight transportation arrangement",
            "48851": "NAICS 48851 Freight transportation arrangement",
            "488510": "NAICS 488510 Freight transportation arrangement",
            "4889": "NAICS 4889 Other support activities for transportation",
            "48899": "NAICS 48899 Other support activities for transportation",
            "488991": "NAICS 488991 Packing and crating",
            "488999": "NAICS 488999 All other support activities for transportation",
            "491": "NAICS 491 Postal service",
            "4911": "NAICS 4911 Postal service",
            "49111": "NAICS 49111 Postal service",
            "491110": "NAICS 491110 Postal service",
            "492": "NAICS 492 Couriers and messengers",
            "4921": "NAICS 4921 Couriers and express delivery services",
            "49211": "NAICS 49211 Couriers and express delivery services",
            "492110": "NAICS 492110 Couriers and express delivery services",
            "4922": "NAICS 4922 Local messengers and local delivery",
            "49221": "NAICS 49221 Local messengers and local delivery",
            "492210": "NAICS 492210 Local messengers and local delivery",
            "493": "NAICS 493 Warehousing and storage",
            "4931": "NAICS 4931 Warehousing and storage",
            "49311": "NAICS 49311 General warehousing and storage",
            "493110": "NAICS 493110 General warehousing and storage",
            "49312": "NAICS 49312 Refrigerated warehousing and storage",
            "493120": "NAICS 493120 Refrigerated warehousing and storage",
            "49313": "NAICS 49313 Farm product warehousing and storage",
            "493130": "NAICS 493130 Farm product warehousing and storage",
            "49319": "NAICS 49319 Other warehousing and storage",
            "493190": "NAICS 493190 Other warehousing and storage",
            "51": "NAICS 51 Information",
            "511": "NAICS17 511 Publishing industries, except internet",
            "5111": "NAICS17 5111 Newspaper, book, and directory publishers",
            "51111": "NAICS17 51111 Newspaper publishers",
            "511110": "NAICS17 511110 Newspaper publishers",
            "51112": "NAICS17 51112 Periodical publishers",
            "511120": "NAICS17 511120 Periodical publishers",
            "51113": "NAICS17 51113 Book publishers",
            "511130": "NAICS17 511130 Book publishers",
            "51114": "NAICS17 51114 Directory and mailing list publishers",
            "511140": "NAICS17 511140 Directory and mailing list publishers",
            "51119": "NAICS17 51119 Other publishers",
            "511191": "NAICS17 511191 Greeting card publishers",
            "511199": "NAICS17 511199 All other publishers",
            "5112": "NAICS17 5112 Software publishers",
            "51121": "NAICS17 51121 Software publishers",
            "511210": "NAICS17 511210 Software publishers",
            "512": "NAICS 512 Motion picture and sound recording industries",
            "5121": "NAICS 5121 Motion picture and video industries",
            "51211": "NAICS 51211 Motion picture and video production",
            "512110": "NAICS 512110 Motion picture and video production",
            "51212": "NAICS 51212 Motion picture and video distribution",
            "512120": "NAICS 512120 Motion picture and video distribution",
            "51213": "NAICS 51213 Motion picture and video exhibition",
            "512131": "NAICS 512131 Motion picture theaters (except drive-ins)",
            "512132": "NAICS 512132 Drive-in motion picture theaters",
            "51219": "NAICS 51219 Postproduction services and other motion picture and video industries",
            "512191": "NAICS 512191 Teleproduction and other postproduction services",
            "512199": "NAICS 512199 Other motion picture and video industries",
            "5122": "NAICS 5122 Sound recording industries",
            "51221": "NAICS12 51221 Record production",
            "512210": "NAICS12 512210 Record production",
            "51222": "NAICS17 51222 Integrated record production and distribution",
            "512220": "NAICS12 512220 Integrated record production and distribution",
            "51223": "NAICS 51223 Music publishers",
            "512230": "NAICS 512230 Music publishers",
            "51224": "NAICS 51224 Sound recording studios",
            "512240": "NAICS 512240 Sound recording studios",
            "51225": "NAICS 51225 Record production and distribution",
            "512250": "NAICS 512250 Record production and distribution",
            "51229": "NAICS 51229 Other sound recording industries",
            "512290": "NAICS 512290 Other sound recording industries",
            "513": "NAICS 513 Publishing industries",
            "5131": "NAICS 5131 Newspaper, periodical, book, and directory publishers",
            "51311": "NAICS 51311 Newspaper publishers",
            "513110": "NAICS 513110 Newspaper publishers",
            "51312": "NAICS 51312 Periodical publishers",
            "513120": "NAICS 513120 Periodical publishers",
            "51313": "NAICS 51313 Book publishers",
            "513130": "NAICS 513130 Book publishers",
            "51314": "NAICS 51314 Directory and mailing list publishers",
            "513140": "NAICS 513140 Directory and mailing list publishers",
            "51319": "NAICS 51319 Other publishers",
            "513191": "NAICS 513191 Greeting card publishers",
            "513199": "NAICS 513199 All other publishers",
            "5132": "NAICS 5132 Software publishers",
            "51321": "NAICS 51321 Software publishers",
            "513210": "NAICS 513210 Software publishers",
            "515": "NAICS17 515 Broadcasting, except internet",
            "5151": "NAICS17 5151 Radio and television broadcasting",
            "51511": "NAICS17 51511 Radio broadcasting",
            "515111": "NAICS17 515111 Radio networks",
            "515112": "NAICS17 515112 Radio stations",
            "51512": "NAICS17 51512 Television broadcasting",
            "515120": "NAICS17 515120 Television broadcasting",
            "5152": "NAICS17 5152 Cable and other subscription programming",
            "51521": "NAICS17 51521 Cable and other subscription programming",
            "515210": "NAICS17 515210 Cable and other subscription programming",
            "516": "NAICS 516 Broadcasting and content providers",
            "5161": "NAICS 5161 Radio and television broadcasting stations",
            "51611": "NAICS 51611 Radio broadcasting stations",
            "516110": "NAICS 516110 Radio broadcasting stations",
            "51612": "NAICS 51612 Television broadcasting stations",
            "516120": "NAICS 516120 Television broadcasting stations",
            "5162": "NAICS 5162 Media streaming distribution services, social networks, and other media networks and content providers",
            "51621": "NAICS 51621 Media streaming distribution services, social networks, and other media networks and content providers",
            "516210": "NAICS 516210 Media streaming distribution services, social networks, and other media networks and content providers",
            "517": "NAICS 517 Telecommunications",
            "5171": "NAICS 5171 Wired and wireless telecommunications (except satellite)",
            "51711": "NAICS 51711 Wired and wireless telecommunications carriers (except satellite)",
            "517110": "NAICS12 517110 Wired telecommunications carriers",
            "517111": "NAICS 517111 Wired telecommunications carriers",
            "517112": "NAICS 517112 Wireless telecommunications carriers (except satellite)",
            "51712": "NAICS 51712 Telecommunications resellers and agents for wireless telecommunication services",
            "517121": "NAICS 517121 Telecommunications resellers",
            "5172": "NAICS12 5172 Wireless telecommunications carriers",
            "51721": "NAICS12 51721 Wireless telecommunications carriers",
            "517210": "NAICS12 517210 Wireless telecommunications carriers",
            "517211": "NAICS02 517211 Paging",
            "517212": "NAICS02 517212 Cellular and other wireless carriers",
            "5173": "NAICS17 5173 Wired and wireless telecommunications carriers",
            "51731": "NAICS17 51731 Wired and wireless telecommunications carriers",
            "517310": "NAICS02 517310 Telecommunications resellers",
            "517311": "NAICS17 517311 Wired telecommunications carriers",
            "517312": "NAICS17 517312 Wireless telecommunications carriers (except satellite)",
            "5174": "NAICS 5174 Satellite telecommunications",
            "51741": "NAICS 51741 Satellite telecommunications",
            "517410": "NAICS 517410 Satellite telecommunications",
            "5175": "NAICS02 5175 Cable and other program distribution",
            "51751": "NAICS02 51751 Cable and other program distribution",
            "517510": "NAICS02 517510 Cable and other program distribution",
            "5178": "NAICS 5178 All other telecommunications",
            "51781": "NAICS 51781 All other telecommunications",
            "517810": "NAICS 517810 All other telecommunications",
            "5179": "NAICS17 5179 Other telecommunications",
            "51791": "NAICS17 51791 Other telecommunications",
            "517910": "NAICS02 517910 Other telecommunications",
            "517911": "NAICS17 517911 Telecommunications resellers",
            "517919": "NAICS17 517919 All other telecommunications",
            "518": "NAICS 518 Computing infrastructure providers, data processing, web hosting, and related services",
            "5181": "NAICS02 5181 Isps and web search portals",
            "51811": "NAICS02 51811 Isps and web search portals",
            "518111": "NAICS02 518111 Internet service providers",
            "518112": "NAICS02 518112 Web search portals",
            "5182": "NAICS 5182 Computing infrastructure providers, data processing, web hosting, and related services",
            "51821": "NAICS 51821 Computing infrastructure providers, data processing, web hosting, and related services",
            "518210": "NAICS 518210 Computing infrastructure providers, data processing, web hosting, and related services",
            "519": "NAICS 519 Web search portals, libraries, archives, and other information services",
            "5191": "NAICS17 5191 Other information services",
            "51911": "NAICS17 51911 News syndicates",
            "519110": "NAICS17 519110 News syndicates",
            "51912": "NAICS17 51912 Libraries and archives",
            "519120": "NAICS17 519120 Libraries and archives",
            "51913": "NAICS17 51913 Internet publishing and web search portals",
            "519130": "NAICS17 519130 Internet publishing and web search portals",
            "51919": "NAICS17 51919 All other information services",
            "519190": "NAICS17 519190 All other information services",
            "5192": "NAICS 5192 Web search portals, libraries, archives, and other information services",
            "51921": "NAICS 51921 Libraries and archives",
            "519210": "NAICS 519210 Libraries and archives",
            "51929": "NAICS 51929 Web search portals and all other information services",
            "519290": "NAICS 519290 Web search portals and all other information services",
            "52": "NAICS 52 Finance and insurance",
            "521": "NAICS 521 Monetary authorities-central bank",
            "5211": "NAICS 5211 Monetary authorities-central bank",
            "52111": "NAICS 52111 Monetary authorities-central bank",
            "521110": "NAICS 521110 Monetary authorities-central bank",
            "522": "NAICS 522 Credit intermediation and related activities",
            "5221": "NAICS 5221 Depository credit intermediation",
            "52211": "NAICS 52211 Commercial banking",
            "522110": "NAICS 522110 Commercial banking",
            "52212": "NAICS17 52212 Savings institutions",
            "522120": "NAICS17 522120 Savings institutions",
            "52213": "NAICS 52213 Credit unions",
            "522130": "NAICS 522130 Credit unions",
            "52218": "NAICS 52218 Savings institutions and other depository credit intermediation",
            "522180": "NAICS 522180 Savings institutions and other depository credit intermediation",
            "52219": "NAICS17 52219 Other depository credit intermediation",
            "522190": "NAICS17 522190 Other depository credit intermediation",
            "5222": "NAICS 5222 Nondepository credit intermediation",
            "52221": "NAICS 52221 Credit card issuing",
            "522210": "NAICS 522210 Credit card issuing",
            "52222": "NAICS 52222 Sales financing",
            "522220": "NAICS 522220 Sales financing",
            "52229": "NAICS 52229 Other nondepository credit intermediation",
            "522291": "NAICS 522291 Consumer lending",
            "522292": "NAICS 522292 Real estate credit",
            "522293": "NAICS17 522293 International trade financing",
            "522294": "NAICS17 522294 Secondary market financing",
            "522298": "NAICS17 522298 All other nondepository credit intermediation",
            "522299": "NAICS 522299 International, secondary market, and all other nondepository credit intermediation",
            "5223": "NAICS 5223 Activities related to credit intermediation",
            "52231": "NAICS 52231 Mortgage and nonmortgage loan brokers",
            "522310": "NAICS 522310 Mortgage and nonmortgage loan brokers",
            "52232": "NAICS 52232 Financial transactions processing, reserve, and clearinghouse activities",
            "522320": "NAICS 522320 Financial transactions processing, reserve, and clearinghouse activities",
            "52239": "NAICS 52239 Other activities related to credit intermediation",
            "522390": "NAICS 522390 Other activities related to credit intermediation",
            "523": "NAICS 523 Securities, commodity contracts, and other financial investments and related activities",
            "5231": "NAICS 5231 Securities and commodity contracts intermediation and brokerage",
            "52311": "NAICS17 52311 Investment banking and securities dealing",
            "523110": "NAICS17 523110 Investment banking and securities dealing",
            "52312": "NAICS17 52312 Securities brokerage",
            "523120": "NAICS17 523120 Securities brokerage",
            "52313": "NAICS17 52313 Commodity contracts dealing",
            "523130": "NAICS17 523130 Commodity contracts dealing",
            "52314": "NAICS17 52314 Commodity contracts brokerage",
            "523140": "NAICS17 523140 Commodity contracts brokerage",
            "52315": "NAICS 52315 Investment banking and securities intermediation",
            "523150": "NAICS 523150 Investment banking and securities intermediation",
            "52316": "NAICS 52316 Commodity contracts intermediation",
            "523160": "NAICS 523160 Commodity contracts intermediation",
            "5232": "NAICS 5232 Securities and commodity exchanges",
            "52321": "NAICS 52321 Securities and commodity exchanges",
            "523210": "NAICS 523210 Securities and commodity exchanges",
            "5239": "NAICS 5239 Other financial investment activities",
            "52391": "NAICS 52391 Miscellaneous intermediation",
            "523910": "NAICS 523910 Miscellaneous intermediation",
            "52392": "NAICS17 52392 Portfolio management",
            "523920": "NAICS17 523920 Portfolio management",
            "52393": "NAICS17 52393 Investment advice",
            "523930": "NAICS17 523930 Investment advice",
            "52394": "NAICS 52394 Portfolio management and investment advice",
            "523940": "NAICS 523940 Portfolio management and investment advice",
            "52399": "NAICS 52399 All other financial investment activities",
            "523991": "NAICS 523991 Trust, fiduciary, and custody activities",
            "523999": "NAICS 523999 Miscellaneous financial investment activities",
            "524": "NAICS 524 Insurance carriers and related activities",
            "5241": "NAICS 5241 Insurance carriers",
            "52411": "NAICS 52411 Direct life, health, and medical insurance carriers",
            "524113": "NAICS 524113 Direct life insurance carriers",
            "524114": "NAICS 524114 Direct health and medical insurance carriers",
            "52412": "NAICS 52412 Direct insurance (except life, health, and medical) carriers",
            "524126": "NAICS 524126 Direct property and casualty insurance carriers",
            "524127": "NAICS 524127 Direct title insurance carriers",
            "524128": "NAICS 524128 Other direct insurance (except life, health, and medical) carriers",
            "52413": "NAICS 52413 Reinsurance carriers",
            "524130": "NAICS 524130 Reinsurance carriers",
            "5242": "NAICS 5242 Agencies, brokerages, and other insurance related activities",
            "52421": "NAICS 52421 Insurance agencies and brokerages",
            "524210": "NAICS 524210 Insurance agencies and brokerages",
            "52429": "NAICS 52429 Other insurance related activities",
            "524291": "NAICS 524291 Claims adjusting",
            "524292": "NAICS 524292 Pharmacy benefit management and other third party administration of insurance and pension funds",
            "524298": "NAICS 524298 All other insurance related activities",
            "525": "NAICS 525 Funds, trusts, and other financial vehicles",
            "5251": "NAICS 5251 Insurance and employee benefit funds",
            "52511": "NAICS 52511 Pension funds",
            "525110": "NAICS 525110 Pension funds",
            "52512": "NAICS 52512 Health and welfare funds",
            "525120": "NAICS 525120 Health and welfare funds",
            "52519": "NAICS 52519 Other insurance funds",
            "525190": "NAICS 525190 Other insurance funds",
            "5259": "NAICS 5259 Other investment pools and funds",
            "52591": "NAICS 52591 Open-end investment funds",
            "525910": "NAICS 525910 Open-end investment funds",
            "52592": "NAICS 52592 Trusts, estates, and agency accounts",
            "525920": "NAICS 525920 Trusts, estates, and agency accounts",
            "52593": "NAICS02 52593 Real estate investment trusts",
            "525930": "NAICS02 525930 Real estate investment trusts",
            "52599": "NAICS 52599 Other financial vehicles",
            "525990": "NAICS 525990 Other financial vehicles",
            "53": "NAICS 53 Real estate and rental and leasing",
            "531": "NAICS 531 Real estate",
            "5311": "NAICS 5311 Lessors of real estate",
            "53111": "NAICS 53111 Lessors of residential buildings and dwellings",
            "531110": "NAICS 531110 Lessors of residential buildings and dwellings",
            "53112": "NAICS 53112 Lessors of nonresidential buildings (except miniwarehouses)",
            "531120": "NAICS 531120 Lessors of nonresidential buildings (except miniwarehouses)",
            "53113": "NAICS 53113 Lessors of miniwarehouses and self-storage units",
            "531130": "NAICS 531130 Lessors of miniwarehouses and self-storage units",
            "53119": "NAICS 53119 Lessors of other real estate property",
            "531190": "NAICS 531190 Lessors of other real estate property",
            "5312": "NAICS 5312 Offices of real estate agents and brokers",
            "53121": "NAICS 53121 Offices of real estate agents and brokers",
            "531210": "NAICS 531210 Offices of real estate agents and brokers",
            "5313": "NAICS 5313 Activities related to real estate",
            "53131": "NAICS 53131 Real estate property managers",
            "531311": "NAICS 531311 Residential property managers",
            "531312": "NAICS 531312 Nonresidential property managers",
            "53132": "NAICS 53132 Offices of real estate appraisers",
            "531320": "NAICS 531320 Offices of real estate appraisers",
            "53139": "NAICS 53139 Other activities related to real estate",
            "531390": "NAICS 531390 Other activities related to real estate",
            "532": "NAICS 532 Rental and leasing services",
            "5321": "NAICS 5321 Automotive equipment rental and leasing",
            "53211": "NAICS 53211 Passenger car rental and leasing",
            "532111": "NAICS 532111 Passenger car rental",
            "532112": "NAICS 532112 Passenger car leasing",
            "53212": "NAICS 53212 Truck, utility trailer, and rv (recreational vehicle) rental and leasing",
            "532120": "NAICS 532120 Truck, utility trailer, and rv (recreational vehicle) rental and leasing",
            "5322": "NAICS 5322 Consumer goods rental",
            "53221": "NAICS 53221 Consumer electronics and appliances rental",
            "532210": "NAICS 532210 Consumer electronics and appliances rental",
            "53222": "NAICS12 53222 Formal wear and costume rental",
            "532220": "NAICS12 532220 Formal wear and costume rental",
            "53223": "NAICS17 53223 Video tape and disc rental",
            "532230": "NAICS12 532230 Video tape and disc rental",
            "53228": "NAICS 53228 Other consumer goods rental",
            "532281": "NAICS 532281 Formal wear and costume rental",
            "532282": "NAICS 532282 Video tape and disc rental",
            "532283": "NAICS 532283 Home health equipment rental",
            "532284": "NAICS 532284 Recreational goods rental",
            "532289": "NAICS 532289 All other consumer goods rental",
            "53229": "NAICS17 53229 Other consumer goods rental",
            "532291": "NAICS12 532291 Home health equipment rental",
            "532292": "NAICS12 532292 Recreational goods rental",
            "532299": "NAICS12 532299 All other consumer goods rental",
            "5323": "NAICS 5323 General rental centers",
            "53231": "NAICS 53231 General rental centers",
            "532310": "NAICS 532310 General rental centers",
            "5324": "NAICS 5324 Commercial and industrial machinery and equipment rental and leasing",
            "53241": "NAICS 53241 Construction, transportation, mining, and forestry machinery and equipment rental and leasing",
            "532411": "NAICS 532411 Commercial air, rail, and water transportation equipment rental and leasing",
            "532412": "NAICS 532412 Construction, mining, and forestry machinery and equipment rental and leasing",
            "53242": "NAICS 53242 Office machinery and equipment rental and leasing",
            "532420": "NAICS 532420 Office machinery and equipment rental and leasing",
            "53249": "NAICS 53249 Other commercial and industrial machinery and equipment rental and leasing",
            "532490": "NAICS 532490 Other commercial and industrial machinery and equipment rental and leasing",
            "533": "NAICS 533 Lessors of nonfinancial intangible assets (except copyrighted works)",
            "5331": "NAICS 5331 Lessors of nonfinancial intangible assets (except copyrighted works)",
            "53311": "NAICS 53311 Lessors of nonfinancial intangible assets (except copyrighted works)",
            "533110": "NAICS 533110 Lessors of nonfinancial intangible assets (except copyrighted works)",
            "54": "NAICS 54 Professional, scientific, and technical services",
            "541": "NAICS 541 Professional, scientific, and technical services",
            "5411": "NAICS 5411 Legal services",
            "54111": "NAICS 54111 Offices of lawyers",
            "541110": "NAICS 541110 Offices of lawyers",
            "54112": "NAICS17 54112 Offices of notaries",
            "541120": "NAICS17 541120 Offices of notaries",
            "54119": "NAICS 54119 Other legal services",
            "541191": "NAICS 541191 Title abstract and settlement offices",
            "541199": "NAICS 541199 All other legal services",
            "5412": "NAICS 5412 Accounting, tax preparation, bookkeeping, and payroll services",
            "54121": "NAICS 54121 Accounting, tax preparation, bookkeeping, and payroll services",
            "541211": "NAICS 541211 Offices of certified public accountants",
            "541213": "NAICS 541213 Tax preparation services",
            "541214": "NAICS 541214 Payroll services",
            "541219": "NAICS 541219 Other accounting services",
            "5413": "NAICS 5413 Architectural, engineering, and related services",
            "54131": "NAICS 54131 Architectural services",
            "541310": "NAICS 541310 Architectural services",
            "54132": "NAICS 54132 Landscape architectural services",
            "541320": "NAICS 541320 Landscape architectural services",
            "54133": "NAICS 54133 Engineering services",
            "541330": "NAICS 541330 Engineering services",
            "54134": "NAICS 54134 Drafting services",
            "541340": "NAICS 541340 Drafting services",
            "54135": "NAICS 54135 Building inspection services",
            "541350": "NAICS 541350 Building inspection services",
            "54136": "NAICS 54136 Geophysical surveying and mapping services",
            "541360": "NAICS 541360 Geophysical surveying and mapping services",
            "54137": "NAICS 54137 Surveying and mapping (except geophysical) services",
            "541370": "NAICS 541370 Surveying and mapping (except geophysical) services",
            "54138": "NAICS 54138 Testing laboratories and services",
            "541380": "NAICS 541380 Testing laboratories and services",
            "5414": "NAICS 5414 Specialized design services",
            "54141": "NAICS 54141 Interior design services",
            "541410": "NAICS 541410 Interior design services",
            "54142": "NAICS 54142 Industrial design services",
            "541420": "NAICS 541420 Industrial design services",
            "54143": "NAICS 54143 Graphic design services",
            "541430": "NAICS 541430 Graphic design services",
            "54149": "NAICS 54149 Other specialized design services",
            "541490": "NAICS 541490 Other specialized design services",
            "5415": "NAICS 5415 Computer systems design and related services",
            "54151": "NAICS 54151 Computer systems design and related services",
            "541511": "NAICS 541511 Custom computer programming services",
            "541512": "NAICS 541512 Computer systems design services",
            "541513": "NAICS 541513 Computer facilities management services",
            "541519": "NAICS 541519 Other computer related services",
            "5416": "NAICS 5416 Management, scientific, and technical consulting services",
            "54161": "NAICS 54161 Management consulting services",
            "541611": "NAICS 541611 Administrative management and general management consulting services",
            "541612": "NAICS 541612 Human resources consulting services",
            "541613": "NAICS 541613 Marketing consulting services",
            "541614": "NAICS 541614 Process, physical distribution, and logistics consulting services",
            "541618": "NAICS 541618 Other management consulting services",
            "54162": "NAICS 54162 Environmental consulting services",
            "541620": "NAICS 541620 Environmental consulting services",
            "54169": "NAICS 54169 Other scientific and technical consulting services",
            "541690": "NAICS 541690 Other scientific and technical consulting services",
            "5417": "NAICS 5417 Scientific research and development services",
            "54171": "NAICS 54171 Research and development in the physical, engineering, and life sciences",
            "541710": "NAICS02 541710 Physical, engineering and biological research",
            "541711": "NAICS12 541711 Research and development in biotechnology",
            "541712": "NAICS12 541712 Other physical and biological research",
            "541713": "NAICS 541713 Research and development in nanotechnology",
            "541714": "NAICS 541714 Research and development in biotechnology (except nanobiotechnology)",
            "541715": "NAICS 541715 Research and development in the physical, engineering, and life sciences (except nanotechnology and biotechnology)",
            "54172": "NAICS 54172 Research and development in the social sciences and humanities",
            "541720": "NAICS 541720 Research and development in the social sciences and humanities",
            "5418": "NAICS 5418 Advertising, public relations, and related services",
            "54181": "NAICS 54181 Advertising agencies",
            "541810": "NAICS 541810 Advertising agencies",
            "54182": "NAICS 54182 Public relations agencies",
            "541820": "NAICS 541820 Public relations agencies",
            "54183": "NAICS 54183 Media buying agencies",
            "541830": "NAICS 541830 Media buying agencies",
            "54184": "NAICS 54184 Media representatives",
            "541840": "NAICS 541840 Media representatives",
            "54185": "NAICS 54185 Indoor and outdoor display advertising",
            "541850": "NAICS 541850 Indoor and outdoor display advertising",
            "54186": "NAICS 54186 Direct mail advertising",
            "541860": "NAICS 541860 Direct mail advertising",
            "54187": "NAICS 54187 Advertising material distribution services",
            "541870": "NAICS 541870 Advertising material distribution services",
            "54189": "NAICS 54189 Other services related to advertising",
            "541890": "NAICS 541890 Other services related to advertising",
            "5419": "NAICS 5419 Other professional, scientific, and technical services",
            "54191": "NAICS 54191 Marketing research and public opinion polling",
            "541910": "NAICS 541910 Marketing research and public opinion polling",
            "54192": "NAICS 54192 Photographic services",
            "541921": "NAICS 541921 Photography studios, portrait",
            "541922": "NAICS 541922 Commercial photography",
            "54193": "NAICS 54193 Translation and interpretation services",
            "541930": "NAICS 541930 Translation and interpretation services",
            "54194": "NAICS 54194 Veterinary services",
            "541940": "NAICS 541940 Veterinary services",
            "54199": "NAICS 54199 All other professional, scientific, and technical services",
            "541990": "NAICS 541990 All other professional, scientific, and technical services",
            "55": "NAICS 55 Management of companies and enterprises",
            "551": "NAICS 551 Management of companies and enterprises",
            "5511": "NAICS 5511 Management of companies and enterprises",
            "55111": "NAICS 55111 Management of companies and enterprises",
            "551111": "NAICS 551111 Offices of bank holding companies",
            "551112": "NAICS 551112 Offices of other holding companies",
            "551114": "NAICS 551114 Corporate, subsidiary, and regional managing offices",
            "56": "NAICS 56 Administrative and support and waste management and remediation services",
            "561": "NAICS 561 Administrative and support services",
            "5611": "NAICS 5611 Office administrative services",
            "56111": "NAICS 56111 Office administrative services",
            "561110": "NAICS 561110 Office administrative services",
            "5612": "NAICS 5612 Facilities support services",
            "56121": "NAICS 56121 Facilities support services",
            "561210": "NAICS 561210 Facilities support services",
            "5613": "NAICS 5613 Employment services",
            "56131": "NAICS 56131 Employment placement agencies and executive search services",
            "561310": "NAICS02 561310 Employment placement agencies",
            "561311": "NAICS 561311 Employment placement agencies",
            "561312": "NAICS 561312 Executive search services",
            "56132": "NAICS 56132 Temporary help services",
            "561320": "NAICS 561320 Temporary help services",
            "56133": "NAICS 56133 Professional employer organizations",
            "561330": "NAICS 561330 Professional employer organizations",
            "5614": "NAICS 5614 Business support services",
            "56141": "NAICS 56141 Document preparation services",
            "561410": "NAICS 561410 Document preparation services",
            "56142": "NAICS 56142 Telephone call centers",
            "561421": "NAICS 561421 Telephone answering services",
            "561422": "NAICS 561422 Telemarketing bureaus and other contact centers",
            "56143": "NAICS 56143 Business service centers",
            "561431": "NAICS 561431 Private mail centers",
            "561439": "NAICS 561439 Other business service centers (including copy shops)",
            "56144": "NAICS 56144 Collection agencies",
            "561440": "NAICS 561440 Collection agencies",
            "56145": "NAICS 56145 Credit bureaus",
            "561450": "NAICS 561450 Credit bureaus",
            "56149": "NAICS 56149 Other business support services",
            "561491": "NAICS 561491 Repossession services",
            "561492": "NAICS 561492 Court reporting and stenotype services",
            "561499": "NAICS 561499 All other business support services",
            "5615": "NAICS 5615 Travel arrangement and reservation services",
            "56151": "NAICS 56151 Travel agencies",
            "561510": "NAICS 561510 Travel agencies",
            "56152": "NAICS 56152 Tour operators",
            "561520": "NAICS 561520 Tour operators",
            "56159": "NAICS 56159 Other travel arrangement and reservation services",
            "561591": "NAICS 561591 Convention and visitors bureaus",
            "561599": "NAICS 561599 All other travel arrangement and reservation services",
            "5616": "NAICS 5616 Investigation and security services",
            "56161": "NAICS 56161 Investigation, guard, and armored car services",
            "561611": "NAICS 561611 Investigation and personal background check services",
            "561612": "NAICS 561612 Security guards and patrol services",
            "561613": "NAICS 561613 Armored car services",
            "56162": "NAICS 56162 Security systems services",
            "561621": "NAICS 561621 Security systems services (except locksmiths)",
            "561622": "NAICS 561622 Locksmiths",
            "5617": "NAICS 5617 Services to buildings and dwellings",
            "56171": "NAICS 56171 Exterminating and pest control services",
            "561710": "NAICS 561710 Exterminating and pest control services",
            "56172": "NAICS 56172 Janitorial services",
            "561720": "NAICS 561720 Janitorial services",
            "56173": "NAICS 56173 Landscaping services",
            "561730": "NAICS 561730 Landscaping services",
            "56174": "NAICS 56174 Carpet and upholstery cleaning services",
            "561740": "NAICS 561740 Carpet and upholstery cleaning services",
            "56179": "NAICS 56179 Other services to buildings and dwellings",
            "561790": "NAICS 561790 Other services to buildings and dwellings",
            "5619": "NAICS 5619 Other support services",
            "56191": "NAICS 56191 Packaging and labeling services",
            "561910": "NAICS 561910 Packaging and labeling services",
            "56192": "NAICS 56192 Convention and trade show organizers",
            "561920": "NAICS 561920 Convention and trade show organizers",
            "56199": "NAICS 56199 All other support services",
            "561990": "NAICS 561990 All other support services",
            "562": "NAICS 562 Waste management and remediation services",
            "5621": "NAICS 5621 Waste collection",
            "56211": "NAICS 56211 Waste collection",
            "562111": "NAICS 562111 Solid waste collection",
            "562112": "NAICS 562112 Hazardous waste collection",
            "562119": "NAICS 562119 Other waste collection",
            "5622": "NAICS 5622 Waste treatment and disposal",
            "56221": "NAICS 56221 Waste treatment and disposal",
            "562211": "NAICS 562211 Hazardous waste treatment and disposal",
            "562212": "NAICS 562212 Solid waste landfill",
            "562213": "NAICS 562213 Solid waste combustors and incinerators",
            "562219": "NAICS 562219 Other nonhazardous waste treatment and disposal",
            "5629": "NAICS 5629 Remediation and other waste management services",
            "56291": "NAICS 56291 Remediation services",
            "562910": "NAICS 562910 Remediation services",
            "56292": "NAICS 56292 Materials recovery facilities",
            "562920": "NAICS 562920 Materials recovery facilities",
            "56299": "NAICS 56299 All other waste management services",
            "562991": "NAICS 562991 Septic tank and related services",
            "562998": "NAICS 562998 All other miscellaneous waste management services",
            "61": "NAICS 61 Educational services",
            "611": "NAICS 611 Educational services",
            "6111": "NAICS 6111 Elementary and secondary schools",
            "61111": "NAICS 61111 Elementary and secondary schools",
            "611110": "NAICS 611110 Elementary and secondary schools",
            "6112": "NAICS 6112 Junior colleges",
            "61121": "NAICS 61121 Junior colleges",
            "611210": "NAICS 611210 Junior colleges",
            "6113": "NAICS 6113 Colleges, universities, and professional schools",
            "61131": "NAICS 61131 Colleges, universities, and professional schools",
            "611310": "NAICS 611310 Colleges, universities, and professional schools",
            "6114": "NAICS 6114 Business schools and computer and management training",
            "61141": "NAICS 61141 Business and secretarial schools",
            "611410": "NAICS 611410 Business and secretarial schools",
            "61142": "NAICS 61142 Computer training",
            "611420": "NAICS 611420 Computer training",
            "61143": "NAICS 61143 Professional and management development training",
            "611430": "NAICS 611430 Professional and management development training",
            "6115": "NAICS 6115 Technical and trade schools",
            "61151": "NAICS 61151 Technical and trade schools",
            "611511": "NAICS 611511 Cosmetology and barber schools",
            "611512": "NAICS 611512 Flight training",
            "611513": "NAICS 611513 Apprenticeship training",
            "611519": "NAICS 611519 Other technical and trade schools",
            "6116": "NAICS 6116 Other schools and instruction",
            "61161": "NAICS 61161 Fine arts schools",
            "611610": "NAICS 611610 Fine arts schools",
            "61162": "NAICS 61162 Sports and recreation instruction",
            "611620": "NAICS 611620 Sports and recreation instruction",
            "61163": "NAICS 61163 Language schools",
            "611630": "NAICS 611630 Language schools",
            "61169": "NAICS 61169 All other schools and instruction",
            "611691": "NAICS 611691 Exam preparation and tutoring",
            "611692": "NAICS 611692 Automobile driving schools",
            "611699": "NAICS 611699 All other miscellaneous schools and instruction",
            "6117": "NAICS 6117 Educational support services",
            "61171": "NAICS 61171 Educational support services",
            "611710": "NAICS 611710 Educational support services",
            "62": "NAICS 62 Health care and social assistance",
            "621": "NAICS 621 Ambulatory health care services",
            "6211": "NAICS 6211 Offices of physicians",
            "62111": "NAICS 62111 Offices of physicians",
            "621111": "NAICS 621111 Offices of physicians (except mental health specialists)",
            "621112": "NAICS 621112 Offices of physicians, mental health specialists",
            "6212": "NAICS 6212 Offices of dentists",
            "62121": "NAICS 62121 Offices of dentists",
            "621210": "NAICS 621210 Offices of dentists",
            "6213": "NAICS 6213 Offices of other health practitioners",
            "62131": "NAICS 62131 Offices of chiropractors",
            "621310": "NAICS 621310 Offices of chiropractors",
            "62132": "NAICS 62132 Offices of optometrists",
            "621320": "NAICS 621320 Offices of optometrists",
            "62133": "NAICS 62133 Offices of mental health practitioners (except physicians)",
            "621330": "NAICS 621330 Offices of mental health practitioners (except physicians)",
            "62134": "NAICS 62134 Offices of physical, occupational and speech therapists, and audiologists",
            "621340": "NAICS 621340 Offices of physical, occupational and speech therapists, and audiologists",
            "62139": "NAICS 62139 Offices of all other health practitioners",
            "621391": "NAICS 621391 Offices of podiatrists",
            "621399": "NAICS 621399 Offices of all other miscellaneous health practitioners",
            "6214": "NAICS 6214 Outpatient care centers",
            "62141": "NAICS 62141 Family planning centers",
            "621410": "NAICS 621410 Family planning centers",
            "62142": "NAICS 62142 Outpatient mental health and substance abuse centers",
            "621420": "NAICS 621420 Outpatient mental health and substance abuse centers",
            "62149": "NAICS 62149 Other outpatient care centers",
            "621491": "NAICS 621491 Hmo medical centers",
            "621492": "NAICS 621492 Kidney dialysis centers",
            "621493": "NAICS 621493 Freestanding ambulatory surgical and emergency centers",
            "621498": "NAICS 621498 All other outpatient care centers",
            "6215": "NAICS 6215 Medical and diagnostic laboratories",
            "62151": "NAICS 62151 Medical and diagnostic laboratories",
            "621511": "NAICS 621511 Medical laboratories",
            "621512": "NAICS 621512 Diagnostic imaging centers",
            "6216": "NAICS 6216 Home health care services",
            "62161": "NAICS 62161 Home health care services",
            "621610": "NAICS 621610 Home health care services",
            "6219": "NAICS 6219 Other ambulatory health care services",
            "62191": "NAICS 62191 Ambulance services",
            "621910": "NAICS 621910 Ambulance services",
            "62199": "NAICS 62199 All other ambulatory health care services",
            "621991": "NAICS 621991 Blood and organ banks",
            "621999": "NAICS 621999 All other miscellaneous ambulatory health care services",
            "622": "NAICS 622 Hospitals",
            "6221": "NAICS 6221 General medical and surgical hospitals",
            "62211": "NAICS 62211 General medical and surgical hospitals",
            "622110": "NAICS 622110 General medical and surgical hospitals",
            "6222": "NAICS 6222 Psychiatric and substance abuse hospitals",
            "62221": "NAICS 62221 Psychiatric and substance abuse hospitals",
            "622210": "NAICS 622210 Psychiatric and substance abuse hospitals",
            "6223": "NAICS 6223 Specialty (except psychiatric and substance abuse) hospitals",
            "62231": "NAICS 62231 Specialty (except psychiatric and substance abuse) hospitals",
            "622310": "NAICS 622310 Specialty (except psychiatric and substance abuse) hospitals",
            "623": "NAICS 623 Nursing and residential care facilities",
            "6231": "NAICS 6231 Nursing care facilities (skilled nursing facilities)",
            "62311": "NAICS 62311 Nursing care facilities (skilled nursing facilities)",
            "623110": "NAICS 623110 Nursing care facilities (skilled nursing facilities)",
            "6232": "NAICS 6232 Residential intellectual and developmental disability, mental health, and substance abuse facilities",
            "62321": "NAICS 62321 Residential intellectual and developmental disability facilities",
            "623210": "NAICS 623210 Residential intellectual and developmental disability facilities",
            "62322": "NAICS 62322 Residential mental health and substance abuse facilities",
            "623220": "NAICS 623220 Residential mental health and substance abuse facilities",
            "6233": "NAICS 6233 Continuing care retirement communities and assisted living facilities for the elderly",
            "62331": "NAICS 62331 Continuing care retirement communities and assisted living facilities for the elderly",
            "623311": "NAICS 623311 Continuing care retirement communities",
            "623312": "NAICS 623312 Assisted living facilities for the elderly",
            "6239": "NAICS 6239 Other residential care facilities",
            "62399": "NAICS 62399 Other residential care facilities",
            "623990": "NAICS 623990 Other residential care facilities",
            "624": "NAICS 624 Social assistance",
            "6241": "NAICS 6241 Individual and family services",
            "62411": "NAICS 62411 Child and youth services",
            "624110": "NAICS 624110 Child and youth services",
            "62412": "NAICS 62412 Services for the elderly and persons with disabilities",
            "624120": "NAICS 624120 Services for the elderly and persons with disabilities",
            "62419": "NAICS 62419 Other individual and family services",
            "624190": "NAICS 624190 Other individual and family services",
            "6242": "NAICS 6242 Community food and housing, and emergency and other relief services",
            "62421": "NAICS 62421 Community food services",
            "624210": "NAICS 624210 Community food services",
            "62422": "NAICS 62422 Community housing services",
            "624221": "NAICS 624221 Temporary shelters",
            "624229": "NAICS 624229 Other community housing services",
            "62423": "NAICS 62423 Emergency and other relief services",
            "624230": "NAICS 624230 Emergency and other relief services",
            "6243": "NAICS 6243 Vocational rehabilitation services",
            "62431": "NAICS 62431 Vocational rehabilitation services",
            "624310": "NAICS 624310 Vocational rehabilitation services",
            "6244": "NAICS 6244 Child care services",
            "62441": "NAICS 62441 Child care services",
            "624410": "NAICS 624410 Child care services",
            "71": "NAICS 71 Arts, entertainment, and recreation",
            "711": "NAICS 711 Performing arts, spectator sports, and related industries",
            "7111": "NAICS 7111 Performing arts companies",
            "71111": "NAICS 71111 Theater companies and dinner theaters",
            "711110": "NAICS 711110 Theater companies and dinner theaters",
            "71112": "NAICS 71112 Dance companies",
            "711120": "NAICS 711120 Dance companies",
            "71113": "NAICS 71113 Musical groups and artists",
            "711130": "NAICS 711130 Musical groups and artists",
            "71119": "NAICS 71119 Other performing arts companies",
            "711190": "NAICS 711190 Other performing arts companies",
            "7112": "NAICS 7112 Spectator sports",
            "71121": "NAICS 71121 Spectator sports",
            "711211": "NAICS 711211 Sports teams and clubs",
            "711212": "NAICS 711212 Racetracks",
            "711219": "NAICS 711219 Other spectator sports",
            "7113": "NAICS 7113 Promoters of performing arts, sports, and similar events",
            "71131": "NAICS 71131 Promoters of performing arts, sports, and similar events with facilities",
            "711310": "NAICS 711310 Promoters of performing arts, sports, and similar events with facilities",
            "71132": "NAICS 71132 Promoters of performing arts, sports, and similar events without facilities",
            "711320": "NAICS 711320 Promoters of performing arts, sports, and similar events without facilities",
            "7114": "NAICS 7114 Agents and managers for artists, athletes, entertainers, and other public figures",
            "71141": "NAICS 71141 Agents and managers for artists, athletes, entertainers, and other public figures",
            "711410": "NAICS 711410 Agents and managers for artists, athletes, entertainers, and other public figures",
            "7115": "NAICS 7115 Independent artists, writers, and performers",
            "71151": "NAICS 71151 Independent artists, writers, and performers",
            "711510": "NAICS 711510 Independent artists, writers, and performers",
            "712": "NAICS 712 Museums, historical sites, and similar institutions",
            "7121": "NAICS 7121 Museums, historical sites, and similar institutions",
            "71211": "NAICS 71211 Museums",
            "712110": "NAICS 712110 Museums",
            "71212": "NAICS 71212 Historical sites",
            "712120": "NAICS 712120 Historical sites",
            "71213": "NAICS 71213 Zoos and botanical gardens",
            "712130": "NAICS 712130 Zoos and botanical gardens",
            "71219": "NAICS 71219 Nature parks and other similar institutions",
            "712190": "NAICS 712190 Nature parks and other similar institutions",
            "713": "NAICS 713 Amusement, gambling, and recreation industries",
            "7131": "NAICS 7131 Amusement parks and arcades",
            "71311": "NAICS 71311 Amusement and theme parks",
            "713110": "NAICS 713110 Amusement and theme parks",
            "71312": "NAICS 71312 Amusement arcades",
            "713120": "NAICS 713120 Amusement arcades",
            "7132": "NAICS 7132 Gambling industries",
            "71321": "NAICS 71321 Casinos (except casino hotels)",
            "713210": "NAICS 713210 Casinos (except casino hotels)",
            "71329": "NAICS 71329 Other gambling industries",
            "713290": "NAICS 713290 Other gambling industries",
            "7139": "NAICS 7139 Other amusement and recreation industries",
            "71391": "NAICS 71391 Golf courses and country clubs",
            "713910": "NAICS 713910 Golf courses and country clubs",
            "71392": "NAICS 71392 Skiing facilities",
            "713920": "NAICS 713920 Skiing facilities",
            "71393": "NAICS 71393 Marinas",
            "713930": "NAICS 713930 Marinas",
            "71394": "NAICS 71394 Fitness and recreational sports centers",
            "713940": "NAICS 713940 Fitness and recreational sports centers",
            "71395": "NAICS 71395 Bowling centers",
            "713950": "NAICS 713950 Bowling centers",
            "71399": "NAICS 71399 All other amusement and recreation industries",
            "713990": "NAICS 713990 All other amusement and recreation industries",
            "72": "NAICS 72 Accommodation and food services",
            "721": "NAICS 721 Accommodation",
            "7211": "NAICS 7211 Traveler accommodation",
            "72111": "NAICS 72111 Hotels (except casino hotels) and motels",
            "721110": "NAICS 721110 Hotels (except casino hotels) and motels",
            "72112": "NAICS 72112 Casino hotels",
            "721120": "NAICS 721120 Casino hotels",
            "72119": "NAICS 72119 Other traveler accommodation",
            "721191": "NAICS 721191 Bed-and-breakfast inns",
            "721199": "NAICS 721199 All other traveler accommodation",
            "7212": "NAICS 7212 Rv (recreational vehicle) parks and recreational camps",
            "72121": "NAICS 72121 Rv (recreational vehicle) parks and recreational camps",
            "721211": "NAICS 721211 Rv (recreational vehicle) parks and campgrounds",
            "721214": "NAICS 721214 Recreational and vacation camps (except campgrounds)",
            "7213": "NAICS 7213 Rooming and boarding houses, dormitories, and workers' camps",
            "72131": "NAICS 72131 Rooming and boarding houses, dormitories, and workers' camps",
            "721310": "NAICS 721310 Rooming and boarding houses, dormitories, and workers' camps",
            "722": "NAICS 722 Food services and drinking places",
            "7221": "NAICS07 7221 Full-service restaurants",
            "72211": "NAICS07 72211 Full-service restaurants",
            "722110": "NAICS07 722110 Full-service restaurants",
            "7222": "NAICS07 7222 Limited-service eating places",
            "72221": "NAICS07 72221 Limited-service eating places",
            "722211": "NAICS07 722211 Limited-service restaurants",
            "722212": "NAICS07 722212 Cafeterias, grill buffets, and buffets",
            "722213": "NAICS07 722213 Snack and nonalcoholic beverage bars",
            "7223": "NAICS 7223 Special food services",
            "72231": "NAICS 72231 Food service contractors",
            "722310": "NAICS 722310 Food service contractors",
            "72232": "NAICS 72232 Caterers",
            "722320": "NAICS 722320 Caterers",
            "72233": "NAICS 72233 Mobile food services",
            "722330": "NAICS 722330 Mobile food services",
            "7224": "NAICS 7224 Drinking places (alcoholic beverages)",
            "72241": "NAICS 72241 Drinking places (alcoholic beverages)",
            "722410": "NAICS 722410 Drinking places (alcoholic beverages)",
            "7225": "NAICS 7225 Restaurants and other eating places",
            "72251": "NAICS 72251 Restaurants and other eating places",
            "722511": "NAICS 722511 Full-service restaurants",
            "722513": "NAICS 722513 Limited-service restaurants",
            "722514": "NAICS 722514 Cafeterias, grill buffets, and buffets",
            "722515": "NAICS 722515 Snack and nonalcoholic beverage bars",
            "81": "NAICS 81 Other services (except public administration)",
            "811": "NAICS 811 Repair and maintenance",
            "8111": "NAICS 8111 Automotive repair and maintenance",
            "81111": "NAICS 81111 Automotive mechanical and electrical repair and maintenance",
            "811111": "NAICS 811111 General automotive repair",
            "811112": "NAICS17 811112 Automotive exhaust system repair",
            "811113": "NAICS17 811113 Automotive transmission repair",
            "811114": "NAICS 811114 Specialized automotive repair",
            "811118": "NAICS17 811118 Other automotive mechanical and elec. repair",
            "81112": "NAICS 81112 Automotive body, paint, interior, and glass repair",
            "811121": "NAICS 811121 Automotive body, paint, and interior repair and maintenance",
            "811122": "NAICS 811122 Automotive glass replacement shops",
            "81119": "NAICS 81119 Other automotive repair and maintenance",
            "811191": "NAICS 811191 Automotive oil change and lubrication shops",
            "811192": "NAICS 811192 Car washes",
            "811198": "NAICS 811198 All other automotive repair and maintenance",
            "8112": "NAICS 8112 Electronic and precision equipment repair and maintenance",
            "81121": "NAICS 81121 Electronic and precision equipment repair and maintenance",
            "811210": "NAICS 811210 Electronic and precision equipment repair and maintenance",
            "811211": "NAICS17 811211 Consumer electronics repair and maintenance",
            "811212": "NAICS17 811212 Computer and office machine repair",
            "811213": "NAICS17 811213 Communication equipment repair",
            "811219": "NAICS17 811219 Other electronic equipment repair",
            "8113": "NAICS 8113 Commercial and industrial machinery and equipment (except automotive and electronic) repair and maintenance",
            "81131": "NAICS 81131 Commercial and industrial machinery and equipment (except automotive and electronic) repair and maintenance",
            "811310": "NAICS 811310 Commercial and industrial machinery and equipment (except automotive and electronic) repair and maintenance",
            "8114": "NAICS 8114 Personal and household goods repair and maintenance",
            "81141": "NAICS 81141 Home and garden equipment and appliance repair and maintenance",
            "811411": "NAICS 811411 Home and garden equipment repair and maintenance",
            "811412": "NAICS 811412 Appliance repair and maintenance",
            "81142": "NAICS 81142 Reupholstery and furniture repair",
            "811420": "NAICS 811420 Reupholstery and furniture repair",
            "81143": "NAICS 81143 Footwear and leather goods repair",
            "811430": "NAICS 811430 Footwear and leather goods repair",
            "81149": "NAICS 81149 Other personal and household goods repair and maintenance",
            "811490": "NAICS 811490 Other personal and household goods repair and maintenance",
            "812": "NAICS 812 Personal and laundry services",
            "8121": "NAICS 8121 Personal care services",
            "81211": "NAICS 81211 Hair, nail, and skin care services",
            "812111": "NAICS 812111 Barber shops",
            "812112": "NAICS 812112 Beauty salons",
            "812113": "NAICS 812113 Nail salons",
            "81219": "NAICS 81219 Other personal care services",
            "812191": "NAICS 812191 Diet and weight reducing centers",
            "812199": "NAICS 812199 Other personal care services",
            "8122": "NAICS 8122 Death care services",
            "81221": "NAICS 81221 Funeral homes and funeral services",
            "812210": "NAICS 812210 Funeral homes and funeral services",
            "81222": "NAICS 81222 Cemeteries and crematories",
            "812220": "NAICS 812220 Cemeteries and crematories",
            "8123": "NAICS 8123 Drycleaning and laundry services",
            "81231": "NAICS 81231 Coin-operated laundries and drycleaners",
            "812310": "NAICS 812310 Coin-operated laundries and drycleaners",
            "81232": "NAICS 81232 Drycleaning and laundry services (except coin-operated)",
            "812320": "NAICS 812320 Drycleaning and laundry services (except coin-operated)",
            "81233": "NAICS 81233 Linen and uniform supply",
            "812331": "NAICS 812331 Linen supply",
            "812332": "NAICS 812332 Industrial launderers",
            "8129": "NAICS 8129 Other personal services",
            "81291": "NAICS 81291 Pet care (except veterinary) services",
            "812910": "NAICS 812910 Pet care (except veterinary) services",
            "81292": "NAICS 81292 Photofinishing",
            "812921": "NAICS 812921 Photofinishing laboratories (except one-hour)",
            "812922": "NAICS 812922 One-hour photofinishing",
            "81293": "NAICS 81293 Parking lots and garages",
            "812930": "NAICS 812930 Parking lots and garages",
            "81299": "NAICS 81299 All other personal services",
            "812990": "NAICS 812990 All other personal services",
            "813": "NAICS 813 Religious, grantmaking, civic, professional, and similar organizations",
            "8131": "NAICS 8131 Religious organizations",
            "81311": "NAICS 81311 Religious organizations",
            "813110": "NAICS 813110 Religious organizations",
            "8132": "NAICS 8132 Grantmaking and giving services",
            "81321": "NAICS 81321 Grantmaking and giving services",
            "813211": "NAICS 813211 Grantmaking foundations",
            "813212": "NAICS 813212 Voluntary health organizations",
            "813219": "NAICS 813219 Other grantmaking and giving services",
            "8133": "NAICS 8133 Social advocacy organizations",
            "81331": "NAICS 81331 Social advocacy organizations",
            "813311": "NAICS 813311 Human rights organizations",
            "813312": "NAICS 813312 Environment, conservation and wildlife organizations",
            "813319": "NAICS 813319 Other social advocacy organizations",
            "8134": "NAICS 8134 Civic and social organizations",
            "81341": "NAICS 81341 Civic and social organizations",
            "813410": "NAICS 813410 Civic and social organizations",
            "8139": "NAICS 8139 Business, professional, labor, political, and similar organizations",
            "81391": "NAICS 81391 Business associations",
            "813910": "NAICS 813910 Business associations",
            "81392": "NAICS 81392 Professional organizations",
            "813920": "NAICS 813920 Professional organizations",
            "81393": "NAICS 81393 Labor unions and similar labor organizations",
            "813930": "NAICS 813930 Labor unions and similar labor organizations",
            "81394": "NAICS 81394 Political organizations",
            "813940": "NAICS 813940 Political organizations",
            "81399": "NAICS 81399 Other similar organizations (except business, professional, labor, and political organizations)",
            "813990": "NAICS 813990 Other similar organizations (except business, professional, labor, and political organizations)",
            "814": "NAICS 814 Private households",
            "8141": "NAICS 8141 Private households",
            "81411": "NAICS 81411 Private households",
            "814110": "NAICS 814110 Private households",
            "92": "NAICS 92 Public administration",
            "921": "NAICS 921 Executive, legislative, and other general government support",
            "9211": "NAICS 9211 Executive, legislative, and other general government support",
            "92111": "NAICS 92111 Executive offices",
            "921110": "NAICS 921110 Executive offices",
            "92112": "NAICS 92112 Legislative bodies",
            "921120": "NAICS 921120 Legislative bodies",
            "92113": "NAICS 92113 Public finance activities",
            "921130": "NAICS 921130 Public finance activities",
            "92114": "NAICS 92114 Executive and legislative offices, combined",
            "921140": "NAICS 921140 Executive and legislative offices, combined",
            "92115": "NAICS 92115 American indian and alaska native tribal governments",
            "921150": "NAICS 921150 American indian and alaska native tribal governments",
            "92119": "NAICS 92119 Other general government support",
            "921190": "NAICS 921190 Other general government support",
            "922": "NAICS 922 Justice, public order, and safety activities",
            "9221": "NAICS 9221 Justice, public order, and safety activities",
            "92211": "NAICS 92211 Courts",
            "922110": "NAICS 922110 Courts",
            "92212": "NAICS 92212 Police protection",
            "922120": "NAICS 922120 Police protection",
            "92213": "NAICS 92213 Legal counsel and prosecution",
            "922130": "NAICS 922130 Legal counsel and prosecution",
            "92214": "NAICS 92214 Correctional institutions",
            "922140": "NAICS 922140 Correctional institutions",
            "92215": "NAICS 92215 Parole offices and probation offices",
            "922150": "NAICS 922150 Parole offices and probation offices",
            "92216": "NAICS 92216 Fire protection",
            "922160": "NAICS 922160 Fire protection",
            "92219": "NAICS 92219 Other justice, public order, and safety activities",
            "922190": "NAICS 922190 Other justice, public order, and safety activities",
            "923": "NAICS 923 Administration of human resource programs",
            "9231": "NAICS 9231 Administration of human resource programs",
            "92311": "NAICS 92311 Administration of education programs",
            "923110": "NAICS 923110 Administration of education programs",
            "92312": "NAICS 92312 Administration of public health programs",
            "923120": "NAICS 923120 Administration of public health programs",
            "92313": "NAICS 92313 Administration of human resource programs (except education, public health, and veterans' affairs programs)",
            "923130": "NAICS 923130 Administration of human resource programs (except education, public health, and veterans' affairs programs)",
            "92314": "NAICS 92314 Administration of veterans' affairs",
            "923140": "NAICS 923140 Administration of veterans' affairs",
            "924": "NAICS 924 Administration of environmental quality programs",
            "9241": "NAICS 9241 Administration of environmental quality programs",
            "92411": "NAICS 92411 Administration of air and water resource and solid waste management programs",
            "924110": "NAICS 924110 Administration of air and water resource and solid waste management programs",
            "92412": "NAICS 92412 Administration of conservation programs",
            "924120": "NAICS 924120 Administration of conservation programs",
            "925": "NAICS 925 Administration of housing programs, urban planning, and community development",
            "9251": "NAICS 9251 Administration of housing programs, urban planning, and community development",
            "92511": "NAICS 92511 Administration of housing programs",
            "925110": "NAICS 925110 Administration of housing programs",
            "92512": "NAICS 92512 Administration of urban planning and community and rural development",
            "925120": "NAICS 925120 Administration of urban planning and community and rural development",
            "926": "NAICS 926 Administration of economic programs",
            "9261": "NAICS 9261 Administration of economic programs",
            "92611": "NAICS 92611 Administration of general economic programs",
            "926110": "NAICS 926110 Administration of general economic programs",
            "92612": "NAICS 92612 Regulation and administration of transportation programs",
            "926120": "NAICS 926120 Regulation and administration of transportation programs",
            "92613": "NAICS 92613 Regulation and administration of communications, electric, gas, and other utilities",
            "926130": "NAICS 926130 Regulation and administration of communications, electric, gas, and other utilities",
            "92614": "NAICS 92614 Regulation of agricultural marketing and commodities",
            "926140": "NAICS 926140 Regulation of agricultural marketing and commodities",
            "92615": "NAICS 92615 Regulation, licensing, and inspection of miscellaneous commercial sectors",
            "926150": "NAICS 926150 Regulation, licensing, and inspection of miscellaneous commercial sectors",
            "927": "NAICS 927 Space research and technology",
            "9271": "NAICS 9271 Space research and technology",
            "92711": "NAICS 92711 Space research and technology",
            "927110": "NAICS 927110 Space research and technology",
            "928": "NAICS 928 National security and international affairs",
            "9281": "NAICS 9281 National security and international affairs",
            "92811": "NAICS 92811 National security",
            "928110": "NAICS 928110 National security",
            "92812": "NAICS 92812 International affairs",
            "928120": "NAICS 928120 International affairs",
            "99": "NAICS 99 Unclassified",
            "999": "NAICS 999 Unclassified",
            "9999": "NAICS 9999 Unclassified",
            "99999": "NAICS 99999 Unclassified",
            "999999": "NAICS 999999 Unclassified"
        }

        self.AGGLEVEL_CODES = AGGLEVEL_CODES
        self.INDUSTRY_CODES = INDUSTRY_CODES

    def clean_industry_titles(self):
        """
        Return a version of morpc.bls.INDUSTRY_CODES in which the dictionary values (industry titles) have been stripped of the prefix
        containing the industry code.
        
        Rationale: The raw industry titles have a prefix with the NAICS code embedded in them.  The industry code may already be captured elsewhere
        (say another column of a dataframe), in which case these prefixes are redundant.  Unfortunately, there are no delimiters that we can use to
        separate the prefix from the actual title, so this function uses a regular expression.  The regular expression looks for the following patterns
        in sequence:
            - Zero or one occurrence of "NAICS" at the start of the string (not present for the "10" series codes
            - Zero or more digits (some titles have digits immediately following the "NAICS")
            - Any number of spaces
            - One or more digits (these are the industry codes in most cases)
            - Optionally, a dash followed by one or more digits (used in cases where codes are combined, for example 44-45)
            - Any number of spaces (the ones that separate the prefix from the actual industry description)
        
        Parameters
        ----------
        None
            
        Returns
        -------
        cleanIndustryCodes : dict
            A dictionary that is identical to morpc.bls.INDUSTRY_CODES except that the industry titles have been stripped of the prefixes
            containing the industry code.
        """
        import re

        cleanIndustryCodes = {key:re.sub(r"^(NAICS)?(\d*)(\s*)(\d+)(-\d+)?(\s*)", "", value) for key,value in zip(self.INDUSTRY_CODES.keys(), self.INDUSTRY_CODES.values())}
        return cleanIndustryCodes

