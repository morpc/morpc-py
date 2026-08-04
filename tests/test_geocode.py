import sqlite3

import pytest

import morpc
from morpc.geocode import _strip_postal_tail


@pytest.fixture
def index(tmp_path):
    """A geocoding index holding a handful of points, standing in for the regional database.

    Passing indexPath to geocode_addresspoints() bypasses build_geocode_index(), so these tests
    exercise the matching without the 183 MB download the real reference data requires. Values are
    stored already normalized, exactly as the builder writes them.
    """
    path = str(tmp_path / "index.sqlite")
    connection = sqlite3.connect(path)
    connection.execute("""create table addresspoints (
        streetaddr text, streetname text, streettype text, prefixdir text, suffixdir text,
        city text, zip text, county text, lon real, lat real, routenum text)""")
    connection.executemany("insert into addresspoints values (?,?,?,?,?,?,?,?,?,?,?)", [
        # An ordinary address.
        ("290", "HIGH", "ST", "W", None, "OSTRANDER", "43061", "Delaware", -83.21639, 40.26325, None),
        # Two units of one building, metres apart: one place.
        ("1150", "COLONY", "DR", None, None, "WESTERVILLE", "43081", "Franklin", -82.92000, 40.12000, None),
        ("1150", "COLONY", "DR", None, None, "WESTERVILLE", "43081", "Franklin", -82.92100, 40.12050, None),
        # The same house number on same-named streets in two counties: two places.
        ("3000", "BETHEL", "RD", None, None, "COLUMBUS", "43230", "Franklin", -83.08000, 40.06000, None),
        ("3000", "BETHEL", "RD", None, None, "BELLEFONTAINE", "43311", "Logan", -83.76000, 40.36000, None),
        # A route published without its class, as Delaware publishes US 42.
        ("844", "42", None, None, "N", "DELAWARE", "43015", "Delaware", -83.06000, 40.29000, "42"),
        # Two different roads sharing a number, as Logan publishes both CR 32 and TR 32. Far enough
        # apart that folding them together would be caught rather than silently averaged.
        ("284", "CR 32", None, None, None, "BELLEFONTAINE", "43311", "Logan", -83.75000, 40.35000, "32"),
        ("284", "TR 32", None, None, None, "BELLEFONTAINE", "43311", "Logan", -83.70000, 40.40000, "32"),
    ])
    connection.commit()
    connection.close()
    return path


def test_match_reports_the_exact_tier(index):
    result = morpc.geocode_addresspoints(["290 W High St"], "unused", zipcodes=["43061"], indexPath=index)
    assert result.loc[0, "matched"]
    assert result.loc[0, "matchtier"] == "exact"
    assert result.loc[0, "geometry"].x == pytest.approx(-83.21639)


def test_match_falls_back_when_components_disagree(index):
    # No street type in the query, so the exact tier cannot fire, but the address is still found.
    result = morpc.geocode_addresspoints(["290 W High"], "unused", zipcodes=["43061"], indexPath=index)
    assert result.loc[0, "matched"]
    assert result.loc[0, "matchtier"] == "components"


def test_units_of_one_building_return_their_centre(index):
    result = morpc.geocode_addresspoints(["1150 COLONY DRIVE"], "unused", zipcodes=["43081"], indexPath=index)
    assert result.loc[0, "matched"]
    assert result.loc[0, "matchcount"] == 2
    assert result.loc[0, "geometry"].x == pytest.approx(-82.9205)


def test_genuinely_ambiguous_addresses_are_not_guessed(index):
    # The same address on two streets 60 km apart, with no ZIP to tell them apart.
    result = morpc.geocode_addresspoints(["3000 BETHEL RD"], "unused", indexPath=index)
    assert not result.loc[0, "matched"]
    assert result.loc[0, "geometry"] is None
    assert result.loc[0, "matchcount"] == 2
    assert "apart" in result.loc[0, "matchnote"]


def test_a_zip_code_resolves_the_ambiguity(index):
    result = morpc.geocode_addresspoints(["3000 BETHEL RD"], "unused", zipcodes=["43311"], indexPath=index)
    assert result.loc[0, "matched"]
    assert result.loc[0, "geometry"].x == pytest.approx(-83.76)


def test_unmatchable_addresses_say_why(index):
    result = morpc.geocode_addresspoints(
        ["ST RT 314 NORTH", "999 NOWHERE RD", ""], "unused", indexPath=index)
    assert not result["matched"].any()
    assert "no house number" in result.loc[0, "matchnote"]
    assert "no address point matches" in result.loc[1, "matchnote"]
    assert "no street name" in result.loc[2, "matchnote"]


