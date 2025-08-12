def schema_from_services_fields(pjson):
    """Extracts the schema from a JSON object returned by an ArcGIS REST API service.

    Parameters:
    -----------
    pjson : dict
        A JSON object returned by an ArcGIS REST API service.
    Returns:
    --------
    schema : dict
        A dictionary containing the schema of the fields in the service.
    """
    import json
    schema = {}
    schema['fields'] = []
    for field in pjson['fields']:
        properties = {}
        properties['name'] = field['name']
        properties['title'] = field['alias']
        ftype = field['type'].replace('esriFieldType', '').lower()
        if ftype == 'oid':
            properties['type'] ='string'
        if ftype == 'double':
            properties['type'] ='number'
        if ftype == 'single':
            ftype ='number'
        if ftype == 'smallinteger':
            properties['type'] ='number'
        if ftype == 'geometry':
            continue # skip extra geometry columns
        schema['fields'].append(properties)

    return schema

def get_totalRecordCount(url):
    """Fetches the total number of records from an ArcGIS REST API service.
    Parameters:
    -----------
    url : str
        The URL of the ArcGIS REST API service.
    Returns:
    --------    
    total_count : int
        The total number of records in the service.
    """
    import requests
    import re

    # Find the total number of records
    r = requests.get(f"{url}/query/", params = {
        "outfields": "*",
        "where": "1=1",
        "f": "geojson",
        "returnCountOnly": "true"})
    total_count = int(re.findall('[0-9]+',str(r.json()))[0])
    r.close()

    return total_count


    
def resource(url):
    """Creates a frictionless Resource object from an ArcGIS REST API service URL.

    Parameters:
    ----------- 
    url : str
        The URL of the ArcGIS REST API service. 
    
    Returns:
    --------    
    resource : frictionless.Resource
        A frictionless Resource object containing the schema and metadata of the service.

    Example:
    --------
    >>> resource = resource("https://services.arcgis.com/arcgis/rest/services/ServiceName/FeatureServer/0")

    """
    import frictionless
    import re
    import requests

    r = requests.get(f"{url}/?f=pjson")
    pjson = r.json()
    r.close()

    resource = {
        "name": re.sub('[:/_ ]', '-', pjson['name']).lower(),
        "format": "json",
        "path": url,
        "schema": schema_from_services_fields(pjson),
        "mediatype": "application/geo+json",
        "_metadata": {
            "type": "arcgis_service",
            "total_records": get_totalRecordCount(url),
            "max_record_count": pjson['maxRecordCount'],
            "wkid": pjson['sourceSpatialReference']['wkid']
        }
    }

    return frictionless.Resource(resource)

def esri_wkid_to_epsg(esri_wkid):
    """Converts an ESRI WKID to an EPSG code.

    Parameters:
    -----------
    esri_wkid : int
        The ESRI WKID to be converted.  
    Returns:
    --------
    epsg : int
        The corresponding EPSG code.
    Example:
    --------
    >>> epsg = esri_wkid_to_epsg(4326)
    >>> print(epsg)
    4326    

    """
    import json
    import requests

    r = requests.get(f"https://spatialreference.org/ref/esri/{esri_wkid}/projjson.json")
    json = r.json()
    epsg = json['base_crs']['id']['code']
    return epsg

def print_bar(i, total):
    """Prints a progress bar to the console.

    Parameters:     
    -----------
    i : int
        The current iteration number.
    total : int
        The total number of iterations.
    """
    from IPython.display import clear_output

    percent = round(i/total * 100, 3)
    completed = round(percent)
    not_completed = 100-completed
    bar = f"{i}/{total} |{'|'*completed}{'.'*not_completed}| {percent}%"
    print(bar)
    clear_output(wait=True)

def get_api_key(path):
    """Reads an API key from a file.
    Parameters: 
    -----------
    path : str
        The path to the file containing the API key.
    Returns:
    --------
    key : str
        The API key read from the file.
    Example:
    --------
    >>> key = get_api_key('path/to/api_key.txt')
    """
    with open(path, 'r') as file:
        key = file.readlines()
    return key[0]

