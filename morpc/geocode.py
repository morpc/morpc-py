import logging
logger = logging.getLogger(__name__)

# Canonical USPS Publication 28 street type abbreviations, and the spelled-out forms and non-standard
# variants observed in county auditor address data. Keys are upper case with no punctuation; look them
# up through normalize_street_type() rather than directly, so that cleaning is applied consistently.
#
# This mapping is shared by the workflows that produce address data and the ones that match against it.
# Keeping it in one place is the point: when the reference side and the query side normalize
# differently, addresses that should join silently fail to.
#
# Values that are genuinely ambiguous are deliberately absent. "TR" is either TRL or TER and "BL" is
# either BLVD or BLF, so mapping either one would be a guess. They pass through unchanged and are
# reported as out of vocabulary instead.
CONST_STREET_TYPE_ABBREV = {
    "ALLEY": "ALY", "ALY": "ALY",
    "AV": "AVE", "AVE": "AVE", "AVENUE": "AVE",
    "BAYOU": "BYU", "BYU": "BYU",
    "BEND": "BND", "BND": "BND",
    "BLF": "BLF", "BLUFF": "BLF",
    "BLVD": "BLVD", "BOULEVARD": "BLVD",
    "CANYON": "CYN", "CYN": "CYN",
    "CENTER": "CTR", "CTR": "CTR",
    "CIR": "CIR", "CIRCLE": "CIR",
    "CLB": "CLB", "CLUB": "CLB",
    "CORNERS": "CORS", "CORS": "CORS",
    "COURT": "CT", "CT": "CT",
    "COVE": "CV", "CV": "CV",
    "CREEK": "CRK", "CRK": "CRK",
    "CRES": "CRES", "CRESCENT": "CRES",
    "CROSSING": "XING", "XING": "XING",
    "CURV": "CURV", "CURVE": "CURV",
    "DR": "DR", "DRIVE": "DR",
    "END": "END",
    "EXPRESSWAY": "EXPY", "EXPY": "EXPY",
    "EXT": "EXT", "EXTENSION": "EXT",
    "FOREST": "FRST", "FRST": "FRST",
    "GATEWAY": "GTWY", "GTWY": "GTWY",
    "GLEN": "GLN", "GLN": "GLN",
    "GREEN": "GRN", "GRN": "GRN",
    "GROVE": "GRV", "GRV": "GRV",
    "HEIGHTS": "HTS", "HTS": "HTS",
    "HIGHWAY": "HWY", "HWY": "HWY",
    "HILL": "HL", "HL": "HL",
    "HOLLOW": "HOLW", "HOLW": "HOLW",
    "ISLE": "ISLE",
    "JCT": "JCT", "JUNCTION": "JCT",
    "LANDING": "LNDG", "LNDG": "LNDG",
    "LANE": "LN", "LN": "LN",
    "LINK": "LINK",
    "LOOP": "LOOP",
    "MALL": "MALL",
    "MANOR": "MNR", "MNR": "MNR",
    "MEWS": "MEWS",
    "OPAS": "OPAS",
    "OVAL": "OVAL",
    "PARK": "PARK", "PK": "PARK",
    "PARKWAY": "PKWY", "PKWY": "PKWY", "PRKY": "PKWY",
    "PASS": "PASS",
    "PASSAGE": "PSGE", "PSGE": "PSGE",
    "PATH": "PATH",
    "PIKE": "PIKE",
    "PL": "PL", "PLACE": "PL",
    "PLAZA": "PLZ", "PLZ": "PLZ",
    "POINT": "PT", "PT": "PT",
    "RAMP": "RAMP",
    "RD": "RD", "ROAD": "RD",
    "RDS": "RDS", "ROADS": "RDS",
    "RIDGE": "RDG", "RDG": "RDG",
    "ROW": "ROW",
    "RUN": "RUN",
    "SPUR": "SPUR",
    "SQ": "SQ", "SQUARE": "SQ",
    "ST": "ST", "STREET": "ST",
    "STREETS": "STS", "STS": "STS",
    "TER": "TER", "TERRACE": "TER",
    "TRACE": "TRCE", "TRAC": "TRCE", "TRCE": "TRCE",
    "TRAIL": "TRL", "TRL": "TRL",
    "UPAS": "UPAS",
    "VIEW": "VW", "VW": "VW",
    "VIS": "VIS", "VISTA": "VIS",
    "WALK": "WALK",
    "WAY": "WAY", "WY": "WAY",
}

# The canonical abbreviations, for validating that a normalized value is one MORPC recognizes.
CONST_STREET_TYPES = frozenset(CONST_STREET_TYPE_ABBREV.values())

# Directional prefixes and suffixes. Anything outside this mapping is not a direction, so
# normalize_directional() discards it rather than passing it through.
CONST_DIRECTIONAL_ABBREV = {
    "N": "N", "NORTH": "N",
    "S": "S", "SOUTH": "S",
    "E": "E", "EAST": "E",
    "W": "W", "WEST": "W",
    "NE": "NE", "NORTHEAST": "NE",
    "NW": "NW", "NORTHWEST": "NW",
    "SE": "SE", "SOUTHEAST": "SE",
    "SW": "SW", "SOUTHWEST": "SW",
}

# The canonical directionals.
CONST_DIRECTIONALS = frozenset(CONST_DIRECTIONAL_ABBREV.values())


def _clean(value):
    """Upper case a value and strip surrounding whitespace and periods, or return None if it is empty.

    Returns None for anything that is not a string, so that pandas nulls pass through untouched.
    """
    if not isinstance(value, str):
        return None
    cleaned = value.strip().strip(".").strip().upper()
    return cleaned if cleaned else None


def normalize_street_type(value):
    """Return the canonical USPS abbreviation for a street type.

    Values already in canonical form are returned unchanged. Spelled-out forms ("ROAD") and the
    non-standard variants seen in county data ("WY") are mapped to the abbreviation. A value with no
    entry in CONST_STREET_TYPE_ABBREV is returned cleaned but otherwise unchanged, so that an
    unrecognized type is preserved for review rather than destroyed; test membership of
    CONST_STREET_TYPES to find those.

    Returns None for null, non-string and empty input.
    """
    cleaned = _clean(value)
    if cleaned is None:
        return None
    return CONST_STREET_TYPE_ABBREV.get(cleaned, cleaned)


def normalize_directional(value):
    """Return the canonical abbreviation for a directional prefix or suffix.

    Unlike normalize_street_type(), a value that is not a direction is discarded rather than passed
    through. A directional field can only hold one of eight values, so anything else is a parsing
    error at the source rather than an unusual direction, and keeping it would only propagate the
    error into joins.

    Returns None for null, non-string, empty and non-directional input.
    """
    cleaned = _clean(value)
    if cleaned is None:
        return None
    return CONST_DIRECTIONAL_ABBREV.get(cleaned)


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