def test_results_are_returned_in_input_order_and_projected(index):
    addresses = ["999 NOWHERE RD", "290 W High St", "1150 COLONY DRIVE"]
    result = morpc.geocode_addresspoints(addresses, "unused", indexPath=index)
    assert list(result["address"]) == addresses
    assert result.crs == "EPSG:4326"


def test_canonical_street_types_pass_through():
    for value in ["RD", "DR", "ST", "AVE", "CT", "LN", "BLVD", "XING", "TRCE"]:
        assert morpc.normalize_street_type(value) == value


def test_spelled_out_street_types_are_abbreviated():
    assert morpc.normalize_street_type("ROAD") == "RD"
    assert morpc.normalize_street_type("AVENUE") == "AVE"
    assert morpc.normalize_street_type("STREET") == "ST"
    assert morpc.normalize_street_type("COURT") == "CT"
    assert morpc.normalize_street_type("PARKWAY") == "PKWY"
    assert morpc.normalize_street_type("CROSSING") == "XING"


def test_street_type_cleaning():
    # Case, surrounding whitespace and trailing periods are all present in county auditor data.
    assert morpc.normalize_street_type("Road") == "RD"
    assert morpc.normalize_street_type("rd") == "RD"
    assert morpc.normalize_street_type("DR ") == "DR"
    assert morpc.normalize_street_type(" Ave. ") == "AVE"


def test_non_standard_street_type_variants():
    assert morpc.normalize_street_type("WY") == "WAY"
    assert morpc.normalize_street_type("AV") == "AVE"
    assert morpc.normalize_street_type("PRKY") == "PKWY"
    assert morpc.normalize_street_type("TRAC") == "TRCE"


def test_unrecognized_street_type_is_preserved_not_discarded():
    # An unmapped value is cleaned but kept, so that it can be reported rather than silently lost.
    assert morpc.normalize_street_type("THAYER") == "THAYER"
    assert morpc.normalize_street_type("ST EXT") == "ST EXT"
    assert "THAYER" not in morpc.CONST_STREET_TYPES


def test_ambiguous_street_types_are_not_guessed():
    # TR is either TRL or TER; BL is either BLVD or BLF. Neither is mapped.
    assert morpc.normalize_street_type("TR") == "TR"
    assert morpc.normalize_street_type("BL") == "BL"


def test_street_type_null_handling():
    assert morpc.normalize_street_type(None) is None
    assert morpc.normalize_street_type("") is None
    assert morpc.normalize_street_type("   ") is None
    assert morpc.normalize_street_type(float("nan")) is None


def test_directionals():
    assert morpc.normalize_directional("N") == "N"
    assert morpc.normalize_directional("NORTH") == "N"
    assert morpc.normalize_directional("South") == "S"
    assert morpc.normalize_directional("West") == "W"
    assert morpc.normalize_directional("northwest") == "NW"


def test_non_directional_values_are_discarded():
    # These appear in the prefixdir field of the address point data and are parsing errors at the
    # source, not unusual directions.
    for value in ["DUNHAM", "A", "B", "C", "D", "<Null>"]:
        assert morpc.normalize_directional(value) is None


def test_directional_null_handling():
    assert morpc.normalize_directional(None) is None
    assert morpc.normalize_directional("") is None
    assert morpc.normalize_directional(float("nan")) is None


def test_house_number_defects_in_published_data():
    # A float tail comes from counties that publish the number as a numeric column, and zero padding
    # is a Knox convention. Both make a literal join fail.
    assert morpc.normalize_house_number("1013.0") == "1013"
    assert morpc.normalize_house_number("01013") == "1013"
    assert morpc.normalize_house_number("00017") == "17"
    assert morpc.normalize_house_number(" 290 ") == "290"


def test_house_number_lists_and_ranges_keep_the_first():
    # A facility address sometimes names every unit in a building. Only the first can be located.
    assert morpc.normalize_house_number("5684-5704") == "5684"
    assert morpc.normalize_house_number("4410,4412,4416,4418") == "4410"
    assert morpc.normalize_house_number("2397/2401/2434") == "2397"


def test_fractional_house_number_is_preserved():
    # Knox publishes one genuinely fractional address. It is not a float tail.
    assert morpc.normalize_house_number("407.5") == "407.5"