def get(resource_path, field_ids=None, api_key=None):
    """Creates a GeoDataFrame from resource file for an ArcGIS Services. Automatically queries for maxRecordCount and
    iterates over the whole feature layer to return all features. Optional: Filter the results by including a list of field
    IDs.

    Example Usage:

    Parameters:
    ------------
    resource_path : str
        The path to the resource file, which can be a local file or a URL to an ArcGIS REST API service.

    field_ids : list of str
        A list of strings that match field ids in the feature layer.

    api_key : str, optional
        An API key for accessing the ArcGIS REST API service. If not provided, the function will attempt to access the service without an API key.

    Returns
    ----------
    gdf : pandas.core.frame.DataFrame
        A GeoPandas GeoDataframe constructed from the GeoJSON requested from the url.

    Raises:
    ------
    RuntimeError: If the provided field_ids are not available in the resource.  

    Example:
    --------
    >>> gdf = get("path/to/resource.json", 
                  field_ids=['OBJECTID', 'NAME'], 
                  api_key=get_api_key('path/to/api_key.txt'))
    """

    import requests
    import frictionless
    import geopandas as gpd

    ## Extract important metadata
    resource = frictionless.Resource(resource_path)
    url = resource.path
    totalRecordCount = resource.to_dict()['_metadata']['total_records']
    maxRecordCount = resource.to_dict()['_metadata']['max_record_count']
    wkid = resource.to_dict()['_metadata']['wkid']
    epsg = esri_wkid_to_epsg(wkid) ## Convert ESRI WKID to EPSG code

    ## Get field names for filtering fields
    schema = resource.schema
    avail_fields = schema.field_names

    geojson_url = f"{url}/query?outFields=*&where=1%3D1&f=geojson"
    ## Verify fields_ids
    if field_ids != None:
        if not set(field_ids).issubset(avail_fields):
            print(f"{field_ids} not in available fields.")
            raise RuntimeError
        else:
            outFields = ",".join(field_ids)
            geojson_url = f"{url}/query?outFields={outFields}&where=1%3D1&f=geojson"

    ## Construct list of source urls to account for max record counts
    sources = []
    offsets = [x for x in range(0, totalRecordCount, maxRecordCount)]
    for i in range(len(offsets)):
        start = offsets[i]
        if offsets[i]+maxRecordCount-1 > totalRecordCount:
            finish = totalRecordCount
            maxRecordCount = totalRecordCount - offsets[i]+1
        else:
            finish = offsets[i]+maxRecordCount-1
        source = {
            "title" : f"{start}-{finish}",
            "path": f"{geojson_url}&resultOffset={offsets[i]}&resultRecordCount={maxRecordCount}"
                 }
        sources.append(source)

    firstTime = True
    offset = 0
    exceededLimit = True
    for i in range(len(sources)):
        print_bar(i, len(sources))
        # Request geojson for each source url
        if api_key == None:
            r = requests.get(sources[i]['path'])
        else:
            r = requests.get(f"{sources[i]['path']}&key={api_key}")
        # Extract the GeoJSON from the API response
        try:
            result = r.json()
        except:
            print(f"CONTENTS OF REQUESTS {r.content}")


        # Read this chunk of data into a GeoDataFrame
        temp = gpd.GeoDataFrame.from_features(result["features"])
        if firstTime:
            # If this is the first chunk of data, create a permanent copy of the GeoDataFrame that we can append to
            gdf = temp.copy()
            firstTime = False
        else:
            # If this is not the first chunk, append to the permanent GeoDataFrame
            gdf = pd.concat([gdf, temp], axis='index')

        # Increase the offset so that the next request fetches the next chunk of data
        offset += maxRecordCount

    return(gdf.set_crs(f"epsg:{epsg}"))