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

    # The hyphen in a compound street name is inconsistent in both directions: the registries write
    # "MARION-BUCYRUS ROAD" where Marion County publishes "MARION BUCYRUS", and "HAZELTON ETNA ROAD"
    # where Licking publishes "HAZELTON-ETNA". Treating it as a space settles the question one way.
    cleaned = re.sub(r"[.,\-]", " ", cleaned)
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


# The geocoding index stores street names and house numbers already normalized, so an index built
# before a change to the normalization functions no longer agrees with the query side. Raise this
# whenever normalize_street_name, normalize_house_number or normalize_zip changes what they return,
# so that a stale index is rebuilt rather than silently matching against the old vocabulary.
CONST_GEOCODE_INDEX_VERSION = 1


def normalize_zip(value):
    """Return a five digit ZIP code, or None.

    Strips the float tail that Knox carries on every one of its records ("43050.0") and the
    ZIP+4 extension that some registries publish, either of which defeats a literal join.
    """
    cleaned = _clean(value)
    if cleaned is None:
        return None
    digits = cleaned.split(".")[0].split("-")[0].strip()
    return digits[:5] if len(digits) >= 5 and digits[:5].isdigit() else None


def build_geocode_index(resourcePath, indexPath=None, force=False):
    """Build the local index that geocode_addresspoints() matches against.

    The published address point database cannot be matched against directly. It carries no index on
    the fields a match joins on, so every lookup is a full scan of 1.25 million rows; its geometry is
    a WKB blob rather than coordinates; and its components are normalized inconsistently between
    counties, so that Knox in particular joins against nothing. Indexing the file in place is not an
    option either, because that changes the file and its Frictionless descriptor records a hash.

    So a separate, smaller database is derived from it once: the match fields normalized through the
    same functions the query side uses, the geometry decoded to coordinates, and an index over the
    join. It is rebuilt automatically when the source it was derived from changes.

    Parameters
    ----------
    resourcePath : str
        Path to the Frictionless resource file describing morpc-addresspoints-standardize. The
        database itself is downloaded and hash verified by morpc.frictionless.resolve_data_path if
        it is not already cached.
    indexPath : str
        Optional. Where to write the index. Defaults to the source database path with a
        ".geocodeindex.sqlite" extension, which keeps it beside the data it was derived from.
    force : bool
        Optional. Rebuild even if the existing index is current. Defaults to False.

    Returns
    -------
    str
        The path to the index.
    """
    import os
    import sqlite3
    import frictionless
    import shapely.wkb
    import morpc.frictionless

    resource = frictionless.Resource(resourcePath)
    sourceDir = os.path.dirname(os.path.abspath(resourcePath))
    sourcePath = morpc.frictionless.resolve_data_path(resource, sourceDir)
    tableName = resource.dialect.get_control("sql").table

    if indexPath is None:
        indexPath = os.path.splitext(sourcePath)[0] + ".geocodeindex.sqlite"

    # An index is current only if it was built from this release of the data and by this version of
    # the normalization. Either one moving on leaves it matching against a vocabulary nothing uses.
    if os.path.exists(indexPath) and not force:
        try:
            existing = sqlite3.connect(indexPath)
            meta = dict(existing.execute("select key, value from meta").fetchall())
            existing.close()
            if (meta.get("sourcehash") == resource.hash
                    and meta.get("version") == str(CONST_GEOCODE_INDEX_VERSION)):
                logger.info("Using existing geocoding index at {}".format(indexPath))
                return indexPath
            logger.info("Geocoding index at {} is out of date. Rebuilding.".format(indexPath))
        except sqlite3.DatabaseError:
            logger.warning("Geocoding index at {} is unreadable. Rebuilding.".format(indexPath))

    logger.info("Building geocoding index at {} from {}".format(indexPath, sourcePath))
    if os.path.exists(indexPath):
        os.remove(indexPath)

    source = sqlite3.connect("file:{}?mode=ro".format(sourcePath), uri=True)
    index = sqlite3.connect(indexPath)
    index.execute("create table meta (key text primary key, value text)")
    index.execute("""create table addresspoints (
        streetaddr text, streetname text, streettype text, prefixdir text, suffixdir text,
        city text, zip text, county text, lon real, lat real)""")

    read = source.execute("""select streetaddr, streetname, streettype, prefixdir, suffixdir,
        city, zip, county, GEOMETRY from {}""".format(tableName))
    written = 0
    skipped = 0
    while True:
        batch = read.fetchmany(50000)
        if not batch:
            break
        rows = []
        for streetaddr, streetname, streettype, prefixdir, suffixdir, city, zip_, county, geometry in batch:
            name = normalize_street_name(streetname)
            if name is None or geometry is None:
                # A record with no street name or no location cannot be matched to or returned.
                skipped += 1
                continue
            point = shapely.wkb.loads(geometry)
            rows.append((normalize_house_number(streetaddr), name, normalize_street_type(streettype),
                         normalize_directional(prefixdir), normalize_directional(suffixdir),
                         _clean(city), normalize_zip(zip_), county, point.x, point.y))
        index.executemany("insert into addresspoints values (?,?,?,?,?,?,?,?,?,?)", rows)
        written += len(rows)
    source.close()

    index.execute("create index idx_number_name on addresspoints(streetaddr, streetname)")
    index.execute("insert into meta values ('sourcehash', ?)", (resource.hash,))
    index.execute("insert into meta values ('sourcepath', ?)", (resource.path,))
    index.execute("insert into meta values ('version', ?)", (str(CONST_GEOCODE_INDEX_VERSION),))
    index.commit()
    index.close()
    logger.info("Geocoding index holds {:,} records. {:,} were skipped for want of a street name "
                "or a location.".format(written, skipped))
    return indexPath


