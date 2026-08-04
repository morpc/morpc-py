import morpc


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
    assert morpc.normalize_street_name("US 23 N OVERPASS I-270") == "US 23 N OVERPASS I-270"


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
