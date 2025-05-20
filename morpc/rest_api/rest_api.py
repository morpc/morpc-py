def metadata_from_services_url(url):
    import requests

    # Find the max number of records allowed per request
    r = requests.get(f"{url}/?f=pjson")
    pjson = r.json()
    metadata = {}
    metadata['url'] = url
    metadata["total_count"] = get_totalRecordCount(url)
    metadata["max_record_count"] = pjson['maxRecordCount']
    metadata["name"] = pjson['name']
    metadata['schema'] = schema_from_services_fields(pjson)
    r.close()
    return metadata

def schema_from_services_fields(pjson):
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


def resource_from_services_url(url):
    import frictionless
    import re
    metadata = metadata_from_services_url(url)

    resource = {
        "name": re.sub('[:/_ ]', '-', metadata['name']).lower(),
        "format": "json",
        "path": metadata['url'],
        "schema": metadata['schema'],
        "mediatype": "application/geo+json",
        "_metadata": {
            "type": "arcgis_service",
            "total_records": metadata['total_count'],
            "max_record_count": metadata['max_record_count']
        }
    }

    return frictionless.Resource(resource)

def print_bar(i, total):
    from IPython.display import clear_output

    percent = round(i/total * 100, 3)
    completed = round(percent)
    not_completed = 100-completed
    bar = f"{i}/{total} |{'|'*completed}{'.'*not_completed}| {percent}%"
    print(bar)
    clear_output(wait=True)

def construct_sources_urls_from_metadata(metadata):
    max_records = metadata['max_record_count']
    total_records = metadata['total_count']
    sources = []
    offsets = [x for x in range(0, total_records, max_records)]
    for i in range(len(offsets)):
        start = offsets[i]
        if offsets[i]+max_records-1 > total_records:
            finish = total_records
            max_records = total_records - offsets[i]+1
        else:
            finish = offsets[i]+max_records-1
        source = {
            "title" : f"{start}-{finish}",
            "path": f"{metadata['url']}/query/?where=1%3D1&outFields=%2A&resultOffset={offsets[i]}&resultRecordCount={max_records}&outSR=4326&f=geojson"
                 }
        sources.append(source)

    return sources

def gdf_from_rest_resource(resource_path, field_ids=None):
    """Creates a GeoDataFrame from resource file for an ArcGIS Services. Automatically queries for maxRecordCount and
    iterates over the whole feature layer to return all features. Optional: Filter the results by including a list of field
    IDs.

    Example Usage:

    Parameters:
    ------------
    url : str
        A path to a ArcGIS Service feature layer.
        Example: https://services2.arcgis.com/ziXVKVy3BiopMCCU/arcgis/rest/services/Parcel/FeatureServer/0

    field_ids : list of str
        A list of strings that match field ids in the feature layer.

    Returns
    ----------
    gdf : pandas.core.frame.DataFrame
        A GeoPandas GeoDataframe constructed from the GeoJSON requested from the url.
    """

    import requests
    import json
    import frictionless
    import geopandas as gpd

    #Construct urls to query for getting total count, json, and geojson
    url = resource.path
    metadata = resource._metadata
    sources = construct_sources_urls_from_metadata(metadata)

    schema = resource.schema

    if field_ids != None:
        if not set(field_ids).issubset(avail_fields):
            print(f"{field_ids} not in available fields.")
            raise RuntimeError
        else:
            outFields = ",".join(field_ids)
            geojson_url = f"{url}/query?outFields={outFields}&where=1%3D1&f=geojson"

    firstTime = True
    offset = 0
    exceededLimit = True
    print(geojson_url)
    while offset < totalRecordCount:
        # print("Downloading records from {}&resultOffset={}&resultRecordCount={}".format(url, offset, recordCount))
        # Request 2000 records from the API starting with the record indicated by offset.
        # Configure the request to include only the required fields, to project the geometries to
        # Ohio State Plane South coordinate reference system (EPSG:3735), and to format the data as GeoJSON
        r = requests.get(f"{geojson_url}&resultOffset={offset}&resultRecordCount={maxRecordCount}")
        # Extract the GeoJSON from the API response
        result = r.json()

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
        print(f"{offset} of {totalRecordCount}")
        clear_output(wait = True)

    if crs != None:
        gdf = gpd.GeoDataFrame(gdf, geometry='geometry').set_crs(crs)
    else:
        gdf = gpd.GeoDataFrame(gdf, geometry='geometry')

    return(gdf)