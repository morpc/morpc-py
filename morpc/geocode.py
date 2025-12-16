import logging
logger = logging.getLogger(__name__)

def geocode(addresses: list):
    """
    Geocode a list of adresses.

    Parameters:
    -----------
    addresses : list
        A list of addresses to pass to geopy.

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

    geolocator = Nominatim(user_agent="morpc-py", timeout=10)

    # Wrap with RateLimiter: min 1 sec between calls as per Nominatim policy
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    df["location"] = df["address"].progress_apply(geocode)
    df["lat"] = df["location"].apply(lambda loc: loc.latitude if loc else None)
    df["lon"] = df["location"].apply(lambda loc: loc.longitude if loc else None)

    return df


