import pytest
from unittest.mock import patch
from app.core.rules_engine import map_coin, generate_hexagram


# ─── CoinMapper ──────────────────────────────────────────────────────────────

def test_map_coin_6_lao_yin():
    line_type, is_changing = map_coin(6)
    assert line_type == "老阴"
    assert is_changing is True


def test_map_coin_7_shao_yang():
    line_type, is_changing = map_coin(7)
    assert line_type == "少阳"
    assert is_changing is False


def test_map_coin_8_shao_yin():
    line_type, is_changing = map_coin(8)
    assert line_type == "少阴"
    assert is_changing is False


def test_map_coin_9_lao_yang():
    line_type, is_changing = map_coin(9)
    assert line_type == "老阳"
    assert is_changing is True


def test_map_coin_invalid_low():
    with pytest.raises(ValueError):
        map_coin(5)


def test_map_coin_invalid_high():
    with pytest.raises(ValueError):
        map_coin(10)


# ─── HexagramGen — no changing lines ─────────────────────────────────────────

def test_no_changing_lines_static_yang():
    # all 少阳: static yang, no dynamic yao
    result = generate_hexagram([7, 7, 7, 7, 7, 7])
    assert result["changing_lines"] == []
    assert result["changed_hexagram"] == result["base_hexagram"]


def test_no_changing_lines_static_yin():
    # all 少阴: static yin, no dynamic yao
    result = generate_hexagram([8, 8, 8, 8, 8, 8])
    assert result["changing_lines"] == []
    assert result["changed_hexagram"] == result["base_hexagram"]


# ─── HexagramGen — with changing lines ───────────────────────────────────────

def test_with_changing_lines_positions():
    # Lines 1, 3 are 老阳 (changing yang → flip to yin)
    # base:    all yang  → "111111" = 乾(1)
    # changed: bits 0,2 flip to 0 → "010111" = 讼(6)
    result = generate_hexagram([9, 7, 9, 7, 7, 7])
    assert result["base_hexagram"] == 1        # 乾
    assert result["changed_hexagram"] == 6     # 讼
    assert result["changing_lines"] == [1, 3]


def test_with_changing_yin_lines():
    # Lines 2, 4 are 老阴 (changing yin → flip to yang)
    # base:    all yin   → "000000" = 坤(2)
    # changed: bits 1,3 flip to 1 → "010100" = 解(40)
    result = generate_hexagram([6, 6, 6, 6, 6, 6])
    # all 老阴: base=坤(2), changed=乾(1), all 6 lines change
    assert result["base_hexagram"] == 2        # 坤
    assert result["changed_hexagram"] == 1     # 乾
    assert result["changing_lines"] == [1, 2, 3, 4, 5, 6]


# ─── HexagramGen — known cases ───────────────────────────────────────────────

def test_all_lao_yang_base_is_qian():
    # 6 爻全为老阳(9) → base = 乾(1)
    result = generate_hexagram([9, 9, 9, 9, 9, 9])
    assert result["base_hexagram"] == 1        # 乾
    assert result["changed_hexagram"] == 2     # 坤（全部翻转为阴）
    assert result["changing_lines"] == [1, 2, 3, 4, 5, 6]


def test_all_lao_yin_base_is_kun():
    # 6 爻全为老阴(6) → base = 坤(2)
    result = generate_hexagram([6, 6, 6, 6, 6, 6])
    assert result["base_hexagram"] == 2        # 坤
    assert result["changed_hexagram"] == 1     # 乾


# ─── HexagramGen — input validation ──────────────────────────────────────────

def test_wrong_length_raises():
    with pytest.raises(ValueError):
        generate_hexagram([9, 9, 9])


def test_invalid_coin_sum_in_list_raises():
    with pytest.raises(ValueError):
        generate_hexagram([9, 9, 5, 9, 9, 9])


# ─── No file IO during generate_hexagram ─────────────────────────────────────

def test_generate_hexagram_no_file_io():
    with patch("builtins.open", side_effect=AssertionError("file IO called")):
        result = generate_hexagram([7, 7, 7, 7, 7, 7])
    assert result["base_hexagram"] is not None
