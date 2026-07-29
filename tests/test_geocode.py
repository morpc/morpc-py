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


def test_canonical_sets_are_self_consistent():
    # Every canonical value must itself normalize to itself, or repeated normalization would drift.
    for value in morpc.CONST_STREET_TYPES:
        assert morpc.normalize_street_type(value) == value
    for value in morpc.CONST_DIRECTIONALS:
        assert morpc.normalize_directional(value) == value