def test_house_number_rejects_non_numbers():
    assert morpc.normalize_house_number("-9") is None      # LBRS "no house number" sentinel
    assert morpc.normalize_house_number("ST") is None
    assert morpc.normalize_house_number(None) is None
    assert morpc.normalize_house_number("") is None


def test_route_spellings_are_folded():
    # The same road is written three ways across the region.
    assert morpc.normalize_street_name("STATE ROUTE 33") == "SR 33"
    assert morpc.normalize_street_name("ST RT 314") == "SR 314"
    assert morpc.normalize_street_name("SR 104") == "SR 104"
    assert morpc.normalize_street_name("COUNTY  ROAD 91") == "CR 91"
    assert morpc.normalize_street_name("US HIGHWAY 23") == "US 23"
    assert morpc.normalize_street_name("US 23 N OVERPASS I-270") == "US 23 N OVERPASS I 270"


def test_hyphenated_names_are_split():
    # The hyphen is inconsistent in both directions between the registries and the counties.
    assert morpc.normalize_street_name("MARION-BUCYRUS") == "MARION BUCYRUS"
    assert morpc.normalize_street_name("HAZELTON ETNA") == "HAZELTON ETNA"
    assert morpc.parse_address("2388 MARION-BUCYRUS ROAD")["streetname"] == "MARION BUCYRUS"


def test_route_prefix_requires_a_route_number():
    # Without a number following it, the prefix is part of an ordinary street name.
    assert morpc.normalize_street_name("INTERSTATE") == "INTERSTATE"
    assert morpc.normalize_street_name("COUNTY LINE") == "COUNTY LINE"


def test_street_name_cleaning():
    assert morpc.normalize_street_name("Olentangy River") == "OLENTANGY RIVER"
    assert morpc.normalize_street_name("W. Nichols") == "W NICHOLS"
    assert morpc.normalize_street_name(None) is None


def test_parse_address_components():
    assert morpc.parse_address("290 W HIGH ST") == {
        "streetaddr": "290", "streetname": "HIGH", "streettype": "ST",
        "prefixdir": "W", "suffixdir": None, "unitnum": None, "unittype": None}
    assert morpc.parse_address("8780 Sunart Court South") == {
        "streetaddr": "8780", "streetname": "SUNART", "streettype": "CT",
        "prefixdir": None, "suffixdir": "S", "unitnum": None, "unittype": None}
    assert morpc.parse_address("202 W. Nichols St.")["streetname"] == "NICHOLS"


def test_parse_address_directional_is_not_stolen_from_the_name():
    # "NORTH" here is the street, not a prefix; dropping it would leave a nameless address.
    parsed = morpc.parse_address("17 NORTH ST")
    assert parsed["streetname"] == "NORTH"
    assert parsed["streettype"] == "ST"
    assert parsed["prefixdir"] is None


def test_parse_address_without_a_street_type():
    parsed = morpc.parse_address("5989 Astor")
    assert parsed["streetname"] == "ASTOR"
    assert parsed["streettype"] is None


def test_parse_address_units():
    parsed = morpc.parse_address("800 W CENTRAL AVE STE B")
    assert (parsed["streetname"], parsed["unittype"], parsed["unitnum"]) == ("CENTRAL", "STE", "B")
    assert morpc.parse_address("76 Georgetowne Dr Apt 7")["unitnum"] == "7"
    assert morpc.parse_address("123 MAIN ST #300")["unitnum"] == "300"


def test_parse_address_without_a_house_number():
    # Not locatable, but reported as such rather than guessed at.
    parsed = morpc.parse_address("ST RT 314 NORTH")
    assert parsed["streetaddr"] is None
    assert parsed["streetname"] == "SR 314"
    assert parsed["suffixdir"] == "N"


def test_parse_address_null_handling():
    assert morpc.parse_address(None) is None
    assert morpc.parse_address("") is None
    assert morpc.parse_address("   ") is None


def test_canonical_sets_are_self_consistent():
    # Every canonical value must itself normalize to itself, or repeated normalization would drift.
    for value in morpc.CONST_STREET_TYPES:
        assert morpc.normalize_street_type(value) == value
    for value in morpc.CONST_DIRECTIONALS:
        assert morpc.normalize_directional(value) == value


