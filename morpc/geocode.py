import logging
logger = logging.getLogger(__name__)

def geocode(addresses: list, endpoint=None):
    """
    Geocode a list of adresses.

    Parameters:
    -----------
    addresses : list
        A list of addresses to pass to geopy.

    endpoint : str
        Optional: str of the endpoint. Used for running nominatim in local docker container, then change to "localhost:8080".

    Returns:
    --------
    pandas.DataFrame

    """

    import pandas as pd, time
    from geopy.geocoders import Nominatim
    from geopy.extra.rate_limiter import RateLimiter
    from tqdm import tqdm

    tqdm.pandas()

    df = pd.DataFrame({'address': addresses})          # needs column 'address'

    if endpoint == None:
        delay = 1
        logging.info(f"Fetching from default public nominatim instance.")
        geolocator = Nominatim(user_agent="morpc-py", timeout=10)

        # Wrap with RateLimiter: min 1 sec between calls as per Nominatim policy
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=delay)
        
        df["location"] = df["address"].progress_apply(geocode)
        df["lat"] = df["location"].apply(lambda loc: loc.latitude if loc else None)
        df["lon"] = df["location"].apply(lambda loc: loc.longitude if loc else None)
    else:
        delay = 0
        geolocator = Nominatim(domain=endpoint, scheme='http', user_agent="local-nominatim")

        geocode = geolocator.geocode

        df["location"] = df["address"].progress_apply(geocode)
        df["lat"] = df["location"].apply(lambda loc: loc.latitude if loc else None)
        df["lon"] = df["location"].apply(lambda loc: loc.longitude if loc else None)





    return df


