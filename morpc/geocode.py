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

# Numbered routes, as the counties spell them in the street name field. Franklin writes "SR 104",
# Knox writes "ST RT 19" and Union writes "STATE ROUTE 245" for the same kind of road, so a name
# matched literally joins within a county and fails across the region. Each spelling is folded to
# one canonical prefix by normalize_street_name(). Longest key first when matching, or "US ROUTE 23"
# would be read as "US" followed by a street named "ROUTE 23".
#
# These are applied to both sides of a match: the reference data is normalized when the geocoding
# index is built, and the query is normalized when it is parsed.
CONST_ROUTE_PREFIX_ABBREV = {
    "STATE ROUTE": "SR", "STATE RTE": "SR", "STATE RT": "SR", "ST ROUTE": "SR", "ST RTE": "SR",
    "ST RT": "SR", "OHIO ROUTE": "SR", "OH ROUTE": "SR", "SR": "SR", "SRT": "SR",
    "COUNTY ROAD": "CR", "COUNTY RD": "CR", "CO ROAD": "CR", "CO RD": "CR", "CR": "CR",
    "TOWNSHIP ROAD": "TR", "TOWNSHIP RD": "TR", "TWP ROAD": "TR", "TWP RD": "TR",
    "US ROUTE": "US", "US RTE": "US", "US RT": "US", "US HIGHWAY": "US", "US HWY": "US", "US": "US",
    "INTERSTATE": "I", "I": "I",
}

# Unit designators that introduce a secondary address unit. A facility address often carries one
# ("1234 E MAIN ST STE 200") where the address point record holds the unit in its own field, so the
# designator and everything after it is split off before the street address is parsed.
CONST_UNIT_TYPES = frozenset([
    "APT", "APARTMENT", "BLDG", "BUILDING", "BSMT", "DEPT", "FL", "FLOOR", "FRNT", "HNGR", "KEY",
    "LBBY", "LOT", "LOWR", "OFC", "OFFICE", "PH", "PIER", "RM", "ROOM", "SLIP", "SPC", "STE",
    "STOP", "SUITE", "TRLR", "UNIT", "UPPR",
])


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


def normalize_house_number(value):
    """Return a house number in a form that can be joined on.

    Three defects in the published data make a literal join fail. Counties that publish the number
    as a numeric column leave a float tail ("1013.0"). Knox zero pads to five digits ("01013"). A
    facility address sometimes names every unit in a building ("4410,4412,4416 MORSE RD") or a range
    ("5684-5704 DIERKER RD"), where only the first number can be located. All three are reduced here.

    A number that is legitimately not an integer is preserved: Knox publishes one fractional address
    ("407.5 SIXTH AVE"), which is distinguishable from a float tail because the fraction is not zero.

    Returns None for null, non-string, empty and non-numeric input, including the LBRS "-9" sentinel
    for "no house number".
    """
    import re

    cleaned = _clean(value)
    if cleaned is None:
        return None

    # Only the first number of a list or a range can be placed on the map.
    cleaned = re.split(r"[,/]|(?<=\d)-(?=\d)", cleaned)[0].strip()

    if cleaned in ("", "-9"):
        return None
    if not cleaned[0].isdigit():
        return None

    # A trailing ".0" is a float that was written as text; ".5" is a real fractional address.
    if re.fullmatch(r"\d+\.0+", cleaned):
        cleaned = cleaned.split(".")[0]

    # Zero padding is a Knox convention, not part of the number. Guard the all-zero case.
    if cleaned.isdigit():
        cleaned = cleaned.lstrip("0") or "0"

    return cleaned


def normalize_street_name(value):
    """Return a street name in a form that can be joined on.

    Upper cases, strips punctuation that the counties are inconsistent about, collapses repeated
    whitespace ("COUNTY  ROAD 91"), and folds the spellings of a numbered route to one canonical
    prefix via CONST_ROUTE_PREFIX_ABBREV, so that "STATE ROUTE 33", "ST RT 33" and "SR 33" all join.

    Returns None for null, non-string and empty input.
    """
    import re

    cleaned = _clean(value)
    if cleaned is None:
        return None

    cleaned = re.sub(r"[.,]", " ", cleaned)
    cleaned = " ".join(cleaned.split())
    if not cleaned:
        return None

    # A route prefix only counts when a route number follows it, so that a street genuinely named
    # "INTERSTATE" or a place called "US BANK" is left alone. Longest spelling wins.
    tokens = cleaned.split()
    for length in (3, 2, 1):
        prefix = " ".join(tokens[:length])
        if prefix in CONST_ROUTE_PREFIX_ABBREV and len(tokens) > length and tokens[length].isdigit():
            return " ".join([CONST_ROUTE_PREFIX_ABBREV[prefix]] + tokens[length:])

    return cleaned


def parse_address(address):
    """Split a single-line street address into the components used by the address point data.

    Returns a dict with the keys streetaddr, streetname, streettype, prefixdir, suffixdir, unitnum
    and unittype, matching the field names in morpc-addresspoints-standardize, with each value
    normalized exactly as that dataset normalizes its own. This is the query side of a match; the
    reference side is normalized when the geocoding index is built. Both must use these functions or
    addresses that should join will silently fail to.

    Only streetname is required to be present. A component the address does not carry is None,
    including streetaddr when the address names no house number ("ST RT 314 NORTH"), which is not
    locatable but is reported rather than guessed at.

    Returns None when the address is null, empty, or contains no street name.
    """
    cleaned = _clean(address)
    if cleaned is None:
        return None

    parsed = {key: None for key in
              ("streetaddr", "streetname", "streettype", "prefixdir", "suffixdir", "unitnum", "unittype")}

    tokens = " ".join(cleaned.replace(",", " ").split()).split()

    # A unit designator ends the street address. "#" is written both joined to the number and apart.
    for position, token in enumerate(tokens):
        designator = token.strip(".").upper()
        if position > 0 and (designator in CONST_UNIT_TYPES or designator.startswith("#")):
            parsed["unittype"] = designator if not designator.startswith("#") else "#"
            remainder = tokens[position + 1:]
            if designator.startswith("#") and len(designator) > 1:
                remainder = [designator[1:]] + remainder
            parsed["unitnum"] = " ".join(remainder) or None
            tokens = tokens[:position]
            break

    if tokens and normalize_house_number(tokens[0]) is not None:
        parsed["streetaddr"] = normalize_house_number(tokens[0])
        tokens = tokens[1:]

    # A trailing directional is a suffix only when a street name would remain without it, so that
    # "5989 ASTOR" keeps its name and "920 THURBER DR WEST" gives up its W.
    if len(tokens) > 1 and normalize_directional(tokens[-1]):
        parsed["suffixdir"] = normalize_directional(tokens[-1])
        tokens = tokens[:-1]

    # Likewise a trailing street type, which by now is last because any suffix directional is gone.
    if len(tokens) > 1:
        candidate = normalize_street_type(tokens[-1])
        if candidate in CONST_STREET_TYPES:
            parsed["streettype"] = candidate
            tokens = tokens[:-1]

    # A leading directional is a prefix only when something other than a street type remains, so
    # that "17 NORTH ST" is North Street rather than a street with no name.
    if len(tokens) > 1 and normalize_directional(tokens[0]):
        parsed["prefixdir"] = normalize_directional(tokens[0])
        tokens = tokens[1:]

    parsed["streetname"] = normalize_street_name(" ".join(tokens))
    if parsed["streetname"] is None:
        return None

    return parsed


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


