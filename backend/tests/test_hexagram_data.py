import pytest
from app.core.hexagram_data import get_hexagram_by_id, get_hexagram_by_binary, _BY_ID, _BY_BINARY


def test_data_completeness():
    assert len(_BY_ID) == 64
    assert set(_BY_ID.keys()) == set(range(1, 65))


def test_binary_code_validity():
    assert len(_BY_BINARY) == 64  # all unique
    for code in _BY_BINARY:
        assert len(code) == 6, f"binary_code {code!r} is not 6 chars"
        assert set(code) <= {"0", "1"}, f"binary_code {code!r} has invalid chars"


def test_lookup_by_id_qian():
    hexagram = get_hexagram_by_id(1)
    assert hexagram["name"] == "乾"
    assert hexagram["binary_code"] == "111111"


def test_lookup_by_binary_kun():
    hexagram = get_hexagram_by_binary("000000")
    assert hexagram["name"] == "坤"
    assert hexagram["hexagram_id"] == 2


def test_invalid_id_zero():
    with pytest.raises(ValueError):
        get_hexagram_by_id(0)


def test_invalid_id_out_of_range():
    with pytest.raises(ValueError):
        get_hexagram_by_id(65)


def test_invalid_binary():
    with pytest.raises(ValueError):
        get_hexagram_by_binary("999999")