def test_route_number_reads_a_route_with_or_without_its_class():
    assert morpc.route_number("US 42") == "42"
    assert morpc.route_number("State Route 104") == "104"
    assert morpc.route_number("42") == "42"
    # Not numbered routes.
    assert morpc.route_number("HIGH") is None
    assert morpc.route_number("US BANK") is None
    assert morpc.route_number(None) is None


def test_route_number_tier_matches_a_county_that_omits_the_class(index):
    # Delaware publishes US 42 as the street name "42", so the regionally normalized query finds
    # nothing under the full name and falls through to the route number.
    result = morpc.geocode_addresspoints(["844 US 42 N"], "unused", indexPath=index)
    assert result.loc[0, "matched"]
    assert result.loc[0, "matchtier"] == "route_number"
    assert result.loc[0, "geometry"].x == pytest.approx(-83.06000)


def test_route_number_does_not_displace_a_full_street_name(index):
    # Logan publishes both CR 32 and TR 32. The full name matches, so the looser tier never runs and
    # the two roads are not folded together.
    result = morpc.geocode_addresspoints(["284 CR 32"], "unused", indexPath=index)
    assert result.loc[0, "matched"]
    assert result.loc[0, "matchtier"] != "route_number"
    assert result.loc[0, "matchcount"] == 1
    assert result.loc[0, "geometry"].x == pytest.approx(-83.75000)


def test_route_number_reports_ambiguity_rather_than_averaging(index):
    # SR 32 is in neither the full names nor a single road, so the route number tier finds Logan's
    # CR 32 and TR 32 together. They are kilometres apart, so the address is left unmatched.
    result = morpc.geocode_addresspoints(["284 SR 32"], "unused", indexPath=index)
    assert not result.loc[0, "matched"]
    assert result.loc[0, "matchtier"] == "route_number"
    assert result.loc[0, "matchcount"] == 2
    assert "apart" in result.loc[0, "matchnote"]


def test_postal_tail_is_stripped_before_parsing():
    # ODRC publishes a full postal address where DODD and CMS publish the street line alone.
    parsed = morpc.parse_address("1990 Harmon Avenue, Columbus, OH 43223")
    assert parsed["streetaddr"] == "1990"
    assert parsed["streetname"] == "HARMON"
    # The street type is inside the tail, so it is lost too when the tail is not removed.
    assert parsed["streettype"] == "AVE"


def test_postal_tail_variants():
    # Spelled-out state, a trailing parenthetical note, and no city segment at all.
    assert morpc.parse_address("5900 BIS Rd SW, Lancaster, Ohio 43130")["streetname"] == "BIS"
    assert morpc.parse_address(
        "16197 State Route 104, Chillicothe, OH 45601, (visitor entrance)")["streetname"] == "SR 104"
    assert morpc.parse_address("1234 Main St, OH 43215")["streetname"] == "MAIN"


def test_a_comma_alone_is_not_a_postal_tail():
    # DODD writes a directional after a comma, and names every unit of a building with commas.
    # Neither is a postal tail, and cutting at the comma would discard part of the address. Asserted
    # against the strip itself: what these addresses go on to parse to is a separate question, and
    # the first two of them parse imperfectly for reasons that predate the strip.
    for address in ["1359 STATE ROUTE #38, SOUTHEAST",
                    "4410,4412,4416,4418,4424,4426 MORSE RD",
                    "1990 HARMON AVENUE, COLUMBUS"]:
        assert _strip_postal_tail(address) == address


def test_a_street_named_for_the_state_is_not_stripped():
    assert morpc.parse_address("123 Ohio Ave")["streetname"] == "OHIO"


def test_highway_shield_and_period_separated_route_forms():
    # ODRC writes the shield form "OH-104" and the period-separated "C.R. 32"; the reference data
    # publishes 18,949 "SR <n>" and 4,960 "CR <n>" and neither of the source forms.
    assert morpc.parse_address("15802 OH-104")["streetname"] == "SR 104"
    assert morpc.parse_address("15802 OH 104")["streetname"] == "SR 104"
    parsed = morpc.parse_address("284 C.R. 32 South")
    assert parsed["streetname"] == "CR 32"
    assert parsed["suffixdir"] == "S"


def test_short_route_prefixes_do_not_capture_ordinary_names():
    # A prefix is only read at the start of a name and only when a number follows, so a street named
    # for the state or for a letter is untouched.
    assert morpc.parse_address("123 Ohio Ave")["streetname"] == "OHIO"
    parsed = morpc.parse_address("100 C Street")
    assert parsed["streetname"] == "C"
    assert parsed["streettype"] == "ST"