def geocode_addresspoints(addresses, resourcePath, zipcodes=None, indexPath=None, tolerance=500):
    """Geocode street addresses by matching them against MORPC's regional address points.

    This is the local alternative to geocode(), which calls Nominatim. It is offline, reproducible,
    and better on in-region addresses, but it can only find an address that a county auditor has
    published a point for, and only within the MORPC 15-county region.

    Matching proceeds in tiers, from every component to the house number and street name alone, and
    the tier that produced each result is reported so that a caller can decide how much to trust it.
    Where a tier finds several points more than `tolerance` apart and nothing distinguishes them, no
    point is returned and the result is reported as ambiguous. An address that is honestly unmatched
    is more useful than a point that is quietly wrong.

    Parameters
    ----------
    addresses : list
        Single-line street addresses ("1234 E MAIN ST"). Anything parse_address() accepts.
    resourcePath : str
        Path to the Frictionless resource file describing morpc-addresspoints-standardize. Pin the
        descriptor from a specific release to pin the reference data.
    zipcodes : list
        Optional. ZIP codes parallel to `addresses`, used to disambiguate a street name that occurs
        in more than one community. Strongly recommended: without one, common street names in
        Franklin County are frequently ambiguous.
    indexPath : str
        Optional. Path to the geocoding index. See build_geocode_index().
    tolerance : float
        Optional. Metres within which several matched points are treated as one place -- the units
        of an apartment building, or the buildings of a hospital campus -- and returned as their
        centre. Beyond it they are treated as different places and the address is left unmatched.
        Defaults to 500, which is above the widest campus observed in the validation facilities
        (353 m across 133 points) and well below the closest genuine collision (two "BETHEL RD"
        addresses 75 km apart).

    Returns
    -------
    geopandas.GeoDataFrame
        One row per input address, in input order, in EPSG:4326. Carries the parsed components, the
        geometry where one was found, and the match reporting fields:

        matched     : bool, whether a point was returned.
        matchtier   : "exact" (every component), "components" (house number, street name and ZIP),
                      "number_name" (house number and street name alone), or None.
        matchcount  : number of address points the winning tier found.
        matchspread : metres between the furthest apart of them.
        matchnote   : why an address was not matched, where it was not.
    """
    import math
    import sqlite3
    import pandas as pd
    import geopandas as gpd
    import shapely

    if zipcodes is None:
        zipcodes = [None] * len(addresses)
    if len(zipcodes) != len(addresses):
        logger.error("zipcodes must be the same length as addresses.")
        raise ValueError

    if indexPath is None:
        indexPath = build_geocode_index(resourcePath)
    index = sqlite3.connect("file:{}?mode=ro".format(indexPath), uri=True)

    def separation(candidates):
        """Metres across the bounding box of the candidate points.

        The diagonal of the box rather than the true furthest pair, which is the same number for the
        two point case that matters and an upper bound otherwise, computed in one pass rather than
        the n squared a common street name would cost.
        """
        if len(candidates) < 2:
            return 0.0
        lons = [c[0] for c in candidates]
        lats = [c[1] for c in candidates]
        midLatitude = math.radians((min(lats) + max(lats)) / 2)
        northing = (max(lats) - min(lats)) * 111320
        easting = (max(lons) - min(lons)) * 111320 * math.cos(midLatitude)
        return math.hypot(northing, easting)

    results = []
    for address, zipcode in zip(addresses, zipcodes):
        parsed = parse_address(address)
        record = {"address": address, "matched": False, "matchtier": None, "matchcount": 0,
                  "matchspread": None, "matchnote": None, "lon": None, "lat": None}

        if parsed is None:
            record["matchnote"] = "no street name could be parsed from the address"
            results.append(record)
            continue
        record.update(parsed)

        if parsed["streetaddr"] is None:
            record["matchnote"] = "address carries no house number, so it cannot be located"
            results.append(record)
            continue

        zipcode = normalize_zip(zipcode)
        tiers = [
            ("exact", "streetaddr=? and streetname=? and streettype is ? and prefixdir is ? and suffixdir is ?"
                      + (" and zip=?" if zipcode else ""),
             [parsed["streetaddr"], parsed["streetname"], parsed["streettype"],
              parsed["prefixdir"], parsed["suffixdir"]] + ([zipcode] if zipcode else [])),
            ("components", "streetaddr=? and streetname=?" + (" and zip=?" if zipcode else ""),
             [parsed["streetaddr"], parsed["streetname"]] + ([zipcode] if zipcode else [])),
            ("number_name", "streetaddr=? and streetname=?",
             [parsed["streetaddr"], parsed["streetname"]]),
        ]

        for tier, where, parameters in tiers:
            candidates = index.execute(
                "select lon, lat from addresspoints where " + where, parameters).fetchall()
            if not candidates:
                continue
            spread = separation(candidates)
            record.update({"matchtier": tier, "matchcount": len(candidates),
                           "matchspread": round(spread, 1)})
            if spread > tolerance:
                record["matchnote"] = ("{} address points {:,.0f} m apart match equally well"
                                       .format(len(candidates), spread))
                break
            # One address commonly matches many points -- the units of an apartment building, or the
            # buildings of a hospital campus. They are one place, so the result is their centre.
            record.update({"matched": True,
                           "lon": sum(c[0] for c in candidates) / len(candidates),
                           "lat": sum(c[1] for c in candidates) / len(candidates)})
            break
        else:
            record["matchnote"] = "no address point matches this house number and street name"

        results.append(record)

    index.close()
    frame = pd.DataFrame(results)
    geometry = [shapely.Point(lon, lat) if pd.notna(lon) else None
                for lon, lat in zip(frame["lon"], frame["lat"])]
    frame = frame.drop(columns=["lon", "lat"])
    logger.info("Matched {:,} of {:,} addresses against the address points."
                .format(int(frame["matched"].sum()), len(frame)))
    return gpd.GeoDataFrame(frame, geometry=geometry, crs="EPSG:4326")


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


