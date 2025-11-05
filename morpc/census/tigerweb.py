import logging

logger = logging.getLogger(__name__)

def get_tigerweb_layers_map(year, survey='ACS'):
    """
    Parameters: s
    -----------
    year : int
        The year of the TIGERweb layer (e.g., 2024).
    survey : str, optional
        The survey type, either 'ACS' (American Community Survey) or 'DEC' for Decennial Census
        or 'Current' for the most current geometries.
        Default is 'ACS'.

    Returns:
    --------
    dict : dict
        A dictionary mapping layer names to their corresponding IDs.

    Example:
    --------
    >>>   layers = get_tigerweb_layers_map(2024, survey='ACS')
    >>>   print(layers)
    """
    import pandas as pd
    import requests
    import re



    if survey not in ['ACS', 'DEC']:
        logger.error(f"Invalid survey type {survey}. Must be 'ACS' or 'DEC'.")
        raise ValueError("Invalid survey type. Must be 'ACS' or 'DEC'.")
    if survey == 'DEC' and year not in ['2010', '2020']:
        logger.error(f"Invalid year {year} for Decennial Census. Must be 2010 or 2020.")
        raise ValueError("Invalid year for Decennial Census. Must be 2010 or 2020.")
    if survey == 'ACS' and pd.to_numeric(year) < 2012:
        logger.error(f"Invalid year {year} for ACS. Must be 2012 or later.")
        raise ValueError("Invalid year for ACS. Must be 2012 or later.")
    if survey == 'DEC':
        survey = 'Census'
    if survey == 'Current':
        year == ""

    baseurl = f"https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/"
    mapserver_path = f"tigerWMS_{survey}{year}/MapServer/"
    mapserver_url = baseurl + mapserver_path

    # Retrieve the layers from the map service
    logger.info(f"Fetching metadata from {mapserver_url}?f=pjson")
    r = requests.get(f"{mapserver_url}?f=pjson")
    
    #   Check if the request was successful
    if r.status_code != 200:
        logger.error(f"Error fetching data from {mapserver_url}: {r.status_code}")
        raise RuntimeError(f"Failed to fetch data from {mapserver_url}")
    else:
        logger.info(f"successful fetch using {r.url}")
    
    # Parse the JSON response
    try:
        layers_json = r.json()
    except:
        logger.error(f"Failed to decode json: CONTENTS OF REQUESTS {r.content}")
        r.close()
        raise RuntimeError(f"Failed to parse JSON from {mapserver_url}")
    r.close()    

    # Convert the layers to a DataFrame for easier manipulation
    layers = pd.DataFrame(layers_json['layers'])
    layers = layers[['id', 'name']]
    layers = layers.loc[layers['name'].str.contains('Labels') == False]  # Exclude label layers
    
    # Convert the DataFrame to a dictionary mapping layer names to IDs
    layers = layers.set_index('name')['id'].to_dict()
    
    layers = {k.lower(): v for k, v in layers.items()}  # Normalize layer names to lowercase
    # remove census from keys in layers
    layers = {k.replace('census ', ''): v for k, v in layers.items()}
    # remove years from keys in layers
    layers = {re.sub(r"^(19|20)\d{2}$ ", '', k): v for k, v in layers.items()}
    # remove the 11Xth from congressional districts
    layers = {re.sub(r"^(11)\d{1}$th ", '', k): v for k, v in layers.items()}

    return layers
    
def get_layer_url(year, layer_name, survey='ACS'):
    """Constructs the URL for a specific TIGERweb layer based on the year, layer name, and survey type.
    Parameters:
    -----------
    year : int
        The year of the TIGERweb layer (e.g., 2024).
    layer_name : str
        The name of the layer to retrieve (e.g., 'tracts', 'counties').
    survey : str, optional
        The survey type, either 'ACS' (American Community Survey) or 'DEC' for Decennial Census.
        Default is 'ACS'.
        
    Returns:
    --------
    str : str
        The URL of the specified TIGERweb layer.

    Example:
    --------
    >>> url = get_layer_url(2024, 'tracts', survey='ACS')
    >>> print(url)
    https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_ACS2024/MapServer/8

    Raises:
    -------
    ValueError: If the survey type or year is invalid, or if the layer name does not exist for the specified year and survey.
    RuntimeError: If there is an error fetching data from the constructed URL.

    
    """
    
    import requests
    import pandas as pd
    
    logger.info(f"Validating Survey {survey} and Year {year}")
    # Validate inputs
    if survey not in ['ACS', 'DEC']:
        raise ValueError("Invalid survey type. Must be 'ACS' or 'DEC'.")
    if survey == 'DEC' and year not in ['2010', '2020']:
        raise ValueError("Invalid year for Decennial Census. Must be 2010 or 2020.")
    if survey == 'ACS' and pd.to_numeric(year) < 2012:
        raise ValueError("Invalid year for ACS. Must be 2012 or later.")    
    if survey == 'DEC':
        survey = 'Census'
    
    layers = get_tigerweb_layers_map(year, survey)

    # Normalize the layer name to lowercase
    layer_name = layer_name.lower()
    
    # Check if the layer name exists in the layers dictionary

    if layer_name not in layers:
        raise ValueError(f"Layer '{layer_name}' not found for year {year} and survey '{survey}'. Available layers: {list(layers.keys())}")

    baseurl = f"https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/"
    mapserver_path = f"tigerWMS_{survey}{year}/MapServer/{layers[layer_name]}"
    mapserver_url = baseurl + mapserver_path

    logger.info(f"url: {mapserver_url}")

    # Verify the constructed URL
    r = requests.get(f"{mapserver_url}?f=pjson")
    if r.status_code != 200:
        print(f"Error fetching data from {mapserver_url}: {r.status_code}")
        raise RuntimeError(f"Failed to fetch data from {mapserver_url}")
    r.close()
    
    # Return the constructed URL
    return mapserver_url
